# Evaluation Strategy

## 1. Fill Rate Metrics
Measure the percentage of the 252 columns populated for the test dataset.

## 2. Accuracy Metrics
- `Taxonomy Accuracy`: Does the item map to a valid, logical Dept/Class/Fine?
- `No Hallucinations`: Verify that no attributes were invented. All output data must be traceable to the input string or a verified manufacturer URL.

## 3. Evaluation Scripts
We will build a `scripts/evaluate_results.py` tool to automatically calculate fill rates and flag potential hallucinations (e.g., values not found in input or source text).
