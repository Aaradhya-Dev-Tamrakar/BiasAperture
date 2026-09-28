# BiasAperture WP3/WP5 — Session Summary: Embedding Targeted SHAP Attributions in HTML Compliance Report

**Date:** September 28, 2026  
**Author:** Tisha (`tiixsha`)  
**Track:** WP3 (Reporting Engine) & WP5 (Integration Pipeline)  
**Related Issue:** [Issue #24](https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/issues/24)  
**Branch:** `feat/wp4-engine`  
**Status:** ✅ Implemented & Tested (Issue #24 remains Open for review)

---

## 1. Problem Statement & Objectives

Per **Issue #24** and **Spec 07 / FR-005**:
- When statistically significant disparities ($p < 0.05, n \ge 30$) are identified, the platform triggers `ShapExplainerEngine` to compute surrogate Shapley feature attributions.
- Previously, `cli.py` ran `ShapExplainerEngine.explain_disparity()` and logged the results to terminal output, but did not forward `ExplanationResult` objects to `ReportContext` or render them in the standalone HTML report.
- The objective was to integrate targeted disparity explanations into the compliance report as Section 3 with pure inline SVG bar charts, while maintaining:
  1. **Schema invariance (Milestone M1)**: `MetricResult` and `SubjectRecord` remain untouched.
  2. **Strict offline compliance (NFR-001)**: Zero external CDNs, scripts, fonts, or images.
  3. **Non-causal regulatory disclaimer**: Clear attribution framing per Bilodeau et al. (2022).

---

## 2. Changes Made

### A. Report Generator Context & Indexing (`src/bias_aperture/report/generator.py`)
- Added `attributions: Sequence[ExplanationResult] = field(default_factory=tuple)` to `ReportContext`.
- Updated `_prepare_template_context()` to construct an `attribution_map: dict[tuple[str, str], ExplanationResult]` keyed by `(subgroup, metric_name)` for $O(1)$ lookups in Jinja2 templates.
- Added `has_attributions: bool` flag to dynamically toggle section rendering.

### B. Report HTML Template (`src/bias_aperture/report/templates/report.html.j2`)
- Added **Section 3: Targeted Disparity Explainability & Proxy Attributions**:
  - Displays one row per flagged disparity with subgroup label, metric badge, and surrogate details.
  - Renders inline SVG bar charts (`shap_bar_svg` macro) showing normalized Shapley feature importance scores.
  - Incorporates the Bilodeau et al. (2022) non-causal disclaimer box.
- Renumbered subsequent Governance Documentation section to Section 4.

### C. CLI Pipeline Orchestration (`src/bias_aperture/cli.py`)
- Collected `ExplanationResult` objects returned by `explainer.explain_disparity()` into `attributions`.
- Forwarded `attributions` into `ReportContext`.
- Enabled `--explain` / `--no-explain` toggling via `argparse.BooleanOptionalAction`.

### D. Automated Test Suite (`src/tests/test_report_shap.py`, `src/tests/test_cli.py`)
- Added [test_report_shap.py](file:///d:/Work/Fusemachines/Fusemachines-Capstone/Proposal/BiasAperture/src/tests/test_report_shap.py):
  - `test_html_report_with_shap_attributions`: Verifies section 3 rendering, SVG charts, and confirms 0 external CDN violations via `_verify_offline_html_contract()`.
  - `test_html_report_without_shap_attributions`: Verifies clean omission of section 3 when no disparities are flagged.
- Updated [test_cli.py](file:///d:/Work/Fusemachines/Fusemachines-Capstone/Proposal/BiasAperture/src/tests/test_cli.py):
  - Verified `--explain` correctly populates the report and `--no-explain` omits the explainability section.

---

## 3. Teammate Handoff & Review Checklist
- [x] Context and template updated in `src/bias_aperture/report/`
- [x] CLI forwarding updated in `src/bias_aperture/cli.py`
- [x] Regression & contract tests added in `src/tests/test_report_shap.py` & `src/tests/test_cli.py`
- [x] Verified zero external dependencies / strict offline contract preserved
- [ ] Review PR / branch `feat/wp4-engine` into `main`
- [ ] Close Issue #24 upon PR merge
