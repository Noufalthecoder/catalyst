import unicodedata
import re

class TextNormalizer:
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Removes repeated spaces, leading/trailing whitespace."""
        if not isinstance(text, str):
            return text
        return re.sub(r'\s+', ' ', text).strip()

    @staticmethod
    def normalize_unicode(text: str) -> str:
        """Normalizes unicode characters (NFKD)."""
        if not isinstance(text, str):
            return text
        return unicodedata.normalize('NFKD', text)

    @staticmethod
    def normalize_for_comparison(text: str) -> str:
        """
        Creates a deeply normalized string solely for matching purposes (lowercased, 
        punctuation removed, unicode normalized).
        """
        if not isinstance(text, str):
            return ""
        text = TextNormalizer.normalize_unicode(text)
        text = TextNormalizer.normalize_whitespace(text)
        # Remove punctuation and special symbols
        text = re.sub(r'[^\w\s]', '', text)
        return text.lower()
