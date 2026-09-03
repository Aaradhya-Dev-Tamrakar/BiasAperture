# Track 04 — FairFace predict.py Source Code Analysis
**Stream:** A (Data Pipeline) · **Priority:** 🔴 Critical · **Owner Focus:** Aaradhya (WP2)
**Estimated Time:** 30 min · **Feeds:** `data_ingestion.py`, `PredictionsFileInterface`

## Instructions
1. Paste `CONTEXT.md` into Claude Desktop first
2. Then paste the prompt below
3. Save the output as `results/04_fairface_predict_analysis.md`

## Prompt

Analyze the source code of `dchen236/FairFace` on GitHub — specifically `predict.py` and any related inference scripts. Document:
1. Exact output CSV column names and order
2. How the `race_7` vs `race_4` model variant is selected
3. What preprocessing (alignment, cropping, normalization) predict.py applies to images
4. The PyTorch model architecture (ResNet-34 variant) and how weights are loaded
5. Output confidence scores: does predict.py output probabilities or just argmax labels?
6. Any command-line arguments, config files, or environment requirements

This analysis feeds directly into building a PredictionsFileInterface that ingests predict.py's CSV output.
