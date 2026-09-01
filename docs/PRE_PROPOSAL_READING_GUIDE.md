# BiasAperture — Pre-Proposal Defense Reading Guide

**Document Purpose:** Foundational study guide and conceptual roadmap distilled from all primary-source syntheses, mathematical harmonizations, and examiner defense strategies for **BiasAperture**.  
**Audience:** Aaradhya Dev Tamrakar & Tisha Manandhar (Fusemachines AI Fellowship Capstone Defense).  
**Status:** Synchronized with research specification freeze through `ba69af4`; guide created at `99bf3aa`.  

---

## 1. The Core Reasoning Chain

Carry this single mental chain into your defense. Every question the panel asks maps to one link in this sequence:

$$\boxed{\text{Problem} \longrightarrow \text{Data} \longrightarrow \text{Estimand} \longrightarrow \text{Metric} \longrightarrow \text{Uncertainty} \longrightarrow \text{Interpretation} \longrightarrow \text{Limits} \longrightarrow \text{Governance}}$$

| Link | Core Idea | Primary Source Grounding |
|---|---|---|
| **1. Problem** | Aggregate accuracy hides severe subgroup failure (*distributional masking*). | Buolamwini & Gebru (2018) *Gender Shades* |
| **2. Data** | 97,698 labeled images on disk across 7 races, 9 ages, 2 genders; 126 possible intersectional cells with highly unequal cell occupancy. | Kärkkäinen & Joo (2021) *FairFace* |
| **3. Estimand** | Conditional inference holding observed subgroup sample sizes $n_a$ invariant. | Fixed-strata within-subgroup resampling design |
| **4. Metric** | Selection disparity (DPD) vs. error-rate parities (EOP, harmonized max-gap EOD). | Hardt et al. (2016) *Equality of Opportunity* |
| **5. Uncertainty** | $n \ge 30$ screening invariant, support checks ($k=5$), valid-replicate threshold ($\tau=0.90$), BCa bootstrap ($B \ge 1000$). | Efron (1987) BCa theory + project stability fallback |
| **6. Interpretation** | Disparities & ratios are effect sizes, requiring statistical support context rather than bare threshold evaluation. | Watkins et al. (2022) *Four-Fifths Critique* |
| **7. Limits** | Feature attribution is not causal evidence of discrimination (*Proxy Evidence Analysis*). Passing $\neq$ global fairness. | Bilodeau et al. (2022) *Impossibility Theorems* |
| **8. Governance** | Metrics without provenance and limitations are incomplete; offline single-file report. | Mitchell et al. (2019) & Gebru et al. (2018) |
| **9. Scope** | Strictly diagnostic: ingest, measure, explain, report. No retraining or debiasing. | Dehdashtian et al. (2024) Survey |

---

## 2. The 4-Layer Conceptual Reading Matrix

You do not need to read dozens of papers. Deeply understand these **9 foundational sources across 4 conceptual layers**:

