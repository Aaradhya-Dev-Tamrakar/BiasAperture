# 05 - Audit Engine

**Status:** Core metrics implemented and tested

## Core Four

For binary task labels across protected groups (general multiclass One-vs-Rest
auditing is deferred and inputs with more than two task labels are rejected):

- **Demographic parity difference:** spread of positive prediction rates.
- **Equalized odds difference:** worst-case spread across TPR and FPR.
- **Equal opportunity difference:** spread of TPR values.
- **Disparate impact ratio:** minimum positive prediction rate divided by the maximum.

Fair values are zero for difference metrics and one for the ratio metric.

## Backend harmonization and failure isolation

Fairlearn `MetricFrame` and AIF360 `ClassificationMetric` supply independent
selection-rate, TPR and FPR primitives. Shared row assembly uses worst-case
TPR/FPR spread for equalized odds and unsigned spread for equal opportunity.
Both libraries' native max-gap EOD agree on the known-answer fixture; AIF360's
signed average odds and average absolute odds are separate metrics. A
cross-validation layer flags differences beyond configured thresholds
($|\Delta| > 0.05$ for difference metrics, $|\Delta| > 0.10$ for ratios).
Bootstrap, hypothesis tests and reporting are shared; library agreement does
not independently validate those components.

Install the `fairness` extra for runtime backends. Fairlearn never substitutes
local formulas when its imports fail. A canonical-backend failure aborts the
audit with a clear error and no newly generated report. Secondary failures remain
isolated and produce missing-value divergence alerts when the canonical backend
has computed values; reports label cross-library validation incomplete even
when there are no eligible values to compare. Task-label validation happens
before backend failure isolation and cannot become an empty success report.

The shared encoder uses the sorted second task label as positive (1 for 0/1,
Male for Female/Male), considering truth and predictions together. A sole
1/True label is positive; other sole labels are negative. Explanations use the
same encoder. This policy preserves the historical default without changing
the locked schema.

## Edge cases

If every group has zero positive predictions, DIR is one while the report should warn that absolute selection is absent. If at least one group has positive predictions and another has none, DIR is zero. Undefined rate calculations must be represented as insufficient or invalid evidence, not as fabricated zeros.

See the [low-level mathematical specification](../docs/research/LOW_LEVEL_SPECIFICATION.md) for formulas and the source under [`src/bias_aperture/fairness/`](../src/bias_aperture/fairness/) for executable behavior.
