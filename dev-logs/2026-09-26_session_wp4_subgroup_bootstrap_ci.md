# BiasAperture WP4 — Session Summary: Per-Subgroup BCa Bootstrap Confidence Intervals

**Date:** September 26, 2026  
**Author:** Tisha (`tiixsha`)  
**Track:** WP4 (Fairness Backends & Statistical Engine)  
**Related Issue:** [Issue #23](https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/issues/23)  
**Branch:** `feat/wp4-engine`  
**Status:** ✅ Implemented & Tested (Issue #23 remains Open for review)

---

## 1. Problem Statement

An audit of `src/bias_aperture/fairness/backends.py` revealed that while the cross-group `ALL` summary rows correctly computed 95% BCa bootstrap confidence intervals ($B \ge 1,000$) via `compute_stratified_bootstrap_ci`, individual per-subgroup rows across all four core metrics:
- Demographic Parity Difference (DPD)
- Equal Opportunity Difference (EOP)
- Equalized Odds Difference (EOD)
- Disparate Impact Ratio (DIR)

in both `FairlearnBackend` and `AIF360Backend` were using hardcoded placeholder bounds:
```python
ci_lower = max(0.0, grp_val - 0.05)
ci_upper = min(1.0, grp_val + 0.05)
```
This diverged from **NFR-002**, **Spec 06** (`specs/06-statistics-and-confidence.md`), and **Claim R-009** (`docs/research/CLAIM_LEDGER.md`).

---

## 2. Changes Made

### A. Fairness Backends (`src/bias_aperture/fairness/backends.py`)
- Replaced placeholder `±0.05` intervals with calls to `compute_stratified_bootstrap_ci` for all 4 metrics across both `FairlearnBackend` and `AIF360Backend`.
- Implemented vectorized group-vs-global helper functions:
  - `_grp_dpd_fn`: Group selection rate vs. global selection rate gap $|r_g - r_{\text{global}}|$.
  - `_grp_eop_fn`: Group TPR vs. global TPR gap $|\text{TPR}_g - \text{TPR}_{\text{global}}|$.
  - `_grp_eod_fn`: Worst-case gap $\max(|\text{TPR}_g - \text{TPR}_{\text{global}}|, |\text{FPR}_g - \text{FPR}_{\text{global}}|)$.
  - `_grp_dir_fn`: Symmetric ratio $\min(r_g, r_{\text{global}}) / \max(r_g, r_{\text{global}})$.
- Resampling is stratified on the one-vs-rest binary partition `rest_sensitive = np.where(sensitive == g, g, "REST")`.
- Preserved the Milestone M1 schema invariant: subgroups with $n < 30$ remain strictly flagged with `insufficient_sample=True`, `metric_value=None`, and `ci_lower=ci_upper=None`.

### B. Unit & Integration Tests (`src/tests/test_fairness_backends.py`)
- Added `test_per_subgroup_bootstrap_ci_not_hardcoded()` verifying that:
  - Every eligible subgroup ($n \ge 30$) produces valid numerical confidence bounds in $[0, 1]$.
  - The calculated bounds do not match the old `metric_value ± 0.05` placeholder.
  - Both `FairlearnBackend` and `AIF360Backend` achieve harmonized consensus.

---

## 3. Teammate Handoff & Review Checklist
- [x] Code implemented in `src/bias_aperture/fairness/backends.py`
- [x] Tests added in `src/tests/test_fairness_backends.py`
- [x] Tracked under GitHub Issue #23
- [ ] Review PR / branch `feat/wp4-engine` into `main`
- [ ] Close Issue #23 upon PR merge
