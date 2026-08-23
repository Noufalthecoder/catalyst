import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from app.utils.cleaners import PlaceholderNormalizer

def test_is_placeholder():
    assert PlaceholderNormalizer.is_placeholder("-- Unbranded --") is True
    assert PlaceholderNormalizer.is_placeholder("-- No Unilog Brand --") is True
    assert PlaceholderNormalizer.is_placeholder("-") is True
    assert PlaceholderNormalizer.is_placeholder(None) is True
    assert PlaceholderNormalizer.is_placeholder("Real Brand") is False

def test_normalize():
    assert PlaceholderNormalizer.normalize("-- Unbranded --") is None
    assert PlaceholderNormalizer.normalize(" Valid String ") == "Valid String"
    assert PlaceholderNormalizer.normalize(123) == 123

def test_clean_record():
    record = {
        "Brand": "-- Unbranded --",
        "Part": "1234",
        "Mfg": "-"
    }
    cleaned = PlaceholderNormalizer.clean_record(record)
    assert cleaned["Brand"] is None
    assert cleaned["Part"] == "1234"
    assert cleaned["Mfg"] is None
