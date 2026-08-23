# Data Directory Layout

This directory manages datasets and precomputed test matrices for BiasAperture.

> **Note**: Actual image datasets, zip archives, and large prediction files are gitignored and must not be committed to version control.

---

## Directory Structure

```
data/
├── raw/                 # Original, untouched datasets
│   ├── fairface/        # FairFace margin025 images and official label CSVs (97,698 released images)
│   └── utkface/         # [CUT] Secondary benchmark (cut per Cut-List #2 / Track 02)
└── processed/           # Schema-aligned test matrices and stratified subsets
    ├── fairface_predictions_val.csv    # Predictions from predict.py on validation set
    └── fairface_dev_5000.csv           # Stratified development subset (n=5,000)
```

---

## Sourcing the FairFace Benchmark (FR-001)

1. **Images & Labels**: Sourced from the official repository [`joojs/fairface`](https://github.com/joojs/fairface) (also `dchen236/FairFace`).
   - Dataset count: 97,698 released images on disk (86,744 train, 10,954 val; 108,501 was the pre-annotation discard total).
   - Padding/Margin: `0.25` (`margin025` aligned crop variant).
   - Preprocessing: `dlib` CNN face detector + 5-point landmark alignment (`get_face_chips(size=300, padding=0.25)`), resized to 224×224 and normalized with ImageNet mean/std.
   - Label taxonomy: 7 races (`White`, `Black`, `Latino_Hispanic`, `East Asian`, `Southeast Asian`, `Indian`, `Middle Eastern`), 2 genders (`Male`, `Female`), 9 age groups (`0-2`, `3-9`, `10-19`, `20-29`, `30-39`, `40-49`, `50-59`, `60-69`, `70+`).
2. **Classifier Baseline Weights (WBS 1.2)**:
   - Default Checkpoint: `fairface_alldata_20191111.pt` (ResNet-34, 18-unit head, 7-race multi-task; loaded by default in `predict.py`).
   - Alternative Checkpoint: `res34_fair_align_multi_7_20190809.pt` (older variant).
   - Inference script: `predict.py`.
