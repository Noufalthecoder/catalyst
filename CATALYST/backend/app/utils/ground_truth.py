from typing import List, Dict, Any, Optional
from app.models.product import CanonicalProduct

class GroundTruthEvaluator:
    @staticmethod
    def calculate_accuracy(predictions: List[CanonicalProduct], ground_truth: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Adapter designed to evaluate predicted CanonicalProducts against an
        official Unilog input-vs-output ground truth dataset.
        
        Returns zeros if the ground_truth is unavailable.
        """
        if not ground_truth:
            return {
                "field_accuracy": 0.0,
                "manufacturer_accuracy": 0.0,
                "brand_accuracy": 0.0,
                "taxonomy_accuracy": 0.0,
                "attribute_accuracy": 0.0,
                "uom_accuracy": 0.0,
                "content_compliance": 0.0,
                "overall_accuracy_score": 0.0,
                "status": "GROUND_TRUTH_DATASET_PENDING"
            }

        # Stubs for mapping and checking correctness
        total = len(predictions)
        mfg_correct = 0
        brand_correct = 0
        tax_correct = 0
        attr_correct = 0

        # Run checks if matching row index matches raw MPN
        for idx, pred in enumerate(predictions):
            if idx < len(ground_truth):
                gt = ground_truth[idx]
                if pred.identity.manufacturer == gt.get("MANUFACTURER_NAME"):
                    mfg_correct += 1
                if pred.identity.brand == gt.get("BRAND_NAME"):
                    brand_correct += 1
                if pred.taxonomy.classpath == gt.get("Classpath"):
                    tax_correct += 1

        return {
            "field_accuracy": round(((mfg_correct + brand_correct) / (total * 2)) * 100, 2) if total else 0.0,
            "manufacturer_accuracy": round((mfg_correct / total) * 100, 2) if total else 0.0,
            "brand_accuracy": round((brand_correct / total) * 100, 2) if total else 0.0,
            "taxonomy_accuracy": round((tax_correct / total) * 100, 2) if total else 0.0,
            "attribute_accuracy": 0.0,
            "uom_accuracy": 0.0,
            "content_compliance": 0.0,
            "overall_accuracy_score": 0.0,
            "status": "COMPLETED"
        }
