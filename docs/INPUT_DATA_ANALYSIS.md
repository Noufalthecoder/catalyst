# Input Data Analysis

## 1. Raw Input Schema
- `Mfg_Part_Num`: Manufacturer Part Number. High fill rate, but often concatenated with brands or sizes.
- `Part_Desc`: Primary input text. Highly unstructured, often contains brand, series, dimensions, UOM, and sometimes category.
- `E1_Brand`: Secondary brand field. Frequently empty (`-- Unbranded --`).
- `Unilog_Brand`: Tertiary brand field. Almost entirely empty (`-- No Unilog Brand --`).
- `DIB_Brand`: Quaternary brand field. Often empty (`-- No DIB Brand --`).
- `Part_Manuf`: Manufacturer name and code (e.g., `Milwaukee Accessory (4031)`). High fill rate.

## 2. Fill Rates and Cardinality
- Total Rows Sampled: 1,000
- `Unilog_Brand`: 0% fill rate (100% missing)
- `E1_Brand`: ~20% fill rate
- `DIB_Brand`: ~24% fill rate
- `Part_Manuf`: ~96% fill rate

## 3. Brand Data Fragmentation
Brands are scattered across `E1_Brand`, `DIB_Brand`, and frequently embedded in `Part_Desc` or `Part_Manuf`. Resolution must prioritize these fields conditionally and validate against known manufacturer master lists.

## 4. Anomalies
- Placeholders like `-- Unbranded --`, `-- No Unilog Brand --`, `-- No DIB Brand --`, and `-` are used extensively instead of nulls.
- `Part_Manuf` contains manufacturer codes appended in parentheses.
