# BiasAperture — Presentation Guide & Verbatim Speaker Notes

**Project Title:** BiasAperture: A Diagnostic and Evaluative Framework for Auditing Demographic Bias in Facial Analysis Systems  
**Authors / Presenters:** Aaradhya Dev Tamrakar & Tisha Manandhar  
**Supervisor:** Shreejan Kisee (Teaching Assistant, Fusemachines AI Fellowship)  
**Program:** Fusemachines AI Fellowship (AIF) 2026 / Department of Electronics & Computer Engineering, Thapathali Campus, IOE  
**Target Duration:** 15 minutes (Presentation) + 10–15 minutes (Panel Q&A and Scrutiny)

---

## Presentation Time Budget & Speaker Handover Map

| Slide # | Slide Title | Lead Speaker | Target Duration | Cumul. Time |
|:---:|---|:---:|:---:|:---:|
| **1** | Title Slide & Introductions | Aaradhya | 0:45 | 0:45 |
| **2** | Distributional Masking & The Problem | Aaradhya | 1:00 | 1:45 |
| **3** | Regulatory Imperative (EU AI Act / NIST) | Tisha | 1:00 | 2:45 |
| **4** | Landscape Analysis & The Engineering Gap | Aaradhya | 1:00 | 3:45 |
| **5** | Objectives & The Strict Diagnostic Boundary | Tisha | 1:00 | 4:45 |
| **6** | Modular Pipeline Architecture | Aaradhya | 1:00 | 5:45 |
| **7** | Design by Contract & $n < 30$ Invariant | Tisha | 0:45 | 6:30 |
| **8** | The Core Four Disparity Metrics | Aaradhya | 1:00 | 7:30 |
| **9** | Heterogeneous Backend Harmonization | Aaradhya | 1:00 | 8:30 |
| **10** | Three-Tier Statistical Inferential Defense | Aaradhya | 1:15 | 9:45 |
| **11** | Targeted Explainability & Proxy Bounds | Tisha | 0:45 | 10:30 |
| **12** | Empirical Validation Benchmark: FairFace | Tisha | 0:45 | 11:15 |
| **13** | Empirical Audit Findings ($N=10,954$) | Aaradhya | 1:00 | 12:15 |
| **14** | Offline Compliance Dossier (Model Cards) | Tisha | 0:45 | 13:00 |
| **15** | Single-Command CLI Orchestration | Aaradhya | 0:45 | 13:45 |
| **16** | Verification, Contract Tests & Claim Ledger | Aaradhya | 0:45 | 14:30 |
| **17** | Execution Schedule & 5-Tier Cut-List | Tisha | 0:45 | 15:15 |
| **18** | Summary of Core Contributions | Joint (A+T) | 0:30 | 15:45 |
| **19** | Conclusion & Q&A Transition | Joint (A+T) | 0:15 | 16:00 |

---

## Slide-by-Slide Verbatim Scripts

### Slide 1: Title Slide & Institutional Context
**Speaker: Aaradhya**
> *"Good morning, respected members of the evaluation panel, our supervisor Shreejan Kisee, and fellowship mentors. I am Aaradhya Dev Tamrakar, and alongside my colleague Tisha Manandhar, we present **BiasAperture** — a diagnostic and evaluative framework for auditing demographic bias in facial analysis systems. This project bridges fairness research and emerging regulatory frameworks by turning scattered mathematical metrics into an automated, standards-aligned auditing platform for computer vision."*

---

### Slide 2: High Aggregate Accuracy Masks Severe Subgroup Failure
**Speaker: Aaradhya**
> *"In 2018, Buolamwini and Gebru’s seminal Gender Shades study exposed a critical vulnerability in commercial computer vision: while facial analysis systems boasted aggregate accuracies exceeding 90%, they exhibited an error rate of 34.7% for darker-skinned females compared to just 0.8% for lighter-skinned males — an astounding 43-to-1 error disparity.  
Standard empirical risk minimization optimizes for majority mass, allowing catastrophic subgroup failures to be distributionally masked. In production systems like biometric KYC, automated border control, and surveillance, this creates severe real-world harm. Today, most audits remain manual, ad-hoc academic exercises. Industry lacks a reusable, vision-native software pipeline to continuously audit these disparities."*

