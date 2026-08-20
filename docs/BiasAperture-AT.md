# BiasAperture-AT (v6)

Fuse Capstone Project — BiasAperture (Fairness & Bias Audit)

**Owner:** A (Aaradhya Dev Tamrakar)
**Team:** A + T (Tisha Manandhar)
**Supervisor:** Shreejan Kisee
**Program:** Fusemachines AI Fellowship (AIF) 2026

**Status:** Feasibility study reviewed (accurate) · Parallel work structure defined · Named ownership assigned (§16) · Novelty check completed (§12) · SHAP explainability layer added (§3) · Proposal report (main.pdf) cross-validated against full source set, zero contradictions (§13) · Repo restructured with docs/ + sync.ps1, literature review matrix built (§15) · Packaging & Ruff standards configured

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

**Explainability layer** (added, per NotebookLM Stage 2 session, July 21 2026): SHAP (SHapley Additive exPlanations) integrated into the Fairness Metrics Engine as an interchangeable Strategy-pattern component. Purpose: local interpretability — identify which facial features drive a given prediction, and detect proxy variable entanglement (model relying on features correlated with protected attributes). Maps to EU AI Act Article 13 (Transparency) and Article 15 (Accuracy/Robustness). Confirmed in repo (§15): requirements.tex now carries FR-005 (SHAP-based attribution on every flagged disparity), matching this scope exactly. Still not reflected in feasibility_study.pdf module list (§3.1.3) — tracked in §13 (Outstanding Action Items), unchanged.

**Explicit scope boundary:** this tool detects and reports bias — it does not retrain the model or fix the bias itself. It is a diagnostic/audit layer, not a corrective one.

## Work Distribution Logic

Distribution principle: separate what one person can complete solo from what genuinely needs two people working together — driven by whether a step requires shared judgment/iteration, not just by how long it takes.

| Phase | Nature | Mode |
|---|---|---|
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

An earlier working split (A = statistical bias detection, T = testing-matrix + reporting) was justified by A's Wk5 (tree-based ensembles + SHAP) fellowship score. That justification was explicitly dropped mid-session — a partial Classroom-grade comparison (W2, W4) surfaced a ~1-point net difference in A's favor, but neither week tests the SHAP/embedding skill the original split relied on, and neither party's actual Wk5 score was available. Current status: scores are being treated as roughly comparable for split purposes; the split will instead be decided by built work, preference, or the solo/together logic in §4.

## Feasibility Study — Reviewed

`Fairness_and_Bias_Audit_System_Feasibility_study.zip` (main.tex/main.pdf/references.bib, 27pp) checked against primary sources — **accurate, no errors found**:

| Claim | Source-checked value | Doc's value | Result |
|---|---|---|---|
| Gender Shades error-rate gap | 34.7% vs 0.8% (PMLR v81, pp.77–91) | "exceeding thirty percentage points" | ✅ |
| FairFace scale/taxonomy | 108,501 images, 7 exact race categories | Matches exactly | ✅ |
| EU AI Act citation | Reg. (EU) 2024/1689, 13 June 2024 | Matches exactly | ✅ |
| NIST AI RMF citation | NIST AI 100-1, Jan 2023 | Matches exactly | ✅ |
| All 18 bib entries | — | Resolve to real papers, correct venue/year | ✅ |

Proposes 5 architectural modules (data ingestion, model interface, fairness metrics engine, report generation, orchestration) validated against FairFace + UTKFace, using AIF360 + Fairlearn as computational back ends, reporting modelled on Model Cards + Datasheets for Datasets.

Two structural gaps identified, addressed in §9–§10: scope reads as fully committed (5 modules, dual toolkit, dual dataset, dual report format, dual UI) with no cut-priority if the timeline slips; and no numeric acceptance criteria were stated (no significance threshold, no target runtime, "at least one" case study left unbounded).

## Cut-List (if behind schedule — drop in this order)

