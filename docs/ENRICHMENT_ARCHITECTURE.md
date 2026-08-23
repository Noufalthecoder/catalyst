# Enrichment Architecture

## Multi-Agent Pipeline
1. **Ingestion & Normalization**: Deterministic cleaning of the 6 input columns.
2. **Identity Resolution**: Manufacturer and Brand standardization using reference lists.
3. **Taxonomy Classification**: AI-assisted mapping of the product to the Dept/Class/Fine hierarchy.
4. **Attribute Extraction (Local)**: Regex/NLP extraction of dimensions and UOMs from `Part_Desc`.
5. **Source Intelligence**: Web scrapers finding official manufacturer URLs and extracting SDS/Specs.
6. **Description Generation**: Templated construction of SHORT_DESC, LONG_DESC based on extracted attributes.
