import pytest
import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.models.product import CanonicalProduct, ProductSource, ProductAttribute, ProductTaxonomy
from app.utils.quality import ProductQualityScore
from app.utils.applicability import AttributeApplicabilityEngine
from app.utils.review_queue import ReviewQueue
from app.utils.ground_truth import GroundTruthEvaluator
from app.data.pipeline_production import ProductionPipeline

def test_product_quality_score():
    product = CanonicalProduct()
    product.identity.identity_confidence = 1.0
    product.taxonomy.confidence = 1.0
    
    # 1. Base score (no sources)
    score1 = ProductQualityScore.calculate_score(product)
    assert score1 >= 0.30 # 0.15 + 0.15

    # 2. Score with primary source and matching MPN
    product.sources = [
        ProductSource(
            url="https://www.3m.com/1", domain="3m.com", source_type="MANUFACTURER_PRODUCT_PAGE",
            authority_level="PRIMARY", title="3M Product Specs Page", description="7100075678"
        )
    ]
    product.identity.raw_mpn = "7100075678"
    score2 = ProductQualityScore.calculate_score(product)
    assert score2 >= 0.70 # +0.20 for primary source, +0.20 for exact MPN match

def test_attribute_applicability():
    app_engine = AttributeApplicabilityEngine
    # Grit is applicable to Sanding Disc
    res1 = app_engine.evaluate_applicability("Sanding Disc", "Sanding Products", "Grit")
    assert res1 == "APPLICABLE"

    # Dishwasher cycles is NOT applicable to Sanding Disc
    res2 = app_engine.evaluate_applicability("Sanding Disc", "Sanding Products", "Dishwasher Wash Cycles")
    assert res2 == "NOT_APPLICABLE"

    # Unknown product type -> UNCERTAIN
    res3 = app_engine.evaluate_applicability("UNKNOWN", "Sanding Products", "Grit")
    assert res3 == "UNCERTAIN"

def test_review_queue_triggers(tmp_path):
    product = CanonicalProduct()
    product.identity.raw_mpn = "12345"
    product.identity.identity_status = "AMBIGUOUS"
    product.identity.identity_confidence = 0.3
    product.taxonomy.status = "UNKNOWN"
    product.web_quality_score = 0.5
    
    review_list = ReviewQueue.evaluate_and_register([product], str(tmp_path))
    assert len(review_list) == 1
    assert "AMBIGUOUS_IDENTITY" in review_list[0]["reasons"]

def test_ground_truth_evaluator():
    res = GroundTruthEvaluator.calculate_accuracy([])
    assert res["status"] == "GROUND_TRUTH_DATASET_PENDING"
    assert res["overall_accuracy_score"] == 0.0

def test_production_pipeline_resumability(tmp_path):
    pipeline = ProductionPipeline(output_dir=str(tmp_path), cache_dir=str(tmp_path))
    
    # Init some tracker states
    pipeline.status_tracker["DCB518ASTS06G"] = "COMPLETED"
    pipeline._save_tracker()
    
    new_pipeline = ProductionPipeline(output_dir=str(tmp_path), cache_dir=str(tmp_path))
    assert new_pipeline.status_tracker["DCB518ASTS06G"] == "COMPLETED"
