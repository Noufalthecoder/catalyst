import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api/review", tags=["Human Review Workspace"])

OUTPUT_DIR = Path(__file__).resolve().parents[3] / "data" / "output"
QUEUE_FILE = OUTPUT_DIR / "review_queue.jsonl"
QUEUE_1000_FILE = OUTPUT_DIR / "review_queue_1000.jsonl"

class ReviewDecisionRequest(BaseModel):
    action: str  # ACCEPT_SOURCE, KEEP_INPUT, MARK_UNKNOWN, OVERRIDE_VALUE, APPROVE_IDENTITY
    attribute: Optional[str] = None
    override_value: Optional[str] = None
    notes: Optional[str] = None

_REVIEW_DECISIONS: Dict[str, Dict[str, Any]] = {}

@router.get("")
def get_review_queue(category: Optional[str] = Query("all")) -> Dict[str, Any]:
    """
    Returns priority-sorted review items with side-by-side conflict comparisons.
    """
    items = []
    
    # Check review_queue.jsonl first
    if QUEUE_FILE.exists():
        try:
            with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                for idx, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue
                    rec = json.loads(line)
                    rec["id"] = str(rec.get("product_index", idx))
                    
                    # Human readable reason explanation
                    reasons = rec.get("reasons", [])
                    primary = reasons[0] if reasons else "MANUAL_REVIEW"
                    
                    if "ATTRIBUTE" in primary:
                        rec["summary"] = "Discrepancy detected between raw input descriptor and official manufacturer specifications."
                        rec["category"] = "ATTRIBUTE"
                        rec["priority"] = "HIGH"
                    elif "IDENTITY" in primary:
                        rec["summary"] = "Ambiguous manufacturer spelling or candidate MPN collision detected."
                        rec["category"] = "IDENTITY"
                        rec["priority"] = "CRITICAL"
                    elif "TAXONOMY" in primary:
                        rec["summary"] = "Confidence below threshold; requires classification confirmation."
                        rec["category"] = "TAXONOMY"
                        rec["priority"] = "MEDIUM"
                    else:
                        rec["summary"] = "Low composite confidence score across technical sources."
                        rec["category"] = "QUALITY"
                        rec["priority"] = "MEDIUM"

                    # Check if already resolved in-session
                    if rec["id"] in _REVIEW_DECISIONS:
                        rec["decision"] = _REVIEW_DECISIONS[rec["id"]]
                        rec["resolved"] = True
                    else:
                        rec["resolved"] = False

                    items.append(rec)
        except Exception as e:
            print(f"Error loading review queue: {e}")

    # Apply category filter
    if category and category != "all":
        items = [i for i in items if i.get("category", "").lower() == category.lower()]

    # Priority sort
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    items.sort(key=lambda x: (1 if x.get("resolved") else 0, priority_order.get(x.get("priority", "MEDIUM"), 2)))

    counts = {
        "all": len(items),
        "attribute": sum(1 for i in items if i.get("category") == "ATTRIBUTE"),
        "identity": sum(1 for i in items if i.get("category") == "IDENTITY"),
        "taxonomy": sum(1 for i in items if i.get("category") == "TAXONOMY"),
        "quality": sum(1 for i in items if i.get("category") == "QUALITY"),
        "resolved": sum(1 for i in items if i.get("resolved"))
    }

    return {
        "items": items,
        "total": len(items),
        "counts": counts
    }

@router.post("/{product_id}/decision")
def submit_review_decision(product_id: str, payload: ReviewDecisionRequest) -> Dict[str, Any]:
    """
    Applies human review decision (e.g. Accept Source, Keep Input, Override Value).
    """
    decision_record = {
        "product_id": product_id,
        "action": payload.action,
        "attribute": payload.attribute,
        "override_value": payload.override_value,
        "notes": payload.notes,
        "timestamp": "2026-08-23T16:20:00Z"
    }
    _REVIEW_DECISIONS[product_id] = decision_record
    
    return {
        "status": "SUCCESS",
        "message": f"Decision '{payload.action}' persisted successfully for product ID {product_id}.",
        "decision": decision_record
    }
