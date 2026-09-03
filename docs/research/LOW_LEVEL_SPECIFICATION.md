# BiasAperture — Research Sprint: Low-Level Technical Specification

**Target Audience:** Core Developers, Mathematical Implementers, Statistical Auditors  
**Document Level:** Low-Level (Mathematical Formulations, Exact Algorithms, Tensor Slicing & Code Specs)  
**Date:** August 2026  
**Context:** Phase 1 capstone specification; Phase 2 product-upgrade research is tracked separately

---

## 1. Formal Semantics of Audited Targets & Demographic Attributes

To prevent category confusion during auditing and evaluation, BiasAperture establishes formal definitions for the prediction target, model prediction, and sensitive demographic axes:

```
                  ┌─────────────────────────────────────────────────────────────┐
                  │                 FORMAL AUDIT TAXONOMY                       │
                  ├───────────────────┬─────────────────────────────────────────┤
                  │ Variable Symbol   │ Operational Definition                  │
                  ├───────────────────┼─────────────────────────────────────────┤
                  │ Y                 │ Ground-truth task label                 │
                  │ Ŷ                 │ Audited model prediction                │
                  │ A                 │ Sensitive / protected demographic axis  │
                  └───────────────────┴─────────────────────────────────────────┘
```

### 1.0. Audited Target Configurations

1. **Downstream Task Audit ($A \neq Y$)**:
   - Auditing a model's prediction on a non-demographic task (or a distinct demographic attribute) across protected groups.
   - *Example*: Auditing binary gender classification ($Y \in \{\text{Male}, \text{Female}\}$) stratified across 7 race groups ($A = \text{Race}$).
   - *Interpretation*: Traditional fairness evaluation testing whether performance parity holds across sensitive groups.
2. **Demographic-Class Performance Audit ($A = Y$)**:
   - Auditing the demographic classifier itself across its own classes.
   - *Example*: Auditing FairFace's 7-race prediction ($Y = \text{Race}, \hat{Y} = \text{Pred\_Race}, A = \text{Race}$).
   - *Interpretation*: Class-conditional per-group performance analysis evaluating whether true positive rates (recall) and false positive rates diverge across the ground-truth classes themselves (rather than conventional group fairness on an external task).

### 1.0.1. Multi-Class One-vs-Rest (OvR) Evaluation Policy

For any multi-class prediction target $Y \in \mathcal{C} = \{c_1, c_2, \dots, c_M\}$ with $M > 2$ classes (e.g. 7 races, 9 age groups):

1. **Binarization**: Decompose the $M$-class problem into $M$ independent One-vs-Rest binary tasks:
   $$Y^{(m)} = \mathbb{I}(Y = c_m), \quad \hat{Y}^{(m)} = \mathbb{I}(\hat{Y} = c_m) \quad \text{for } m \in \{1, \dots, M\}$$
2. **Metric Computation**: Compute the Core Four metrics ($\text{DPD}^{(m)}, \text{EOD}^{(m)}, \text{EOP}^{(m)}, \text{DIR}^{(m)}$) for each binary class task $m$ across the protected attribute subgroups $a \in A$.
3. **Macro-Aggregation Policy**:
   - **Macro-DPD, Macro-EOD, Macro-EOP**: Arithmetic unweighted mean across all $M$ classes:
     $$\text{Macro-DPD} = \frac{1}{M} \sum_{m=1}^M \text{DPD}^{(m)}, \quad \text{Macro-EOD} = \frac{1}{M} \sum_{m=1}^M \text{EOD}^{(m)}, \quad \text{Macro-EOP} = \frac{1}{M} \sum_{m=1}^M \text{EOP}^{(m)}$$
     *Methodological Note: Macro aggregation assigns equal evaluative weight to each One-vs-Rest class irrespective of sample prevalence.*
   - **Macro-DIR Policy**: **DIR is reported per class but is NOT macro-averaged**, because arithmetic averaging of non-linear ratios produces mathematically distorted and uninterpretable aggregate statistics.
