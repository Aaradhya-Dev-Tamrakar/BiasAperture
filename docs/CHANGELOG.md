# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `__main__.py` module entrypoint for `python -m bias_aperture` support.
- Comprehensive end-to-end integration test suite (`test_integration.py`):
  multi-group race audits, gender-axis switching, insufficient-sample guards,
  CLI error paths, and module entrypoint verification.
- Semantic changelog replacing sync-only timestamps.

## [0.1.0] — 2026-09-05

### Added

- **Schema (M1 Lock)**: `SubjectRecord` and `MetricResult` dataclasses with
  frozen-field enforcement, demographic label taxonomies (`RACE_LABELS`,
  `GENDER_LABELS`, `AGE_LABELS`), and NFR-003 data-integrity guard
  (`MIN_SUBGROUP_SAMPLE_SIZE = 30`).
- **Data Ingestion (WP2)**: `DataIngestionPipeline` with dual-mode validation
  (STRICT / PERMISSIVE), column alias resolution, duplicate detection, cohort
  profiling, and OvR multi-class transformation.
- **Model Interface (WP1)**: `PredictionsFileInterface` for CSV/JSON batch
  ingestion; `InProcessInterface` abstract contract (stub for WP2 extension).
- **Fairness Engine (WP4)**: Dual-backend strategy pattern with
  `FairlearnBackend` and `AIF360Backend` computing the Core Four metrics
  (DPD, EOD, EOP, DIR); `CrossValidationOrchestrator` for multi-backend
  consensus verification with divergence alerting.
- **Statistical Rigour**: BCa bootstrap confidence intervals
  (`B ≥ 1,000` resamples), Pearson's χ² independence test with Fisher's exact
  test fallback for sparse 2×2 tables, and Holm–Bonferroni step-down FWER
  correction.
- **Explainability (WP4/WP5)**: `ShapExplainerEngine` with conditional
  triggering (p < 0.05, n ≥ 30), exact additive Shapley surrogate attribution
  via logistic regression proxy, and `compute_ita()` ITA colorimetry function.
- **Report Generation (WP3)**: Zero-network standalone HTML compliance reports
  via Jinja2 templates, with Model Card presentation, executive summary strip,
  severity-ordered subgroup matrices, and regulatory mapping tables (EU AI Act
  Articles 10/13, NIST AI RMF Measure 2.11).
- **CLI Orchestrator (WP5)**: `bias-aperture` console entrypoint wiring the
  full pipeline: ingestion → dual-backend fairness → conditional explainability
  → HTML report compilation.
- **CI/CD**: GitHub Actions workflow with pytest and Ruff linting on `main`.
- **Multi-remote sync**: `sync.ps1` script for automated staging, rebasing, and
  pushing across `origin`, `duo`, and `org` mirrors.
- **Documentation**: 12 specification documents (`specs/00–11`), literature
  review matrix (20 papers), proposal defense master dossier, presentation
  slides with speaker notes, and data governance guidelines.
- **Research infrastructure**: FairFace prediction scripts, dev subset
  stratification, stale-claims checker, and multi-stream research results.

### Fixed

- Harmonised AIF360 backend sign conventions for EOD (max-of-gaps) and EOP
  (unsigned absolute difference) to match Fairlearn's formulations.
- Fisher's exact test fallback for sparse 2×2 contingency tables when any
  expected cell count < 5.
- Stale SHAP/UTKFace claims cleaned across six documentation files.
- Node 20 deprecation warning suppression in GitHub Actions CI.

### Changed

- UTKFace formally cut from runtime scope (profiled only) due to DEX age noise
  and race-label collapse; FairFace retained as sole benchmark dataset.
- Spatial SHAP (PartitionExplainer) and ITA pipeline integration deferred to
  Phase 2; surrogate Shapley attribution serves as the production fallback.
