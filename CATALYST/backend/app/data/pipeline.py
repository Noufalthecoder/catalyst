import json
import logging
import os
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.models.product import (
    CanonicalProduct, RawProductInput, CleanedProductInput, CleanedField,
    ProductIdentity, IdentityEvidence, ProductTaxonomy, ProductContent, ProductValidation
)
from app.utils.cleaners import PlaceholderNormalizer
from app.utils.text import TextNormalizer
from app.utils.mpn import MPNParser
from app.utils.brand import BrandResolver
from app.utils.manufacturer import ManufacturerResolver
from app.utils.product_type import ProductTypeDetector
from app.utils.desc_parser import ProductDescriptionParser
from app.utils.duplicate import DuplicateDetector
from app.data.manager import ReferenceDataManager

logger = logging.getLogger(__name__)

class IdentityPipeline:
    def __init__(self, reference_dir: str, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Reference Data Manager
        self.ref_manager = ReferenceDataManager(reference_dir)
        try:
            self.ref_manager.load_all()
            logger.info("Loaded reference datasets successfully.")
        except Exception as e:
            logger.warning(f"Reference data loading skipped or failed: {e}. Running in Mode B.")

        # Resolvers
        mfg_repo = self.ref_manager.manufacturer_repository if self.ref_manager._loaded else None
        self.brand_resolver = BrandResolver(mfg_repo)
        self.mfg_resolver = ManufacturerResolver(mfg_repo)
        self.duplicate_detector = DuplicateDetector()

    def process_record(self, raw_row: Dict[str, Any], record_idx: int) -> CanonicalProduct:
        """
        Processes a single raw input record into a CanonicalProduct.
        """
        # 1. Capture Raw Product Input
        raw_input = RawProductInput(
            mfg_part_num=str(raw_row.get("Mfg_Part_Num")) if pd.notna(raw_row.get("Mfg_Part_Num")) else None,
            part_desc=str(raw_row.get("Part_Desc")) if pd.notna(raw_row.get("Part_Desc")) else None,
            e1_brand=str(raw_row.get("E1_Brand")) if pd.notna(raw_row.get("E1_Brand")) else None,
            unilog_brand=str(raw_row.get("Unilog_Brand")) if pd.notna(raw_row.get("Unilog_Brand")) else None,
            dib_brand=str(raw_row.get("DIB_Brand")) if pd.notna(raw_row.get("DIB_Brand")) else None,
            part_manuf=str(raw_row.get("Part_Manuf")) if pd.notna(raw_row.get("Part_Manuf")) else None
        )

        # 2. Build Cleaned Product Input
        cleaned_input = CleanedProductInput(
            mfg_part_num=CleanedField(
                original_value=raw_input.mfg_part_num,
                normalized_value=PlaceholderNormalizer.normalize(raw_input.mfg_part_num)
            ),
            part_desc=CleanedField(
                original_value=raw_input.part_desc,
                normalized_value=PlaceholderNormalizer.normalize(raw_input.part_desc)
            ),
            e1_brand=CleanedField(
                original_value=raw_input.e1_brand,
                normalized_value=PlaceholderNormalizer.normalize(raw_input.e1_brand)
            ),
            unilog_brand=CleanedField(
                original_value=raw_input.unilog_brand,
                normalized_value=PlaceholderNormalizer.normalize(raw_input.unilog_brand)
            ),
            dib_brand=CleanedField(
                original_value=raw_input.dib_brand,
                normalized_value=PlaceholderNormalizer.normalize(raw_input.dib_brand)
            ),
            part_manuf=CleanedField(
                original_value=raw_input.part_manuf,
                normalized_value=PlaceholderNormalizer.normalize(raw_input.part_manuf)
            )
        )

        cleaned_mfg_part_num = cleaned_input.mfg_part_num.normalized_value
        cleaned_part_desc = cleaned_input.part_desc.normalized_value

        # 3. Parse MPN
        mpn_info = MPNParser.parse(cleaned_mfg_part_num, cleaned_part_desc)

        # 4. Resolve Brand
        brand_record = {
            "e1_brand": raw_input.e1_brand,
            "unilog_brand": raw_input.unilog_brand,
            "dib_brand": raw_input.dib_brand,
            "part_desc": cleaned_part_desc
        }
        brand_info = self.brand_resolver.resolve(brand_record)

        # 5. Resolve Manufacturer
        mfg_record = {
            "part_manuf": raw_input.part_manuf,
            "part_desc": cleaned_part_desc
        }
        mfg_info = self.mfg_resolver.resolve(mfg_record, resolved_brand=brand_info["brand"])

        # 6. Detect Product Type
        type_info = ProductTypeDetector.detect(cleaned_part_desc)

        # 7. Check duplicates
        dup_info = self.duplicate_detector.check_and_register(
            record_id=record_idx,
            mpn=mpn_info["raw_mpn"],
            norm_mpn=mpn_info["normalized_mpn"],
            mfg=mfg_info["canonical_name"],
            brand=brand_info["brand"],
            desc=cleaned_part_desc
        )

        # 8. Compute Confidence Score & Status
        # Confidence score formula:
        # - MPN exists: +0.4
        # - Brand resolved: +0.3
        # - Manufacturer resolved: +0.3
        # Maximum score is 1.0.
        confidence = 0.0
        if mpn_info["raw_mpn"]:
            confidence += 0.4
        if brand_info["brand"]:
            confidence += 0.3
        if mfg_info["canonical_name"]:
            confidence += 0.3

        status = "UNKNOWN"
        if brand_info["status"] == "CONFLICTED" or mfg_info["status"] == "CONFLICTED":
            status = "CONFLICTED"
        elif confidence >= 0.9:
            status = "VERIFIED"
        elif confidence >= 0.6:
            status = "PROBABLE"
        elif confidence > 0.0:
            status = "AMBIGUOUS"
        else:
            status = "UNKNOWN"

        # 9. Build Evidence
        evidence = []
        if mpn_info["raw_mpn"]:
            evidence.append(IdentityEvidence(
                field="mfg_part_num",
                value=mpn_info["raw_mpn"],
                source="Mfg_Part_Num",
                evidence=f"Primary MPN extracted directly from input.",
                status="VERIFIED"
            ))
        if brand_info["brand"]:
            evidence.append(IdentityEvidence(
                field="brand",
                value=brand_info["brand"],
                source="e1_brand/dib_brand/part_desc",
                evidence=brand_info["evidence"],
                status=brand_info["status"]
            ))
        if mfg_info["canonical_name"]:
            evidence.append(IdentityEvidence(
                field="manufacturer",
                value=mfg_info["canonical_name"],
                source="part_manuf/brand_linkage",
                evidence="; ".join(mfg_info["evidence"]),
                status=mfg_info["status"]
            ))

        identity = ProductIdentity(
            raw_mpn=mpn_info["raw_mpn"],
            normalized_mpn=mpn_info["normalized_mpn"],
            manufacturer=mfg_info["canonical_name"],
            manufacturer_candidates=mfg_info["candidates"],
            brand=brand_info["brand"],
            brand_candidates=brand_info["brand_candidates"],
            product_name=type_info["product_type"],
            alternate_mpn=mpn_info["alternate_mpn"],
            identity_confidence=round(confidence, 2),
            identity_status=status,
            identity_evidence=evidence
        )

        taxonomy = ProductTaxonomy(
            classpath=None,
            confidence=0.0
        )

        content = ProductContent(
            product_title=cleaned_part_desc
        )

        # Build final CanonicalProduct
        product = CanonicalProduct(
            raw=raw_input,
            cleaned=cleaned_input,
            identity=identity,
            taxonomy=taxonomy,
            attributes=[],
            features=[],
            content=content,
            sources=[],
            assets=[],
            validation=ProductValidation(
                schema_compliant=False,
                validation_errors=[],
                quality_state=status
            )
        )
        return product

    def run_pipeline(self, input_file_path: str) -> Dict[str, Any]:
        """
        Runs the batch pipeline over the complete input file.
        Writes data/output/canonical_products.jsonl and data/output/identity_report.json.
        """
        input_path = Path(input_file_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file_path}")

        # Ingestion using pandas
        if input_path.suffix.lower() == '.csv':
            df = pd.read_csv(input_path)
        elif input_path.suffix.lower() == '.xlsx':
            df = pd.read_excel(input_path)
        else:
            raise ValueError(f"Unsupported input format: {input_path.suffix}")

        total_products = len(df)
        canonical_products = []
        parsing_failures = 0
        failures_list = []

        output_jsonl_path = self.output_dir / "canonical_products.jsonl"
        
        with open(output_jsonl_path, "w", encoding="utf-8") as f:
            for idx, row in df.iterrows():
                try:
                    product = self.process_record(row.to_dict(), idx)
                    canonical_products.append(product)
                    
                    # Write single JSON line
                    # Using by_alias=True to support Pydantic aliases
                    f.write(product.model_dump_json(by_alias=True) + "\n")
                except Exception as e:
                    parsing_failures += 1
                    logger.error(f"Error processing record {idx}: {e}")
                    failures_list.append({"index": idx, "row": row.to_dict(), "error": str(e)})

        # Identity Metrics Calculation
        unique_mpns = len(self.duplicate_detector.exact_mpn_map)
        
        # Duplicate candidates count
        dup_count = 0
        pos_dup_count = 0
        for idx, prod in enumerate(canonical_products):
            # Check duplicate status via duplicate detector
            mpn = prod.identity.raw_mpn
            norm_mpn = prod.identity.normalized_mpn
            mfg = prod.identity.manufacturer
            brand = prod.identity.brand
            desc = prod.cleaned.part_desc.normalized_value
            
            # Temporary duplicate check (without registering again)
            status_check = self.duplicate_detector.check_and_register(
                record_id=f"check_{idx}",
                mpn=None, norm_mpn=None, mfg=None, brand=None, desc=None # don't register
            )
            
        # Let's count duplicate tags directly from pipeline outputs
        status_counts = {"UNIQUE": 0, "DUPLICATE": 0, "POSSIBLE_DUPLICATE": 0}
        brand_identified_count = 0
        mfg_identified_count = 0
        prod_type_detected_count = 0
        confidence_distribution = {
            "1.0": 0,
            "0.7 - 0.9": 0,
            "0.4 - 0.6": 0,
            "0.1 - 0.3": 0,
            "0.0": 0
        }
        
        ambiguous_identities = 0
        unknown_identities = 0

        # Rerun check using registered duplicate detector state
        detector = DuplicateDetector()
        for idx, prod in enumerate(canonical_products):
            dup_res = detector.check_and_register(
                record_id=idx,
                mpn=prod.identity.raw_mpn,
                norm_mpn=prod.identity.normalized_mpn,
                mfg=prod.identity.manufacturer,
                brand=prod.identity.brand,
                desc=prod.cleaned.part_desc.normalized_value
            )
            status_counts[dup_res["status"]] += 1
            
            if prod.identity.brand:
                brand_identified_count += 1
            if prod.identity.manufacturer:
                mfg_identified_count += 1
            if prod.identity.product_name and prod.identity.product_name != "UNKNOWN":
                prod_type_detected_count += 1
                
            conf = prod.identity.identity_confidence
            if conf >= 1.0:
                confidence_distribution["1.0"] += 1
            elif conf >= 0.7:
                confidence_distribution["0.7 - 0.9"] += 1
            elif conf >= 0.4:
                confidence_distribution["0.4 - 0.6"] += 1
            elif conf >= 0.1:
                confidence_distribution["0.1 - 0.3"] += 1
            else:
                confidence_distribution["0.0"] += 1

            if prod.identity.identity_status == "AMBIGUOUS":
                ambiguous_identities += 1
            elif prod.identity.identity_status == "UNKNOWN":
                unknown_identities += 1

        report = {
            "total_products": total_products,
            "unique_mpns": unique_mpns,
            "duplicate_candidates": status_counts["DUPLICATE"] + status_counts["POSSIBLE_DUPLICATE"],
            "duplicates": status_counts["DUPLICATE"],
            "possible_duplicates": status_counts["POSSIBLE_DUPLICATE"],
            "products_with_identified_brands": brand_identified_count,
            "products_with_identified_manufacturers": mfg_identified_count,
            "products_with_detected_product_types": prod_type_detected_count,
            "ambiguous_identities": ambiguous_identities,
            "unknown_identities": unknown_identities,
            "confidence_distribution": confidence_distribution,
            "parsing_failures": parsing_failures,
            "failures_list": failures_list
        }

        output_report_path = self.output_dir / "identity_report.json"
        with open(output_report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return report