4. **Per-Class Support Reporting Invariant**:
   - Macro summary metrics must always be accompanied by per-class metric values and class-wise support counts ($n_{Y=c_m, a}$) to prevent masking weak-support sub-cohorts.

---

## 2. Mathematical Fairness Formulations & Backend Harmonization

Let $Y \in \{0, 1\}$ denote the binary (or OvR-binarized) ground-truth label, $\hat{Y} \in \{0, 1\}$ denote the model prediction, and $A \in \{a_1, a_2, \dots, a_K\}$ denote the protected demographic attribute across $K$ mutually exclusive subgroups.

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       CORE FOUR METRICS TAXONOMY                                        │
├───────────────────────────────┬─────────────────────────────────────────────────┬───────────────────────┤
│ Metric Name                   │ Mathematical Definition                         │ Fair Value / Range    │
├───────────────────────────────┼─────────────────────────────────────────────────┼───────────────────────┤
│ Demographic Parity Difference │ max_a P(Y_hat=1|A=a) - min_a P(Y_hat=1|A=a)     │ 0.0  [0.0, 1.0]       │
│ Equalized Odds Difference     │ max( max_a TPR_a - min_a TPR_a,                 │ 0.0  [0.0, 1.0]       │
│                               │      max_a FPR_a - min_a FPR_a )                │                       │
│ Equal Opportunity Difference  │ max_a TPR_a - min_a TPR_a                       │ 0.0  [0.0, 1.0]       │
│ Disparate Impact Ratio        │ min_a P(Y_hat=1|A=a) / max_a P(Y_hat=1|A=a)     │ 1.0  [0.0, 1.0]       │
└───────────────────────────────┴─────────────────────────────────────────────────┴───────────────────────┘
```

---

### 1.1. Demographic Parity Difference (DPD)

Measures the spread in selection rates across demographic groups unconditional on ground truth:

$$\text{DPD} = \max_{a \in A} P(\hat{Y}=1 \mid A=a) - \min_{a \in A} P(\hat{Y}=1 \mid A=a)$$

- **Fairlearn API**: `fairlearn.metrics.demographic_parity_difference(y_true, y_pred, sensitive_features=A)`
- **AIF360 API**: Evaluated via `BinaryLabelDatasetMetric.statistical_parity_difference()`.

---

### 1.2. Equalized Odds Difference (EOD) — Resolving Definitional Divergence

Let $\text{TPR}_a = P(\hat{Y}=1 \mid Y=1, A=a)$ and $\text{FPR}_a = P(\hat{Y}=1 \mid Y=0, A=a)$.

#### The Divergence Found in Research (Tracks 09, 10, 14)

- **Fairlearn / Hardt et al. (2016)**: Computes the worst-case disparity: $\max(|\Delta\text{TPR}|, |\Delta\text{FPR}|)$.
- **AIF360 Native (`average_odds_difference`)**: Computes the average gap: $\frac{1}{2}(|\Delta\text{TPR}| + |\Delta\text{FPR}|)$.

#### The Locked Resolution

`AIF360Backend` is explicitly adapted to calculate the worst-case disparity from raw confusion-matrix counts to maintain parity with Fairlearn:

```python
eod_value = max(abs(tpr_gap), abs(fpr_gap))
```

---

### 1.3. Equal Opportunity Difference (EOP) — Resolving Sign Mismatch

$$\text{EOP} = \max_{a \in A} \text{TPR}_a - \min_{a \in A} \text{TPR}_a$$

#### The Divergence Found in Research (Track 14)

- **Fairlearn**: Returns unsigned difference $\ge 0$.
- **AIF360 Native**: Returns signed difference $\text{TPR}_u - \text{TPR}_p \in [-1, 1]$.

#### The Locked Resolution

`AIF360Backend` applies `abs()` before storing to `MetricResult.metric_value` to prevent signed outputs (e.g. $-0.293$ vs $+0.293$) from tripping divergence alerts:

```python
eop_value = abs(float(metric.equal_opportunity_difference()))
```

---

### 1.4. Disparate Impact Ratio (DIR) & Edge Cases

$$\text{DIR} = \frac{\min_{a \in A} P(\hat{Y}=1 \mid A=a)}{\max_{a \in A} P(\hat{Y}=1 \mid A=a)}$$

- **Symmetric Bounded Form (`symmetric_disparate_impact_ratio`)**: Scaled to $[0, 1]$, where $1.0$ represents demographic parity across multi-group sets without reference-group bias.
- **Zero-Denominator Edge Handling**:
  - If $\max_a P(\hat{Y}=1 \mid A=a) = 0.0$ (no positive predictions in any group), $\text{DIR} = 1.0$ (no relative disparity), and `absolute_selection_warning = True` is raised.
  - If $\min_a P(\hat{Y}=1 \mid A=a) = 0.0$ and $\max > 0$, $\text{DIR} = 0.0$ (complete disparate exclusion).
- **Four-Fifths Adverse-Impact Screening Heuristic**: Evaluated relative to the $0.80$ screening heuristic (EEOC guidance) via bootstrap confidence intervals.

---

## 3. Statistical Engine Implementation Details

### 3.1. Vectorized Stratified BCa Bootstrap Confidence Intervals

BiasAperture implements a dedicated vectorized BCa bootstrap engine on `numpy.random.Generator`.

#### Bootstrap Population Model & Stratified Resampling Rationale

$$\text{Bootstrap Population Model} = \text{Fixed Observed Subgroup Strata}$$
Resampling is performed strictly *within* observed demographic strata ($A=a$) rather than unconditional i.i.d. sampling across the mixed dataset.

- **Estimand Meaning**: The bootstrap CI estimates uncertainty conditional on the observed subgroup composition ($n_a$), rather than uncertainty arising from random variation in subgroup proportions.
- **Allocation Invariance**: Preserves the observed sample size within each eligible subgroup/cell ($n_a$), preventing random demographic fluctuations from confounding disparity estimation.

#### Why a Custom Engine is Employed

1. **Fixed-Strata Index Drawing**: Preserves the observed sample size within each eligible subgroup/cell across all intersectional slices.
2. **Simultaneous Multi-Group Evaluation**: Computes the full $K$-group metric vector in a single vectorized pass.
3. **Deterministic Seeded PRNG**: Uses `numpy.random.Generator(PCG64)` for deterministic seeded random-stream reproducibility under a fixed NumPy implementation and identical call sequence.
4. **Explicit Stability Bounds & Metric-Specific Replicate Validity**:
   - Implements the BiasAperture stability threshold ($|a| \le 0.5$) with empirical percentile fallback.
   - **Replicate Validity Contract**: Every bootstrap replicate is checked for metric-specific support (DPD/DIR: valid non-empty denominator; EOP: positive support $n_{Y=1, a} > 0$; EOD: positive and negative support $n_{Y=1, a} > 0 \land n_{Y=0, a} > 0$).
   - Invalid replicates are excluded; if the valid replicate fraction falls below $\tau = 0.90$ (*a project-defined conservative engineering acceptance criterion*), the engine reports `insufficient_sample=True` rather than silently converting undefined rates to zero.

```
                    ┌──────────────────────────────────────────┐
                    │      Original Data (N subjects)          │
                    └────────────────────┬─────────────────────┘
                                         │
                                         ▼
                    ┌──────────────────────────────────────────┐
                    │   Stratified Index Resampling (B=1000)   │
                    │   rng.choice(idx_g, size=len(idx_g))     │
                    └────────────────────┬─────────────────────┘
                                         │
                                         ▼
                    ┌──────────────────────────────────────────┐
                    │    Metric Evaluation Loop (B replicates) │
                    │    theta_hat_b = [f(boot_b) for b in B]  │
                    └────────────────────┬─────────────────────┘
                                         │
                                         ▼
                    ┌──────────────────────────────────────────┐
                    │       Jackknife Acceleration (a) &       │
                    │         Bias Correction (z0)             │
                    └────────────────────┬─────────────────────┘
                                         │
                        ┌────────────────┴────────────────┐
                        ▼                                 ▼
              [ Is BCa Valid? ]                  [ Acceleration / ]
              ├── YES ──► Compute BCa Limits     [ Bias Degenerate?]
              └── NO  ──► Percentile Fallback    └──► Percentile Fallback
