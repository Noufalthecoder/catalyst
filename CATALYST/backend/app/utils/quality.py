from typing import Any
from app.models.product import CanonicalProduct

class ProductQualityScore:
    @staticmethod
    def calculate_score(product: CanonicalProduct) -> float:
        """
        Calculates a composite product quality score (from 0.0 to 1.0) based on 
        evidence completeness, validation check results, and source authority.
        
        Formula Weights:
        1. Identity Confidence (15%): product.identity.identity_confidence
        2. Taxonomy Confidence (15%): product.taxonomy.confidence
        3. Source Authority (20%): +20% if at least one PRIMARY source is fetched
        4. Exact MPN Match (20%): +20% if MPN matches exact text in description
        5. Attribute Validity (20%): percentage of non-INVALID, non-UNKNOWN attributes
        6. Content/Description Completeness (10%): +10% if LONG_DESC1 is generated
        
        Maximum possible score: 1.0
        """
        score = 0.0

        # 1. Identity
        score += (product.identity.identity_confidence or 0.0) * 0.15

        # 2. Taxonomy
        score += (product.taxonomy.confidence or 0.0) * 0.15

        # 3. Source Authority
        has_primary = any(s.authority_level == "PRIMARY" for s in product.sources)
        if has_primary:
            score += 0.20

        # 4. Exact MPN Match
        has_mpn_match = any(
            product.identity.raw_mpn.lower() in (s.description or "").lower() 
            for s in product.sources
        )
        if has_mpn_match:
            score += 0.20

        # 5. Attribute Validity
        if product.enriched_attributes:
            valid_count = sum(1 for a in product.enriched_attributes if a.status in ["VERIFIED", "PROBABLE"])
            coverage = valid_count / len(product.enriched_attributes)
            score += coverage * 0.20

        # 6. Content completeness
        # Check descriptions mapped to delivery format
        from app.utils.content_generation import ContentGenerator
        descs = ContentGenerator.generate_descriptions(product)
        if descs.get("LONG_DESC1") and "engineered" in descs["LONG_DESC1"]:
            score += 0.10

        return round(score, 2)
