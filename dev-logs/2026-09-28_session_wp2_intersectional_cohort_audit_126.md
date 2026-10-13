# BiasAperture WP2/WP3 — Session Summary: 126 Race × Age × Gender Intersectional Cohort Audit

**Date:** September 28, 2026  
**Author:** Tisha Manandhar (`tiixsha`)  
**Track:** WP2 (Stream A: Data Ingestion & Governance) & WP3 (Reporting)  
**Related Issue:** [Issue #25](https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/issues/25)  
**Branch:** `feat/stream-data`  
**Status:** ✅ Implemented & Tested (Issue #25 remains Open for review)

---

## 1. Problem Statement & Motivation

Under **EU AI Act Article 10(5)** and project requirement **NFR-003**:
- Demographic bias auditing cannot rely solely on 1D unitary protected attributes (e.g. race alone or gender alone). Deeply marginalized intersectional subgroups may experience compounding bias that is obscured in aggregate metrics.
- The locked FairFace demographic taxonomy (Milestone M1) comprises:
  - 7 Races (`East Asian`, `Indian`, `Black`, `White`, `Middle Eastern`, `Latino_Hispanic`, `Southeast Asian`)
  - 9 Age Brackets (`0-2`, `3-9`, `10-19`, `20-29`, `30-39`, `40-49`, `50-59`, `60-69`, `70+`)
  - 2 Genders (`Male`, `Female`)
- This forms an exact **$7 \times 9 \times 2 = 126$ cell 3-way contingency matrix**.
- When evaluating datasets with intersectional granularity, sparse cells with $n < 30$ samples must be strictly flagged as `insufficient_sample=True` to prevent erratic metric estimates and invalid statistical inferences (Claim **R-008**, **R-009**).

---

## 2. Technical Implementation

### A. Core Engine (`src/bias_aperture/data_ingestion.py`)
- **`compute_126_intersectional_matrix`**: Classmethod added to `DataIngestionPipeline` that:
  - Systematically constructs the Cartesian product of all 126 `(race, age, gender)` tuples.
  - Enumerates and calculates sample sizes ($n$), positive support ($n_{Y=1}$), and negative support ($n_{Y=0}$).
  - Strictly tags each cell with `is_nfr003_eligible` ($n \ge 30$) and `insufficient_sample_at_ingestion` ($n < 30$).
- **`SubgroupCohortProfile` Extensions**:
  - Added `intersectional_126_counts: dict[str, SubgroupCellStats]` field.
  - Added convenience properties: `eligible_126_cells`, `insufficient_126_cells`, `eligible_126_count`, and `insufficient_126_count`.
  - Preserved backward compatibility with existing 2-way intersectional lookups (`intersectional_counts`).

### B. Audit Script (`scripts/audit_126_intersectional_cohort.py`)
- Standalone execution script running the 126-cohort profiler over `data/processed/fairface_predictions_val.csv`.
- Generates markdown verification table artifact `docs/research/INTERSECTIONAL_COHORT_AUDIT_126.md`.

### C. Automated Test Suite (`src/tests/test_data_ingestion.py`)
- Added `test_compute_126_intersectional_matrix()`:
  - Verifies exact $7 \times 9 \times 2 = 126$ cell count.
  - Asserts consistency: $\sum n_i = N_{\text{cohort}}$.
  - Validates eligibility thresholding: $n \ge 30$ passes, $n < 30$ is marked insufficient.
  - Validates that zero-count cells are preserved with $n=0$ and flagged insufficient.
- Added `test_subgroup_cohort_profile_126_properties()`:
  - Verifies `eligible_126_count` and `insufficient_126_count` slice filters.

---

## 3. Empirical Audit Findings (`fairface_predictions_val.csv`)

Execution of `scripts/audit_126_intersectional_cohort.py` across the 10,389 valid validation records yielded:
- **Eligible Cells ($n \ge 30$):** **85 / 126** (67.5%)
- **Sparse / Suppressed Cells ($n < 30$):** **41 / 126** (32.5%)
- **Key Intersectional Risk Areas:**
  - `70+` Age Bracket: **0 / 14 cells eligible (0.0% coverage)**. All elderly intersectional bins are statistically unmeasurable and suppressed.
  - `0-2` Age Bracket: **1 / 14 cells eligible (7.1% coverage)**. Only `White Female` infant cohort meets $n \ge 30$.
  - `60-69` Age Bracket: **2 / 14 cells eligible (14.3% coverage)**. Only `White Male` and `White Female` meet $n \ge 30$.
  - Core Age Brackets (`3-9`, `10-19`, `20-29`, `30-39`, `40-49`): **100.0% coverage** (14/14 cells eligible across all races and genders).

---

## 4. Teammate Handoff & Review Checklist
- [x] Implemented `compute_126_intersectional_matrix()` in `src/bias_aperture/data_ingestion.py`
- [x] Extended `SubgroupCohortProfile` with 126-cell properties
- [x] Added unit tests in `src/tests/test_data_ingestion.py` (31/31 passed)
- [x] Created `scripts/audit_126_intersectional_cohort.py`
- [x] Generated `docs/research/INTERSECTIONAL_COHORT_AUDIT_126.md` with full 126-cell distribution
- [x] Preserved Milestone M1 schema invariance (`SubjectRecord` and `MetricResult` untouched)
- [x] Verified zero Ruff linter errors (`ruff check src/`)
- [ ] Review PR / branch `feat/stream-data` into `main`
- [ ] Close Issue #25 upon PR merge

