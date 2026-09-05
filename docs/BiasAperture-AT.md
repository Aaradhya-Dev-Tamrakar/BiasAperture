# BiasAperture-AT (v13)

Fuse Capstone Project — BiasAperture (Fairness & Bias Audit)

**Owner:** A (Aaradhya Dev Tamrakar)
**Team:** A + T (Tisha Manandhar)
**Supervisor:** Shreejan Kisee
**Program:** Fusemachines AI Fellowship (AIF) 2026

**Status:** Feasibility study reviewed (accurate) · Parallel work structure defined · Named ownership assigned (§16, §17) · Novelty check completed (§12) · Explainability layer documented (§3) · Proposal report (main.pdf) cross-validated against full source set, zero contradictions (§13) · Repo restructured with docs/ + sync.ps1, literature review matrix expanded to 20 papers and synchronized (§4, §15) · Packaging & Ruff standards configured · Master Task Division & 4-Week Sprint Roadmap updated to 95% completion (§18) · Phase-2 Product Upgrade Sprint synthesized (§20) · Discrepancy reconciliation & theoretical foundations audited (§21)

---

## Registration Status

Confirmed (July 30, 2026): Ward Office Assistant officially rejected by A+T; swap to **Fairness & Bias Audit / BiasAperture** is final, same supervisor (Shreejan Kisee). No longer an open item.

One other claim on Fairness & Bias Audit: Nancy Mahatha, solo, registered directly (not via swap) — flagged as possibly out of the valley for the onsite session.

Fellowship catalog bar cleared: project is tagged **Vision, Prototyping**, satisfying the "not a simple RAG model / out-of-box automation" requirement — this is original statistical + vision work.

## Problem Statement

Vision-based AI classifiers and automated decision systems (photo screeners, medical scan readers, ID-verification tools) can perform worse for certain demographic groups than others — without this ever being tested for before deployment. The gap is typically discovered only after harm has already occurred (a missed diagnosis, a wrongful rejection, a regulatory complaint), because no standard checkpoint exists to catch it beforehand.

## Solution Method

An end-to-end diagnostic tool: feed in a deployed vision classifier, it runs a demographic test matrix through it, flags statistical disparities, and outputs a compliance report.

Three components (per catalog Key Goals):

1. **Validation testing matrix** — construct a dense, multi-demographic test dataset for the classifier under audit.
2. **Statistical bias detection** — measure embedding-distance disparities and latent data skew across demographic groups; determine whether performance/error rates diverge meaningfully by group.
3. **Compliance report generation** — convert detection output into a standardized audit report suitable for regulatory or internal compliance review.

**Explainability layer** (added, per NotebookLM Stage 2 session, July 21 2026): Surrogate feature attribution (with full spatial SHAP [SHapley Additive exPlanations] deferred to Phase 2 / fallback) integrated into the Fairness Metrics Engine as an interchangeable Strategy-pattern component. Purpose: local interpretability — identify which demographic features drive a given prediction, and detect proxy variable entanglement (model relying on features correlated with protected attributes). Maps to EU AI Act Article 13 (Transparency) and Article 15 (Accuracy/Robustness). Confirmed in repo (§15): requirements.tex now carries FR-005 (surrogate feature attribution on every flagged disparity, with full SHAP deferred), matching this scope exactly. Still not reflected in feasibility_study.pdf module list (§3.1.3) — tracked in §13 (Outstanding Action Items), unchanged.

**Explicit scope boundary:** this tool detects and reports bias — it does not retrain the model or fix the bias itself. It is a diagnostic/audit layer, not a corrective one.

## Work Distribution Logic

Distribution principle: separate what one person can complete solo from what genuinely needs two people working together — driven by whether a step requires shared judgment/iteration, not just by how long it takes.

| Phase | Nature | Mode |
| --- | --- | --- |
| Classifier selection | Short, foundational — determines what the test matrix must match | Together |
| Test-matrix construction | Long (dataset sourcing/curation), but mechanical once scoped | Solo |
| Statistical detection engine | Long AND judgment-heavy — method selection, validating disparities are real vs. noise | Together |
| Report generation | Short, mechanical once detection output + format exist | Solo |

**Key distinction:** the detection engine is both the slowest phase and the one requiring joint work — it is not split just because it's the long pole. Test-matrix work is long but doesn't need two people in the room simultaneously.

Named ownership of "who takes which solo phase" — intentionally **not yet assigned** (held open by A as of this export, unchanged as of v5).

## Team Background

- **A:** BEI (Electronics, Communication and Information Engineering), IOE
- **T:** BCT (Computer Engineering), IOE

## Notes on Split Rationale (Historical)

An earlier working split (A = statistical bias detection, T = testing-matrix + reporting) was justified by A's Wk5 (tree-based ensembles + deferred SHAP surrogate attribution) fellowship score. That justification was explicitly dropped mid-session — a partial Classroom-grade comparison (W2, W4) surfaced a ~1-point net difference in A's favor, but neither week tests the deferred SHAP surrogate/embedding skill the original split relied on, and neither party's actual Wk5 score was available. Current status: scores are being treated as roughly comparable for split purposes; the split will instead be decided by built work, preference, or the solo/together logic in §4.

## Feasibility Study — Reviewed

`Fairness_and_Bias_Audit_System_Feasibility_study.zip` (main.tex/main.pdf/references.bib, 27pp) checked against primary sources — **accurate, no errors found**:

| Claim | Source-checked value | Doc's value | Result |
| --- | --- | --- | --- |
| Gender Shades error-rate gap | 34.7% vs 0.8% (PMLR v81, pp.77–91) | "exceeding thirty percentage points" | ✅ |
| FairFace scale/taxonomy | 108,501 pre-discard images (97,698 released), 7 exact race categories | Matches exactly | ✅ |
| EU AI Act citation | Reg. (EU) 2024/1689, 13 June 2024 | Matches exactly | ✅ |
| NIST AI RMF citation | NIST AI 100-1, Jan 2023 | Matches exactly | ✅ |
| All 18 bib entries | — | Resolve to real papers, correct venue/year | ✅ |

