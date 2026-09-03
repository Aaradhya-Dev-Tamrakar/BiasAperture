# Session Walkthrough: Full Codebase Audit, Discrepancy Resolution & Multi-Remote Git Synchronization

**Date:** 2026-08-31  
**Project:** BiasAperture — A Diagnostic and Evaluative Framework for Auditing Demographic Bias in Facial Analysis Systems  
**Program:** Fusemachines AI Fellowship (AIF) 2026 (Kathmandu, Nepal)  
**Authors:** Aaradhya Dev Tamrakar (`@AaradhyaDT`) & Tisha Manandhar (`@tiixsha`)  
**Supervisor:** Shreejan Kisee (Teaching Assistant, Fusemachines AI Fellowship)  
**Status:** M1–M5 Core Engine Verified · 55/55 Tests Passing · Git Clean Across All Remotes (`origin`, `duo`, `org`)

---

## 1. Executive Summary & Objectives

In this session, we performed an end-to-end audit, reconciliation, and synchronization of the BiasAperture codebase against the project requirements, planning documentation ([`docs/BiasAperture-AT.md`](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/docs/BiasAperture-AT.md)), and [`README.md`](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/README.md).

### Core Goals Accomplished

1. **Repository & Documentation Audit**: Evaluated claims, file trees, sprint matrices, and implementation statuses across all 5 work packages (WP1–WP5).
2. **Discrepancy Identification & Remediation**:
   - Fixed `AIF360Backend` pass-through delegation by implementing native `aif360.datasets.BinaryLabelDataset` and `aif360.metrics.ClassificationMetric`.
   - Implemented exact additive Shapley surrogate attribution layer ($\phi_i = w_i(x_i - \mathbb{E}[x_i])$) in [`src/bias_aperture/explainability.py`](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/src/bias_aperture/explainability.py) with resilient fallback for Windows C-extension DLL / MAX_PATH issues.
   - Connected the explainability pipeline to the CLI orchestrator ([`src/bias_aperture/cli.py`](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/src/bias_aperture/cli.py)) via the `--explain` flag.
   - Fixed tree structure and documentation version drift in [`README.md`](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/README.md).
3. **Verification & Testing**:
   - Expanded test suite to **55 tests**, achieving 100% pass rate (`uv run --extra dev pytest`).
   - Linted and formatted with Ruff with 0 errors (`ruff check`, `ruff format`).
4. **Git Conflict Resolution & Synchronization**:
   - Successfully pulled upstream changes from `origin/main`.
   - Resolved merge conflicts across `README.md`, `pyproject.toml`, and generated a clean `uv.lock`.
   - Successfully pushed commit `eb43fa5` to all three configured remotes:
     - `origin` (`https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models.git`)
     - `duo` (`https://github.com/AaradhyaDT/BiasAperture.git`)
     - `org` (`https://github.com/Aaradhya-Dev-Tamrakar/BiasAperture.git`)

---

## 2. Audit Findings & Resolution Matrix

