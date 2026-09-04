# Track 15 & 16 Research Synthesis — SHAP Explainability & Proxy Detection

**Canonical Document:** Refer to [`docs/research/shap_explainability_and_weighting_principles.md`](../../docs/research/shap_explainability_and_weighting_principles.md) for the full mathematical derivations, combinatorial proofs, and KernelSHAP weighting analysis.

---

## Key Takeaways for Track 15 & 16

1. **SHAP Mathematical Principle:**
   * Cooperative game theory (Shapley, 1953; Lundberg & Lee, 2017).
   * Uniquely satisfies four fairness axioms: Efficiency, Symmetry, Dummy, and Additivity.
   * Total Payout: $f(x) - \mathbb{E}[f(X)]$.

2. **How Weights Are Decided:**
   * **Exact Shapley Combinatorial Weight:**
     $$W(|S|) = \frac{|S|!(|N| - |S| - 1)!}{|N|!} = \frac{1}{|N| \binom{|N|-1}{|S|}}$$
     Derived from uniform random player arrival orderings.
   * **KernelSHAP Regression Weighting Kernel:**
     $$\pi_x(z') = \frac{M - 1}{\binom{M}{|z'|} \cdot |z'| \cdot (M - |z'|)}$$
     Forms a U-shaped curve: places high weights on size-1 (main effects) and size-$(M-1)$ (total interaction effects) coalitions while down-weighting intermediate coalitions.

3. **What "Values" Mean:**
   * Marginal contribution relative to a background baseline expectation $\mathbb{E}[f(X)]$.
   * In linear surrogate models ([`src/bias_aperture/explainability.py`](../../src/bias_aperture/explainability.py)):
     $$\phi_i = w_i \cdot (x_i - \mathbb{E}[x_i])$$
     where $w_i$ is the surrogate model weight and $(x_i - \mathbb{E}[x_i])$ is the centered demographic feature value.

4. **Facial Analysis & Proxy Detection (FR-005 / Kurian et al. 2024):**
   * Pixel-level SHAP ($50,176$ pixels) is intractable; use `shap.PartitionExplainer` or face semantic region masks (skin, hair, eyes/nose/mouth, background).
   * Flagged disparities ($p < 0.05, n \ge 30$) trigger attribution mass analysis across regions.
   * Corroborate skin-tone attribution shifts with Individual Typology Angle (ITA) colorimetry.
