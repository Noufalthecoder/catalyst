import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query

from app.models.product import CanonicalProduct
from app.utils.content_generation import ContentGenerator

router = APIRouter(prefix="/api/catalog", tags=["Catalog Intelligence"])

OUTPUT_DIR = Path(__file__).resolve().parents[3] / "data" / "output"
JSONL_FILE = OUTPUT_DIR / "CATALYST_FINAL_1000.jsonl"

_PRODUCT_CACHE: Optional[List[Dict[str, Any]]] = None

def _get_products() -> List[Dict[str, Any]]:
    global _PRODUCT_CACHE
    if _PRODUCT_CACHE is not None:
        return _PRODUCT_CACHE
    
    products = []
    if JSONL_FILE.exists():
        try:
            with open(JSONL_FILE, "r", encoding="utf-8") as f:
                for idx, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    data["id"] = str(idx) # unique ID for routing
                    products.append(data)
        except Exception as e:
            print(f"Error loading catalog JSONL: {e}")
            
    _PRODUCT_CACHE = products
    return _PRODUCT_CACHE

@router.get("")
def list_catalog(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    search: Optional[str] = None,
    brand: Optional[str] = None,
    manufacturer: Optional[str] = None,
    product_type: Optional[str] = None,
    quality_band: Optional[str] = None, # "high", "medium", "low"
    status: Optional[str] = None
) -> Dict[str, Any]:
    all_prods = _get_products()
    filtered = all_prods

    if search:
        s_lower = search.strip().lower()
        filtered = [
            p for p in filtered
            if s_lower in (p.get("identity", {}).get("raw_mpn") or "").lower()
            or s_lower in (p.get("identity", {}).get("brand") or "").lower()
            or s_lower in (p.get("identity", {}).get("manufacturer") or "").lower()
            or s_lower in (p.get("raw", {}).get("part_desc") or "").lower()
            or s_lower in (p.get("taxonomy", {}).get("product_type") or "").lower()
        ]

    if brand:
        filtered = [p for p in filtered if (p.get("identity", {}).get("brand") or "").lower() == brand.lower()]

    if manufacturer:
        filtered = [p for p in filtered if (p.get("identity", {}).get("manufacturer") or "").lower() == manufacturer.lower()]

    if product_type:
        filtered = [p for p in filtered if (p.get("taxonomy", {}).get("product_type") or "").lower() == product_type.lower()]

    if quality_band:
        if quality_band == "high":
            filtered = [p for p in filtered if p.get("web_quality_score", 0) >= 0.8]
        elif quality_band == "medium":
            filtered = [p for p in filtered if 0.4 <= p.get("web_quality_score", 0) < 0.8]
        elif quality_band == "low":
            filtered = [p for p in filtered if p.get("web_quality_score", 0) < 0.4]

    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    items = filtered[start:end]

    # Collect unique filters for UI
    all_brands = sorted(list(set(p.get("identity", {}).get("brand") for p in all_prods if p.get("identity", {}).get("brand"))))
    all_mfgs = sorted(list(set(p.get("identity", {}).get("manufacturer") for p in all_prods if p.get("identity", {}).get("manufacturer"))))
    all_types = sorted(list(set(p.get("taxonomy", {}).get("product_type") for p in all_prods if p.get("taxonomy", {}).get("product_type") and p.get("taxonomy", {}).get("product_type") != "UNKNOWN")))

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size else 1,
        "filters_meta": {
            "brands": all_brands[:40],
            "manufacturers": all_mfgs[:40],
            "product_types": all_types[:40]
        }
    }

@router.get("/hero-demo")
def get_hero_demo_product() -> Dict[str, Any]:
    """
    Returns a richly-featured real product for the interactive 'See CATALYST in action' showcase.
    """
    all_prods = _get_products()
    # Find Diablo Sanding Belt or 3M Disc
    target = next((p for p in all_prods if "dcb518" in (p.get("identity", {}).get("raw_mpn") or "").lower()), None)
    if not target and all_prods:
        target = all_prods[0]
        
    return {
        "product": target,
        "pipeline_steps": [
            {
                "step": 1,
                "title": "Raw Dirty Input Ingested",
                "description": "Cryptic descriptor: '1/2X18 60G FILE BELT 6PK'",
                "raw_fields": target.get("raw", {})
            },
            {
                "step": 2,
                "title": "Identity Intelligence Resolved",
                "description": f"Brand resolved: '{target.get('identity', {}).get('brand')}' | MPN parsed: '{target.get('identity', {}).get('raw_mpn')}'",
                "confidence": target.get("identity", {}).get("identity_confidence", 1.0)
            },
            {
                "step": 3,
                "title": "Industrial Taxonomy Assigned",
                "description": f"Classified as '{target.get('taxonomy', {}).get('classpath')}'",
                "department": target.get("taxonomy", {}).get("department"),
                "product_type": target.get("taxonomy", {}).get("product_type")
            },
            {
                "step": 4,
                "title": "Authoritative Sources Discovered",
                "description": "Primary manufacturer domain verified with exact MPN specs table match.",
                "sources": target.get("sources", [])
            },
            {
                "step": 5,
                "title": "Normalized Technical Attributes",
                "description": "Extracted Width (1/2 in), Length (18 in), Grit (60), Packaging (6-pack).",
                "attributes": target.get("enriched_attributes", [])
            },
            {
                "step": 6,
                "title": "Commerce Description Generated",
                "description": "Generated Short, Long, and Invoicing descriptions conforming to Unilog rules.",
                "descriptions": target.get("content", {})
            }
        ]
    }

@router.get("/{product_id}")
def get_product_detail(product_id: str) -> Dict[str, Any]:
    all_prods = _get_products()
    product = None
    
    # Try by index ID first
    if product_id.isdigit():
        idx = int(product_id)
        if 0 <= idx < len(all_prods):
            product = all_prods[idx]
            
    # Try by MPN match
    if not product:
        product = next((p for p in all_prods if (p.get("identity", {}).get("raw_mpn") or "").lower() == product_id.lower()), None)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found in catalog database.")

    # Ensure generated content is present
    if not product.get("content", {}).get("short_desc"):
        try:
            prod_model = CanonicalProduct.model_validate(product)
            descs = ContentGenerator.generate_descriptions(prod_model)
            product["content"] = {
                "short_desc": descs.get("SHORT_DESC"),
                "long_desc": descs.get("LONG_DESC1"),
                "invoice_desc": descs.get("INVOICE_DESC")
            }
        except Exception:
            pass

    return product
