"""
Unit tests for Core Four fairness metrics (WP4).
"""

from __future__ import annotations

import numpy as np
import pytest

from bias_aperture.fairness.metrics import (
    compute_group_rates,
    demographic_parity_difference,
    equal_opportunity_difference,
    equalized_odds_difference,
    symmetric_disparate_impact_ratio,
)


def test_dpd_calculation() -> None:
    rates = {"White": 0.80, "Black": 0.50, "Asian": 0.70}
    val = demographic_parity_difference(rates)
    assert val == pytest.approx(0.30, abs=1e-5)

    with pytest.raises(ValueError, match="at least 2 subgroups"):
        demographic_parity_difference({"White": 0.80})


def test_eod_calculation() -> None:
    tpr = {"White": 0.90, "Black": 0.60}
    fpr = {"White": 0.20, "Black": 0.10}
    # TPR gap = 0.30, FPR gap = 0.10 -> max = 0.30
    val = equalized_odds_difference(tpr, fpr)
    assert val == pytest.approx(0.30, abs=1e-5)


def test_eop_calculation() -> None:
    tpr = {"White": 0.90, "Black": 0.65, "Latino": 0.70}
    val = equal_opportunity_difference(tpr)
    assert val == pytest.approx(0.25, abs=1e-5)


def test_symmetric_dir() -> None:
    rates = {"White": 0.80, "Black": 0.40}
    val, warning = symmetric_disparate_impact_ratio(rates)
    assert val == pytest.approx(0.50, abs=1e-5)
    assert not warning

    # Zero denominator case
    val_zero, warning_zero = symmetric_disparate_impact_ratio(
        {"White": 0.0, "Black": 0.0}
    )
    assert val_zero == 1.0
    assert warning_zero


def test_compute_group_rates() -> None:
    y_true = np.array([1, 1, 0, 0, 1, 0])
    y_pred = np.array([1, 0, 1, 0, 1, 0])
    sensitive = np.array(["A", "A", "A", "B", "B", "B"])

    rates = compute_group_rates(y_true, y_pred, sensitive)
    assert "A" in rates and "B" in rates
    assert rates["A"]["n"] == 3
    assert rates["B"]["n"] == 3
    assert rates["A"]["selection_rate"] == pytest.approx(2 / 3, abs=1e-4)