```

#### Mathematical Steps for BCa

1. **Bootstrap Replication**: Compute $\hat{\theta}^*_1, \dots, \hat{\theta}^*_B$ over stratified resamples.
2. **Bias-Correction Parameter ($z_0$)**:
   $$z_0 = \Phi^{-1} \left( \frac{1}{B} \sum_{b=1}^B \mathbb{I}(\hat{\theta}^*_b < \hat{\theta}) \right)$$
3. **Jackknife Acceleration ($a$)**:
   Using leave-one-out jackknife estimates $\hat{\theta}_{(i)}$ for $i=1, \dots, n$:
   $$\bar{\theta}_{(\cdot)} = \frac{1}{n} \sum_{i=1}^n \hat{\theta}_{(i)}, \quad a = \frac{\sum_{i=1}^n (\bar{\theta}_{(\cdot)} - \hat{\theta}_{(i)})^3}{6 \left[ \sum_{i=1}^n (\bar{\theta}_{(\cdot)} - \hat{\theta}_{(i)})^2 \right]^{3/2}}$$
4. **BCa Adjusted Percentiles ($\alpha_1, \alpha_2$)**:
   $$\alpha_1 = \Phi \left( z_0 + \frac{z_0 + z_{\alpha/2}}{1 - a(z_0 + z_{\alpha/2})} \right), \quad \alpha_2 = \Phi \left( z_0 + \frac{z_0 + z_{1-\alpha/2}}{1 - a(z_0 + z_{1-\alpha/2})} \right)$$
5. **Fallback Condition**: If $|a| > 0.5$ (stability threshold), $z_0$ is undefined, or the adjusted quantiles fall outside $[0, 1]$, fall back immediately to standard empirical percentiles:
   $$\text{CI}_{\text{fallback}} = \left[ \text{Percentile}\left(\hat{\theta}^*, 2.5\right), \; \text{Percentile}\left(\hat{\theta}^*, 97.5\right) \right]$$

---

### 3.2. Chi-Squared Contingency & Holm-Bonferroni Adjustment

1. **Table Layout**: For attribute $A$ with $K$ subgroups, construct $2 \times K$ matrix:
   $$O = \begin{bmatrix}
   n_{1, \text{pos}} & n_{2, \text{pos}} & \dots & n_{K, \text{pos}} \\
   n_{1, \text{neg}} & n_{2, \text{neg}} & \dots & n_{K, \text{neg}}
   \end{bmatrix}$$
2. **Independence Test**: Compute $\chi^2 = \sum \frac{(O_{ij} - E_{ij})^2}{E_{ij}}$ with degrees of freedom $\text{dof} = K - 1$.
3. **Holm-Bonferroni Step-Down FWER Adjustment**:
   Given $M$ sorted $p$-values $p_{(1)} \le p_{(2)} \le \dots \le p_{(M)}$:
   $$p_{(k)}^{\text{adj}} = \min \left( 1, \; \max_{j \le k} \left[ (M - j + 1) \cdot p_{(j)} \right] \right)$$
   Reject the null hypothesis if $p_{(k)}^{\text{adj}} < \alpha = 0.05$.

---

### 3.3. Statistical Adequacy & Estimand Mapping

#### 3.3.1. Screening Invariant ($n \ge 30$) vs. Conservative Support Rules

The $n \ge 30$ threshold is an **engineering minimum screening invariant (NFR-003)** to reject severely undersampled cells; it is not a claim of universal statistical sufficiency. Full inferential validity requires metric-specific conservative screening conditions:

```
┌─────────────────┬─────────────────────────────────────────────────┬───────────────────────────────────────────────────────┐
│ Metric / Test   │ Target Estimand Structure                       │ Conservative Engineering Screening Conditions        │
├─────────────────┼─────────────────────────────────────────────────┼───────────────────────────────────────────────────────┤
│ DPD             │ Selection rates across sensitive groups         │ Total n_a >= 30 for all groups                        │
│ EOP             │ True positive rates (Recall) across groups      │ n_a >= 30 AND positive support n_{Y=1, a} >= 5        │
│ EOD             │ Joint True Positive & False Positive parity     │ n_a >= 30 AND n_{Y=1, a} >= 5 AND n_{Y=0, a} >= 5     │
│ DIR             │ Bounded selection ratio min(rate)/max(rate)     │ Total n_a >= 30; if max=0, flag zero-selection        │
│ Chi-Squared     │ Homogeneity of demographic contingency table    │ Expected cell counts E_ij >= 5 (Cochran heuristic)    │
└─────────────────┴─────────────────────────────────────────────────┴───────────────────────────────────────────────────────┘
```

*Note: The minimum support threshold of 5 observations is applied as a conservative engineering rule to prevent extreme rate volatility; it is not claimed as an asymptotic sufficiency criterion.*

#### 3.3.2. DIR Zero-Denominator Reporting Invariant

When $\max_a P(\hat{Y}=1 \mid A=a) = 0.0$, BiasAperture records:

- `relative_disparity = 0.0` ($\text{DIR} = 1.0$)
- `absolute_selection_rate_max = 0.0`
- `absolute_selection_warning = True` (model produced zero positive selections across all audited cohorts).

---

## 3. FairFace Architecture & Preprocessing Deep Dive

### 3.1. ResNet-34 Multi-Task Head & Tensor Slicing

The baseline model is an ImageNet-pretrained ResNet-34 backbone terminating in a single fully connected layer of 18 output units:

```
[ Input Image 3x224x224 ]
          │
          ▼
