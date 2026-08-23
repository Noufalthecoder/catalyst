import pandas as pd
from typing import List, Dict, Union
from pathlib import Path

from app.utils.cleaners import PlaceholderNormalizer

class InputDataLoader:
    EXPECTED_COLUMNS = [
        "Mfg_Part_Num",
        "Part_Desc",
        "E1_Brand",
        "Unilog_Brand",
        "DIB_Brand",
        "Part_Manuf"
    ]

    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)

    def load(self) -> List[Dict]:
        """
        Loads the input data from XLSX or CSV and validates the schema.
        Returns a list of cleaned records.
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"Input file not found: {self.file_path}")

        if self.file_path.suffix.lower() == '.csv':
            df = pd.read_csv(self.file_path)
        elif self.file_path.suffix.lower() == '.xlsx':
            df = pd.read_excel(self.file_path)
        else:
            raise ValueError(f"Unsupported file extension: {self.file_path.suffix}")

        self._validate_schema(df)
        
        records = df.to_dict(orient="records")
        cleaned_records = [PlaceholderNormalizer.clean_record(r) for r in records]
        return cleaned_records

    def _validate_schema(self, df: pd.DataFrame):
        """
        Validates that all exactly required columns exist.
        """
        missing = [col for col in self.EXPECTED_COLUMNS if col not in df.columns]
        if missing:
            raise ValueError(f"Input schema error. Missing columns: {missing}")
