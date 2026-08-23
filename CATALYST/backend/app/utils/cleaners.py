import pandas as pd
import numpy as np

class PlaceholderNormalizer:
    """
    Normalizes common placeholder values found in the data into standard Python None.
    """
    KNOWN_PLACEHOLDERS = {
        "-- Unbranded --",
        "-- No Unilog Brand --",
        "-- No DIB Brand --",
        "-",
        "",
    }

    @classmethod
    def is_placeholder(cls, value) -> bool:
        """
        Checks if a given value is a known placeholder, blank, NaN, or None.
        """
        if pd.isna(value) or value is None:
            return True
        if isinstance(value, str):
            val_str = value.strip()
            if not val_str:
                return True
            if val_str in cls.KNOWN_PLACEHOLDERS:
                return True
        return False

    @classmethod
    def normalize(cls, value):
        """
        Returns None if the value is a placeholder, else returns the stripped string or original value.
        """
        if cls.is_placeholder(value):
            return None
        if isinstance(value, str):
            return value.strip()
        return value

    @classmethod
    def clean_record(cls, record: dict) -> dict:
        """
        Cleans a dictionary record by normalizing all its values.
        """
        return {k: cls.normalize(v) for k, v in record.items()}
