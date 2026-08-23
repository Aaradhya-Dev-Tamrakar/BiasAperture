# Track 15 — SHAP for Image Classifiers
**Stream:** D (Explainability) · **Priority:** 🟡 Medium · **Owner Focus:** Tisha (WP4)
**Estimated Time:** 45 min · **Feeds:** `explainability.py`

## Instructions
1. Paste `CONTEXT.md` into Claude Desktop first
2. Then paste the prompt below
3. Save the output as `results/15_shap_integration.md`

## Prompt

Research SHAP (SHapley Additive exPlanations) for explaining a ResNet-34 image classifier's predictions. BiasAperture needs to run SHAP on every flagged disparity (FR-005). Cover:

1. **SHAP variant selection:**
   - KernelSHAP (model-agnostic, slow) vs. DeepSHAP (PyTorch-native, fast) vs. GradientSHAP
   - Which works with a pretrained ResNet-34 on aligned face images (224×224)?
   - Runtime estimate: SHAP on 1 image, 100 images, 1000 images?
2. **Integration with BiasAperture:**
   - Input: a SubjectRecord (image_id, demographics, true/predicted labels) + the model
   - Output: per-pixel or per-region SHAP values showing which facial features drove the prediction
   - Strategy pattern: SHAP as an interchangeable component (FR-005 spec)
3. **Visualization:**
   - `shap.image_plot()` — what does the output look like?
   - How to embed SHAP visualizations in the Jinja2 HTML report
   - Saving SHAP plots as PNG/SVG for report embedding
4. **Proxy variable detection:**
   - How to detect if the model is using skin tone as a proxy for race
   - Aggregate SHAP values across subgroups to compare feature importance

Provide a complete Python code example: load ResNet-34, run SHAP on one image, save visualization.