---

### Slide 3: From Academic Critique to Legal Compliance
**Speaker: Tisha**
> *"Auditing demographic bias is no longer just an ethical preference; it is rapidly becoming a statutory legal requirement.  
Under the European Union AI Act, Article 10 mandates that training, validation, and testing datasets undergo rigorous governance and examination for biases likely to lead to discrimination. Biometric categorization systems that infer sensitive attributes like race, gender, and age are categorized as High-Risk AI under Annex III. Concurrently, the NIST AI Risk Management Framework establishes voluntary measurement standards under its Measure functions.  
Compliance cannot be demonstrated with informal, throwaway Jupyter notebooks. It demands formal, reproducible, tamper-evident software infrastructure that translates regulatory mandates into concrete statistical metrics."*

---

### Slide 4: Comparative Landscape Audit: The Workflow Gap
**Speaker: Aaradhya**
> *"To understand the state of the art, we conducted a systematic comparative review across seven existing bias auditing toolkits: Fairlearn, AIF360, Aequitas, Google What-If Tool, JFAM, FAT Forensics, and FairTest.  
As shown in our comparative matrix, existing toolkits are overwhelmingly tabular-first. They lack computer-vision-native demographic taxonomies, cannot handle multi-class One-vs-Rest binarization without ad-hoc scripts, and do not cross-check independent computation backends. Furthermore, none provide integrated sample-size screening invariants ($n \ge 30$) or generate self-contained, air-gapped HTML compliance dossiers mapped to Article 10.  
This reveals our formal problem statement: there is an engineering gap between mature theoretical fairness metrics and a reusable software platform that operationalizes them into a repeatable auditing workflow."*

---

### Slide 5: Objectives & The Strict Diagnostic Boundary
**Speaker: Tisha**
> *"To bridge this gap, our general objective is to design and build BiasAperture. We have structured our work around five specific functional objectives: modular ingestion of datasets and prediction interfaces, dual-backend computation across Fairlearn and AIF360, targeted explainability, self-contained offline reporting, and formal regulatory traceability.  
Crucially, we enforce a **strict diagnostic boundary**. BiasAperture is an independent diagnostic instrument: we ingest, profile, measure disparities, calculate confidence intervals, and report compliance. We explicitly do **not** perform model retraining, loss weight debiasing, or synthetic image generation. Following good scientific practice and the separation of concerns established by Dehdashtian et al., an auditor must remain an objective evaluator, not an optimizer of model weights."*

---

### Slide 6: Modular Pipeline Architecture
**Speaker: Aaradhya**
> *"BiasAperture is architected as five decoupled, cooperating modules governed by SOLID object-oriented design principles.  
Data and model outputs enter through the ingestion module, where annotations are normalized into our locked schema. Models are accessed through framework-agnostic adapters supporting batch prediction files or direct in-process PyTorch inference. The core analytical engine evaluates fairness metrics using the Strategy pattern, allowing interchangeable backends. When statistically significant disparities occur, targeted proxy attribution is triggered. Finally, a flat Jinja2 compiler produces a self-contained offline HTML dossier.  
Because high-level orchestration depends on abstract interfaces rather than vendor implementations, backends or file formats can be swapped without altering system correctness."*

---

### Slide 7: Design by Contract: The Locked Schema
**Speaker: Tisha**
> *"To ensure seamless collaboration between parallel development streams, our data contracts were locked at Milestone M1.  
Our fundamental datum is `SubjectRecord`, storing normalized 7-race, 9-age, and 2-gender categories alongside ground-truth and prediction labels. All outputs populate immutable `MetricResult` payloads.  
A cornerstone of our framework is the **$n < 30$ sample-size screening invariant**. Under the Central Limit Theorem, point estimates from small samples are statistically volatile. Any demographic slice with sample size $n < 30$ is strictly prohibited from publishing point estimates or confidence intervals. Its `MetricResult` automatically sets `insufficient_sample=True` and `metric_value=None`. This is an architectural integrity invariant, ensuring decision-makers are never misled by small-sample noise."*

