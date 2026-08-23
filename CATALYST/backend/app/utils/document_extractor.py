from typing import Dict, Any, Optional, List
import re

class DocumentExtractor:
    @staticmethod
    def extract_text_and_tables(html_content: str) -> Dict[str, Any]:
        """
        Parses HTML content to extract titles, headings, spec tables, and paragraphs.
        """
        extracted = {
            "title": "",
            "headings": [],
            "spec_table": {},
            "bullet_points": [],
            "raw_text": ""
        }

        if not html_content:
            return extracted

        # Extract Title
        title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
        if title_match:
            extracted["title"] = title_match.group(1).strip()

        # Extract Headings (h1, h2)
        headings = re.findall(r'<h[12]>(.*?)</h[12]>', html_content, re.IGNORECASE)
        extracted["headings"] = [h.strip() for h in headings]

        # Extract Specification Tables
        # Matches <tr><td>Label</td><td>Value</td></tr> or <th>/<td> with properties
        tr_matches = re.findall(r'<tr[^>]*>\s*<t[dh][^>]*>(.*?)</t[dh]>\s*<t[dh][^>]*>(.*?)</t[dh]>\s*</tr>', html_content, re.DOTALL | re.IGNORECASE)
        for label, val in tr_matches:
            # Strip tags and normalize spacing
            lbl_clean = re.sub(r'<[^>]*>', '', label).strip()
            val_clean = re.sub(r'<[^>]*>', '', val).strip()
            if lbl_clean:
                lbl_clean = re.sub(r'\s*:\s*$', '', lbl_clean)  # Strip trailing colons
                extracted["spec_table"][lbl_clean] = val_clean

        # Extract Bullet Points
        li_matches = re.findall(r'<li>(.*?)</li>', html_content, re.IGNORECASE)
        extracted["bullet_points"] = [re.sub(r'<[^>]*>', '', li).strip() for li in li_matches]

        # Extract paragraphs/text
        p_matches = re.findall(r'<p>(.*?)</p>', html_content, re.IGNORECASE)
        text_blocks = [re.sub(r'<[^>]*>', '', p).strip() for p in p_matches]
        extracted["raw_text"] = " ".join(text_blocks)

        return extracted

    @classmethod
    def match_product(cls, html_content: str, brand: Optional[str], mpn: Optional[str]) -> str:
        """
        Checks if the fetched page content matches the targeted brand and MPN.
        Returns: MATCHED, PROBABLE_MATCH, or REJECTED.
        """
        if not html_content:
            return "REJECTED"

        content_lower = html_content.lower()

        # Match exact MPN (non-alphanumeric stripped)
        if mpn:
            mpn_clean = re.sub(r'[^\w]', '', mpn.lower())
            content_clean = re.sub(r'[^\w]', '', content_lower)
            if mpn_clean in content_clean:
                return "MATCHED"

        # Match Brand
        brand_matched = False
        if brand:
            if brand.lower() in content_lower:
                brand_matched = True

        # If brand is matched and there is some keyword overlap
        if brand_matched:
            return "PROBABLE_MATCH"

        return "REJECTED"
