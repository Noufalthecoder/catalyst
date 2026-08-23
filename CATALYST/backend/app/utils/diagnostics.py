import json
from pathlib import Path
from typing import List, Dict, Any
from app.models.product import CanonicalProduct

class UnknownAttributeDiagnostics:
    @staticmethod
    def diagnose_product_attributes(product: CanonicalProduct) -> CanonicalProduct:
        """
        Diagnoses why each attribute remains UNKNOWN or of low confidence.
        Sets the attribute's status or adds diagnostic metadata.
        """
        sources = product.sources
        
        has_sources = len(sources) > 0
        has_matched_sources = any(s.authority_level != "UNTRUSTED" for s in sources)

        from app.utils.applicability import AttributeApplicabilityEngine
        fine_class = product.taxonomy.fine
        prod_type = product.taxonomy.product_type

        # Check both attributes lists to keep models consistent
        target_lists = [product.attributes, product.enriched_attributes]
        
        for attr_list in target_lists:
            for attr in attr_list:
                # 1. Check applicability
                if AttributeApplicabilityEngine.evaluate_applicability(prod_type, fine_class, attr.label) == "NOT_APPLICABLE":
                    attr.status = "NOT_APPLICABLE"
                    attr.evidence = "NOT_APPLICABLE"
                    continue

                if attr.value is None or attr.status == "UNKNOWN":
                    attr.status = "UNKNOWN"
                    if not has_sources:
                        attr.evidence = "SOURCE_NOT_FOUND"
                    elif not has_matched_sources:
                        attr.evidence = "SOURCE_NOT_FOUND"
                    elif any(c.get("attribute") == attr.label for c in product.source_conflicts):
                        attr.evidence = "AMBIGUOUS"
                    else:
                        attr.evidence = "SOURCE_DOES_NOT_CONTAIN_VALUE"
                elif attr.status == "INVALID":
                    attr.evidence = "NORMALIZATION_FAILED"

        return product

    @classmethod
    def analyze_batch(cls, products: List[CanonicalProduct], output_dir: str) -> Dict[str, Any]:
        """
        Analyzes unknown attributes across a batch of products and writes:
        - docs/UNKNOWN_ATTRIBUTE_ANALYSIS.md
        - data/output/unknown_attribute_analysis.json
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        total_products = len(products)
        diagnostics_stats = {}
        
        total_unknowns = 0
        total_attributes = 0

        # Tally counts by label and cause
        for prod in products:
            prod_diagnosed = cls.diagnose_product_attributes(prod)
            for attr in prod_diagnosed.enriched_attributes:
                total_attributes += 1
                if attr.status == "UNKNOWN":
                    total_unknowns += 1
                    label = attr.label
                    cause = attr.evidence or "REFERENCE_RULE_UNAVAILABLE"
                    
                    if label not in diagnostics_stats:
                        diagnostics_stats[label] = {
                            "count": 0,
                            "causes": {}
                        }
                    
                    diagnostics_stats[label]["count"] += 1
                    diagnostics_stats[label]["causes"][cause] = diagnostics_stats[label]["causes"].get(cause, 0) + 1

        # Format stats for export
        analysis_report = []
        for label, data in diagnostics_stats.items():
            count = data["count"]
            pct = round((count / total_products) * 100, 2)
            
            # Find the primary cause
            causes_sorted = sorted(data["causes"].items(), key=lambda x: x[1], reverse=True)
            primary_cause = causes_sorted[0][0] if causes_sorted else "SOURCE_MISSING_ATTRIBUTE"

            analysis_report.append({
                "attribute": label,
                "count": count,
                "percentage": pct,
                "likely_cause": primary_cause,
                "causes_breakdown": data["causes"]
            })

        # Write JSON Report
        json_report_path = output_path / "unknown_attribute_analysis.json"
        with open(json_report_path, "w", encoding="utf-8") as f:
            json.dump({
                "total_products": total_products,
                "total_attributes": total_attributes,
                "total_unknowns": total_unknowns,
                "unknown_percentage": round((total_unknowns / total_attributes) * 100, 2) if total_attributes else 0.0,
                "attributes": sorted(analysis_report, key=lambda x: x["count"], reverse=True)
            }, f, indent=2)

        # Write Markdown Report to docs/
        docs_dir = Path("c:/Users/Mohammed Noufal V/catalyst1/docs")
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        md_content = "# Unknown Attribute Diagnostics Analysis Report\n\n"
        md_content += f"- **Total Products Processed**: {total_products}\n"
        md_content += f"- **Total Expected Attributes**: {total_attributes}\n"
        md_content += f"- **Total Unknown Attributes**: {total_unknowns}\n"
        md_content += f"- **Attribute Fill Gap Rate**: {round((total_unknowns / total_attributes) * 100, 2) if total_attributes else 0.0}%\n\n"
        
        md_content += "## Diagnostic Cause Breakdown by Attribute\n\n"
        md_content += "| Attribute | Unknown Count | Percentage | Likely Primary Cause | Breakdown |\n"
        md_content += "|---|---|---|---|---|\n"
        
        for item in sorted(analysis_report, key=lambda x: x["count"], reverse=True):
            breakdown_str = ", ".join([f"{k}: {v}" for k, v in item["causes_breakdown"].items()])
            md_content += f"| {item['attribute']} | {item['count']} | {item['percentage']}% | `{item['likely_cause']}` | {breakdown_str} |\n"

        with open(docs_dir / "UNKNOWN_ATTRIBUTE_ANALYSIS.md", "w", encoding="utf-8") as f:
            f.write(md_content)

        return diagnostics_stats
