# Track 10 — AIF360 API — BinaryLabelDataset & Cross-Validation
**Stream:** C (Fairness Engine) · **Priority:** 🔴 Critical · **Owner Focus:** Tisha (WP4)
**Estimated Time:** 45 min · **Feeds:** `fairness/aif360_backend.py`

## Instructions
1. Paste `CONTEXT.md` into Claude Desktop first
2. Then paste the prompt below
3. Save the output as `results/10_aif360_implementation.md`

## Prompt

Research IBM's AI Fairness 360 (AIF360) Python library for implementing these 4 fairness metrics:
1. `demographic_parity_difference` — which AIF360 class/method computes this?
2. `equalized_odds_difference` — which AIF360 class/method?
3. `equal_opportunity_difference` — which AIF360 class/method?
4. `disparate_impact_ratio` — which AIF360 class/method?

For each metric, provide:
- Exact AIF360 API call with imports (BinaryLabelDataset, ClassificationMetric, etc.)
- How to construct BinaryLabelDataset from a pandas DataFrame with multiple protected attributes
- How AIF360 handles multi-valued protected attributes (7 race groups, not just binary)
- Known differences from Fairlearn's computation of the same metric

Critical question: AIF360 was designed for binary protected attributes — how does it handle FairFace's 7-race taxonomy? Document any one-vs-rest encoding needed.

Provide a complete, runnable Python code example.
