import json
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.models.product import (
    CanonicalProduct, ProductTaxonomy, ProductAttribute, ProductContent
)
from app.utils.cleaners import PlaceholderNormalizer
from app.utils.text import TextNormalizer
from app.utils.product_type import ProductTypeDetector
from app.utils.understanding import ProductUnderstandingEngine
from app.utils.taxonomy import TaxonomyEngine
from app.utils.attribute_schema import AttributeSchemaEngine
from app.utils.desc_parser import ProductDescriptionParser
from app.utils.duplicate import DuplicateDetector
from app.data.repositories.taxonomy_repository import TaxonomyRepository

logger = logging.getLogger(__name__)

class PipelineTaxonomy:
    def __init__(self, reference_dir: str, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Taxonomy Repository
        taxonomy_file = Path(reference_dir) / "Unilog_Taxonomy_Tree.xlsx"
        self.taxonomy_repo = TaxonomyRepository(taxonomy_file if taxonomy_file.exists() else None)
        self.taxonomy_engine = TaxonomyEngine(self.taxonomy_repo)

    def process_product(self, product: CanonicalProduct) -> CanonicalProduct:
        """
        Enriches a CanonicalProduct with taxonomy and attribute schema.
        """
        cleaned_desc = product.cleaned.part_desc.normalized_value or ""
        raw_mpn = product.raw.mfg_part_num
        brand = product.identity.brand
        manufacturer = product.identity.manufacturer
        product_type = product.identity.product_name

        # 1. Product Understanding Engine
        understanding = ProductUnderstandingEngine.analyze(
            part_desc=cleaned_desc,
            mfg_part_num=raw_mpn,
            brand=brand,
            manufacturer=manufacturer,
            product_type=product_type,
            alternate_mpn=product.identity.alternate_mpn
        )
        
        # Map semantic summary to long description
        product.content.long_desc = understanding["semantic_summary"]

        # 2. Taxonomy Engine classification
        tax_res = self.taxonomy_engine.classify(
            part_desc=cleaned_desc,
            product_type=product_type,
            brand=brand,
            manufacturer=manufacturer
        )

        product.taxonomy = ProductTaxonomy(
            department=tax_res["department"],
            class_name=tax_res["class_name"],
            fine=tax_res["fine"],
            classpath=tax_res["classpath"],
            product_type=tax_res["product_type"],
            product_family=tax_res["product_family"],
            confidence=tax_res["confidence"],
            status=tax_res["status"],
            method=tax_res["method"],
            evidence=tax_res["evidence"]
        )

        # 3. Dynamic Attribute Schema Discovery
        schema_defs = AttributeSchemaEngine.generate_schema(product.taxonomy.class_name)

        # 4. Description specifications extraction & population
        desc_specs = ProductDescriptionParser.parse(cleaned_desc)
        
        resolved_attributes = []
        for def_item in schema_defs:
            label = def_item.label
            val_type = def_item.value_type
            expected_uom = def_item.uom
            
            val = None
            evidence_str = None
            status = "UNKNOWN"
            confidence = 0.0

            # Match values from desc_specs
            spec_key = label.lower().replace(" ", "_")
            
            # Special manual handling for common labels
            if label == "Grit" and desc_specs.get("grit"):
                val = desc_specs["grit"]
                evidence_str = f"Extracted grit '{val}' from description."
                status = "VERIFIED"
                confidence = 0.9
            elif label == "Voltage" and desc_specs.get("voltage"):
                val = desc_specs["voltage"]
                evidence_str = f"Extracted voltage '{val}' from description."
                status = "VERIFIED"
                confidence = 0.9
            elif label == "Amperage" and desc_specs.get("amperage"):
                val = desc_specs["amperage"]
                evidence_str = f"Extracted power/amp '{val}' from description."
                status = "VERIFIED"
                confidence = 0.9
            elif label == "Material" and desc_specs.get("material"):
                val = desc_specs["material"]
                evidence_str = f"Extracted material '{val}' from description."
                status = "VERIFIED"
                confidence = 0.9
            elif label == "Color" and desc_specs.get("color"):
                val = desc_specs["color"]
                evidence_str = f"Extracted color '{val}' from description."
                status = "VERIFIED"
                confidence = 0.9
            elif label == "Pack Qty" and desc_specs.get("packaging_qty"):
                val = desc_specs["packaging_qty"]
                evidence_str = f"Extracted pack quantity '{val}' from description."
                status = "VERIFIED"
                confidence = 0.9
            elif label == "Length" and desc_specs.get("dimensions"):
                # Parse length dimension if possible
                dims = desc_specs["dimensions"].split(",")
                for d in dims:
                    if "'" in d or "ft" in d:
                        val = d.strip()
                        evidence_str = f"Extracted length dimension '{val}' from description."
                        status = "VERIFIED"
                        confidence = 0.9
                        break

            # Conflict checking (multiple voltage indicators etc. in description)
            if label == "Voltage" and val:
                # If there's another voltage in description
                matches = re.findall(r'\b\d+(?:\.\d+)?\s*V\b', cleaned_desc, re.IGNORECASE)
                if len(set(matches)) > 1:
                    status = "CONFLICTED"
                    evidence_str = f"Conflicting voltages found in description: {', '.join(set(matches))}"

            resolved_attributes.append(ProductAttribute(
                label=label,
                value=val,
                uom=expected_uom if val else None,
                normalized_value=val,
                status=status,
                confidence=confidence,
                source="input_description" if val else None,
                evidence=evidence_str
            ))

        product.attributes = resolved_attributes
        
        # Populate technology & packaging features
        if desc_specs.get("technology"):
            product.features.append(desc_specs["technology"])
        if desc_specs.get("packaging_uom"):
            product.features.append(f"UOM: {desc_specs['packaging_uom']}")

        return product

    def run_pipeline(self, input_jsonl_path: str) -> Dict[str, Any]:
        input_path = Path(input_jsonl_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input JSONL file not found: {input_jsonl_path}")

        canonical_products = []
        parsing_failures = 0
        failures_list = []

        # Read JSONL file
        with open(input_path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                try:
                    product_dict = json.loads(line)
                    product = CanonicalProduct.model_validate(product_dict)
                    
                    # Run Phase 3 processing
                    processed_prod = self.process_product(product)
                    canonical_products.append(processed_prod)
                except Exception as e:
                    parsing_failures += 1
                    logger.error(f"Error processing record {idx}: {e}")
                    failures_list.append({"index": idx, "line": line, "error": str(e)})

        # Write output JSONL
        output_jsonl_path = self.output_dir / "canonical_products_taxonomy.jsonl"
        with open(output_jsonl_path, "w", encoding="utf-8") as f:
            for prod in canonical_products:
                f.write(prod.model_dump_json(by_alias=True) + "\n")

        # Duplicate Pairs Review
        detector = DuplicateDetector()
        reviewed_pairs = []
        dup_metrics = {"EXACT_DUPLICATE": 0, "LIKELY_DUPLICATE": 0, "LIKELY_VARIANT": 0, "UNRELATED": 0}

        for idx, prod in enumerate(canonical_products):
            dup_res = detector.check_and_register(
                record_id=idx,
                mpn=prod.identity.raw_mpn,
                norm_mpn=prod.identity.normalized_mpn,
                mfg=prod.identity.manufacturer,
                brand=prod.identity.brand,
                desc=prod.cleaned.part_desc.normalized_value
            )
            
            if dup_res["status"] in ["DUPLICATE", "POSSIBLE_DUPLICATE"]:
                for prior_idx in dup_res["duplicate_of"]:
                    prod_a = canonical_products[prior_idx]
                    prod_b = prod
                    
                    review_res = DuplicateDetector.review_duplicate(prod_a, prod_b)
                    dup_metrics[review_res["status"]] += 1
                    
                    reviewed_pairs.append({
                        "product_a_idx": prior_idx,
                        "product_b_idx": idx,
                        "raw_mpn_a": prod_a.identity.raw_mpn,
                        "raw_mpn_b": prod_b.identity.raw_mpn,
                        "status": review_res["status"],
                        "reasoning": review_res["reasoning"],
                        "confidence": review_res["confidence"]
                    })

        # Quality Report Metrics
        total_products = len(canonical_products)
        taxonomy_assigned = 0
        taxonomy_ambiguous = 0
        taxonomy_unknown = 0
        prod_type_detected = 0
        prod_family_detected = 0
        attribute_schemas_generated = 0
        attribute_conflicts = 0
        
        conf_dist = {
            "1.0": 0,
            "0.7 - 0.9": 0,
            "0.4 - 0.6": 0,
            "0.1 - 0.3": 0,
            "0.0": 0
        }

        for prod in canonical_products:
            tax = prod.taxonomy
            if tax.department:
                taxonomy_assigned += 1
            if tax.status == "AMBIGUOUS":
                taxonomy_ambiguous += 1
            elif tax.status == "UNKNOWN":
                taxonomy_unknown += 1

            if tax.product_type and tax.product_type != "UNKNOWN":
                prod_type_detected += 1
            if tax.product_family and tax.product_family != "UNKNOWN":
                prod_family_detected += 1

            if prod.attributes:
                attribute_schemas_generated += 1
                for attr in prod.attributes:
                    if attr.status == "CONFLICTED":
                        attribute_conflicts += 1

            c = tax.confidence
            if c >= 1.0:
                conf_dist["1.0"] += 1
            elif c >= 0.7:
                conf_dist["0.7 - 0.9"] += 1
            elif c >= 0.4:
                conf_dist["0.4 - 0.6"] += 1
            elif c >= 0.1:
                conf_dist["0.1 - 0.3"] += 1
            else:
                conf_dist["0.0"] += 1

        report = {
            "total_products": total_products,
            "taxonomy_assigned": taxonomy_assigned,
            "taxonomy_ambiguous": taxonomy_ambiguous,
            "taxonomy_unknown": taxonomy_unknown,
            "product_type_detected": prod_type_detected,
            "product_family_detected": prod_family_detected,
            "attribute_schemas_generated": attribute_schemas_generated,
            "attribute_conflicts": attribute_conflicts,
            "duplicate_pairs_reviewed": len(reviewed_pairs),
            "likely_duplicates": dup_metrics["LIKELY_DUPLICATE"],
            "exact_duplicates": dup_metrics["EXACT_DUPLICATE"],
            "likely_variants": dup_metrics["LIKELY_VARIANT"],
            "unrelated_pairs": dup_metrics["UNRELATED"],
            "classification_confidence_distribution": conf_dist,
            "parsing_failures": parsing_failures,
            "failures_list": failures_list,
            "duplicate_reviews": reviewed_pairs
        }

        output_report_path = self.output_dir / "taxonomy_report.json"
        with open(output_report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return report
