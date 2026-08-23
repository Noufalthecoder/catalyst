# Input Output Mapping

## 1. Direct Passthroughs
- `Mfg_Part_Num` -> `Mfg_Part_Num`
- `Part_Desc` -> `Part_Desc`
- `E1_Brand` -> `E1_Brand`
- `Unilog_Brand` -> `Unilog_Brand`
- `DIB_Brand` -> `DIB_Brand`
- `Part_Manuf` -> `Part_Manuf`

## 2. Transformations
- `Part_Manuf` -> (Cleaned) -> `MANUFACTURER_NAME`
- `E1_Brand` / `DIB_Brand` / `Part_Desc` -> (Resolved) -> `BRAND_NAME`
- `Mfg_Part_Num` -> `MANUFACTURER_PART_NUMBER`
- `Part_Desc` -> (Parsed) -> `MOBILE_DESC`, `SHORT_DESC`, Attributes, Dimensions.

## 3. Net-New Fields (Enrichment Required)
- `Dept`, `Class`, `Fine`, `Classpath` (Requires Taxonomy Engine)
- `ITEM_FEATURES_1..20` (Requires Web Source Intelligence / LLM extraction)
- `ATTRIBUTE_LABEL/VALUE 1..50` (Requires deep parsing and extraction)
- `Product Image`, `SDS`, `Specification Sheet` (Requires Web Scraping / PDF extraction)
