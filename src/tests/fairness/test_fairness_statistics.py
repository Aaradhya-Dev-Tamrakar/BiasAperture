"""
Unit tests for fairness statistics engine (WP4).
"""

from __future__ import annotations

import numpy as np
import pytest

from bias_aperture.fairness.statistics import (
    adjust_family_pvalues,
    compute_contingency_chi2,
    compute_metric_specific_test,
    compute_stratified_bootstrap_ci,
    compute_subgroup_bootstrap_ci,
    holm_bonferroni_correction,
)
from bias_aperture.schema import MetricResult


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


def test_metric_specific_hypothesis_tests() -> None:
    # Construct scenario where selection rates are equal (50% for A and B)
    # but TPR diverges sharply (Group A: TPR=80%, Group B: TPR=20%)
    # Group A: 50 records. 25 Y=1 (20 pred=1 -> TPR=0.8), 25 Y=0 (5 pred=1)
    # Group B: 50 records. 25 Y=1 (5 pred=1 -> TPR=0.2), 25 Y=0 (20 pred=1)
    y_true_a = [1] * 25 + [0] * 25
    y_pred_a = [1] * 20 + [0] * 5 + [1] * 5 + [0] * 20
    sens_a = ["A"] * 50

    y_true_b = [1] * 25 + [0] * 25
    y_pred_b = [1] * 5 + [0] * 20 + [1] * 20 + [0] * 5
    sens_b = ["B"] * 50

    yt = np.array(y_true_a + y_true_b)
    yp = np.array(y_pred_a + y_pred_b)
    s = np.array(sens_a + sens_b)

    # 1. DPD test: selection rates are identical (25/50 vs 25/50), so p=1.0
    dpd_res = compute_metric_specific_test("demographic_parity_difference", yt, yp, s)
    assert dpd_res.hypothesis_family == "selection_rate"
    assert dpd_res.raw_p == pytest.approx(1.0, abs=1e-2)

    # 2. EOP test: TPR is conditioned on Y=1 (20/25 vs 5/25), so p < 0.001
    eop_res = compute_metric_specific_test("equal_opportunity_difference", yt, yp, s)
    assert eop_res.hypothesis_family == "conditional_odds"
    assert eop_res.raw_p < 0.001

    # 3. EOD test: joint TPR and FPR evaluation, also significant
    eod_res = compute_metric_specific_test("equalized_odds_difference", yt, yp, s)
    assert eod_res.hypothesis_family == "conditional_odds"
    assert eod_res.raw_p < 0.01


def test_subgroup_bootstrap_ci_not_heuristic() -> None:
    y_true = np.array([1] * 50 + [0] * 50)
    y_pred = np.array([1] * 40 + [0] * 10 + [1] * 10 + [0] * 40)
    sensitive = np.array(["GroupA"] * 50 + ["GroupB"] * 50)

    ci_low, ci_high = compute_subgroup_bootstrap_ci(
        y_true,
        y_pred,
        sensitive,
        "GroupA",
        "demographic_parity_difference",
        n_resamples=200,
    )

    assert ci_low is not None and ci_high is not None
    assert 0.0 <= ci_low <= ci_high <= 1.0
    # Must NOT be the fake ±0.05 heuristic
    point_est = abs(float(y_pred[sensitive == "GroupA"].mean()) - float(y_pred.mean()))
    assert ci_low != pytest.approx(
        point_est - 0.05, abs=1e-5
    ) or ci_high != pytest.approx(point_est + 0.05, abs=1e-5)


def test_bca_large_n_block_jackknife_branch() -> None:
    # Dataset with N=400 (triggers n > 300 delete-d block jackknife)
    rng = np.random.default_rng(42)
    n = 400
    sensitive = np.array(["A"] * 200 + ["B"] * 200)
    y_true = rng.choice([0, 1], size=n, p=[0.5, 0.5])
    y_pred = rng.choice([0, 1], size=n, p=[0.4, 0.6])

    def simple_dpd(yt: np.ndarray, yp: np.ndarray, s: np.ndarray) -> float:
        return abs(float(yp[s == "A"].mean() - yp[s == "B"].mean()))

    ci_low, ci_high = compute_stratified_bootstrap_ci(
        y_true, y_pred, sensitive, simple_dpd, n_resamples=1000, seed=42
    )

    assert 0.0 <= ci_low <= ci_high <= 1.0


def test_adjust_family_pvalues_wiring() -> None:
    results = [
        MetricResult(
            metric_name="demographic_parity_difference",
            subgroup="ALL",
            subgroup_sample_size=100,
            metric_value=0.2,
            ci_lower=0.1,
            ci_upper=0.3,
            p_value=0.01,
            raw_p_value=0.01,
            hypothesis_family="selection_rate",
        ),
        MetricResult(
            metric_name="disparate_impact_ratio",
            subgroup="ALL",
            subgroup_sample_size=100,
            metric_value=0.8,
            ci_lower=0.7,
            ci_upper=0.9,
            p_value=0.04,
            raw_p_value=0.04,
            hypothesis_family="selection_rate",
        ),
    ]

    adjusted = adjust_family_pvalues(results)
    assert len(adjusted) == 2
    # In selection_rate family with m=2:
    # 0.01 * 2 = 0.02
    # 0.04 * 1 = 0.04
    assert adjusted[0].adjusted_p_value == pytest.approx(0.02, abs=1e-4)
    assert adjusted[1].adjusted_p_value == pytest.approx(0.04, abs=1e-4)
    assert adjusted[0].adjustment_method == "holm_bonferroni"
    assert adjusted[0].p_value == adjusted[0].adjusted_p_value
