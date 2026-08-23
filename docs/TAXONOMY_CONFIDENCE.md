# Taxonomy Confidence Scoring Formula

The confidence score of a taxonomy classification is calculated deterministically based on the sum of individual evidence signals:

1. **Product Type Detection Match (+0.4)**
   - If the detected `product_type` corresponds directly to a taxonomy node (e.g. `Dishwasher` -> `Built-In Dishwashers`).

2. **Description Keyword Match (+0.3)**
   - If key tokens from the product description uniquely identify category patterns (e.g. `Attic Access Door` -> `Attic Access Doors`).

3. **Brand-Category Match (+0.2)**
   - If the resolved brand is known to manufacture items in this taxonomy branch (e.g. `TREX` in `Decking & Railing`).

4. **Manufacturer-Category Match (+0.1)**
   - If the resolved manufacturer is known to supply items in this taxonomy branch (e.g. `TimberTech` in `Decking & Railing`).

### Status Mapping
- **VERIFIED**: Score = 1.0 (Stage 1 Exact match with reference taxonomy master)
- **PROBABLE / INFERRED**: Score >= 0.7 (Fuzzy or rule-based Stage 1/Stage 2 match in Mode B)
- **AMBIGUOUS**: 0.0 < Score < 0.7 (Conflicting keyword signals or missing parent categories)
- **UNKNOWN**: Score = 0.0 (No signal matches)
