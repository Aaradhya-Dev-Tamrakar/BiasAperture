# 06 - Statistics and Confidence

**Status:** Implemented in the fairness/statistics layer; end-to-end report inspection remains verification work

Every reported disparity must carry sample size, a p-value or an explicit insufficient-sample flag, and a 95% confidence interval when the metric is defined.

## Significance

Use a chi-squared independence test with `ALPHA = 0.05`. The report must preserve the exact p-value rather than reducing it to a pass/fail label. Multiple-testing behavior must match the current implementation and be documented with the generated evidence.

## Bootstrap

Confidence intervals use at least `MIN_BOOTSTRAP_RESAMPLES = 1000` resamples. Resampling is stratified within eligible demographic groups so observed subgroup allocation is preserved. A seeded NumPy generator is required when reproducibility is claimed.

The implementation may use BCa intervals with a percentile fallback for degenerate acceleration terms. Invalid metric-specific replicates must be excluded or cause an insufficient result according to the executable statistical contract.

## Sample guard

Any subgroup with `n < 30` is not reportable as a computed metric. Its `MetricResult` must set `insufficient_sample=True` and leave computed values unset. This is an integrity rule, not a presentation preference.

See [schema-lock-m1.md](../docs/schema-lock-m1.md), [LOW_LEVEL_SPECIFICATION.md](../docs/research/LOW_LEVEL_SPECIFICATION.md), and [verification](09-verification.md).