---

### Slide 8: The Core Four Fairness Metrics
**Speaker: Aaradhya**
> *"BiasAperture formalizes the Core Four disparity metrics from fairness literature:  
Demographic Parity Difference and Disparate Impact Ratio measure selection parity — evaluating independence between model predictions and demographic attributes. Equal Opportunity Difference and Equalized Odds Difference measure error-rate parity — conditioning on ground-truth outcomes following Hardt et al.  
For multi-class targets, such as FairFace’s 9 age categories, we implement Macro One-vs-Rest binarization across all classes, while evaluating Disparate Impact per class without distortion."*

---

### Slide 9: Heterogeneous Backend Harmonization
**Speaker: Aaradhya**
> *"A key engineering contribution of our work is identifying and resolving mathematical divergences between established libraries.  
When computing Equalized Odds Difference on identical data, Fairlearn calculates the worst-case max gap across TPR and FPR disparities, whereas native AIF360 calculates their arithmetic mean. Furthermore, AIF360 produces a signed difference relative to an arbitrary privileged group, whereas Fairlearn uses an unsigned magnitude. Additionally, selecting an arbitrary 'privileged' group across 7 non-ordinal racial categories is conceptually ungrounded.  
BiasAperture reconciles these divergences in our adapter layer: we standardize EOD to the worst-case max gap, normalize EOP to absolute magnitude, and enforce a symmetric, bounded Disparate Impact Ratio ($\min/\max \in [0, 1]$). On identical inputs, both backends now yield identical, auditable numbers."*

---

### Slide 10: Three-Tier Statistical Inferential Defense
**Speaker: Aaradhya**
> *"As Watkins et al. (2022) demonstrated, disparity metrics are effect sizes, not standalone proof of bias. BiasAperture deploys a three-tier inferential defense to separate genuine systematic bias from random sampling variance.  
Tier 1 enforces minimum sample size ($n \ge 30$) and metric-specific positive cell support ($n_+ \ge 5$).  
Tier 2 performs Pearson’s $\chi^2$ contingency tests (with Fisher’s Exact fallback for small cell expectations), controlled by Holm-Bonferroni step-down correction to govern the Family-Wise Error Rate across multi-group hypothesis families.  
Tier 3 computes 95% Bias-Corrected and Accelerated (BCa) bootstrap confidence intervals from 1,000 resamples, stratified within subgroups to hold observed sample sizes fixed, backed by automated percentile fallback policies for degenerate acceleration or boundary violations."*

---

### Slide 11: Targeted Explainability & Proxy Attribution
**Speaker: Tisha**
> *"To prevent computational bottlenecks in high-throughput pipelines, explainability is triggered selectively: only demographic slices exhibiting statistically significant disparities ($p < 0.05$ and $n \ge 30$) undergo feature attribution.  
We deploy surrogate demographic attribution alongside objective skin-tone colorimetry using the Individual Typology Angle ($\text{ITA}$), measuring melanin and luminance in CIELAB space without racial proxy assumptions.  
Crucially, our interpretation is bounded by the Impossibility Theorems of Bilodeau et al. (2022): feature attribution provides exploratory proxy clues regarding feature sensitivity, never causal proof of algorithmic discrimination. BiasAperture clearly demarcates correlation from causation in all audit outputs."*

---

### Slide 12: Empirical Validation Benchmark: FairFace
**Speaker: Tisha**
> *"We ground our validation on the FairFace benchmark dataset created by Kärkkäinen and Joo (2021). Our local benchmark on disk contains 97,698 labeled images — 86,744 in training and 10,954 in validation — spanning a balanced 7-race, 9-age, and 2-gender taxonomy yielding 126 intersectional demographic cells.  
Our validation target is a ResNet-34 multi-task baseline classifier operating on $300 \times 300$ aligned facial chips.  
During preliminary data audits, we formally descoped UTKFace under Cut-List item #2 due to documented 3-of-7 racial taxonomy collapse and noisy model-estimated age labels, concentrating validation exclusively on FairFace’s curated ground truth."*

