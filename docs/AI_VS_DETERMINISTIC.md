# AI vs Deterministic Boundaries

## 1. Deterministic (Python/Regex/Rules)
- Removing `-- Unbranded --` and other placeholders.
- Stripping ` (4031)` codes from manufacturer names.
- Extracting standard dimensions (e.g., `1/2" x 4"`) from descriptions.
- UOM standardization (`in`, `inch`, `"` -> `Inches`).
- Output generation and CSV formatting.

## 2. AI / LLM
- **Taxonomy Classification**: Deciding if a "Stikit Film P150" is an Abrasive Disc or Sandpaper.
- **Feature Extraction from PDFs**: Reading an unstructured spec sheet and identifying `ITEM_FEATURES`.
- **Anomaly Detection**: Flagging when an extracted attribute contradicts the `Part_Desc`.
