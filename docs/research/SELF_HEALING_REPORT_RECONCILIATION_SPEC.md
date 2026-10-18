# Self-Healing & Dynamically Upgrading Compliance Report Creation Pipeline

**Tracked Issue**: [#57](https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/issues/57)  
**Work Packages**: WP3 (Report Generation), WP5 (CLI Orchestration & Systems Integration)  
**Author**: Aaradhya Dev Tamrakar (`@AaradhyaDT`)  
**Date**: October 18, 2026  

---

## 1. Problem Statement & Audit Findings

BiasAperture generates standalone offline HTML compliance dossiers and A4 companion PDFs adhering to the Mitchell et al. (2019) Model Card standard, Gebru et al. (2018) Datasheet format, and EU AI Act / NIST AI RMF regulatory mappings.

A comprehensive audit of the reporting pipeline revealed four critical discrepancies that require systematic remediation:

1. **Surrogate Explainability Duplication**:
   - `ShapExplainerEngine` fits a global ridge-regularized linear surrogate on the complete evaluation dataset and computes a single global feature importance vector.
   - However, the report generator previously repeated this exact same global feature importance block for every statistically flagged `(subgroup, metric)` cell.
   - For models with broad disparities (such as `MobileNetV2` and `ResNet-50` with 32 flagged cells), this duplicated identical SVG bar charts and non-causal disclaimers 32 times, inflating reports to 17 pages.
2. **Executive Summary Card 3 Mismatch**:
   - Executive Summary Card 3 (`Worst headline metric`) iterated over Table 2's subgroup rows instead of Table 1's overall cross-group summary metrics (`subgroup == "ALL"`).
   - This caused Card 3 to report `DPD = 0.097 (Black)` while Table 1 prominently displayed `DPD = 0.053` and `EOD = 0.244`, creating an immediate visual contradiction.
3. **Visual Scaling Inversion & Coordinate Distortion**:
   - `ci_whisker_svg` in Table 1 dynamically computed symmetric $[-max\_bound, +max\_bound]$ ranges around zero.
   - Because disparate impact ratio (`DIR = 0.923`) and demographic parity difference (`DPD = 0.053`) had different bounds, they were rendered at the exact same horizontal pixel (`x ≈ 175px`). Furthermore, the left half of the chart represented impossible negative values ($< 0.0$).
   - In Table 2, `_build_subgroup_matrix` sorted metric bars using `{"DPD": 0, "EOP": 1, "EOD": 2, "DIR": 3}`, causing the 4 vertical bars in `metric_bars_svg` to swap EOD and EOP relative to the table's column order (`DPD, EOD, EOP, DIR`).
4. **Maintenance Friction & Report Drift**:
   - As new models (`ViT-B/16`, `ResNet-50`, `MobileNetV2`) or new demographic axes (`race`, `gender`, `race_gender`) were introduced, report metadata had to be manually re-specified or defaulted to hardcoded ResNet-34 values.
   - Any upgrade to templates, typography, or CSS caused pre-compiled reports in `report/` to fall out of synchronization with no automated tool to detect drift or self-heal.

---

## 2. Architecture & Design Specification

### 2.1 Component 1: Dynamic Model & Dataset Metadata Auto-Resolution (`metadata_registry.py`)
To eliminate hardcoded defaults, a centralized `ModelMetadataRegistry` dynamically resolves model specifications from model names or prediction signatures:
- **Known Baselines**:
  - `FairFace ResNet-34 Multi-Task Classifier`: 21.3M parameters, multi-task linear head (race=7, gender=2, age=9), Kärkkäinen & Joo (2021).
  - `ResNet-50 (FairFace Baseline)`: 25.6M parameters, He et al. (2016), ImageNet-1k pretrained, fine-tuned on FairFace.
  - `MobileNetV2 (FairFace Baseline)`: 3.5M parameters, inverted residual bottlenecks, Sandler et al. (2018).
  - `ViT-B/16 (FairFace Baseline)`: 86.6M parameters, Vision Transformer with Patch16 embeddings, Dosovitskiy et al. (2020).
- **Self-Healing Fallback**: When evaluating an unindexed model, the registry dynamically synthesizes an honest, transparent model card based on input shape, classes, and prediction formats rather than hallucinating false weights or descriptions.

### 2.2 Component 2: Truthful Analytical & Visual Engine (`generator.py` & `report.html.j2`)
1. **Headline Metric Calibration**:
   - Card 3 (`Worst headline metric`) is computed directly from Table 1 `summary_metrics` (`subgroup == "ALL"`) across `DPD`, `EOD`, `EOP`, and `DIR` using normalized distance from parity (`|val|` for difference metrics, `|1.0 - val|` for ratio metrics).
   - Falls back to `subgroup_matrix` only when `summary_metrics` is absent (synthetic unit tests).
2. **Fixed Truthful Whisker Domain**:
   - `ci_whisker_svg` maps values to a calibrated $[0.0, 1.0]$ axis with explicit ticks at `0.0`, `0.5`, and `1.0`.
   - For difference metrics (`DPD`, `EOD`, `EOP`), the `0.10` parity threshold is marked.
   - For `DIR`, the `0.80` EEOC 4/5ths threshold and `1.00` parity reference are marked.
3. **Table 2 Metric Bar Ordering**:
   - Canonical sort order set to `order = {"DPD": 0, "EOD": 1, "EOP": 2, "DIR": 3}` to match table columns.
4. **Self-Healing Sample & Conditional Support Badges**:
   - If `subgroup_sample_size < 30`: renders `N/A (n < 30)`.
   - If `subgroup_sample_size >= 30` and `insufficient_sample`: renders `N/A (Cond. Support)` with hover title explaining strata support shortage ($P < 5$ or $N < 5$).
5. **Unified Section 3 Explainability**:
   - Merges duplicate explainability blocks into a single numbered section:
     `3. Targeted Disparity Explainability & Proxy Attributions`
     `Demographic Surrogate Associations — Mean absolute contribution to surrogate log-odds`
   - Renders the Bilodeau et al. (2024) non-causal disclaimer, a compact table of triggered `(subgroup, metric)` pairs, the global feature importance horizontal bar chart `<svg class="inline-chart">`, and numeric feature values **once**.
   - Dynamically numbers the Governance section as Section 4 (or Section 3 if attributions are absent).

### 2.3 Component 3: Autonomous Report Reconciler (`reconciler.py` & `scripts/reconcile_reports.py`)
Provides deterministic auditing and self-healing:
- `--check`: Verifies that every HTML report has an up-to-date companion PDF, complies with the R-015 offline contract (0 external URLs), satisfies factual consistency (Card 3 matches Table 1), adheres to $[0.0, 1.0]$ whisker bounds, and does not exceed page count thresholds ($\le 8$ pages).
- `--heal`: Automatically regenerates ResNet-34 reports from `data/processed/fairface_predictions_val.csv`, re-renders multi-backbone reports (`ViT-B/16`, `ResNet-50`, `MobileNetV2`) with updated metadata, and re-exports companion PDFs via the modern Blink engine.

### 2.4 Component 4: Build Automation & CI Gate Integration
- **`scripts/verify.py`**: Added deterministic check `[4/4] Report integrity & self-healing reconciliation check`.
- **`Makefile` & `make.bat`**: Added `make reconcile` (`python scripts/reconcile_reports.py --heal`) and `make check-reports` (`python scripts/reconcile_reports.py --check`).

---

## 3. Pre-Compiled Dossier Target Matrix

| Dossier | Architecture | Demographic Axis | Key Evaluated Finding |
|---|---|---|---|
| `audit_val_race_verified.html` | ResNet-34 Multi-Task | Race (7 groups) | Validated dual-backend consensus, DPD=0.053, DIR=0.923 |
| `audit_report_val_resnet_race.html` | ResNet-34 Baseline | Race (7 groups) | Benchmark baseline across FairFace validation split |
| `audit_report_val_gender.html` | ResNet-34 Baseline | Gender (2 groups) | Binary gender audit with conditional support checks |
| `audit_report_val_race_gender_shap.html` | ResNet-34 Intersectional | Race × Gender (14 groups) | Intersectional audit with surrogate attribution |
| `audit_report_val_vit_race.html` | ViT-B/16 Baseline | Race (7 groups) | 86.6M parameter Vision Transformer disparity profile |
| `audit_report_val_resnet50_race.html` | ResNet-50 Baseline | Race (7 groups) | 25.6M parameter residual network disparity profile |
| `audit_report_val_mobilenet_race.html` | MobileNetV2 Baseline | Race (7 groups) | 3.5M parameter lightweight mobile vision architecture |
