from typing import Dict, List, Optional, Tuple, Any
from fuzzywuzzy import fuzz

class DuplicateDetector:
    def __init__(self):
        # Indexes to store processed item signatures and map them to their record indexes or IDs
        self.exact_mpn_map = {}
        self.norm_mpn_map = {}
        self.mfg_mpn_map = {}
        self.brand_mpn_map = {}
        self.desc_list = []  # List of tuples (record_id, normalized_desc)

    def check_and_register(self, record_id: Any, mpn: Optional[str], norm_mpn: Optional[str], 
                           mfg: Optional[str], brand: Optional[str], desc: Optional[str]) -> Dict[str, Any]:
        """
        Checks if the item is a duplicate of a previously registered item, then registers it.
        Returns:
            {
                "status": "UNIQUE" | "DUPLICATE" | "POSSIBLE_DUPLICATE",
                "duplicate_of": [list of prior record_ids]
            }
        """
        status = "UNIQUE"
        duplicate_of = []

        # 1. Check exact raw MPN
        if mpn and mpn in self.exact_mpn_map:
            # If raw MPN is identical, we check if manufacturer matches
            prior_ids = self.exact_mpn_map[mpn]
            for pid in prior_ids:
                duplicate_of.append(pid)
            status = "DUPLICATE"

        # 2. Check normalized MPN
        elif norm_mpn and norm_mpn in self.norm_mpn_map:
            prior_ids = self.norm_mpn_map[norm_mpn]
            for pid in prior_ids:
                duplicate_of.append(pid)
            status = "POSSIBLE_DUPLICATE"

        # 3. Check manufacturer + MPN combo
        elif mfg and norm_mpn:
            sig = (mfg.lower(), norm_mpn)
            if sig in self.mfg_mpn_map:
                prior_ids = self.mfg_mpn_map[sig]
                for pid in prior_ids:
                    duplicate_of.append(pid)
                status = "DUPLICATE"

        # 4. Check brand + MPN combo
        elif brand and norm_mpn:
            sig = (brand.lower(), norm_mpn)
            if sig in self.brand_mpn_map:
                prior_ids = self.brand_mpn_map[sig]
                for pid in prior_ids:
                    duplicate_of.append(pid)
                status = "DUPLICATE"

        # 5. Check description fuzzy similarity (high similarity fallback)
        if status == "UNIQUE" and desc and len(desc) > 10:
            for pid, prior_desc in self.desc_list:
                if len(prior_desc) > 10:
                    sim = fuzz.token_set_ratio(desc, prior_desc)
                    if sim >= 95:
                        duplicate_of.append(pid)
                        status = "POSSIBLE_DUPLICATE"
                        break

        # Register the values in the maps for future checks
        if mpn:
            if mpn not in self.exact_mpn_map:
                self.exact_mpn_map[mpn] = []
            self.exact_mpn_map[mpn].append(record_id)
            
        if norm_mpn:
            if norm_mpn not in self.norm_mpn_map:
                self.norm_mpn_map[norm_mpn] = []
            self.norm_mpn_map[norm_mpn].append(record_id)

        if mfg and norm_mpn:
            sig = (mfg.lower(), norm_mpn)
            if sig not in self.mfg_mpn_map:
                self.mfg_mpn_map[sig] = []
            self.mfg_mpn_map[sig].append(record_id)

        if brand and norm_mpn:
            sig = (brand.lower(), norm_mpn)
            if sig not in self.brand_mpn_map:
                self.brand_mpn_map[sig] = []
            self.brand_mpn_map[sig].append(record_id)

        if desc:
            self.desc_list.append((record_id, desc))

        return {
            "status": status,
            "duplicate_of": list(set(duplicate_of))
        }

    @staticmethod
    def review_duplicate(prod_a: Any, prod_b: Any) -> Dict[str, Any]:
        """
        Classifies a candidate duplicate pair:
        - EXACT_DUPLICATE: Identical MPN, Brand, and Mfg.
        - LIKELY_DUPLICATE: Matches MPN/metadata but has minor desc or field variations.
        - LIKELY_VARIANT: High description similarity, but differs in length/size suffix in MPN.
        - UNRELATED: Complete mismatched MPN, Brand, or low similarity.
        """
        mpn_a = prod_a.identity.raw_mpn
        mpn_b = prod_b.identity.raw_mpn
        norm_a = prod_a.identity.normalized_mpn
        norm_b = prod_b.identity.normalized_mpn
        brand_a = prod_a.identity.brand
        brand_b = prod_b.identity.brand
        mfg_a = prod_a.identity.manufacturer
        mfg_b = prod_b.identity.manufacturer
        desc_a = prod_a.cleaned.part_desc.normalized_value or ""
        desc_b = prod_b.cleaned.part_desc.normalized_value or ""

        # Exact Matches
        if mpn_a == mpn_b and mpn_a is not None:
            if brand_a == brand_b and mfg_a == mfg_b:
                return {
                    "status": "EXACT_DUPLICATE",
                    "reasoning": "Identical MPN, Brand, and Manufacturer.",
                    "confidence": 1.0
                }
            return {
                "status": "LIKELY_DUPLICATE",
                "reasoning": "Identical MPN but metadata (Brand/Mfg) differs or is partially missing.",
                "confidence": 0.8
            }

        if norm_a == norm_b and norm_a is not None:
            return {
                "status": "EXACT_DUPLICATE",
                "reasoning": "Identical Normalized MPN.",
                "confidence": 0.95
            }

        # Check description similarity
        sim = fuzz.token_set_ratio(desc_a, desc_b)
        
        # Check if they are variant of same product family (e.g. 16' vs 20' decking)
        if sim > 90 and brand_a == brand_b and brand_a is not None:
            # Check for numeric suffix differences in MPN
            # e.g., ADB15516CS vs ADB15520CS
            diff_len = abs(len(str(mpn_a)) - len(str(mpn_b)))
            if diff_len <= 3:
                return {
                    "status": "LIKELY_VARIANT",
                    "reasoning": f"High description similarity ({sim}%) and same brand, but differing MPN suggests size/pack variant.",
                    "confidence": 0.85
                }
            return {
                "status": "LIKELY_VARIANT",
                "reasoning": f"High description similarity ({sim}%) suggests variants under the same product family.",
                "confidence": 0.8
            }

        if sim > 80:
            return {
                "status": "LIKELY_DUPLICATE",
                "reasoning": f"High description similarity ({sim}%) suggests potential duplicates despite different MPNs.",
                "confidence": 0.7
            }

        return {
            "status": "UNRELATED",
            "reasoning": f"Low description similarity ({sim}%) and different MPNs.",
            "confidence": 0.9
        }
