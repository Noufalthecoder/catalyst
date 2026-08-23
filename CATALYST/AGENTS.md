# CATALYST — Engineering Constitution

## Project

CATALYST is an AI-powered Product Intelligence and Catalog
Enrichment Engine for the UniHack 2026 challenge by Unilog.

The system transforms incomplete and inconsistent industrial
product information into standardized, validated and
commerce-ready product records.

## Core Principle

AI for understanding.
Rules for correctness.
Evidence for trust.

## Non-Negotiable Rules

1. The system must work on unseen evaluation data.
2. Never hardcode answers for sample products.
3. Never create fake enrichment results.
4. Never use mock data in the final product.
5. Never fabricate product attributes.
6. Missing information must remain UNKNOWN rather than being hallucinated.
7. Conflicting information must be marked CONFLICTED.
8. Prefer authoritative manufacturer sources.
9. Manufacturer and brand names must be validated against the approved master data.
10. Attribute values must be validated against the approved LOV where applicable.
11. UOM values must follow the provided Unilog UOM standards.
12. Fraction/decimal conversions must follow the provided reference table.
13. LLMs must return structured data whenever possible.
14. LLMs must never control the final output schema.
15. Deterministic code must handle exact formatting and validation.
16. The final output must contain exactly the required 252 columns.
17. Never rename, remove, reorder or invent expected output columns.
18. Every new module must have automated tests.
19. Existing functionality must not be broken when adding new functionality.
20. Run tests after every significant implementation change.
21. Never claim metrics that were not actually measured.
22. Keep source evidence internally for generated attributes.
23. Track confidence for important AI-generated decisions.
24. Optimize for correctness before visual polish.
25. Optimize for the actual UniHack evaluation workflow.

## Architecture Philosophy

The pipeline should follow:

RAW INPUT
→ INGESTION
→ PRODUCT IDENTITY
→ TAXONOMY
→ SOURCE INTELLIGENCE
→ ATTRIBUTE EXTRACTION
→ NORMALIZATION
→ CONTENT GENERATION
→ VALIDATION
→ 252-COLUMN OUTPUT

## AI Usage

Use AI for:

- Semantic product understanding
- Classification
- Entity resolution when deterministic matching is insufficient
- Information extraction
- Evidence interpretation
- Description generation

Do NOT use AI for:

- Exact output schema generation
- Header naming
- UOM formatting
- Fraction conversion
- Character counting
- Required-field validation
- CSV/XLSX structure
- Deterministic business rules

## Quality States

Use these states where applicable:

VERIFIED
INFERRED
UNKNOWN
CONFLICTED

## Development Style

Build modularly.

Prefer small, testable services over one giant pipeline.

Before modifying existing code:

1. Inspect it.
2. Understand dependencies.
3. Make the smallest appropriate change.
4. Run relevant tests.
5. Verify the application still works.

Never silently swallow errors.
