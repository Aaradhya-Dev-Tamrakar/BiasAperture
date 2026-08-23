# Track 11 — Bootstrap Confidence Intervals
**Stream:** C (Fairness Engine) · **Priority:** 🔴 Critical · **Owner Focus:** Tisha (WP4)
**Estimated Time:** 30 min · **Feeds:** `fairness/statistics.py`

## Instructions
1. Paste `CONTEXT.md` into Claude Desktop first
2. Then paste the prompt below
3. Save the output as `results/11_bootstrap_ci_implementation.md`

## Prompt

Research and implement bootstrap confidence intervals for fairness metrics in Python. Requirements:
1. Minimum B = 1,000 resamples (NFR-002), report 95% CI
2. The metric being bootstrapped is a disparity metric (e.g., accuracy difference between subgroups)
3. Must handle subgroup-stratified resampling: resample within each demographic subgroup, not globally
4. Must handle edge case: subgroup with n < 30 → do NOT compute CI, flag as insufficient

Research these specific questions:
- BCa (bias-corrected and accelerated) vs. percentile method — which is more appropriate for disparity metrics?
- numpy.random.Generator vs. scipy.stats.bootstrap — which API is cleaner?
- Seed management for reproducibility
- Performance: 1,000 resamples × 7 race groups × 4 metrics — is this fast enough? Vectorization strategies?

Provide a complete Python function: `bootstrap_ci(metric_fn, y_true, y_pred, group_labels, n_resamples=1000, ci=0.95) → (ci_lower, ci_upper)`
