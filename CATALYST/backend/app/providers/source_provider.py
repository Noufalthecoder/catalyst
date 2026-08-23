import time
import re
import urllib.request
import urllib.parse
import urllib.error
import hashlib
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from app.models.product import CanonicalProduct, ProductSource
from app.providers.search_provider import SearchProvider, DuckDuckGoSearchProvider, NoneSearchProvider
from app.utils.source_discovery import SourceDiscoveryEngine

logger = logging.getLogger(__name__)

class SourceProvider:
    def discover_and_fetch(self, product: CanonicalProduct) -> List[ProductSource]:
        raise NotImplementedError()

class LiveWebSourceProvider(SourceProvider):
    def __init__(self, search_provider: SearchProvider, cache_dir: str = "../data/cache/web", rate_limit_delay: float = 0.1):
        self.search_provider = search_provider
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0.0

    def _get_cache_path(self, url: str) -> Path:
        url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{url_hash}.json"

    def _fetch_url_with_retry(self, url: str, retries: int = 3, timeout: float = 5.0) -> Optional[str]:
        # Enforce rate-limiting delay
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()

        backoff = 1.0
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        for attempt in range(retries):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    content_type = response.info().get_content_type()
                    # Skip binary downloads except HTML and plain text
                    if "html" not in content_type and "text" not in content_type:
                        logger.warning(f"Skipping unsupported content-type: {content_type} for {url}")
                        return None
                    return response.read().decode("utf-8", errors="ignore")
            except urllib.error.HTTPError as e:
                # Handle HTTP codes (e.g. 404, 500)
                logger.warning(f"HTTPError {e.code} for URL: {url} (Attempt {attempt+1}/{retries})")
                if e.code in [404, 403]:
                    break # Don't retry client errors
            except Exception as e:
                logger.warning(f"Request failed for URL {url}: {e} (Attempt {attempt+1}/{retries})")
            
            time.sleep(backoff)
            backoff *= 2
        return None

    def discover_and_fetch(self, product: CanonicalProduct) -> List[ProductSource]:
        brand = product.identity.brand or ""
        mpn = product.identity.raw_mpn or ""
        mfg = product.identity.manufacturer or ""
        prod_type = product.taxonomy.product_type or ""

        # 1. Generate Query Strategies
        queries = []
        if brand and mpn:
            queries.append(f"{brand} {mpn}")
        if mfg and mpn:
            queries.append(f"{mfg} {mpn}")
        if mpn:
            queries.append(f"{mpn} official specifications")
        if brand and prod_type and mpn:
            queries.append(f"{brand} {prod_type} {mpn}")

        # Remove empty strings
        queries = [q for q in queries if q.strip()]

        candidate_urls = []
        
        # If NoneSearchProvider, yield SOURCE_PROVIDER_NOT_CONFIGURED error
        if isinstance(self.search_provider, NoneSearchProvider):
            logger.warning("Search provider is not configured.")
            return []

        # Run Search Resolution (limit to top queries to prevent excessive queries)
        for q in queries[:2]:
            urls = self.search_provider.search(q)
            for u in urls:
                if u not in candidate_urls:
                    candidate_urls.append(u)
            if len(candidate_urls) >= 5:
                break

        # Filter and prioritize official manufacturer sources
        mfg_domain = SourceDiscoveryEngine.get_manufacturer_domain(brand)
        
        ranked_candidates = []
        for url in candidate_urls[:6]:
            domain = urllib.parse.urlparse(url).netloc.lower()
            
            # Simple relevance filtering
            # URL must contain brand keywords or MPN segment
            url_lower = url.lower()
            mpn_clean = re.sub(r'\W+', '', mpn.lower()) if mpn else ""
            url_clean = re.sub(r'\W+', '', url_lower)
            
            if mpn_clean and mpn_clean not in url_clean:
                # Skip irrelevant search spam
                continue

            is_official = False
            if mfg_domain and mfg_domain in domain:
                is_official = True

            ranked_candidates.append({
                "url": url,
                "domain": domain,
                "is_official": is_official
            })

        # Sort official domains first
        ranked_candidates.sort(key=lambda x: x["is_official"], reverse=True)

        fetched_sources = []
        for cand in ranked_candidates[:3]:
            url = cand["url"]
            cache_path = self._get_cache_path(url)
            
            fetch_res = None
            if cache_path.exists():
                try:
                    with open(cache_path, "r", encoding="utf-8") as f:
                        fetch_res = json.load(f)
                        # Check origin
                        if fetch_res.get("source_origin") != "LIVE":
                            fetch_res = None # force refresh if cache is from simulation
                except Exception:
                    pass

            if not fetch_res:
                content = self._fetch_url_with_retry(url)
                if not content:
                    continue
                
                fetch_res = {
                    "url": url,
                    "http_status": 200,
                    "content": content,
                    "retrieved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "content_hash": hashlib.md5(content.encode("utf-8")).hexdigest(),
                    "source_origin": "LIVE",
                    "extraction_status": "SUCCESS"
                }
                
                try:
                    with open(cache_path, "w", encoding="utf-8") as f:
                        json.dump(fetch_res, f, indent=2)
                except Exception:
                    pass

            source_model = ProductSource(
                url=url,
                domain=cand["domain"],
                source_type="MANUFACTURER_PRODUCT_PAGE" if cand["is_official"] else "DISTRIBUTOR",
                authority_level="PRIMARY" if cand["is_official"] else "SECONDARY",
                title=f"{brand} Specifications" if brand else "Specs Page",
                description=fetch_res.get("content"),
                retrieved_at=fetch_res.get("retrieved_at"),
                content_hash=fetch_res.get("content_hash"),
                http_status=fetch_res.get("http_status"),
                extraction_status=fetch_res.get("extraction_status"),
                source_origin="LIVE"
            )
            fetched_sources.append(source_model)

        return fetched_sources

class FixtureSourceProvider(SourceProvider):
    def __init__(self, cache_dir: str = "../data/cache/web"):
        self.cache_dir = Path(cache_dir)

    def discover_and_fetch(self, product: CanonicalProduct) -> List[ProductSource]:
        """
        Mock resolver that returns local mock files / simulated page content.
        Identical to historical SourceFetcher simulation.
        """
        brand = product.identity.brand
        mpn = product.identity.raw_mpn
        prod_type = product.taxonomy.product_type
        
        # Load from SourceDiscoveryEngine
        candidates = SourceDiscoveryEngine.discover_candidate_urls(brand, mpn, prod_type)
        
        fetched_sources = []
        from app.utils.source_fetcher import SourceFetcher
        fetcher = SourceFetcher(cache_dir=str(self.cache_dir))
        
        for cand in candidates[:3]:
            url = cand["url"]
            res = fetcher.fetch(url)
            
            source_model = ProductSource(
                url=url,
                domain=cand["domain"],
                source_type=cand["source_type"],
                authority_level=cand["authority_level"],
                title=cand["title"],
                description=res.get("content"),
                retrieved_at=res.get("retrieved_at"),
                content_hash=res.get("content_hash"),
                http_status=res.get("http_status"),
                extraction_status=res.get("extraction_status"),
                source_origin="FIXTURE"
            )
            fetched_sources.append(source_model)
            
        return fetched_sources
