# Data Processing & Demographic Profiling Pipeline

This document details the data ingestion, demographic alignment, intersectional cohort partitioning, and batch inference architecture implemented within **BiasAperture**.

---

## 1. Pipeline Overview & Diagnostic Scope

BiasAperture operates under a **strict diagnostic scope**:
- The framework ingests pre-labeled demographic face datasets, processes model prediction streams, measures demographic performance disparities across specified demographic axes, and compiles compliance dossiers.
- The framework **never** retrains models, debiases model weights, or generates synthetic training samples.
- The pipeline adheres strictly to **Milestone M1 Schema Invariance** (`src/bias_aperture/schema.py`), ensuring complete separation between data ingestion, inference logging, metric computation, and report rendering.

```
Raw FairFace Archive
  (Images & CSVs)
        │
        ▼
Data Ingestion & Integrity Validation
  (FairFaceImageDataset / data_ingestion.py)
        │
        ├──▶ In-Process / Batch Inference (ViT-B/16 & ResNet-34)
        │         │
        │         ▼
        │    Standardized Predictions File (CSV)
        │         │
        ▼         ▼
Demographic Alignment & Cohort Partitioning
  (PredictionsFileInterface / SubjectRecord)
        │
        ▼
Intersectional Contingency Matrix (126 Cohorts)
  - 7 Race × 2 Gender × 9 Age cohorts
  - Sample threshold check (n >= 30)
        │
        ▼
Disparity Evaluation & Statistical Confidence
  (Chi-Square, 95% Bootstrap CI, Statistical Parity, Equal Opportunity)
        │
        ▼
Dual-Format Compliance Dossiers (HTML + Immutable A4 PDF)
```

---

## 2. FairFace Ingestion & Pre-Alignment

### 2.1 Dataset Taxonomy & Attributes
BiasAperture benchmarks facial analysis models against the **FairFace** benchmark dataset (Kärkkäinen & Joo, 2021). FairFace provides demographic annotations balanced across 7 race/ethnicity groups:
- **Race / Ethnicity (7 categories)**:
  - `White`
  - `Black`
  - `Indian`
  - `East Asian`
  - `Southeast Asian`
  - `Middle Eastern`
  - `Latino_Hispanic`
- **Perceived Gender (2 categories)**:
  - `Male`
  - `Female`
- **Age (9 standard categories)**:
  - `0-2`, `3-9`, `10-19`, `20-29`, `30-39`, `40-49`, `50-59`, `60-69`, `70+`

### 2.2 Face Cropping and Alignment
To eliminate confounding geometric noise (head tilts, variable focal distances, asymmetric shoulder crops), raw input images pass through standard affine alignment based on 5 facial landmark coordinates (inner/outer eye corners and nose tip):
- **Margin Ratio**: Pre-aligned images use a padding margin ratio of 0.25 (or 1.25 for context sensitivity), centered on detected facial bounding boxes.
- **Resolution**: Normalized to $224 \times 224$ pixels, standardized with ImageNet mean and standard deviation tensors for Vision Transformer (ViT) and ResNet ingestion.

### 2.3 Multi-Dataset Architecture & Registry (`dataset_adapters.py`)
To extend diagnostic evaluation beyond FairFace, BiasAperture provides an extensible dataset adapter framework (`DatasetAdapter` and `DatasetRegistry`):
1. **FairFace Adapter (`fairface`)**:
   - Ingests canonical 7-race, 9-age, 2-gender annotations.
   - Enforces standard categorization without label remapping.
2. **UTKFace Adapter (`utkface`)**:
   - Ingests filenames or CSV records formatted with UTKFace nomenclature: `[age]_[gender]_[race]_[date].jpg`.
   - Age discretization: Maps continuous integer ages into standard FairFace age brackets (`0-2`, `3-9`, `10-19`, `20-29`, etc.).
   - Race taxonomy mapping:
     - `0` -> `White`
     - `1` -> `Black`
     - `2` -> `East Asian`
     - `3` -> `Indian`
     - `4` -> `Latino_Hispanic`
   - Explicit quality caveats: UTKFace carries inherent DEX age-estimator noise and race taxonomy collapse (conflating Southeast Asian into East Asian/Indian, and omitting Middle Eastern). These caveats are documented in `ReportContext.dataset_limitations` and propagated into the compliance report.


