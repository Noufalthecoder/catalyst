from typing import List, Dict, Any
import json
from pathlib import Path
from app.models.product import CanonicalProduct
from app.utils.quality import ProductQualityScore

class EvaluationEngine:
    @staticmethod
    def evaluate_batch(products: List[CanonicalProduct], output_dir: str) -> Dict[str, Any]:
        """
        Runs comprehensive checks on all pipeline components and prints/writes
        a unified metrics JSON summary to data/output/evaluation_report.json.
        """
        total = len(products)
        identity_verified = 0
        taxonomy_assigned = 0
        has_sources = 0
        attributes_enriched = 0
        total_attributes = 0
        invalid_attributes = 0
        conflicts = 0
        content_complete = 0
        
        quality_scores = []

        for p in products:
            # 1. Identity
            if p.identity.identity_status == "VERIFIED":
                identity_verified += 1
            
            # 2. Taxonomy
            if p.taxonomy.department:
                taxonomy_assigned += 1

            # 3. Sources
            if p.sources:
                has_sources += 1

            # 4. Attributes
            total_attributes += len(p.enriched_attributes)
            for attr in p.enriched_attributes:
                if attr.value is not None:
                    attributes_enriched += 1
                if attr.status == "INVALID":
                    invalid_attributes += 1
                elif attr.status == "CONFLICTED":
                    conflicts += 1

            # 5. Content
            from app.utils.content_generation import ContentGenerator
            descs = ContentGenerator.generate_descriptions(p)
            if descs.get("LONG_DESC1"):
                content_complete += 1

            # 6. Composite Score
            q_score = ProductQualityScore.calculate_score(p)
            quality_scores.append(q_score)

        avg_quality = sum(quality_scores) / total if total else 0.0

        report = {
            "total_products": total,
            "identity_preservation_rate": round((identity_verified / total) * 100, 2) if total else 0.0,
            "taxonomy_assignment_rate": round((taxonomy_assigned / total) * 100, 2) if total else 0.0,
            "source_coverage_rate": round((has_sources / total) * 100, 2) if total else 0.0,
            "attribute_fill_rate": round((attributes_enriched / total_attributes) * 100, 2) if total_attributes else 0.0,
            "invalid_attribute_rate": round((invalid_attributes / total_attributes) * 100, 2) if total_attributes else 0.0,
            "conflict_rate": round((conflicts / total_attributes) * 100, 2) if total_attributes else 0.0,
            "content_coverage_rate": round((content_complete / total) * 100, 2) if total else 0.0,
            "average_product_quality_score": round(avg_quality, 2)
        }

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        with open(output_path / "evaluation_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return report
