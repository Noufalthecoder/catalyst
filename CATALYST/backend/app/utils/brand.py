from typing import Dict, List, Optional, Any
from app.data.repositories.manufacturer_repository import ManufacturerRepository
from app.utils.cleaners import PlaceholderNormalizer
from app.utils.text import TextNormalizer
import re

class BrandResolver:
    # Deterministic mapping for common brand abbreviations and aliases (Mode B)
    BRAND_ALIASES = {
        "MILW": "Milwaukee",
        "MILWAUKEE": "Milwaukee",
        "DEWALT": "DEWALT",
        "DEWLT": "DEWALT",
        "MAKITA": "Makita",
        "GE": "GE",
        "SQ": "Speed Queen",
        "SPEED QUEEN": "Speed Queen",
        "3M": "3M",
        "3 M": "3M",
        "COOPER": "Cooper",
        "LUTRON": "Lutron",
        "LEVITON": "Leviton",
        "KICHLER": "Kichler",
        "SATCO": "Satco",
        "PHILIPS": "Philips",
        "WIZ": "Wiz",
        "FEIT": "Feit Electric",
        "FEIT ELECTRIC": "Feit Electric",
        "BOSCH": "Bosch",
        "DREMEL": "Dremel",
        "GRIZZLY": "Grizzly",
        "KREG": "Kreg",
        "VESSEL": "Vessel",
        "TIMBERTECH": "TimberTech",
        "TIMBER TECH": "TimberTech",
        "TREX": "Trex",
        "DIABLO": "Diablo",
        "SENCO": "Senco",
        "MIRKA": "Mirka",
        "FESTO": "Festool",
        "FESTOOL": "Festool",
        "PROVIA": "ProVia",
        "CERTAINTEED": "CertainTeed",
        "LP": "LP SmartSide",
        "LP SMARTSIDE": "LP SmartSide",
        "JAMESHARDIE": "James Hardie",
        "HARDIE": "James Hardie",
        "FIRST ALERT": "First Alert",
        "BRK": "BRK",
        "RADIANS": "Radians",
        "MALCO": "Malco",
        "IRWIN": "Irwin",
        "SABRE": "Sabre",
        "STREAMLIGHT": "Streamlight"
    }

    def __init__(self, mfg_repo: Optional[ManufacturerRepository] = None):
        self.mfg_repo = mfg_repo
        # Check if repo has data (Mode A vs Mode B)
        self.mode_a = mfg_repo is not None and len(mfg_repo.exact_brand_idx) > 0

    def resolve(self, record: Dict[str, Any], resolved_mfg: Optional[str] = None) -> Dict[str, Any]:
        """
        Resolves brand name using explicit inputs, description parsing, and master lists.
        """
        evidence_list = []
        candidates = []

        raw_e1 = record.get("e1_brand")
        raw_unilog = record.get("unilog_brand")
        raw_dib = record.get("dib_brand")
        part_desc = record.get("part_desc", "")

        # Clean placeholders
        e1 = PlaceholderNormalizer.normalize(raw_e1)
        unilog = PlaceholderNormalizer.normalize(raw_unilog)
        dib = PlaceholderNormalizer.normalize(raw_dib)

        # Collect explicit non-empty brands
        explicit_brands = []
        for src, val in [("unilog_brand", unilog), ("e1_brand", e1), ("dib_brand", dib)]:
            if val:
                explicit_brands.append((src, val))
                if val not in candidates:
                    candidates.append(val)

        # 1. Handle Explicit Brands
        if explicit_brands:
            # Check for conflict among explicit values
            unique_explicit = list(set([val for src, val in explicit_brands]))
            if len(unique_explicit) > 1:
                return {
                    "brand": None,
                    "brand_candidates": unique_explicit,
                    "confidence": 0.3,
                    "status": "CONFLICTED",
                    "evidence": f"Conflicting explicit brands: {', '.join([f'{src}: {val}' for src, val in explicit_brands])}"
                }

            # Single explicit brand
            source_field, val = explicit_brands[0]
            resolved_val = self._clean_and_map_brand(val)
            
            if self.mode_a:
                # Mode A: Validate against repository
                repo_res = self.mfg_repo.resolve_brand(resolved_val)
                if repo_res["match"]:
                    return {
                        "brand": repo_res["match"],
                        "brand_candidates": [repo_res["match"]],
                        "confidence": 1.0,
                        "status": "VERIFIED",
                        "evidence": f"Matched explicit {source_field} in brand master: {resolved_val}"
                    }
            
            # If not in master, or in Mode B
            return {
                "brand": resolved_val,
                "brand_candidates": [resolved_val],
                "confidence": 0.8,
                "status": "PROBABLE",
                "evidence": f"Resolved from explicit input field: {source_field}"
            }

        # 2. Extract brand embedded in Part_Desc
        if part_desc:
            # Mode A: Match against brand master
            if self.mode_a:
                for norm_b, canon_b in self.mfg_repo.norm_brand_idx.items():
                    # Check for exact word boundary match in normalized description
                    norm_desc = TextNormalizer.normalize_for_comparison(part_desc)
                    if re.search(r'\b' + re.escape(norm_b) + r'\b', norm_desc):
                        return {
                            "brand": canon_b,
                            "brand_candidates": [canon_b],
                            "confidence": 0.7,
                            "status": "PROBABLE",
                            "evidence": f"Extracted brand '{canon_b}' from description using brand master"
                        }

            # Mode B: Fallback regex matching using brand aliases
            norm_desc = TextNormalizer.normalize_for_comparison(part_desc)
            for alias, canon in self.BRAND_ALIASES.items():
                alias_norm = TextNormalizer.normalize_for_comparison(alias)
                if re.search(r'\b' + re.escape(alias_norm) + r'\b', norm_desc):
                    return {
                        "brand": canon,
                        "brand_candidates": [canon],
                        "confidence": 0.7,
                        "status": "PROBABLE",
                        "evidence": f"Extracted brand '{canon}' from description using alias patterns"
                    }

        # 3. Known manufacturer/brand relationship
        if resolved_mfg and self.mode_a:
            mfg_brands = self.mfg_repo.mfg_to_brand.get(resolved_mfg, set())
            if len(mfg_brands) == 1:
                canon_b = list(mfg_brands)[0]
                return {
                    "brand": canon_b,
                    "brand_candidates": [canon_b],
                    "confidence": 0.6,
                    "status": "PROBABLE",
                    "evidence": f"Inferred brand '{canon_b}' from resolved manufacturer '{resolved_mfg}' relationship"
                }

        # 4. Unknown
        return {
            "brand": None,
            "brand_candidates": [],
            "confidence": 0.0,
            "status": "UNKNOWN",
            "evidence": "No explicit brand fields or description matches found"
        }

    def _clean_and_map_brand(self, brand: str) -> str:
        """
        Cleans and maps brand names to canonical forms if aliases exist.
        """
        cleaned = brand.strip()
        norm = cleaned.upper()
        if norm in self.BRAND_ALIASES:
            return self.BRAND_ALIASES[norm]
        return cleaned
