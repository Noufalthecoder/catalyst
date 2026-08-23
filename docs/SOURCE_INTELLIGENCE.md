# Source Intelligence Strategy

## 1. Authoritative Sources
We prioritize manufacturer domains. For example, for a "Milwaukee" tool, we search `milwaukeetool.com`.

## 2. Verification
If a source provides an attribute (e.g., Voltage = 18V), we cross-reference it against the original `Part_Desc` or `Mfg_Part_Num` to ensure we are looking at the exact same SKU.

## 3. Handling Conflicts
If the web source says 20V but the description says 18V, we output `CONFLICTED` for that attribute, as per the non-negotiable rules.
