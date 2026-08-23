import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.models.product import CanonicalProduct
from app.utils.understanding import ProductUnderstandingEngine
from app.utils.taxonomy import TaxonomyEngine
from app.utils.attribute_schema import AttributeSchemaEngine
from app.utils.desc_parser import ProductDescriptionParser
from app.utils.duplicate import DuplicateDetector
from app.data.repositories.taxonomy_repository import TaxonomyRepository

def test_product_understanding():
    res = ProductUnderstandingEngine.analyze(
        part_desc="3M 775L Stikit Film P150 - Cubitron II 50 Disc/Box",
        mfg_part_num="3MABR-7100075678",
        brand="3M",
        manufacturer="3M Company",
        product_type="Abrasive Disc"
    )
    assert res["product_name"] == "Abrasive Disc"
    assert "Cubitron II" not in res["semantic_summary"]  # should be clean and not guess specs
    assert "Abrasive Disc" in res["semantic_summary"]
    assert res["status"] == "VERIFIED"

def test_taxonomy_classification_and_consistency():
    repo = TaxonomyRepository(None)
    engine = TaxonomyEngine(repo)

    # Valid check (Mode B)
    res = engine.classify(
        part_desc="3M 775L Stikit Film P150",
        product_type="Sanding Product",
        brand="3M"
    )
    assert res["department"] == "Building Materials"
    assert res["class_name"] == "Abrasives"
    assert res["status"] == "INFERRED"

    # Conflicted/Inconsistent check
    # Pretend department is Appliances but Class is Abrasives (Stage 3 check)
    engine.repo.DEFAULT_TAXONOMY_MAP["Sanding Product"] = {
        "department": "Appliances",
        "class": "Abrasives",
        "fine": "Sanding Products",
        "classpath": "Appliances > Abrasives > Sanding Products"
    }
    res_conf = engine.classify(
        part_desc="3M 775L",
        product_type="Sanding Product"
    )
    assert res_conf["status"] == "CONFLICTED"
    
    # Restore map
    engine.repo.DEFAULT_TAXONOMY_MAP["Sanding Product"] = {
        "department": "Building Materials",
        "class": "Abrasives",
        "fine": "Sanding Products",
        "classpath": "Building Materials > Abrasives > Sanding Products"
    }

def test_attribute_schema_generation():
    defs = AttributeSchemaEngine.generate_schema("Abrasives")
    labels = [d.label for d in defs]
    assert "Grit" in labels
    assert "Diameter" in labels

    # Default schema fallback
    defs_fallback = AttributeSchemaEngine.generate_schema("NonExistentClass")
    labels_fallback = [d.label for d in defs_fallback]
    assert "Voltage" in labels_fallback

def test_description_parser_grit_and_pkg():
    res = ProductDescriptionParser.parse("3M 775L Stikit Film P150 - Cubitron II 50 Disc/Box")
    assert res["grit"] == "P150"
    assert res["technology"] == "Cubitron II"
    assert res["packaging_qty"] == "50"
    assert res["packaging_uom"] == "Disc/Box"

def test_duplicate_review_classification():
    # Construct mock CanonicalProducts
    prod_a_dict = {
        "raw": {"mfg_part_num": "ADB15516CS"},
        "cleaned": {"part_desc": {"normalized_value": "TimberTech English Walnut Decking 16ft"}},
        "identity": {
            "raw_mpn": "ADB15516CS",
            "normalized_mpn": "ADB15516CS",
            "brand": "TimberTech",
            "manufacturer": "TimberTech",
            "product_name": "Decking Board"
        }
    }
    prod_b_dict = {
        "raw": {"mfg_part_num": "ADB15520CS"},
        "cleaned": {"part_desc": {"normalized_value": "TimberTech English Walnut Decking 20ft"}},
        "identity": {
            "raw_mpn": "ADB15520CS",
            "normalized_mpn": "ADB15520CS",
            "brand": "TimberTech",
            "manufacturer": "TimberTech",
            "product_name": "Decking Board"
        }
    }

    prod_a = CanonicalProduct.model_validate(prod_a_dict)
    prod_b = CanonicalProduct.model_validate(prod_b_dict)

    res = DuplicateDetector.review_duplicate(prod_a, prod_b)
    # Different MPNs, very similar desc, same brand -> LIKELY_VARIANT
    assert res["status"] == "LIKELY_VARIANT"
