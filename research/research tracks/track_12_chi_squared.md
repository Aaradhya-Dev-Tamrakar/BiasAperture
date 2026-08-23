# Track 12 — Chi-Squared Significance Testing
**Stream:** C (Fairness Engine) · **Priority:** 🔴 Critical · **Owner Focus:** Tisha (WP4)
**Estimated Time:** 30 min · **Feeds:** `fairness/statistics.py`

## Instructions
1. Paste `CONTEXT.md` into Claude Desktop first
2. Then paste the prompt below
3. Save the output as `results/12_chi_squared_testing.md`

## Prompt

Research chi-squared significance testing applied to fairness metric disparities. Requirements:
1. α = 0.05 significance threshold (NFR-001), report exact p-values
2. The test determines whether observed accuracy differences across demographic subgroups are statistically significant

Research these specific questions:
- `scipy.stats.chi2_contingency` vs. `scipy.stats.chisquare` — which is correct for a confusion-matrix-based fairness test?
- How to construct the contingency table from (true_label, predicted_label, subgroup) data
- Correction: Yates' correction — should it be applied? When?
- What happens when expected cell counts are < 5? Fisher's exact test as fallback?
- Multiple testing correction: with 7 race groups × 4 metrics = 28 tests, should Bonferroni or Holm-Bonferroni be applied?
- Relationship between chi-squared p-value and the bootstrap CI — are they redundant or complementary?

Provide a complete Python function: `chi_squared_test(y_true, y_pred, group_labels, alpha=0.05) → (chi2_stat, p_value, significant: bool)`
