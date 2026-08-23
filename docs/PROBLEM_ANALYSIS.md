# Problem Analysis

## 1. The Core Data Engineering Challenge
The data provided by distributors is messy, incomplete, and highly fragmented. A single string (`Part_Desc`) often holds the keys to 10+ distinct output columns.

## 2. Why Pure LLM Approaches Fail
- **Hallucinations**: LLMs invent specs that sound plausible but are wrong.
- **Latency & Cost**: Running 1000 items through complex LLM prompts for 252 columns is slow and expensive.
- **Inconsistency**: LLMs might return "Inches" one time and "in." another.
- **Taxonomy**: LLMs struggle to place items into a strict, predefined 3-level hierarchy without deterministic guidance.

## 3. The CATALYST Solution
- **Deterministic Foundation**: Use Python rules, regex, and dictionaries for cleaning, standardizing, and extracting known entities (e.g., stripping placeholders, resolving standard fractions).
- **Targeted AI**: Use AI *only* for semantic understanding (e.g., matching a weirdly phrased category to the taxonomy) and web scraping intelligence (extracting specs from a manufacturer's PDF).
