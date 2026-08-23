from typing import Dict, Any, Optional
import pandas as pd
from pathlib import Path

class TaxonomyRepository:
    # Mode B static inferred tree mappings based on product_type
    DEFAULT_TAXONOMY_MAP = {
        "Sanding Product": {
            "department": "Building Materials",
            "class": "Abrasives",
            "fine": "Sanding Products",
            "classpath": "Building Materials > Abrasives > Sanding Products"
        },
        "Abrasive Wheel": {
            "department": "Building Materials",
            "class": "Abrasives",
            "fine": "Grinding & Cut-Off Wheels",
            "classpath": "Building Materials > Abrasives > Grinding & Cut-Off Wheels"
        },
        "Tape": {
            "department": "Building Materials",
            "class": "Adhesives & Tape",
            "fine": "Tapes",
            "classpath": "Building Materials > Adhesives & Tape > Tapes"
        },
        "Dishwasher": {
            "department": "Appliances",
            "class": "Large Appliances",
            "fine": "Built-In Dishwashers",
            "classpath": "Appliances & Consumer Electronics > Kitchen Appliances > Built-In Dishwashers"
        },
        "Dryer": {
            "department": "Appliances",
            "class": "Large Appliances",
            "fine": "Dryers",
            "classpath": "Appliances & Consumer Electronics > Laundry > Dryers"
        },
        "Washer": {
            "department": "Appliances",
            "class": "Large Appliances",
            "fine": "Washers",
            "classpath": "Appliances & Consumer Electronics > Laundry > Washers"
        },
        "Laundry Center": {
            "department": "Appliances",
            "class": "Large Appliances",
            "fine": "Laundry Centers",
            "classpath": "Appliances & Consumer Electronics > Laundry > Laundry Centers"
        },
        "Ceiling Fan": {
            "department": "Electrical",
            "class": "Lighting & Fans",
            "fine": "Ceiling Fans",
            "classpath": "Electrical > Lighting & Fans > Ceiling Fans"
        },
        "Lighting Fixture": {
            "department": "Electrical",
            "class": "Lighting & Fans",
            "fine": "Lighting Fixtures",
            "classpath": "Electrical > Lighting & Fans > Lighting Fixtures"
        },
        "Light Bulb": {
            "department": "Electrical",
            "class": "Lighting & Fans",
            "fine": "Light Bulbs",
            "classpath": "Electrical > Lighting & Fans > Light Bulbs"
        },
        "Portable Light": {
            "department": "Electrical",
            "class": "Lighting & Fans",
            "fine": "Flashlights & Work Lights",
            "classpath": "Electrical > Lighting & Fans > Flashlights & Work Lights"
        },
        "Power Tool Battery / Charger": {
            "department": "Tools",
            "class": "Power Tool Accessories",
            "fine": "Batteries & Chargers",
            "classpath": "Tools > Power Tool Accessories > Batteries & Chargers"
        },
        "Measuring / Layout Tool": {
            "department": "Tools",
            "class": "Hand Tools",
            "fine": "Measuring Tools",
            "classpath": "Tools > Hand Tools > Measuring Tools"
        },
        "Safety Glasses": {
            "department": "Safety",
            "class": "Personal Protective Equipment",
            "fine": "Eye Protection",
            "classpath": "Safety > Personal Protective Equipment > Eye Protection"
        },
        "Heated Apparel": {
            "department": "Safety",
            "class": "Personal Protective Equipment",
            "fine": "Heated Workwear",
            "classpath": "Safety > Personal Protective Equipment > Heated Workwear"
        },
        "Sander": {
            "department": "Tools",
            "class": "Power Tools",
            "fine": "Sanders",
            "classpath": "Tools > Power Tools > Sanders"
        },
        "Saw / Cutting Tool": {
            "department": "Tools",
            "class": "Power Tools",
            "fine": "Saws",
            "classpath": "Tools > Power Tools > Saws"
        },
        "Outlet / Switch": {
            "department": "Electrical",
            "class": "Wiring Devices",
            "fine": "Outlets & Switches",
            "classpath": "Electrical > Wiring Devices > Outlets & Switches"
        },
        "Microwave": {
            "department": "Appliances",
            "class": "Kitchen Appliances",
            "fine": "Microwaves",
            "classpath": "Appliances & Consumer Electronics > Kitchen Appliances > Microwaves"
        },
        "Range": {
            "department": "Appliances",
            "class": "Kitchen Appliances",
            "fine": "Ranges",
            "classpath": "Appliances & Consumer Electronics > Kitchen Appliances > Ranges"
        },
        "Refrigerator / Freezer": {
            "department": "Appliances",
            "class": "Kitchen Appliances",
            "fine": "Refrigerators & Freezers",
            "classpath": "Appliances & Consumer Electronics > Kitchen Appliances > Refrigerators & Freezers"
        },
        "Decking Board": {
            "department": "Building Materials",
            "class": "Decking & Railing",
            "fine": "Decking Boards",
            "classpath": "Building Materials > Decking & Railing > Decking Boards"
        },
        "Fascia Board": {
            "department": "Building Materials",
            "class": "Decking & Railing",
            "fine": "Fascia Boards",
            "classpath": "Building Materials > Decking & Railing > Fascia Boards"
        },
        "Railing Accessory": {
            "department": "Building Materials",
            "class": "Decking & Railing",
            "fine": "Railing Accessories",
            "classpath": "Building Materials > Decking & Railing > Railing Accessories"
        },
        "Post Accessory": {
            "department": "Building Materials",
            "class": "Decking & Railing",
            "fine": "Post Accessories",
            "classpath": "Building Materials > Decking & Railing > Post Accessories"
        },
        "Door / Window / Skylight": {
            "department": "Building Materials",
            "class": "Doors & Windows",
            "fine": "Doors & Windows",
            "classpath": "Building Materials > Doors & Windows > Doors & Windows"
        },
        "Drywall": {
            "department": "Building Materials",
            "class": "Drywall & Plaster",
            "fine": "Drywall Panels",
            "classpath": "Building Materials > Drywall & Plaster > Drywall Panels"
        },
        "Fastener (Nails/Staples)": {
            "department": "Hardware",
            "class": "Fasteners",
            "fine": "Collation Nails & Staples",
            "classpath": "Hardware > Fasteners > Collation Nails & Staples"
        },
        "Load Center": {
            "department": "Electrical",
            "class": "Power Distribution",
            "fine": "Load Centers",
            "classpath": "Electrical > Power Distribution > Load Centers"
        },
        "Lumber": {
            "department": "Building Materials",
            "class": "Lumber & Composite",
            "fine": "Dimensional Lumber",
            "classpath": "Building Materials > Lumber & Composite > Dimensional Lumber"
        },
        "Siding / Soffit Panel": {
            "department": "Building Materials",
            "class": "Siding & Soffit",
            "fine": "Siding & Soffit Panels",
            "classpath": "Building Materials > Siding & Soffit > Siding & Soffit Panels"
        },
        "Insulation Board": {
            "department": "Building Materials",
            "class": "Insulation",
            "fine": "Rigid Foam Insulation",
            "classpath": "Building Materials > Insulation > Rigid Foam Insulation"
        },
        "Coffee / Espresso Maker": {
            "department": "Appliances",
            "class": "Kitchen Appliances",
            "fine": "Coffee Makers",
            "classpath": "Appliances & Consumer Electronics > Kitchen Appliances > Coffee Makers"
        },
        "Measuring Tool": {
            "department": "Tools",
            "class": "Hand Tools",
            "fine": "Measuring Tools",
            "classpath": "Tools > Hand Tools > Measuring Tools"
        },
        "Safety Glasses": {
            "department": "Safety",
            "class": "Personal Protective Equipment",
            "fine": "Eye Protection",
            "classpath": "Safety > Personal Protective Equipment > Eye Protection"
        },
        "Fire Extinguisher": {
            "department": "Safety",
            "class": "Fire Protection",
            "fine": "Fire Extinguishers",
            "classpath": "Safety > Fire Protection > Fire Extinguishers"
        },
        "Smoke Detector": {
            "department": "Safety",
            "class": "Fire Protection",
            "fine": "Smoke Detectors",
            "classpath": "Safety > Fire Protection > Smoke Detectors"
        },
        "Drilling / Router Accessory": {
            "department": "Tools",
            "class": "Power Tool Accessories",
            "fine": "Drilling & Routing Accessories",
            "classpath": "Tools > Power Tool Accessories > Drilling & Routing Accessories"
        },
        "Saw Blade": {
            "department": "Tools",
            "class": "Power Tool Accessories",
            "fine": "Saw Blades",
            "classpath": "Tools > Power Tool Accessories > Saw Blades"
        },
        "Woodworking Machine": {
            "department": "Tools",
            "class": "Woodworking",
            "fine": "Stationary Machinery",
            "classpath": "Tools > Woodworking > Stationary Machinery"
        }
    }

    def __init__(self, taxonomy_file: Optional[Path] = None):
        self.taxonomy_file = taxonomy_file
        self.mode_a = False
        self.taxonomy_db = {}
        if taxonomy_file and taxonomy_file.exists():
            try:
                self._load_taxonomy(taxonomy_file)
                self.mode_a = True
            except Exception:
                pass

    def _load_taxonomy(self, filepath: Path):
        df = pd.read_excel(filepath)
        for _, row in df.iterrows():
            ptype = str(row.get("PRODUCT_TYPE", "")).strip()
            if ptype:
                self.taxonomy_db[ptype.lower()] = {
                    "department": str(row.get("DEPARTMENT", "")),
                    "class": str(row.get("CLASS", "")),
                    "fine": str(row.get("FINE", "")),
                    "classpath": str(row.get("CLASSPATH", ""))
                }

    def get_taxonomy(self, product_type: str) -> Optional[Dict[str, str]]:
        if not product_type:
            return None
            
        if self.mode_a:
            return self.taxonomy_db.get(product_type.lower())
        else:
            return self.DEFAULT_TAXONOMY_MAP.get(product_type)
