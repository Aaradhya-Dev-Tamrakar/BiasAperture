# Session Clarity & Task Prioritization — BiasAperture M5 Integration Phase

**Date:** 2026-09-01  
**Project:** BiasAperture — A Diagnostic and Evaluative Framework for Auditing Demographic Bias in Facial Analysis Systems  
**Program:** Fusemachines AI Fellowship (AIF) 2026 (Kathmandu, Nepal)  
**Authors:** Aaradhya Dev Tamrakar (`@AaradhyaDT`) & Tisha Manandhar (`@tiixsha`)  
**Supervisor:** Shreejan Kisee (Teaching Assistant, Fusemachines AI Fellowship)  
**Status:** M1–M4 Complete (55/55 Tests Passing) · M5 Integration & Benchmark Phase · Task Split Clarified

---

## 1. Executive Summary & Session Goals

This session focused on **regaining project clarity** after the rapid completion of M1–M4 phases. With 55 tests passing and the core engine verified, the team now operates in M5 (Integration & Benchmark Execution). The session accomplishments:

1. **Reviewed all planning documentation** — [`BiasAperture-AT.md` (v10)](../../docs/BiasAperture-AT.md), [Session Walkthrough (2026-08-31)](./2026-08-31_session_walkthrough_audit_and_sync.md), [Task Division & Roadmap (2026-08-31)](./2026-08-31_task_division_and_roadmap_audit.md).
2. **Extracted Master TO DOs Matrix** — Identified 9 concrete remaining action items organized by priority (P1/P2/P3).
3. **Clarified task ownership** — Locked explicit task split between Aaradhya and Tisha, eliminating ambiguity.
4. **Documented next steps** — Ready to begin empirical benchmark execution.

---

## 2. Project State Recap (as of 2026-09-01)

| Milestone | Component | Status | Owner | Test Count |
|---|---|---|---|---|
| **M1** | Schema & Data Ingestion | ✅ Complete | Tisha | 4 tests |
| **M2** | Model Interface & Fairness Backends | ✅ Complete | Aaradhya | 7 tests |
| **M3** | Statistical Testing (χ², BCa Bootstrap) | ✅ Complete | Aaradhya | 9 tests |
| **M4** | SHAP Explainability & CLI Orchestration | ✅ Complete | Aaradhya | 55+ tests total |
| **M5** | Empirical Benchmark & Report Generation | 🟡 In Progress | Both | — |

**Core Deliverables Ready:**

- ✅ Data ingestion pipeline (`src/bias_aperture/data_ingestion.py`)
- ✅ Model interface (`src/bias_aperture/model_interface.py`)
- ✅ Fairness metrics engine with Fairlearn + AIF360 backends (`src/bias_aperture/fairness/`)
- ✅ Statistical rigor (χ² tests, BCa bootstrap CIs)
- ✅ SHAP explainability layer (`src/bias_aperture/explainability.py`)
- ✅ Offline HTML report generator (`src/bias_aperture/report/`)
- ✅ CLI orchestrator with `--explain` flag (`src/bias_aperture/cli.py`)
- ✅ Complete pytest suite (55/55 passing)

**Not Yet Done:**

- 🔴 Empirical inference run (ResNet-34 on 10,954 validation images)
- 🔴 Flagship HTML audit report generation
- 🔴 Final LaTeX report with empirical results
- 🔴 Defense preparation & logistics

---

## 3. Master TO DOs — Complete Task Breakdown

### 🔴 **PRIORITY 1 — Empirical Benchmark Execution** (Start Now)

| # | Task | Owner | Target Artifact | Acceptance Criteria |
|:---:|---|:---:|---|---|
| 1.1 | **Validation Inference Run** — Execute ResNet-34 classifier inference on 10,954 FairFace validation images | **Aaradhya** | `data/processed/fairface_predictions_val.csv` | CSV contains: `image_id`, `predicted_label`, `true_label`, `subgroup_race`, `subgroup_gender`, `subgroup_age`; schema-aligned with [`schema.py`](../../src/bias_aperture/schema.py) |
| 1.2 | **Flagship Audit HTML Generation** — Execute `bias-aperture audit` on predictions CSV to generate compliance report | **Aaradhya** | `report/audit_report.html` | Zero-network standalone HTML; Model Card + Datasheet sections; all 4 disparity metrics (DPD, DIR, EOP, EOD) with 95% BCa CI and χ² p-values; subgroups with n < 30 flagged as "insufficient_sample" |
| 1.3 | **Lock Defense Logistics** — Confirm defense date, presentation duration, marking breakdown (40% project weighting) | **Tisha** | Meeting notes in [`docs/BiasAperture-AT.md`](../../docs/BiasAperture-AT.md) (§19) | Written confirmation from TA Shreejan Kisee with explicit grading rubric |

