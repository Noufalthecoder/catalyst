import urllib.request
import urllib.parse
import re
import logging
from typing import List

logger = logging.getLogger(__name__)

class SearchProvider:
    def search(self, query: str) -> List[str]:
        """
        Runs search and returns a list of candidate URLs.
        """
        raise NotImplementedError()

class DuckDuckGoSearchProvider(SearchProvider):
    def search(self, query: str) -> List[str]:
        """
        Queries DuckDuckGo HTML endpoint and extracts target URLs from redirects.
        """
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36"
        }
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode("utf-8", errors="ignore")
            
            # Find DDG outbound redirect links (uddg=URL)
            matches = re.findall(r'uddg=([^&"\']+)', html)
            urls = []
            for m in matches:
                decoded_url = urllib.parse.unquote(m)
                if decoded_url.startswith("http") and "duckduckgo.com" not in decoded_url:
                    urls.append(decoded_url)
            
            # De-duplicate while preserving order
            seen = set()
            unique_urls = []
            for u in urls:
                if u not in seen:
                    seen.add(u)
                    unique_urls.append(u)
                    
            logger.info(f"DDG Search resolved {len(unique_urls)} links for: '{query}'")
            return unique_urls
            
        except Exception as e:
            logger.error(f"DuckDuckGo search fetch failed for '{query}': {e}")
            return []

class NoneSearchProvider(SearchProvider):
    def search(self, query: str) -> List[str]:
        logger.warning(f"No search provider configured. Request for '{query}' ignored.")
        return []
