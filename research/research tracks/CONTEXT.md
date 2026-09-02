# BiasAperture — System Context (paste this first)

You are researching for **BiasAperture**, a demographic bias auditing platform for computer vision models. Key facts:

## Project Scope

- **Diagnostic only**: detects and reports bias. Does NOT retrain, debias, or generate synthetic data.
- **Benchmark**: FairFace dataset (108,501 images, 7 race groups, 2 gender, 9 age bins)
- **Classifier**: ResNet-34 pretrained on FairFace (dchen236/FairFace, race_7 variant)
- **Regulatory**: EU AI Act Article 10 + NIST AI RMF (AI 100-1)

## Phase-2 Research

The original capstone sprint covers Tracks 01–20. The separate Phase-2 Product
Upgrade Sprint covers Tracks 21–38; use `PHASE2_CONTEXT.md` and
`PHASE2_RUNNER_GUIDE.md` for its additive rules, dependencies, and status. The
merged findings are in `../results/synth_phase2.md`. Track 22 is parked and
Track 23 is dropped; 16 tracks are currently available to claim.

## Core Four Disparity Metrics

1. `demographic_parity_difference`
2. `equalized_odds_difference`
3. `equal_opportunity_difference`
4. `disparate_impact_ratio`

## Locked Schema (DO NOT modify)

- **Race Labels (7)**: White, Black, Latino_Hispanic, East Asian, Southeast Asian, Indian, Middle Eastern
- **Gender Labels (2)**: Male, Female
- **Age Labels (9)**: 0-2, 3-9, 10-19, 20-29, 30-39, 40-49, 50-59, 60-69, 70+

## Statistical Requirements

- Chi-squared significance test (α = 0.05, exact p-values)
- Bootstrap 95% CI (≥ 1,000 resamples)
- Minimum subgroup size: n ≥ 30 (below → flag "insufficient sample", never compute)

## Dual-Backend Architecture

- Fairlearn AND AIF360 compute the same metrics independently
- Divergences between backends are flagged in the report
- Strategy pattern: `FairnessBackend` ABC with `FairlearnBackend` and `AIF360Backend`

## Output Schema (MetricResult dataclass)

- metric_name, subgroup, subgroup_sample_size, metric_value, ci_lower, ci_upper, p_value, insufficient_sample

## Tech Stack

- Python ≥ 3.10, pandas, numpy, scipy, Fairlearn, AIF360, SHAP
- Jinja2 for HTML reports
- pytest for testing, ruff for linting (88-char lines)