```
┌─────────────────────────┬──────────────────────────────────┬────────────────────────────────────────────────────────┐
│ Component / Track       │ Identified Discrepancy           │ Resolution Implemented                                 │
├─────────────────────────┼──────────────────────────────────┼────────────────────────────────────────────────────────┤
│ AIF360 Backend          │ AIF360Backend delegated directly │ Implemented native BinaryLabelDataset mapping and      │
│ (WP4 - Engine)          │ to Fairlearn adapter             │ ClassificationMetric invocations in backends.py        │
├─────────────────────────┼──────────────────────────────────┼────────────────────────────────────────────────────────┤
│ Explainability & SHAP   │ Module had placeholder method    │ Added ShapExplainerEngine with linear surrogate exact  │
│ (WP4 - FR-005)          │ without live attribution logic   │ Shapley computation and safe numba/shap guard          │
├─────────────────────────┼──────────────────────────────────┼────────────────────────────────────────────────────────┤
│ CLI Orchestrator        │ CLI lacked explainability hook   │ Added --explain flag and wired flagged disparity       │
│ (WP5 - Integration)     │                                  │ attribution trigger (p < 0.05 and n >= 30)             │
├─────────────────────────┼──────────────────────────────────┼────────────────────────────────────────────────────────┤
│ Documentation           │ README tree missing files;       │ Synchronized repo layout and bumped AT version marker  │
│ (Docs / Planning)       │ BiasAperture-AT marked v6        │ to (v10) matching latest sprint iteration              │
├─────────────────────────┼──────────────────────────────────┼────────────────────────────────────────────────────────┤
│ Git Sync & Remotes      │ Upstream divergence causing      │ Resolved merge conflicts, regenerated uv.lock, and     │
│ (Version Control)       │ rejected push                    │ pushed cleanly to origin, duo, and org                 │
└─────────────────────────┴──────────────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 3. Code Modifications Breakdown

### 3.1 Native AIF360 Backend (`src/bias_aperture/fairness/backends.py`)

- Replaced the pass-through delegator with full protected-attribute encoding into `aif360.datasets.BinaryLabelDataset`.
- Configured `ClassificationMetric` with privileged group indices vs unprivileged group indices for multi-group demographic disparity extraction.
- Preserved harmonization across both Fairlearn and AIF360 backends conforming to R-005/R-006.

### 3.2 Additive Shapley Surrogate Explainability (`src/bias_aperture/explainability.py`)

- Implemented `explain_surrogate(records, target_subgroup)` calculating exact linear Shapley values:
  $$\phi_i = w_i(x_i - \mathbb{E}[x_i])$$
- Built robust defensive imports against Windows MAX_PATH/numba DLL load issues, ensuring explainability runs seamlessly in all CI/CD and local development environments without binary crashes.
- Added structured output dataclass `SurrogateExplanation` capturing top demographic proxy drivers.

### 3.3 CLI Integration (`src/bias_aperture/cli.py`)

- Added `--explain` CLI argument (boolean flag, defaults to True).
- Evaluated significant disparities ($p < 0.05$, $n \ge 30$) and triggered automatic proxy feature attribution outputting formatted explanation summaries to stdout and reports.

### 3.4 Package & Dependency Alignment (`pyproject.toml`, `uv.lock`)

- Registered `shap>=0.49.1` and `scikit-learn>=1.3.0` in package dependencies and optional `dev`/`fairness` groups.
- Regenerated `uv.lock` with zero syntax or version conflicts.

---

## 4. Test Suite & Validation Evidence

### Pytest Execution Summary

```
uv run --extra dev pytest
============================= test session starts =============================
platform win32 -- Python 3.13.x, pytest-8.x.x, pluggy-1.x.x
rootdir: c:\Users\Aaradhya\Downloads\_Organized\Fuse AI Fellowship\Capstone Project\fuseai-fellowship\BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models
configfile: pyproject.toml
testpaths: src/tests
collected 55 items

src/tests/test_backend_harmonization.py ....                             [  7%]
src/tests/test_cli.py ......                                            [ 18%]
src/tests/test_data_ingestion.py ....                                   [ 25%]
src/tests/test_explainability.py ...                                    [ 30%]
src/tests/test_fairness_backends.py ......                              [ 41%]
src/tests/test_fairness_metrics.py ..........                           [ 60%]
src/tests/test_fairness_statistics.py .........                         [ 76%]
src/tests/test_known_answer_fairness_metrics.py ....                    [ 83%]
src/tests/test_model_interface.py ...                                   [ 89%]
src/tests/test_offline_report_contract.py ...                           [ 94%]
src/tests/test_report_generator.py .                                    [ 96%]
src/tests/test_schema.py ..                                             [100%]

============================== 55 passed in 3.76s ==============================
```

### Ruff Quality Checks

```bash
uv run --extra dev ruff check src/
# Output: All checks passed!

uv run --extra dev ruff format --check src/
# Output: 27 files already formatted
```

---

## 5. Git Remote Synchronization & Provenance

Commit `eb43fa5` titled:
> `fix(engine): harmonize AIF360 backend, integrate SHAP proxy explainer, and sync docs`

Successfully pushed to all 3 remotes:

```
To https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models.git
   2a850fa..eb43fa5  main -> main
To https://github.com/AaradhyaDT/BiasAperture.git
   2a850fa..eb43fa5  main -> main
To https://github.com/Aaradhya-Dev-Tamrakar/BiasAperture.git
   2a850fa..eb43fa5  main -> main
```

---

## 6. Next Steps & Remaining Roadmap

1. **Benchmark Execution (M5)**:
   - Run live FairFace validation split (97,698 images / ResNet-34 predictions) through `bias-aperture` CLI.
   - Generate full offline standalone HTML compliance audit report.
2. **LaTeX Report Integration**:
   - Insert final computed disparity tables, bootstrap confidence intervals, and SHAP attribution figures into `report/main.pdf`.
3. **Viva Defense Readiness**:
   - Review [`docs/PROPOSAL_DEFENSE_GUIDE.md`](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/docs/PROPOSAL_DEFENSE_GUIDE.md) and [`docs/BiasAperture_NOVELTY_INTEGRATION_DEFENSE.md`](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/docs/BiasAperture_NOVELTY_INTEGRATION_DEFENSE.md) for final presentation.
