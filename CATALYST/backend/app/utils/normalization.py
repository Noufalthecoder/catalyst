from typing import Any, Dict, Optional, Tuple, List
import re
from app.models.product import ProductAttribute

class AttributeNormalizationEngine:
    UOM_MAP = {
        "inch": "in",
        "inches": "in",
        "\"": "in",
        "foot": "ft",
        "feet": "ft",
        "'": "ft",
        "volt": "V",
        "volts": "V",
        "v": "V",
        "amp": "A",
        "amps": "A",
        "a": "A",
        "pound": "lb",
        "pounds": "lb",
        "lbs": "lb"
    }

    @classmethod
    def normalize_uom(cls, raw_uom: str) -> Optional[str]:
        if not raw_uom:
            return None
        cleaned = raw_uom.strip().lower()
        return cls.UOM_MAP.get(cleaned, raw_uom.strip())

    @staticmethod
    def decimal_to_fraction(val: float) -> str:
        """
        Converts decimal values to exact industrial fractions where mathematically safe.
        """
        whole = int(val)
        rem = round(val - whole, 4)
        if rem == 0:
            return str(whole)
        
        # Standard industrial fraction mappings
        frac_map = {
            0.5: "1/2",
            0.25: "1/4",
            0.75: "3/4",
            0.125: "1/8",
            0.375: "3/8",
            0.625: "5/8",
            0.875: "7/8",
            0.0625: "1/16",
            0.1875: "3/16",
            0.3125: "5/16",
            0.4375: "7/16",
            0.5625: "9/16",
            0.6875: "11/16",
            0.8125: "13/16",
            0.9375: "15/16"
        }
        
        if rem in frac_map:
            frac = frac_map[rem]
            return f"{whole}-{frac}" if whole > 0 else frac
        return str(val)

    @classmethod
    def normalize_dimension(cls, val_str: str) -> Tuple[Optional[str], Optional[float], Optional[str]]:
        """
        Normalizes dimension strings like '50.25 in' or '50-1/4"' to:
        (normalized_fractional_value, numeric_value, uom)
        """
        if not val_str:
            return None, None, None

        # Clean spaces
        cleaned = val_str.strip()
        
        # Parse value and UOM e.g. "50.25 in", "1/2\"", "0.5"
        match = re.match(r'^([\d\-/\.]+)\s*([a-zA-Z\"\'\s]+)?$', cleaned)
        if not match:
            return cleaned, None, None

        raw_val = match.group(1)
        raw_uom = match.group(2)
        
        uom = cls.normalize_uom(raw_uom) if raw_uom else None

        # Parse numeric value
        numeric_val = None
        if "-" in raw_val:
            # Mixed fraction e.g. 50-1/4
            parts = raw_val.split("-")
            if len(parts) == 2:
                try:
                    whole = float(parts[0])
                    frac_parts = parts[1].split("/")
                    if len(frac_parts) == 2:
                        numeric_val = whole + (float(frac_parts[0]) / float(frac_parts[1]))
                except ValueError:
                    pass
        elif "/" in raw_val:
            # Simple fraction e.g. 1/2
            parts = raw_val.split("/")
            if len(parts) == 2:
                try:
                    numeric_val = float(parts[0]) / float(parts[1])
                except ValueError:
                    pass
        else:
            # Decimal or integer e.g. 50.25
            try:
                numeric_val = float(raw_val)
            except ValueError:
                pass

        # Generate normalized fractional representation
        normalized_str = raw_val
        if numeric_val is not None:
            normalized_str = cls.decimal_to_fraction(numeric_val)
            if uom:
                normalized_str = f"{normalized_str} {uom}"

        return normalized_str, numeric_val, uom

    @classmethod
    def validate_and_normalize(cls, attr: ProductAttribute, expected_type: str) -> ProductAttribute:
        """
        Validates attribute value types and normalizes their formats.
        Expected types: TEXT, BOOLEAN, QUANTITY, MEASUREMENT, MEASUREMENT_RANGE,
        FRACTION, MIXED_MEASUREMENT, PACKAGING, ELECTRICAL_RATING, DECIBEL_RATING, ENUM
        """
        if attr.value is None:
            attr.status = "UNKNOWN"
            return attr

        val_str = str(attr.value).strip()
        attr.raw_value = val_str

        t_clean = expected_type.upper().strip()
        if t_clean in ["INTEGER", "DECIMAL"]:
            t_clean = "QUANTITY"

        # 1. TEXT validation is always valid
        if t_clean == "TEXT":
            attr.normalized_value = val_str
            attr.status = "VERIFIED" if attr.status != "CONFLICTED" else "CONFLICTED"
            return attr

        # 2. BOOLEAN validation
        if t_clean == "BOOLEAN":
            val_lower = val_str.lower()
            if val_lower in ["yes", "true", "1"]:
                attr.normalized_value = True
                attr.status = "VERIFIED"
            elif val_lower in ["no", "false", "0"]:
                attr.normalized_value = False
                attr.status = "VERIFIED"
            else:
                attr.status = "INVALID"
            return attr

        # 3. QUANTITY validation
        if t_clean == "QUANTITY":
            # Handles integers, decimals or counts
            num_match = re.search(r'\b\d+(?:\.\d+)?\b', val_str)
            if num_match:
                val_num = float(num_match.group(0))
                attr.normalized_value = int(val_num) if val_num.is_integer() else val_num
                attr.status = "VERIFIED"
            else:
                attr.status = "INVALID"
            return attr

        # 4. MEASUREMENT / FRACTION / MIXED_MEASUREMENT
        if t_clean in ["MEASUREMENT", "FRACTION", "MIXED_MEASUREMENT"]:
            norm_val, num_val, uom = cls.normalize_dimension(val_str)
            if num_val is not None:
                attr.normalized_value = norm_val
                attr.uom = uom
                attr.status = "VERIFIED"
            else:
                attr.status = "INVALID"
            return attr

        # 5. ELECTRICAL_RATING (e.g. 20 V MAX, 120 VAC, 15 A)
        if t_clean == "ELECTRICAL_RATING":
            # Match number followed by V, VAC, A, Amps etc.
            elec_match = re.search(r'\b(\d+(?:\.\d+)?)\s*(V|VAC|VDC|A|Amps|Amp|Ah|mAh)\b', val_str, re.IGNORECASE)
            if elec_match:
                val_num = elec_match.group(1)
                uom = cls.normalize_uom(elec_match.group(2))
                attr.normalized_value = f"{val_num} {uom}"
                attr.uom = uom
                attr.status = "VERIFIED"
            else:
                attr.status = "INVALID"
            return attr

        # 6. DECIBEL_RATING (e.g. 47 dBA, 47 db)
        if t_clean == "DECIBEL_RATING":
            db_match = re.search(r'\b(\d+(?:\.\d+)?)\s*(dBA|dB|db)\b', val_str, re.IGNORECASE)
            if db_match:
                attr.normalized_value = f"{db_match.group(1)} dBA"
                attr.uom = "dBA"
                attr.status = "VERIFIED"
            else:
                attr.status = "INVALID"
            return attr

        # 7. PACKAGING (e.g. 50 Disc/Box, 5-pack, 6pc)
        if t_clean == "PACKAGING":
            pkg_match = re.search(r'\b(\d+)\s*(Disc/Box|Sheets/Box|pc|pk|ct|pack|box|pair|pairs)\b', val_str, re.IGNORECASE)
            if pkg_match:
                attr.normalized_value = f"{pkg_match.group(1)} {pkg_match.group(2)}"
                attr.status = "VERIFIED"
            else:
                pkg_match_2 = re.search(r'\b(\d+)\s*-\s*(pack)\b', val_str, re.IGNORECASE)
                if pkg_match_2:
                    attr.normalized_value = f"{pkg_match_2.group(1)}-pack"
                    attr.status = "VERIFIED"
                else:
                    attr.status = "INVALID"
            return attr

        # 8. ENUM / RANGE / MEASUREMENT_RANGE
        if t_clean in ["ENUM", "RANGE", "MEASUREMENT_RANGE"]:
            attr.normalized_value = val_str
            attr.status = "VERIFIED"
            return attr

        attr.status = "INVALID"
        return attr
