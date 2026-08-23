# DATA FOUNDATION

## Overview
The Data Foundation module sets up the robust ETL capabilities required for the CATALYST Enrichment Engine. Since the reference `.xlsx` files contain complex structures (merged cells, dual blocks), we use dedicated repositories to load and index them in a reusable way.

## Components
- **Input Loader (`input_loader.py`)**: Loads `Sample-1000_Items.xlsx`, enforcing strict schema checks on the required 6 raw columns. Applies `PlaceholderNormalizer` automatically.
- **Repositories**:
  - `ManufacturerRepository`: Indexes exact and normalized brands/manufacturers.
  - `FractionRepository`: Maps decimals (0.5) to fractions (1/2) accurately.
- **ReferenceDataManager**: A singleton that orchestrates loading all the repositories into memory and serves as the single source of truth for the app.
- **CanonicalProduct Model**: Pydantic models for type-safe representation of the product identity, taxonomy, attributes, and content.

## Usage
Run the CLI tool to profile the data:
```bash
python -m app.cli profile
```

Run tests to ensure everything is functioning correctly:
```bash
pytest backend/tests
```
