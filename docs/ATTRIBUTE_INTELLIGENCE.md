# Attribute Intelligence Strategy

## 1. The 50 Attribute Pairs
The output schema allows up to 50 generic `ATTRIBUTE_LABEL`, `ATTRIBUTE_VALUE`, `ATTRIBUTE_UOM` triplets.

## 2. Extraction Pipeline
1. **Identify**: What attributes matter for this `Class`? (e.g., Voltage for Drills, Grit for Sandpaper).
2. **Extract (Local)**: Can we find it in the `Part_Desc`?
3. **Extract (Web)**: Can we find it on the manufacturer's spec sheet?
4. **Standardize**: Ensure the label is consistent (e.g., "Drive Size") and the UOM is standard.