---

### Slide 13: Empirical Benchmark Findings on 10,954 Images
**Speaker: Aaradhya**
> *"We executed a full audit across all 10,954 FairFace validation images.  
As detailed in our empirical results, the baseline ResNet-34 model exhibits substantial demographic disparities on gender classification: Demographic Parity Difference reaches 0.923 with an extremely tight 95% BCa confidence interval of $[0.915, 0.930]$ and $p = 0.000$, confirming statistically significant selection disparity. The Disparate Impact Ratio drops to 0.070, severely breaching the EEOC 0.80 four-fifths rule.  
Furthermore, our Tier 1 Support Guards successfully flagged sparse conditioning cells as N/A rather than outputting volatile point estimates. Every reported row is fully crosswalked to EU AI Act Article 10 and NIST AI RMF Measure 2.11."*

---

### Slide 14: Standalone Offline Compliance Dossier
**Speaker: Tisha**
> *"The output of BiasAperture is a single-file, zero-network HTML compliance dossier synthesizing Model Cards and Datasheets for Datasets conventions.  
Because auditing biometric models often involves sensitive data and air-gapped security requirements, the dossier contains zero external CDN calls, web fonts, or tracker scripts. All interactive charts and visual distributions are rendered as self-contained inline SVG and base64 assets.  
Auditors and compliance officers can securely email, inspect, and archive the dossier offline while maintaining complete traceability to Article 10(2), 10(3), and 10(5) of the EU AI Act."*

---

### Slide 15: Single-Command CLI Orchestration
**Speaker: Aaradhya**
> *"BiasAperture packages this multi-stage workflow behind an ergonomic Command Line Interface.  
With a single invocation of `bias-aperture audit`, users supply predictions CSV files, specify protected demographic axes, activate dual-backend cross-checking, and generate the compliance dossier.  
The telemetry provides real-time logging of sample validation, backend parity checks, bootstrap resampling, and disparity flags. It is production-ready for automated CI/CD regression testing."*

---

### Slide 16: Verification, Contract Testing & Claim Ledger
**Speaker: Aaradhya**
> *"Our engineering is backed by a rigorous test suite of 55 passing pytest cases covering schema boundaries, metric harmonization parity, BCa bootstrap reproducibility, and report formatting. A deterministic 8-record ground-truth known-answer test validates exact scalar parity across backends.  
Furthermore, we maintain an auditable Claim Ledger tracking 20 active literature claims and 5 formally falsified hypotheses — such as proving early that normal approximation intervals fail on bounded ratio metrics, and falsifying UTKFace dataset viability before it could introduce downstream noise."*

---

### Slide 17: Execution Schedule & 5-Tier Descoping Strategy
**Speaker: Tisha**
> *"Our project roadmap progressed through five structured milestones from Milestone M1 schema locking through Milestone M5 benchmark audit execution.  
To guarantee delivery under strict deadlines, we established an explicit 5-tier descoping sequence in advance: dropping the Web UI in favor of the CLI, descoping UTKFace (which was formally executed), dropping PDF export in favor of offline HTML, and retaining precomputed file ingestion over in-process models.  
Our non-negotiable core — ingestion, fairness metrics, statistical testing, and compliance reporting — remained completely insulated from delivery risk."*

---

### Slide 18: Summary of Core Engineering Contributions
**Speaker: Joint (Aaradhya & Tisha)**
> **Aaradhya:** *"In summary, BiasAperture makes four core contributions: first, a vision-native auditing architecture tailored to computer vision pipelines; second, mathematical harmonization resolving vendor discrepancies between Fairlearn and AIF360."*  
> **Tisha:** *"Third, a three-tier inferential defense providing statistical credibility to fairness effect sizes; and fourth, a regulator-legible offline compliance dossier directly aligned with the EU AI Act and NIST AI RMF."*

