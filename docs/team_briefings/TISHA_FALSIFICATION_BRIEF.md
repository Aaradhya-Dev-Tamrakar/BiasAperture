# Team Briefing: Falsification & Pre-Flight Verification Contracts (#56, #21)

**Owner / Assignee:** `@tiixsha`  
**Architectural Peer / Reviewer:** `@AaradhyaDT`  
**Purpose:** Pre-flight engineering guardrails, edge-case falsification criteria, and statutory verification contracts to support implementation without violating domain ownership boundaries.

---

## Part 1: Issue #56 — SigLIP2 Vision-Language Benchmark Integration (Model 5)

### Target Checkpoint & Checkpoint Architecture
- **Model Identifier:** `prithivMLmods/Realistic-Gender-Classification` (Hugging Face)
- **Base Backbone:** `google/siglip2-base-patch16-224` (Vision-Language Contrastive Foundation Model)
- **Primary Deliverables:**
  - `scripts/predict_siglip.py`
  - Validation split predictions CSV: `data/processed/fairface_predictions_siglip_val.csv` ($N = 10,954$)
  - Standalone HTML dossier & companion A4 PDF
  - Unit tests: `src/tests/test_predict_siglip.py`
  - 5-model comparative benchmark table update in `PERSONAL_LOG.md`

### Falsification Traps & Architectural Guardrails

#### 1. Architectural Taxonomy Guardrail (Supervised Head vs. Zero-Shot VLM)
- **The Trap:** Claiming that this evaluation benchmarks "zero-shot vision-language inference via text prompt similarity".
- **The Ground Truth:** While the vision encoder was pretrained with SigLIP2 sigmoid contrastive language-image loss, `prithivMLmods/Realistic-Gender-Classification` is fine-tuned as a standard classification model (`SiglipForImageClassification`) with a dedicated 2-unit linear head (`num_labels=2`).
- **Defense Requirement:** In documentation, presentations, and thesis text, classify Model 5 as a *Fine-Tuned Sigmoid Contrastive Vision Tower (`SiglipForImageClassification`)*, **not** zero-shot open-vocabulary scoring. This prevents an external examiner from challenging prompt engineering methodology.

#### 2. Label Polarity Inversion Falsification
- **The Trap:** Inverting the `0` vs. `1` index mapping, which causes predicted class labels to flip, yielding a ~15% inverted accuracy artifact.
- **The Ground Truth:** Before running batch inference across all 10,954 validation images, inspect:
  ```python
  from transformers import AutoModelForImageClassification
  model = AutoModelForImageClassification.from_pretrained("prithivMLmods/Realistic-Gender-Classification")
  print("id2label mapping:", model.config.id2label)
  ```
- **Pre-Flight Test:** Run inference on 10 known validation samples where `gender == "Female"` and 10 where `gender == "Male"`. Verify that `normalize_gender_label()` produces matching categorical strings (`"Female"` and `"Male"`) with expected baseline accuracy (>85%).

#### 3. Image Preprocessing & Normalization Contract
- **The Trap:** Reusing ImageNet mean/standard deviation normalization (`mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]`) or center-cropping transforms from `predict_resnet50.py`.
- **The Ground Truth:** SigLIP2 processors (`SiglipImageProcessor`) resize images directly to $224 \times 224$ and rescale pixel intensities to $[-1.0, 1.0]$ via `rescale_factor = 1/127.5` with `image_mean = [0.5, 0.5, 0.5]` and `image_std = [0.5, 0.5, 0.5]`.
- **Requirement:** Rely strictly on `AutoImageProcessor.from_pretrained("prithivMLmods/Realistic-Gender-Classification")` inside the PyTorch `Dataset` collator rather than custom TorchVision transforms.

