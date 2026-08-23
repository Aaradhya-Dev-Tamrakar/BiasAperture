# Track 19 — NIST AI RMF Detailed Mapping
**Stream:** F (Defense) · **Priority:** 🟡 Medium · **Owner Focus:** Both
**Estimated Time:** 30 min · **Feeds:** Report regulatory mapping, defense documentation

## Instructions
1. Paste `CONTEXT.md` into Claude Desktop first
2. Then paste the prompt below
3. Save the output as `results/19_nist_rmf_mapping.md`

## Prompt

Research the NIST AI Risk Management Framework (NIST AI 100-1, January 2023) in detail and map it to BiasAperture's outputs:

1. **Four core functions:** Govern, Map, Measure, Manage — what does each require?
2. **For each of BiasAperture's 4 metrics**, which NIST function does it serve?
   - demographic_parity_difference → ?
   - equalized_odds_difference → ?
   - equal_opportunity_difference → ?
   - disparate_impact_ratio → ?
3. **For BiasAperture's report outputs**, which NIST categories do they address?
   - Model Card → ?
   - FairFace Datasheet → ?
   - SHAP attribution → ?
   - Statistical significance (p-values, CIs) → ?
4. **Crosswalk with EU AI Act Article 10:** show how the two frameworks overlap and complement
5. **Draft NIST compliance statement** for BiasAperture's report template

Reference the actual NIST AI 100-1 document, not summaries.
