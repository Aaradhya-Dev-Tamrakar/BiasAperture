# 11 - Requirements Traceability

**Status:** Initial traceability baseline; update as evidence lands

| Requirement / invariant | Specification | Implementation anchor | Evidence | Status |
| --- | --- | --- | --- | --- |
| FairFace-aligned demographic schema | [02](02-data-model.md) | `src/bias_aperture/schema.py` | Schema tests | Implemented / Tested |
| Core Four disparity metrics | [05](05-audit-engine.md) | `src/bias_aperture/fairness/` | Known-answer tests | Implemented / Tested |
| `n >= 30` reportability guard | [02](02-data-model.md), [06](06-statistics-and-confidence.md) | `MetricResult.__post_init__` | Schema tests | Implemented / Tested |
| Chi-squared significance at alpha 0.05 | [06](06-statistics-and-confidence.md) | Fairness statistics layer | Report inspection | Needs confirmation |
| At least 1,000 bootstrap resamples | [06](06-statistics-and-confidence.md) | Fairness statistics layer | Statistical tests and run metadata | Needs confirmation |
| Predictions-file audit workflow | [03](03-orchestrator.md), [04](04-intake-and-classification.md) | `cli.py`, interfaces, ingestion | End-to-end CLI run | Implemented / Tested |
| Standalone HTML report | [08](08-report-and-compliance.md) | `src/bias_aperture/report/` | Offline report contract tests | Implemented / Tested |
| Targeted explainability | [07](07-explainability.md) | `src/bias_aperture/explainability.py` | Explainability tests/artifacts | Partially implemented |
| Diagnostic-only scope | [00](00-overview-and-mvp-scope.md), [10](10-security-and-governance.md) | Project-wide constraint | Review and report text | Implemented |
| Empirical case-study claims | [09](09-verification.md) | `data/processed/`, `report/` | Claim ledger and generated report | Needs confirmation |

## Source requirements

The FR/NFR identifiers originate in the proposal and planning records, especially [BiasAperture-AT](../docs/BiasAperture-AT.md), [schema-lock-m1.md](../docs/schema-lock-m1.md), and `report/src/chapters/requirements.tex`. This table is a navigation layer; those source records remain authoritative where a conflict exists.

When implementation and research prose disagree, record the discrepancy, prefer the locked schema and executable tests for current behavior, and label unresolved decisions rather than silently choosing a value.
