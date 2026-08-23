from typing import Dict, Any, Optional, List
from app.data.repositories.taxonomy_repository import TaxonomyRepository

class TaxonomyEngine:
    # Consistency mapping: valid classes for each department
    DEPARTMENT_TO_CLASSES = {
        "Building Materials": [
            "Abrasives", "Adhesives & Tape", "Decking & Railing", "Doors & Windows", 
            "Drywall & Plaster", "Lumber & Composite", "Siding & Soffit", "Insulation"
        ],
        "Appliances": [
            "Large Appliances", "Kitchen Appliances", "Laundry"
        ],
        "Electrical": [
            "Lighting & Fans", "Power Distribution", "Wiring Devices"
        ],
        "Tools": [
            "Power Tool Accessories", "Hand Tools", "Power Tools", "Woodworking"
        ],
        "Safety": [
            "Personal Protective Equipment", "Fire Protection"
        ],
        "Hardware": [
            "Fasteners"
        ]
    }

    def __init__(self, repo: TaxonomyRepository):
        self.repo = repo

    def classify(self, part_desc: Optional[str], product_type: Optional[str], 
                 brand: Optional[str] = None, manufacturer: Optional[str] = None) -> Dict[str, Any]:
        """
        Classifies a product using deterministic signals (Stage 1), 
        semantic LLM fallback (Stage 2), and logical consistency validation (Stage 3).
        """
        # --- Stage 1: Deterministic Signals ---
        taxonomy_info = self.repo.get_taxonomy(product_type)
        method = "rule"
        confidence = 0.9 if product_type and product_type != "UNKNOWN" else 0.0
        status = "INFERRED" if not self.repo.mode_a else "VERIFIED"
        evidence = f"Matched detected product type '{product_type}' against taxonomy map."

        # --- Stage 2: Semantic/LLM Fallback (Stubbed/Mocked Interface) ---
        if not taxonomy_info and part_desc:
            # Stage 2 fuzzy keyword mapping for unmatched cases
            desc_lower = part_desc.lower()
            if "dryer" in desc_lower:
                taxonomy_info = self.repo.get_taxonomy("Dryer")
                evidence = "Inferred category 'Dryer' from description token."
            elif "washer" in desc_lower:
                taxonomy_info = self.repo.get_taxonomy("Washer")
                evidence = "Inferred category 'Washer' from description token."
            elif "outlet" in desc_lower or "receptacle" in desc_lower:
                taxonomy_info = self.repo.get_taxonomy("Outlet / Switch")
                evidence = "Inferred category 'Outlet / Switch' from description token."
            elif "light" in desc_lower or "lamp" in desc_lower or "chandelier" in desc_lower:
                taxonomy_info = self.repo.get_taxonomy("Lighting Fixture")
                evidence = "Inferred category 'Lighting Fixture' from description token."
            
            if taxonomy_info:
                method = "semantic"
                confidence = 0.7
                status = "INFERRED"

        # If still not classified, mark unknown
        if not taxonomy_info:
            return {
                "department": None,
                "class_name": None,
                "fine": None,
                "classpath": None,
                "product_type": product_type,
                "product_family": None,
                "confidence": 0.0,
                "status": "UNKNOWN",
                "method": "unknown",
                "evidence": "No matching taxonomy nodes found for product type or description."
            }

        dept = taxonomy_info.get("department")
        cls_name = taxonomy_info.get("class")
        fine = taxonomy_info.get("fine")
        classpath = taxonomy_info.get("classpath")

        # --- Stage 3: Consistency Validation ---
        valid_classes = self.DEPARTMENT_TO_CLASSES.get(dept, [])
        if cls_name and cls_name not in valid_classes:
            status = "CONFLICTED"
            confidence = 0.3
            evidence = f"Inconsistent taxonomy path: class '{cls_name}' is invalid for department '{dept}'."

        return {
            "department": dept,
            "class_name": cls_name,
            "fine": fine,
            "classpath": classpath,
            "product_type": product_type,
            "product_family": f"{brand} {product_type}" if brand else product_type,
            "confidence": round(confidence, 2),
            "status": status,
            "method": method,
            "evidence": evidence
        }
