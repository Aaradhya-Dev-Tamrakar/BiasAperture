# 11 - Requirements Traceability

**Status:** Updated baseline synchronized with `report/src/chapters/requirements.tex` (FR-001–FR-011, NFR-001–NFR-010; FairFace benchmark exclusively; UTKFace legacy scope eliminated).

---

## 1. Functional Requirements Matrix (FR-001 to FR-011)

| Requirement ID & Title | Specification | Implementation Anchor | Evidence & Test Anchor | Status |
| --- | --- | --- | --- | --- |
| **FR-001: Data Ingestion & Alignment** | [02](02-data-model.md), [04](04-intake-and-classification.md) | `src/bias_aperture/data_ingestion.py`, `schema.py` | `tests/test_data_ingestion.py`, `tests/test_schema.py` | Implemented / Tested |
| **FR-002: Dual-Mode Model Interface** | [03](03-orchestrator.md), [04](04-intake-and-classification.md) | `src/bias_aperture/model_interface.py` | `tests/test_model_interface.py` | Implemented / Tested |
| **FR-003: Core Four Metric Computation** | [05](05-audit-engine.md) | `src/bias_aperture/fairness/backends.py`, `engine.py` | `tests/test_fairness_backends.py`, `tests/test_fairness_engine.py` | Implemented / Tested |
| **FR-004: Statistical Significance Testing** | [06](06-statistics-and-confidence.md) | `src/bias_aperture/fairness/statistics.py` | `tests/test_statistics.py` | Implemented / Tested |
| **FR-005: Surrogate Explainability** | [07](07-explainability.md) | `src/bias_aperture/explainability.py` | `tests/test_explainability.py` | Implemented / Tested |
| **FR-006: Standardized Report Generation** | [08](08-report-and-compliance.md) | `src/bias_aperture/report/generator.py` | `tests/test_report_generator.py` | Implemented / Tested |
| **FR-007: Regulatory Traceability Crosswalk** | [08](08-report-and-compliance.md) | `src/bias_aperture/report/generator.py` | Report inspection & regulatory mapping tests | Implemented / Tested |
| **FR-008: CLI Orchestration & Configuration** | [03](03-orchestrator.md) | `src/bias_aperture/cli.py` | `tests/test_cli.py`, end-to-end CLI runs | Implemented / Tested |
| **FR-009: Licensing Acknowledgement** | [10](10-security-and-governance.md) | `src/bias_aperture/cli.py` | `tests/test_cli.py` (interactive & bypass flag) | Implemented / Tested |
| **FR-010: Intersectional & Multiclass Decomposition** | [04](04-intake-and-classification.md), [05](05-audit-engine.md) | `src/bias_aperture/fairness/` (`OvRTransformer`) | `tests/test_fairness_engine.py`, `tests/test_data_ingestion.py` | Implemented / Tested |
| **FR-011: Audit Provenance & Run Manifest** | [03](03-orchestrator.md), [08](08-report-and-compliance.md), [10](10-security-and-governance.md) | `src/bias_aperture/report/generator.py`, `cli.py` | Run metadata validation in HTML reports & tests | Implemented / Tested |

---

## 2. Non-Functional Requirements Matrix (NFR-001 to NFR-010)

| Requirement ID & Title | Specification | Implementation Anchor | Evidence & Test Anchor | Status |
| --- | --- | --- | --- | --- |
| **NFR-001: Statistical Rigour ($\alpha = 0.05$)** | [06](06-statistics-and-confidence.md) | `src/bias_aperture/fairness/statistics.py`, `schema.py` | Exact $p$-value assertions in `tests/test_statistics.py` | Implemented / Tested |
| **NFR-002: Uncertainty Quantification ($B \ge 1{,}000$)** | [06](06-statistics-and-confidence.md) | `src/bias_aperture/fairness/statistics.py` | Bootstrap percentile CI tests & metadata verification | Implemented / Tested |
| **NFR-003: Sample Size Guard ($n < 30$)** | [02](02-data-model.md), [06](06-statistics-and-confidence.md) | `src/bias_aperture/schema.py` (`MetricResult.__post_init__`) | Boundary schema tests (`insufficient_sample=True`) | Implemented / Tested |
| **NFR-004: Audit Execution Performance** | [00](00-overview-and-mvp-scope.md), [09](09-verification.md) | Orchestrator & batch pipeline | Runtime profiling on dev subset & validation split | Implemented / Tested |
| **NFR-005: Architectural Modularity** | [01](01-architecture.md) | Decoupled module boundaries (`ModelInterface`, `FairnessBackend`) | Test suite modularity & Ruff boundary checks | Implemented / Tested |
| **NFR-006: Reproducibility & Pinned Dependencies** | [06](06-statistics-and-confidence.md) | `pyproject.toml`, `uv.lock`, fixed random seeds | Deterministic test execution (`random_state=42`) | Implemented / Tested |
| **NFR-007: Cross-Platform Portability** | [00](00-overview-and-mvp-scope.md) | Pure Python stack across Linux, macOS, and Windows | Multi-OS CI workflows & path-agnostic test suites | Implemented / Tested |
| **NFR-008: Explainability Overhead Bounding** | [07](07-explainability.md) | `src/bias_aperture/explainability.py` | Attribution restricted to flagged disparity cohorts | Implemented / Tested |
| **NFR-009: Strict Diagnostic Scope Boundary** | [00](00-overview-and-mvp-scope.md), [10](10-security-and-governance.md) | Project-wide architectural constraint | Zero retraining, debiasing, or generation routines | Implemented |
| **NFR-010: Offline Self-Containment & Data Privacy** | [08](08-report-and-compliance.md), [10](10-security-and-governance.md) | `src/bias_aperture/report/` | Offline HTML validation without remote CDN requests | Implemented / Tested |

---

## 3. Source Requirements and Authority

The formal IEEE 830-style requirement statements originate in [report/src/chapters/requirements.tex](../report/src/chapters/requirements.tex) and the planning records ([schema-lock-m1.md](../docs/schema-lock-m1.md), [BiasAperture-AT](../docs/BiasAperture-AT.md)). This document serves as the implementation-facing verification anchor ensuring continuous traceability from statutory requirements to executable tests.

When implementation and research prose disagree, record the discrepancy, prefer the locked schema and executable tests for current behavior, and label unresolved decisions rather than silently choosing a value.
