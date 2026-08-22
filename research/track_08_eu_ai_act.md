# Track 08 — EU AI Act Article 10 Regulatory Mapping
**Stream:** B (Report Generation) · **Priority:** 🔴 Critical · **Owner Focus:** Both
**Estimated Time:** 45 min · **Feeds:** Report regulatory mapping section

## Instructions
1. Paste `CONTEXT.md` into Claude Desktop first
2. Then paste the prompt below
3. Save the output as `results/08_regulatory_mapping.md`

## Prompt

Research EU AI Act (Regulation (EU) 2024/1689) Article 10 in full text. For each sub-clause (10(1) through 10(6)), document:
1. The exact legal text of the sub-clause
2. What technical requirement it imposes on a high-risk AI system
3. Which of BiasAperture's 4 metrics maps to it: demographic_parity_difference, equalized_odds_difference, equal_opportunity_difference, disparate_impact_ratio
4. What evidence BiasAperture's report must show to demonstrate compliance
5. How the mapping relates to Annex IV (technical documentation requirements)

Also map to NIST AI RMF (NIST AI 100-1, Jan 2023) categories: which of Govern/Map/Measure/Manage does each metric address?

Also research Buscemi et al. 2025 "Assessing High-Risk AI Systems under the EU AI Act" for their legal-to-technical decomposition methodology and how BiasAperture can cite it.
