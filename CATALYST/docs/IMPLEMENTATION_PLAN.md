# IMPLEMENTATION PLAN

## Overview
This phased implementation plan is optimized for the hackathon deadline, focusing on establishing a reliable and accurate data pipeline before adding UI or polish. It sequences tasks logically from data ingestion and foundational models to output generation and validation.

## Phase 1: Data Foundation (Priority 1-2)
- **1.1 Working Data Pipeline**: Set up ingestion scripts to parse `Sample-1000_Items.xlsx` and `Unilog-Sample_200_Items-Input-vs-Output.xlsx`. Cleanse placeholder values (e.g. `-- Unbranded --`). Set up the exact 252-column export scaffolding.
- **1.2 Canonical Product Object**: Define a Python dataclass or Pydantic model representing the internal state (Identity, Taxonomy, Attributes, Source Evidence, Confidence States). This object will serve as the contract between all pipeline stages.

## Phase 2: Core Intelligence (Priority 3-4)
- **2.1 Identity Resolution Engine**: Implement deterministic matching of manufacturer and brand names against `UniCat_Manufacturer_and_Brand_List.xlsx`. Include fallback logic for fuzzy matching.
- **2.2 Taxonomy Classification**: Implement classification logic using LLM prompts to assign the correct Classpath based on descriptions and categories, guided by the LOV constraints.

## Phase 3: Enrichment & Normalization (Priority 5-7)
- **3.1 Source Enrichment**: Implement basic web fetching/scraping strictly targeting manufacturer URLs to gather manuals, specifications, and images.
- **3.2 Attribute Extraction**: Use LLM information extraction to pull raw attributes (size, material, features) from descriptions and source text.
- **3.3 LOV & UOM Normalization**: Build a deterministic validation layer.
  - Map extracted attributes to `Unicat_Lov_v1_0_Updated_With_Remarks.xlsx`.
  - Implement regex-based UOM standardizer using `Unilog_Master_UOM_Standards.xlsx` and the decimal/fraction mapping.

## Phase 4: Generation & Validation (Priority 8-11)
- **4.1 Content Generation**: Write specific LLM prompts for generating Product Title, Invoice Desc, Mobile Desc, and Long Desc, adhering strictly to formulas and character limits from the `CONTENT_GUIDELINES`.
- **4.2 Trust & Validation Framework**: Implement scripts to enforce character limits, LOV adherence, and field presence.
- **4.3 252-Column Export**: Map the finalized Canonical Product Object to the expected delivery format.
- **4.4 Evaluation Framework**: Build a scoring script comparing generated output against the 200-item ground truth, tracking metrics for Identity accuracy, UOM compliance, schema adherence, etc.

## Phase 5: Presentation & Polish (Priority 12-14)
- **5.1 Simple API Integration**: Wrap the pipeline in a lightweight FastAPI/Flask application.
- **5.2 Frontend Demo**: Build a minimal frontend to input raw descriptions and visualize the enrichment process, highlighting quality states (VERIFIED, INFERRED).
- **5.3 Demo Polish**: Finalize presentation materials focusing on the accuracy metrics and system architecture.

## Summary

1. **What the actual problem is**: Distributor product data is messy, incomplete, and non-standard. It needs to be enriched and formatted into a strict 252-column master schema to be useful for commerce.
2. **What CATALYST will build**: An automated pipeline that uses AI for understanding (extraction/generation) and deterministic logic for correctness (LOV/UOM validation) to process raw rows into compliant product records.
3. **What the hardest technical challenges are**: Reconciling unstructured/noisy descriptions into exact LOV constraint values, resolving entity identities cleanly, and ensuring LLM outputs adhere strictly to formatting rules without hallucinating.
4. **What should be deterministic**: Schema building, 252-column mapping, UOM standard formatting, fraction conversions, LOV matching, and character count validation.
5. **What should use AI**: Semantic product understanding, extracting raw attributes from text, categorizing products, and generating natural language descriptions.
6. **What should use external sources**: Manufacturer specifications, data sheets, and images.
7. **What should be built first**: The raw ingestion pipeline, Canonical Product Object, and the deterministic export scaffolding, followed by Identity Resolution.