[ ResNet-34 Backbone (Layers 1-4) ]
          │
          ▼
[ AdaptiveAvgPool2d -> 512-d ]
          │
          ▼
[ Linear(in_features=512, out_features=18) ]
          │
          ├── Slice [0:7]   ──► Softmax ──► Race Probabilities (7 Classes)
          ├── Slice [7:9]   ──► Softmax ──► Gender Probabilities (2 Classes)
          └── Slice [9:18]  ──► Softmax ──► Age Probabilities (9 Classes)
```

```python
# Exact PyTorch slicing from predict.py
outputs = model(images)  # Shape: (batch_size, 18)

race_logits   = outputs[:, 0:7]    # 7 race classes
gender_logits = outputs[:, 7:9]    # 2 gender classes
age_logits    = outputs[:, 9:18]   # 9 age bins

race_preds   = torch.argmax(race_logits, dim=1)
gender_preds = torch.argmax(gender_logits, dim=1)
age_preds    = torch.argmax(age_logits, dim=1)
```

---

### 3.2. Preprocessing & Alignment Pipeline

1. **Face Detection & Alignment**:
   - `dlib.cnn_face_detection_model_v1` detects bounding box.
   - `dlib.shape_predictor_5_face_landmarks` identifies 5 facial landmarks (two eye corners, nose base).
   - `dlib.get_face_chips(img, shapes, size=300, padding=0.25)` extracts aligned $300 \times 300$ square crop.
2. **Torchvision Tensor Normalization**:
   - Resize to $224 \times 224$.
   - Scale pixel values to $[0.0, 1.0]$.
   - Normalize with ImageNet constants:
     $$\mu = [0.485, 0.456, 0.406], \quad \sigma = [0.229, 0.224, 0.225]$$

---

## 4. Resolution Guide for the 21 Cross-Track Conflicts

| # | Discrepancy / Conflict | Tracks | Technical Resolution Applied in Code |
|---|---|:---:|---|
| **1** | Equalized Odds: max-gap vs mean-gap | 09, 10, 17 | `AIF360Backend` manually computes $\max(\Delta\text{TPR}, \Delta\text{FPR})$ using raw TPR/FPR primitives. |
| **2** | Disparate Impact Ratio formulation | 09, 10, 13 | Symmetric bounded ratio $\min/\max \in [0, 1]$ adopted as headline metric; pairwise matrix retained for diagnosis. |
| **3** | Signed vs Unsigned EOP | 14 | `AIF360Backend` calls `abs()` on native output before populating `MetricResult`. |
| **4** | Cross-group metric row shape | 11, 13, 14 | Cross-group metrics output summary rows with explicit `subgroup="ALL"` and per-group deviation tables. |
| **5** | Timing of $n \ge 30$ sample size guard | 09, 14 | Input arrays are pre-filtered in `fairness/base.py` *before* invoking backend libraries. |
| **6** | Zero-denominator DIR handling | 13 | Evaluated conditionally: $0/0 \to 1.0$, $x/0 \to 0.0$ (no new schema field needed). |
| **7** | EOD two-stratum $p$-value combination | 12, 14 | Report the conservative (higher) $p$-value: $p = \max(p_{\text{TPR}}, p_{\text{FPR}})$. |
| **8** | Multiple-testing correction family | 12 | Holm-Bonferroni correction applied per protected demographic attribute family. |
| **9** | AIF360 privileged/unprivileged leakage | 10 | Report layer maps all labels to objective strings: `subgroup` and `reference_group`. |
| **10** | Regulatory-tag storage mechanism | 08, 19 | Static lookup dictionary in `bias_aperture.report` mapping metric names to Article 10 / NIST clauses (leaves `schema.py` unmodified). |
| **11** | EU AI Act Art. 10(5) ownership | 08 | Embedded directly in the Model Card / Datasheet governance section in `report/`. |
| **12** | `ExplanationResult` schema integration | 15, 16 | Maintained as an internal dataclass in `explainability.py` without modifying M1 `schema.py`. |
| **13** | Dashboard pass/fail semantics | 05 | Framed as an analytical "scanning aid" rather than a legal certification verdict. |
| **14** | SHAP visual format | 05, 15 | Rendered strictly as base64-encoded inline raster PNGs (`data:image/png;base64,...`). |
| **15** | Checkpoint filename mismatch | 01, 04 | Documented `fairface_alldata_20191111.pt` as primary default and `res34_fair_align_multi_7_20190809.pt` as alternative. |
| **16** | Dataset size (108,501 vs 97,698) | 01, 03 | Verified 97,698 released images on disk (86,744 train + 10,954 val); 108,501 documented as pre-discard total. |
| **17** | Preprocessing method (MTCNN vs dlib) | 04, 07 | Stale MTCNN references updated to `dlib` CNN face detector with 5-point alignment. |
| **18** | File path column ambiguity | 01 | `PredictionsFileInterface` maps `face_name_align` for predictions and `file` for raw label CSVs. |
| **19** | Track prompt label drift | 17, 18 | Resolved in master project register (Track 17 = Strategy Pattern, Track 18 = pytest Suite). |
| **20** | Ingestion sample check naming | 03 | Named `insufficient_sample_at_ingestion` to avoid colliding with `MetricResult.insufficient_sample`. |
| **21** | Constant duplication in statistics | 11 | `fairness/statistics.py` imports `MIN_SUBGROUP_SAMPLE_SIZE` directly from `schema.py`. |
