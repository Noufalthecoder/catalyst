# Implementation Roadmap

1. **Phase 1: Data Foundation (COMPLETED)**
   - Initialized repositories, Pydantic models, text normalizers.
   - Analyzed the real 1000-item dataset and 252-column schema.

2. **Phase 2: Canonical Identity & Extraction (NEXT)**
   - Build `ManufacturerNormalizer` to handle `Part_Manuf` parsing.
   - Build `DescriptionParser` (Regex/NLP) for dimensions and UOMs.
   - Map to `CanonicalProduct`.

3. **Phase 3: Taxonomy AI**
   - Integrate an LLM router to assign `Dept/Class/Fine`.

4. **Phase 4: Web Intelligence**
   - Implement web search agent to find official `MFR URL`.
   - Extract `ITEM_FEATURES`.

5. **Phase 5: Output Generation**
   - Map `CanonicalProduct` back to the exact 252-column CSV.
   - Final validation against the `No Hallucination` rules.
