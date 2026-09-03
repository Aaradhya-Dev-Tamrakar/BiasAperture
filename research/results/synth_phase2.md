# Phase-2 Research Synthesis — Tracks 21, 24–38

**Parent epic:** task_2026-09-02_002 · 16 tracks merged (22/23 blocked, excluded — see note at end) · Research-only, no code/repo edits in any track.

---

## 1. Verdict Matrix

| Track | Topic | Stream | Recommendation | Novelty | Scope |
|---|---|---|---|---|---|
| 21 | Streaming/Continuous Audit Mode | — | PROTOTYPE FIRST (design only) | — | Additive |
| 24 | Bias Root-Cause Clustering | G (Novelty) | PROTOTYPE FIRST (Variant 2 only) | Weak/Moderate | Adjacent Ext. / Experimental |
| 25 | Web Dashboard Architecture | — | PROTOTYPE FIRST | Weak | Product Infra |
| 26 | Interactive Drill-Down UX | H (UI/UX) | PROPOSAL — pending sign-off | — | — |
| 27 | Executive Summary Mode | H (UI/UX) | PROTOTYPE FIRST, gated on 26 | — | Adjacent Ext. |
| 28 | Accessibility & i18n | — | Desk-audit fixes, in-scope now | — | — |
| 29 | Pluggable Metric Registry | — | PROTOTYPE FIRST | Moderate | Core Extension |
| 30 | Model-Agnostic Adapters | — | PROTOTYPE FIRST (HF before ONNX) | Low-Moderate | Core Extension |
| 31 | Audit-as-Code Profiles | — | PROTOTYPE FIRST | Low-Moderate | Additive |
| 32 | API-First Service Layer | — | PROPOSAL (research only) | — | — |
| 33 | Containerized Deployment | J (Deploy/Ops) | BUILD NOW (engine) / PROTOTYPE FIRST (inference+SaaS) | Weak | Product Infra |
| 34 | Performance Profiling | — | BUILD LATER (post-defense) | — | Product Infra |
| 35 | Data Privacy & Governance | — | 3-tier deployment mapping (proposal) | — | — |
| 36 | Regulatory Expansion Map | K (Biz/Reg) | BUILD LATER | Moderate | Core Extension |
| 37 | Pricing & Packaging | — | 3-tier model (proposal) | — | — |
| 38 | Licensing Strategy | — | Flag only — Aaradhya/Tisha decision | — | — |

---

## 2. Highest-Confidence, Ready-to-Build Findings

- **Track 36 — NYC LL144.** `disparate_impact_ratio` is arithmetically identical to LL144's mandated "impact ratio." Zero schema change, high source confidence. Gate: needs a `ReportContext.regulatory_map` → `regulatory_maps` (framework-keyed) shape decision first — a design call, not more research — and should land alongside Track 29's registry so the pattern isn't repeated ad hoc per framework.
- **Track 33 — container image weight.** Verified by grep: `torch`/`torchvision` are imported only in `scripts/run_fairface_inference.py`, never inside `src/bias_aperture/`. The engine can ship as a lean `python:3.11-slim` image with zero source changes. **BUILD NOW.** A second, optional `torch`-carrying inference image is separate and lower priority.
- **Track 34 — bootstrap CI is the real bottleneck**, not subgroup count. Called only 8x/run (4 metrics × 2 backends, whole-dataset row only); the serial resample loop (`statistics.py:191-207`) is what scales badly. Two NFR-preserving fixes identified: vectorized `scipy.stats.bootstrap`, and parallelizing the two independent backend calls. No legitimate path to reduce `n_resamples<1000` or `n<30` for speed — parallelization is the only sanctioned lever. Sequenced after capstone defense, before productization.

---

## 3. Time-Sensitive / Corrective Findings

- **Track 36:** Colorado SB 24-205 (the audit-mandate law the original brief assumed live) was **enjoined 2026-04-27** and repealed/replaced by SB 26-189 (2026-05-14, effective 2027-01-01, notice-only, no audit duty). Do not map against the original SB 24-205 text anywhere downstream.
- **Track 24:** `explainability.py`'s actual attribution vectors are demographic-dummy importances (race/gender/age one-hot via a `LogisticRegression` surrogate) — **not** the region/pixel-level lighting/pose/skin-tone proxy vectors the task brief assumed. That richer pipeline was scoped by Phase-1 Track 16 and never implemented (6 open items still logged, unresolved). This re-opens Track 16 rather than being a self-contained new feature.
- **Track 34:** a prior submission for this track contained a literal unexpanded shell placeholder instead of real content — flagged and resubmitted with corrected content. Worth a spot-check if any downstream track cited the first version.

---

## 4. Architectural / Coordination Conflicts (unresolved, need owner sign-off)

