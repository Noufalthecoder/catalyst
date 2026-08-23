import pandas as pd
from typing import Dict, List, Optional, Union
from pathlib import Path

class FractionRepository:
    def __init__(self):
        self.decimal_to_frac = {}
        self.frac_to_decimal = {}

    def load_from_excel(self, file_path: Union[str, Path]):
        """
        Loads Decimal_Fraction.xlsx.
        Parses all blocks in the sheet (it has multiple side-by-side tables).
        """
        df = pd.read_excel(file_path, header=None)
        
        # Iterate over pairs of columns (Fraction | Decimal)
        num_cols = len(df.columns)
        for i in range(0, num_cols, 2):
            if i + 1 >= num_cols:
                break
            
            sub_df = df.iloc[:, i:i+2].dropna()
            for _, row in sub_df.iterrows():
                frac = str(row.iloc[0]).strip()
                try:
                    dec = float(row.iloc[1])
                    self.decimal_to_frac[dec] = frac
                    self.frac_to_decimal[frac] = dec
                except ValueError:
                    pass

    def decimal_to_fraction(self, decimal_value: float) -> Optional[str]:
        # Simple exact lookup, or extracting whole number + fraction
        if decimal_value in self.decimal_to_frac:
            return self.decimal_to_frac[decimal_value]
            
        # Handle mixed fractions e.g. 50.25 -> 50-1/4
        whole = int(decimal_value)
        remainder = round(decimal_value - whole, 6)
        
        if remainder in self.decimal_to_frac:
            frac = self.decimal_to_frac[remainder]
            if whole > 0:
                return f"{whole}-{frac}"
            return frac
            
        return None

    def fraction_to_decimal(self, fraction_value: str) -> Optional[float]:
        if fraction_value in self.frac_to_decimal:
            return self.frac_to_decimal[fraction_value]
        # Implementation for mixed like 50-1/4
        if "-" in fraction_value:
            parts = fraction_value.split("-")
            if len(parts) == 2 and parts[1] in self.frac_to_decimal:
                try:
                    return float(parts[0]) + self.frac_to_decimal[parts[1]]
                except ValueError:
                    pass
        return None
