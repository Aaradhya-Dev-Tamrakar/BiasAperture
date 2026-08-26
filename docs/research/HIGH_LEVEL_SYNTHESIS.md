# BiasAperture — Research Sprint: High-Level Executive Synthesis

**Target Audience:** Project Leads, Fellowship Supervisors, Technical Assessors, Viva Defense Panel  
**Document Level:** High-Level (Executive, Novelty Defense, Regulatory Mapping & Strategic Overview)  
**Date:** August 2026  
**Context:** Milestone M1 Completion & 20-Track Parallel Research Sprint

---

## 1. Executive Summary & Vision

**BiasAperture** is an open-source, strictly diagnostic demographic bias auditing platform for computer vision (facial analysis) models.

Modern facial analysis systems exhibit well-documented performance disparities across intersectional demographic groups (e.g., race, gender, and age). While foundational academic toolkits exist for tabular algorithmic fairness (such as Fairlearn and AIF360), they remain disconnected from the realities of computer vision pipelines, lack standardized statistical safeguards against sample-size artifacts, and do not bridge the gap between technical metric outputs and emerging regulatory mandates.

BiasAperture bridges this operational gap. It consumes facial image datasets and model predictions, executes dual-backend cross-validated fairness computations, enforces hard sample-size ($n \ge 30$) and uncertainty (bootstrap CI) guards, triggers targeted local explainability (SHAP) on statistically significant disparities, and exports a single-file, regulator-legible compliance report aligned with the **EU Artificial Intelligence Act (Regulation EU 2024/1689)** and the **NIST AI Risk Management Framework (AI 100-1)**.

```┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                  BIASAPERTURE ARCHITECTURAL FLOW                                │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

   [ Computer Vision Model & Dataset ]
                    │
                    ▼
     [ 1. Data & Model Ingestion ] ──────────► dlib CNN Align + Schema Invariant Validation
                    │
                    ▼
     [ 2. Fairness Detection Engine ] ───────► Dual-Backend Cross-Validation (Fairlearn + AIF360)
                    │                         ├── Core Four Metrics: DPD, EOD, EOP, DIR
                    │                         └── Statistical Rigor: Chi-Squared (p<0.05) + 95% BCa CI
                    ▼
     [ 3. Targeted Explainability ] ─────────► Triggered on Flagged Disparities (p < α, n ≥ 30)
                    │                         ├── SHAP (PartitionExplainer / GradientExplainer)
                    │                         └── Proxy Detection (Attribution Shift + ITA Skin Tone)
                    ▼
     [ 4. Compliance Report Generator ] ─────► Self-Contained HTML (Mitchell Model Card + Gebru Datasheet)
                                              └── Regulatory Tracing: EU AI Act Art. 10 & NIST AI RMF
```

---

## 2. The Five Operating Modules

BiasAperture is structured into five cohesive work packages (WPs) operating under strict scope boundaries:

1. **WP1: Baseline & Schema Lock (Completed)**
   - Locked internal schema contracts (`SubjectRecord`, `MetricResult`) and taxonomies (7 race categories, 2 gender categories, 9 age bins).
   - Fixed the baseline reference classifier (`dchen236/FairFace` ResNet-34 multi-task architecture).
2. **WP2: Data Ingestion & Model Interfacing (Stream A)**
   - Dual-mode ingestion: `PredictionsFileInterface` (non-negotiable core batch CSV/JSON ingestion) and `InProcessInterface` (live PyTorch inference).
   - Two-mode validation (strict/fail-fast vs. profiling) verifying schema conformance and catching missing/corrupt values.
3. **WP3: Compliance Report Generation (Stream B)**
   - Single-file standalone HTML report generation using Jinja2 with inline CSS and base64-encoded visual artifacts.
   - Built-in **Model Cards for Model Reporting** (Mitchell et al., 2019, 9 sections) and **Datasheets for Datasets** (Gebru et al., 2018).
