from typing import Dict, List, Optional, Any
from app.data.repositories.manufacturer_repository import ManufacturerRepository
from app.utils.cleaners import PlaceholderNormalizer
from app.utils.text import TextNormalizer
import re

class ManufacturerResolver:
    # Deterministic mapping from Brand to canonical Manufacturer name (Mode B)
    BRAND_TO_MFG = {
        "Milwaukee": "Milwaukee Tool",
        "DEWALT": "DEWALT",
        "Makita": "Makita USA Inc",
        "GE": "GE Appliances",
        "Speed Queen": "Speed Queen",
        "3M": "3M Company",
        "Cooper": "Cooper Wiring Devices",
        "Lutron": "Lutron",
        "Leviton": "Leviton Mfg Co",
        "Kichler": "Kichler Lighting",
        "Satco": "Satco Products Inc",
        "Philips": "Philips Lighting",
        "Wiz": "Philips Lighting",
        "Feit Electric": "Feit Electric",
        "Bosch": "Robert Bosch Tool Corp",
        "Dremel": "Robert Bosch Tool Corp",
        "Grizzly": "Grizzly Industrial",
        "Kreg": "Kreg Tool Company",
        "Vessel": "Vessel Tools USA Inc",
        "TimberTech": "TimberTech",
        "Trex": "Trex Company Inc",
        "Diablo": "Freud Inc",
        "Senco": "Senco Products Inc",
        "Mirka": "Mirka Abrasives Inc",
        "Festool": "Festool USA",
        "ProVia": "ProVia",
        "CertainTeed": "CertainTeed Gypsum",
        "LP SmartSide": "LP SmartSide",
        "James Hardie": "James Hardie",
        "First Alert": "First Alert",
        "Radians": "Radians",
        "Malco": "Malco Products",
        "Irwin": "Irwin Industrial Tools",
        "Sabre": "Sabre",
        "Streamlight": "Streamlight"
    }

    def __init__(self, mfg_repo: Optional[ManufacturerRepository] = None):
        self.mfg_repo = mfg_repo
        self.mode_a = mfg_repo is not None and len(mfg_repo.exact_mfg_idx) > 0

    def clean_manufacturer_string(self, raw_manuf: str) -> str:
        """
        Cleans strings like 'Milwaukee Accessory (4031)' or '3 M Co (5293)'
        by stripping out bracketed codes and extra spaces.
        """
        if not raw_manuf:
            return ""
        # Remove parenthesized parts e.g. " (4031)"
        cleaned = re.sub(r'\s*\([^)]*\)', '', raw_manuf)
        return cleaned.strip()

    def resolve(self, record: Dict[str, Any], resolved_brand: Optional[str] = None) -> Dict[str, Any]:
        """
        Resolves manufacturer using explicit inputs, descriptions, and brand linkages.
        """
        raw_manuf = record.get("part_manuf")
        part_desc = record.get("part_desc", "")

        # Clean placeholder
        manuf = PlaceholderNormalizer.normalize(raw_manuf)
        
        candidates = []
        if manuf:
            cleaned_manuf = self.clean_manufacturer_string(manuf)
            candidates.append(cleaned_manuf)
        else:
            cleaned_manuf = None

        # 1. Mode A: Resolve against master list
        if self.mode_a and cleaned_manuf:
            repo_res = self.mfg_repo.resolve_manufacturer(cleaned_manuf)
            if repo_res["match"]:
                return {
                    "canonical_name": repo_res["match"],
                    "candidates": [repo_res["match"]],
                    "confidence": 1.0,
                    "status": "VERIFIED",
                    "evidence": [f"Matched cleaned manufacturer '{cleaned_manuf}' in manufacturer master"]
                }
            
            # Try to match the raw value directly just in case
            repo_res_raw = self.mfg_repo.resolve_manufacturer(manuf)
            if repo_res_raw["match"]:
                return {
                    "canonical_name": repo_res_raw["match"],
                    "candidates": [repo_res_raw["match"]],
                    "confidence": 1.0,
                    "status": "VERIFIED",
                    "evidence": [f"Matched raw manufacturer '{manuf}' in manufacturer master"]
                }

        # 2. Mode B or Missing from master list: Deterministic cleaning
        if cleaned_manuf:
            # Match code pattern or name mapping
            canon_name = self._map_to_canonical(cleaned_manuf)
            return {
                "canonical_name": canon_name,
                "candidates": [canon_name],
                "confidence": 0.8,
                "status": "PROBABLE",
                "evidence": [f"Resolved from cleaned Part_Manuf input: '{cleaned_manuf}'"]
            }

        # 3. Infer from resolved Brand
        if resolved_brand:
            inferred_mfg = self.BRAND_TO_MFG.get(resolved_brand)
            if inferred_mfg:
                return {
                    "canonical_name": inferred_mfg,
                    "candidates": [inferred_mfg],
                    "confidence": 0.7,
                    "status": "PROBABLE",
                    "evidence": [f"Inferred manufacturer '{inferred_mfg}' from resolved brand '{resolved_brand}'"]
                }

        # 4. Unknown
        return {
            "canonical_name": None,
            "candidates": [],
            "confidence": 0.0,
            "status": "UNKNOWN",
            "evidence": ["No valid Part_Manuf field or brand linkage available"]
        }

    def _map_to_canonical(self, name: str) -> str:
        """
        Maps cleaned names to standard forms if known.
        """
        norm = name.upper()
        if "MILWAUKEE" in norm:
            return "Milwaukee Tool"
        if "DEWALT" in norm or "DEWLT" in norm:
            return "DEWALT"
        if "MAKITA" in norm:
            return "Makita USA Inc"
        if "FREUD" in norm:
            return "Freud Inc"
        if "MIRKA" in norm:
            return "Mirka Abrasives Inc"
        if "APPLIANCE DEALERS" in norm:
            return "Appliance Dealers Cooperative"
        if "3 M" in norm or "3M CO" in norm:
            return "3M Company"
        return name
