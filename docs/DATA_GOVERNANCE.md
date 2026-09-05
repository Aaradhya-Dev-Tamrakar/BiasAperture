# BiasAperture — Data Governance & Privacy Protocol

**Document Version:** 1.0.0 (Locked Baseline)  
**Scope:** Ethical, legal, and operational governance for facial imagery and demographic metadata ingestion  
**Applicability:** All BiasAperture pipelines, datasets, test matrices, and development environments  
**Date:** August 2026

---

## 1. Dataset Provenance & Licensing

BiasAperture utilizes benchmark computer vision datasets strictly for scientific diagnostic evaluation and demographic bias auditing.

| Dataset | Primary Source / Authors | Original Image Origin | Licensing Terms | Intended Usage |
|---|---|---|---|---|
| **FairFace** | Karkkainen & Joo (2021) | YFCC-100M (Flickr CC licenses) | Custom Research Non-Commercial License | Benchmark bias evaluation & demographic classifier baseline |

### 1.1. Ingestion Restrictions

- **No Redistribution**: BiasAperture code repositories do not distribute or host raw facial imagery. All image files reside locally under `data/raw/` and are strictly excluded via `.gitignore`.
- **Reference-Only Access**: Pipelines ingest images via local file paths or structured prediction CSVs.

---

## 2. Special-Category Demographic Data & Regulatory Safeguards

Demographic attributes (race, ethnic origin, gender, and age) represent sensitive, special-category personal data under global data protection frameworks (including GDPR Article 9 and EU AI Act Article 10(5) / Article 4a). This project identifies and documents applicable special-category data considerations and safeguards for diagnostic bias auditing.

### 2.1. Statutory Justification for Bias Auditing

Under **EU AI Act Regulation (EU) 2024/1689 Article 10(5) & Article 4a**:
> *Providers of high-risk AI systems may process special categories of personal data solely to the extent strictly necessary for the purpose of ensuring bias detection and correction in relation to the high-risk AI systems... subject to appropriate safeguards.*

BiasAperture operates strictly within these diagnostic safeguards:

1. **Diagnostic Exclusivity**: Data is processed solely to measure disparity metrics and feature attributions; no biometric identification, surveillance, user profiling, or model retraining is performed.
2. **Synthetic / Anonymized Intermediate Artifacts**: Intermediate reports, confusion matrices, and bootstrap distributions contain only aggregate statistics ($n, p\text{-value}, \text{CI}$) rather than individual biometric identifiers.
3. **Feature Attribution & Surrogate Masking**: Attribution overlays (demographic-dummy surrogates or deferred spatial SHAP) are rendered as normalized gradient masks or aggregate dummy weights; original facial chips are not serialized into report payloads unless explicitly configured with local privacy flags.

---

## 3. Storage, Retention & Security Policy

1. **Local Ephemeral Storage**: Raw facial images are stored on local non-shared storage with standard filesystem access controls.
2. **No Cloud Ingestion Without Encryption**: Datasets must never be uploaded to public buckets or unauthenticated endpoints.
3. **Data Retention**: Test datasets and extracted features are retained only for the duration of the audit evaluation and benchmark study, following which raw caches can be purged.

---

## 4. Researcher Ethics & Responsibilities

1. **Taxonomy Limitations**: Demographic categorizations (e.g. 7-race classification) are coarse, socially constructed taxonomies provided by the benchmark authors; they do not represent biological ground truth.
2. **Misuse Prevention**: BiasAperture tooling must never be deployed for automated demographic screening, discriminatory gatekeeping, or unconsented biometric profiling.
