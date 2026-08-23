import json
import csv
import logging
from pathlib import Path
from typing import List, Dict, Any

from app.models.product import CanonicalProduct
from app.utils.normalization import AttributeNormalizationEngine
from app.utils.diagnostics import UnknownAttributeDiagnostics
from app.utils.desc_parser import ProductDescriptionParser
from app.utils.attribute_schema import AttributeSchemaEngine
from app.schema.delivery_schema import DeliverySchemaEngine

logger = logging.getLogger(__name__)

class PipelineDelivery:
    def __init__(self, cache_dir: str = "../data/cache/web", output_dir: str = "../data/output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.delivery_engine = DeliverySchemaEngine()

    def process_and_export_pilot(self, pilot_jsonl_path: str) -> Dict[str, Any]:
        """
        Runs attribute validation, targeted second-pass extraction, 
        cleansing, and strict 252-column CSV mapping on the 20 pilot products.
        """
        input_path = Path(pilot_jsonl_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Web pilot input JSONL not found: {pilot_jsonl_path}")

        products = []
        
        with open(input_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                prod_dict = json.loads(line)
                product = CanonicalProduct.model_validate(prod_dict)
                products.append(product)

        # Process each product for validation and second-pass extraction
        for prod in products:
            class_name = prod.taxonomy.class_name or prod.taxonomy.fine or "Abrasives"
            expected_schema = AttributeSchemaEngine.generate_schema(class_name)
            
            # Map expected attributes to a list
            schema_lookup = {attr.label.strip().lower(): attr for attr in expected_schema}
            
            # Process attributes
            for attr in prod.enriched_attributes:
                label_lower = attr.label.strip().lower()
                expected_type = "TEXT"
                if label_lower in schema_lookup:
                    expected_type = schema_lookup[label_lower].value_type or "TEXT"

                # 1. Targeted Second-Pass Extraction
                # If attribute is UNKNOWN but primary sources exist, scan raw text
                if (attr.value is None or attr.status == "UNKNOWN") and len(prod.sources) > 0:
                    for source in prod.sources:
                        if source.authority_level != "UNTRUSTED" and source.description:
                            second_val = ProductDescriptionParser.second_pass_extract(
                                source.description, attr.label, expected_type
                            )
                            if second_val:
                                attr.value = second_val
                                attr.status = "VERIFIED"
                                attr.confidence = 0.85
                                attr.source = source.url
                                attr.evidence = f"Second-pass match for key '{attr.label}'."
                                break

                # 2. Validation & Normalization
                AttributeNormalizationEngine.validate_and_normalize(attr, expected_type)

            # Trace and tag unknown attributes
            UnknownAttributeDiagnostics.diagnose_product_attributes(prod)

        # Perform Diagnostic analysis & write docs/UNKNOWN_ATTRIBUTE_ANALYSIS.md
        UnknownAttributeDiagnostics.analyze_batch(products, str(self.output_dir))

        # Generate CSV Mapping rows
        csv_rows = []
        export_failures = 0
        schema_compliant = True

        for prod in products:
            try:
                row = self.delivery_engine.map_product(prod)
                # Strict Schema Verification
                self.delivery_engine.validate_schema(row)
                csv_rows.append(row)
            except Exception as e:
                export_failures += 1
                schema_compliant = False
                logger.error(f"Failed to export product {prod.identity.raw_mpn}: {e}")

        # Write to data/output/pilot_delivery.csv
        csv_path = self.output_dir / "pilot_delivery.csv"
        if csv_rows:
            headers = list(csv_rows[0].keys())
            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for row in csv_rows:
                    writer.writerow(row)

        # Quality Report Metrics
        total_products = len(products)
        attributes_enriched = 0
        attributes_verified = 0
        attributes_probable = 0
        attributes_conflicted = 0
        attributes_unknown = 0
        attributes_invalid = 0
        total_attributes = 0

        for p in products:
            total_attributes += len(p.enriched_attributes)
            for attr in p.enriched_attributes:
                if attr.value is not None:
                    attributes_enriched += 1
                if attr.status == "VERIFIED":
                    attributes_verified += 1
                elif attr.status == "PROBABLE":
                    attributes_probable += 1
                elif attr.status == "CONFLICTED":
                    attributes_conflicted += 1
                elif attr.status == "UNKNOWN":
                    attributes_unknown += 1
                elif attr.status == "INVALID":
                    attributes_invalid += 1

        report = {
            "products_processed": total_products,
            "rows_exported": len(csv_rows),
            "schema_compliance": schema_compliant,
            "total_attributes": total_attributes,
            "attribute_coverage": round((attributes_enriched / total_attributes) * 100, 2) if total_attributes else 0.0,
            "verified_attributes": attributes_verified,
            "probable_attributes": attributes_probable,
            "unknown_attributes": attributes_unknown,
            "invalid_attributes": attributes_invalid,
            "not_applicable_attributes": 0,  # Defined dynamically at system level
            "source_coverage": sum(1 for p in products if p.sources),
            "content_coverage": sum(1 for p in csv_rows if p.get("LONG_DESC1")),
            "export_failures": export_failures
        }

        output_report_path = self.output_dir / "delivery_report.json"
        with open(output_report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return report
