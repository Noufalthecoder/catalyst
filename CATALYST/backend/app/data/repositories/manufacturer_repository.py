import pandas as pd
from typing import Dict, Optional, Union
from pathlib import Path
from app.utils.text import TextNormalizer

class ManufacturerRepository:
    def __init__(self):
        self.exact_mfg_idx = {}
        self.norm_mfg_idx = {}
        self.mfg_code_idx = {}
        
        self.exact_brand_idx = {}
        self.norm_brand_idx = {}
        self.brand_code_idx = {}
        
        self.mfg_to_brand = {}

    def load_from_excel(self, file_path: Union[str, Path]):
        """
        Loads UniCat_Manufacturer_and_Brand_List.xlsx.
        """
        df = pd.read_excel(file_path)
        
        # Verify columns exist
        expected_cols = ["MANUFACTURER_NAME", "MANUFACTURER_CODE", "BRAND_NAME", "BRAND_CODE"]
        for col in expected_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column in Manufacturer Master: {col}")

        # Build indexes
        for _, row in df.iterrows():
            mfg_name = str(row["MANUFACTURER_NAME"]) if pd.notna(row["MANUFACTURER_NAME"]) else ""
            mfg_code = str(row["MANUFACTURER_CODE"]) if pd.notna(row["MANUFACTURER_CODE"]) else ""
            brand_name = str(row["BRAND_NAME"]) if pd.notna(row["BRAND_NAME"]) else ""
            brand_code = str(row["BRAND_CODE"]) if pd.notna(row["BRAND_CODE"]) else ""

            if mfg_name:
                self.exact_mfg_idx[mfg_name] = mfg_name
                self.norm_mfg_idx[TextNormalizer.normalize_for_comparison(mfg_name)] = mfg_name
                if mfg_code:
                    self.mfg_code_idx[mfg_code] = mfg_name
            
            if brand_name:
                self.exact_brand_idx[brand_name] = brand_name
                self.norm_brand_idx[TextNormalizer.normalize_for_comparison(brand_name)] = brand_name
                if brand_code:
                    self.brand_code_idx[brand_code] = brand_name

            if mfg_name and brand_name:
                if mfg_name not in self.mfg_to_brand:
                    self.mfg_to_brand[mfg_name] = set()
                self.mfg_to_brand[mfg_name].add(brand_name)

    def resolve_manufacturer(self, value: str) -> Dict[str, Union[str, float]]:
        if not value:
            return {"input": value, "match": None, "code": None, "method": "none", "score": 0.0}
        
        # Exact Match
        if value in self.exact_mfg_idx:
            return {"input": value, "match": self.exact_mfg_idx[value], "method": "exact", "score": 1.0}
        
        # Normalized Match
        norm_val = TextNormalizer.normalize_for_comparison(value)
        if norm_val in self.norm_mfg_idx:
            return {"input": value, "match": self.norm_mfg_idx[norm_val], "method": "normalized", "score": 1.0}
        
        # Fuzzy Candidate Retrieval could be added here
        
        return {"input": value, "match": None, "method": "none", "score": 0.0}

    def resolve_brand(self, value: str, manufacturer: Optional[str] = None) -> Dict[str, Union[str, float]]:
        if not value:
            return {"input": value, "match": None, "code": None, "method": "none", "score": 0.0}

        # Exact Match
        if value in self.exact_brand_idx:
            # Optionally verify if it belongs to manufacturer if specified
            return {"input": value, "match": self.exact_brand_idx[value], "method": "exact", "score": 1.0}
        
        # Normalized Match
        norm_val = TextNormalizer.normalize_for_comparison(value)
        if norm_val in self.norm_brand_idx:
            return {"input": value, "match": self.norm_brand_idx[norm_val], "method": "normalized", "score": 1.0}

        return {"input": value, "match": None, "method": "none", "score": 0.0}
