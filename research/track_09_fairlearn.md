# Track 09 — Fairlearn API — MetricFrame & Core Four
**Stream:** C (Fairness Engine) · **Priority:** 🔴 Critical · **Owner Focus:** Tisha (WP4)
**Estimated Time:** 45 min · **Feeds:** `fairness/fairlearn_backend.py`

## Instructions
1. Paste `CONTEXT.md` into Claude Desktop first
2. Then paste the prompt below
3. Save the output as `results/09_fairlearn_implementation.md`

## Prompt

Research the Fairlearn Python library (current stable version) for implementing these 4 fairness metrics:
1. `demographic_parity_difference` — via MetricFrame
2. `equalized_odds_difference` — via MetricFrame
3. `equal_opportunity_difference` — via MetricFrame
4. `disparate_impact_ratio` — via MetricFrame or manual computation

For each metric, provide:
- Exact Fairlearn API call with imports
- Input format: what arrays/DataFrames does Fairlearn expect?
- How to handle multiple protected attributes (race × gender intersections)
- How to convert a list of SubjectRecord(image_id, race, gender, age, true_label, predicted_label) into Fairlearn's expected input
- Edge cases: what happens with empty subgroups, single-class subgroups, n=1?

Also research: does Fairlearn compute bootstrap CIs or p-values natively, or must we add those ourselves?

Provide a complete, runnable Python code example computing all 4 metrics from a list of (true_label, predicted_label, race, gender) tuples.
