# Track 01 — FairFace Dataset Deep-Dive
**Stream:** A (Data Pipeline) · **Priority:** 🔴 Critical · **Owner Focus:** Aaradhya (WP2)
**Estimated Time:** 30–45 min · **Feeds:** `data_ingestion.py`

## Instructions
1. Paste `CONTEXT.md` into Claude Desktop first
2. Then paste the prompt below
3. Save the output as `results/01_fairface_dataset_profile.md`

## Prompt

You are researching the FairFace dataset (Karkkainen & Joo, 2021 WACV) for a bias auditing platform called BiasAperture. Produce a technical profile document covering:
1. Exact CSV column names and dtypes from `dchen236/FairFace` predict.py output (race_7 model variant)
2. Distribution of images across the 7 race groups, 2 gender groups, 9 age bins
3. Known label noise or annotation disagreement rates from the original paper
4. Train/val split sizes and how `face_name_align` column maps to file paths
5. Any edge cases: missing values, ambiguous labels, multi-label rows
6. The exact command to run predict.py and the checkpoint file `res34_fair_align_multi_7_20190809.pt`

Output a structured markdown document with tables. Cite the WACV 2021 paper and the GitHub repo directly.