```
┌────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: PROBLEM & BENCHMARK DATA                                      │
│ • Buolamwini & Gebru (2018) — Gender Shades                            │
│ • Kärkkäinen & Joo (2021) — FairFace                                   │
├────────────────────────────────────────────────────────────────────────┤
│ LAYER 2: FAIRNESS MATHEMATICS & EFFECT-SIZE METRICS                    │
│ • Hardt, Price, & Srebro (2016) — Equality of Opportunity (EOD, EOP)   │
│ • Watkins, McKenna, & Chen (2022) — Four-Fifths Critique (DIR)         │
├────────────────────────────────────────────────────────────────────────┤
│ LAYER 3: STATISTICAL INFERENCE & EXPLAINABILITY BOUNDS                 │
│ • Efron (1987) — Better Bootstrap Confidence Intervals (BCa)           │
│ • Bilodeau et al. (2022) — Impossibility Theorems for Attribution      │
├────────────────────────────────────────────────────────────────────────┤
│ LAYER 4: ECOSYSTEM CONTEXT & REPORTING PHILOSOPHY                      │
│ • Dehdashtian, Wang, & Boddeti (2024) — CV Fairness Survey             │
│ • Mitchell et al. (2019) — Model Cards for Model Reporting             │
│ • Gebru et al. (2018) — Datasheets for Datasets                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

### Layer 1: Problem & Benchmark Data

#### 1. Buolamwini & Gebru (2018) — *Gender Shades: Intersectional Accuracy Disparities in Commercial Gender Classification*

* **What to Read:** Section 3 (PPB dataset & Fitzpatrick skin types) and Section 5 (Empirical results).
* **The Insight:** Commercial classifiers achieved overall error rates under 12%, but intersectional error rates reached **34.7% for darker females vs. 0.8% for lighter males** (a 43:1 error gap).
* **Takeaway:** Overall accuracy creates *distributional masking*. Aggregate metrics should be complemented by subgroup and intersectional analysis where the data support it (with low-support cells explicitly flagged rather than estimated unstably).

#### 2. Kärkkäinen & Joo (2021) — *FairFace: Face Attribute Dataset for Balanced Race, Gender, and Age*

* **What to Read:** Section 3 (Balanced dataset construction, 7-race taxonomy) and Section 4 (ResNet-34 multi-task baseline).
* **The Insight:** Prior face datasets (LFW, CelebA) were heavily skewed (70–80% White). FairFace was intentionally sampled with demographic balancing goals across 7 races, 9 age groups, and 2 genders.
* **Takeaway:**
  * Distinguish the paper from your local artifact: **97,698 labeled images in the released artifact on disk: 86,744 train and 10,954 validation** after post-annotation quality filtering.
  * The Cartesian taxonomy yields $7 \times 2 \times 9 = 126$ possible intersectional cells with **highly unequal cell occupancy**.
  * Baseline classifier uses `dlib` 5-point alignment chips ($300 \times 300$, $0.25$ padding) and an 18-unit linear layer (`torch.Size([18, 512])` sliced `[0:7]`, `[7:9]`, `[9:18]`).

---

### Layer 2: Fairness Mathematics & Effect-Size Metrics

#### 3. Hardt, Price, & Srebro (2016) — *Equality of Opportunity in Supervised Learning*

* **What to Read:** Section 2 (Definitions of Equalized Odds and Equal Opportunity).
* **The Insight:** Demographic Parity forces equal positive prediction rates regardless of base rates, which can incentivize harmful, arbitrary predictions. Error-rate parity criteria condition on true outcome $Y$:
  * **Equal Opportunity (EOP):** Equal True Positive Rates across groups on $Y=1$:
    $$P(\hat{Y}=1 \mid A=a, Y=1) = P(\hat{Y}=1 \mid A=b, Y=1)$$
  * **Equalized Odds (EOD):** Equal True Positive Rates **and** False Positive Rates across groups:
    $$P(\hat{Y}=1 \mid A=a, Y=y) = P(\hat{Y}=1 \mid A=b, Y=y) \quad \forall y \in \{0, 1\}$$
* **Takeaway for BiasAperture:**
  * Hardt et al. provide the error-rate criteria, not Demographic Parity (which stems from broader statistical parity literature).
  * Hardt et al. define the condition across groups; BiasAperture's headline scalar is our **harmonized max-gap operationalization**:
    $$\text{EOD} = \max\left( \max_a \text{TPR}_a - \min_a \text{TPR}_a, \; \max_a \text{FPR}_a - \min_a \text{FPR}_a \right)$$
  * This harmonizes Fairlearn's worst-case gap with native AIF360's mean gap $\frac{1}{2}(\Delta\text{TPR} + \Delta\text{FPR})$.

#### 4. Watkins, McKenna, & Chen (2022) — *The Four-Fifths Rule is Not Disparate Impact*

* **What to Read:** Section 2 & 3 (Doctrinal origins in US EEOC employment law vs. algorithmic application).
* **The Insight:** Treating the 80% (4/5ths) selection ratio as an unadjusted pass/fail metric in ML is "epistemic trespassing." On small sample sizes or rare positive classes, random sampling variance routinely triggers **unstable or statistically unsupported apparent violations**.
* **Takeaway for BiasAperture:**
  * Disparate Impact Ratio ($\text{DIR}$) is an **effect-size description**, not standalone proof of unfairness.
  * BiasAperture computes DIR as a **symmetric bounded ratio** ($\min_a \text{rate}_a / \max_a \text{rate}_a \in [0, 1]$) to avoid arbitrarily picking a "privileged" group among 7 non-ordinal races.
  * DIR is always paired with cell-support checks and appropriate inferential procedures, including contingency-table tests where their assumptions are satisfied, plus bootstrap confidence intervals.

---

### Layer 3: Statistical Inference & Explainability Bounds

#### 5. Efron (1987) — *Better Bootstrap Confidence Intervals (BCa)*

* **What to Read:** Conceptual mechanics of Bias-Correction ($z_0$) and Acceleration ($a$).
* **The Insight:** Simple percentile bootstrap intervals assume the bootstrap distribution is symmetric and unbiased. Ratio-based metrics (DIR) and multi-group extreme differences (max-min gaps) exhibit heavy skewness and boundary constraints where percentile CIs under-cover.
* **Takeaway for BiasAperture:**
  * **Median Bias Correction ($z_0$):** Adjusts for discrepancy between bootstrap median and point estimate.
  * **Acceleration ($a$):** Jackknife-based adjustment for skewness / variance dependency on the parameter.
  * **Estimand Contract:** BiasAperture resamples *within* demographic strata (fixed $n_a$) to estimate uncertainty conditional on observed subgroup composition.
  * **Explicit Fallback Policy:** BiasAperture falls back to the empirical percentile interval when its explicit numerical stability and degeneracy checks fail, including the project-defined $|a| > 0.5$ criterion or invalid interval bounds.

#### 6. Bilodeau et al. (2022) — *Impossibility Theorems for Feature Attribution*

* **What to Read:** Introduction and the Core Impossibility Theorem.
* **The Insight:** Additive linear feature attribution methods (SHAP, Integrated Gradients) cannot mathematically guarantee distinguishing whether a deep neural network is utilizing a true causal feature versus a correlated spurious proxy in general data distributions.
* **Takeaway for BiasAperture:**
  * **Attribution Evidence is not, by itself, causal evidence of discrimination.**
  * SHAP highlighting a facial region does not prove the model is discriminatory because of that demographic trait.
  * This justifies our strict naming convention: **Proxy Evidence Analysis**, providing exploratory visual diagnostic evidence, not causal proof.

---

### Layer 4: Ecosystem Context & Reporting Philosophy

#### 7. Dehdashtian, Wang, & Boddeti (2024) — *Fairness and Bias Mitigation in Computer Vision: A Survey*

* **What to Read:** Section 2 (Taxonomy of Bias across Pipeline) and Section 6 (Diagnostic vs. Mitigation techniques).
* **The Insight:** A rich literature exists for training-time loss debiasing, adversarial reweighting, and post-processing, but standardized, reusable audit pipelines for computer vision workflows are lacking.
* **Takeaway for BiasAperture:**
  * Validates our **strictly diagnostic boundary**.
  * Combining measurement and mitigation into a single tool compromises audit objectivity. BiasAperture produces an independent diagnostic baseline.

#### 8 & 9. Mitchell et al. (2019) (*Model Cards*) & Gebru et al. (2018) (*Datasheets*)

* **What to Read:** The philosophy of structured machine learning documentation.
* **The Insight:** Quantitative evaluation numbers without context (intended use, limitations, evaluation population, data provenance, caveats) are actively misleading.
* **Takeaway for BiasAperture:**
  * Why the output is a **self-contained offline HTML report**, not a raw JSON dictionary.
  * Implements the 9 Model Card sections using lightweight Jinja2 templates (avoiding heavy Apache TFX/MLMD dependencies from Google's `model-card-toolkit`).

---

## 3. The 12 Master First-Principles Questions

Master these 12 questions to defend the proposal from first principles:

### 1. Problem & Intersectional Masking

* **Q:** *Why can high overall model accuracy conceal severe demographic disparities?*
* **A:** Aggregate accuracy averages across the entire population. When a dataset is demographically imbalanced, high accuracy on dominant groups (e.g., lighter males) masks severe error rates on underrepresented intersectional subgroups (e.g., darker females, older cohorts), as established by Buolamwini & Gebru.

### 2. Fairness Metrics Hierarchy

* **Q:** *What are the precise mathematical definitions of DPD, EOP, and EOD?*
* **A:**
  * **Demographic Parity Difference (DPD):** Evaluates unconditional selection parity:
    $$\text{DPD} = \max_a P(\hat{Y}=1 \mid A=a) - \min_a P(\hat{Y}=1 \mid A=a)$$
  * **Equal Opportunity Difference (EOP):** Evaluates conditional positive-class error parity ($Y=1$):
    $$\text{EOP} = \max_a \text{TPR}_a - \min_a \text{TPR}_a$$
  * **Equalized Odds Difference (EOD):** Evaluates conditional error parity across both outcomes ($Y=1$ and $Y=0$):
    $$\text{EOD} = \max\left( \max_a \text{TPR}_a - \min_a \text{TPR}_a, \; \max_a \text{FPR}_a - \min_a \text{FPR}_a \right)$$

### 3. Multi-Class One-vs-Rest (OvR) Policy

* **Q:** *How does BiasAperture handle multi-class targets (e.g., 7 races, 9 age groups)?*
* **A:** Multi-class targets ($M > 2$) are binarized into $M$ One-vs-Rest (OvR) tasks. DPD, EOD, and EOP are evaluated per binary task and macro-averaged across classes. In contrast, Disparate Impact Ratio is reported per class and is **never macro-averaged**, as averaging non-linear ratios introduces severe mathematical distortion.

### 4. Effect-Size Interpretation

* **Q:** *Why is a metric like $\text{DIR} = 0.72$ by itself insufficient to claim model bias?*
* **A:** As Watkins et al. demonstrated, a ratio is an effect size, not a statistical test. It does not communicate sample size, variance, or stability. A small subgroup with few observations can produce an extreme ratio purely by chance. DIR must be paired with cell-support checks and appropriate inferential procedures, including contingency-table tests where their assumptions are satisfied, plus bootstrap confidence intervals.

### 5. Sample-Size Screening Invariant

* **Q:** *What does the $n \ge 30$ threshold represent, and what does it NOT mean?*
* **A:** $n \ge 30$ is a **project-defined engineering screening invariant** to filter out unstable, undersized subgroups before primary disparity estimation. It is **not** a universal statistical law or proof of normality under the Central Limit Theorem. Filtered subgroups are flagged as `insufficient_sample=True, metric_value=None`.

### 6. Bootstrap Estimand & Mechanics

* **Q:** *What are $z_0$ and $a$, and what is your bootstrap estimand?*
* **A:** Our estimand is uncertainty conditional on observed demographic composition, achieved via **fixed-strata within-subgroup resampling** ($B \ge 1000$). $z_0$ corrects for median bias, and $a$ adjusts for distribution skewness via jackknife acceleration. BiasAperture falls back to empirical percentile intervals when its explicit numerical stability and degeneracy checks fail, including the project-defined $|a| > 0.5$ criterion or invalid interval bounds.

### 7. Explainability Limits

* **Q:** *Can SHAP feature attribution prove that a model is racially biased?*
* **A:** No. Per Bilodeau et al. (2022) impossibility theorems, SHAP attribution is not, by itself, causal evidence of discrimination. Deep networks may utilize features that correlate with demographic traits without establishing causal mechanisms. SHAP provides **Proxy Evidence Analysis** (exploratory visual association), not causal proof.

### 8. Backend Harmonization

* **Q:** *Why not just use Fairlearn or AIF360 directly?*
* **A:** Fairlearn and AIF360 disagree on native definitions. Fairlearn calculates EOD as the worst-case max gap ($\max(\Delta\text{TPR}, \Delta\text{FPR})$), while native AIF360 calculates the average gap ($\frac{1}{2}(\Delta\text{TPR} + \Delta\text{FPR})$). AIF360 also returns a signed difference for EOP. BiasAperture harmonizes both libraries to a unified contract, using them for **heterogeneous software implementation cross-checking**.

### 9. Defensible Novelty

* **Q:** *What is novel about BiasAperture if you are integrating existing tools?*
* **A:** Engineering and integration novelty. Among the seven tools evaluated in our comparative review, we did not identify a system that integrates computer-vision demographic taxonomies, multi-backend mathematical harmonization, statistical screening guards, stratified BCa bootstrap uncertainty, targeted explainability, and regulatory reporting into one reusable workflow.

### 10. Passing Audit Semantics

* **Q:** *What does a passing audit result actually establish?*
* **A:** A passing result establishes that under the audited benchmark, specified metrics, sample support conditions, and inference framework, measured disparities did not exceed predefined diagnostic thresholds. It does **not** prove absence of discrimination, causal fairness, generalizability beyond the test set, or legal compliance.

### 11. Regulatory Alignment

* **Q:** *How does BiasAperture align with the EU AI Act?*
* **A:** BiasAperture provides **technical audit infrastructure** aligned with Article 10 data governance requirements: Article 10(2) provenance logs, Article 10(3) statistical adequacy and representation guards, and Article 10(5) bias examination over demographic categories. It does not provide legal certification.

### 12. Scope Boundary

* **Q:** *Why is BiasAperture strictly diagnostic, and what is out of scope?*
* **A:** Retraining, fine-tuning, loss debiasing, and synthetic generation are strictly out of scope. Diagnostic auditing must remain independent from model mitigation to maintain objectivity and prevent conflicting optimization objectives.

---

## 4. Mental Hierarchy: Meaning $\to$ Justification $\to$ Limitation $\to$ Number

Prioritize understanding why each parameter exists before reciting the numeric constant:

| Concept / Invariant | Exact Specification | Meaning & Justification | Known Boundary / Limitation |
|---|---|---|---|
| **Primary Benchmark** | 97,698 labeled images ($86,744 \text{ train} + 10,954 \text{ val}$) | Released artifact count on disk with human labels | Does not equal uncurated 108.5k pre-discard count |
| **Intersectional Grid** | 126 cells ($7 \text{ races} \times 2 \text{ genders} \times 9 \text{ ages}$) | Cartesian demographic combinations | Cell occupancy is highly non-uniform; many sparse cells |
| **Screening Invariant** | $n \ge 30$ per subgroup | Prevents unstable small samples from entering analysis | Engineering threshold; not a universal statistical law |
| **Cell Support Guard** | $k \ge 5$ observations | Requires $n_{Y=1, a} \ge 5$ (EOP) and $n_{Y=0, a} \ge 5$ (EOD) | Unmet support forces `insufficient_sample=True` |
| **Bootstrap Iterations** | $B \ge 1,000$ resamples | Monte Carlo precision for tail quantiles | Stratified within observed strata (fixed $n_a$) |
| **Replicate Validity** | $\tau = 0.90$ (90% valid) | Minimum valid bootstrap replicates required | Prevents estimation on near-empty demographic slices |
| **Significance Level** | $\alpha = 0.05$ | Baseline error threshold with Holm FWER adjustment | Controls family-wise false discoveries across 126 cells |
| **Harmonized Fair Values** | $\text{DPD}=0.0, \text{EOD}=0.0, \text{EOP}=0.0, \text{DIR}=1.0$ | Ideal parity values across harmonized metrics | Symmetric $\min/\max$ DIR avoids arbitrary privileged group |
| **ResNet-34 Architecture** | 18 units (`torch.Size([18, 512])`) | Multi-task slices: race [0:7], gender [7:9], age [9:18] | Evaluated via `dlib` 5-point alignment ($300\times300$ chips) |
| **Descoping Cut-List** | 1. UI $\to$ 2. UTKFace $\to$ 3. PDF $\to$ 4. In-Process $\to$ 5. AIF360 | Pre-planned graceful degradation under time pressure | Diagnostic core (ingestion, engine, report) is never cut |