| Order | Cut | Why first/last |
|---|---|---|
| 1 | Web UI (Streamlit/Flask), keep CLI only | Pure UX layer, zero grading relevance to the fairness-engineering core |
| 2 | UTKFace, keep FairFace only | Architecture already anticipated this; UTKFace's DEX label-noise is already the doc's own flagged risk. Note (§15): UTKFace has no corresponding bib entry in report/references.bib as of v5 — if this cut is NOT taken, a source paper for UTKFace still needs to be added. |
| 3 | PDF export, keep HTML only | HTML+Jinja2 alone satisfies "standardised, exportable" and the Model Cards/Datasheets structure |
| 4 | Direct in-process inference, keep predictions-file (CSV/JSON) ingestion only | Actually the simpler mode; removes GPU/dependency-version risk entirely (doc's own flagged risk); confirmed predict.py + pretrained checkpoint are public — see §9 |
| 5 | AIF360, keep Fairlearn only | Last resort — Fairlearn alone computes all 4 named disparity metrics, but this is the only cut that measurably weakens the "methodologically defensible" claim |

**Non-negotiable core, never cut:** ingestion + one model + fairness engine + one report format + scope-boundary statement.

## Acceptance Criteria

- Significance: chi-squared tests, **α = 0.05**, report exact p-values
- Bootstrap CI: **1,000 resamples minimum**, 95% CI on subgroup accuracy differences
- Minimum reportable subgroup size: **n ≥ 30** per cell — below this, flag "insufficient sample, not reported" instead of computing
- Runtime target: full FairFace (108,501 img) ≤ 4hr GPU; stratified dev subset (n=5,000) ≤ 30min CPU
- Case study minimum: FairFace baseline ResNet-34 on FairFace, all 4 named disparity metrics (demographic parity diff, equalised odds diff, equal opportunity diff, disparate impact ratio). Confirmed: pretrained checkpoint `res34_fair_align_multi_7_20190809.pt` and `predict.py` are both public on `joojs/fairface` GitHub — no training run needed, just inference + CSV export.
- Report completeness rule: every metric row must show (subgroup n, point estimate, 95% CI, p-value or n<30 flag) — no exceptions.

## Work Structure — Restructured for Concurrency

A confirmed: wants work to run **concurrent and codependent**, not sequential — §4's original solo/together split still names the right phases, but "test-matrix construction" and "report generation" as literally sequenced (report-gen blocked on detection-engine output, which is blocked on test-matrix) leaves one person idle first.

Fix — same two solo phases, restructured to both start day one:

| Stream | Blocks on | Deliverable |
|---|---|---|
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

Claimed novelty per §2.4 of the feasibility study: not a new fairness metric or mitigation technique — the contribution is a **reusable, face-specific audit pipeline** bridging tabular-first toolkits (AIF360/Fairlearn) and vision-classifier workflows, with regulatory-mapped reporting (Annex IV/Model Cards). This is engineering/integration novelty, not research novelty — acceptable for capstone scope, but must be defended as such, not oversold.

Prior-art search conducted this session. Confirmed general-purpose/tabular-first tools already known via §7 sources (AIF360, Fairlearn) do not cover face-specific ingestion + demographic schema + regulatory reporting. Additional tools surfaced, none closing the gap:

| Tool | Category | Why it doesn't collapse the gap |
|---|---|---|
| Aequitas (DSSG, U. Chicago) | Open-source bias audit toolkit | Tabular/binary-classification-first, same limitation as AIF360/Fairlearn |
| FairSight | Visual analytics for classifier bias | General classification, not face/image-native |
| FairTest | Unintended-association testing | General-purpose, not vision-specific |
| Themis-ml, FAT Forensics, What-If Tool | General fairness/mitigation libraries | Same tabular/general-purpose limitation |
| NGO Algorithm Audit — JFAM (unsupervised-bias-detection) | Audit-framed, OECD-catalogued, Stanford AI Audit Competition 2023 finalist | Binary classifiers generally, not face-specific; early-stage, docs WIP |

**Defense framing to have ready:** if asked "why not just run Fairlearn directly on exported predictions" — answer is face-specific schema alignment (7-race/9-age FairFace taxonomy), demographic-label handling, and Annex IV/NIST-risk-category report mapping, not "because images are involved." The regulatory-mapping angle (metric row → specific legal article) is the stronger differentiator versus the vision-pipeline angle — fewer student fairness-toolkit projects tie output to named statute clauses than build an image pipeline.

## Outstanding Action Items

Consolidated here so neither drops through the cracks — both are edits pending on the same file, `feasibility_study.pdf`:

| Item | Target | Status |
|---|---|---|
| 1 | Add one sentence to §2.2 (Current Fairness Toolkits) naming Aequitas alongside AIF360/Fairlearn, same tabular-limitation caveat. Prominent enough (DSSG/U. Chicago, most "top fairness toolkit" roundups) that an examiner may ask "why not Aequitas" — lit review should preempt this. | feasibility_study.pdf §2.2 | Not yet applied (unchanged as of v5) |
| 2 | Add the SHAP explainability layer (§3 above) to the module list. | feasibility_study.pdf §3.1.3 | Not yet applied to feasibility_study.pdf — but now reflected in report/src/chapters/requirements.tex as FR-005 (§15). Two different documents; feasibility_study.pdf edit itself remains outstanding. |

## Proposal Report — Cross-Validated (August 1, 2026)

`report/main.pdf` (BiasAperture proposal, submitted to repo, July 2026) checked this session against the full engineering-strategy notebook source set — EU AI Act full text (EUR-Lex), Article 10 source, NIST AI RMF, AIF360 docs, Fairlearn docs, FairFace/UTKFace dataset profiles, Model Cards paper, Datasheets for Datasets paper, and the feasibility study itself:

| Claim | Result |
|---|---|
| Art. 10 in force 2 Aug 2026 | ✅ Supported — Art. 113 EUR-Lex |
| Table 4-3 mapping (10(2)/10(3)/10(4)/10(5)) | ✅ Supported — matches actual EUR-Lex sub-clause content |
| AIF360 + Fairlearn implement DPD/EOD/EOP/DIR | ✅ Supported |
| FairFace 108,501 images | ✅ Supported |
| Gender Shades 34.7% vs 0.8% | ✅ Supported |
| Requirements/architecture/schedule/risk register vs. feasibility study | ✅ Supported — Explainability Layer (§3 above) is a documented addition beyond the original feasibility scope, not drift; Appendix D risk register is a verbatim reproduction of feasibility Table 8.1 |
| EU AI Act = Reg. (EU) 2024/1689 | ✅ Supported |

Zero unsupported or contradicted claims. Proposal is factually submission-ready; §13's two items remain the only open documentation gaps (both on feasibility_study.pdf, not main.pdf).

## Repo Structure & Literature Review Matrix (August 7, 2026)

Verification pass (Claude session) confirmed report/src/chapters/literatureReview.tex and requirements.tex both already fulfill the AIF program's Literature Review Guidelines and Project Requirement templates in full — no gaps, content exceeds template depth. All \cref/\label targets resolve, all \cite keys resolve against references.bib (11 entries).

Literature review matrix built: `docs/literature-review-matrix.md` — 9 papers (Buolamwini & Gebru 2018 "Gender Shades", Dehdashtian et al. 2024 CV fairness survey, Hardt et al. 2016 "Equality of Opportunity", Watkins et al. 2022 "Four-Fifths Rule" critique, Kurian et al. 2024 medical-imaging proxy-bias study, Mitchell et al. 2019 "Model Cards", Gebru et al. 2018 "Datasheets for Datasets", Karkkainen & Joo 2021 "FairFace", Buscemi et al. 2025 "Assessing High-Risk AI Systems under the EU AI Act") in the guideline's Walden-referenced column format (Title/Author/Date, Conceptual Framework, RQ, Datasets, Methodology, Analysis & Results, Conclusions, Implications). Sourced entirely from existing references.bib + literatureReview.tex, no external claims added. Meets the guideline's 5-paper minimum.

**Gap surfaced:** UTKFace is used as a secondary benchmark in the report (and named in §8's cut-list above) but has no corresponding bib entry in references.bib — no source paper currently tracked for it. Relevant directly to Cut #2 in §8: if UTKFace is kept rather than cut, this needs resolving before submission.

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
|---|---|---|
| Data Exploration (FairFace + UTKFace — profiling, distributions, malformed/missing attributes) | A | Consistent, low-fluctuation output under varying input conditions — least prone to introducing noise while working through messy, unfamiliar data |
| Model Specification Finalise (locking metric set — AIF360/Fairlearn choices, diagnostic scope) | T | High-power, high-precision execution; will not let an unverified or half-settled spec pass through |
| Proposal Report Finalise | T drafts claims/scope, A formats & compiles | T's intolerance for overstatement keeps the report's claims honest against what's actually been decided; A's steady execution handles consistent formatting and assembly |
| Presentation Draft | A | Adaptable — able to restructure and adjust the narrative as content from other modules shifts closer to the deadline |
| Task Division (this task itself — next sprint's split) | Joint | Both weigh in; no single-owner reasoning applies to planning the split |

**Prior module-level split** (established earlier in the same chat session, for reference):

| Task | Owner | Reasoning |
|---|---|---|
| Data ingestion & preprocessing | A | Consistent output handling messy/malformed data |
| Cross-module integration & handling unexpected dataset/metric behavior | A | High adaptability |
| Bias metric implementation (AIF360/Fairlearn) | T | High-power precision; no unverified results pass through |
| SHAP/explainability visualization | T | Detail-dense, rigorous presentation work |
| Statistical significance / validation | T | Uncompromising standard against unsupported conclusions |
| Report drafting (claims/findings narrative) | A | Steady assembly across shifting inputs |
| Report review (accuracy check) | T | Natural check against overstated claims |
| LaTeX formatting & final compilation | A | Consistent, reliable on fixed repeatable process |

**Note:** A mentioned sending T a screenshot of the module-level split table above, prior to the coming-week plan being defined.

No change to §1–§15 content, §4/§10 named-ownership status, §9 acceptance criteria, or §13 action items.

---

*Exported from Fuse capstone planning session — reflects state as of this export, not a final locked plan.*

**Revision:** A/T naming applied throughout, replacing full names/initials, per confirmed decision from prior session.

**Revision 2 (July 17, 2026):** §7–§10 added — feasibility study reviewed and citation-checked (accurate), cut-list, acceptance criteria, and work restructured for concurrency per A's explicit preference. Named ownership of solo streams remains open, per §4's original scope.

**Revision 3 (July 30, 2026):** Project renamed BiasAperture throughout. §12 added — novelty assessment and prior-art check (Aequitas, FairSight, FairTest, Themis-ml, FAT Forensics, What-If Tool, JFAM), none closing the claimed research gap. §2.2 addition to feasibility_study.pdf flagged as outstanding action item, not yet applied. §1 updated — Ward Office Assistant → BiasAperture swap confirmed final, no longer open. §3 updated — SHAP explainability layer added per July 21 NotebookLM engineering session (not yet in feasibility_study.pdf module list — action item). §11 (naming history) added — "BioFair: Compliance Engine" from the same July 21 session noted as superseded by BiasAperture.

**Revision 4 (August 1, 2026):** §3's dangling "action item below" reference (pointed nowhere in v3) resolved — new §13 consolidates both outstanding feasibility_study.pdf edits (Aequitas citation, SHAP module-list addition) in one place; §12's duplicate inline copy of the Aequitas item removed in favor of the §13 reference. New §14 added — report/main.pdf cross-validated this session against the full engineering-strategy source set (EU AI Act/EUR-Lex, Article 10, NIST AI RMF, AIF360, Fairlearn, FairFace/UTKFace, Model Cards, Datasheets, feasibility study): zero contradictions, zero unsupported claims. No change to §4/§10 named-ownership status, §9 acceptance criteria, or §13 action items — all remain open exactly as in v3.

**Revision 5 (August 7, 2026):** New §15 added — repo verification pass, literature review matrix (docs/literature-review-matrix.md, 8 papers, meets 5-paper minimum), repo restructure (docs/ folder, sync.ps1, README update), pushed as commit 00b89c7. §3 updated — SHAP explainability layer confirmed present in report/src/chapters/requirements.tex as FR-005, distinct from the still-outstanding feasibility_study.pdf edit. §8 Cut #2 (UTKFace) annotated with the missing-bib-entry gap found in §15. §13 item #2 status clarified: requirements.tex now reflects SHAP, feasibility_study.pdf §3.1.3 still does not — item remains open, not resolved. No change to §4/§9/§10/§12 content. Title renamed from Fuse-capstone-project-AT_v4 to BiasAperture-AT_v5, matching the project's confirmed name (§1, §11) rather than the earlier Fuse-capstone working title.

**Revision 6 (August 20, 2026):** New §16 added — coming-week (Aug 20) trait-based task assignment for 5 named items (Data Exploration, Model Specification Finalise, Proposal Report Finalise, Presentation Draft, Task Division), plus the prior module-level split from the same session, both carried over verbatim from a separate Claude chat exercise. Scope is independent of §1–§15's project-tracking content — no registration, feasibility-study, acceptance-criteria, cut-list, novelty-check, or repo-structure content was touched. No change to §1–§15. Title renamed from BiasAperture-AT_v5 to BiasAperture-AT_v6.
