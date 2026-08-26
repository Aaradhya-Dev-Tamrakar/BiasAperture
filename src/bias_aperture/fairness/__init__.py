"""Fairness computation engine package (WP4 / Stream C).

Exports:
- Core Four calculators: ``demographic_parity_difference``,
  ``equalized_odds_difference``, ``equal_opportunity_difference``,
  ``symmetric_disparate_impact_ratio``, ``compute_group_rates``
- Backend interfaces: ``FairnessBackend``, ``FairlearnBackend``, ``AIF360Backend``
- Cross-validation: ``CrossValidationOrchestrator``, ``DivergenceAlert``
- Statistical engine: ``compute_contingency_chi2``,
  ``compute_stratified_bootstrap_ci``, ``holm_bonferroni_correction``
- Screening & sample guards: ``screen_subgroups``, ``screen_numeric_groups``,
  ``eligible_groups``
"""

from __future__ import annotations

from bias_aperture.fairness.backends import (
    AIF360Backend,
    CrossValidationOrchestrator,
    DivergenceAlert,
    FairlearnBackend,
)
from bias_aperture.fairness.base import (
    EligibilityReport,
    FairnessBackend,
    eligible_groups,
    screen_numeric_groups,
    screen_subgroups,
)
from bias_aperture.fairness.metrics import (
    compute_group_rates,
    demographic_parity_difference,
    equal_opportunity_difference,
    equalized_odds_difference,
    symmetric_disparate_impact_ratio,
)
from bias_aperture.fairness.statistics import (
    compute_contingency_chi2,
    compute_stratified_bootstrap_ci,
    holm_bonferroni_correction,
)

__all__ = [
    "AIF360Backend",
    "CrossValidationOrchestrator",
    "DivergenceAlert",
    "EligibilityReport",
    "FairlearnBackend",
    "FairnessBackend",
    "compute_contingency_chi2",
    "compute_group_rates",
    "compute_stratified_bootstrap_ci",
    "demographic_parity_difference",
    "eligible_groups",
    "equal_opportunity_difference",
    "equalized_odds_difference",
    "holm_bonferroni_correction",
    "screen_numeric_groups",
    "screen_subgroups",
    "symmetric_disparate_impact_ratio",
]
