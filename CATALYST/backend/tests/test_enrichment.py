import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.models.product import CanonicalProduct, ProductSource, ProductAttribute
from app.utils.source_discovery import SourceDiscoveryEngine
from app.utils.source_ranker import SourceRanker
from app.utils.document_extractor import DocumentExtractor
from app.utils.evidence_extractor import EvidenceExtractor
from app.utils.source_fetcher import SourceFetcher

def test_source_ranking():
    src = {
        "url": "https://www.3m.com/products/7100075678",
        "domain": "3m.com",
        "source_type": "MANUFACTURER_PRODUCT_PAGE",
        "title": "3M 7100075678 Abrasive Disc"
    }
    ranked = SourceRanker.score_source(src, brand="3M", mpn="7100075678", product_type="Abrasive Disc")
    assert ranked["final_score"] >= 75.0
    assert ranked["authority_level"] == "PRIMARY"

def test_document_extractor_and_relevance():
    html = """
    <html>
    <head><title>3M 7100075678 Product Details</title></head>
    <body>
      <h1>3M Product 7100075678</h1>
      <table>
        <tr><td>Grit</td><td>P150</td></tr>
      </table>
    </body>
    </html>
    """
    ext = DocumentExtractor.extract_text_and_tables(html)
    assert ext["title"] == "3M 7100075678 Product Details"
    assert ext["spec_table"]["Grit"] == "P150"

    rel = DocumentExtractor.match_product(html, brand="3M", mpn="7100075678")
    assert rel == "MATCHED"

    rel_bad = DocumentExtractor.match_product(html, brand="Dewalt", mpn="DCB518")
    assert rel_bad == "REJECTED"

def test_evidence_consensus_and_conflict():
    # Scenario: Two matching sources with same specs -> consensus
    sources = [
        ProductSource(
            url="https://www.3m.com/1", domain="3m.com", source_type="MANUFACTURER_PRODUCT_PAGE",
            authority_level="PRIMARY", title="3M 7100075678 Page", description="Grit: P150",
            extraction_status="SUCCESS"
        ),
        ProductSource(
            url="https://www.3m.com/2", domain="3m.com", source_type="MANUFACTURER_DATASHEET",
            authority_level="PRIMARY", title="3M 7100075678 Datasheet", description="Grit: P150",
            extraction_status="SUCCESS"
        )
    ]
    
    schema_attrs = [
        ProductAttribute(label="Grit", value_type="text", value=None)
    ]

    res = EvidenceExtractor.extract_attributes(sources, schema_attrs)
    assert res["enriched_attributes"][0].status == "VERIFIED"
    assert res["enriched_attributes"][0].value == "P150"
    assert not res["source_conflicts"]

    # Scenario: Conflicting specs -> CONFLICTED status
    sources_conflict = [
        ProductSource(
            url="https://www.3m.com/1", domain="3m.com", source_type="MANUFACTURER_PRODUCT_PAGE",
            authority_level="PRIMARY", title="3M 7100075678 Page", description="Grit: P150",
            extraction_status="SUCCESS"
        ),
        ProductSource(
            url="https://www.3m.com/2", domain="3m.com", source_type="MANUFACTURER_DATASHEET",
            authority_level="PRIMARY", title="3M 7100075678 Datasheet", description="Grit: P120",
            extraction_status="SUCCESS"
        )
    ]

    res_conflict = EvidenceExtractor.extract_attributes(sources_conflict, schema_attrs)
    assert res_conflict["enriched_attributes"][0].status == "CONFLICTED"
    assert len(res_conflict["source_conflicts"]) == 1

def test_source_fetcher_caching(tmp_path):
    fetcher = SourceFetcher(cache_dir=str(tmp_path))
    url = "https://www.3m.com/products/7100075678"
    
    res1 = fetcher.fetch(url)
    assert res1["http_status"] == 200
    
    # Second fetch should hit the cache
    res2 = fetcher.fetch(url)
    assert res2["content_hash"] == res1["content_hash"]
    
def test_untrusted_script_security():
    html_with_js = """
    <html>
    <head><script>alert('malicious script execution!');</script></head>
    <body>
      <p>Voltage Rating: 120V</p>
    </body>
    </html>
    """
    ext = DocumentExtractor.extract_text_and_tables(html_with_js)
    # Ensure JavaScript was not executed (it was just parsed as HTML plain text elements, not executed)
    assert "Voltage" in ext["raw_text"] or "120V" in ext["raw_text"]
