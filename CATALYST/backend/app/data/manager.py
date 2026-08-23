from pathlib import Path
from typing import Optional
from app.data.repositories.manufacturer_repository import ManufacturerRepository
from app.data.repositories.fraction_repository import FractionRepository
import logging

logger = logging.getLogger(__name__)

class ReferenceDataManager:
    def __init__(self, reference_dir: str):
        self.reference_dir = Path(reference_dir)
        self.manufacturer_repository = ManufacturerRepository()
        self.fraction_repository = FractionRepository()
        self._loaded = False

    def load_all(self):
        if self._loaded:
            return

        mfg_file = self.reference_dir / "UniCat_Manufacturer_and_Brand_List.xlsx"
        fraction_file = self.reference_dir / "Decimal_Fraction.xlsx"
        
        try:
            if mfg_file.exists():
                self.manufacturer_repository.load_from_excel(mfg_file)
            else:
                logger.error(f"Missing manufacturer file: {mfg_file}")

            if fraction_file.exists():
                self.fraction_repository.load_from_excel(fraction_file)
            else:
                logger.error(f"Missing fraction file: {fraction_file}")
                
            # Further repositories (UOM, LOV, OutputSchema) would be loaded here.
        except Exception as e:
            logger.error(f"Failed to load reference data: {e}")
            raise
            
        self._loaded = True
