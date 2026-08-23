import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.models.product import CanonicalProduct, ProductAttribute
from app.utils.normalization import AttributeNormalizationEngine
from app.utils.content_generation import ContentGenerator
from app.schema.delivery_schema import DeliverySchemaEngine, ExportBlockedException

def test_decimal_to_fraction():
    norm = AttributeNormalizationEngine
    assert norm.decimal_to_fraction(0.5) == "1/2"
    assert norm.decimal_to_fraction(50.25) == "50-1/4"
    assert norm.decimal_to_fraction(0.125) == "1/8"
    assert norm.decimal_to_fraction(12.0) == "12"

def test_attribute_validation():
    norm = AttributeNormalizationEngine
    
    # 1. Measurement parsing
    attr_meas = ProductAttribute(label="Length", value="50.25 in")
    res_meas = norm.validate_and_normalize(attr_meas, "MEASUREMENT")
    assert res_meas.status == "VERIFIED"
    assert res_meas.normalized_value == "50-1/4 in"
    assert res_meas.uom == "in"

    # 2. Boolean validation
    attr_bool = ProductAttribute(label="Prop 65", value="yes")
    res_bool = norm.validate_and_normalize(attr_bool, "BOOLEAN")
    assert res_bool.status == "VERIFIED"
    assert res_bool.normalized_value is True

    # 3. Invalid types
    attr_invalid = ProductAttribute(label="Voltage", value="not-a-number")
    res_invalid = norm.validate_and_normalize(attr_invalid, "DECIMAL")
    assert res_invalid.status == "INVALID"

def test_content_generation():
    product = CanonicalProduct()
    product.identity.brand = "Milwaukee"
    product.taxonomy.product_type = "Cut Off Disc"
    product.identity.raw_mpn = "49-94-0013"
    
    # Add verified spec
    product.enriched_attributes = [
        ProductAttribute(label="Grit", value="P150", status="VERIFIED")
    ]
    
    descs = ContentGenerator.generate_descriptions(product)
    assert "Milwaukee Cut Off Disc 49-94-0013" in descs["SHORT_DESC"]
    assert "P150" in descs["LONG_DESC1"]
    assert "Grit: P150" in descs["MOBILE_DESC"]

def test_delivery_schema_strictness():
    # Attempting to load delivery mapping
    engine = DeliverySchemaEngine()
    
    product = CanonicalProduct()
    product.identity.brand = "3M"
    product.identity.raw_mpn = "7100075678"
    product.taxonomy.product_type = "Sanding Disc"
    
    row = engine.map_product(product)
    assert len(row) == 252
    assert "MFR URL" in row
    assert "Actual Image (Yes/No)" in row

    # Test schema validator
    assert engine.validate_schema(row) is True

    # Artificially alter keys to test validation blockage
    bad_row = dict(row)
    bad_row.pop("MFR URL")
    with pytest.raises(ExportBlockedException):
        engine.validate_schema(bad_row)
