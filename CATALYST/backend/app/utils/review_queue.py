import json
from pathlib import Path
from typing import List, Dict, Any
from app.models.product import CanonicalProduct

class ReviewQueue:
    @staticmethod
    def evaluate_and_register(products: List[CanonicalProduct], output_dir: str) -> List[Dict[str, Any]]:
        """
        Scans a batch of processed CanonicalProduct objects, maps them to one of three states:
        AUTO_APPROVED, NEEDS_REVIEW, or BLOCKED, and saves them to review_queue.jsonl.
        """
        review_records = []

        for idx, prod in enumerate(products):
            reasons = []
            state = "AUTO_APPROVED"

            # 1. BLOCKED Conditions (Unrecoverable processing / critical quality fails)
            if prod.web_quality_score < 0.30:
                reasons.append("LOW_QUALITY_CRITICAL")
                state = "BLOCKED"
            elif not prod.identity.raw_mpn:
                reasons.append("MISSING_MPN")
                state = "BLOCKED"

            # 2. NEEDS_REVIEW Conditions (Unresolved ambiguities or validation warnings)
            if state != "BLOCKED":
                # Identity Ambiguity
                if prod.identity.identity_status in ["AMBIGUOUS", "UNKNOWN"] or prod.identity.identity_confidence < 0.8:
                    reasons.append("AMBIGUOUS_IDENTITY")
                    state = "NEEDS_REVIEW"

                # Taxonomy Uncertainty
                if prod.taxonomy.status == "UNKNOWN" or prod.taxonomy.confidence < 0.8:
                    reasons.append("LOW_TAXONOMY_CONFIDENCE")
                    state = "NEEDS_REVIEW"

                # Attribute Conflicts
                if len(prod.source_conflicts) > 0:
                    reasons.append("ATTRIBUTE_VALUE_CONFLICT")
                    state = "NEEDS_REVIEW"

                # Invalid Attributes
                has_invalid = any(a.status == "INVALID" for a in prod.enriched_attributes)
                if has_invalid:
                    reasons.append("INVALID_ATTRIBUTE_FORMAT")
                    state = "NEEDS_REVIEW"

                # Acceptable overall quality threshold
                if prod.web_quality_score < 0.60:
                    reasons.append("WEAK_SOURCE_EVIDENCE")
                    state = "NEEDS_REVIEW"

            # If not auto-approved, register in the queue
            if state != "AUTO_APPROVED":
                review_records.append({
                    "product_index": idx,
                    "mpn": prod.identity.raw_mpn,
                    "brand": prod.identity.brand,
                    "state": state,
                    "reasons": reasons,
                    "web_quality_score": prod.web_quality_score,
                    "conflicts": prod.source_conflicts
                })

        # Save to data/output/review_queue.jsonl
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        queue_file = output_path / "review_queue.jsonl"
        
        with open(queue_file, "w", encoding="utf-8") as f:
            for rec in review_records:
                f.write(json.dumps(rec) + "\n")

        return review_records