---

### Slide 19: Conclusion & Q&A Transition
**Speaker: Joint (Aaradhya & Tisha)**
> **Aaradhya:** *"BiasAperture transforms theoretical fairness formulas into an automated, production-grade diagnostic pipeline. All code, empirical datasets, and verification suites are accessible in our repository."*  
> **Tisha:** *"Thank you for your time and attention. We now welcome questions and discussion from the evaluation committee."*

---

## Scripted Answers to Anticipated Panel Grilling

### Scrutiny Question 1: "Aren't you just writing a wrapper around Fairlearn and AIF360?"
**Answer (Aaradhya):**
> *"No. The relationship between BiasAperture and Fairlearn or AIF360 is analogous to Docker and Linux cgroups. Docker did not invent cgroups or kernel namespaces, but it eliminated workflow friction and standardized containerization.  
Existing fairness toolkits are tabular-first. Applying them to computer vision requires multi-class One-vs-Rest binarization, face alignment, intersectional slicing, and proxy feature attribution. More importantly, Fairlearn and AIF360 compute mathematically divergent definitions of Equalized Odds on identical data and use conflicting sign conventions. BiasAperture reconciles these mathematical divergences into an auditable contract, enforces $n \ge 30$ support guards that neither library provides, and outputs an offline compliance dossier crosswalked to the EU AI Act. That is an engineering contribution of systems integration and harmonization."*

---

### Scrutiny Question 2: "Why didn't you implement model retraining or debiasing algorithms?"
**Answer (Tisha):**
> *"Diagnostic integrity requires a strict separation of concerns from model remediation.  
First, an auditor must remain an objective, independent evaluator. If an auditing tool automatically perturbs weights or thresholds to pass its own tests, the audit loses independent credibility under Goodhart's Law.  
Second, in their 2024 survey, Dehdashtian, Wang, and Boddeti establish a formal division between diagnostic auditing and mitigation. BiasAperture is purposefully positioned on the diagnostic side: we produce the authoritative disparity dossier that downstream engineering teams use to inform their own domain-specific retraining and mitigation strategies."*

---

### Scrutiny Question 3: "Why use BCa bootstrap instead of standard normal approximation confidence intervals?"
**Answer (Aaradhya):**
> *"Standard normal approximation ($\hat{\theta} \pm 1.96 \cdot \text{SE}$) assumes asymptotic symmetry. In fairness auditing, this assumption routinely fails.  
First, ratio metrics like Disparate Impact Ratio ($\min/\max$) have highly skewed sampling distributions with heavy right tails.  
Second, difference metrics like DPD and EOD are theoretically bounded between 0 and 1. Near boundary values (such as an accurate model with DPD near 0), normal approximation intervals frequently produce negative lower bounds ($< 0$), which are mathematically impossible.  
Efron’s Bias-Corrected and Accelerated (BCa) bootstrap solves both issues: the bias correction parameter $z_0$ adjusts for median bias, the acceleration parameter $a$ corrects for variance skewness via jackknife residuals, and BCa intervals are transformation-invariant, respecting natural parameter boundaries."*

---

### Scrutiny Question 4: "Why is sample size $n=30$ chosen as the screening threshold?"
**Answer (Tisha):**
> *"Under standard statistical theory and the Central Limit Theorem, $n=30$ is the classical empirical rule-of-thumb below which sampling distributions cannot be assumed approximately normal. In intersectional demographic slices (such as 7 races $\times$ 9 ages $\times$ 2 genders = 126 cells), peripheral bins frequently contain very few samples.  
Computing point estimates on cells with $n < 30$ produces extreme variance and unstable ratios. Enforcing $n \ge 30$ ensures that published disparities reflect genuine algorithmic patterns rather than random sampling variance. As Watkins et al. demonstrated, unadjusted thresholds on small samples lead to rampant false alarms."*
