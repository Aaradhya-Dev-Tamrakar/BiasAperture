# 07 - Explainability

**Status:** Current surrogate attribution implemented; richer image-native analysis deferred

Explainability is a targeted diagnostic step after metric computation. It should run only when a disparity is statistically flagged and the relevant subgroup has sufficient support. It must explain an observed model behavior, not claim that an attribution proves causation.

The current repository uses demographic-dummy surrogate attribution. This is suitable for the present audit evidence but is not equivalent to spatial attribution over facial pixels.

Spatial SHAP, face parsing, ITA colorimetry, proxy-feature analysis, and GPU gradient explainers described in research documents are deferred unless their dependencies, inputs, limitations, and tests are added. They must not be presented as current MVP behavior.

Explainability artifacts should be embedded or referenced by the standalone report without changing the locked `MetricResult` contract.
