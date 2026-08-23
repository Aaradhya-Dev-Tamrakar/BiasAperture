# Track 14 — Equalized Odds & Equal Opportunity — Theory to Code
**Stream:** C (Fairness Engine) · **Priority:** 🟡 Medium · **Owner Focus:** Tisha (WP4)
**Estimated Time:** 30 min · **Feeds:** Metric implementation, cross-validation

## Instructions
1. Paste `CONTEXT.md` into Claude Desktop first
2. Then paste the prompt below
3. Save the output as `results/14_eod_eop_implementation.md`

## Prompt

Research Equalized Odds and Equal Opportunity from the original Hardt, Price & Srebro 2016 NeurIPS paper, and implement them:

1. **Formal definitions:**
   - Equalized Odds: P(Ŷ=1|A=a, Y=y) = P(Ŷ=1|A=b, Y=y) for all y ∈ {0,1} and all groups a,b
   - Equal Opportunity: same but only for Y=1 (positive class)
2. **As "difference" metrics** (not binary pass/fail):
   - `equalized_odds_difference`: max over y ∈ {0,1} of |TPR_a - TPR_b| or |FPR_a - FPR_b|
   - `equal_opportunity_difference`: |TPR_a - TPR_b|
3. **Multi-group extension:** with 7 race groups, how to aggregate pairwise differences? Max difference? Average?
4. **Edge cases:** groups with no positive labels, groups with no negative labels, groups with n < 30
5. **Comparison:** verify that Fairlearn's and AIF360's implementations match the paper's definitions — document any discrepancies

Provide standalone Python implementations (no library dependencies except numpy) and cross-validate against Fairlearn output.