**Dependencies:** None — all three can start immediately.  
**Estimated Duration:** 2–3 days parallel execution.

---

### 🟡 **PRIORITY 2 — Compliance & Data Validation** (Parallel with P1)

| # | Task | Owner | Target Artifact | Acceptance Criteria |
|:---:|---|:---:|---|---|
| 2.1 | **Model Card & Datasheet Audit** — Audit generated HTML report for EU AI Act Article 10/13 compliance | **Tisha** | Audit checklist in `report/audit_report.html` | ✅ Model Card includes: use cases, training data, performance metrics, limitations, recommendations ✅ Datasheet includes: motivation, composition, collection process, preprocessing, distribution, maintenance ✅ Article 10 (High-risk AI): transparency obligations satisfied ✅ Article 13 (Automated individual decision-making): user rights clearly stated |
| 2.2 | **Intersectional Subgroup Slice Audit** — Verify 126 intersectional demographic bins (7 race × 9 age × 2 gender) for proper sample-size enforcement | **Tisha** | Verification report in `data/subgroup_coverage_audit.md` | ✅ All bins with n ≥ 30 have computed metrics ✅ All bins with n < 30 have `insufficient_sample=True` and `metric_value=None` ✅ No exceptions or special-case metric values for small-n bins ✅ Coverage visualization showing bin fill rates |
| 2.3 | **LaTeX Report Finalization** — Ingest empirical disparity tables into `resultsAndDiscussion.tex` and compile final `main.pdf` | **Aaradhya** | `report/main.pdf` | ✅ Table 1: DPD/DIR/EOP/EOD point estimates for all demographic groups ✅ Table 2: 95% BCa CIs for each metric ✅ Table 3: χ² test statistics and exact p-values ✅ Figure 1: Disparity heatmap (race × gender × age) ✅ Zero LaTeX compilation errors ✅ All bibliography entries resolve (bibtex clean) ✅ Glossary up-to-date (makeglossaries clean) |

**Dependencies:** 2.1 and 2.2 depend on 1.2 (audit report generated); 2.3 depends on 1.1 (predictions CSV).  
**Estimated Duration:** 2–3 days.

---

### 🟢 **PRIORITY 3 — Defense & Finalization** (After P1 + P2)

| # | Task | Owner | Target Artifact | Acceptance Criteria |
|:---:|---|:---:|---|---|
| 3.1 | **Claim Ledger Sealing** — Transition assertions in [`CLAIM_LEDGER.md`](../../docs/research/CLAIM_LEDGER.md) from `VERIFIED (STATIC)` to `REPRODUCIBLE (LIVE BENCHMARK)` | **Aaradhya** | Updated [`CLAIM_LEDGER.md`](../../docs/research/CLAIM_LEDGER.md) with `REPRODUCIBLE` seals | ✅ All major empirical claims (e.g., "FairFace contains 97,698 images", "ResNet-34 exhibits DPD of X% across demographic groups") marked `REPRODUCIBLE (BENCHMARK)` with live evidence links ✅ Claim count: all 60+ assertions addressed ✅ Examiner can trace any claim to empirical evidence |
| 3.2 | **Consolidated Slide Deck** — Create 10–15 minute unified presentation covering Problem → Dataset → Architecture → Statistics → Live Demo → Compliance | **Joint (A + T)** | `docs/presentation/slides.pdf` | ✅ Slide 1–2: Problem statement & motivation (friction gap for auditing vision classifiers) ✅ Slide 3–4: FairFace dataset integrity, 97,698 images, 7 race × 9 age × 2 gender taxonomy ✅ Slide 5–6: BiasAperture architecture (5-module dataflow, schema contracts) ✅ Slide 7–9: Statistical rigor (χ² significance, BCa bootstrap CIs, minimum n=30 guard) ✅ Slide 10–12: Live `bias-aperture audit` demo + sample report output ✅ Slide 13–15: EU AI Act compliance mapping (Articles 10, 13, 15, Annex IV) |
| 3.3 | **Viva Rehearsal & Mock Defense** — Practice terminal CLI workflow and answer grilling questions from [`VERIFICATION_AND_SCRUTINY_GUIDE.md`](../../docs/research/VERIFICATION_AND_SCRUTINY_GUIDE.md) | **Joint (A + T)** | Rehearsal notes in `docs/` | ✅ Aaradhya: Fluent demo of `bias-aperture audit --explain <csv>` with live output ✅ Tisha: Fluent walkthrough of dataset profiling and Model Card compliance ✅ Both: Answer 10+ adversarial questions from scrutiny guide without hesitation ✅ Timing: Full defense ≤ 15 minutes, questions ≤ 20 minutes ✅ Video recording or observer notes (optional but recommended) |