#### 4. Audit-Cohort Integrity & Schema Lock (Milestone M1)
- **The Trap:** Catching `FileNotFoundError` or image decode exceptions with `try/except: continue`, silently dropping corrupted images and yielding $N < 10,954$.
- **The Ground Truth:** The FairFace validation split contains exactly 10,954 images. Any dropped row invalidates cross-model comparability against Models 1–4.
- **Requirement:** Raise an explicit `RuntimeError` on read failure:
  ```python
  try:
      img = Image.open(img_path).convert("RGB")
  except Exception as exc:
      raise RuntimeError(
          f"Audit-cohort integrity violation: failed to read image '{img_filename}' "
          f"at '{img_path}': {exc}. Dropping rows is strictly prohibited."
      ) from exc
  ```
- **Output CSV Columns:** Must match Milestone M1 schema:
  `face_name_align,true_gender,predicted_gender,subgroup_race,subgroup_gender,subgroup_age`

---

## Part 2: Issue #21 — EU AI Act Article 10 Timeline Alignment

### Regulatory Context & Defect Analysis
- **Current Defect:** Presentation slide 03 and certain background documentation state: *"The EU AI Act (Article 10) enters into force 2 August 2026... This creates an immediate compliance imperative"*.
- **The Ground Truth:**
  - Regulation (EU) 2024/1689 entered into force on 1 August 2024.
  - Phased applicability under Article 113 was amended by **Regulation (EU) 2026/1744** (Omnibus Deferral).
  - High-risk AI requirements under Chapter III (including Article 10 Data and Data Governance) apply from:
    - **2 December 2027** for Annex III systems (including facial analysis / biometric categorization systems).
    - **2 August 2028** for Annex I regulated products.
  - Prohibited AI practices under Article 5 (such as untargeted scraping of facial images) became applicable on **2 February 2025**.
  - Regulation (EU) 2026/1744 deleted former Article 10(5) and inserted **Article 4a** (permitting strictly necessary processing of special-category personal data for bias detection and correction under strict safeguards).

### Exact Remediation Target Inventory

1. `presentation/slides/03_regulatory.tex`:
   - Line 10: Update subtitle from generic applicability to reflect the Article 113 timetable as amended by Regulation (EU) 2026/1744.
   - Text modification: Clarify that Annex III biometric categorization systems must comply by **2 December 2027**, establishing an active compliance preparation window rather than an expired 2026 deadline.
2. `docs/DATA_GOVERNANCE.md`:
   - Line 31: Replace residual references to "Article 10(5) & Article 4a" with direct reference to **Article 4a (inserted by Regulation (EU) 2026/1744)**, noting that former Article 10(5) was deleted.
3. `docs/PROPOSAL_DEFENSE_MASTER_DOSSIER.md`:
   - Line 125: Reframe the regulatory deadline bullet from "immediate 2026 imperative" to "phased statutory enforcement window (December 2027 for Annex III biometric categorization systems under Regulation (EU) 2026/1744)".
4. `docs/PRESENTATION_DISCREPANCY_NOTES.md`:
   - Mark Discrepancy Ledger item #5 as **RESOLVED** once slide 03 and documentation targets are synchronized.

---

## Pre-Flight Verification Checklist

Before submitting PRs for Issues #56 or #21, verify against these deterministic gates:

- [ ] `uv run --extra dev ruff check src/ scripts/` passes with 0 errors.
- [ ] `uv run --extra dev ruff format --check src/ scripts/` confirms clean formatting.
- [ ] `python scripts/verify.py` passes all deterministic AST, lint, and reconciliation checks.
- [ ] For #56: `wc -l data/processed/fairface_predictions_siglip_val.csv` outputs exactly 10,955 lines (header + 10,954 records).
- [ ] For #56: `python -c "import pandas as pd; df=pd.read_csv('data/processed/fairface_predictions_siglip_val.csv'); assert len(df)==10954; assert set(df['predicted_gender'])=={'Male', 'Female'}"` runs without assertion error.
- [ ] For #21: Zero occurrences of "Article 10 enters into force 2 August 2026" remain across LaTeX slides, markdown docs, and HTML templates.
