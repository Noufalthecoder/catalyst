import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.models.product import CanonicalProduct
from app.utils.mpn import MPNParser
from app.utils.brand import BrandResolver
from app.utils.manufacturer import ManufacturerResolver
from app.utils.product_type import ProductTypeDetector
from app.utils.desc_parser import ProductDescriptionParser
from app.utils.duplicate import DuplicateDetector
from app.data.pipeline import IdentityPipeline

def test_mpn_parsing():
    parsed = MPNParser.parse("DCB518ASTS06G", "DCB518ASTS06G Diablo 1/2\"x18\" - Sanding Belt 6pc")
    assert parsed["raw_mpn"] == "DCB518ASTS06G"
    assert parsed["normalized_mpn"] == "DCB518ASTS06G"
    assert parsed["series"] == "Diablo"
    
    # Alternate MPN check
    parsed_alt = MPNParser.parse("XYZ-123", "Some Description Replaces ABC-789")
    assert parsed_alt["alternate_mpn"] == "ABC-789"

def test_brand_resolution_mode_b():
    resolver = BrandResolver(None) # Mode B
    
    # Explicit brand
    record = {"e1_brand": "TREX", "unilog_brand": None, "dib_brand": None, "part_desc": ""}
    res = resolver.resolve(record)
    assert res["brand"] == "Trex"
    assert res["status"] == "PROBABLE"
    
    # Embedded brand
    record_emb = {"e1_brand": None, "unilog_brand": None, "dib_brand": None, "part_desc": "3M 775L Stikit Film"}
    res_emb = resolver.resolve(record_emb)
    assert res_emb["brand"] == "3M"
    
    # Conflicted brands
    record_conf = {"e1_brand": "TREX", "unilog_brand": None, "dib_brand": "TimberTech", "part_desc": ""}
    res_conf = resolver.resolve(record_conf)
    assert res_conf["status"] == "CONFLICTED"

def test_manufacturer_resolution_mode_b():
    resolver = ManufacturerResolver(None) # Mode B
    
    # Strip bracketed code
    record = {"part_manuf": "Milwaukee Accessory (4031)", "part_desc": ""}
    res = resolver.resolve(record)
    assert res["canonical_name"] == "Milwaukee Tool"
    assert res["status"] == "PROBABLE"
    
    # Inferred from brand
    record_inf = {"part_manuf": None, "part_desc": ""}
    res_inf = resolver.resolve(record_inf, resolved_brand="DEWALT")
    assert res_inf["canonical_name"] == "DEWALT"

def test_product_type_detection():
    pt = ProductTypeDetector.detect("Milwaukee 5\"x.045\"x7/8\" Metal Cut Off Disc")
    assert pt["product_type"] == "Abrasive Wheel"
    
    pt2 = ProductTypeDetector.detect("Dishwasher SS")
    assert pt2["product_type"] == "Dishwasher"

def test_description_spec_extraction():
    specs = ProductDescriptionParser.parse("Milwaukee 5\"x.045\"x7/8\" Metal Cut Off Disc 10pc 120V")
    assert specs["voltage"] == "120V"
    assert specs["quantity"] == "10pc"
    assert "5\"" in specs["dimensions"]

def test_duplicate_detection():
    detector = DuplicateDetector()
    
    res1 = detector.check_and_register(
        record_id=1,
        mpn="DCB518ASTS06G",
        norm_mpn="DCB518ASTS06G",
        mfg="Freud Inc",
        brand="Diablo",
        desc="Diablo Sanding Belt 6pc"
    )
    assert res1["status"] == "UNIQUE"
    
    # Duplicate raw MPN
    res2 = detector.check_and_register(
        record_id=2,
        mpn="DCB518ASTS06G",
        norm_mpn="DCB518ASTS06G",
        mfg="Freud Inc",
        brand="Diablo",
        desc="Diablo Sanding Belt 6pc"
    )
    assert res2["status"] == "DUPLICATE"
    assert 1 in res2["duplicate_of"]
    
    # Possible duplicate by normalized MPN
    res3 = detector.check_and_register(
        record_id=3,
        mpn="dcb518asts06g",
        norm_mpn="DCB518ASTS06G",
        mfg="Different Mfg",
        brand="Diablo",
        desc="Another desc"
    )
    assert res3["status"] == "POSSIBLE_DUPLICATE"