**Dependencies:** 3.1, 3.2, 3.3 all depend on completion of P1 + P2.  
**Estimated Duration:** 3–5 days.

---

## 4. Ownership & Trait Rationale

### **Aaradhya (BEI, IOE) — Redwood/Unicorn Hair**

**Trait Profile:** Adaptable builder, steady assembly across shifting inputs, strong tooling & mathematical depth.

**P1 Assignments:**

- Task 1.1 (Inference run): Manages batch model inference pipeline, tensor transformations, CSV schema alignment.
- Task 1.2 (Audit report): Orchestrates end-to-end ingestion → metrics → stats → SHAP → HTML pipeline.

**P2 Assignments:**

- Task 2.3 (LaTeX finalization): Re-runs `makeglossaries`, `bibtex`, `pdflatex`; consistent formatting across chapters.

**P3 Assignments:**

- Task 3.1 (Claim ledger sealing): Audits and transitions empirical claims with live evidence links.
- Task 3.2, 3.3 (Joint defense): Co-leads statistical/demo portions; practices CLI live coding under pressure.

---

### **Tisha (BCT, IOE) — Black Walnut/Dragon Heartstring**

**Trait Profile:** High-precision execution, uncompromising standard on claims & boundaries, structural & domain-level clarity.

**P1 Assignments:**

- Task 1.3 (Defense logistics): Communicates with TA Shreejan; locks grading rubric and boundaries early (intolerance for ambiguity).

**P2 Assignments:**

- Task 2.1 (Model Card audit): Acts as quality gate, ensuring HTML report matches Model Card/Datasheet standards strictly; no overstatement of compliance.
- Task 2.2 (Subgroup audit): Detail-dense scrutiny of 126 bins, verifies sample-size guards fire correctly, no exceptions.

**P3 Assignments:**

- Task 3.2, 3.3 (Joint defense): Co-leads regulatory/dataset portions; practices Model Card walkthrough under examiner questions.

---

## 5. Execution Plan & Timeline

### **Week of 2026-09-01 (This Week) — P1 Execution**

| Day | Aaradhya | Tisha | Status |
|---|---|---|---|
| **Mon 09-01** | Begin inference run setup; prepare ResNet-34 checkpoint + predict.py | Begin defense logistics outreach to Shreejan | 🔄 In Progress |
| **Tue 09-02** | Execute batch inference (10,954 validation images); generate CSV | Await Shreejan response; prepare logistics checklist | 🔄 In Progress |
| **Wed 09-03** | Run `bias-aperture audit` on CSV; debug any schema mismatches | Confirm defense date/rubric from Shreejan | 🔄 In Progress |
| **Thu 09-04** | Finalize audit HTML report; archive for review | Confirm with Aaradhya that P1 complete | 🟡 Pending |
| **Fri 09-05** | **P1 COMPLETE**; Begin LaTeX prep | **P1 COMPLETE**; Begin Model Card audit | 🟡 Pending |

### **Week of 2026-09-08 (Next Week) — P2 Execution**

| Day | Aaradhya | Tisha | Status |
|---|---|---|---|
| **Mon 09-08** | Ingest empirical tables into LaTeX | Audit Model Card/Datasheet compliance | — |
| **Tue 09-09** | Compile final `main.pdf`; verify all chapters | Audit subgroup bin coverage (126 cells) | — |
| **Wed 09-10** | Finalize LaTeX; prepare for P3 | Finalize audit reports | — |
| **Thu 09-11** | Begin claim ledger sealing | Joint: Begin slide deck creation | — |
| **Fri 09-12** | **P2 COMPLETE** | **P2 COMPLETE** | — |

### **Week of 2026-09-15 (Following Week) — P3 Execution**

