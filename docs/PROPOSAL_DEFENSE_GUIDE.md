# BiasAperture — Proposal Defense Preparation Guide

**Defending:** *BiasAperture: A Diagnostic and Evaluative Framework for Auditing Demographic Bias in Facial Analysis Systems*  
**Presenters:** Aaradhya Dev Tamrakar & Tisha Manandhar  
**Supervisor:** Shreejan Kisee (TA, Fusemachines AI Fellowship)  
**Program:** Fusemachines AI Fellowship (AIF) 2026 / Department of Electronics and Computer Engineering, Thapathali Campus, IOE  

---

## Table of Contents

1. [Defense Format & Strategy](#1-defense-format--strategy)
2. [Slide Deck Outline (15–20 slides)](#2-slide-deck-outline-1520-slides)
3. [Slide-by-Slide Script & Talking Points](#3-slide-by-slide-script--talking-points)
4. [The Novelty Question — Your Most Important Defense](#4-the-novelty-question--your-most-important-defense)
5. [Anticipated Hard Questions & Scripted Answers (30+)](#5-anticipated-hard-questions--scripted-answers-30)
6. [Traps to Avoid](#6-traps-to-avoid)
7. [Numbers You Must Know Cold](#7-numbers-you-must-know-cold)
8. [Mock Grilling Checklist](#8-mock-grilling-checklist)

---

## 1. Defense Format & Strategy

### What a Proposal Defense Is

A proposal defense is **not** a results presentation. You are convincing the panel of three things:

| Question the Panel Asks | What They Want to See |
|---|---|
| **Is this problem real?** | A clear gap in existing tools, backed by literature |
| **Is the proposed solution well-designed?** | Sound architecture, feasible scope, clear methodology |
| **Can this team execute it?** | Realistic schedule, descoping strategy, evidence of preparation |

### Your Strategic Advantage

You have done an unusual amount of pre-implementation rigor. Use this:

> **Framing line:** "We have not just proposed what we will build — we have verified the assumptions we are building on. We tracked 20 research claims through a formal verification lifecycle, formally invalidated 5 initial hypotheses before they could waste implementation time, and codified 7 claims as passing automated tests. The implementation phase starts on verified ground."

### Presentation Time Budget

| Section | Time | Notes |
|---|---|---|
| Introduction & Problem | 3 min | Hook with Gender Shades stat, land the gap |
| Literature Review | 3 min | 9 papers → 1 slide table, not 9 slides |
| Objectives & Scope | 2 min | 5 objectives, scope boundary, what you do NOT do |
| Architecture & Methodology | 5 min | The meat — pipeline, metrics, statistics |
| Regulatory Mapping | 2 min | EU AI Act + NIST — show the traceability tables |
| Schedule & Feasibility | 2 min | WBS, Gantt, descoping cut-list |
| Conclusion & Q\&A Transition | 1 min | Restate diagnostic scope, invite questions |
| **Total Presentation** | **~18 min** | Leave 10–15 min for Q\&A |

---

## 2. Slide Deck Outline (15–20 slides)

### Slide 1: Title Slide
- Project title, authors, supervisor, institutional affiliation, date
- BiasAperture logo if available

### Slide 2: The Problem — A Single Striking Number
- **"34.7% vs 0.8%"** — Buolamwini & Gebru (2018) error rate gap
- One sentence: facial analysis systems exhibit severe demographic accuracy disparities
- One sentence: no reusable, standards-aligned auditing tool exists to measure this systematically

### Slide 3: The Regulatory Urgency
- EU AI Act Article 10 enters force for bias assessment on **2 August 2026** (it's already live)
- Biometric categorization is explicitly classified as high-risk AI
- NIST AI RMF provides complementary voluntary measurement framework
- **Implication:** This isn't just academic — compliance infrastructure is needed *now*

### Slide 4: Problem Statement (Formal)
> "There is a clear engineering gap between a mature body of fairness metrics and the availability of a reusable, standards-aligned software platform that operationalises this research into a repeatable auditing workflow for facial analysis systems."

### Slide 5: Literature Review Summary Table
- Single table with 9 papers, 3 columns: Paper, Key Finding, How BiasAperture Uses It
- **Do not** read through all 9 — highlight 3–4 key ones:
  - Buolamwini & Gebru → motivates the problem
  - Hardt et al. → defines EOD/EOP metrics we adopt
  - Watkins et al. → critiques bare thresholds → justifies our statistical rigor
  - Kärkkäinen & Joo → provides FairFace benchmark dataset

### Slide 6: The Engineering Gap (Competitive Landscape)
- 7-tool feature matrix: Aequitas, Fairlearn, AIF360, Google WIT, JFAM, FAT Forensics, FairTest
- Show columns: CV-native schema | Statistical guards | SHAP explainability | Regulatory mapping | Offline report
- **No existing tool fills all columns** — that's the gap BiasAperture fills

### Slide 7: General & Specific Objectives
- **General:** Design an end-to-end diagnostic platform that identifies demographic disparities in facial analysis models and reports them in a regulator-legible format
- **5 Specific Objectives** — list them (directly from your intro.tex)

### Slide 8: Scope & Limitations — The Diagnostic Boundary
- **In scope:** Ingest → Measure → Explain → Report
- **Explicitly NOT in scope:** Retrain, fine-tune, debias, generate synthetic data
- This is the most important slide for credibility — **own your boundaries**

### Slide 9: System Architecture Diagram
- Use your `architecture_highlevel.jpg`
- Label the 6 modules: Ingestion → Model Interface → Fairness Engine → Explainability → Report → Orchestration
- Show data flow: `SubjectRecord` → `MetricResult` → HTML Report

### Slide 10: The Core Four Disparity Metrics
- Table with 4 metrics: DPD, EOD, EOP, DIR
- Mathematical definition for each (keep formulas visible but don't read them aloud)
- Fair-value column: 0.0, 0.0, 0.0, 1.0
- **Key talking point:** "Every metric has a precise mathematical definition, and we verified that AIF360 and Fairlearn don't always agree on these definitions — we harmonized them"

### Slide 11: Backend Harmonization — Why "Just Use Fairlearn" Isn't Enough
- EOD divergence: Fairlearn uses max-gap, AIF360 uses mean-gap → **different numbers on same data**
- EOP sign mismatch: AIF360 returns signed, Fairlearn returns unsigned
- DIR: symmetric bounded ratio to avoid privileged-group designation across 7 races
- **This is a live demonstration of engineering novelty** — show the specific conflict

### Slide 12: Statistical Rigor — Three Layers of Defense
1. **$n \geq 30$ guard:** Subgroups below threshold are flagged, never scored
2. **$\chi^2$ independence test + Holm-Bonferroni FWER:** Every disparity tested for statistical significance across 126 intersectional cells
3. **Stratified BCa bootstrap CI ($B \geq 1000$):** Every metric accompanied by 95% confidence interval

### Slide 13: Explainability — SHAP + ITA Proxy Detection
- Triggered only on statistically significant disparities (not whole dataset)
- PartitionExplainer (black-box default) / GradientExplainer (PyTorch fast-path)
- ITA skin-tone colorimetry to detect if classification decisions correlate with skin-tone proxies
- **Honest limitation:** cite Bilodeau et al. impossibility theorems — feature attribution ≠ causal proof

### Slide 14: Regulatory Traceability
- **Two-column table:** Article 10 sub-clause → BiasAperture output that addresses it
- **Second table:** NIST AI RMF Measure subcategory → BiasAperture mechanism
- **Key line:** "Every row in our audit report is tagged with its regulatory basis"

### Slide 15: Report Output — Standalone Offline HTML
- Screenshot/mockup of the HTML report structure
- Model Cards (Mitchell et al.) + Datasheets (Gebru et al.) structure
- Zero external CDN dependencies — single file, works offline
- **Why it matters:** auditors can share it without network access or dependency installation

### Slide 16: Work Breakdown & Schedule
- Show the WBS table (8 work packages)
- Show the Gantt chart
- Highlight parallel streams: Stream A (Data/Ingestion — Tisha) ‖ Stream B (Report — Tisha) while Stream C (Fairness Engine — Aaradhya) ‖ Stream D (Explainability — Aaradhya)
- Convergence at WP4 → Integration at WP5

### Slide 17: Descoping Strategy — What Gets Cut First
- Show the 5-tier cut-list table
- **This slide earns enormous credibility** — it shows you've thought about failure modes
- Emphasize: "The non-negotiable core — ingestion, one model interface, fairness engine, one report format — is never cut"

### Slide 18: Verification Strategy
- Schema-locked at M1 → both streams build against shared contract
- 22 research-contract tests already passing
- Known-answer 8-record deterministic baseline (DPD=0.500, EOD=0.500, EOP=0.500, DIR=0.333)
- Dual-backend cross-validation as implementation correctness check

### Slide 19: Conclusion
- Restate the gap → restate the solution → restate the diagnostic boundary
- "BiasAperture does not fix bias. It finds it, measures it, explains it, and reports it — with statistical rigor and regulatory traceability."

### Slide 20: Questions
- Clean slide, project title, "Thank you — Questions?"

---

## 3. Slide-by-Slide Script & Talking Points

### Opening (Slide 2) — The Hook

> "In 2018, Buolamwini and Gebru audited three commercial gender-classification systems and found that the worst-performing intersectional subgroup — darker-skinned females — had an error rate of 34.7%, while the best-performing group — lighter-skinned males — had just 0.8%. That's a 43-to-1 gap. That single audit changed the conversation about fairness in computer vision. But here's the thing — it was a one-off study. There is no reusable software platform that lets someone replicate that kind of audit on an arbitrary model. That's the gap we're filling."

### Architecture (Slide 9) — The Pipeline

> "BiasAperture is a linear diagnostic pipeline with six modules. Raw data enters through the ingestion layer, which validates demographics against a locked schema. Predictions come either from a model object or a precomputed CSV file. The fairness engine computes four disparity metrics using two independent backends — Fairlearn and AIF360 — as a cross-check. If a statistically significant disparity is detected, the explainability layer uses SHAP to identify which visual features are driving it. Finally, the report generator assembles everything into a standalone HTML document structured around Model Cards and Datasheets conventions, with every metric tagged to its EU AI Act and NIST AI RMF basis."

### Harmonization (Slide 11) — The Engineering Novelty Demo

> "Here's a concrete example of why 'just use Fairlearn' isn't sufficient. We verified — in code — that Fairlearn and AIF360 produce *different numbers* for Equalized Odds Difference on the same input data. Fairlearn computes the worst-case gap — the maximum of the TPR gap and FPR gap. AIF360 computes the average of those two gaps. On our test matrix, Fairlearn reports 0.30 and AIF360 reports 0.20. Which one is 'correct'? We followed Hardt et al.'s original definition and harmonized both to the worst-case max-gap formulation. This is the kind of integration problem that's invisible until you actually wire the tools together."

### Statistical Rigor (Slide 12) — The Credibility Anchor

> "We don't just report a number and call it a disparity. Every metric goes through three layers of statistical defense. First, any subgroup with fewer than 30 observations is flagged as insufficient and never scored — because small samples produce wild variance. Second, every disparity is tested for statistical significance using a chi-squared test, with Holm-Bonferroni correction to control the family-wise error rate across 126 intersectional cells. Third, every metric comes with a 95% bootstrap confidence interval from at least 1,000 stratified resamples. If a disparity doesn't survive all three checks, we don't report it as a finding."

### Descoping (Slide 17) — The Maturity Signal

> "We know this is an ambitious proposal for an eight-week timeline with two people. So we defined our descoping order in advance. If we fall behind, we cut the web UI first — it's cosmetic. Then UTKFace — we already formally documented its label-noise limitations. Then PDF export. Then direct model inference. The last resort is dropping AIF360 entirely and keeping only Fairlearn. But the diagnostic core — ingestion, fairness engine, one report format — is never cut. We'd rather deliver a narrow, correct system than a broad, broken one."

---

## 4. The Novelty Question — Your Most Important Defense

This **will** come up. The panel will ask some variant of: *"Aren't you just combining existing tools?"*

### The Wrong Answer (Avoid This)

> ~~"We're building something new that nobody has done before."~~

This invites the follow-up: *"But AIF360 already computes these metrics..."* and you're trapped.

### The Right Answer (Memorize This Framework)

**Step 1 — Acknowledge the tools exist:**
> "You're right that Fairlearn, AIF360, and SHAP all exist independently. We are not claiming to have invented a new fairness metric or a new statistical test."

**Step 2 — Name the specific friction:**
> "What doesn't exist is a system that bridges them for computer vision workflows. Fairlearn and AIF360 assume tabular data with a single protected attribute. Face classifiers produce predictions across seven race categories, nine age bins, and two gender labels — 126 intersectional cells. There's no off-the-shelf schema bridge."

**Step 3 — Show you found real conflicts:**
> "And when we actually wired them together, we discovered they don't agree. Equalized Odds Difference gives you different numbers depending on which library you use — Fairlearn uses the max-gap definition, AIF360 uses the mean-gap. We had to read both source codes, trace the math back to Hardt et al.'s original paper, and harmonize them. That's not 'just combining.'"

**Step 4 — Land the analogy:**
> "Docker didn't invent containerization — that technology existed. Docker's contribution was making containers usable in one command. Our contribution is making fairness auditing usable for face classifiers in one workflow, instead of three weeks of custom engineering."

**Step 5 — Quantify the value:**
> "A practitioner doing this manually today spends two to four weeks writing the glue code. We're building it once, documenting it, and making it open-source so the next auditor takes two days, not two weeks."

### Supporting Evidence to Cite on Demand

| Friction Point | Evidence |
|---|---|
| EOD math divergence | R-005: Fairlearn reports 0.30, AIF360 reports 0.20 on same input |
| EOP sign mismatch | R-006: AIF360 returns −0.30 (signed), Fairlearn returns 0.30 (unsigned) |
| No CV-native schema | 7-tool competitive matrix shows no tool handles 7-race × 9-age × 2-gender natively |
| No statistical guards | Watkins et al. (2022) critiques bare 80% thresholds as "epistemic trespassing" |
| No regulatory tagging | No existing tool maps metrics to EU AI Act Article 10 sub-clauses |

---

## 5. Anticipated Hard Questions & Scripted Answers (30+)

### Category A: Scope & Novelty

---

**Q1: "Why not just use Fairlearn directly?"**

> "Fairlearn is designed for tabular classification with a single protected attribute. Face classifiers operate over images with multiple, non-ordinal demographic axes — seven races, nine age groups, two genders. There's no built-in FairFace-to-Fairlearn schema bridge. And Fairlearn doesn't provide regulatory traceability, SHAP explainability, or an offline compliance report. BiasAperture fills that integration gap."

---

**Q2: "What's novel about your project? You're not inventing new metrics."**

> [Use the 5-step framework from Section 4 above]

---

**Q3: "Why only diagnosis? Why not fix the bias?"**

> "By design. Diagnostic and corrective fairness are fundamentally different engineering problems, as Dehdashtian et al.'s survey makes clear. Mixing them creates a system that's mediocre at both. We deliberately positioned BiasAperture on the diagnostic side so that a future mitigation tool can consume our findings as input without us having to compromise either system's integrity. The separation of concerns is the feature, not the limitation."

---

**Q4: "Is this a software engineering project or a research project?"**

> "It's an engineering project solving a research-informed problem. We don't invent new theory — we take mature theory from Hardt et al., Buolamwini & Gebru, and Watkins et al., and operationalize it into a reusable platform. The engineering novelty is in the schema bridge, the backend harmonization, the statistical rigor layer, and the regulatory traceability — none of which exist in any single existing tool."

---

**Q5: "Two people, eight weeks — is this feasible?"**

> "Yes, for three reasons. First, we've pre-verified our assumptions — 20 research claims tracked through a formal ledger, 5 hypotheses formally invalidated before they could waste implementation time, and 7 claims already codified as passing automated tests. Second, our architecture supports parallel streams — Tisha builds ingestion and reporting while Aaradhya builds the fairness engine and explainability, both against a locked schema contract. Third, we have a descoping strategy with five tiers, and the non-negotiable core is deliberately narrow enough for two people."

---

### Category B: Technical Depth

---

**Q6: "Why $n \geq 30$? Isn't that arbitrary?"**

> "It's a conservative heuristic grounded in the Central Limit Theorem — sample means of $n \geq 30$ from any distribution are approximately normal, which is the assumption underlying our chi-squared tests and bootstrap confidence intervals. We tested what happens without it: on FairFace validation data, including undersized subgroups caused a 3× distortion in disparity estimates. On a constructed 4-sample outlier, the distortion was 45×. The guard isn't arbitrary — it's empirically justified."

---

**Q7: "Why chi-squared and not Fisher's exact test?"**

> "Chi-squared is our primary test because most of our contingency tables are large enough — FairFace has nearly 100,000 images. Fisher's exact test is specified as a fallback for 2×2 cells with expected counts below 5, which can occur in sparse intersectional cells. We've documented this in our low-level specification."

---

**Q8: "Why BCa bootstrap instead of standard percentile bootstrap?"**

> "BCa — Bias-Corrected and Accelerated — adjusts for both median bias and skewness in the bootstrap distribution, producing more accurate confidence intervals than standard percentile methods, especially for ratio-based metrics like DIR. We also have an automatic fallback: if the jackknife acceleration factor exceeds 0.5, or the bias-correction term is degenerate, we fall back to standard percentile intervals. We tried using `scipy.stats.bootstrap` directly but it failed on multi-group metrics requiring fixed-strata resampling — that's invalidated hypothesis INV-002."

---

**Q9: "Why Holm-Bonferroni and not Benjamini-Hochberg (FDR)?"**

> "We control Family-Wise Error Rate, not False Discovery Rate, because our report is intended for regulatory compliance. Reporting even one false disparity to a regulator is worse than missing a marginal one. Holm-Bonferroni controls FWER at $\alpha$ and is uniformly more powerful than plain Bonferroni — it rejects at least as many hypotheses. For 126 intersectional cells, that power gain matters."

---

**Q10: "How do you handle multi-class classification? Race has 7 classes."**

> "One-vs-Rest binarization. For each of the $M$ classes, we create a binary task — 'is this class vs. everything else' — and compute DPD, EOD, and EOP per binary task. The macro-average across classes gives the overall metric. DIR is the exception — we report it per-class and never macro-average it, because averaging ratios introduces non-linear distortion. This is specified in our low-level architecture document."

---

**Q11: "What happens if all subgroups predict perfectly (DIR denominator = 0)?"**

> "Explicit edge-case contracts. When $\max(\text{rate}) = 0$, meaning no subgroup is ever predicted positive, we define DIR = 1.0 with an `absolute_selection_warning` flag — because there is no disparity if nobody is selected. When $\min = 0$ and $\max > 0$, DIR = 0.0 — maximum disparity. These are codified in automated tests (R-010)."

---

**Q12: "Why not use LIME instead of SHAP?"**

> "SHAP satisfies the three Shapley axioms — efficiency, symmetry, and dummy — providing theoretically grounded attribution values. LIME approximates with a local linear model that lacks these guarantees. For a diagnostic platform intended to produce regulatory evidence, we need the stronger theoretical foundation. Additionally, PartitionExplainer works as a pure black-box — it doesn't require internal model access, which supports our predictions-file interface mode."

---

**Q13: "SHAP can't prove causation. Aren't you overclaiming?"**

> "Absolutely not — and we explicitly document this limitation. We cite Bilodeau et al.'s 2022 impossibility theorems, which prove that additive linear feature attribution methods cannot guarantee distinguishing spurious from causal features for general neural networks. Our SHAP layer provides 'exploratory proxy evidence,' not causal proof. The compliance report includes explicit limitations disclosures. This is claim R-014 in our research ledger."

---

### Category C: Dataset & Preprocessing

---

**Q14: "Why FairFace specifically?"**

> "FairFace is the most suitable publicly available benchmark for our purposes. It has 97,698 images with human-annotated labels across 7 race categories, 2 gender categories, and 9 age bins — matching the intersectional granularity our framework requires. It was specifically designed for balanced demographic representation. The commonly cited 108,501 figure was the pre-annotation total before quality filtering — the released dataset has exactly 97,698 labeled images."

---

**Q15: "Why did you drop UTKFace?"**

> "Two formal reasons, documented as invalidated hypothesis INV-004. First, UTKFace uses only 3 race categories — White, Black, Asian — which collapses our locked 7-race schema. East Asian, Southeast Asian, Indian, and Middle Eastern are unrecoverable. Second, UTKFace's age labels are DEX model-estimated, not human-annotated, introducing noise we can't quantify. We formally cut it under Cut-List item #2."

---

**Q16: "Why dlib and not MTCNN for face detection?"**

> "Because FairFace's own preprocessing pipeline uses dlib, not MTCNN. We initially assumed MTCNN — that was invalidated hypothesis INV-001. Source code inspection of the official FairFace `predict.py` confirmed usage of `dlib.cnn_face_detection_model_v1` with 5-point landmark alignment, 300×300 face chips, 0.25 padding, resized to 224×224 with ImageNet normalization. Using a different detector than the training pipeline would introduce distribution shift."

---

**Q17: "Is FairFace's 7-race taxonomy adequate? It doesn't include [X group]."**

> "No demographic taxonomy is exhaustive — that's a known limitation we document explicitly. FairFace's 7-category taxonomy is the most granular publicly available benchmark at this scale. Our locked schema is designed so that if a future dataset with finer categories becomes available, the `RACE_LABELS` constant can be extended without changing the pipeline architecture. But for this project, we audit what is measurable with validated data."

---

### Category D: Architecture & Implementation

---

**Q18: "Why two fairness backends? Isn't one enough?"**

> "One is sufficient for computation. Two provide cross-validation. When both libraries produce the same number on the same input, we have higher confidence the result is correct. When they disagree — as they did for EOD and EOP — we know to investigate. We discovered three material divergences (R-005, R-006, INV-005) specifically because we ran both backends. However, we explicitly reframed this as 'software implementation cross-checking,' not 'statistical independence' — that was invalidated hypothesis INV-005."

---

**Q19: "What design patterns did you use and why?"**

> "Six, each tied to a specific architectural decision:
> - **Strategy** for the fairness backends — so cutting AIF360 is a config change, not a rewrite
> - **Adapter** for the model interface — so cutting direct inference doesn't affect downstream code
> - **Builder** for data ingestion — matching the multi-step curation process
> - **Factory** for report generation — so adding PDF export later doesn't modify the HTML path
> - **Template Method** for the report structure — fixing the Model Cards section skeleton
> - **Facade** for orchestration — hiding the pipeline behind a single `audit` command
>
> These aren't academic exercises — each pattern is tied to a specific item in our descoping cut-list."

---

**Q20: "Why a CLI and not a web UI?"**

> "The web UI is Cut #1 in our descoping strategy — the first thing dropped if we fall behind. A CLI is sufficient for the auditing workflow: specify dataset, model, metrics, run. The diagnostic core doesn't benefit from a GUI. If time permits, a Streamlit wrapper could be added later, but it adds zero analytical value."

---

**Q21: "Why Jinja2 and not Google's model-card-toolkit?"**

> "We evaluated `model-card-toolkit` and rejected it (R-016). It pulls in the full Apache TFX/MLMD dependency stack, which creates heavy TensorFlow pinning conflicts and adds significant installation complexity. It also has no built-in support for EU AI Act Article 10 mapping or dual-backend metrics. Custom Jinja2 templates achieve 100% Model Cards structural compliance with zero heavy dependencies."

---

### Category E: Regulatory & Ethics

---

**Q22: "How does BiasAperture map to the EU AI Act specifically?"**

> "Four Article 10 sub-clauses:
> - **10(2)(f)** — examination of possible biases → our four Core Four metrics across 126 intersectional cells
> - **10(2)(g)** — detection, prevention, mitigation → diagnostic detection and measurement (not mitigation)
> - **10(3)** — appropriate statistical properties → $n \geq 30$ guard, support checks, 95% bootstrap CIs
> - **10(5)** — processing special-category data for bias detection → non-commercial research licensing, local processing, aggregate-only reporting
>
> We also map to Annex IV §2(g) for technical documentation of validation procedures."

---

**Q23: "Are you claiming legal compliance?"**

> "No. We provide *technical audit controls that support examination* of Article 10 requirements. We do not claim to constitute a legal compliance certification. That distinction is explicit in every regulatory mapping we produce. Our claim is R-017: 'diagnostic detection/documentation only; mitigation out of scope.'"

---

**Q24: "How do you handle the privacy implications of processing demographic data?"**

> "We have a documented data governance protocol (DATA_GOVERNANCE.md) addressing EU AI Act Article 10(5) and GDPR Article 9. Key provisions: non-commercial research licensing only, all processing is local (no cloud transmission), results are aggregate-only (no individual-level demographic predictions are stored or exported), and SHAP face-chip visualizations use masked overlays. We also require explicit dataset licensing acknowledgment before any audit runs (FR-009)."

---

### Category F: Feasibility & Risk

---

**Q25: "What's your biggest risk?"**

> "Timeline. Eight weeks for two people is tight. That's exactly why we defined the descoping order in advance — so we never have to make that decision under pressure. Our biggest *technical* risk was assumption failure — discovering halfway through that our preprocessing, metric definitions, or statistical methods were wrong. We mitigated that by spending the first phase verifying every assumption before implementation. Five hypotheses that would have burned weeks turned out to be wrong — we caught them before writing production code."

---

**Q26: "What if AIF360 and Fairlearn update and break your harmonization?"**

> "Our dependency versions are pinned in a lockfile (NFR-006). The harmonization adapters are tested against deterministic known-answer matrices — if either library changes its internal math, our contract tests will fail immediately. The system is designed to detect this, not silently accept it."

---

**Q27: "What happens if your bootstrap CI escapes [0,1]?"**

> "Documented edge case. If BCa-adjusted quantiles fall outside [0, 1] — which can happen when the acceleration parameter is extreme — we automatically fall back to standard percentile bootstrap intervals. This is specified in our low-level specification and tested in our contract suite."

---

**Q28: "Can this scale beyond FairFace? What about real production models?"**

> "The architecture is model-agnostic by design. The `PredictionsFileInterface` accepts any CSV/JSON file mapping image IDs to predictions and demographics. A production model team exports their predictions, supplies a demographic-labeled test set, and runs the same pipeline. We validate on FairFace because it's a controlled benchmark with known properties — but the pipeline doesn't know or care that it's FairFace."

---

### Category G: Research Integrity & Methodology

---

**Q29: "You used AI tools for research. How do you ensure the claims are valid?"**

> "We used AI-assisted reconnaissance to accelerate literature exploration and hypothesis generation — but every consequential technical claim was subsequently verified through primary-source inspection, tensor probing, source code reading, or automated testing. We track this explicitly in our Claim Ledger: all 20 active claims are at VERIFIED or REPRODUCIBLE status. Zero remain at ASSERTED. And we formally documented 5 hypotheses that turned out to be wrong, rather than silently correcting them. The methodology statement in our ledger makes this transparent."

---

**Q30: "Why track invalidated hypotheses? Isn't that just showing your mistakes?"**

> "It's showing our research integrity. Five initial assumptions turned out to be wrong: we assumed MTCNN, we assumed scipy bootstrap would work directly, we assumed AIF360 and Fairlearn agreed on EOD math, we assumed UTKFace was usable, and we assumed dual backends meant statistical independence. Each of these, if uncaught, would have either produced incorrect results or wasted weeks of implementation. Documenting refutations is standard research practice — it shows the work, not the mistakes."

---

**Q31: "How do you verify your fairness metrics are computed correctly?"**

> "Three levels. First, known-answer testing: we hand-calculated DPD, EOD, EOP, and DIR on a minimal 8-record synthetic matrix and assert exact values (DPD=0.500, EOD=0.500, EOP=0.500, DIR=0.333) in automated tests. Second, we replicate the matrix 8× to $n=64$ and verify the values hold — proving scale-invariance. Third, we run both Fairlearn and AIF360 on the same data and require agreement (after harmonization). If any of these checks fail, we know exactly where to look."

---

**Q32: "What's your testing strategy?"**

> "We already have 22 research-contract tests across 6 test files:
> - `test_schema.py` — NFR-003 invariant enforcement ($n < 30$ guard)
> - `test_model_interface.py` — CSV/JSON ingestion validation
> - `test_data_ingestion.py` — strict/permissive validation modes, profiling
> - `test_known_answer_fairness_metrics.py` — deterministic 8-record ground-truth
> - `test_backend_harmonization.py` — EOD divergence, EOP sign, DIR edge cases, sample-size skew
> - `test_offline_report_contract.py` — zero-network HTML validation
>
> These run before implementation begins — they're the acceptance criteria the implementation must satisfy."

---

## 6. Traps to Avoid

### ❌ Trap 1: Overclaiming Novelty
**Don't say:** "No one has ever done this before."  
**Do say:** "No existing tool integrates all five of these capabilities for computer vision workflows."

### ❌ Trap 2: Understating the Engineering
**Don't say:** "We just combine AIF360 and Fairlearn."  
**Do say:** "We discovered they disagree on the math, harmonized them, and wrapped them in statistical guards that neither provides."

### ❌ Trap 3: Claiming Causal Explainability
**Don't say:** "SHAP tells us *why* the model is biased."  
**Do say:** "SHAP provides feature attribution that helps *investigate* which visual features correlate with a detected disparity. We cite impossibility theorems that prevent causal claims."

### ❌ Trap 4: Overselling Regulatory Compliance
**Don't say:** "BiasAperture makes you compliant with the EU AI Act."  
**Do say:** "BiasAperture provides technical audit evidence that supports examination of Article 10 requirements."

### ❌ Trap 5: Apologizing for Not Having Built It Yet
**Don't say:** "We haven't implemented anything yet."  
**Do say:** "We've verified every assumption the implementation will rest on. Seven claims are already codified as passing automated tests. The schema is locked, the test suite is written, and the implementation phase starts on verified ground."

### ❌ Trap 6: Getting Lost in Math
**Don't:** derive the BCa formula on the board unless explicitly asked.  
**Do:** know the formula, know *why* BCa over percentile, and offer to derive it if asked.

---

## 7. Numbers You Must Know Cold

| Fact | Number | Source |
|---|---|---|
| Gender Shades worst error rate | 34.7% (darker-skinned females) | Buolamwini & Gebru (2018) |
| Gender Shades best error rate | 0.8% (lighter-skinned males) | Buolamwini & Gebru (2018) |
| FairFace total images | 97,698 (86,744 train + 10,954 val) | R-002 |
| Intersectional cells | 126 (7 race × 2 gender × 9 age) | Schema |
| Core Four metrics | DPD, EOD, EOP, DIR | FR-003 |
| Minimum sample size | $n \geq 30$ | NFR-003 |
| Bootstrap resamples | $B \geq 1,000$ | NFR-002 |
| Significance level | $\alpha = 0.05$ | NFR-001 |
| Race categories | 7 | Schema |
| Gender categories | 2 | Schema |
| Age bins | 9 | Schema |
| Research claims tracked | 20 active + 5 invalidated | Claim Ledger |
| Automated contract tests | 22 across 6 test files | Test suite |
| Competitive tools audited | 7 (Aequitas, Fairlearn, AIF360, WIT, JFAM, FAT Forensics, FairTest) | R-019 |
| ResNet-34 head size | 18 units (7+2+9) over 512 features | R-001 |
| EOD divergence example | Fairlearn: 0.30, AIF360: 0.20 | R-005 |
| Sample-size distortion (FairFace) | ~3× | R-008 |
| Sample-size distortion (synthetic) | ~45× | R-008 |
| EU AI Act Article 10 effective date | 2 August 2026 | Regulation EU 2024/1689 |
| Descoping tiers | 5 (Web UI → UTKFace → PDF → In-process → AIF360) | Cut-list |
| Known-answer ground truth | DPD=0.500, EOD=0.500, EOP=0.500, DIR=0.333 | R-020 |

---

## 8. Mock Grilling Checklist

Use this checklist for mock defense sessions with each other or with Shreejan:

### Round 1: Warm-Up (5 min)
- [ ] What is BiasAperture?
- [ ] What problem does it solve?
- [ ] What does it NOT do?

### Round 2: Technical Depth (10 min)
- [ ] Explain your four metrics without looking at notes
- [ ] What's the difference between EOD in Fairlearn vs AIF360?
- [ ] Why $n \geq 30$?
- [ ] What happens when DIR denominator is zero?
- [ ] Why BCa over standard percentile bootstrap?
- [ ] Why Holm-Bonferroni and not Bonferroni?

### Round 3: Novelty & Scope (5 min)
- [ ] "This is just integration" — defend it
- [ ] "Why not fix the bias?" — defend the diagnostic boundary
- [ ] "What's novel?" — give the 5-step answer without notes
- [ ] Name 3 specific conflicts you discovered between AIF360 and Fairlearn

### Round 4: Feasibility & Risk (5 min)
- [ ] What's your biggest risk?
- [ ] Walk through the cut-list in order
- [ ] What's the non-negotiable core?
- [ ] How are you splitting work between two people?

### Round 5: Rapid Fire — Numbers (3 min)
- [ ] How many images in FairFace?
- [ ] How many intersectional cells?
- [ ] What's $\alpha$?
- [ ] How many bootstrap resamples?
- [ ] How many research claims? How many invalidated?
- [ ] What are the 4 metrics' fair values?
- [ ] When does EU AI Act Article 10 take effect?

---

> [!TIP]
> **Pre-Defense Ritual:** The morning of the defense, re-read only this section and the [Numbers table](#7-numbers-you-must-know-cold). Don't try to memorize new material the day of. You already know the project — the defense is about communicating it clearly under pressure.

> [!IMPORTANT]
> **Division of Labor for Presentation:** Decide in advance who presents which slides. A natural split:
> - **Aaradhya:** Problem & motivation, architecture, fairness engine, statistical rigor, explainability (Slides 2–4, 9–13)
> - **Tisha:** Literature review, reporting, regulatory mapping, schedule, descoping (Slides 5–8, 14–17)
> - **Both:** Conclusion, Q\&A (Slides 18–20)
>
> Practice transitions between speakers — smooth handoffs signal team cohesion.
