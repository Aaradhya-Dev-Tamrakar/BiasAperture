# BiasAperture — Monthly Progress & Weekly Reports Index

**Period:** August 2026 (2026-08-01 through 2026-08-31)  
**Project:** BiasAperture — A Diagnostic and Evaluative Framework for Auditing Demographic Bias in Facial Analysis Systems  
**Program:** Fusemachines AI Fellowship (AIF) 2026 (Kathmandu, Nepal)  
**Authors:** Aaradhya Dev Tamrakar (`@AaradhyaDT`) & Tisha Manandhar (`@tiixsha`)  
**Supervisor:** Shreejan Kisee (Teaching Assistant, Fusemachines AI Fellowship)  
**Current Milestone State:** M1–M4 Core Engine Verified · 55/55 Tests Passing · M5 Integration in Progress

---

## 1. Executive Summary

During August 2026, BiasAperture advanced from an initial fellowship proposal to an audit-grade diagnostic software platform. Development was structured across four weekly sprints, covering proposal scaffolding, schema locking (M1), requirements and architecture formalization, a 20-track parallel research sprint, dataset exploration, fairness engine implementation (Fairlearn and native AIF360 backends), bootstrap confidence intervals, Chi-squared significance testing, additive Shapley surrogate feature attribution, offline HTML reporting, and a full CLI orchestrator with 55 passing unit tests.

```
August 2026 Sprint Progression:
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│ Week 1 (Aug 01-07)      │ ──> │ Week 2 (Aug 08-14)      │ ──> │ Week 3 (Aug 15-21)      │ ──> │ Week 4 (Aug 22-31)      │
│ Inception & LaTeX Cls   │     │ M1 Schema Lock & Papers │     │ FR-001-005 & TA Stds    │     │ 20-Tracks, Math & CLI   │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
```

---

## 2. Weekly Reports Breakdown

The complete weekly development logs are divided into dedicated reports:

| Sprint Report | Date Range | Primary Focus | Key Deliverables & Milestones |
|---|:---:|---|---|
| **[WK1 Report](2026-08-07_WK1_report.md)** | `2026-08-01` $\to$ `2026-08-07` | **Inception, LaTeX & Environment** | Custom `at_fuse_aif.cls` document class, Overleaf optimization, VS Code recipes, `README.md` baseline, initial `sync.ps1`. |
| **[WK2 Report](2026-08-14_WK2_report.md)** | `2026-08-08` $\to$ `2026-08-14` | **M1 Schema Lock & Literature Matrix** | Milestone M1 schema contract (`schema.py`, `schema-lock-m1.md`), $n < 30$ sample guards, 9-paper literature matrix in Walden format. |
| **[WK3 Report](2026-08-21_WK3_report.md)** | `2026-08-15` $\to$ `2026-08-21` | **Requirements, Architecture & Standards** | Functional requirements (`FR-001`–`FR-005`), statutory mappings (EU AI Act / NIST AI RMF), 5-module system architecture, TA/Khwopa standards (Ruff, pyproject.toml), agent guidelines. |
| **[WK4 Report](2026-08-27_WK4_report.md)** | `2026-08-22` $\to$ `2026-08-27` (Thursday close) | **Research Sprint, Core Engine & CLI** | 20-track research sprint, 3-level synthesis, `CLAIM_LEDGER.md`, FairFace disk verification (97,698 images), Fairlearn + native AIF360 backends, BCa bootstrap ($B \ge 1,000$), $\chi^2$ significance tests, SHAP explainer, `bias-aperture` CLI, 55/55 Pytest tests, multi-remote sync. |

The current report after the August 27 cutoff is [WK5 Report](2026-09-02_WK5_report.md), covering August 28 through September 2 and the Phase-2 Product Upgrade Sprint.

---

## 3. High-Level Monthly Achievements

1. **Academic & Statutory Scaffolding**:
   - Proposal compiled and formatted using `at_fuse_aif.cls` (`report/main.pdf`).
   - Mapped all 5 functional requirements to EU AI Act (Articles 10, 13, 15) and NIST AI Risk Management Framework (Map, Measure, Manage).
2. **Empirical Groundwork & Claim Ledger**:
   - Resolved dataset disk counts: **97,698 released FairFace images** verified on disk.
   - Identified UTKFace synthetic DEX noise to support diagnostic boundaries.
   - Established auditable [`CLAIM_LEDGER.md`](../../docs/research/CLAIM_LEDGER.md) tracking 60+ verified claims with formal reproduction procedures.
3. **Core Algorithmic Engine**:
   - Implemented Core Four metrics (DPD, DIR, EOP, EOD) with dual backends (Fairlearn and native AIF360 `BinaryLabelDataset` / `ClassificationMetric`).
   - Implemented 95% BCa Bootstrap Confidence Intervals ($B \ge 1,000$) and Chi-squared significance tests ($p < 0.05$).
   - Implemented exact linear Shapley surrogate feature attribution layer ($\phi_i = w_i(x_i - \mathbb{E}[x_i])$) in `explainability.py`.
4. **Tooling & Orchestration**:
   - Offline, single-file Jinja2 HTML report generator with embedded Base64 charts and zero CDN network calls.
   - Command-line interface (`bias-aperture audit`) with multi-backend and explainability toggles.
   - 100% pass rate across 55 automated unit tests (`uv run --extra dev pytest`).
   - Clean Git synchronization across all three configured remotes (`origin`, `duo`, `org`).

---

## 4. Master TO DOs & Remaining Roadmap

| Priority | Category / Phase | Target Deliverable | Owner | Target Branch / File |
|:---:|---|---|:---:|---|
| 🔴 **P1** | **Empirical Benchmark** | Validation split inference (`predict.py`) over 10,954 images | Aaradhya | `data/processed/fairface_predictions_val.csv` |
| 🔴 **P1** | **Empirical Benchmark** | Execute `bias-aperture audit` to render flagship HTML report | Aaradhya | `report/audit_report.html` |
| 🔴 **P1** | **Supervisor Logistics** | Confirm Viva defense date, duration, and score breakdown with TA Shreejan Kisee | Tisha | `docs/BiasAperture-AT.md` |
| 🟡 **P2** | **Compliance Verification** | Audit Model Card & Datasheet text for statutory compliance | Tisha | `report/audit_report.html` |
| 🟡 **P2** | **Data Validation** | Verify representation across 126 intersectional bins ($7 \times 9 \times 2$) | Tisha | `data/` |
| 🟡 **P2** | **LaTeX Report** | Ingest final benchmark tables and SHAP plots into `report/main.pdf` | Aaradhya | `report/main.pdf` |
| 🟢 **P3** | **Claim Ledger** | Transition ledger claims to `REPRODUCIBLE (LIVE BENCHMARK)` | Aaradhya | `docs/research/CLAIM_LEDGER.md` |
| 🟢 **P3** | **Defense Preparation** | Compile unified 10–15 min presentation deck & rehearse live demo | Joint | `docs/presentation/slides.pdf` |

---

## 5. Related Master Documentation

- [Master Task Division & Trait Allocation](../../docs/BiasAperture-AT.md)
- [Session Walkthrough: Full Codebase Audit & Sync](../2026-08-31_session_walkthrough_audit_and_sync.md)
- [Task Division & Roadmap Audit](../2026-08-31_task_division_and_roadmap_audit.md)
- [Auditable Research Claim Ledger](../../docs/research/CLAIM_LEDGER.md)
- [Proposal Defense Preparation Guide](../../docs/PROPOSAL_DEFENSE_GUIDE.md)
