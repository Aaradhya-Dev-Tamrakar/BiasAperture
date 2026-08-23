# Track 18 — Pytest Testing Patterns for Fairness Metrics
**Stream:** E (Testing) · **Priority:** 🟡 Medium · **Owner Focus:** Both
**Estimated Time:** 30 min · **Feeds:** `src/tests/` test suite

## Instructions
1. Paste `CONTEXT.md` into Claude Desktop first
2. Then paste the prompt below
3. Save the output as `results/18_pytest_patterns.md`

## Prompt

Design a comprehensive pytest test suite for a fairness metrics engine. The engine computes 4 metrics (demographic_parity_difference, equalized_odds_difference, equal_opportunity_difference, disparate_impact_ratio) across 7 race groups.

Design tests for:
1. **Known-answer tests:** hand-computed expected values for small synthetic datasets
2. **Edge cases:** empty subgroups, single-element subgroups, all-correct predictions, all-wrong predictions
3. **NFR-003 guard:** verify that n < 30 → insufficient_sample=True, metric_value=None
4. **Statistical properties:** bootstrap CI contains the point estimate, CI width decreases with n
5. **Cross-validation:** Fairlearn and AIF360 produce the same results (within tolerance) on identical input
6. **Parametrized fixtures:** test all 4 metrics × 7 subgroups × 2 backends systematically
7. **Property-based testing:** using Hypothesis library to generate random demographic datasets

Existing fixtures in conftest.py provide: `sample_subject_records` (7 SubjectRecord instances across all race groups) and `mock_core_four_results` (4 MetricResult instances for race=Black).

Provide complete pytest code examples with clear docstrings.