1. **Track 23 status discrepancy.** Track 29's memory marks Track 23 "dropped" (scope conflict with NOVELTY_INTEGRATION_DEFENSE.md), but Track 30's own task spec names Track 23 as a *prerequisite*. Surfaced, not resolved by either track.
2. **UX sequencing chain: 26 → 27 → 28.** Track 27 (Executive Summary) is explicitly built on top of Track 26 (Drill-Down UX) per its own task spec, but Track 26 was still `claimed`, not merged, when 27 ran — so 27 treated 26's conclusions as a *pending proposal*, not settled fact. Track 28's WCAG/i18n audit was also done without a wired report/generator.py source in-session — desk-audit only, against documented design. All three need a single Aaradhya/Tisha review pass together so the verdict vocabulary (non-verdict "X of Y flagged," never PASS/FAIL) and the badge palette stay consistent across tiers. Note: `report.html.j2` **already ships** a `badge-pass`/`badge-fail` pattern keyed to raw `p<0.05` — Track 26 is resolving a live pattern, not a hypothetical one.
3. **Track 24 vs Track 26 UX slot.** Track 24 recommends reserving a "Shared Drivers / Root Cause Themes" section slot in Track 26's report structure now, even though the clustering feature itself is parked pending Track 16.
4. **Track 29's registry pattern is a load-bearing dependency for multiple other tracks:** Track 26 owns the new report section for it; Tracks 31/32 need a metric-selection field (31 reserves `metrics.active` for this); Track 36's plugin/regulatory metrics must render regulatory-unmapped even when a profile's `regulatory_mapping` is set.
5. **Track 31's NFR guard-safety model** is the enforcement layer several others assume exists: tightening α/bootstrap-floor/n≥30 never needs approval; loosening any of them requires a logged `overrides[]` entry (justification + approver) enforced by a `profile_validator.py` importable by both `cli.py` (runtime) and Track 32's CI (commit-time gate). Track 31 flags that it does not have the source NFR doc text — only team-memory defaults (α=0.05, B≥1000) — so exact bound direction/floor need verification against the actual NFR docs before this ships.
6. **Track 32's API layer is designed as the sole backend** for Track 25's dashboard — explicitly not a parallel reimplementation path. `results.json` (raw metrics, for CI/CD gating) and `report` (rendered, for humans/dashboard) are deliberately split, mirroring the CLI's existing raw-vs-rendered separation.

---

## 5. Business-Track Dependencies (37, 38 → product tracks)

- **Track 37 (Pricing)** proposes a 3-tier ladder (free open-core CLI → paid hosted dashboard/API/CI-gate → custom-quote enterprise) modeled on Evidently/Arize/WhyLabs open-core patterns, with the enterprise tier anchored to Credo AI's sourced $30K–$150K+/yr. It explicitly could not map Tracks 33/35's scope into a tier (shared-memory unavailable at the time) — flagged for those owners to reconcile.
- **Track 38 (Licensing)** is a **flag, not a recommendation** — the repo is entirely MIT today, meaning (a) anyone can already fork the fairness engine into a competing hosted product, and (b) any future relicense is not retroactive (Terraform→OpenTofu precedent: already-public MIT code stays MIT forever). Two structurally different paths are laid out for Aaradhya/Tisha to choose between, not resolved here: GitLab-style single-repo directory split vs. Styra-style separate-repo commercial layer. If Track 37/33/25/32/21's commercial-tier features get written into the current MIT tree before this decision is made, that code is irrevocably MIT the moment it's pushed — this is the one finding across all 16 tracks with a real time cost to delaying.
- **Track 35 (Data Privacy)** feeds Track 33's SaaS-vs-on-prem sketch and Track 37/38's commercial-tier framing: 3-tier deployment model (air-gapped/on-prem for regulated clients; isolated single-tenant cloud for standard enterprise; multi-tenant SaaS restricted to non-PII/synthetic trials only). Key compliance flag: **race/ethnicity is GDPR Art.9 special-category data regardless of stated purpose** — "we're only using it to check for bias" does not itself create an Art.9(2) exemption; needs its own lawful basis. Gender/sex is *not* Art.9 (only sexual orientation is); age is ordinary Art.6. Could not cross-reference `docs/DATA_GOVERNANCE.md` in-session — flagged for the merger to diff.

---

## 6. Deferred / Parked Items (explicit, not silent)

- **Track 24 Variant 1** (true unsupervised clustering on region-level SHAP vectors) — parked behind Track 16 revival + empirical flagged-row count (cited HDBSCAN power threshold ~N=40–80; real BiasAperture flagged-row counts are unmeasured and plausibly below that).
- **Track 33's inference image + full SaaS multi-tenancy** — parked behind Track 30 (adapters) and Track 35 (governance) landing first.
- **Track 34's parallelization/vectorization fixes** — sequenced after capstone defense, before productization; not a current blocker.
- **Track 36's ISO/IEC 42001 clause numbers and financial-services (SR 11-7/ECOA) framing** — secondary-source-confirmed only; need primary-text/legal review before being shown to a buyer as more than illustrative.

---

## 7. Open Decisions Requiring Aaradhya/Tisha Sign-Off (consolidated)

1. Track 26/27/28 verdict vocabulary + badge palette — single joint review, not three independent ones.
2. Track 16 revival (blocks Track 24 Variant 1 entirely).
3. Track 23 status — dropped or prerequisite? (Track 29 vs Track 30 disagree.)
4. `ReportContext.regulatory_map` → multi-framework shape (blocks Track 36 shipping).
5. Track 31's exact NFR-001/002/003 bound values — verify against source NFR docs, not team memory.
6. Licensing mechanism (Track 38) — decide before any commercial-tier code (21/25/32/33/35) lands in the current MIT tree.

---

*Note on 22/23:* both remain in the parent epic's board but were excluded from this merge by design — `merge_results` only gathers `done`-state children. Track 22 (`task_2026-09-02_004`) is parked pending Tracks 25/36 landing first. Track 23 (`task_2026-09-02_005`) is marked dropped (scope conflict with NOVELTY_INTEGRATION_DEFENSE.md) — see conflict #1 above regarding Track 30's disagreement with that status.
