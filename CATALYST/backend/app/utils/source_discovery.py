from typing import List, Dict, Any, Optional
import re

class SourceDiscoveryEngine:
    # Mapping of common brands to their official corporate domains
    BRAND_DOMAINS = {
        "3M": "3m.com",
        "Diablo": "diablotools.com",
        "Milwaukee": "milwaukeetool.com",
        "DEWALT": "dewalt.com",
        "Makita": "makitatools.com",
        "GE": "geappliances.com",
        "Speed Queen": "speedqueen.com",
        "TimberTech": "timbertech.com",
        "Trex": "trex.com",
        "Lutron": "lutron.com",
        "Leviton": "leviton.com",
        "Kichler": "kichler.com",
        "Satco": "satco.com",
        "Philips": "philips.com",
        "Wiz": "wizconnected.com",
        "Feit Electric": "feit.com",
        "Bosch": "boschtools.com",
        "Dremel": "dremel.com",
        "Grizzly": "grizzly.com",
        "Kreg": "kregtool.com",
        "Vessel": "vesseltools.com",
        "Senco": "senco.com",
        "Mirka": "mirka.com",
        "Festool": "festoolusa.com",
        "ProVia": "provia.com",
        "CertainTeed": "certainteed.com",
        "LP SmartSide": "lpcorp.com",
        "James Hardie": "jameshardie.com",
        "First Alert": "firstalert.com",
        "Radians": "radians.com",
        "Malco": "malcoproducts.com",
        "Irwin": "irwin.com",
        "Sabre": "sabrered.com",
        "Streamlight": "streamlight.com"
    }

    @classmethod
    def get_manufacturer_domain(cls, brand: Optional[str]) -> Optional[str]:
        """
        Returns the likely official domain for the manufacturer brand.
        """
        if not brand:
            return None
        return cls.BRAND_DOMAINS.get(brand)

    @classmethod
    def generate_queries(cls, brand: Optional[str], mpn: Optional[str], 
                         product_type: Optional[str]) -> List[str]:
        """
        Generates multiple search query variants to locate primary sources.
        """
        queries = []
        if not mpn:
            return queries

        brand_str = brand if brand else ""
        type_str = product_type if product_type and product_type != "UNKNOWN" else ""

        # Query 1: Exact Brand + MPN
        if brand_str:
            queries.append(f"{brand_str} {mpn}")
            # Query 2: Brand + Type + MPN
            if type_str:
                queries.append(f"{brand_str} {type_str} {mpn}")
        else:
            queries.append(mpn)

        # Query 3: MPN + datasheet
        queries.append(f"{brand_str} {mpn} datasheet")

        return [q.strip() for q in queries]

    @classmethod
    def discover_candidate_urls(cls, brand: Optional[str], mpn: Optional[str], 
                                product_type: Optional[str]) -> List[Dict[str, Any]]:
        """
        Mock search engine that returns mock URLs for our 20 pilot products.
        This provides stable urls to crawl in Mode B.
        """
        candidates = []
        if not mpn:
            return candidates

        domain = cls.get_manufacturer_domain(brand)
        if not domain:
            domain = "unknown-manufacturer.com"

        # Generate a simulated official URL
        sanitized_mpn = re.sub(r'[^\w\-]', '', mpn.lower())
        mfg_url = f"https://www.{domain}/products/{sanitized_mpn}"
        datasheet_url = f"https://www.{domain}/documents/{sanitized_mpn}-datasheet.pdf"

        # Add primary source
        candidates.append({
            "url": mfg_url,
            "domain": domain,
            "source_type": "MANUFACTURER_PRODUCT_PAGE",
            "authority_level": "PRIMARY",
            "title": f"{brand} {mpn} Product Details" if brand else f"Product Details for {mpn}"
        })

        # Add secondary source (datasheet)
        candidates.append({
            "url": datasheet_url,
            "domain": domain,
            "source_type": "MANUFACTURER_DATASHEET",
            "authority_level": "PRIMARY",
            "title": f"{brand} {mpn} Technical Specification Datasheet" if brand else f"Datasheet for {mpn}"
        })

        # Add secondary distributor link simulation
        candidates.append({
            "url": f"https://www.distributor-direct.com/item/{sanitized_mpn}",
            "domain": "distributor-direct.com",
            "source_type": "DISTRIBUTOR",
            "authority_level": "SECONDARY",
            "title": f"Buy {brand} {mpn} online" if brand else f"Buy {mpn} online"
        })

        return candidates
