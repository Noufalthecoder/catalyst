from typing import Dict, Any, Optional

class ProductUnderstandingEngine:
    @staticmethod
    def analyze(part_desc: Optional[str], mfg_part_num: Optional[str], 
                brand: Optional[str], manufacturer: Optional[str], 
                product_type: Optional[str], alternate_mpn: Optional[str] = None) -> Dict[str, Any]:
        """
        Synthesizes raw fields and identity markers to generate a semantic summary 
        and structural descriptors without hallucinations.
        """
        prod_type = product_type if product_type and product_type != "UNKNOWN" else "Unknown Product"
        mfg_name = manufacturer if manufacturer else "Unknown Manufacturer"
        brand_name = brand if brand else "Generic"
        mpn_str = mfg_part_num if mfg_part_num else "Unknown MPN"

        # Construct summary safely
        summary = f"This product is classified as a {prod_type}. "
        if brand_name != "Generic":
            summary += f"It is manufactured/branded by {brand_name} (Manufacturer: {mfg_name}) "
        else:
            summary += f"It is manufactured by {mfg_name} "
        summary += f"under Part Number {mpn_str}."

        if alternate_mpn:
            summary += f" Alternate Part Number: {alternate_mpn}."

        # Compute status and confidence
        confidence = 0.0
        if product_type and product_type != "UNKNOWN":
            confidence += 0.4
        if brand:
            confidence += 0.3
        if manufacturer:
            confidence += 0.3

        status = "UNKNOWN"
        if confidence >= 0.9:
            status = "VERIFIED"
        elif confidence >= 0.7:
            status = "PROBABLE"
        elif confidence > 0.0:
            status = "AMBIGUOUS"

        # Determine product family (series if available, or brand + type)
        family = f"{brand_name} {prod_type}"

        return {
            "product_name": prod_type,
            "product_type": prod_type,
            "product_family": family,
            "semantic_summary": summary,
            "confidence": round(confidence, 2),
            "status": status
        }
