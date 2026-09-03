# BiasAperture: Complete Low-Level Technical Overview

**Date:** September 2, 2026  
**Audience:** Developers, Implementers, Statistical Auditors  
**Purpose:** Single-source reference for all low-level technical details of BiasAperture

---

## Table of Contents

1. [Project Scope & Non-Negotiable Constraints](#project-scope)
2. [Internal Data Contracts (Locked at M1)](#data-contracts)
3. [Core Fairness Metrics](#fairness-metrics)
4. [Statistical Rigor Layer](#statistical-rigor)
5. [Backend Harmonization & Cross-Validation](#backend-harmonization)
6. [Data Ingestion Pipeline (WP2)](#data-ingestion)
7. [Compliance Report Generation (WP3)](#compliance-report)
8. [Explainability Layer](#explainability)
9. [FairFace Model Architecture](#fairface-model)
10. [Module Organization](#module-organization)
11. [Guards & Safety Mechanisms](#guards)
12. [Execution Flow (Happy Path)](#execution-flow)

---

## Project Scope & Non-Negotiable Constraints {#project-scope}

### What it does

- Ingest facial image datasets and demographic model predictions
- Execute dual-backend fairness computations (Fairlearn + AIF360)
- Measure demographic disparities across 7 races, 2 genders, 9 age groups
- Generate standalone HTML compliance reports (EU AI Act & NIST AI RMF compliant)
- Trigger targeted SHAP explainability on statistically significant disparities

### What it explicitly does NOT do (hard scope boundary)

- **No model retraining or fine-tuning** (strictly diagnostic)
- **No in-processing weight debiasing** or synthetic data generation
- **No web UI or PDF generation** (CLI + HTML only)
- **No model internals modification** or mitigation algorithms

---

## Internal Data Contracts (Locked at M1) {#data-contracts}

### SubjectRecord Schema

Every face in the dataset becomes one `SubjectRecord` in `src/bias_aperture/schema.py`:

```python
@dataclass(frozen=True)
class SubjectRecord:
    image_id: str                    # Unique face identifier
    race: RaceLabel                  # 7 categories: White, Black, Latino_Hispanic,
                                      # East Asian, Southeast Asian, Indian, Middle Eastern
    gender: GenderLabel              # 2 categories: Male, Female
    age: AgeLabel                    # 9 bins: 0-2, 3-9, 10-19, 20-29, 30-39,
                                      # 40-49, 50-59, 60-69, 70+
    true_label: str                  # Ground-truth label (audit-specific)
    predicted_label: str             # Model's prediction (audit-specific)
```

**Label Vocabularies (Immutable):**

| Category | Values |
|----------|--------|
| **Race (7)** | White, Black, Latino_Hispanic, East Asian, Southeast Asian, Indian, Middle Eastern |
| **Gender (2)** | Male, Female |
| **Age (9)** | 0-2, 3-9, 10-19, 20-29, 30-39, 40-49, 50-59, 60-69, 70+ |

### MetricResult Schema

Fairness engine output—one row per metric per subgroup:

```python
@dataclass(frozen=True)
class MetricResult:
    metric_name: str                 # One of: demographic_parity_difference,
                                      # equalized_odds_difference,
                                      # equal_opportunity_difference,
                                      # disparate_impact_ratio
    subgroup: str                    # e.g., "race=Black" or "race=Black&gender=Female"
    subgroup_sample_size: int        # Total observations in this subgroup
    metric_value: float | None       # None if insufficient_sample=True (NFR-003)
    ci_lower: float | None           # 95% Bootstrap CI lower bound
    ci_upper: float | None           # 95% Bootstrap CI upper bound
    p_value: float | None            # Chi-squared test p-value
    insufficient_sample: bool        # True if n < 30 (NFR-003 guard)
```

**Critical Guard (NFR-003):**

- If `subgroup_sample_size < 30`, then `insufficient_sample=True` and `metric_value=None`
- **Never fabricate values for small samples** — this is a hard enforcement in `__post_init__`

**Statistical Constants (Locked):**

```python
MIN_SUBGROUP_SAMPLE_SIZE = 30      # NFR-003: Engineering minimum
ALPHA = 0.05                        # NFR-001: Significance threshold
MIN_BOOTSTRAP_RESAMPLES = 1_000    # NFR-002: Minimum for 95% CI
```

---

## Core Fairness Metrics {#fairness-metrics}

### The Core Four

All four metrics are **computed on binary One-vs-Rest (OvR) basis** for multi-class tasks (7 races, 9 ages):

| Metric | Formula | Fair Value | Interpretation |
|--------|---------|-----------|-----------------|
| **DPD** (Demographic Parity Difference) | max P(Ŷ=1\|A=a) - min P(Ŷ=1\|A=a) | 0.0 | Selection rates uniform across groups |
| **EOD** (Equalized Odds Difference) | max(max TPRₐ - min TPRₐ, max FPRₐ - min FPRₐ) | 0.0 | Both true & false positive rates uniform |
| **EOP** (Equal Opportunity Difference) | max TPRₐ - min TPRₐ | 0.0 | True positive rates uniform across groups |
| **DIR** (Disparate Impact Ratio) | min P(Ŷ=1\|A=a) / max P(Ŷ=1\|A=a) | 1.0 | Selection ratio ≥ 80% (EEOC heuristic) |

### Multi-Class Evaluation Policy (OvR)

For tasks with $M > 2$ classes (7 races, 9 ages):

1. **Binarization**: Decompose into $M$ independent One-vs-Rest binary tasks
   $$Y^{(m)} = \mathbb{I}(Y = c_m), \quad \hat{Y}^{(m)} = \mathbb{I}(\hat{Y} = c_m)$$

2. **Metric Computation**: Compute all four metrics for each class $m$ independently

3. **Macro-Aggregation Policy**:
   - **Macro-DPD, Macro-EOP, Macro-EOD**: Unweighted arithmetic mean across all $M$ classes
     $$\text{Macro-DPD} = \frac{1}{M} \sum_{m=1}^M \text{DPD}^{(m)}$$
   - **Macro-DIR**: **NOT macro-averaged** (ratios don't average meaningfully)

4. **Per-Class Support Reporting**: Macro summaries always accompanied by per-class values and class-wise support counts $n_{Y=c_m, a}$

### Backend-Specific Harmonization

**Critical Divergence Resolutions (from 20-Track Research Sprint):**

1. **EOD (Equalized Odds Difference)**:
   - Fairlearn: max(|ΔTPRₐ|, |ΔFPRₐ|) — worst-case disparity
   - AIF360 native: ½(|ΔTPRₐ| + |ΔFPRₐ|) — average gap
   - **Resolution**: AIF360Backend adapted to compute worst-case (locked via max-of-gaps)

2. **EOP (Equal Opportunity Difference)**:
   - Fairlearn: Unsigned [0, 1]
   - AIF360: Signed [-1, 1]
   - **Resolution**: AIF360Backend applies `abs()` before storing to prevent divergence alerts

3. **DIR (Disparate Impact Ratio) Zero-Denominator**:
   - If max_a P(Ŷ=1|A=a) = 0.0 → DIR = 1.0 (no relative disparity)
   - Flag `absolute_selection_warning=True`
   - If min_a > 0 and max_a = 0 → DIR = 0.0 (complete exclusion)

---

## Statistical Rigor Layer {#statistical-rigor}

### Chi-Squared Independence Testing

1. **Table Layout**: For attribute $A$ with $K$ subgroups, construct 2×K matrix:
   $$O = \begin{bmatrix}
   n_{1, \text{pos}} & n_{2, \text{pos}} & \dots & n_{K, \text{pos}} \\
   n_{1, \text{neg}} & n_{2, \text{neg}} & \dots & n_{K, \text{neg}}
   \end{bmatrix}$$

2. **Independence Test**: Compute $\chi^2 = \sum \frac{(O_{ij} - E_{ij})^2}{E_{ij}}$ with dof = $K - 1$

3. **Holm-Bonferroni Step-Down FWER Adjustment**:
   Given $M$ sorted $p$-values $p_{(1)} \le p_{(2)} \le \dots \le p_{(M)}$:
   $$p_{(k)}^{\text{adj}} = \min \left( 1, \; \max_{j \le k} \left[ (M - j + 1) \cdot p_{(j)} \right] \right)$$
   Reject null hypothesis if $p_{(k)}^{\text{adj}} < \alpha = 0.05$

4. **Fallback**: Fisher's Exact Test for 2×2 tables with expected cell counts < 5

### Stratified BCa Bootstrap (B ≥ 1,000 resamples)

**Why custom bootstrap?** Standard `scipy.stats.bootstrap` fails on multi-group metrics and doesn't support stratification.

**Algorithm:**

```
Original Data (N subjects)
            ↓
Stratified Index Resampling (B=1000)
  For each group a: idx_boot_a = rng.choice(idx_a, size=len(idx_a))
            ↓
Metric Evaluation Loop (B replicates)
  θ̂*_b = [f(boot_b) for b in 1..B]
            ↓
Jackknife Acceleration (a) & Bias Correction (z₀)
            ↓
        [Is BCa Valid?]
       /    |    \
    YES     NO    Degenerate
     ↓      ↓        ↓
   BCa   Percentile  Percentile
   CIs   Fallback    Fallback
```

**Mathematical Steps:**

1. **Bootstrap Replication**: Compute $\hat{\theta}^*_1, \dots, \hat{\theta}^*_B$ over stratified resamples
   - Preserves observed group composition across all replicates
   - Each group resampled independently with replacement

2. **Bias-Correction Parameter ($z_0$)**:
   $$z_0 = \Phi^{-1} \left( \frac{1}{B} \sum_{b=1}^B \mathbb{I}(\hat{\theta}^*_b < \hat{\theta}) \right)$$
   - Empirical frequency of bootstrap replicates below observed point estimate
   - Measures whether bootstrap distribution is centered on point estimate

3. **Jackknife Acceleration ($a$)**:
   Using leave-one-out jackknife estimates $\hat{\theta}_{(i)}$ for $i=1, \dots, n$:
   $$a = \frac{\sum_{i=1}^n (\bar{\theta}_{(\cdot)} - \hat{\theta}_{(i)})^3}{6 \left[ \sum_{i=1}^n (\bar{\theta}_{(\cdot)} - \hat{\theta}_{(i)})^2 \right]^{3/2}}$$
   - Measures right-skewness of the bootstrap distribution
   - Stability threshold: |a| ≤ 0.5 (if violated, use percentile fallback)

4. **BCa Adjusted Percentiles ($\alpha_1, \alpha_2$)**:
   $$\alpha_1 = \Phi \left( z_0 + \frac{z_0 + z_{\alpha/2}}{1 - a(z_0 + z_{\alpha/2})} \right)$$
   $$\alpha_2 = \Phi \left( z_0 + \frac{z_0 + z_{1-\alpha/2}}{1 - a(z_0 + z_{1-\alpha/2})} \right)$$
   - Adjusted quantile indices for [2.5%, 97.5%] confidence interval

5. **Fallback Condition**: If |a| > 0.5, z₀ undefined, or adjusted quantiles fall outside [0, 1]:
   $$\text{CI}_{\text{fallback}} = \left[ \text{Percentile}\left(\hat{\theta}^*, 2.5\right), \; \text{Percentile}\left(\hat{\theta}^*, 97.5\right) \right]$$

### Replicate Validity Contract

Not every bootstrap replicate is valid (e.g., if a group has no positive class in a replicate, TPR undefined):

- **Valid fraction must ≥ 90%** (conservative engineering threshold τ = 0.90)
- If < 90% valid replicates → flag `insufficient_sample=True`
- **Per-metric validity rules**:
  - **DPD/DIR**: Requires non-empty denominator (any prediction rate)
  - **EOP**: Requires $n_{Y=1, a} > 0$ (positive class support)
  - **EOD**: Requires both $n_{Y=1, a} > 0$ AND $n_{Y=0, a} > 0$

### Statistical Adequacy & Estimand Mapping

The $n \ge 30$ threshold is an **engineering minimum screening invariant (NFR-003)**, not universal statistical sufficiency. Full validity requires metric-specific conservative screening:

| Metric / Test | Estimand Structure | Conservative Screening Conditions |
|---|---|---|
| DPD | Selection rates across groups | Total $n_a ≥ 30$ for all groups |
| EOP | True positive rates (Recall) | $n_a ≥ 30$ AND $n_{Y=1,a} ≥ 5$ |
| EOD | Joint TPR & FPR parity | $n_a ≥ 30$ AND $n_{Y=1,a} ≥ 5$ AND $n_{Y=0,a} ≥ 5$ |
| DIR | Bounded selection ratio | Total $n_a ≥ 30$; flag if max=0 |
| Chi-Squared | Contingency table homogeneity | Expected cell $E_{ij} ≥ 5$ (Cochran) |

**Note**: Minimum support of 5 observations is a conservative engineering rule, not asymptotic sufficiency claim.

---

## Backend Harmonization & Cross-Validation {#backend-harmonization}

### Two Independent Fairness Backends

**FairlearnBackend** (`fairness/fairlearn_backend.py`):

- Multi-class native pass (no OvR decomposition needed internally)
- max-of-gaps for EOD
- Unsigned EOP [0, 1]
- Deterministic metric computation via `fairlearn.metrics.*`

**AIF360Backend** (`fairness/aif360_backend.py`):

- N one-vs-rest binary runs (OvR decomposition required)
- Manual max-of-gaps adaptation (overrides AIF360's default mean-of-gaps)
- `abs()` on signed EOP before storing
- Uses BinaryLabelDataset strategy

### CrossValidationOrchestrator

Located in `fairness/orchestrator.py`:

```python
class CrossValidationOrchestrator:
    def __init__(self, backends: Sequence[FairnessBackend]):
        self.backends = backends  # [FairlearnBackend, AIF360Backend]
    
    def compute_metrics(self, data: Sequence[SubjectRecord]) -> tuple[
        list[MetricResult],  # Point estimates
        list[DivergenceWarning]  # Backend mismatches
    ]:
        results_per_backend = [b.compute_metrics(data) for b in self.backends]
        
        # Cross-check and flag divergences
        divergences = self._detect_divergence(results_per_backend)
        
        return results_per_backend[0], divergences
```

**Divergence Detection**:

- Compares results: if |v₁ - v₂| > ε, flag warning
- Tolerances:
  - **Differences (DPD, EOP, EOD)**: ε = 0.05
  - **Ratios (DIR)**: ε = 0.10
- **Shared base logic** in `base.py` prevents false divergences from pandas/numpy grouping inconsistencies

---

## Data Ingestion Pipeline (WP2) {#data-ingestion}

### ModelInterface Strategy Pattern

Abstract base class in `model_interface.py`:

```python
class ModelInterface(ABC):
    @abstractmethod
    def get_predictions(self) -> Iterator[SubjectRecord]:
        """Yield SubjectRecords from predictions."""
        pass
```

### Two Concrete Implementations

#### 1. PredictionsFileInterface (Non-negotiable core)

**Purpose**: Read CSV/JSON batch prediction files

**Responsibility**:

- Parse CSV columns or JSON records
- Map demographic columns → RACE_LABELS, GENDER_LABELS, AGE_LABELS
- Map task columns (caller-specified) → true_label, predicted_label
- Validate: mandatory fields present, labels in vocabulary, image_ids non-corrupt

**Usage**:

```python
interface = PredictionsFileInterface(
    predictions_file="results.csv",
    demographic_mapping={
        "race_col": "predicted_race",
        "gender_col": "predicted_gender",
        "age_col": "predicted_age"
    },
    task_mapping={
        "true_label": "ground_truth_gender",
        "predicted_label": "model_gender_pred"
    }
)

for subject in interface.get_predictions():
    print(subject.image_id, subject.race, subject.predicted_label)
```

#### 2. InProcessInterface (Optional PyTorch hook)

**Purpose**: Direct model inference on images (for live evaluation)

**Alignment Pipeline**:

1. `dlib.cnn_face_detection_model_v1`: Detect bounding box
2. `dlib.shape_predictor_5_face_landmarks`: Identify 5 landmarks (2 eye corners, nose base)
3. `dlib.get_face_chips(img, shapes, size=300, padding=0.25)`: Extract aligned 300×300 crop
4. Torchvision preprocessing: resize 224×224, normalize with ImageNet constants

**Normalization Constants**:

- μ = [0.485, 0.456, 0.406]
- σ = [0.229, 0.224, 0.225]

### Two-Mode Validation Engine

#### Strict/Fail-Fast Mode

- Production audits
- Raises error on first anomaly (missing field, unmapped label, corrupt image_id, duplicate)
- Halts execution immediately

#### Permissive/Profiling Mode

- Exploratory data ingestion
- Collects all anomalies without halting
- Returns structured `ValidationSummary` diagnostic report
- NaN distributions, syntax drifts, unmapped categories tracked

### Data Ingestion Flow

```
Raw CSV/JSON/Images
        ↓
ModelInterface.get_predictions()
        ↓
Iterator[SubjectRecord] stream
        ↓
Validator (Strict/Permissive)
        ↓
Validated Iterator[SubjectRecord]
        ↓
Filter by demographic label valid
        ↓
OvR Transformer (Multi-class → Binary)
        ↓
Ready for fairness engine
```

---

## Compliance Report Generation (WP3) {#compliance-report}

### Single-File Offline HTML

**Guarantees**:

- Zero CDN/JavaScript runtime dependencies
- Base64-encoded inline images (SHAP attributions)
- Embedded CSS (no external stylesheets)
- Self-contained standalone export

### Technology Stack

- **Templating**: Jinja2 (custom implementation, not TFX Model Card Toolkit)
- **Styling**: Inline CSS with semantic HTML5
- **Images**: Base64 PNG encoding for SHAP visual attribution

### Report Structure

1. **Model Card** (Mitchell et al., 2019):
   - Model details, intended use, performance, limitations, training procedures, evaluation procedures, ethical considerations, caveats, recommendations

2. **Datasheet for Datasets** (Gebru et al., 2018):
   - Motivation, composition, collection process, preprocessing, distribution, maintenance

3. **EU AI Act Article 10 Mapping**:
   - Traces each metric to regulatory sub-clauses (10.2.f, 10.2.g, 10.3, 10.5)
   - Demonstrates Article 10(2)–(5) compliance

4. **NIST AI RMF Measurement**:
   - Maps to NIST Measure 1.1, 2.11, 2.3, 2.9
   - Documents risk measurement and fairness evaluation

### Generation Flow

```
MetricResult[] + MetricResult[SHAP]
        ↓
Jinja2 Context Dictionary
        ↓
Template Rendering
        ├─ Model Card sections
        ├─ Datasheet sections
        ├─ Metric tables (DPD, EOD, EOP, DIR)
        ├─ Statistical confidence (CI, p-value)
        ├─ Regulatory mapping
        └─ Inline Base64 PNG SHAP images
        ↓
compliance.html (standalone)
```

---

## Explainability Layer {#explainability}

### Conditional Triggering

Explainability runs **only if** a metric row satisfies both conditions:

- $p\text{-value} < 0.05$ (statistically significant)
- $n \geq 30$ (sufficient sample size)

**Design Rationale**: Minimize compute overhead by targeting only high-confidence disparities.

### Architecture

```
Metric Result Row ──► [Is Disparity Flagged?] ──► NO ──► Skip SHAP (Zero overhead)
                           │ (p<0.05 AND n≥30)
                           ▼ YES
                    [Explainer Strategy]
                           │
           ┌────────────────┴────────────────┐
           ▼                                 ▼
 PartitionExplainer              GradientExplainer
 (Black-Box Default)             (In-Process PyTorch)
           │                                 │
           └────────────────┬────────────────┘
                            ▼
             [Pretrained Face Parsing (BiSeNet)]
                            ▼
             [Spatial Attribution Shift + ITA]
                            ▼
             [Inlined Base64 PNG Visualization]
```

### Two Explainer Strategies

#### PartitionExplainer (Black-Box Default)

- Works without model internals
- Divides image into segments
- Measures impact of masking each segment
- Suitable for arbitrary model pipelines

#### GradientExplainer (In-Process PyTorch Fast-Path)

- Direct access to model gradients
- Fast computation for live models
- Higher fidelity attribution
- Enabled only for InProcessInterface models

### Proxy Detection

**Dual-Signal Analysis**:

1. **Spatial SHAP Attribution Shift**: Which facial regions drive the disparity?
   - Eye regions? Mouth? Skin texture?
   - Indicates what proxy features model relies on

2. **Individual Typology Angle (ITA) Skin Tone**:
   - Measure skin tone colorimetry in sRGB space
   - Correlate with disparity magnitude
   - Evidence of skin-tone-based discrimination

**Output**: Annotated SHAP heatmap + ITA histogram + proxy risk assessment

---

## FairFace Model Architecture {#fairface-model}

### Baseline Reference

**Classifier**: dchen236/FairFace (ResNet-34 multi-task)

**Architecture**:

- **Backbone**: ResNet-34 (ImageNet-pretrained)
- **Output head**: Single fully connected layer, 18 units

```
[ Input Image 3x224x224 ]
        │
        ▼
[ ResNet-34 Backbone (Layers 1-4) ]
        │
        ▼
[ AdaptiveAvgPool2d → 512-d ]
        │
        ▼
[ Linear(512 → 18) ]
        │
        ├── Slice [0:7]   ──► Softmax ──► Race Probabilities (7 Classes)
        ├── Slice [7:9]   ──► Softmax ──► Gender Probabilities (2 Classes)
        └── Slice [9:18]  ──► Softmax ──► Age Probabilities (9 Classes)
```

### Inference Slicing

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

### Preprocessing & Alignment Pipeline

1. **Face Detection & Alignment**:
   - `dlib.cnn_face_detection_model_v1`: Detect bounding box
   - `dlib.shape_predictor_5_face_landmarks`: Identify 5 facial landmarks
   - `dlib.get_face_chips(img, shapes, size=300, padding=0.25)`: Extract aligned 300×300 crop

2. **Tensor Normalization**:
   - Resize to 224×224
   - Scale pixel values to [0.0, 1.0]
   - Normalize with ImageNet constants:
     - μ = [0.485, 0.456, 0.406]
     - σ = [0.229, 0.224, 0.225]

---

## Module Organization {#module-organization}

### Directory Structure

```
src/bias_aperture/
├── schema.py                    # Locked contracts (SubjectRecord, MetricResult)
├── model_interface.py           # Adapter pattern (PredictionsFile, InProcess)
├── data_ingestion.py            # Stream A (WP2): Validation, OvR transformer
├── report/
│   ├── __init__.py
│   ├── generator.py             # Stream B (WP3): Jinja2 compilation
│   └── templates/               # HTML templates + CSS
├── fairness/
│   ├── __init__.py
│   ├── base.py                  # Shared sample-size logic, FairnessBackend ABC
│   ├── fairlearn_backend.py     # FairlearnBackend implementation
│   ├── aif360_backend.py        # AIF360Backend implementation
│   ├── orchestrator.py          # CrossValidationOrchestrator
│   ├── statistics.py            # BCa bootstrap, Chi-squared, Holm-Bonferroni
│   └── exceptions.py            # Custom exceptions
├── explainability.py            # Demographic-dummy surrogate attribution
├── cli.py                       # High-level CLI facade
└── __init__.py

tests/
├── test_schema.py               # Schema invariants
├── test_data_ingestion.py       # Validation modes, OvR transformer
├── test_model_interface.py      # Interface contracts
├── test_backend_harmonization.py # Divergence detection
├── test_known_answer_fairness_metrics.py # Math verification
└── test_offline_report_contract.py # HTML generation
```

### Public API

Primary entry point: `bias_aperture/cli.py`

```python
# High-level facade
def audit_model(
    predictions_file: str,
    demographic_mapping: dict[str, str],
    task_mapping: dict[str, str],
    output_html: str,
    backend: Literal["fairlearn", "aif360", "both"] = "both",
    profiling_mode: bool = False
) -> Path:
    """Execute complete audit pipeline and export compliance report."""
```

---

## Guards & Safety Mechanisms {#guards}

| Guard | Code/Rule | Enforced By | Rationale |
|-------|-----------|-------------|-----------|
| **NFR-001** (Significance) | α = 0.05 | Chi-squared tests | Standard statistical threshold |
| **NFR-002** (Uncertainty) | B ≥ 1,000 | Bootstrap resampling | 95% CI stability |
| **NFR-003** (Sample Size) | n ≥ 30 | Pre-computation filtering | Eliminate noise-driven false positives |
| **Replicate Validity** | τ ≥ 90% | Bootstrap validity check | Reject degenerate replicates |
| **Stability Bound** | \|a\| ≤ 0.5 | Acceleration fallback | Use percentile when skewness extreme |
| **Schema Enforcement** | Dataclass `__post_init__` | Runtime validation | Prevent invalid MetricResult states |
| **Backend Divergence** | ε = 0.05 (diff), 0.10 (ratio) | CrossValidationOrchestrator | Catch library-specific bugs |

---

## Execution Flow (Happy Path) {#execution-flow}

### End-to-End Pipeline

```
Step 1: Ingest
  Raw predictions/images
  ├─ PredictionsFileInterface (CSV/JSON) OR
  └─ InProcessInterface (PyTorch)
  → Iterator[SubjectRecord]

Step 2: Validate
  Demographic labels, task labels, schema conformance
  ├─ Strict mode: raise on first error
  └─ Permissive mode: collect summary
  → Validated Iterator[SubjectRecord]

Step 3: Stratify
  Filter subgroups with n < 30
  → SubgroupRegistry {race=Black: 1,234 obs, race=White: 5,678 obs, ...}

Step 4: Compute
  DPD, EOP, EOD, DIR (both FairlearnBackend + AIF360Backend)
  → list[MetricResult] per backend

Step 5: Test
  Chi-squared independence + Holm-Bonferroni correction
  → p_value for each metric row

Step 6: Confidence
  Stratified BCa bootstrap (B=1,000)
  → ci_lower, ci_upper per metric row

Step 7: Explainability
  Conditional trigger: p < 0.05 AND n ≥ 30
   └─ Demographic-dummy surrogate attribution
   → Attribution evidence for the report

Step 8: Report
  Jinja2 compilation
  ├─ Model Card (9 sections)
  ├─ Datasheet (Gebru framework)
  ├─ Metric tables + confidence intervals
  ├─ Regulatory mapping (EU AI Act, NIST AI RMF)
  └─ Inline SHAP visualizations
  → compliance.html (standalone offline)
```

### Key Invariants Maintained

1. **No fabricated values**: If n < 30, metric_value=None (not 0.0 or placeholder)
2. **Dual-backend verification**: Always run both backends, report divergences
3. **Stratified bootstrap**: Preserve observed group composition across resamples
4. **Replicate validity**: Reject bootstrap replicates that violate metric definitions
5. **Regulatory tracing**: Every technical finding maps to EU AI Act / NIST AI RMF clause
6. **Offline guarantee**: HTML export has zero external dependencies

---

## Additional References

- **Full Specification**: `docs/research/LOW_LEVEL_SPECIFICATION.md`
- **Architecture**: `docs/research/MID_LEVEL_ARCHITECTURE.md`
- **Executive Summary**: `docs/research/HIGH_LEVEL_SYNTHESIS.md`
- **Claim Ledger**: `docs/research/CLAIM_LEDGER.md`
- **Schema Lock**: `docs/schema-lock-m1.md`
- **Data Governance**: `docs/DATA_GOVERNANCE.md`

---

**Document Version**: 1.0  
**Last Updated**: 2026-09-02  
**Status**: Locked (Milestone M1 Complete)