4. **WP4: Statistical Fairness Engine & Explainability (WP4 / Streams C, D, E)**
   - Evaluates the **Core Four** fairness metrics: Demographic Parity Difference (DPD), Equalized Odds Difference (EOD), Equal Opportunity Difference (EOP), and Disparate Impact Ratio (DIR).
   - Enforces the **NFR-003 sample-size guard ($n \ge 30$)** to eliminate false-positive disparities caused by small-cell noise.
   - Computes exact $\chi^2$ independence tests ($p$-value, $\alpha=0.05$) and 95% Bootstrap Confidence Intervals ($B \ge 1,000$ resamples).
   - Targeted local SHAP visual attribution and proxy variable detection.
5. **WP5: System Orchestration & CLI (Integration)**
   - High-level facade orchestrating the pipeline from raw ingestion to the final exported compliance dossier.

---

## 3. The 20-Track Research Sprint: Key Findings

To completely de-risk implementation, a comprehensive 20-track parallel research sprint was executed across 6 thematic streams:

| Stream | Focus Area | Tracks | Critical Takeaways & Decisions |
| --- | --- | :---: | --- |
| **Stream A** | Data Ingestion | 01–04 | • FairFace uses a ResNet-34 backbone with a single 18-unit multi-task head and `dlib` 5-point alignment (not MTCNN).<br>• Released dataset on disk contains **97,698 images** (86,744 train, 10,954 val).<br>• **UTKFace is formally cut** due to 3/7 race-mapping collapses and DEX age noise. |
| **Stream B** | Report Gen | 05–08 | • Single-file HTML generator with zero CDN/JS runtime dependencies.<br>• Custom Jinja2 implementation chosen over `model-card-toolkit` (avoids rigid TFX dependencies).<br>• Complete sub-clause mapping for EU AI Act Article 10(2)–10(5). |
| **Stream C** | Fairness Math | 09–14 | • Discovered mathematical divergence between Fairlearn (max-of-gaps) and AIF360 (mean-of-gaps) for EOD; unified under max-of-gaps.<br>• Uncovered that AIF360 returns signed EOP while Fairlearn is unsigned (fixed with `abs()`).<br>• Proved $3\times$ disparity skew if $n < 30$ groups are filtered post-computation rather than pre-computation.<br>• Designed custom BCa/percentile bootstrap because `scipy.stats.bootstrap` fails on multi-group metrics. |
| **Stream D** | Explainability | 15–16 | • Selected `PartitionExplainer` as black-box default and `GradientExplainer` for live PyTorch models.<br>• Designed dual-signal proxy detection combining spatial SHAP shift with Individual Typology Angle (ITA) skin-tone colorimetry.<br>• Grounded limitations in Bilodeau et al. (2022) impossibility results. |
| **Stream E** | Architecture | 17–18 | • Formulated `FairnessBackend` Strategy pattern and `CrossValidationOrchestrator`.<br>• Built shared sample-size logic in `base.py` to prevent false backend divergence.<br>• Engineered known-answer 8-record test suite and Hypothesis property tests. |
| **Stream F** | Defense | 19–20 | • Mapped platform directly to NIST AI RMF **Measure** function (2.11, 2.3, 1.1).<br>• Executed competitive audit against 7 industry tools confirming unique positioning. |

---

## 4. Defensible Novelty & Competitor Positioning

A common question during technical defenses is: *"Why build a new tool when Fairlearn, AIF360, and Aequitas already exist?"*

The novelty of BiasAperture lies not in reinventing individual mathematical equations, but in **solving computer vision workflow friction through end-to-end architectural integration**.

### 4.1. Reproducible Competitive Search Protocol

