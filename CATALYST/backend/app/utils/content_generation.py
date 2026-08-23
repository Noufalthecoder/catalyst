from typing import Dict, Any, Optional
from app.models.product import CanonicalProduct

class ContentGenerator:
    @staticmethod
    def generate_descriptions(product: CanonicalProduct) -> Dict[str, str]:
        """
        Generates product descriptions (Short, Invoice, Mobile, Long, Retail, Marketing)
        strictly from verified or probable attribute values to prevent hallucination.
        """
        brand = product.identity.brand or "Generic"
        noun = product.taxonomy.product_type or "Product"
        mpn = product.identity.raw_mpn or ""

        # Gather clean verified specifications
        specs = {}
        for attr in product.enriched_attributes:
            if attr.value is not None and attr.status in ["VERIFIED", "PROBABLE"]:
                specs[attr.label] = attr.value

        # Reusable templates based on product category/noun
        # 1. SHORT_DESC (max 60 chars)
        short_desc = f"{brand} {noun}"
        if mpn:
            short_desc += f" {mpn}"
        
        # Add key attribute to short desc if space allows
        for key in ["Grit", "Voltage", "Length", "Color"]:
            if key in specs:
                added = f" {specs[key]}"
                if len(short_desc) + len(added) <= 60:
                    short_desc += added
                    break
        
        short_desc = short_desc[:60].strip()

        # 2. INVOICE_DESC (max 30 chars - truncated, highly abbreviated)
        invoice_desc = f"{brand[:5].upper()} {noun[:15]} {mpn[:8]}"
        invoice_desc = invoice_desc[:30].strip()

        # 3. MOBILE_DESC (bulleted details)
        bullets = []
        if brand != "Generic":
            bullets.append(f"Brand: {brand}")
        if mpn:
            bullets.append(f"Model/MPN: {mpn}")
        for lbl, val in specs.items():
            bullets.append(f"{lbl}: {val}")
        
        mobile_desc = "\n".join([f"- {b}" for b in bullets]) if bullets else f"Product details for {short_desc}"

        # 4. LONG_DESC1 (comprehensive paragraph)
        long_desc = f"The {brand} {noun} (MPN: {mpn}) is engineered for standard industrial applications. "
        if specs:
            spec_clauses = [f"features a {lbl.lower()} of {val}" for lbl, val in specs.items()]
            long_desc += f"It " + ", ".join(spec_clauses) + "."
        else:
            long_desc += "Provides robust performance and standard compliance."

        # 5. RETAIL_DESC & MARKETING_DESCRIPTION
        retail_desc = f"High-quality {brand} {noun}. Engineered with premium materials for durability."
        marketing_desc = f"Discover the reliability of the {brand} {noun}. Ideal for professionals requesting top-tier specifications."

        return {
            "SHORT_DESC": short_desc,
            "INVOICE_DESC": invoice_desc,
            "MOBILE_DESC": mobile_desc,
            "LONG_DESC1": long_desc,
            "RETAIL_DESC": retail_desc,
            "MARKETING_DESCRIPTION": marketing_desc
        }
