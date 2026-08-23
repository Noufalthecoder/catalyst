from typing import Dict, Any, Optional, List
from app.utils.source_discovery import SourceDiscoveryEngine

class SourceRanker:
    @staticmethod
    def score_source(source: Dict[str, Any], brand: Optional[str], mpn: Optional[str], 
                     product_type: Optional[str]) -> Dict[str, Any]:
        """
        Calculates a relevance and authority score for a discovered source.
        
        Scoring Weights:
        - Official manufacturer domain match: +40 points
        - Exact MPN matching in URL or title: +35 points
        - Brand matching in domain or title: +10 points
        - Product type match in URL or title: +8 points
        - Product name/type similarity: +7 points
        
        Maximum possible score: 100
        """
        relevance_score = 0.0
        authority_score = 0.0
        
        url = source.get("url", "")
        title = source.get("title", "")
        domain = source.get("domain", "")

        # 1. Official Manufacturer Domain Check
        official_domain = SourceDiscoveryEngine.get_manufacturer_domain(brand)
        if official_domain and official_domain in domain:
            authority_score += 40.0

        # 2. Exact MPN Check
        if mpn:
            mpn_clean = mpn.lower()
            if mpn_clean in url.lower() or mpn_clean in title.lower():
                relevance_score += 35.0

        # 3. Brand Match
        if brand:
            brand_clean = brand.lower()
            if brand_clean in domain.lower() or brand_clean in title.lower():
                relevance_score += 10.0

        # 4. Product Type Match
        if product_type and product_type != "UNKNOWN":
            pt_clean = product_type.lower().replace(" ", "")
            url_clean = url.lower().replace("-", "").replace("_", "")
            title_clean = title.lower().replace(" ", "")
            if pt_clean in url_clean or pt_clean in title_clean:
                relevance_score += 8.0

        # 5. Product Name Similarity
        # If the title contains words from the product type
        if product_type and product_type != "UNKNOWN":
            words = product_type.lower().split()
            matches = sum(1 for w in words if w in title.lower())
            if matches == len(words):
                relevance_score += 7.0
            elif matches > 0:
                relevance_score += 4.0

        final_score = authority_score + relevance_score
        
        # Determine authority level based on source type and scoring
        auth_level = "UNTRUSTED"
        if final_score >= 75.0:
            auth_level = "PRIMARY"
        elif final_score >= 40.0:
            auth_level = "SECONDARY"

        source_copy = dict(source)
        source_copy["relevance_score"] = relevance_score
        source_copy["authority_score"] = authority_score
        source_copy["final_score"] = final_score
        source_copy["authority_level"] = auth_level
        
        return source_copy

    @classmethod
    def rank_and_filter(cls, sources: List[Dict[str, Any]], brand: Optional[str], 
                        mpn: Optional[str], product_type: Optional[str]) -> List[Dict[str, Any]]:
        """
        Scores all candidate sources, filters out untrusted, and sorts by final score.
        """
        scored_sources = [cls.score_source(s, brand, mpn, product_type) for s in sources]
        # Filter out untrusted sources
        trusted = [s for s in scored_sources if s["authority_level"] != "UNTRUSTED"]
        # Sort descending
        return sorted(trusted, key=lambda x: x["final_score"], reverse=True)