- **Search Window**: August 2026
- **Sources & Indexes**: GitHub Topics (`fairness-metrics`, `bias-audit`, `ai-fairness`), PyPI, Papers With Code, Google Scholar.
- **Inclusion Criteria**: Open-source, maintained software packages offering demographic fairness metric evaluation or model card reporting.
- **Exclusion Criteria**: Domain-specific proprietary tools (healthcare-only EHR auditors), unmaintained research scripts (< 5 commits).
- **Reviewed Tool Set**: Aequitas, Fairlearn, AIF360, Google What-If Tool (WIT), JFAM, FAT Forensics, FairTest.

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                COMPETITOR CAPABILITY LANDSCAPE (2026)                                 │
├───────────────────┬──────────────┬──────────────┬──────────────┬──────────────┬───────────────────────┤
│ Tool / Framework  │ CV & 7-Race  │ Dual-Backend │ Stat Guards  │ Regulatory   │ Targeted Local SHAP   │
│                   │ Ingestion    │ Cross-Check  │ (n≥30 + CI)  │ Mapping      │ on Flagged Disparity  │
├───────────────────┼──────────────┼──────────────┼──────────────┼──────────────┼───────────────────────┤
│ Aequitas          │ ✗            │ ✗            │ ✗            │ ✗            │ ✗ (Global plots only) │
│ Fairlearn         │ ✗ (Tabular)  │ ✗            │ ✗            │ ✗            │ ✗                     │
│ AIF360            │ ✗ (Tabular)  │ ✗            │ ✗            │ ✗            │ ✗                     │
│ Google What-If    │ ✗ (Interactive) ✗           │ ✗            │ ✗            │ ✗                     │
│ JFAM (Alg. Audit) │ ✗ (Unlabeled)│ ✗            │ Partial      │ ✗            │ ✗                     │
│ FAT Forensics     │ ✗            │ ✗            │ ✗            │ ✗            │ Partial (Own module)  │
├───────────────────┼──────────────┼──────────────┼──────────────┼──────────────┼───────────────────────┤
│ **BiasAperture**  │ **✓ (Native)**│ **✓ (Locked)**│ **✓ (Hard)** │ **✓ (EU/NIST)**│ **✓ (Targeted Post)** │
└───────────────────┴──────────────┴──────────────┴──────────────┴──────────────┴───────────────────────┘
```

### The 5 Unique Architectural Differentiators

1. **CV-Native Demographic Pipeline**: Ingests raw multi-output predictions and aligns them directly into a 7-race, 2-gender, 9-age schema without manual tabular wrangling.
2. **Heterogeneous Implementation Cross-Validation**: Executes computations across two independent library backends (Fairlearn & AIF360) to catch library-specific bugs, numerical edge cases, and API discrepancies.
3. **Hard Statistical Invariants & Adequacy Guards**: Enforces $n \ge 30$ minimum screening guards alongside positive/negative class support checks and 95% BCa Bootstrap CIs.
4. **Targeted Explainability (Proxy Evidence Analysis)**: Automatically triggers SHAP and ITA skin-tone analysis *only* on rows that exhibit statistically verified bias ($p < 0.05, n \ge 30$).
5. **Direct Regulatory Provenance**: Maps each technical finding to EU AI Act Article 10 sub-clauses and NIST AI RMF Measure subcategories.

---

## 5. Regulatory Alignment: EU AI Act & NIST AI RMF

### EU Artificial Intelligence Act (Regulation EU 2024/1689)

BiasAperture provides technical audit capabilities supporting examination under high-risk AI data governance rules:

- **Article 10(2)(f)**: Mandates examination of potential biases in datasets. *Supported via Core Four disparity evaluation across 126 intersectional demographic cells.*
- **Article 10(2)(g)**: Requires measures to detect, prevent, and mitigate bias. *Explicit Scope Boundary: BiasAperture provides diagnostic **Detection, Measurement, and Documentation**; automated prevention and model mitigation are strictly out of scope.*
- **Article 10(3)**: Mandates that datasets have appropriate statistical properties. *Directly supported by the $n \ge 30$ screening guard, class support conditions, and 95% bootstrap confidence intervals.*
- **Article 10(5)**: Processing of special-category demographic data for bias auditing. *Addressed through the explicit Data Governance protocol ([`docs/DATA_GOVERNANCE.md`](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/BiasAperture/docs/DATA_GOVERNANCE.md)).*
- **Annex IV §2(g)**: Technical documentation requirements for validation and test procedures.

### NIST AI Risk Management Framework (NIST AI RMF 1.0, 2023)

*Note: Evaluated against NIST AI RMF 1.0 (January 2023), the locked baseline version for this study.*
BiasAperture instruments the **Measure** core function:

- **Measure 2.11**: Fairness and bias are evaluated, quantified, and documented.
- **Measure 1.1**: Risks that cannot be reliably quantified are documented rather than ignored (*the exact structural role of `insufficient_sample=True, metric_value=None`*).
- **Measure 1.3**: Rigorous assessment participation (*noting Measure 1.3 concerns independent personnel involvement, while BiasAperture provides heterogeneous dual-library implementation cross-checking*).
- **Measure 2.9**: Explainability and interpretability metrics (*realized via targeted SHAP pixel attributions and ITA skin colorimetry*).

---

## 6. Scope Invariants & Descoping Strategy (Cut-List)

To guarantee deterministic, high-quality completion on the fellowship schedule, the project operates under strict non-negotiable boundaries and an established cut-list.

### What BiasAperture Will NEVER Do

- **No Model Retraining / Fine-Tuning**: BiasAperture is strictly diagnostic.
- **No In-Processing Weight Debiasing**: Does not alter weights or loss functions.
- **No Synthetic Data Generation**: Does not generate synthetic demographic faces.

### Formal Cut-List (Ordered by Drop Priority)

1. **Web UI**: Drop Streamlit/Flask; retain robust CLI and static HTML exports.
2. **UTKFace Benchmark**: Formally dropped to focus 100% of engineering bandwidth on FairFace.
3. **PDF Generation**: Retain standalone HTML; drop headless browser PDF compilation.
4. **In-Process PyTorch Inference**: Fall back strictly to batch predictions file ingestion (`PredictionsFileInterface`).
5. **AIF360 Backend**: Retain Fairlearn as standalone engine (only as an emergency measure).

---

## 7. Current Project State & Next Steps

### Project State & Verification Rigor

In academic evaluation and technical auditing, we maintain an explicit distinction between specification, empirical verification, and implementation maturity:

- **Research & Design Specification**: **Largely Complete (100%)** — All mathematical harmonizations, backend strategies, and schema contracts are locked.
- **Empirical Verification**: **Partly Specified, Formally Tracked (65%)** — Formally tracked in [`docs/research/CLAIM_LEDGER.md`](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/BiasAperture/docs/research/CLAIM_LEDGER.md) across 20 claims (7 codified in passing automated tests, 13 verified via primary sources, external datasets, and REPL probes).
- **Implementation**: **In Progress (~65% overall codebase progress)** — Core schema, model interfaces, data ingestion pipeline, and backend harmonization tests all passing (39/39 tests); concrete fairness backends and HTML generators under active development.
- **End-to-End Validation**: **Planned (WP5)** — Execution of the complete 97,698-image FairFace benchmark audit.

> **Methodology Chapter Formulation:**  
> *"BiasAperture employed parallel AI-assisted reconnaissance to accelerate source exploration and hypothesis generation; all consequential technical claims were subsequently organized into an auditable claim ledger and subjected to primary-source inspection, isolated empirical probing, known-answer validation, and reproducibility testing before implementation."*

```
Milestone Implementation State:
Overall Progress: [████████████████░░░░] 65%
├── WP1: Schema Lock & Baseline (100% - COMPLETED)
├── Research Synthesis & Claim Ledger (100% - LOCKED & TRACKED)
├── WP2: Data Ingestion & Test Matrix (70% - In Progress, 17/17 tests passing)
├── WP3: Compliance Reporting (50% - In Progress, HTML contract verified)
├── WP4: Fairness Engine & Explainability (60% - In Progress, dual-backend harmonization verified)
└── WP5: Integration & CLI (20% - In Progress, orchestration pipeline staged)
```

With the research and design specifications de-risked, and data ingestion pipeline fully operational (17/17 tests), the roadmap focuses on completing remaining critical work:

1. ✅ `bias_aperture/data_ingestion.py` complete with validation modes & OvR transformer (Stream A complete).
2. Implement `bias_aperture/report/generator.py` and finalize Jinja2 HTML templates (Stream B).
3. Implement `bias_aperture/fairness/backends.py`, statistical engines (BCa bootstrap, χ² FWER), and SHAP explainability (WP4).
4. Wire the end-to-end CLI orchestrator and conduct the final benchmark audit (WP5).
