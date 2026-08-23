# Canonical Product State

## The Canonical Model
We use a strongly-typed Pydantic model (`CanonicalProduct`) internally to represent the enriched state. This decouples the messy 252-column output contract from our internal processing logic.

## State Transitions
1. `RawInput`: The raw 6 columns.
2. `CleanedInput`: Placeholders removed, unicode normalized.
3. `CanonicalProduct (Initial)`: Direct mappings applied (e.g., manufacturer name cleaned).
4. `CanonicalProduct (Enriched)`: Taxonomy assigned, attributes extracted, dimensions parsed.
5. `CanonicalProduct (Verified)`: Manufacturer sources scraped and cross-referenced.
6. `FinalOutput`: Serialized to the 252-column CSV.
