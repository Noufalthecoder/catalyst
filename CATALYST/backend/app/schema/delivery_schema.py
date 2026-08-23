import json
from pathlib import Path
from typing import Dict, Any, List
from app.models.product import CanonicalProduct
from app.utils.content_generation import ContentGenerator

class ExportBlockedException(Exception):
    pass

class DeliverySchemaEngine:
    def __init__(self, schema_path: str = "app/schema/output_schema.json"):
        # Resolve absolute path relative to project backend CWD
        self.schema_path = Path(schema_path)
        if not self.schema_path.exists():
            # Try absolute workspace resolution
            self.schema_path = Path("c:/Users/Mohammed Noufal V/catalyst1/CATALYST/backend/app/schema/output_schema.json")
            
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Authoritative schema JSON not found: {schema_path}")
            
        with open(self.schema_path, "r", encoding="utf-8") as f:
            schema_data = json.load(f)
            self.expected_columns = schema_data["columns"]

    def map_product(self, product: CanonicalProduct) -> Dict[str, Any]:
        """
        Maps a single CanonicalProduct to the precise 252-column output structure.
        """
        # Generate descriptions
        descs = ContentGenerator.generate_descriptions(product)

        # Build attribute lookup
        specs = {}
        for attr in product.enriched_attributes:
            specs[attr.label.strip().lower()] = attr

        row = {}
        
        # 1. Sources mapping
        sources = product.sources
        row["MFR URL"] = sources[0].url if len(sources) > 0 else ""
        for i in range(1, 6):
            row[f"Ref URL {i}"] = sources[i].url if len(sources) > i else ""

        # 2. Basic identifiers
        row["PART_NUMBER"] = product.identity.raw_mpn or ""
        row["Dept"] = product.taxonomy.department or ""
        row["Class"] = product.taxonomy.class_name or ""
        row["Fine"] = product.taxonomy.fine or ""
        row["SKU - MY_PART_NUMBER"] = product.identity.raw_mpn or ""
        row["Mfg_Part_Num"] = product.identity.raw_mpn or ""
        row["Part_Desc"] = product.raw.part_desc or ""
        row["E1_Brand"] = product.raw.e1_brand or ""
        row["Unilog_Brand"] = product.raw.unilog_brand or ""
        row["DIB_Brand"] = product.raw.dib_brand or ""
        row["Part_Manuf"] = product.raw.part_manuf or ""
        row["MANUFACTURER_NAME"] = product.identity.manufacturer or ""
        row["BRAND_NAME"] = product.identity.brand or ""
        row["TRADE_NAME"] = ""
        row["MANUFACTURER_PART_NUMBER"] = product.identity.raw_mpn or ""
        row["ALTERNATE_PART_NUMBER"] = product.identity.alternate_mpn or ""
        row["Classpath"] = product.taxonomy.classpath or ""

        # 3. Content fields
        row["MOBILE_DESC"] = descs.get("MOBILE_DESC", "")
        row["INVOICE_DESC"] = descs.get("INVOICE_DESC", "")
        row["SHORT_DESC"] = descs.get("SHORT_DESC", "")
        row["LONG_DESC1"] = descs.get("LONG_DESC1", "")
        row["RETAIL_DESC"] = descs.get("RETAIL_DESC", "")
        row["MARKETING_DESCRIPTION"] = descs.get("MARKETING_DESCRIPTION", "")

        # 4. Features list mapping
        features = product.features or []
        for i in range(1, 21):
            row[f"ITEM_FEATURES_{i}"] = features[i-1] if len(features) > (i-1) else ""

        # 5. Core properties
        row["With"] = ""
        row["Standard/Approvals"] = ""
        row["Prop 65"] = ""
        row["Application"] = specs.get("application").value if "application" in specs else ""
        row["Includes"] = ""
        row["Product Name"] = product.identity.product_name or ""

        # 6. Attributes block (1 to 50)
        # Filter attributes that are NOT common system columns
        other_attrs = []
        for attr in product.enriched_attributes:
            label_lower = attr.label.lower()
            if label_lower not in ["length", "width", "height", "weight", "volume", "application", "voltage", "amperage"]:
                if attr.status in ["VERIFIED", "PROBABLE"]:
                    other_attrs.append(attr)

        for i in range(1, 51):
            if len(other_attrs) > (i-1):
                attr = other_attrs[i-1]
                row[f"ATTRIBUTE_LABEL {i}"] = attr.label
                row[f"ATTRIBUTE_VALUE {i}"] = str(attr.normalized_value or attr.value)
                row[f"ATTRIBUTE_UOM {i}"] = attr.uom or ""
            else:
                row[f"ATTRIBUTE_LABEL {i}"] = ""
                row[f"ATTRIBUTE_VALUE {i}"] = ""
                row[f"ATTRIBUTE_UOM {i}"] = ""

        # 7. Identifiers
        row["UPC"] = ""
        row["EAN"] = ""
        row["GTIN"] = ""
        row["UNSPSC"] = product.taxonomy.unspsc or ""
        row["Warranty"] = ""
        row["List Price"] = ""
        row["Selling Qty"] = ""
        row["Selling UOM"] = ""
        row["Standard Packaging Information"] = ""

        # 8. Dimensions & Weight
        # Direct lookup from attributes if present
        row["LENGTH"] = str(specs["length"].normalized_value) if "length" in specs and specs["length"].status in ["VERIFIED", "PROBABLE"] else ""
        row["LENGTH_UOM"] = specs["length"].uom if "length" in specs and specs["length"].status in ["VERIFIED", "PROBABLE"] else ""
        
        row["HEIGHT"] = str(specs["height"].normalized_value) if "height" in specs and specs["height"].status in ["VERIFIED", "PROBABLE"] else ""
        row["HEIGHT_UOM"] = specs["height"].uom if "height" in specs and specs["height"].status in ["VERIFIED", "PROBABLE"] else ""

        row["WIDTH"] = str(specs["width"].normalized_value) if "width" in specs and specs["width"].status in ["VERIFIED", "PROBABLE"] else ""
        row["WIDTH_UOM"] = specs["width"].uom if "width" in specs and specs["width"].status in ["VERIFIED", "PROBABLE"] else ""

        row["WEIGHT"] = str(specs["weight"].normalized_value) if "weight" in specs and specs["weight"].status in ["VERIFIED", "PROBABLE"] else ""
        row["WEIGHT_UOM"] = specs["weight"].uom if "weight" in specs and specs["weight"].status in ["VERIFIED", "PROBABLE"] else ""

        row["VOLUME"] = str(specs["volume"].normalized_value) if "volume" in specs and specs["volume"].status in ["VERIFIED", "PROBABLE"] else ""
        row["VOLUME_UOM"] = specs["volume"].uom if "volume" in specs and specs["volume"].status in ["VERIFIED", "PROBABLE"] else ""

        # 9. Digital Assets & SDS Documents
        row["Product Image"] = product.assets[0] if len(product.assets) > 0 else ""
        for i in range(1, 5):
            row[f"Alternate Image {i}"] = product.assets[i] if len(product.assets) > i else ""

        # SDS and Manual types from sources
        row["SDS"] = ""
        row["SDS_1"] = ""
        row["Warranty Information"] = ""
        row["Catalog"] = ""
        row["Specification Sheet"] = ""
        row["Instruction/Installation Manual"] = ""
        row["Service Manual"] = ""
        row["Owners/User Manual"] = ""
        row["Line Drawing"] = ""
        row["MTR"] = ""
        row["RoHS"] = ""
        row["Full Engineering Drawing"] = ""
        row["Energy Star Guide"] = ""
        row["Technical Bulletin"] = ""
        row["Submittal"] = ""
        row["Compatibility Chart"] = ""
        row["Size Chart"] = ""
        row["Product Label/Insert"] = ""
        row["Video Link"] = ""
        row["Video Link 1"] = ""
        
        # Populate manual/sheet URLs from sources
        for s in sources:
            if s.source_type == "MANUFACTURER_DATASHEET":
                row["Specification Sheet"] = s.url
            elif s.source_type == "MANUFACTURER_MANUAL":
                row["Instruction/Installation Manual"] = s.url
            elif s.source_type == "MANUFACTURER_CATALOG":
                row["Catalog"] = s.url

        row["Country Of Origin"] = ""
        row["Discontinued"] = ""
        row["Actual Image (Yes/No)"] = "Yes" if len(product.assets) > 0 else "No"

        # Strictly enforce and order columns to match output_schema.json
        ordered_row = {}
        for col in self.expected_columns:
            # Match case-insensitively but output exact schema casing
            col_match = next((k for k in row.keys() if k.lower().strip() == col.lower().strip()), None)
            if col_match:
                ordered_row[col] = row[col_match]
            else:
                ordered_row[col] = ""

        return ordered_row

    def validate_schema(self, row: Dict[str, Any]) -> bool:
        """
        Validates that the output row conforms exactly to the 252-column schema contract.
        """
        keys = list(row.keys())
        if len(keys) != 252:
            raise ExportBlockedException(f"Schema violation: expected 252 columns, got {len(keys)}.")
        
        for idx, col in enumerate(self.expected_columns):
            if keys[idx] != col:
                raise ExportBlockedException(f"Schema violation: column name mismatch at index {idx}. Expected '{col}', got '{keys[idx]}'.")
        
        return True
