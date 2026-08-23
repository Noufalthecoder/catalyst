import os
import re
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.models.product import CanonicalProduct, ProductSource, ProductAttribute
from app.utils.source_discovery import SourceDiscoveryEngine
from app.utils.source_ranker import SourceRanker
from app.utils.source_fetcher import SourceFetcher
from app.utils.document_extractor import DocumentExtractor
from app.utils.evidence_extractor import EvidenceExtractor
from app.providers.search_provider import DuckDuckGoSearchProvider, NoneSearchProvider
from app.providers.source_provider import LiveWebSourceProvider, FixtureSourceProvider

logger = logging.getLogger(__name__)

class WebEnrichmentEngine:
    def __init__(self, cache_dir: str = "../data/cache/web", output_dir: str = "../data/output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure providers based on environment variables
        env = os.environ.get("ENVIRONMENT", "production")
        provider_config = os.environ.get("SOURCE_PROVIDER", "fixture" if env == "TEST" else "live")
        search_config = os.environ.get("SEARCH_PROVIDER", "duckduckgo")

        if provider_config == "fixture":
            self.provider = FixtureSourceProvider(cache_dir=cache_dir)
        else:
            if search_config == "none":
                search_prov = NoneSearchProvider()
            else:
                search_prov = DuckDuckGoSearchProvider()
            self.provider = LiveWebSourceProvider(search_provider=search_prov, cache_dir=cache_dir)

    def process_product(self, product: CanonicalProduct) -> CanonicalProduct:
        """
        Enriches a CanonicalProduct using the active web source provider,
        spec parsing, and evidence consensus.
        """
        brand = product.identity.brand
        mpn = product.identity.raw_mpn

        # 1. Discover and fetch sources
        product.sources = self.provider.discover_and_fetch(product)
        
        # Apply document verification rules
        for src in product.sources:
            relevance = DocumentExtractor.match_product(src.description, brand, mpn)
            if relevance == "REJECTED":
                logger.warning(f"Rejected fetched source due to low relevance: {src.url}")
                src.authority_level = "UNTRUSTED"

        # 5. Evidence Extraction & Consensus
        enrich_res = EvidenceExtractor.extract_attributes(product.sources, product.attributes)
        
        product.enriched_attributes = enrich_res["enriched_attributes"]
        product.source_conflicts = enrich_res["source_conflicts"]

        # 6. Calculate Web Quality Score
        quality_score = 0.0
        has_primary = any(s.authority_level == "PRIMARY" for s in product.sources)
        if has_primary:
            quality_score += 0.4
        
        has_mpn_match = any(DocumentExtractor.match_product(s.description, brand, mpn) == "MATCHED" for s in product.sources)
        if has_mpn_match:
            quality_score += 0.3

        enriched_count = sum(1 for a in product.enriched_attributes if a.value is not None)
        if product.enriched_attributes:
            coverage = enriched_count / len(product.enriched_attributes)
            quality_score += (coverage * 0.2)

        if not product.source_conflicts:
            quality_score += 0.1

        product.web_quality_score = round(quality_score, 2)

        return product

    def run_pilot(self, input_jsonl_path: str, count: int = 20) -> Dict[str, Any]:
        """
        Runs the pilot enrichment pipeline over the first 'count' items in the input.
        """
        input_path = Path(input_jsonl_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input JSONL file not found: {input_jsonl_path}")

        pilot_products = []
        with open(input_path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                if idx >= count:
                    break
                line = line.strip()
                if not line:
                    continue
                product_dict = json.loads(line)
                product = CanonicalProduct.model_validate(product_dict)
                
                # Enrich record
                enriched_prod = self.process_product(product)
                pilot_products.append(enriched_prod)

        # Write output JSONL for pilot
        output_jsonl_path = self.output_dir / "web_enrichment_pilot.jsonl"
        with open(output_jsonl_path, "w", encoding="utf-8") as f:
            for prod in pilot_products:
                f.write(prod.model_dump_json(by_alias=True) + "\n")

        # Pilot Metrics Calculation
        total_products = len(pilot_products)
        products_with_sources = sum(1 for p in pilot_products if p.sources)
        products_with_official = sum(1 for p in pilot_products if any("MANUFACTURER" in s.source_type for s in p.sources))
        products_with_exact_mpn = sum(1 for p in pilot_products if any(DocumentExtractor.match_product(s.description, p.identity.brand, p.identity.raw_mpn) == "MATCHED" for s in p.sources))
        
        attributes_enriched = 0
        attributes_verified = 0
        attributes_conflicted = 0
        attributes_unknown = 0
        total_attributes = 0

        for p in pilot_products:
            total_attributes += len(p.enriched_attributes)
            for attr in p.enriched_attributes:
                if attr.value is not None:
                    attributes_enriched += 1
                if attr.status == "VERIFIED":
                    attributes_verified += 1
                elif attr.status == "CONFLICTED":
                    attributes_conflicted += 1
                elif attr.status == "UNKNOWN":
                    attributes_unknown += 1

        avg_sources = sum(len(p.sources) for p in pilot_products) / total_products if total_products else 0.0

        report = {
            "total_products": total_products,
            "products_with_sources": products_with_sources,
            "products_with_official_sources": products_with_official,
            "products_with_exact_mpn_evidence": products_with_exact_mpn,
            "products_without_useful_sources": total_products - products_with_sources,
            "total_attributes": total_attributes,
            "attributes_enriched": attributes_enriched,
            "attributes_verified": attributes_verified,
            "attributes_conflicted": attributes_conflicted,
            "attributes_unknown": attributes_unknown,
            "average_sources_per_product": round(avg_sources, 2)
        }

        output_report_path = self.output_dir / "web_enrichment_pilot_report.json"
        with open(output_report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return report
