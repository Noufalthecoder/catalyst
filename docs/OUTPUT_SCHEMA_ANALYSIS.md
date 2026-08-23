# Output Schema Analysis

## 1. The 252-Column Target Schema
The output schema is highly denormalized, containing exactly 252 columns required for commerce-ready records.

## 2. Core Groupings
- **Identity & Taxonomy**: `PART_NUMBER`, `Dept`, `Class`, `Fine`, `SKU - MY_PART_NUMBER`, `Mfg_Part_Num`, `MANUFACTURER_NAME`, `BRAND_NAME`.
- **Descriptions**: `MOBILE_DESC`, `INVOICE_DESC`, `SHORT_DESC`, `LONG_DESC1`, `RETAIL_DESC`, `MARKETING_DESCRIPTION`.
- **Dimensions & Weights**: `LENGTH`, `HEIGHT`, `WIDTH`, `WEIGHT`, `VOLUME` (and their respective `_UOM` columns).
- **Features & Attributes**: `ITEM_FEATURES_1` through `ITEM_FEATURES_20`, `ATTRIBUTE_LABEL 1` through `ATTRIBUTE_LABEL 50` (with `_VALUE` and `_UOM`).
- **Assets & Documents**: `Product Image`, `SDS`, `Warranty Information`, `Specification Sheet`, `Video Link`, etc.

## 3. Strict Rules & Conventions
- Missing attributes must be left blank or marked as `UNKNOWN`. No hallucinations.
- `UNKNOWN` vs `CONFLICTED`: Handle edge cases explicitly.
- The 252 original column names must remain EXACTLY as they are. Do not rename them.