| Day | Aaradhya & Tisha | Status |
|---|---|---|
| **Mon 09-15** | Joint: Finalize slide deck (10–15 minutes) | — |
| **Tue 09-16** | Joint: Mock defense rehearsal #1 (full run-through) | — |
| **Wed 09-17** | Joint: Mock defense rehearsal #2 (focus on weak areas) | — |
| **Thu 09-18** | Joint: Final prep; video recording (optional) | — |
| **Fri 09-19** | **READY FOR VIVA** | — |

---

## 6. Key Acceptance Criteria (Do Not Compromise)

1. **Sample Size Guard (NFR-003):** No metric computed for subgroups with n < 30. Must set `insufficient_sample=True` and `metric_value=None` instead.
2. **Statistical Rigor (NFR-001 & NFR-002):**
   - Every reported metric includes: point estimate, 95% BCa CI (B ≥ 1,000 resamples), χ² p-value, subgroup n.
   - Significance threshold: α = 0.05 (exact p-values reported, never binned as "p < 0.001").
3. **EU AI Act Compliance (Art. 10, 13, 15):**
   - Model Card & Datasheet sections in HTML report strictly follow Mitchell et al. & Gebru et al. templates.
   - Transparency, accuracy, and robustness obligations explicitly addressed.
4. **Zero-Network Report:** HTML report must be standalone (no external links, embedded charts as Base64).
5. **CLI Usability:** `bias-aperture audit --explain <csv>` must run end-to-end without manual intervention or debugging.

---

## 7. Remaining Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| ResNet-34 inference takes > 4 hours | Low | Delays P1 by 1 day | Pre-test on GPU with small batch; use batched prediction |
| Schema mismatch between CSV and metrics engine | Medium | Blocks entire P1–P2 | Dry-run schema validation before full inference run |
| HTML report rendering issues (charts, styling) | Low | Delays P1.2 by 1–2 days | Test Jinja2 template rendering with mock data first |
| Model Card audit uncovers compliance gaps | Medium | Requires P2.1 rework | Tisha audits early (day 1 of P1); flag issues immediately |
| Subgroup bin coverage reveals n < 30 surprises | Medium | May require data re-collection | Pre-emptively run coverage analysis on full dataset this week |
| Defense logistics unresolved from Shreejan | High | Cascades uncertainty into P3 | Tisha follows up daily if no response by Wed |

---

## 8. Success Metrics (Definition of Done)

**P1 Complete:** ✅ `fairface_predictions_val.csv` generated, ✅ `audit_report.html` generated, ✅ Defense logistics confirmed.

**P2 Complete:** ✅ Model Card audit passed, ✅ Subgroup bin audit passed (all n ≥ 30 computed, n < 30 flagged), ✅ `main.pdf` compiled with empirical tables.

**P3 Complete:** ✅ Slide deck ready, ✅ Viva rehearsal passed (both team members fluent on all topics), ✅ Claim ledger sealed.

**FINAL READINESS:** All 9 tasks complete, 55/55 tests passing, zero blockers, team confident in defense.

---

## 9. Session Artifacts & References

- **Planning:** [`docs/BiasAperture-AT.md`](../../docs/BiasAperture-AT.md) (v10)
- **Prior Walkthrough:** [Session Walkthrough (2026-08-31)](./2026-08-31_session_walkthrough_audit_and_sync.md)
- **Prior Task Division:** [Task Division & Roadmap (2026-08-31)](./2026-08-31_task_division_and_roadmap_audit.md)
- **Claim Ledger:** [`docs/research/CLAIM_LEDGER.md`](../../docs/research/CLAIM_LEDGER.md)
- **Scrutiny Guide:** [`docs/research/VERIFICATION_AND_SCRUTINY_GUIDE.md`](../../docs/research/VERIFICATION_AND_SCRUTINY_GUIDE.md)
- **Schema Lock:** [`docs/schema-lock-m1.md`](../../docs/schema-lock-m1.md)

---

## 10. Next Action (Immediate)

**Aaradhya:** Begin Task 1.1 setup — locate ResNet-34 checkpoint, verify predict.py availability, prepare batch inference pipeline.

**Tisha:** Begin Task 1.3 — draft email/message to TA Shreejan Kisee requesting defense logistics confirmation (date, duration, marking rubric).

**Both:** Confirm timeline alignment and any blocking dependencies at end of today (EOD 2026-09-01).

---

**Status:** 🟢 Ready to Execute — All 9 Tasks Mapped, Ownership Clear, Dependencies Resolved.