---

## 3. Cohort Integrity & Fail-Fast Guarantees

Preserving the statistical validity of an algorithmic audit requires absolute data fidelity:
1. **Zero Synthetic Substitution**:
   - `FairFaceImageDataset` prohibits substituting synthetic blank, noise, or zero-filled (black) frames when an image cannot be read or located.
   - Silently substituting synthetic images distorts model confidence, shifts error distributions, and corrupts measured demographic subgroups.
2. **Fail-Fast Error Propagation**:
   - Any missing, truncated, or corrupted image raises an explicit `RuntimeError` identifying the exact image path, filename, and underlying I/O error.
   - Auditing runs halt deterministically rather than reporting distorted parity metrics.
3. **Immutability of Ground Truth**:
   - Ingestion records are parsed directly into immutable `SubjectRecord` instances.
   - Every subject record retains its original `image_id`, demographic labels (`race`, `gender`, `age`), ground truth label (`true_label`), and model output (`predicted_label`).

---

## 4. Multi-Model Batch Inference Pipeline

BiasAperture evaluates comparative fairness between diverse architectural paradigms:
- **Vision Transformer (ViT-B/16)**: `google/vit-base-patch16-224` (or task-specific checkpoint `rizvandwiki/gender-classification-2`), evaluating self-attention patch embeddings across demographic groups.
- **Convolutional Network (ResNet-34)**: Deep residual convolutional network baseline evaluating localized inductive biases.

### 4.1 Prediction Ingestion Interface
Inference outputs are serialized to standardized prediction CSV records containing:
```csv
face_name_align,race,gender,age,true_label,predicted_label
1.jpg,East Asian,Female,20-29,Female,Female
2.jpg,White,Male,30-39,Male,Male
```
These are ingested by `PredictionsFileInterface` (or loaded directly through `InProcessInterface` for interactive auditing) to construct the internal audit cohort.

---

## 5. 126-Cohort Intersectional Contingency Matrix

While aggregate parity metrics (e.g., across race alone or gender alone) reveal high-level disparities, compound biases frequently hide at intersections (Crenshaw, 1989; Buolamwini & Gebru, 2018).

BiasAperture generates a full **126-cohort contingency matrix**:
$$\text{Total Cohorts} = 7 \text{ (Race)} \times 2 \text{ (Gender)} \times 9 \text{ (Age)} = 126 \text{ Intersectional Subgroups}$$

### 5.1 Sample Size Invariant ($n \ge 30$)
Per the Milestone M1 Schema specification:
- Any intersectional subgroup with $n < 30$ samples is flagged with `insufficient_sample=True`.
- The corresponding `metric_value` is set to `None` to prevent spurious claims of disparity or compliance on statistically inadequate sample sizes (Central Limit Theorem baseline).
- The count $n$ is explicitly reported alongside standard errors and confidence intervals.

---

## 6. Statistical Significance & Disparity Metrics

For all eligible subgroups ($n \ge 30$), the pipeline calculates:
1. **Point Estimates**:
   - **Selection Rate / Demographic Parity Ratio (DPR)**: Disparity in positive outcome rates across groups.
   - **Equalized Odds / True Positive Rate Ratio (TPRR)**: Parity in recall between demographic groups.
   - **False Positive Rate Disparity**: Parity in error distributions.
2. **Confidence Intervals**:
   - Non-parametric **95% Bootstrap Confidence Intervals** ($B \ge 1,000$ resamples) to capture sampling variance without assuming normality.
3. **Hypothesis Testing**:
   - **Pearson's $\chi^2$ Test of Independence** ($\alpha = 0.05$) to establish statistical significance against the null hypothesis of demographic independence.

---

## 7. Dual-Format Export Standard

Every audit run produces two synchronized artifacts:
1. **Interactive HTML Dossier**:
   - Air-gapped, zero-CDN compliance report.
   - Inline raw `<svg>` forest plots and disparity whiskers.
   - `schema.org` JSON-LD metadata for machine readability.
2. **Immutable A4 PDF Companion**:
   - Generated via headless Blink engine (`scripts/export_report_pdf.py`).
   - Exact 1-to-1 visual correspondence with print pagination rules (`@media print`, page breaks, vector-crisp typography).
