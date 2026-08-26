"""
Unit tests for fairness statistics engine (WP4).
"""

from __future__ import annotations

import numpy as np
import pytest

from bias_aperture.fairness.statistics import (
    compute_contingency_chi2,
    compute_stratified_bootstrap_ci,
    holm_bonferroni_correction,
)


def test_holm_bonferroni_correction() -> None:
    raw_p = [0.01, 0.04, 0.03, 0.005]
    adj_p = holm_bonferroni_correction(raw_p)

    assert len(adj_p) == len(raw_p)
    # 0.005 is smallest (m=4) -> 0.005 * 4 = 0.02
    # 0.01 is next (m=3) -> max(0.02, 0.01*3) = 0.03
    # 0.03 is next (m=2) -> max(0.03, 0.03*2) = 0.06
    # 0.04 is next (m=1) -> max(0.06, 0.04*1) = 0.06
    assert adj_p[3] == pytest.approx(0.02, abs=1e-4)
    assert adj_p[0] == pytest.approx(0.03, abs=1e-4)
    assert adj_p[2] == pytest.approx(0.06, abs=1e-4)
    assert adj_p[1] == pytest.approx(0.06, abs=1e-4)


def test_contingency_chi2() -> None:
    y_true = np.array([1] * 50 + [0] * 50)
    y_pred = np.array([1] * 40 + [0] * 10 + [1] * 10 + [0] * 40)
    sensitive = np.array(["A"] * 50 + ["B"] * 50)

    chi2, p_val, dof = compute_contingency_chi2(y_true, y_pred, sensitive)
    assert chi2 > 0.0
    assert p_val < 0.05
    assert dof == 1


def test_bootstrap_ci_coverage() -> None:
    # Synthetic group rates
    y_true = np.array([1] * 40 + [0] * 40)
    y_pred = np.array([1] * 35 + [0] * 5 + [1] * 20 + [0] * 20)
    sensitive = np.array(["A"] * 40 + ["B"] * 40)

    def mean_diff(yt: np.ndarray, yp: np.ndarray, s: np.ndarray) -> float:
        rate_a = yp[s == "A"].mean()
        rate_b = yp[s == "B"].mean()
        return abs(float(rate_a - rate_b))

    low, high = compute_stratified_bootstrap_ci(
        y_true, y_pred, sensitive, mean_diff, n_resamples=1000, seed=42
    )

    point_est = mean_diff(y_true, y_pred, sensitive)
    assert 0.0 <= low <= point_est <= high <= 1.0
