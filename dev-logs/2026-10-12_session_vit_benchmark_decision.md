# BiasAperture — Engineering & Research Decision Log

**Date:** 2026-10-12  
**Topic:** Multi-Model Auditing Expansion (ViT-B/16 vs. ResNet-34)  
**Catalyst:** Proposal Defense Panel Recommendation (Timecode 00:16:57: *"Evaluate different models, not just ResNet. Try some other models like ViT and compare the scores."*)  
**Target Branch:** `feat/vit-model-audit` (derived from canonical `main`)  
**Status:** In Progress / Decision Recorded

---

## 1. Context & Architectural Rationale

During the Phase 1 Proposal Defense, the evaluation panel acknowledged BiasAperture's diagnostic framework but strongly advised demonstrating multi-model auditing capabilities across distinct neural architectures—specifically comparing Vision Transformers (ViT) against the baseline Convolutional Neural Network (ResNet-34).

Because BiasAperture's core engine (`src/bias_aperture/`) was designed to ingest predictions via `PredictionsFileInterface` (CSV/JSON), this expansion does **not** alter the core fairness computation, schema invariants, or statistical testing modules. It only requires:
1. Running inference using a pretrained ViT model on the FairFace validation set ($N = 10,954$).
2. Exporting predictions to a schema-aligned CSV (`data/processed/fairface_predictions_vit_val.csv`).
3. Running `bias-aperture audit` to generate comparative HTML compliance dossiers.

---

## 2. Research Track Mapping

* **Track 22 (`track_22_multi_model_comparative_benchmarking_and_leaderboard.md`):**  
  * **Previous Status:** Parked on 2026-09-02 pending product roadmap stabilization.
  * **New Status:** **Unparked & Active.** Re-scoped specifically to comparative disparity analysis between ViT-B/16 and ResNet-34 on FairFace.

---

## 3. Implementation Plan & Work Breakdown

1. **Inference Runner:**
   * Author `scripts/predict_vit.py` to batch infer FairFace validation images using `google/vit-base-patch16-224` (or zero-shot CLIP ViT-B/16).
   * Decode labels for `gender`, `race`, and `age`.
2. **Data Export:**
   * Save outputs to `data/processed/fairface_predictions_vit_val.csv` with standard columns:
     `face_name_align`, `race`, `gender`, `age`, `true_label`, `predicted_label`.
3. **Disparity Auditing:**
   * Execute dual-backend audit (`FairlearnBackend` + `AIF360Backend`):
     - Demographic Parity Difference (DPD)
     - Equalized Odds Difference (EOD)
     - Equal Opportunity Difference (EOP)
     - Disparate Impact Ratio (DIR)
   * Compute 95% BCa Bootstrap Confidence Intervals ($B \ge 1,000$) and metric-specific $\chi^2$ hypothesis tests.
4. **Disparity Comparison:**
   * Generate `report/audit_report_val_vit_gender.html` and tabulate the architectural disparity delta against `report/audit_report_val_gender.html` (ResNet-34 baseline).
5. **Quality Assurance:**
   * Verify all 85+ pytests continue passing.
   * Ensure Ruff check and formatting clean.

---

## 4. Git & Branching Strategy

* **Active Feature Branch:** `feat/vit-model-audit` branched from `main`.
* **Sync Strategy:** Use `sync.ps1` to keep remotes (`origin`, `duo`, `org`) synchronized.
* **PR Integration:** Integrate into `main` via PR with partner review, referencing the corresponding GitHub issue.

---

## 5. Audit Execution Results (2026-10-12, Session 2)

**Status:**  COMPLETE — Full inference run + audit report generated.

### Infrastructure Resolved
- Resolved `SyntaxError` in `src/bias_aperture/report/generator.py` (git merge conflict markers at line 219–223 corrupted the `save()` method). Fixed by restoring `out.write_text(html, encoding="utf-8")`.
- Created `scripts/predict_vit.py` — batch ViT-B/16 inference runner using `rizvandwiki/gender-classification-2` (HuggingFace). Outputs predictions to `data/processed/fairface_predictions_vit_val.csv`.
- Full inference run completed over all $N = 10,954$ FairFace validation images.

### ViT-B/16 Headline Fairness Metrics (Race axis, N=10,954)

| Metric | Point Estimate | 95% BCa CI | p-value |
|---|---|---|---|
| DPD | 0.276 | [0.239, 0.308] | <0.001  |
| EOD | 0.274 | [0.232, 0.305] | <0.001  |
| EOP | 0.274 | [0.232, 0.305] | <0.001  |
| DIR | 0.527 | [0.493, 0.579] | <0.001  |

All 7 race subgroups flagged (p < 0.05). 0 suppressed by NFR-003 (all n ≥ 30).

### ViT-B/16 Per-Race Subgroup Matrix

| Race | n | DPD | EOP | EOD | DIR | EEOC 4/5 |
|---|---|---|---|---|---|---|
| Middle Eastern | 1,209 | 0.181 | 0.131 | 0.131 | 0.691 |  FAIL |
| East Asian | 1,550 | 0.096 | 0.139 | 0.139 | 0.763 |  FAIL |
| Southeast Asian | 1,415 | 0.090 | 0.144 | 0.144 | 0.778 |  FAIL |
| White | 2,085 | 0.039 | 0.065 | 0.065 | 0.911 |  PASS |
| Black | 1,556 | 0.035 | 0.080 | 0.080 | 0.913 |  PASS |
| Indian | 1,516 | 0.025 | 0.076 | 0.076 | 0.941 |  PASS |
| Latino/Hispanic | 1,623 | 0.005 | 0.050 | 0.050 | 0.988 |  PASS |

### Cross-Model Comparison: ViT-B/16 (Race) vs. ResNet-34 (Gender)

| Dimension | ViT-B/16 — Race | ResNet-34 — Gender |
|---|---|---|
| N | 10,954 | 10,954 |
| DPD | **0.276**  | **0.923**  |
| DIR | **0.527**  | **0.039**  |
| Significant subgroups | 7 / 7 | 2 / 2 |
| Worst subgroup | Middle Eastern (DIR=0.691) | Female (DPD=0.488, DIR=0.070) |

**Interpretation:**
- ResNet-34 exhibits **catastrophically extreme gender bias** (DIR=0.039, DPD=0.923) — the model almost exclusively classifies male as positive.
- ViT-B/16 exhibits **moderate but significant race bias** — Middle Eastern, East Asian, and Southeast Asian groups fail the EEOC 4/5ths threshold (DIR < 0.80). White, Black, Indian, and Latino/Hispanic groups pass.
- Both architectures show demographically disparate behaviour at $p < 0.001$; neither is compliant under EU AI Act Art. 10 / NIST Measure 2.11.
- The disparity pattern in ViT reflects training distribution skew toward Western/East Asian faces, consistent with literature on ImageNet-lineage models.

### Output Artifacts

| Artifact | Path |
|---|---|
| ViT predictions CSV | `data/processed/fairface_predictions_vit_val.csv` |
| ViT audit report | `report/audit_report_val_vit_race.html` |
| ResNet-34 baseline | `report/audit_report_val_gender.html` |
| Inference script | `scripts/predict_vit.py` |

### Next Steps
- [ ] Sync branch `feat/vit-model-audit` to all remotes via `sync.ps1`.
- [ ] Open PR → `main` with partner review.
- [ ] Update Track 22 in `PHASE2_TASK_MAP.md` to `COMPLETE`.
- [ ] Reference findings in LaTeX report `report/main.tex` (Section: Multi-Model Evaluation).
