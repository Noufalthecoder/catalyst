from typing import Dict, Any, Optional
import re

class ProductTypeDetector:
    # Rule-based regex matches for common categories
    RULES = [
        (r'\b(?:sanding belt|sanding sponge|sanding disc|abrasive disc|flap disc|abranet|iridium grip)\b', 'Sanding Product'),
        (r'\b(?:cut-off disc|grinding wheel|cut off disc|grinding disc|diamond blade|cutting wheel)\b', 'Abrasive Wheel'),
        (r'\b(?:joist tape| legacy emseal tape|vinyl elect tape|masking tape|duct tape)\b', 'Tape'),
        (r'\bdishwasher\b', 'Dishwasher'),
        (r'\b(?:dryer|gas dryer|elect dryer)\b', 'Dryer'),
        (r'\blaundry center\b', 'Laundry Center'),
        (r'\b(?:washer|elect washer|washing machine)\b', 'Washer'),
        (r'\bkneeling pad\b', 'Kneeling Pad'),
        (r'\b(?:tire pressure|inflator gauge)\b', 'Inflator Gauge'),
        (r'\bmortar\b', 'Mortar'),
        (r'\b(?:composite balusters|rail kit|rail panel|gate|finyline|select classic)\b', 'Railing Accessory'),
        (r'\b(?:pvc decking|decking|grooved deck)\b', 'Decking Board'),
        (r'\b(?:fascia|pvc fascia)\b', 'Fascia Board'),
        (r'\b(?:post sleeve|post trim|flat post cap|support post|elite post trim|post cap)\b', 'Post Accessory'),
        (r'\b(?:attic access door|patio dr|skylight|hopper|basement ecoliteplus)\b', 'Door / Window / Skylight'),
        (r'\b(?:drywall|easi-lite|firelite|gypsum)\b', 'Drywall'),
        (r'\bthreshold\b', 'Threshold'),
        (r'\brainscreen\b', 'Rainscreen'),
        (r'\b(?:doug fir|lumber|timber|board)\b', 'Lumber'),
        (r'\b(?:sub floor|osb|subfloor)\b', 'Subfloor Panel'),
        (r'\b(?:premier rib xl|metal panel|roofing panel)\b', 'Roofing Panel'),
        (r'\b(?:duration|shingles|roof shingles)\b', 'Roof Shingles'),
        (r'\b(?:ice guard|eaveguard|ice & water shield)\b', 'Ice & Water Shield'),
        (r'\b(?:hardie sgd|smart lap sdg|hardiesmooth|smartside|soffit|soffit panel)\b', 'Siding / Soffit Panel'),
        (r'\b(?:wall mount trex|ada wall mount|int end cap|ada rail)\b', 'ADA Railing Accessory'),
        (r'\b(?:r-sheathing|insulated r-sheathing|insulation board)\b', 'Insulation Board'),
        (r'\b(?:ceiling tile|fine fissured|suspension ceiling)\b', 'Ceiling Tile'),
        (r'\b(?:jumpstart|power supply|battery mounts|battery mount|8d battery)\b', 'Power / Battery Accessory'),
        (r'\b(?:hanger|box cover|gfi box cover|pvc box cover|oct box|square box)\b', 'Electrical Box Accessory'),
        (r'\b(?:decor plate|wall plate|switch plate)\b', 'Wall Plate'),
        (r'\b(?:dimmer|plug in dimmer|dimmer switch)\b', 'Dimmer Switch'),
        (r'\b(?:timer|indoor timer|mech timer|digital indoor timer|24hr mech timer)\b', 'Timer Switch'),
        (r'\b(?:led lt|strip light|wall lt|bath light|chandelier|ceiling lt|pendant lt|down lt|downlight|shop light|wall sconce|wrap light|highbay light|fixture)\b', 'Lighting Fixture'),
        (r'\b(?:flor|halogen|sodium|incan|led bulb|edison st19|mr16|light bulb|fluorescent bulb)\b', 'Light Bulb'),
        (r'\b(?:flashlight|clip light|headlight|work light|nano clip)\b', 'Portable Light'),
        (r'\b(?:load cntr|load center|panelboard)\b', 'Load Center'),
        (r'\b(?:entrance cable|so cord|cat5e|stranded wire|triplex wire|wire|cable|cord)\b', 'Electrical Cable / Wire'),
        (r'\bcord grip\b', 'Cable Grip'),
        (r'\b(?:outlet|wall tap|gfci outlet|plug|switch|toggle switch|receptacle)\b', 'Outlet / Switch'),
        (r'\bbeverage center\b', 'Beverage Center'),
        (r'\b(?:coffee maker|espresso|espresso machine)\b', 'Coffee / Espresso Maker'),
        (r'\bwall oven\b', 'Wall Oven'),
        (r'\b(?:microwave|microwave drawer|otr microwave)\b', 'Microwave'),
        (r'\bcooktop\b', 'Cooktop'),
        (r'\b(?:range|gas range|electric range)\b', 'Range'),
        (r'\b(?:grill|toaster|toast oven)\b', 'Kitchen Countertop Appliance'),
        (r'\b(?:freezer|fridge|freezer chest|refrigerator|refrigerator/freezer)\b', 'Refrigerator / Freezer'),
        (r'\bhole drilling system\b', 'Drilling System'),
        (r'\b(?:finish nail|staple|brad nail|finishing nail)\b', 'Fastener (Nails/Staples)'),
        (r'\b(?:fan|hunter fan|gilmour fan|anisten fan|cassius fan|jetty fan|ceiling fan)\b', 'Ceiling Fan'),
        (r'\b(?:cordless vacuum|vacuum cleaner)\b', 'Vacuum Cleaner'),
        (r'\bdriveway alert\b', 'Security Alert'),
        (r'\bgravity latch\b', 'Gate Hardware'),
        (r'\bbottle\b', 'Water Bottle'),
        (r'\bgrease gun\b', 'Grease Gun'),
        (r'\btool chest\b', 'Tool Chest'),
        (r'\b(?:post wrap|inside cas|post sleeve wrap)\b', 'Trim / Post Wrap'),
        (r'\bt-square\b', 'Measuring Tool'),
        (r'\bmechanical pencil\b', 'Writing Instrument'),
        (r'\bsafety glasses\b', 'Safety Glasses'),
        (r'\bfire extinguisher\b', 'Fire Extinguisher'),
        (r'\bsmoke & co alarm\b', 'Smoke Detector'),
        (r'\b(?:heated work glove|glove liners|heated hoodie|heated gear|heated glove)\b', 'Heated Apparel'),
        (r'\bphone holster\b', 'Phone Holster'),
        (r'\bvoltage detector\b', 'Voltage Detector'),
        (r'\b(?:bigcal|laser|cross line laser|line laser|mason line|raftersquare|rafter square)\b', 'Measuring / Layout Tool'),
        (r'\b(?:countersink|stop drill|plug cutter|router bit|spindle shaper)\b', 'Drilling / Router Accessory'),
        (r'\b(?:sander|orbit sander|deos663xcv sander)\b', 'Sander'),
        (r'\bcollated attach\b', 'Tool Attachment'),
        (r'\bfile\b', 'Hand Tool (File)'),
        (r'\b(?:saw blade|dado pro set)\b', 'Saw Blade'),
        (r'\b(?:hole dozer kit|jig saw blade|band saw|circ saw|miter saw|recip saw|table saw|track saw|circular saw|jigsaw|bandsaw)\b', 'Saw / Cutting Tool'),
        (r'\b(?:starter kit|battery pack|charger|fast charger|powerpack|lithium battery)\b', 'Power Tool Battery / Charger'),
        (r'\b(?:dust extractor|paper bag)\b', 'Dust Extractor / Vacuum Accessory'),
        (r'\b(?:shaper|stock feeder)\b', 'Woodworking Machine Accessory'),
        (r'\b(?:jointer|planer|planing machine|edge sander|benchtop planer)\b', 'Woodworking Machine')
    ]

    @classmethod
    def detect(cls, part_desc: Optional[str]) -> Dict[str, Any]:
        """
        Detects product type from Part_Desc using regex rules.
        """
        if not part_desc:
            return {
                "product_type": "UNKNOWN",
                "confidence": 0.0,
                "method": "unknown"
            }

        # Clean description for matching
        desc_clean = part_desc.lower()

        for pattern, prod_type in cls.RULES:
            if re.search(pattern, desc_clean):
                return {
                    "product_type": prod_type,
                    "confidence": 0.9,
                    "method": "rule"
                }

        # Fallback to general classification
        return {
            "product_type": "UNKNOWN",
            "confidence": 0.0,
            "method": "unknown"
        }
