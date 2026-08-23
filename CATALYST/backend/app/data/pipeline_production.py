import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.models.product import CanonicalProduct
from app.data.pipeline_delivery import PipelineDelivery
from app.utils.review_queue import ReviewQueue
from app.utils.evaluation import EvaluationEngine

logger = logging.getLogger(__name__)

class ProductionPipeline:
    def __init__(self, output_dir: str = "../data/output", cache_dir: str = "../data/cache/web"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir = Path(cache_dir)
        
        # In-memory status tracker
        self.tracker_file = self.output_dir / "production_batch_status.json"
        self.status_tracker = self._load_tracker()

    def _load_tracker(self) -> Dict[str, str]:
        if self.tracker_file.exists():
            try:
                with open(self.tracker_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_tracker(self):
        try:
            with open(self.tracker_file, "w") as f:
                json.dump(self.status_tracker, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save production tracker: {e}")

    def run_batch(self, input_jsonl_path: str, max_products: Optional[int] = None, 
                  resume: bool = True, dry_run: bool = False) -> Dict[str, Any]:
        """
        Processes products in batch with support for resuming, dry-runs, and status logging.
        """
        input_path = Path(input_jsonl_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_jsonl_path}")

        products_to_process = []
        
        with open(input_path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                prod_dict = json.loads(line)
                mpn = prod_dict.get("identity", {}).get("raw_mpn", f"index_{idx}")
                
                # Check resume status
                if resume and self.status_tracker.get(mpn) == "COMPLETED":
                    continue

                products_to_process.append((mpn, prod_dict))
                if max_products and len(products_to_process) >= max_products:
                    break

        if dry_run:
            logger.info(f"[DRY RUN] Would process {len(products_to_process)} products.")
            return {"dry_run": True, "count": len(products_to_process)}

        processed_products = []
        from app.data.pipeline_enrichment import WebEnrichmentEngine
        enrich_engine = WebEnrichmentEngine(cache_dir=str(self.cache_dir), output_dir=str(self.output_dir))
        
        # PipelineDelivery runs normalization and validation
        delivery_pipeline = PipelineDelivery(cache_dir=str(self.cache_dir), output_dir=str(self.output_dir))

        for mpn, prod_dict in products_to_process:
            self.status_tracker[mpn] = "PROCESSING"
            self._save_tracker()
            
            try:
                product = CanonicalProduct.model_validate(prod_dict)
                
                # 1. Web Enrichment
                enriched_prod = enrich_engine.process_product(product)
                
                # 2. Normalization & Validation (inside delivery pipeline mapping)
                # We normalize attributes directly on the enriched_prod
                from app.utils.attribute_schema import AttributeSchemaEngine
                from app.utils.normalization import AttributeNormalizationEngine
                from app.utils.diagnostics import UnknownAttributeDiagnostics
                
                class_name = enriched_prod.taxonomy.class_name or enriched_prod.taxonomy.fine or "Abrasives"
                expected_schema = AttributeSchemaEngine.generate_schema(class_name)
                schema_lookup = {attr.label.strip().lower(): attr for attr in expected_schema}

                for attr in enriched_prod.enriched_attributes:
                    label_lower = attr.label.strip().lower()
                    expected_type = "TEXT"
                    if label_lower in schema_lookup:
                        expected_type = schema_lookup[label_lower].value_type or "TEXT"
                    
                    AttributeNormalizationEngine.validate_and_normalize(attr, expected_type)
                
                UnknownAttributeDiagnostics.diagnose_product_attributes(enriched_prod)
                
                processed_products.append(enriched_prod)
                self.status_tracker[mpn] = "COMPLETED"
            except Exception as e:
                logger.error(f"Failed to process product {mpn}: {e}")
                self.status_tracker[mpn] = "FAILED"
            
            self._save_tracker()

        # Generate evaluations & review queues if we processed items
        if processed_products:
            ReviewQueue.evaluate_and_register(processed_products, str(self.output_dir))
            EvaluationEngine.evaluate_batch(processed_products, str(self.output_dir))

        return {
            "processed_count": len(processed_products),
            "tracker": self.status_tracker,
            "processed_products": processed_products
        }
