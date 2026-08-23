import re
from typing import Dict, Any, Optional, List

class ProductDescriptionParser:
    @staticmethod
    def parse(part_desc: Optional[str]) -> Dict[str, Any]:
        """
        Deep description parser for specifications, packaging, technology, and measurements.
        """
        results = {
            "brand": None,
            "series": None,
            "product_noun": None,
            "grit": None,
            "technology": None,
            "packaging_qty": None,
            "packaging_uom": None,
            "quantity": None,
            "dimensions": None,
            "voltage": None,
            "amperage": None,
            "material": None,
            "color": None,
            "application": None,
            "compatibility": None
        }

        if not part_desc:
            return results

        # 1. Grit (e.g. P150, P120, P80, 220 Grit)
        grit_match = re.search(r'\b(P\d+|\d+\s*Grit)\b', part_desc, re.IGNORECASE)
        if grit_match:
            results["grit"] = grit_match.group(1)

        # 2. Technology (e.g. Cubitron II)
        tech_match = re.search(r'\b(Cubitron(?:\s+II)?|Steel\s+Demon|Speed\s+Demon|Powerpack)\b', part_desc, re.IGNORECASE)
        if tech_match:
            results["technology"] = tech_match.group(1)

        # 3. Packaging Qty & UOM (e.g. 50 Disc/Box, 6pc)
        pkg_match = re.search(r'\b(\d+)\s*(Disc/Box|Sheets/Box|pc|pk|ct|pack|box|pairs?|pair)\b', part_desc, re.IGNORECASE)
        if pkg_match:
            results["packaging_qty"] = pkg_match.group(1)
            results["packaging_uom"] = pkg_match.group(2)
            results["quantity"] = pkg_match.group(0)
        else:
            # Fallback for simple qty like "6pc"
            qty_match = re.search(r'\b(\d+)\s*(?:pc|pk|ct|pack)\b', part_desc, re.IGNORECASE)
            if qty_match:
                results["packaging_qty"] = qty_match.group(1)
                results["quantity"] = qty_match.group(0)

        # 4. Brand extraction fallback
        brands = ["3M", "Diablo", "Milwaukee", "Makita", "DEWALT", "GE", "Speed Queen", "CertainTeed", "LP SmartSide"]
        for b in brands:
            if re.search(r'\b' + re.escape(b) + r'\b', part_desc, re.IGNORECASE):
                results["brand"] = b
                break

        # 5. Noun / Product Type
        nouns = ["Dishwasher", "Dryer", "Washer", "Film", "Belt", "Disc", "Sponge", "Wheel", "Blade", "Cable", "Wire", "Timer", "Dimmer", "Bulb"]
        for n in nouns:
            if re.search(r'\b' + re.escape(n) + r'\s*\b', part_desc, re.IGNORECASE):
                results["product_noun"] = n
                break

        # 6. Dimensions (e.g. 1/2"x18", 6'x36", 5")
        dim_patterns = [
            r'\b\d+(?:/\d+)?\s*(?:\"|\'|in|ft|mm)?\s*[xX]\s*\d+(?:/\d+)?\s*(?:\"|\'|in|ft|mm)?\b',
            r'\b\d+(?:\.\d+)?\s*(?:\"|\'|in|ft|mm)\b'
        ]
        dims = []
        for pattern in dim_patterns:
            matches = re.findall(pattern, part_desc)
            if matches:
                dims.extend(matches)
        if dims:
            results["dimensions"] = ", ".join(dims)

        # 7. Voltage
        volt_match = re.search(r'\b(\d+(?:\.\d+)?)\s*V\b', part_desc, re.IGNORECASE)
        if volt_match:
            results["voltage"] = f"{volt_match.group(1)}V"

        # 8. Amperage / Power
        amp_match = re.search(r'\b(\d+(?:\.\d+)?)\s*(?:A|AH)\b', part_desc, re.IGNORECASE)
        if amp_match:
            results["amperage"] = f"{amp_match.group(1)}A"
        else:
            hp_match = re.search(r'\b(\d+(?:\.\d+)?)\s*HP\b', part_desc, re.IGNORECASE)
            if hp_match:
                results["amperage"] = f"{hp_match.group(1)}HP"

        # 9. Material
        materials = ["Stainless Steel", "Steel", "Aluminum", "Composite", "Vinyl", "PVC", "OSB", "Brass"]
        for m in materials:
            if re.search(r'\b' + re.escape(m) + r'\b', part_desc, re.IGNORECASE):
                results["material"] = m
                break

        # 10. Color
        colors = ["White", "Black", "Gray", "Charcoal", "Brownstone", "Slate Gray", "Clay"]
        for c in colors:
            if re.search(r'\b' + re.escape(c) + r'\b', part_desc, re.IGNORECASE):
                results["color"] = c
                break

        # 11. Application / Compatibility
        if "for metal" in part_desc.lower() or "metal cutting" in part_desc.lower():
            results["application"] = "Metal Cutting"
        elif "masonry" in part_desc.lower():
            results["application"] = "Masonry Cutting"
        elif "decking" in part_desc.lower():
            results["application"] = "Decking"

        return results

    @classmethod
    def parse_ai(cls, part_desc: Optional[str]) -> Dict[str, Any]:
        return cls.parse(part_desc)

    @staticmethod
    def second_pass_extract(content_text: str, label: str, val_type: str) -> Optional[str]:
        """
        Searches specific text windows in the source document around relevant keywords
        to locate missing attributes.
        """
        if not content_text:
            return None
            
        # Target keywords based on the attribute label
        keywords = [label.lower()]
        if label.lower() == "voltage":
            keywords.extend(["volt", "v", "power"])
        elif label.lower() == "amperage":
            keywords.extend(["amp", "a", "ah", "current"])
        elif label.lower() == "grit":
            keywords.extend(["grit", "p", "grain"])
        elif label.lower() == "material":
            keywords.extend(["material", "construction", "finish"])
        elif label.lower() == "pack qty":
            keywords.extend(["pack", "qty", "count", "pcs", "piece"])

        for kw in keywords:
            # Find occurrences of keyword and extract a 50-character window
            for match in re.finditer(r'\b' + re.escape(kw) + r'\b', content_text, re.IGNORECASE):
                start = max(0, match.start() - 10)
                end = min(len(content_text), match.end() + 45)
                window = content_text[start:end]
                
                # Check for value matching the expected type in the window
                if val_type in ["INTEGER", "QUANTITY"]:
                    num_match = re.search(r'\b\d+\b', window)
                    if num_match:
                        return num_match.group(0)
                elif val_type in ["DECIMAL", "MEASUREMENT"]:
                    num_match = re.search(r'\b\d+(?:\.\d+)?\b', window)
                    if num_match:
                        return num_match.group(0)
                elif val_type == "BOOLEAN":
                    bool_match = re.search(r'\b(yes|no|true|false)\b', window, re.IGNORECASE)
                    if bool_match:
                        return bool_match.group(1)
                else:
                    # Text/generic lookup
                    val_match = re.search(r'\b' + re.escape(kw) + r'\s*[:\-\s]\s*([a-zA-Z0-9\-\.\/]+)\b', window, re.IGNORECASE)
                    if val_match:
                        return val_match.group(1).strip()
        return None