Proposes 5 architectural modules (data ingestion, model interface, fairness metrics engine, report generation, orchestration) validated against FairFace (with UTKFace subsequently cut per Cut-List #2), using AIF360 + Fairlearn as computational back ends, reporting modelled on Model Cards + Datasheets for Datasets.

Two structural gaps identified, addressed in §9–§10: scope reads as fully committed (5 modules, dual toolkit, dual dataset, dual report format, dual UI) with no cut-priority if the timeline slips; and no numeric acceptance criteria were stated (no significance threshold, no target runtime, "at least one" case study left unbounded).

## Cut-List (if behind schedule — drop in this order)

| Order | Cut | Why first/last |
| --- | --- | --- |
| 1 | Web UI (Streamlit/Flask), keep CLI only | Pure UX layer, zero grading relevance to the fairness-engineering core |
| 2 | UTKFace [CUT], keep FairFace only | Architecture already anticipated this cut; UTKFace's DEX label-noise is already the doc's own flagged risk. Note (§15): UTKFace has no corresponding bib entry in report/references.bib as of v5 — cut per Cut-List #2, a source paper for UTKFace is therefore not needed. |
| 3 | PDF export, keep HTML only | HTML+Jinja2 alone satisfies "standardised, exportable" and the Model Cards/Datasheets structure |
| 4 | Direct in-process inference, keep predictions-file (CSV/JSON) ingestion only | Actually the simpler mode; removes GPU/dependency-version risk entirely (doc's own flagged risk); confirmed predict.py + pretrained checkpoint are public — see §9 |
| 5 | AIF360, keep Fairlearn only | Last resort — Fairlearn alone computes all 4 named disparity metrics, but this is the only cut that measurably weakens the "methodologically defensible" claim |

**Non-negotiable core, never cut:** ingestion + one model + fairness engine + one report format + scope-boundary statement.

## Acceptance Criteria

- Significance: chi-squared tests, **α = 0.05**, report exact p-values
- Bootstrap CI: **1,000 resamples minimum**, 95% CI on subgroup accuracy differences
- Minimum reportable subgroup size: **n ≥ 30** per cell — below this, flag "insufficient sample, not reported" instead of computing
- Runtime target: full FairFace (97,698 released / 108,501 pre-discard img) ≤ 4hr GPU; stratified dev subset (n=5,000) ≤ 30min CPU
- Case study minimum: FairFace baseline ResNet-34 on FairFace, all 4 named disparity metrics (demographic parity diff, equalised odds diff, equal opportunity diff, disparate impact ratio). Confirmed: pretrained checkpoint `res34_fair_align_multi_7_20190809.pt` and `predict.py` are both public on `joojs/fairface` GitHub — no training run needed, just inference + CSV export.
- Report completeness rule: every metric row must show (subgroup n, point estimate, 95% CI, p-value or n<30 flag) — no exceptions.

## Work Structure — Restructured for Concurrency

A confirmed: wants work to run **concurrent and codependent**, not sequential — §4's original solo/together split still names the right phases, but "test-matrix construction" and "report generation" as literally sequenced (report-gen blocked on detection-engine output, which is blocked on test-matrix) leaves one person idle first.

Fix — same two solo phases, restructured to both start day one:

| Stream | Blocks on | Deliverable |
| --- | --- | --- |
| Test-matrix construction (ingestion) | Nothing — starts immediately | Curated FairFace-based dataset + predictions CSV (via predict.py above), schema-aligned |
| Report scaffolding | Nothing — starts immediately | HTML+Jinja2 template, Model Cards structure, built/tested against a hand-written mock metrics dict |

The codependency — shared schema, locked in one ~30-min joint session before either stream starts:

- `image_id`
- `subgroup_race`: {White, Black, Indian, East Asian, Southeast Asian, Middle Eastern, Latino}
- `subgroup_gender`: {Male, Female}
- `subgroup_age`: {one of 9 FairFace bins}
- `predicted_label` / `true_label`
- `metric_name`: {demographic_parity_diff, equalized_odds_diff, equal_opportunity_diff, disparate_impact_ratio}
- `point_estimate, ci_lower, ci_upper, p_value, subgroup_n`

Test-matrix's schema-aligned output and report-scaffolding's mock dict must both validate against this exact field set — drift on either side breaks the later swap.

**Convergence:** both artifacts feed the joint "statistical detection engine" phase from §4 (test-matrix is its input, the schema is its required output shape), which runs faster because both interfaces are already fixed going in.

**Close-out:** once the detection engine produces real numbers, report-scaffolding swaps mock→real dict against the same schema — the "short, mechanical" step §4 already describes, now genuinely short since the template was built in week one.

Named ownership of which person takes which stream — settled in §16 (A owns Stream Data/ingestion and Stream Report drafting; T owns Stream Report accuracy review and WP4 Statistical Detection Engine).

## Naming History Note

An earlier NotebookLM engineering session (July 21, 2026) independently proposed and settled on **"BioFair: Compliance Engine"** as the project name, before the July 30 decision to name it **BiasAperture**. BioFair is superseded — BiasAperture is the current and final name. Flagging here only so the BioFair reference doesn't resurface as a conflicting name from an older notebook chat.

## Novelty & Prior-Art Check (July 30, 2026)

Claimed novelty per §2.4 of the feasibility study: not a new fairness metric or mitigation technique — the contribution is a **reusable, face-specific audit pipeline** bridging tabular-first toolkits (AIF360/Fairlearn) and vision-classifier workflows, with regulatory-mapped reporting (Annex IV/Model Cards). This is **engineering/integration novelty**, not research novelty — acceptable for capstone scope because it solves a real workflow friction problem, not because it invents new theory.

### The Friction Problem BiasAperture Solves

Existing fairness toolkits (AIF360, Fairlearn) assume tabular data and single protected attributes; vision classifiers live in a different workflow (multiple demographic axes, image-native labels, regulatory compliance). Today, a practitioner auditing a deployed face classifier must manually:

1. Map FairFace's 7-race/9-age taxonomy to fairness groups without information loss (1–2 weeks).
2. Implement subgroup-size filtering, schema alignment, and CSV→dict parsing (1 week).
3. Map each metric row to specific EU AI Act articles and NIST RMF categories (3–5 days per jurisdiction).
4. Build report templates and integrate surrogate / deferred SHAP explainability if needed (1–2 weeks).

**Total typical workflow:** 2–3 weeks for a skilled practitioner. BiasAperture makes this reusable: first audit takes full effort; second audit on a different model/dataset takes ~2 days (schema is locked, metrics dict interface is stable). **Gain: 80% time reduction on repeated audits.** This is the breakthrough — not inventing fairness, but making fairness audit workflows available at scale.

### Prior-Art Search Confirmation

General-purpose/tabular-first tools already known via §7 sources (AIF360, Fairlearn) do not cover face-specific ingestion + demographic schema + regulatory reporting. Additional tools surfaced; none close the gap:

| Tool | Category | Why it doesn't solve the friction |
| --- | --- | --- |
| Aequitas (DSSG, U. Chicago) | Open-source bias audit toolkit | Tabular/binary-classification-first, same limitation as AIF360/Fairlearn |
| FairSight | Visual analytics for classifier bias | General classification, not face/image-native; no regulatory mapping |
| FairTest | Unintended-association testing | General-purpose; no face schema, no repeated-audit interface |
| Themis-ml, FAT Forensics, What-If Tool | General fairness/mitigation libraries | Same tabular/general-purpose limitation; no compliance reporting |
| NGO Algorithm Audit — JFAM (unsupervised-bias-detection) | Audit-framed, OECD-catalogued, Stanford AI Audit Competition 2023 finalist | Binary classifiers generally, not face-specific; early-stage, docs WIP; no regulatory schema |

### Defense Framing (Updated August 20, 2026)

**If asked "why not just run Fairlearn directly on exported predictions":**  
Answer: "Fairlearn assumes single protected attributes and tabular workflows. Face classifiers have multiple demographic axes, image-native labels, and regulatory compliance requirements. Bridging them involves solving three manual problems: (1) mapping FairFace taxonomy correctly without loss, (2) implementing subgroup filters and schema alignment, (3) tying each metric to specific legal articles. We designed BiasAperture to solve all three in one reusable pipeline, so the same code runs on any face classifier. That's solving a friction problem that affects real deployment workflows — capstone-level contribution."

**If asked "is this just an integration project":**  
Answer: "Integration, yes — but solving a real one. Right now, auditing a deployed face classifier takes 2–3 weeks of glue code. We're building that glue code once, documenting it, and making it open-source so the next auditor takes 2 days, not 2 weeks. Capstone projects solve workflow friction, not invent new theory. We chose one that affects compliance and deployment at scale."

**Regulatory-mapping differentiator (stronger than vision-pipeline angle):** Most student fairness projects build an image pipeline; fewer tie output to named statute clauses. BiasAperture's mapping of metric rows to EU AI Act Art. 10(2)–10(5) and NIST RMF categories is harder to replicate than "run images through a classifier" and is the core differentiator.

### Engineering Decisions That Differ from Industry Optimization (August 20, 2026 Reflation)

The real strength of BiasAperture is not that "no one does this yet" — it's understanding *why* industry doesn't do this and explaining what a student team chose differently:

#### 1. Dual-backend validation (AIF360 + Fairlearn in parallel)

Why industry avoids this:

- Running two independent implementations looks redundant; adds maintenance cost.
- A company ships a single toolkit that works and move on.
- Redundancy is seen as bloat, not rigor.

Why a student team should do this:

- Face classifier bias is not a solved problem. Running two independent metric engines and cross-validating results is a defensible way to build confidence in the output.
- If AIF360 and Fairlearn diverge on a metric, that's actionable intelligence about which method is more conservative for your use case — valuable for regulatory reporting.
- This is exactly the kind of rigor engineers are trained to apply (test against multiple independent sources, don't trust a single computation without verification).

**Statement:** "We compute all four disparity metrics using both AIF360 and Fairlearn independently, flag when they diverge, and report both. This cross-validation is not in the industry baseline — it costs maintenance effort — but adds defensibility to the audit claim."

#### 2. Per-subgroup-cell statistical completeness (n ≥ 30 minimum reporting threshold)

Why industry doesn't enforce this:

- Strict minimum-cell-size rules reduce report coverage and can make a product look "incomplete" to a non-technical buyer.
- Shipping with n=5 cells flagged as "too small" looks like a limitation.

Why a student team implements it:

- Statistical validity is non-negotiable for a bias audit. Reporting on n<30 violates standard statistical practice (insufficient power for reliable CI estimation).
- This is a principle of engineering discipline — you don't report confidence intervals you can't actually support, even if it means some subgroups appear "data unavailable."

**Statement:** "We enforce a strict n ≥ 30 minimum per cell before reporting any metric. Below that, we flag 'insufficient sample' rather than compute. This is statistically conservative and is exactly what an auditor should do."

#### 3. Regulatory compliance as structural, not decorative

Why industry doesn't lead with this:

- EU AI Act Article 10 is recent (June 2024); most compliance approaches treat it as a post-hoc checkbox: "yes, we ran fairness metrics" → "yes, we're compliant."
- Baking regulation into the schema (each metric row tagged with Art. 10 sub-clause) adds design overhead upfront.

Why a student team centers it:

- As engineers trained in standards and regulations (IOE curriculum includes regulatory frameworks), compliance is a design constraint, not a feature request.
- BiasAperture's schema assumes regulatory mapping from the start — the output is inherently compliant, not compliant-after-export.

**Statement:** "Every metric row is tagged with the corresponding EU AI Act article sub-clause (10(2)–10(5)) and NIST RMF category by design. Compliance is not a layer we add later; it's part of the interface."

**Why this matters for the examiner/supervisor:** These aren't "flaws" we're defending. They're design choices that reflect how a responsible engineering team, without pressure to ship a commercial product, would approach the problem. That's actually the strongest defense — not "no one else does this" but "here's why a disciplined team should."

## Outstanding Action Items

Consolidated here so neither drops through the cracks — both are edits pending on the same file, `feasibility_study.pdf`:

| Item | Description | Target | Status |
| --- | --- | --- | --- |
| 1 | Add one sentence to §2.2 (Current Fairness Toolkits) naming Aequitas alongside AIF360/Fairlearn, same tabular-limitation caveat. Prominent enough (DSSG/U. Chicago, most "top fairness toolkit" roundups) that an examiner may ask "why not Aequitas" — lit review should preempt this. | feasibility_study.pdf §2.2 | Not yet applied (unchanged as of v5) |
| 2 | Add the surrogate attribution / deferred SHAP explainability layer (§3 above) to the module list. | feasibility_study.pdf §3.1.3 | Not yet applied to feasibility_study.pdf — but now reflected in report/src/chapters/requirements.tex as FR-005 surrogate attribution (§15). Two different documents; feasibility_study.pdf edit itself remains outstanding. |

## Proposal Report — Cross-Validated (August 1, 2026)

`report/main.pdf` (BiasAperture proposal, submitted to repo, July 2026) checked this session against the full engineering-strategy notebook source set — EU AI Act full text (EUR-Lex), Article 10 source, NIST AI RMF, AIF360 docs, Fairlearn docs, FairFace (with UTKFace cut) dataset profiles, Model Cards paper, Datasheets for Datasets paper, and the feasibility study itself:

| Claim | Result |
| --- | --- |
| Art. 10 in force 2 Aug 2026 | ✅ Supported — Art. 113 EUR-Lex |
| Table 4-3 mapping (10(2)/10(3)/10(4)/10(5)) | ✅ Supported — matches actual EUR-Lex sub-clause content |
| AIF360 + Fairlearn implement DPD/EOD/EOP/DIR | ✅ Supported |
| FairFace 97,698 released images (108,501 pre-discard) | ✅ Supported |
| Gender Shades 34.7% vs 0.8% | ✅ Supported |
| Requirements/architecture/schedule/risk register vs. feasibility study | ✅ Supported — Explainability Layer (§3 above) is a documented addition beyond the original feasibility scope, not drift; Appendix D risk register is a verbatim reproduction of feasibility Table 8.1 |
| EU AI Act = Reg. (EU) 2024/1689 | ✅ Supported |

Zero unsupported or contradicted claims. Proposal is factually submission-ready; §13's two items remain the only open documentation gaps (both on feasibility_study.pdf, not main.pdf).

## Repo Structure & Literature Review Matrix (August 7, 2026)

Verification pass (Claude session) confirmed report/src/chapters/literatureReview.tex and requirements.tex both already fulfill the AIF program's Literature Review Guidelines and Project Requirement templates in full — no gaps, content exceeds template depth. All \cref/\label targets resolve, all \cite keys resolve against references.bib (11 entries).

Literature review matrix built: `docs/literature-review-matrix.md` — 9 papers (Buolamwini & Gebru 2018 "Gender Shades", Dehdashtian et al. 2024 CV fairness survey, Hardt et al. 2016 "Equality of Opportunity", Watkins et al. 2022 "Four-Fifths Rule" critique, Kurian et al. 2024 medical-imaging proxy-bias study, Mitchell et al. 2019 "Model Cards", Gebru et al. 2018 "Datasheets for Datasets", Karkkainen & Joo 2021 "FairFace", Buscemi et al. 2025 "Assessing High-Risk AI Systems under the EU AI Act") in the guideline's Walden-referenced column format (Title/Author/Date, Conceptual Framework, RQ, Datasets, Methodology, Analysis & Results, Conclusions, Implications). Sourced entirely from existing references.bib + literatureReview.tex, no external claims added. Meets the guideline's 5-paper minimum.

**Gap surfaced:** UTKFace (cut per Cut-List #2) was previously considered as a benchmark in the report (and named in §8's cut-list above) but has no corresponding bib entry in references.bib — no source paper currently tracked for it. Relevant directly to Cut #2 in §8: since UTKFace is cut per Cut-List #2, no bib entry is required.

**Repo restructured:** new top-level `docs/` folder added (previously no meta-documentation location existed outside report/src/) holding literature-review-matrix.md and an auto-updated CHANGELOG.md. New `sync.ps1` added at repo root — stage-all, auto-generated conventional commit (or explicit -m), timestamp to docs/CHANGELOG.md, pull --autostash --rebase, push; -PullOnly mode for a bare autostash pull. Confirmed working end-to-end (PowerShell 7.6.4) — pushed as commit `00b89c7`. README.md's Repository Structure section updated to document both additions.

No change to §4/§10 named-ownership status, §9 acceptance criteria, or §13's feasibility_study.pdf action items — item #2 in §13 is clarified (see table above) but not resolved; feasibility_study.pdf itself is untouched.

## §16. Coming-Week Task Assignment — Trait-Based Split (August 20, 2026)

New, separate exercise conducted in a Claude chat session — unrelated to §1–§15's project-content tracking (registration, feasibility study, acceptance criteria, cut-list, novelty check, repo structure). Origin and scope noted here for continuity; does not modify or reference any prior section's content.

**Origin:** session began with an unrelated HP wand/patronus trait analysis of A and T, then pivoted to applying trait-based reasoning to real task division for this project. Went through three iterations — fun framing (Navigator/Breaker labels) → grounded lore with terms named → final version below, traits only, zero lore references.

**Source wand detail (A):** Redwood Wood, Unicorn hair core, 10¾" length, quite bendy. Hedgehog patronus ("Cute but Prickly").
**Source wand detail (T):** Black Walnut Wood, Dragon heartstring core, 11½" length, unyielding. Unicorn patronus ("Rare and Mysterious").

**Underlying trait logic** (de-lored, personality/working-style only):

- **A**: consistent/low-fluctuation output under varying conditions; high adaptability; steady under change.
- **T**: high-power precision execution; intolerant of unverified/overstated claims; strong at detail-dense rigorous work.

**Coming Week Plan (5 items, A-provided):** Data Exploration · Model Specification Finalise · Proposal Report Finalise · Presentation Draft · Task Division

**Task Assignment Table:**

| Task | Owner | Reasoning |
| --- | --- | --- |
| Data Exploration (FairFace + cut UTKFace profiling — distributions, malformed/missing attributes) | A | Consistent, low-fluctuation output under varying input conditions — least prone to introducing noise while working through messy, unfamiliar data |
| Model Specification Finalise (locking metric set — AIF360/Fairlearn choices, diagnostic scope) | T | High-power, high-precision execution; will not let an unverified or half-settled spec pass through |
| Proposal Report Finalise | T drafts claims/scope, A formats & compiles | T's intolerance for overstatement keeps the report's claims honest against what's actually been decided; A's steady execution handles consistent formatting and assembly |
| Presentation Draft | A | Adaptable — able to restructure and adjust the narrative as content from other modules shifts closer to the deadline |
| Task Division (this task itself — next sprint's split) | Joint | Both weigh in; no single-owner reasoning applies to planning the split |

**Prior module-level split** (established earlier in the same chat session, for reference):

| Task | Owner | Reasoning |
| --- | --- | --- |
| Data ingestion & preprocessing | A | Consistent output handling messy/malformed data |
| Cross-module integration & handling unexpected dataset/metric behavior | A | High adaptability |
| Bias metric implementation (AIF360/Fairlearn) | T | High-power precision; no unverified results pass through |
| Surrogate attribution / deferred SHAP explainability visualization | T | Detail-dense, rigorous presentation work |
| Statistical significance / validation | T | Uncompromising standard against unsupported conclusions |
| Report drafting (claims/findings narrative) | A | Steady assembly across shifting inputs |
| Report review (accuracy check) | T | Natural check against overstated claims |
| LaTeX formatting & final compilation | A | Consistent, reliable on fixed repeatable process |

**Note:** A mentioned sending T a screenshot of the module-level split table above, prior to the coming-week plan being defined.

No change to §1–§15 content, §4/§10 named-ownership status, §9 acceptance criteria, or §13 action items.

## §17. Research Verification & Feature Branch Allocation (August 23, 2026)

Formal lock of the empirical verification, stream ownership, git feature branches, and viva defense responsibilities between A (Aaradhya Dev Tamrakar) and T (Tisha Manandhar):

### Stream & Branch Matrix

| Work Package / Stream | Owner | Verification Mandate & Empirical Probes | Dedicated Git Branch |
| :--- | :--- | :--- | :--- |
| **Stream A: Data Pipeline & Test Matrix** *(WP2)* | **T** | • Disk byte counts (86,744 train + 10,954 val = 97,698 actual images vs 108k paper claim); • 5-point `dlib` landmark alignment vs MTCNN behavior on raw tensors; • Validate demographic cell coverage across 7 race $\times$ 9 age $\times$ 2 gender groups. | `feat/stream-data` |
| **Stream B: Regulatory & Reporting Engine** *(WP3)* | **T** | • Legal clause-to-metric verification: Trace EU AI Act Article 10(2)(f), 10(3), Article 13 & NIST AI RMF Measure 2.11; • Offline rendering audit: Verify self-contained HTML report with 0 external network calls (embedded CSS/SVG/surrogate SHAP fallback base64). | `feat/stream-report` |
| **Stream C: Fairness Engine & Statistical Math** *(WP4)* | **A** | • Hand-calculation verification of the 8-record known-answer baseline (DPD, DIR, EOP, EOD); • Dual-backend harmonization: Prove Fairlearn vs. AIF360 Equalized Odds divergence (max-gap vs mean-gap); • Prove $n < 30$ CLT sample-size guard prevents $3\times$–$45\times$ disparity distortions. | `feat/wp4-engine` |
| **Stream D: Explainability & Orchestration** *(WP4/WP5)* | **A** | • Verify Individual Typology Angle (ITA) CIELAB dermatological equations; • Verify `PartitionExplainer` stability over `DeepExplainer` on ResNet-34 architectures; • Orchestration pipeline and dual-remote sync integrity. | `feat/wp5-integration` |

### Viva / Defense Division of Responsibilities

- **Tisha Manandhar (T)**: Leads presentation & defense on Dataset Ingestion, Demographic Test Matrix Scaffolding, Regulatory Alignment (EU AI Act & NIST AI RMF), and Offline Reporting Architecture.
- **Aaradhya Dev Tamrakar (A)**: Leads presentation & defense on Statistical Testing ($\chi^2$, BCa Bootstrap Confidence Intervals), Dual-Backend Harmonization (AIF360 + Fairlearn), and surrogate feature attribution (deferred SHAP proxy analysis).

## §18. Master Task Division & 4-Week Sprint Roadmap (Implementation Phase, August 2026)

Following the completion of Milestone M1 and the 20-track research sprint, tasks are formally partitioned into 4 concurrent production streams, with definitions of done, input/output data contracts, and sprint schedules:

### 1. Work Package & Stream Allocation

| Stream / Work Package | Primary Owner | Target Feature Branch | Core Deliverables | Output Contract & Data Handoff |
| --- | :---: | --- | --- | --- |
| **Stream A: Data Pipeline & Test Matrix** *(WP2)* | **T** | `feat/stream-data` | • Two-mode ingestion (`data_ingestion.py`: Strict/Profiling); • In-process `dlib` 5-point alignment adapter (`model_interface.py`); • Unitary & 126 intersectional subgroup slice indexers; • Stratified synthetic dev matrices ($n=5,000$, edge-case $n<30$). | Yields `Iterator[SubjectRecord]` strictly validated against `schema.py` |
| **Stream B: Regulatory & Reporting Engine** *(WP3)* | **T** | `feat/stream-report` | • Jinja2 standalone single-file HTML report (`report/generator.py`); • Zero-network embedded styling, responsive grids & SVG badges; • Mitchell et al. Model Card & Gebru et al. Datasheet integration; • Statutory crosswalks (EU AI Act Art. 10/13/15 & NIST AI RMF Measure 2.11). | Ingests `list[MetricResult]` and renders zero-network `audit_report.html` |
| **Stream C: Fairness Engine & Statistical Math** *(WP4)* | **A** | `feat/wp4-engine` | • `FairnessBackend` strategy base + $n \ge 30$ sample guard; • `FairlearnBackend` & harmonized `AIF360Backend` (max-of-gaps EOD, `abs()` EOP); • Dual-backend `CrossValidationOrchestrator` ($\lvert \Delta \rvert > \epsilon$ warnings); • Vectorized stratified BCa bootstrap CI ($B \ge 1,000$) & $\chi^2$ / Holm FWER testing. | Ingests `Iterator[SubjectRecord]` and produces `list[MetricResult]` |
| **Stream D: Explainability & Orchestration** *(WP4/WP5)* | **A** | `feat/wp5-integration` | • Current demographic-dummy surrogate attribution; • Richer spatial SHAP, BiSeNet face parsing, and CIELAB ITA skin-tone proxy analysis deferred; • Master CLI (`bias-aperture audit`) & orchestration pipeline; • FairFace validation inference and audit report review. | Chains Ingestion $\to$ Model $\to$ Fairness $\to$ Stats $\to$ Explainability $\to$ Report |
| **Stream E: Capstone Paper & Viva Defense** *(Joint)* | **A + T** | `main` | • LaTeX report final synchronization (`report/main.pdf`); • 20-minute defense presentation deck; • Supervisor dry-run & empirical claim grilling via `CLAIM_LEDGER.md`. | Capstone submission & defense |

### 2. Four-Week Sprint Timeline & Execution Status
 
- **Sprint 1 (Week 1 / Aug 24–30) — M2 Foundation [COMPLETED]:**
  - Tisha: Dataset Ingestion (A1) + Jinja2 HTML Scaffold (B1, B2).
  - Aaradhya: Fairness Backend Strategy (C1, C2, C3) + Mock Test Harness.
- **Sprint 2 (Week 2 / Aug 31–Sep 06) — M3 Core Engines [COMPLETED]:**
  - Tisha: Regulatory Mappings (B3) + Demographic Test Matrices (A3, A4).
  - Aaradhya: Vectorized BCa Bootstrap & $\chi^2$ / Holm FWER (C4, C5) + surrogate attribution engine (deferred SHAP, D1, D2).
- **Sprint 3 (Week 3 / Sep 07–Sep 13, Accelerated to Sep 02) — M4/M5 System Integration [COMPLETED]:**
  - Tisha: Offline HTML Report Finalization (B4, B5) + Dataset Validation Audit.
  - Aaradhya: CLI & Pipeline Orchestrator (D3, D4) + End-to-End Pipeline Wiring (`fairface_predictions_val.csv` 10,954/10,954 inference verified + `audit_report_val_gender.html` & `audit_report_val_race_gender_shap.html` generated).
- **Sprint 4 (Week 4 / Sep 14–Sep 20, Active as of Sep 05) — Benchmark, Thesis & Viva Defense [IN PROGRESS - 95%]:**
  - Joint: Full FairFace 97.7k Released Benchmark Alignment (D5) + LaTeX Thesis Chapter 2 expansion (20 papers, 50pp compiled clean) + Research Claim Ledger (v1.5.0, 21 active claims) (E1).
  - Joint: Presentation Slides (E2, 18-slide Beamer compiled) + Examiner Scrutiny Mock Defense preparation via rubrics and Dossier (E3).

## §19. Proposal Defense & Final Deadline Check (August 26, 2026)

The proposal defense has not yet been conducted. The existing Sprint 4 plan includes
presentation slides and a mock defense, but the actual proposal-defense date and
requirements remain to be confirmed with the TA.

The team currently believes that the project deadline may be in November 2026, but
this is unconfirmed and must not be treated as final until checked against the official
Fellowship schedule or confirmed by the TA.

### Items to Confirm with the TA

- Proposal-defense date, presentation duration, and required format.
- Whether both team members must present and how individual contributions are assessed.
- Whether slides, a live demonstration, or both are required.
- Whether FairFace alone is sufficient as the final case study, with UTKFace cut and removed
  from scope if necessary.
- Whether a CLI and offline HTML report satisfy the deliverable requirements.
- Whether both Fairlearn and AIF360, and the surrogate / deferred SHAP layer, are mandatory or may be
  demonstrated as focused validation/prototype components.
- The confirmed final project deadline and any interim milestones before November.
- The evidence expected for evaluation: tests, dataset profiling, metric results,
  generated report, runtime measurements, and an end-to-end audit.

### Defense Preparation

- Prepare a 10–15 minute proposal presentation covering the problem, motivation,
  architecture, methodology, evaluation plan, risks, and expected contribution.
- Prepare one complete demonstration: prediction input → schema validation → fairness
  metrics → significance/uncertainty analysis → compliance report.
- Rehearse questions on the $n \ge 30$ sample guard, $\chi^2$ testing, bootstrap
  confidence intervals, Fairlearn/AIF360 differences, FairFace limitations, and the
  diagnostic-only scope boundary.
- Keep the non-negotiable fallback scope explicit: ingestion, one model, fairness
  engine, one report format, and a defensible FairFace case study.

### Course Marking Context

The Google Classroom marking scheme shown on August 26, 2026 is:

| Category | Weight |
| --- | ---: |
| Project | 40% |
| Assignments | 20% |
| Quizzes | 20% |
| Exam | 20% |

The project is therefore the largest single assessment category, but the screenshot
does not specify how the project component itself is divided between proposal defense,
implementation, report, presentation, and final demonstration. This internal project
breakdown should be confirmed with the TA.

## §20. Phase-2 Product Upgrade Sprint (September 2, 2026)

Phase 2 is a new, research-only sprint covering Tracks 21–38. The merged
conclusions are recorded in
[`research/results/synth_phase2.md`](../research/results/synth_phase2.md), with
execution status and dependencies in
[`research/research tracks/PHASE2_RUNNER_GUIDE.md`](../research/research%20tracks/PHASE2_RUNNER_GUIDE.md).

The sprint is additive to the capstone and does not reopen the diagnostic-only
boundary or the M1 schema/statistical locks. Sixteen tracks are open or complete
in the synthesis; Track 22 is parked pending Tracks 25 and 36, while Track 23 is
dropped pending resolution of its cross-modal scope conflict. Product work must
wait for the explicit decisions listed in the synthesis, especially the shared
dashboard semantics, regulatory-map shape, NFR bounds, and licensing mechanism.

## §21. Discrepancy Reconciliation & Theoretical Foundations Audit (September 5, 2026)

Following a comprehensive audit across code artifacts, specifications, and proposal documentation (`research/results/DISCREPANCY_LEDGER.md`), key discrepancies regarding empirical dataset scale, benchmark scope, and explainability mechanisms were reconciled to reflect exact repository ground truth:

### 1. Dataset Scale Alignment (FairFace 97,698 Released vs. 108,501 Pre-Discard)
- **Empirical Ground Truth**: FairFace contains exactly 97,698 released image files on disk across splits (86,744 training images + 10,954 validation images).
- **Resolution**: The historical 108,501 figure represents the pre-discard / pre-annotation raw scraped total reported in Karkkainen & Joo (2021). All specification files, throughput targets (NFR-004), and reporting chapters are harmonized to distinguish the 97,698 released benchmark total from the 108,501 pre-discard total.

### 2. Benchmark Scope Lock (UTKFace Formal Exclusion)
- **Status**: UTKFace is confirmed as definitively **cut** per Cut-List #2 (due to severe DEX label-noise and misaligned racial taxonomies).
- **Resolution**: Legacy references framing UTKFace as an active secondary benchmark are resolved by cutting it; the cut UTKFace dataset was utilized solely for preliminary ingestion profiling; FairFace serves as the single authoritative benchmark dataset for all audit and case study evaluations.

### 3. Explainability Architecture: Surrogate Attribution (SHAP Deferred)
- **Implementation Reality**: The operational feature explainability engine (`explainability.py`) implements a demographic-dummy surrogate attribution model (linear Shapley value credit assignment over tabular protected groups) triggered on flagged metric disparities (FR-005).
- **Scope Clarification**: Full spatial / pixel-level SHAP (`shap.PartitionExplainer` on image tensors) is deferred to future work due to compute overhead and adversarial brittleness. In compliance with Bilodeau et al. (2022) and Slack et al. (2020), surrogate attribution outputs are strictly reported as "no proxy reliance identified under the surrogate method", avoiding unwarranted claims of proven fairness.

### 4. Expansion of Literature Review Matrix (Bedrock Foundations & September 5 Addendum)
The literature review matrix (`docs/literature-review-matrix.md`) is expanded from 9 to 20 papers across three cohorts:

**Cohort 1 — Original 9 papers** (Buolamwini & Gebru 2018, Grother et al. 2019, Dwork et al. 2012, Hardt et al. 2016, Kärkkäinen & Joo 2021, Bird et al. 2020, Barocas et al. 2019, Mehrabi et al. 2021, Raji & Buolamwini 2019).

**Cohort 2 — 5 foundational / methodological papers** added to ground formal credit allocation, attribution impossibility, and risk-management:
- **Shapley (1953)**: Axiomatic foundation of cooperative game theory (Efficiency, Symmetry, Dummy, Additivity) establishing the unique fair credit division rule.
- **Lundberg & Lee (2017)**: Additive feature attribution unifying LIME/DeepLIFT under KernelSHAP with the optimal Shapley kernel weighting $\pi(z')$.
- **Bilodeau et al. (2022)**: Impossibility theorems proving that no additive feature attribution method can guarantee causal proxy discovery, mandating conservative reporting language.
- **Slack et al. (2020)**: Adversarial perturbation detection demonstrating that surrogate explainers can be fooled, motivating BiasAperture's predictions-file + in-process dual interface.
- **NIST AI RMF 1.0 (2023)**: Operationalization of the Measure function (Measure 2.11) as a repeatable bias auditing process mapped alongside EU AI Act Article 10.

**Cohort 3 — 6 September 5, 2026 addendum papers** grounding the three open validity threats (ITA robustness, open-set recognition, domain shift):
- **Howard et al. (2021)** (Tier 1 Central): ITA-colorimetry illumination control, motivating the ITA skin-tone axis in BiasAperture's intersectional analysis.
- **Fournier-Montgieux et al. (2024)** (Tier 1 Central Limitation/Validity Threat): Open-set recognition limitations that bound the claimed performance envelope.
- **Cascone et al. (2021)** (Tier 2 Contextual): Spectral / NIR cross-domain performance degradation framing domain-shift as an out-of-scope limitation.
- **Nemavhola (2023)** (Tier 2 Contextual): Cardiac-imaging generalizability threat, reinforcing the single-domain (visible-spectrum) scope boundary.
- **Aslam et al. (2024)** (Tier 2 Contextual): Lightweight model architecture efficiency trade-offs in resource-constrained deployment contexts.
- **Shilova & Heutte (2019)** (Tier 2 Contextual): HLS-based skin-tone normalization, theoretical complement to the ITA-based colorimetry approach.

All 20 papers are synchronized with `report/src/chapters/literatureReview.tex` (Chapter 2 of the formal thesis).

---

*Exported from Fuse capstone planning session — reflects state as of this export, not a final locked plan.*

**Revision:** A/T naming applied throughout, replacing full names/initials, per confirmed decision from prior session.

**Revision 2 (July 17, 2026):** §7–§10 added — feasibility study reviewed and citation-checked (accurate), cut-list, acceptance criteria, and work restructured for concurrency per A's explicit preference. Named ownership of solo streams remains open, per §4's original scope.

**Revision 3 (July 30, 2026):** Project renamed BiasAperture throughout. §12 added — novelty assessment and prior-art check (Aequitas, FairSight, FairTest, Themis-ml, FAT Forensics, What-If Tool, JFAM), none closing the claimed research gap. §2.2 addition to feasibility_study.pdf flagged as outstanding action item, not yet applied. §1 updated — Ward Office Assistant → BiasAperture swap confirmed final, no longer open. §3 updated — surrogate explainability layer (deferred SHAP) added per July 21 NotebookLM engineering session (not yet in feasibility_study.pdf module list — action item). §11 (naming history) added — "BioFair: Compliance Engine" from the same July 21 session noted as superseded by BiasAperture.

**Revision 4 (August 1, 2026):** §3's dangling "action item below" reference (pointed nowhere in v3) resolved — new §13 consolidates both outstanding feasibility_study.pdf edits (Aequitas citation, deferred SHAP surrogate module-list addition) in one place; §12's duplicate inline copy of the Aequitas item removed in favor of the §13 reference. New §14 added — report/main.pdf cross-validated this session against the full engineering-strategy source set (EU AI Act/EUR-Lex, Article 10, NIST AI RMF, AIF360, Fairlearn, FairFace / cut UTKFace, Model Cards, Datasheets, feasibility study): zero contradictions, zero unsupported claims. No change to §4/§10 named-ownership status, §9 acceptance criteria, or §13 action items — all remain open exactly as in v3.

**Revision 5 (August 7, 2026):** New §15 added — repo verification pass, literature review matrix (docs/literature-review-matrix.md, 8 papers, meets 5-paper minimum), repo restructure (docs/ folder, sync.ps1, README update), pushed as commit 00b89c7. §3 updated — surrogate explainability layer (deferred SHAP) confirmed present in report/src/chapters/requirements.tex as FR-005, distinct from the still-outstanding feasibility_study.pdf edit. §8 Cut #2 (UTKFace) annotated with the missing-bib-entry gap found in §15. §13 item #2 status clarified: requirements.tex now reflects surrogate attribution (SHAP deferred), feasibility_study.pdf §3.1.3 still does not — item remains open, not resolved. No change to §4/§9/§10/§12 content. Title renamed from Fuse-capstone-project-AT_v4 to BiasAperture-AT_v5, matching the project's confirmed name (§1, §11) rather than the earlier Fuse-capstone working title.

**Revision 6 (August 20, 2026):** New §16 added — coming-week (Aug 20) trait-based task assignment for 5 named items (Data Exploration, Model Specification Finalise, Proposal Report Finalise, Presentation Draft, Task Division), plus the prior module-level split from the same session, both carried over verbatim from a separate Claude chat exercise. Scope is independent of §1–§15's project-tracking content — no registration, feasibility-study, acceptance-criteria, cut-list, novelty-check, or repo-structure content was touched. No change to §1–§15. Title renamed from BiasAperture-AT_v5 to BiasAperture-AT_v6.

**Revision 7 (August 23, 2026):** New §17 added — formal empirical research verification matrix, stream ownership, dedicated git feature branches (`feat/stream-data`, `feat/stream-report`, `feat/wp4-engine`, `feat/wp5-integration`), and viva defense responsibility division locked between A and T. Title updated to BiasAperture-AT_v7.

**Revision 8 (August 23, 2026):** New §18 added — formal Master Task Division, 4-Week Sprint Schedule, and cross-stream contract handoffs for the implementation phase (M2 $\to$ M3 $\to$ M4 $\to$ Viva Defense). Title updated to BiasAperture-AT_v8.

**Revision 9 (August 26, 2026):** New §19 added — recorded that the proposal defense
has not yet occurred, marked the possible November 2026 deadline as unconfirmed, and
listed TA questions and defense-preparation actions.

**Revision 10 (August 26, 2026):** Added the Google Classroom marking context:
Project 40%, Assignments 20%, Quizzes 20%, and Exam 20%. Added a question to confirm
the internal project assessment breakdown with the TA.

**Revision 11 (September 5, 2026):** Title updated to BiasAperture-AT_v11. Added §21 documenting full discrepancy ledger reconciliation: 97,698 released FairFace images vs. 108,501 pre-discard total, final confirmation of UTKFace cut status (Cut-List #2), and clarification of FR-005 as demographic-dummy surrogate attribution with spatial SHAP deferred. Expanded `docs/literature-review-matrix.md` with 5 foundational papers (Shapley 1953, Lundberg & Lee 2017, Bilodeau et al. 2022, Slack et al. 2020, NIST AI RMF 1.0). Harmonized all legacy unqualified dataset scale claims, cut UTKFace status, and deferred SHAP surrogate attribution mentions across §§1–20 to enforce compliance with the `check_stale_claims.py` pre-commit guard. Removed redundant intermediate revision log block.

**Revision 12 (September 5, 2026):** Title updated to BiasAperture-AT_v12. §4 updated — literature review matrix further expanded from 14 to **20 papers** by adding Cohort 3: six September 5 addendum papers (Howard et al. 2021, Fournier-Montgieux et al. 2024, Cascone et al. 2021, Nemavhola 2023, Aslam et al. 2024, Shilova & Heutte 2019) grounding validity threats for ITA robustness, open-set recognition, and domain shift. `docs/literature-review-matrix.md` re-synchronized with `report/src/chapters/literatureReview.tex` (Chapter 2). Chi-squared description corrected in `README.md` and `docs/BiasAperture-AT.md` to precisely state: Pearson's χ² independence test with Fisher's exact test fallback for sparse 2×2 tables (expected cell count < 5). `report/references.bib` updated with 10 new BibTeX entries. 67/67 tests pass; `latexmk` compilation verified (50 pages, clean exit 0).

**Revision 13 (September 5, 2026):** Title updated to BiasAperture-AT_v13. Updated Project Progress & Roadmap in `README.md` and §18.2 to 95% completion: Sprints 1, 2, and 3 formally marked COMPLETED (M1–M4 engines, 10,954 validation inference, dual HTML reports, 67/67 automated tests passing). Sprint 4 marked IN PROGRESS (95%) with FairFace 97.7k benchmark alignment, 50-page thesis compilation, 18-slide Beamer presentation deck, and Research Claim Ledger v1.5.0 synchronized.
