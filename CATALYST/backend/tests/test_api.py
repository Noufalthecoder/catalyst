import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).parent.parent))

from app.main import app

client = TestClient(app)

def test_health_check():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ONLINE"
    assert "CATALYST" in data["engine"]

def test_stats_overview():
    res = client.get("/api/stats/overview")
    assert res.status_code == 200
    data = res.json()
    assert "kpis" in data
    assert "stages" in data
    assert len(data["stages"]) == 8

def test_stats_analytics():
    res = client.get("/api/stats/analytics")
    assert res.status_code == 200
    data = res.json()
    assert "quality_distribution" in data
    assert "attribute_breakdown" in data

def test_catalog_list():
    res = client.get("/api/catalog?page=1&page_size=10")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) <= 10

def test_catalog_hero_demo():
    res = client.get("/api/catalog/hero-demo")
    assert res.status_code == 200
    data = res.json()
    assert "product" in data
    assert "pipeline_steps" in data
    assert len(data["pipeline_steps"]) == 6

def test_review_queue():
    res = client.get("/api/review")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "counts" in data

def test_sources_overview():
    res = client.get("/api/sources")
    assert res.status_code == 200
    data = res.json()
    assert "top_manufacturer_domains" in data

def test_exports_list():
    res = client.get("/api/exports")
    assert res.status_code == 200
    data = res.json()
    assert "exports" in data
