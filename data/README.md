# Data Directory Layout

This directory manages datasets and precomputed test matrices for BiasAperture.

> **Note**: Actual image datasets, zip archives, and large prediction files are gitignored and must not be committed to version control.

---

## Directory Structure

```
data/
├── raw/                 # Original, untouched datasets
│   ├── fairface/        # FairFace margin025 images and official label CSVs
│   └── utkface/         # UTKFace dataset (secondary benchmark, optional)
└── processed/           # Schema-aligned test matrices and stratified subsets
    ├── fairface_predictions_val.csv    # Predictions from predict.py on validation set
    └── fairface_dev_5000.csv           # Stratified development subset (n=5,000)
```

---

## Sourcing the FairFace Benchmark (FR-001)

1. **Images & Labels**: Sourced from the official repository [`joojs/fairface`](https://github.com/joojs/fairface).
   - Padding/Margin: `0.25` (aligned crop variant).
   - Label taxonomy: 7 races (`White`, `Black`, `Latino_Hispanic`, `East Asian`, `Southeast Asian`, `Indian`, `Middle Eastern`), 2 genders, 9 age groups.
2. **Classifier Baseline Weights (WBS 1.2)**:
   - Checkpoint: `res34_fair_align_multi_7_20190809.pt` (ResNet-34, race_7 variant).
   - Inference script: `predict.py`.
