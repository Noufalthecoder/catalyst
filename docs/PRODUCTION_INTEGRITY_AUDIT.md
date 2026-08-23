# Production Integrity Audit Report

Integrity analysis for the 1,000-product production run.

## Final Status
**PIPELINE_VALIDATED_BUT_DATA_REQUIRES_AUDIT**

## 1. Review Queue Tallies
All 1,000 products are marked NEEDS_REVIEW. Below is the breakdown of the exact conditions that caused products to enter the review queue:

| Category | Count | Percentage | Avg Quality | Min Quality | Max Quality |
|---|---|---|---|---|---|
| IDENTITY | 30 | 3.0% | 0.12 | 0.1 | 0.18 |
| TAXONOMY | 408 | 40.8% | 0.68 | 0.1 | 0.88 |
| SOURCE | 0 | 0.0% | 0.0 | 0.0 | 0.0 |
| ATTRIBUTE | 529 | 52.9% | 0.82 | 0.14 | 0.92 |
| QUALITY | 247 | 24.7% | 0.11 | 0.1 | 0.18 |
| DUPLICATE | 0 | 0.0% | 0.0 | 0.0 | 0.0 |
| CONTENT | 0 | 0.0% | 0.0 | 0.0 | 0.0 |
| OTHER | 0 | 0.0% | 0.0 | 0.0 | 0.0 |

## 2. Review Threshold Audit
The ReviewQueue flags products under the following conditions:
- **Identity status**: Ambiguous or Unknown (confidence < 0.50)
- **Taxonomy status**: Unknown (confidence < 0.50)
- **Attribute conflict**: Presence of conflicting specs from multiple sources
- **Invalid Attribute Format**: Any single attribute marked as `INVALID`
- **Low Quality**: Composite score < 0.40

### Selective Review decision Matrix Proposal
To make the review queue selective without compromising accuracy:
1. **Pass Gates**: If Identity is verified, Taxonomy confidence >= 0.80, conflicts count is 0, and invalid formats count is 0, automatically approve.
2. **Review Gates**: Flag only if conflicts exist, validation fails, or quality falls below 0.50.

## 3. Product-Level Source Ingestion
- **At least one source**: 753
- **Official manufacturer source**: 753
- **Exact MPN matches**: 747
- **Only secondary source**: 0
- **No source**: 247

## 4. Attribute Coverage
- **Total Expected Attributes**: 5000
- **Verified**: 481
- **Probable**: 0
- **Invalid**: 565
- **Unknown**: 3954
- **Not Applicable**: 0
- **Conflicted**: 0

## 5. Quality Score distribution
- **Mean**: 0.65
- **Median**: 0.84
- **Min**: 0.1
- **Max**: 0.92

| Band | Count |
|---|---|
| 0.00-0.19 | 247 |
| 0.20-0.39 | 0 |
| 0.40-0.59 | 45 |
| 0.60-0.79 | 0 |
| 0.80-1.00 | 708 |

## 6. Sample Audit (20 Representative Products)
| Group | MPN | Brand | Manufacturer | Product Type | Verified | Invalid | Quality | Review Reasons |
|---|---|---|---|---|---|---|---|---|
| HIGH | DCB518ASTS06G | Diablo | Freud Inc | Sanding Product | 1 | 2 | 0.92 | INVALID_ATTRIBUTE_FORMAT |
| HIGH | 3MABR-7100075678 | 3M | Jam Industrial Supply LLC | UNKNOWN | 1 | 1 | 0.88 | INVALID_ATTRIBUTE_FORMAT |
| HIGH | 3MABR-7100045865 | 3M | Jam Industrial Supply LLC | UNKNOWN | 1 | 1 | 0.88 | INVALID_ATTRIBUTE_FORMAT |
| HIGH | 3MABR-7100048736 | 3M | Jam Industrial Supply LLC | UNKNOWN | 1 | 1 | 0.88 | INVALID_ATTRIBUTE_FORMAT |
| HIGH | 3MABR-7100075690 | 3M | Jam Industrial Supply LLC | UNKNOWN | 1 | 1 | 0.88 | INVALID_ATTRIBUTE_FORMAT |
| MEDIUM | 73272TBK | DSI Westbury | Palmer Donavin Mfg Company | Post Accessory | 1 | 1 | 0.48 | INVALID_ATTRIBUTE_FORMAT |
| MEDIUM | 27233 | AJM | A J Manufacturing Inc | Door / Window / Skylight | 0 | 1 | 0.44 | INVALID_ATTRIBUTE_FORMAT |
| MEDIUM | 1517602 | United Window & Door | United Window & Door Manufacturing | Door / Window / Skylight | 0 | 1 | 0.44 | INVALID_ATTRIBUTE_FORMAT |
| MEDIUM | 1517603 | United Window & Door | United Window & Door Manufacturing | Door / Window / Skylight | 0 | 1 | 0.44 | INVALID_ATTRIBUTE_FORMAT |
| MEDIUM | 1517604 | United Window & Door | United Window & Door Manufacturing | Door / Window / Skylight | 1 | 1 | 0.48 | INVALID_ATTRIBUTE_FORMAT |
| LOW | 5B-332-080 | None | Mirka Abrasives Inc | UNKNOWN | 0 | 0 | 0.1 | LOW_QUALITY |
| LOW | 5B-332-120 | None | Mirka Abrasives Inc | UNKNOWN | 0 | 0 | 0.1 | LOW_QUALITY |
| LOW | 9A-570-240 | None | Mirka Abrasives Inc | Sanding Product | 0 | 1 | 0.14 | INVALID_ATTRIBUTE_FORMAT, LOW_QUALITY |
| LOW | 9A-570-320 | None | Mirka Abrasives Inc | Sanding Product | 0 | 1 | 0.14 | INVALID_ATTRIBUTE_FORMAT, LOW_QUALITY |
| LOW | ASH-40-40-04 | None | Emseal Joint Systems Ltd | UNKNOWN | 0 | 0 | 0.1 | LOW_QUALITY |
| FLAGGED | DCB518ASTS06G | Diablo | Freud Inc | Sanding Product | 1 | 2 | 0.92 | INVALID_ATTRIBUTE_FORMAT |
| FLAGGED | 3MABR-7100075678 | 3M | Jam Industrial Supply LLC | UNKNOWN | 1 | 1 | 0.88 | INVALID_ATTRIBUTE_FORMAT |
| FLAGGED | 3MABR-7100045865 | 3M | Jam Industrial Supply LLC | UNKNOWN | 1 | 1 | 0.88 | INVALID_ATTRIBUTE_FORMAT |
| FLAGGED | 3MABR-7100048736 | 3M | Jam Industrial Supply LLC | UNKNOWN | 1 | 1 | 0.88 | INVALID_ATTRIBUTE_FORMAT |
| FLAGGED | 3MABR-7100075690 | 3M | Jam Industrial Supply LLC | UNKNOWN | 1 | 1 | 0.88 | INVALID_ATTRIBUTE_FORMAT |

## 7. Web Enrichment & Pipeline Performance
- **HTTP Requests**: 2,000
- **Unique URLs Fetched**: 2259
- **Cache Hits**: 2,000 (100.0% hit rate)
- **Cache Misses**: 0
- **Processing Duration**: 13.21s (average 0.013s per product)

*Note: All web fetching and document extraction phases were skipped and retrieved directly from pre-seeded caching mocks.*
