from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AttributeDefinition(BaseModel):
    label: str
    value_type: str  # numeric, text, boolean
    uom: Optional[str] = None
    required: bool = False
    source_priority: List[str] = Field(default_factory=lambda: ["manufacturer", "technical_document", "input_description"])
    extraction_strategy: str = "regex_then_llm"
    attribute_type: str = "STANDARD_ATTRIBUTE"  # STANDARD_ATTRIBUTE or UNILOG_CONTROLLED_ATTRIBUTE

class AttributeSchemaEngine:
    # Schema templates per Class
    SCHEMAS_BY_CLASS = {
        "Abrasives": [
            AttributeDefinition(label="Grit", value_type="text"),
            AttributeDefinition(label="Diameter", value_type="numeric", uom="in"),
            AttributeDefinition(label="Length", value_type="numeric", uom="in"),
            AttributeDefinition(label="Width", value_type="numeric", uom="in"),
            AttributeDefinition(label="Material", value_type="text"),
            AttributeDefinition(label="Pack Qty", value_type="numeric")
        ],
        "Large Appliances": [
            AttributeDefinition(label="Voltage", value_type="numeric", uom="V"),
            AttributeDefinition(label="Amperage", value_type="numeric", uom="A"),
            AttributeDefinition(label="Finish", value_type="text"),
            AttributeDefinition(label="Mounting Type", value_type="text"),
            AttributeDefinition(label="Capacity", value_type="text"),
            AttributeDefinition(label="Sound Level", value_type="numeric", uom="dBA"),
            AttributeDefinition(label="Energy Star Certified", value_type="boolean", attribute_type="UNILOG_CONTROLLED_ATTRIBUTE")
        ],
        "Kitchen Appliances": [
            AttributeDefinition(label="Voltage", value_type="numeric", uom="V"),
            AttributeDefinition(label="Amperage", value_type="numeric", uom="A"),
            AttributeDefinition(label="Finish", value_type="text"),
            AttributeDefinition(label="Capacity", value_type="text"),
            AttributeDefinition(label="Energy Star Certified", value_type="boolean", attribute_type="UNILOG_CONTROLLED_ATTRIBUTE")
        ],
        "Decking & Railing": [
            AttributeDefinition(label="Length", value_type="numeric", uom="ft"),
            AttributeDefinition(label="Width", value_type="numeric", uom="in"),
            AttributeDefinition(label="Thickness", value_type="numeric", uom="in"),
            AttributeDefinition(label="Color", value_type="text"),
            AttributeDefinition(label="Material", value_type="text"),
            AttributeDefinition(label="Profile", value_type="text", attribute_type="UNILOG_CONTROLLED_ATTRIBUTE")
        ],
        "Lighting & Fans": [
            AttributeDefinition(label="Voltage", value_type="numeric", uom="V"),
            AttributeDefinition(label="Wattage", value_type="numeric", uom="W"),
            AttributeDefinition(label="Color Temperature", value_type="numeric", uom="K"),
            AttributeDefinition(label="Luminous Flux", value_type="numeric", uom="lm"),
            AttributeDefinition(label="Dimmable", value_type="boolean"),
            AttributeDefinition(label="Bulb Base", value_type="text", attribute_type="UNILOG_CONTROLLED_ATTRIBUTE")
        ],
        "Fasteners": [
            AttributeDefinition(label="Length", value_type="numeric", uom="in"),
            AttributeDefinition(label="Gauge", value_type="numeric", uom="GA"),
            AttributeDefinition(label="Shank Diameter", value_type="numeric", uom="in"),
            AttributeDefinition(label="Material", value_type="text"),
            AttributeDefinition(label="Pack Qty", value_type="numeric")
        ]
    }

    # Fallback default schema for other classes
    DEFAULT_SCHEMA = [
        AttributeDefinition(label="Voltage", value_type="numeric", uom="V"),
        AttributeDefinition(label="Amperage", value_type="numeric", uom="A"),
        AttributeDefinition(label="Material", value_type="text"),
        AttributeDefinition(label="Color", value_type="text"),
        AttributeDefinition(label="Pack Qty", value_type="numeric")
    ]

    @classmethod
    def generate_schema(cls, class_name: Optional[str]) -> List[AttributeDefinition]:
        """
        Dynamically returns the list of expected attributes for a given taxonomy class.
        """
        if not class_name:
            return cls.DEFAULT_SCHEMA

        return cls.SCHEMAS_BY_CLASS.get(class_name, cls.DEFAULT_SCHEMA)
