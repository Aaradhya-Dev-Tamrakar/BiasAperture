# BiasAperture — Proposal Defense Preparation Guide

**Defending:** _BiasAperture: A Diagnostic and Evaluative Framework for Auditing Demographic Bias in Facial Analysis Systems_  
**Presenters:** Aaradhya Dev Tamrakar & Tisha Manandhar  
**Supervisor:** Shreejan Kisee (TA, Fusemachines AI Fellowship)  
**Program:** Fusemachines AI Fellowship (AIF) 2026 / Department of Electronics and Computer Engineering, Thapathali Campus, IOE

---

## Table of Contents

1. [Defense Format & Strategy](#1-defense-format--strategy)
2. [Slide Deck Outline (15–20 slides)](#2-slide-deck-outline-1520-slides)
3. [Slide-by-Slide Script & Talking Points](#3-slide-by-slide-script--talking-points)
4. [The Novelty Question — Your Most Important Defense](#4-the-novelty-question--your-most-important-defense)
5. [Anticipated Hard Questions & Scripted Answers (32 Questions)](#5-anticipated-hard-questions--scripted-answers-32-questions)
6. [Traps to Avoid](#6-traps-to-avoid)
7. [Numbers You Must Know Cold](#7-numbers-you-must-know-cold)
8. [Mock Grilling Checklist](#8-mock-grilling-checklist)

---

## 1. Defense Format & Strategy

### What a Proposal Defense Is

A proposal defense is **not** a completed results presentation. You are convincing the panel of three core pillars:

| Question the Panel Asks                     | What They Want to See                                                                                |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| **Is this problem real?**                   | A clear gap in existing tools, grounded in literature and comparative reviews                        |
| **Is the proposed solution well-designed?** | Sound architecture, locked schemas, harmonized math, robust statistical safeguards                   |
| **Can this team execute it?**               | Realistic schedule, clear work breakdown, pre-verified contracts, and an explicit descoping strategy |

### Your Strategic Advantage

You have completed an extensive research verification and specification phase:

> **Framing line:** "We have not just proposed what we will build — we have verified the foundational assumptions we are building on. We tracked 20 active research claims through an auditable claim ledger, formally invalidated 5 initial hypotheses before they could cause architectural rework, harmonized mathematical conflicts between libraries, and codified 22 contract and known-answer tests. We have verified the assumptions and locked the methodology; core implementation and empirical benchmark validation are the next phase."

### Presentation Time Budget

| Section                      | Time        | Notes                                                                                   |
| ---------------------------- | ----------- | --------------------------------------------------------------------------------------- |
| Introduction & Problem       | 3 min       | Hook with Gender Shades disparity finding, frame the workflow gap                       |
| Literature Review            | 3 min       | Synthesis of foundational works & comparative audit of 7 tools                          |
| Objectives & Scope           | 2 min       | 5 specific objectives, strictly diagnostic boundary, what is NOT in scope               |
| Architecture & Methodology   | 5 min       | Modular pipeline, Core Four metrics, mathematical harmonization, statistical safeguards |
| Regulatory Alignment         | 2 min       | Technical audit infrastructure mapped to EU AI Act Art. 10 & NIST AI RMF                |
| Schedule & Feasibility       | 2 min       | WBS, Gantt schedule, 5-tier descoping cut-list                                          |
| Conclusion & Q\&A Transition | 1 min       | Reiterate diagnostic scope, invite examiner questions                                   |
| **Total Presentation**       | **~18 min** | Leave 10–15 min for Q\&A                                                                |

---

## 2. Slide Deck Outline (15–20 slides)

### Slide 1: Title Slide

- Project title, authors, supervisor, institutional affiliation, date
- BiasAperture logo / header

### Slide 2: The Problem — A Documented Disparity

- **"34.7% vs 0.8%"** — Buolamwini & Gebru (2018) _Gender Shades_ intersectional error rate disparity
- Core observation: commercial facial analysis systems exhibit severe demographic accuracy disparities
- Core challenge: our review did not identify an existing reusable open-source platform that combines this complete diagnostic workflow for facial analysis auditing

### Slide 3: Regulatory Alignment & Technical Context

- The EU AI Act (Regulation EU 2024/1689) applies in stages, with Article 10 (Data and data governance) and high-risk requirements in Chapter III scheduled for phased applicability under Article 113 (e.g., December 2027 for Annex III, August 2028 for Annex I)
- Certain biometric categorization systems based on sensitive or protected attributes are classified as high-risk under Annex III, subject to the Act's broader provisions and prohibitions (Article 5)
- NIST AI Risk Management Framework (AI RMF 1.0) provides a complementary voluntary measurement taxonomy
- **Implication:** Technical audit infrastructure aligned with relevant data governance and bias-assessment requirements is increasingly critical

### Slide 4: Problem Statement (Formal)

> "There is an engineering gap between a mature body of fairness metrics and the availability of a reusable, standards-aligned software platform that operationalises this research into a repeatable auditing workflow for facial analysis systems."

### Slide 5: Literature Review Summary Table

- Synthesis table covering foundational literature:
  - Buolamwini & Gebru (2018) → motivates intersectional demographic auditing
  - Hardt et al. (2016) → formalizes Equalized Odds and Equal Opportunity criteria
  - Watkins et al. (2022) → critiques unadjusted ratio thresholds → motivates statistical safeguards
  - Kärkkäinen & Joo (2021) → provides FairFace balanced 7-race benchmark dataset
  - Dehdashtian et al. (2024) → catalogues diagnostic vs. mitigation divide

### Slide 6: The Engineering Gap (Comparative Landscape Audit)

- 7-tool feature matrix: Aequitas, Fairlearn, AIF360, Google WIT, JFAM, FAT Forensics, FairTest
- Feature columns: Vision-native taxonomy | Heterogeneous cross-checking | Statistical support guards | Targeted explainability | Regulatory traceability | Self-contained offline report
- **Key finding:** Among the seven tools included in our comparative review, we did not identify a system integrating all of these capabilities into a single facial-analysis audit workflow

### Slide 7: General & Specific Objectives

- **General Objective:** Design a modular diagnostic and evaluative software platform, BiasAperture, that systematically identifies demographic accuracy disparities in facial analysis models and reports them in a standardized, regulator-legible format
- **5 Specific Objectives:**
  1. Modular ingestion architecture for models and precomputed prediction files
  2. Heterogeneous backend cross-checking (Fairlearn + AIF360) with rigorous statistical testing
  3. Standardized exportable HTML report (Model Cards & Datasheets structure)
  4. Benchmark validation against FairFace (97,698 labeled images)
  5. Technical traceability mapping to EU AI Act Art. 10 and NIST AI RMF Measure functions

### Slide 8: Scope & Limitations — The Diagnostic Boundary

- **In Scope:** Ingest $\to$ Profile $\to$ Measure Disparities $\to$ Statistical Testing $\to$ Targeted Explainability $\to$ Compliance Report
- **Explicitly Out of Scope:** Model retraining, fine-tuning, loss debiasing, synthetic image generation
- **Principle:** Diagnostic integrity requires separation of concerns from model remediation

### Slide 9: System Architecture Diagram

- High-level architecture: Ingestion $\to$ Model Interface $\to$ Fairness Engine $\to$ Explainability $\to$ Report Generation $\to$ CLI Orchestration
- Contract data structures: `SubjectRecord` $\to$ `MetricResult` $\to$ Standalone HTML Report

### Slide 10: The Core Four Disparity Metrics

- Table of primary disparity metrics:
  - **Demographic Parity Difference (DPD):** $\max_a P(\hat{Y}=1 \mid A=a) - \min_a P(\hat{Y}=1 \mid A=a)$ (Fair value: $0.0$)
  - **Equalized Odds Difference (EOD):** $\max(\Delta\text{TPR}, \Delta\text{FPR})$ (Fair value: $0.0$)
  - **Equal Opportunity Difference (EOP):** $\max_a \text{TPR}_a - \min_a \text{TPR}_a$ (Fair value: $0.0$)
  - **Disparate Impact Ratio (DIR):** $\min_a P(\hat{Y}=1 \mid A=a) / \max_a P(\hat{Y}=1 \mid A=a)$ (Fair value: $1.0$)
- Class policy: Macro-OvR binarization for multi-class targets; DIR evaluated per class without macro-averaging

### Slide 11: Heterogeneous Backend Harmonization

- **EOD Mathematical Divergence:** Fairlearn calculates worst-case gap $\max(\Delta\text{TPR}, \Delta\text{FPR})$, whereas native AIF360 calculates average gap $\frac{1}{2}(\Delta\text{TPR} + \Delta\text{FPR})$ $\to$ harmonized to worst-case gap per Hardt et al.
- **EOP Sign Mismatch:** AIF360 returns signed difference $\in [-1, 1]$, whereas Fairlearn defines unsigned difference $\ge 0$ $\to$ harmonized via absolute value adapter
- **DIR Bounded Formulation:** Evaluated as symmetric ratio $\min/\max \in [0, 1]$ to avoid arbitrary "privileged" group selection across 7 non-ordinal race categories

### Slide 12: Statistical Safeguards — Three-Tier Inferential Defense

1. **Sample-Size Screening & Support Guards:** Minimum screening invariant of $n \ge 30$, alongside metric-specific positive/negative support requirements ($n_{Y=1, a} \ge 5$ for EOP; $n_{Y=1, a} \ge 5 \land n_{Y=0, a} \ge 5$ for EOD)
2. **Hypothesis Testing & FWER Control:** $\chi^2$ test of independence (Fisher's exact test fallback for low expected cell counts) with Holm-Bonferroni step-down correction across intersectional hypothesis families
3. **Stratified Vectorized BCa Bootstrap:** Stratified within-subgroup resampling ($B \ge 1,000$) with empirical percentile fallback for extreme acceleration ($|a| > 0.5$), degenerate bias correction, or interval boundary violations, enforcing a $\ge 90\%$ valid-replicate engineering criterion

### Slide 13: Explainability — Targeted Proxy Evidence Analysis

- Triggered selectively on statistically significant disparities ($p < 0.05, n \ge 30$) to preserve computational efficiency
- `PartitionExplainer` default for black-box prediction files; `GradientExplainer` fast-path for direct PyTorch models
- Skin-tone colorimetry via Individual Typology Angle ($\text{ITA} = \arctan((L^* - 50)/b^*) \times 180/\pi$)
- **Theoretical Bounds:** Grounded in Bilodeau et al. (2022) impossibility theorems — feature attribution provides exploratory proxy evidence, not causal proof

### Slide 14: Regulatory Traceability Mapping

- Direct mapping of technical outputs to Article 10 components (10(2) Governance, 10(3) Data Quality & Support, 10(4) Context, 10(5) Bias Examination)
- Alignment with NIST AI RMF 1.0 **Measure** functions (Measure 2.11 bias quantification, Measure 1.1 unquantifiable risk documentation via insufficient-sample flags, Measure 1.3 software implementation cross-checking)

### Slide 15: Report Output — Self-Contained Offline HTML

- Mitchell et al. (2019) Model Cards + Gebru et al. (2018) Datasheets structure
- Flat single-file HTML with embedded inline CSS and base64-encoded visualizations
- Zero external CDN or network requests to enable offline auditor sharing and privacy compliance

### Slide 16: Work Breakdown & Schedule

- 8 work packages structured for concurrent development:
  - Stream A (Data Ingestion & Matrix Construction) ‖ Stream B (Report Scaffolding)
  - Stream C (Fairness Engine & Statistics) ‖ Stream D (Explainability & Orchestration)
- Milestone progression: M1 (Schema Lock) $\to$ M2 (Scaffolds) $\to$ M3 (Core Engines) $\to$ M4 (Integration & Benchmark Validation)

### Slide 17: Pre-Defined Descoping Strategy (Cut-List)

- Formal 5-tier descoping sequence:
  1. Web UI $\to$ retain CLI only
  2. UTKFace secondary dataset $\to$ retain FairFace primary benchmark only (_formally executed per Cut #2_)
  3. PDF export $\to$ retain offline HTML report only
  4. Direct in-process model inference $\to$ retain precomputed predictions file ingestion only
  5. AIF360 backend $\to$ retain Fairlearn backend only (emergency fallback)
- **Non-negotiable core:** Data ingestion, one model interface, fairness engine, one report format, and scope-boundary statement

### Slide 18: Verification & Contract Testing

- Milestone M1 schema locked in code (`SubjectRecord`, `MetricResult`)
- 22 automated research-contract and known-answer tests already implemented
- Deterministic 8-record ground-truth baseline ($\text{DPD}=0.500, \text{EOD}=0.500, \text{EOP}=0.500, \text{DIR}=0.3333$)
- Documented Claim Ledger tracking 20 active claims and 5 invalidated hypotheses

### Slide 19: Conclusion

- Summary: BiasAperture operationalizes fairness auditing into a standardized, repeatable engineering pipeline
- "We have verified the foundational assumptions and locked the contracts; implementation and empirical benchmark validation are the next phase."

### Slide 20: Questions & Discussion

- Project title, author contacts, repository link

---

## 3. Slide-by-Slide Script & Talking Points

### Opening (Slide 2) — The Hook

> "In 2018, Buolamwini and Gebru’s _Gender Shades_ study revealed that commercial gender-classification systems exhibited an error rate of 34.7% for darker-skinned females compared to just 0.8% for lighter-skinned males. That finding catalyzed the algorithmic fairness field. However, in practice, demographic audits remain predominantly one-off, manual academic efforts. Our review did not identify a reusable open-source platform that integrates this complete audit workflow for facial analysis systems. That is the engineering gap BiasAperture is designed to address."

### Problem Statement & Regulatory Context (Slides 3–4)

> "This requirement is increasingly relevant under emerging AI governance frameworks. The EU AI Act is phasing in regulatory requirements, with Article 10 data-governance and bias-examination provisions scheduled under the Article 113 timetable. Certain biometric categorization systems classifying sensitive characteristics are identified as high-risk under Annex III, subject to the Act's broader provisions. BiasAperture provides technical audit infrastructure aligned with these data-governance and bias-assessment requirements, translating high-level regulatory mandates into concrete statistical metrics and documentation."

### Architecture (Slide 9) — The Pipeline

> "BiasAperture is architected as a modular diagnostic pipeline. Demographic data and model outputs enter through the ingestion module and are validated against our locked schema. Predictions are obtained either from a local PyTorch model or batch-ingested from a standard CSV or JSON predictions file. The core engine calculates four disparity metrics using heterogeneous implementation cross-checking across Fairlearn and AIF360. Where statistically significant disparities occur, the current explainability implementation, using demographic-dummy surrogate attribution, provides visual proxy evidence; richer spatial SHAP and ITA analysis remain deferred. Finally, a self-contained offline HTML report is compiled using Model Cards and Datasheets conventions."

### Harmonization (Slide 11) — Engineering Novelty in Practice

> "A key example of why reusable integration requires deeper engineering than simple script concatenation is backend harmonization. When evaluating Equalized Odds Difference, Fairlearn implements the worst-case gap—the maximum of the TPR and FPR disparities—following Hardt et al. In contrast, native AIF360 computes the arithmetic mean of those two disparities. On identical data, this creates an artificial numerical discrepancy. We reconciled these mathematical differences in our adapter layer, ensuring consistent, standardized metric definitions across backends."

### Statistical Safeguards (Slide 12) — Inferential Credibility

> "To ensure reported disparities reflect genuine systematic patterns rather than sampling noise, we implement three layers of statistical safeguards. First, a minimum sample-size screening invariant of $n \ge 30$, combined with metric-specific cell support checks. Second, chi-squared tests of independence with Holm-Bonferroni step-down correction to control family-wise error rate across intersectional hypothesis families. Third, stratified within-subgroup BCa bootstrap confidence intervals from at least 1,000 resamples, with automated percentile fallback policies for extreme acceleration or boundary violations."

### Descoping (Slide 17) — Feasibility and Risk Planning

> "To guarantee feasibility within our timeline, we established an explicit 5-tier descoping sequence in advance. If timeline constraints arise, secondary features such as the Web UI or PDF export are dropped first. For example, during research verification, we formally descoped UTKFace under Cut-List item #2 due to documented 3-of-7 race taxonomy collapse and noisy model-estimated age labels. The diagnostic core—ingestion, predictions interface, fairness engine, and compliance report—is preserved under all circumstances."

---

## 4. The Novelty Question — Your Most Important Defense

When examiners ask: _"Aren't you just combining existing toolkits like Fairlearn, AIF360, and SHAP?"_

### What NOT to Say

- ❌ _"We invented brand new fairness metrics."_ (False — metrics are established in literature).
- ❌ _"No other tool can compute these numbers."_ (False — Fairlearn/AIF360 compute tabular metrics).

### The 5-Step Defense Framework

1. **Acknowledge the Foundational Tools:**

   > "Fairlearn and AIF360 are established, high-quality libraries, and the current explainability implementation uses demographic-dummy surrogate attribution, with richer spatial SHAP and ITA analysis remaining deferred. We do not claim to have invented new fairness metrics or new statistical tests."

2. **Identify the Domain Workflow Friction:**

   > "However, existing fairness toolkits are predominantly designed for tabular data with generalized schemas. Facial analysis models operate in computer vision pipelines involving multi-class, intersectional demographic taxonomies (such as FairFace's 7 races, 9 age groups, and 2 genders). Bridging these requires custom schema curation, multi-class One-vs-Rest binarization, and image-specific handling that practitioners currently have to build from scratch."

3. **Demonstrate Discovered Mathematical Conflicts:**

   > "Furthermore, heterogeneous libraries do not natively agree on mathematical definitions. Fairlearn and AIF360 compute mathematically divergent definitions of Equalized Odds Difference (worst-case max-gap vs. average gap) and use conflicting sign conventions for Equal Opportunity Difference. Harmonizing these differences into an auditable, consistent contract is an essential engineering contribution."

4. **Use the Tooling Analogy:**

   > "Much like standard build systems or containerization platforms did not invent compilers or kernel namespaces, their contribution was eliminating workflow friction, unifying disparate interfaces, and making existing capabilities reliably reusable. BiasAperture provides that unified diagnostic layer for facial analysis auditing."

5. **Summarize the Concrete Contribution:**
   > "Instead of each practitioner independently implementing schema conversion, metric harmonization, statistical adequacy guards, proxy explainability triggers, and regulatory crosswalks, BiasAperture packages these verified decisions into a single, reproducible workflow."

---

## 5. Anticipated Hard Questions & Scripted Answers (32 Questions)

### Category A: Scope & Novelty

**Q1: "Why not just use Fairlearn directly for this evaluation?"**

> "Fairlearn already provides intersectional sensitive-feature assessment. Our gap is not that Fairlearn cannot represent multiple demographic groups. The gap is that BiasAperture builds a complete facial-analysis audit workflow around those capabilities, including FairFace-specific ingestion, harmonization with a second backend, statistical adequacy controls, targeted explainability, and audit reporting."

**Q2: "What is the primary contribution if you are not proposing new fairness algorithms?"**

> "Our contribution is reusable integration and methodological standardization. We bridge computer vision taxonomies with fairness metrics, harmonize mathematical divergences between existing libraries, enforce statistical screening guards and bootstrap uncertainty estimation, and generate audit reports with explicit regulatory traceability."

**Q3: "Why is the system strictly diagnostic? Why not incorporate bias mitigation?"**

> "Diagnostic evaluation and model remediation are distinct engineering concerns. As highlighted in Dehdashtian et al.'s survey, coupling mitigation directly into an auditing tool risks compromising the independence and objectivity of the audit. By remaining strictly diagnostic, BiasAperture provides an unbiased measurement baseline that external mitigation workflows can reliably consume."

**Q4: "Is this a software engineering project or an applied AI research project?"**

> "It is an applied AI engineering project that operationalizes established fairness research. It addresses the practical software and statistical challenges of making theoretical metrics reusable, statistically reliable, and regulator-legible in computer vision workflows."

**Q5: "Is an 8-week timeline realistic for a two-person team to deliver this framework?"**

> "Yes. We have completed the research verification and schema lock phase, pre-verifying 20 claims and invalidating 5 flawed hypotheses. Our architecture separates concerns into concurrent streams (ingestion/reporting in parallel with fairness/explainability) against a locked data contract. Furthermore, our pre-defined 5-tier descoping strategy ensures the core diagnostic platform delivers reliably on schedule."

---

### Category B: Statistical Rigor & Methodology

**Q6: "Why did you select $n \ge 30$ as a sample size threshold? Is this a universal statistical law?"**

> "We do not claim that $n \ge 30$ is a universal statistical validity threshold. It is a project-defined minimum screening invariant. We then apply metric-specific support requirements and expected-cell-count checks. The threshold was adopted conservatively to prevent extremely undersized subgroup estimates from entering the primary disparity analysis."

**Q7: "When do you use the Chi-squared test versus Fisher's Exact Test?"**

> "Chi-squared tests of independence evaluate independence across demographic contingency tables. However, when expected cell counts fall below 5 in sparse intersectional $2 \times 2$ cells, we apply Fisher's Exact Test to prevent test statistic distortion."

**Q8: "Why implement a custom bootstrap engine rather than using `scipy.stats.bootstrap` directly?"**

> "We evaluated SciPy's bootstrap functionality, but chose a custom implementation because BiasAperture requires fixed observed subgroup composition, simultaneous K-group fairness-statistic computation, deterministic seeded resampling, and project-specific invalid-replicate and fallback policies. The custom engine therefore implements our required estimand and contract rather than merely duplicating a library default."

**Q9: "Why did you choose the Holm-Bonferroni procedure over Benjamini-Hochberg FDR?"**

> "In regulatory and compliance auditing, controlling the Family-Wise Error Rate (FWER) is critical to prevent reporting false positive disparities. The Holm-Bonferroni step-down procedure controls FWER at $\alpha = 0.05$ while offering strictly greater statistical power than the standard Bonferroni correction across our 126 intersectional cells."

**Q10: "How does the system evaluate multi-class classification tasks?"**

> "For multi-class targets ($M > 2$), the task is decomposed into $M$ binary One-vs-Rest (OvR) problems. DPD, EOD, and EOP are evaluated per binary task and macro-averaged across classes. In contrast, Disparate Impact Ratio is reported per class and is explicitly not macro-averaged, as averaging non-linear ratios introduces mathematical distortion."

**Q11: "What happens if no subgroup receives a positive prediction (DIR denominator = 0)?"**

> "When $\max_a(\text{selection rate}_a) = 0$, meaning no subgroup receives positive predictions, DIR is defined by policy contract as $1.0$ accompanied by an `absolute_selection_warning = True` flag, since no comparative selection disparity exists. When $\min = 0$ and $\max > 0$, DIR is $0.0$. These boundary contracts are codified in our automated tests."

**Q12: "Why choose SHAP over other explainability methods like LIME?"**

> "The current explainability implementation uses demographic-dummy surrogate attribution; richer spatial SHAP and ITA analysis remain deferred. We selected SHAP because it provides a theoretically grounded additive attribution framework and supports the black-box explanation path required by our prediction-file interface. The choice is architectural, not a claim that SHAP produces causal explanations."

**Q13: "Can SHAP feature attributions prove that a model is biased due to facial features?"**

> "No, and we explicitly document this limitation. In accordance with Bilodeau et al. (2022) impossibility theorems, additive feature attribution methods cannot guarantee distinguishing spurious correlations from causal features in neural networks. The current explainability implementation uses demographic-dummy surrogate attribution and provides exploratory proxy evidence, not causal proof; richer spatial SHAP and ITA analysis remain deferred."

---

### Category C: Datasets & Preprocessing

**Q14: "Why is FairFace selected as the primary benchmark dataset?"**

> "FairFace was specifically constructed for balanced demographic distribution across 7 race groups, 9 age bins, and 2 genders, totaling 97,698 human-annotated images on disk. Its granularity matches the multi-group intersectional schema required for our evaluation."

**Q15: "Why was UTKFace descoped from the primary evaluation?"**

> "Our preliminary research verification revealed two major limitations: UTKFace collapses Asian subcategories into a single class (supporting only 3 of our 7 locked race categories) and relies on DEX model-estimated age labels rather than human annotations. We formally descoped it under Cut-List item #2 to preserve schema and data integrity."

**Q16: "Why use `dlib` 5-point alignment instead of MTCNN for preprocessing?"**

> "Official FairFace baseline models were trained using `dlib` CNN face detection and 5-point landmark chip extraction ($300 \times 300$, $0.25$ padding). Using MTCNN would introduce detector-induced domain shift between evaluation and model training."

**Q17: "Is a 7-race taxonomy sufficient to capture global demographic diversity?"**

> "No static taxonomy can capture all human demographic nuances. FairFace's 7-category taxonomy represents the most granular balanced public benchmark currently available. BiasAperture's schema is designed to allow taxonomy extension if more comprehensive benchmarks emerge."

---

### Category D: Architecture & Implementation

**Q18: "Why implement dual fairness backends if one toolkit can calculate the metrics?"**

> "Dual backend execution provides heterogeneous software implementation cross-checking. Running both Fairlearn and AIF360 against the same input ensures that results do not depend on library-specific implementation artifacts or unhandled internal edge cases."

**Q19: "Which software design patterns are utilized in the architecture?"**

> "We employ six design patterns aligned with our descoping cut-list: Strategy (interchangeable fairness backends), Adapter (dual-mode model interfaces), Builder (multi-stage data ingestion), Factory (report generation formats), Template Method (Model Card structure), and Facade (CLI orchestration)."

**Q20: "Why prioritize a Command-Line Interface (CLI) over a graphical Web UI?"**

> "A CLI provides a scriptable, reproducible interface suitable for automated audit pipelines and CI/CD integration. Graphical interfaces represent presentation layers that can be added without altering analytical core functionality."

**Q21: "Why use custom Jinja2 templates instead of Google's `model-card-toolkit`?"**

> "An audit of `model-card-toolkit` revealed heavy dependencies on Apache TFX and TensorFlow Model Analysis (TFMA), which create installation fragility. Custom Jinja2 templates achieve complete structural alignment with Mitchell et al. (2019) while maintaining a lightweight dependency footprint."

---

### Category E: Regulatory Alignment & Ethics

**Q22: "How does BiasAperture align with the EU AI Act?"**

> "BiasAperture implements technical audit controls aligned with Article 10 data governance requirements: Article 10(2) design and provenance documentation, Article 10(3) statistical adequacy and representation checks, and Article 10(5) bias examination over demographic categories."

**Q23: "Does using BiasAperture certify legal compliance under the EU AI Act?"**

> "No. BiasAperture provides technical diagnostic evidence and documentation to support compliance examinations. Legal compliance certification involves organizational, operational, and legal determinations beyond the scope of technical tooling."

**Q24: "How does the framework address privacy concerns regarding demographic data?"**

> "Our data governance protocol restricts processing to non-commercial research licensing, executes all computation locally without external network transmission, outputs aggregate statistical metrics, and applies facial-chip masking to prevent individual re-identification."

---

### Category F: Feasibility, Reliability & Risk

**Q25: "What is the primary technical risk in the upcoming implementation phase?"**

> "The primary technical risk is handling computational runtime for full-dataset bootstrap resampling and explainability. We mitigate this through vectorized bootstrap implementations, stratified development subsets ($n=5,000$), and conditional triggering of attribution only on flagged disparities; the current explainability implementation uses demographic-dummy surrogate attribution, with richer spatial SHAP and ITA analysis remaining deferred."

**Q26: "How do you guarantee that future library updates will not break metric calculations?"**

> "All dependencies are pinned via deterministic lockfiles (`uv.lock`), and all metric implementations are continuously validated against our deterministic 8-record known-answer test fixtures."

**Q27: "What occurs if bootstrap confidence intervals produce bounds outside $[0, 1]$?"**

> "Our statistical engine enforces explicit validity rules: if BCa acceleration or bias adjustments project bounds outside $[0, 1]$, the system automatically logs a diagnostic event and falls back to empirical percentile bootstrap intervals."

**Q28: "Can BiasAperture audit models trained on architectures other than ResNet?"**

> "Yes. The `PredictionsFileInterface` operates on precomputed CSV/JSON prediction exports, decoupling the auditing framework from the underlying model architecture, framework, or runtime environment."

---

### Category G: Research Integrity & Project Status

**Q29: "How do you ensure the validity of research specifications developed during the design phase?"**

> "Every research claim is tracked in our auditable Claim Ledger. Claims must progress from assertion through primary-source inspection, tensor probing, and reproduction via automated unit tests. Currently, 20 active claims are verified or reproducible, and zero unverified assertions remain."

**Q30: "Why do you maintain a register of invalidated hypotheses?"**

> "Documenting refuted hypotheses (such as MTCNN preprocessing assumptions and native library math discrepancies) maintains research transparency, prevents recurring mistakes, and provides empirical justification for our architectural decisions."

**Q31: "How are the mathematical implementations of fairness metrics verified?"**

> "We use a multi-tiered verification hierarchy: hand-calculated known-answer contracts on synthetic matrices, scale-invariance testing across replicated samples, and cross-backend comparison across harmonized libraries."

**Q32: "What is the current status of the codebase as of this proposal defense?"**

> "We have completed Milestone M1: demographic and metric schemas are locked, 22 research-contract and known-answer tests are passing, and foundational ingestion and model interfaces are scaffolded. The subsequent phase focuses on core engine implementation (WP2–WP5) and full benchmark validation."

---

## 6. Traps to Avoid

### ❌ Trap 1: Overclaiming Novelty

- **Don't say:** _"No one has ever built a fairness auditing system before."_
- **Do say:** _"Among the seven tools evaluated in our comparative review, we did not identify a platform that integrates this complete facial analysis audit workflow."_

### ❌ Trap 2: Oversimplifying the Engineering Effort

- **Don't say:** _"We are simply piping Fairlearn into AIF360."_
- **Do say:** _"We harmonized underlying mathematical divergences between toolkits and implemented statistical screening and bootstrap safeguards."_

### ❌ Trap 3: Claiming Causal Explanations

- **Don't say:** _"SHAP explains why the model is biased."_
- **Do say:** _"The current explainability implementation uses demographic-dummy surrogate attribution, which provides feature attributions that highlight visual proxy correlations associated with detected disparities, subject to known non-causal theoretical bounds; richer spatial SHAP and ITA analysis remain deferred."_

### ❌ Trap 4: Overstating Regulatory Certification

- **Don't say:** _"BiasAperture guarantees EU AI Act compliance."_
- **Do say:** _"BiasAperture provides technical diagnostic evidence supporting the examination of Article 10 requirements."_

### ❌ Trap 5: Misrepresenting Project Phase

- **Don't say:** _"We have already completed the full benchmark audit."_
- **Do say:** _"We have completed research verification, locked our contracts, and implemented acceptance tests; core pipeline execution and full benchmark validation constitute the upcoming phase."_

### ❌ Trap 6: Misattributing Sample-Size Invariants

- **Don't say:** _"The Central Limit Theorem proves that $n \ge 30$ ensures statistical validity."_
- **Do say:** _"The $n \ge 30$ threshold is a conservative screening invariant to filter out unstable, undersized subgroups before applying support checks and hypothesis tests."_

---

## 7. Numbers You Must Know Cold

| Metric / Parameter           | Value / Specification                                                     | Context / Primary Source                                                           |
| ---------------------------- | ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| **Gender Shades Disparity**  | 34.7% (darker female) vs 0.8% (lighter male)                              | Buolamwini & Gebru (2018)                                                          |
| **FairFace Labeled Dataset** | 97,698 images (86,744 train + 10,954 val)                                 | Released disk total (Claim R-002)                                                  |
| **Intersectional Subgroups** | 126 cells ($7 \text{ race} \times 2 \text{ gender} \times 9 \text{ age}$) | Locked schema taxonomy                                                             |
| **Core Four Metrics**        | DPD, EOD, EOP, DIR                                                        | Functional Requirement FR-003                                                      |
| **Sample Size Invariant**    | $n \ge 30$                                                                | Non-Functional Requirement NFR-003                                                 |
| **Bootstrap Resamples**      | $B \ge 1,000$ iterations                                                  | Non-Functional Requirement NFR-002                                                 |
| **Significance Level**       | $\alpha = 0.05$                                                           | Non-Functional Requirement NFR-001                                                 |
| **FairFace Race Classes**    | 7 categories                                                              | White, Black, Latino_Hispanic, East Asian, Southeast Asian, Indian, Middle Eastern |
| **FairFace Age Bins**        | 9 bins                                                                    | 0-2, 3-9, 10-19, 20-29, 30-39, 40-49, 50-59, 60-69, 70+                            |
| **Research Claims Tracked**  | 20 active + 5 invalidated                                                 | Auditable Claim Ledger (`CLAIM_LEDGER.md`)                                         |
| **Contract / Unit Tests**    | 22 tests across 6 test modules                                            | Milestone M1 test suite                                                            |
| **Evaluated Toolkits**       | 7 tools audited in comparative review                                     | Aequitas, Fairlearn, AIF360, WIT, JFAM, FAT Forensics, FairTest                    |
| **ResNet-34 Output Layer**   | 18 units (`torch.Size([18, 512])`)                                        | Multi-task slice: [0:7], [7:9], [9:18] (Claim R-001)                               |
| **EOD Divergence Example**   | Fairlearn: 0.3000 (max) vs AIF360: 0.2000 (mean)                          | Verified math discrepancy (Claim R-005)                                            |
| **Small-Sample Distortion**  | $\sim 3\times$ (FairFace val) to $\sim 45\times$ (synthetic outlier)      | Distortion from unfiltered $n < 30$ (Claim R-008)                                  |
| **Descoping Tiers**          | 5 formal tiers                                                            | Web UI $\to$ UTKFace $\to$ PDF $\to$ In-Process $\to$ AIF360                       |
| **Known-Answer Proof**       | $\text{DPD}=0.500, \text{EOD}=0.500, \text{EOP}=0.500, \text{DIR}=0.3333$ | 8-record deterministic baseline (Claim R-020)                                      |

---

## 8. Mock Grilling Checklist

### Round 1: Foundations & Scope (5 min)

- [ ] Clearly define BiasAperture and the specific gap it addresses.
- [ ] State what is explicitly out of scope (mitigation, retraining).
- [ ] Explain why diagnostic separation of concerns is necessary.

### Round 2: Technical & Statistical Depth (10 min)

- [ ] Define the Core Four disparity metrics without reading notes.
- [ ] Explain the mathematical difference between Fairlearn and AIF360 for EOD.
- [ ] Explain the role of the $n \ge 30$ screening invariant without citing the CLT as proof.
- [ ] Describe the zero-denominator policy for Disparate Impact Ratio.
- [ ] Explain why BCa bootstrap with percentile fallback was implemented.
- [ ] Explain why Holm-Bonferroni correction is used for intersectional cells.

### Round 3: Novelty & Integration Defense (5 min)

- [ ] Deliver the 5-step response to "Isn't this just combining existing tools?".
- [ ] Give three concrete examples of library divergences or integration friction.
- [ ] Defend why custom integration represents valid engineering novelty.

### Round 4: Feasibility, Risks & Roadmap (5 min)

- [ ] Walk through the 5-tier descoping sequence in order.
- [ ] Identify the non-negotiable architectural core.
- [ ] Explain how task ownership is divided across workstreams.

### Round 5: Rapid-Fire Metrics & Constants (3 min)

- [ ] State FairFace dataset count on disk (97,698).
- [ ] State total intersectional cells (126).
- [ ] State alpha value ($\alpha = 0.05$) and minimum bootstrap resamples ($B \ge 1,000$).
- [ ] State the fair values for all four disparity metrics ($0.0, 0.0, 0.0, 1.0$).
