# Track 06 — Model Cards Specification Deep-Dive
**Stream:** B (Report Generation) · **Priority:** 🟡 Medium · **Owner Focus:** Aaradhya (WP3)
**Estimated Time:** 30 min · **Feeds:** Report template structure

## Instructions
1. Paste `CONTEXT.md` into Claude Desktop first
2. Then paste the prompt below
3. Save the output as `results/06_model_cards_mapping.md`

## Prompt

Research the "Model Cards for Model Reporting" paper (Mitchell et al., 2019, FAT*) in detail. For each section of a Model Card, document:
1. What the section requires (per the paper)
2. How BiasAperture's output maps to it (we compute 4 disparity metrics across 7 race × 2 gender × 9 age groups on FairFace using a ResNet-34 classifier)
3. What data from BiasAperture's MetricResult schema fills each section
4. Draft content for each section, specific to BiasAperture's use case

Model Card sections to cover: Model Details, Intended Use, Factors, Metrics, Evaluation Data, Training Data (N/A — we audit, not train), Quantitative Analyses, Ethical Considerations, Caveats and Recommendations.

Also research Google's official Model Card Toolkit (model-card-toolkit Python package) — is it worth using, or is a custom Jinja2 template simpler?
