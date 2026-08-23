from typing import List, Dict, Any, Optional
from app.models.product import ProductAttribute, ProductSource
from app.utils.text import TextNormalizer
import re

class EvidenceExtractor:
    @staticmethod
    def extract_attributes(sources: List[ProductSource], schema_attributes: List[ProductAttribute]) -> Dict[str, Any]:
        """
        Extracts specifications from fetched sources, runs multi-source consensus, 
        and flags attribute conflicts.
        """
        enriched_attributes = []
        source_conflicts = []

        for schema_attr in schema_attributes:
            label = schema_attr.label
            expected_uom = schema_attr.uom

            candidates = []
            
            # Search all fetched sources
            for source in sources:
                # We skip untrusted sources or failed extractions
                if source.authority_level == "UNTRUSTED" or source.extraction_status == "FAILED":
                    continue

                # Simulate extraction by checking simulated spec tables or parsed contents
                # Note: self.fetcher returned simulated HTML with tables, which DocumentExtractor parsed.
                # In mock execution, self.extract_document parses it into source.description or similar.
                # Let's inspect the source document content hash or content directly.
                # We can mock this by checking a small local dictionary map:
                val = None
                evidence_text = ""
                
                # Check if we can find the label in the source's parsed spec tables
                # To mock this, we can search the source's content text
                content_text = source.description or ""
                
                # We search for label patterns e.g. "Grit: P150" or "Voltage Rating: 120 V"
                pattern = r'\b' + re.escape(label) + r'(?:\s+Rating)?\b[:\-]?\s*([A-Z0-9\-\.\/\s]+)\b'
                match = re.search(pattern, content_text, re.IGNORECASE)
                if match:
                    val = match.group(1).strip()
                    evidence_text = match.group(0).strip()
                
                if val:
                    # Clean and normalize the value
                    val_norm = val.lower().replace(" ", "")
                    candidates.append({
                        "value": val,
                        "value_normalized": val_norm,
                        "source_url": source.url,
                        "source_title": source.title,
                        "evidence_text": evidence_text
                    })

            if not candidates:
                # If no web evidence found, keep the Phase 3 attribute (which could be resolved from description)
                enriched_attributes.append(schema_attr)
                continue

            # Multi-source consensus check
            unique_values = list(set([c["value_normalized"] for c in candidates]))
            
            if len(unique_values) == 1:
                # Agreement across all sources!
                best_cand = candidates[0]
                enriched_attributes.append(ProductAttribute(
                    label=label,
                    value=best_cand["value"],
                    uom=expected_uom if best_cand["value"] else None,
                    normalized_value=best_cand["value"],
                    status="VERIFIED",
                    confidence=0.95,
                    source=best_cand["source_url"],
                    evidence=f"Consensus match: '{best_cand['evidence_text']}' from {best_cand['source_title']}."
                ))
            else:
                # Disagreement/Conflict!
                source_conflicts.append({
                    "attribute": label,
                    "candidates": candidates
                })
                # Set attribute status to CONFLICTED
                enriched_attributes.append(ProductAttribute(
                    label=label,
                    value=candidates[0]["value"],  # Default to first candidate
                    uom=expected_uom,
                    normalized_value=candidates[0]["value"],
                    status="CONFLICTED",
                    confidence=0.3,
                    source="MULTI_SOURCE",
                    evidence=f"Conflict detected between: " + "; ".join([f"{c['source_title']} ({c['value']})" for c in candidates])
                ))

        return {
            "enriched_attributes": enriched_attributes,
            "source_conflicts": source_conflicts
        }
