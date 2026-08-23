# Track 16 — Proxy Variable Detection via SHAP
**Stream:** D (Explainability) · **Priority:** 🟢 Low · **Owner Focus:** Tisha (WP4)
**Estimated Time:** 30 min · **Feeds:** `explainability.py`, proxy analysis methodology

## Instructions
1. Paste `CONTEXT.md` into Claude Desktop first
2. Then paste the prompt below
3. Save the output as `results/16_proxy_variable_detection.md`

## Prompt

Research proxy variable detection in facial analysis systems using SHAP attribution. This relates to Kurian et al. 2024 (eBioMedicine) finding that CNNs encode demographic info via unrelated visual features.

1. **The proxy problem:** A face classifier might use skin darkness, hair texture, or facial structure as proxies for race — even when race is not a training label. How does SHAP surface this?
2. **Aggregate SHAP analysis:** For a subgroup flagged with significant disparity, how to:
   - Average SHAP values across all images in that subgroup
   - Compare against the overall population's SHAP values
   - Identify features with statistically significant SHAP differences across subgroups
3. **Facial region segmentation:** Map pixel-level SHAP to semantic face regions (eyes, nose, mouth, skin, hair) — any existing tools or masks?
4. **Reporting format:** How to present proxy variable findings in a compliance report (EU AI Act Article 13 transparency, Article 15 accuracy/robustness)
5. **Limitations:** When can SHAP NOT detect proxy variables? False negatives?

Provide a concrete methodology: "Given a set of images flagged for disparity, here is the step-by-step analysis to determine proxy reliance."
