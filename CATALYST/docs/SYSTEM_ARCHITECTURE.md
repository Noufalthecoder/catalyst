# SYSTEM ARCHITECTURE

## 1. Overview
CATALYST is a Product Intelligence and Catalog Enrichment Engine. The system's primary architecture is a modular, pipeline-based data processor that transforms raw inputs into a complete 252-column output following strict schema, UOM, and List of Values (LOV) constraints.

## 2. Pipeline Stages

### 2.1 Ingestion
- **Input**: Raw 1,000-row sample data (e.g. `Sample-1000_Items.xlsx`)
- **Technology**: Pandas/OpenPyXL
- **Logic**: Read data, strip out known placeholder values (e.g., "-- Unbranded --", "-- No Unilog Brand --"), format cleanup.

### 2.2 Identity Resolution
- **Input**: Cleaned Raw Data
- **Technology**: Deterministic matching (FuzzyWuzzy / regex), fallback to LLM
- **Logic**: Map `Part_Manuf`, `E1_Brand`, etc. against the `UniCat_Manufacturer_and_Brand_List.xlsx`. Ensure exact casing and symbols (e.g., ®, ™).

### 2.3 Taxonomy Classification
- **Input**: Resolved Product Identity & Description
- **Technology**: LLM Classification / Embedding Search
- **Logic**: Assign proper Classpath and UNSPSC category using the LOV structure.

### 2.4 Source Intelligence
- **Input**: Resolved Product Identity
- **Technology**: Web scrapers/API (Manufacturer sites only)
- **Logic**: Gather technical specs and URLs. (Distributor/marketplace sites are explicitly excluded).

### 2.5 Attribute Extraction
- **Input**: Source Intelligence Data & Raw Descriptions
- **Technology**: LLM Semantic Extraction
- **Logic**: Extract raw attributes (e.g., Wash Cycles, Amperage, Dimensions) based on the target category in LOV.

### 2.6 LOV Normalization
- **Input**: Raw Extracted Attributes
- **Technology**: Deterministic Mapping / Fuzzy Matching against `Unicat_Lov_v1_0_Updated_With_Remarks.xlsx`
- **Logic**: Map extracted attributes to the canonical values allowed for that specific Classpath.

### 2.7 UOM Normalization
- **Input**: Normalized Attributes containing units
- **Technology**: Deterministic regex matching and dictionary lookup against `Unilog_Master_UOM_Standards.xlsx` and `Decimal_Fraction.xlsx`
- **Logic**: Convert standard measurements, ensuring space between value and unit (e.g., "50-1/4 in" instead of "50.25in").

### 2.8 Content Generation
- **Input**: Normalized Attributes, Identity, Taxonomy
- **Technology**: LLM with strict prompting templates
- **Logic**: Generate required descriptions (Product Title, Short Desc, Long Desc, Invoice Desc, Mobile Desc) strictly adhering to character limits and formulaic rules in `UNILOG_INTERNAL_CONTENT_GUIDELINES.docx`.

### 2.9 Trust & Validation
- **Input**: Generated Content and Output Objects
- **Technology**: Deterministic Rule Engine
- **Logic**: Validate character limits, schema adherence, and LOV matching. Assign quality states: VERIFIED, INFERRED, UNKNOWN, CONFLICTED.

### 2.10 252-Column Mapping & Export
- **Input**: Validated Product Object
- **Technology**: Pandas/OpenPyXL
- **Logic**: Transform the Canonical Product Object into the exact 252-column structure and export to Excel without modifying column order or headers.

## 3. Technology Stack
- **Language**: Python
- **LLM**: Gemini / OpenAI (for semantic extraction, classification, description generation)
- **Data Processing**: Pandas, OpenPyXL
- **Evaluation Framework**: Custom Python validation scripts comparing Output to `Unilog-Sample_200_Items-Input-vs-Output.xlsx`
