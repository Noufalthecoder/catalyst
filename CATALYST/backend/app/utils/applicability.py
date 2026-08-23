from typing import Optional
from app.utils.attribute_schema import AttributeSchemaEngine

class AttributeApplicabilityEngine:
    @staticmethod
    def evaluate_applicability(product_type: Optional[str], fine_class: Optional[str], 
                               attribute_label: str) -> str:
        """
        Determines whether a given attribute is relevant/applicable to the product category.
        Returns: APPLICABLE, NOT_APPLICABLE, or UNCERTAIN.
        """
        if not product_type or product_type == "UNKNOWN":
            return "UNCERTAIN"

        category = fine_class or "Abrasives"
        expected_schema = AttributeSchemaEngine.generate_schema(category)
        
        # Build lookup set of expected labels
        expected_labels = {a.label.strip().lower() for a in expected_schema}

        # Some attributes are universally applicable (e.g. Dimensions, Weight, Brand)
        universal_labels = {
            "length", "width", "height", "weight", "volume", "brand", 
            "material", "color", "pack qty", "application", "grit", 
            "voltage", "amperage", "technology", "series"
        }
        
        label_clean = attribute_label.strip().lower()
        if label_clean in expected_labels or label_clean in universal_labels:
            return "APPLICABLE"

        # Explicitly flag mismatched attributes
        return "NOT_APPLICABLE"
