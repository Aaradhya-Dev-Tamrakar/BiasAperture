# 07 - Explainability

**Status:** Current surrogate attribution implemented; richer image-native analysis deferred

Explainability is a targeted diagnostic step after metric computation. It should run only when a disparity is statistically flagged and the relevant subgroup has sufficient support. It must explain an observed model behavior, not claim that an attribution proves causation.

The current repository fits a logistic surrogate to encoded binary predictions
using demographic dummy features. It shares the fairness engine's positive-class
encoding and reports mean absolute additive contributions to surrogate log-odds
across the full audit. These are demographic associations, not causal drivers or
an explanation of the disparity statistic. No attribution is generated without
records; missing variance and execution failures return explicit unavailable
statuses. A missing p-value does not qualify as statistical significance.

Spatial SHAP, face parsing, ITA colorimetry, proxy-feature analysis, and GPU gradient explainers described in research documents are deferred unless their dependencies, inputs, limitations, and tests are added. They must not be presented as current MVP behavior.

The CLI enables this step by default and accepts `--no-explain` to prevent
invocation. Attribution values and unavailable statuses are retained in the
standalone report through `ReportContext`, without changing `MetricResult`.
`AuditResult.explained_count` counts results with actual attribution values.
