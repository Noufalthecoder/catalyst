import re
from typing import Dict, Optional, Tuple, List

class MPNParser:
    # Common series names to look for in descriptions
    KNOWN_SERIES = [
        "Cubitron II", "Steel Demon", "Speed Demon", "Performance+", "Ceramic+", "Diablo", "Classic",
        "Vintage Azek", "Landmark Azek", "Harvest Azek", "Transcend Lineage", "Transcend", "Enhance Naturals",
        "Enhance Basics", "Enhance", "Select 2.0", "Select", "Elite", "Heritage", "ecoLitePlus", "ecoLite",
        "Duration", "TruDef", "SmartSide", "Blue Plus", "Zip R6.6", "Zip R3.6", "Zip R9.6", "Fine Fissured",
        "M12", "M18", "Surge", "Fuel", "LXT", "Starfish", "Steff", "Align-A-Saw", "Stealthstop", "JWBS",
        "T-Glide", "BIGCAL", "Pro Heated", "Aerial Snow", "Slyde King"
    ]

    @staticmethod
    def normalize_mpn(mpn: str) -> str:
        """
        Normalizes the MPN for matching and standard display:
        - Strips whitespace
        - Converts to uppercase
        - Keeps hyphens, dots, and slashes as requested.
        """
        if not mpn:
            return ""
        return mpn.strip().upper()

    @classmethod
    def parse(cls, mfg_part_num: Optional[str], part_desc: Optional[str]) -> Dict[str, Optional[str]]:
        """
        Parses the raw MPN and description to identify:
        - raw_mpn
        - normalized_mpn
        - alternate_mpn
        - series
        - model
        """
        raw_mpn = mfg_part_num.strip() if mfg_part_num else None
        normalized_mpn = cls.normalize_mpn(raw_mpn) if raw_mpn else None
        alternate_mpn = None
        series = None
        model = None

        if not part_desc:
            return {
                "raw_mpn": raw_mpn,
                "normalized_mpn": normalized_mpn,
                "alternate_mpn": alternate_mpn,
                "series": series,
                "model": model
            }

        # Try to find alternate MPN in part_desc
        # e.g., "Replaces XXXXX" or "ALT: XXXXX" or bracketed numbers
        alt_patterns = [
            r"(?:replaces|alt|alternate|repl)\s*[:#-]?\s*([A-Z0-9\-\.\/]+)",
            r"\((?:replaces|alt|alternate|repl)\s*[:#-]?\s*([A-Z0-9\-\.\/]+)\)",
        ]
        for pattern in alt_patterns:
            match = re.search(pattern, part_desc, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                if val != raw_mpn:
                    alternate_mpn = val
                    break

        # Detect series
        for known_s in cls.KNOWN_SERIES:
            if re.search(r'\b' + re.escape(known_s) + r'\b', part_desc, re.IGNORECASE):
                series = known_s
                break

        # Detect model from description
        # If there's an identifier that looks like a model and is different from the MPN
        # e.g., "Grizzly G0771Z" -> G0771Z is the model if the raw_mpn is T27417 or similar.
        # Let's search for sequences of letters and numbers that might be a model
        words = part_desc.split()
        for word in words:
            word_clean = re.sub(r'[^\w\-\.\/]', '', word)
            # A model is usually alphanumeric, >= 4 chars, and contains numbers
            if (len(word_clean) >= 4 and 
                any(c.isdigit() for c in word_clean) and 
                any(c.isalpha() for c in word_clean) and
                word_clean != raw_mpn):
                model = word_clean
                break

        return {
            "raw_mpn": raw_mpn,
            "normalized_mpn": normalized_mpn,
            "alternate_mpn": alternate_mpn,
            "series": series,
            "model": model
        }
