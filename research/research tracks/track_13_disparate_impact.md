# Track 13 — Disparate Impact Ratio — Implementation & Legal Context
**Stream:** C (Fairness Engine) · **Priority:** 🟡 Medium · **Owner Focus:** Tisha (WP4)
**Estimated Time:** 30 min · **Feeds:** Metric implementation, report phrasing

## Instructions
1. Paste `CONTEXT.md` into Claude Desktop first
2. Then paste the prompt below
3. Save the output as `results/13_disparate_impact_ratio.md`

## Prompt

Research the Disparate Impact Ratio (DIR) metric in depth, covering both implementation and legal context:

**Implementation:**
1. Formula: min(selection_rate_a / selection_rate_b, selection_rate_b / selection_rate_a) — or is it always unprivileged/privileged?
2. How to define "privileged" vs "unprivileged" group when there are 7 race groups (not binary)
3. Pairwise DIR (every pair of groups) vs. min-group-vs-max-group — which approach?
4. Edge cases: selection_rate = 0, selection_rate = 1, denominator = 0

**Legal context:**
1. The four-fifths rule (80% threshold) — EEOC origin and why Watkins et al. 2022 critique it
2. BiasAperture's approach: always pair DIR with chi-squared + bootstrap CI, never use bare ratio as pass/fail
3. How to report DIR in a regulatory-compliant way that avoids the "epistemic trespassing" Watkins warns about

Provide a complete Python implementation and a recommended report phrasing template.
