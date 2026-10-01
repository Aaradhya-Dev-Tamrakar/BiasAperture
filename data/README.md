# Dataset Management & Setup

This directory contains instructions and metadata for datasets and precomputed test matrices used by BiasAperture.

> **Note**: Raw image archives and large inference files are excluded from version control via `.gitignore`. Follow the instructions below to download and place datasets locally.

---

## Directory Layout

```
data/
├── fairface-img-margin025-trainval/  # FairFace benchmark images and official annotations
│   ├── data/                         # fairface_label_{train,val}.csv
│   └── faces/                        # margin025 train and val image crops
└── processed/                        # Precomputed prediction matrices and test splits
    ├── fairface_predictions_val.csv  # Validation inference baseline (10,954 records)
    └── fairface_dev_5000.csv         # Stratified development subset (n=5,000)
```

---

## FairFace Benchmark Setup

BiasAperture uses the **FairFace** benchmark (Kärkkäinen & Joo, 2021) as its primary evaluation dataset for auditing demographic bias in facial analysis models.

### 1. Sourcing Images & Annotations

- **Official Repository**: [FairFace on GitHub](https://github.com/joojs/fairface) (also available via `dchen236/FairFace`)
- **Dataset Size**: 97,698 released images (86,744 training images, 10,954 validation images)
- **Crop Variant**: `margin025` (0.25 padding around facial bounding box)
- **Preprocessing Pipeline**: `dlib` 5-point facial landmark alignment (`get_face_chips(size=300, padding=0.25)`), resized to 224×224 pixels and normalized with ImageNet statistics (mean `[0.485, 0.456, 0.406]`, std `[0.229, 0.224, 0.225]`).

### 2. Demographic Taxonomies

- **Race (7 categories)**: `White`, `Black`, `Latino_Hispanic`, `East Asian`, `Southeast Asian`, `Indian`, `Middle Eastern`
- **Gender (2 categories)**: `Male`, `Female`
- **Age (9 intervals)**: `0-2`, `3-9`, `10-19`, `20-29`, `30-39`, `40-49`, `50-59`, `60-69`, `70+`

### 3. Baseline Classifier Weights

For generating baseline prediction matrices:
- **Default Checkpoint**: `fairface_alldata_20191111.pt` (ResNet-34 multi-task architecture with an 18-unit output head for race, gender, and age classification).
- **Inference Script**: Run `scripts/run_fairface_inference.py` to produce model prediction CSVs for input into `bias-aperture audit`.
