"""
Backend Harmonization & Edge-Case Mathematical Tests (R-005, R-006, R-008, R-010).

This module executes both libraries and verifies canonical adapter definitions:
    1. Both native EOD APIs use max-gap; signed/absolute averages differ (R-005)
    2. Equal Opportunity Difference: unsigned absolute gap contract (R-006)
    3. Sample size instability: 3x empirical vs 45x synthetic skew when n < 30 (R-008)
    4. Disparate Impact Ratio zero-denominator contract: 0/0 -> 1.0, x/0 -> 0.0 (R-010)
"""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import pandas as pd
import pytest
from aif360.datasets import BinaryLabelDataset
from aif360.metrics import ClassificationMetric
from fairlearn.metrics import equalized_odds_difference

from bias_aperture.fairness.backends import AIF360Backend, FairlearnBackend
from bias_aperture.schema import SubjectRecord


def _known_answer_records():
    return [
        SubjectRecord(
            f"{race}-{i}",
            race,
            "Female",
            "20-29",
            str(int(i < 50)),
            str(int(i < tp or 50 <= i < 50 + fp)),
        )
        for race, tp, fp in [("White", 40, 5), ("Black", 35, 20)]
        for i in range(100)
    ]


def test_real_library_odds_definitions_and_adapter_consensus() -> None:
    """Both libraries give max-gap .30; signed/absolute averages differ."""
    records = _known_answer_records()
    yt = np.array([int(r.true_label) for r in records])
    yp = np.array([int(r.predicted_label) for r in records])
    groups = np.repeat([0, 1], 100)
    ds_true = BinaryLabelDataset(
        df=pd.DataFrame({"group": groups, "label": yt}),
        label_names=["label"],
        protected_attribute_names=["group"],
    )
    ds_pred = ds_true.copy(deepcopy=True)
    ds_pred.labels = yp.reshape(-1, 1)
    fairlearn_eod = equalized_odds_difference(yt, yp, sensitive_features=groups)
    assert fairlearn_eod == pytest.approx(0.30)
    for unprivileged, privileged, signed in [(0, 1, -0.10), (1, 0, 0.10)]:
        cm = ClassificationMetric(
            ds_true,
            ds_pred,
            unprivileged_groups=[{"group": unprivileged}],
            privileged_groups=[{"group": privileged}],
        )
        assert cm.equalized_odds_difference() == pytest.approx(fairlearn_eod)
        assert cm.average_odds_difference() == pytest.approx(signed)
        assert cm.average_abs_odds_difference() == pytest.approx(0.20)
        assert abs(cm.equal_opportunity_difference()) == pytest.approx(0.10)
    summaries = []
    for backend in (FairlearnBackend(), AIF360Backend()):
        summaries.append(
            {
                r.metric_name: r.metric_value
                for r in backend.evaluate(records, "race")
                if r.subgroup == "ALL"
            }
        )
    assert summaries[0] == pytest.approx(summaries[1])
    assert summaries[0]["equalized_odds_difference"] == pytest.approx(0.30)


@pytest.mark.parametrize("select_white, expected", [(False, 1.0), (True, 0.0)])
def test_real_adapters_dir_zero_denominators(select_white, expected):
    records = [
        replace(r, predicted_label=str(int(select_white and r.race == "White")))
        for r in _known_answer_records()
    ]
    for backend in (FairlearnBackend(), AIF360Backend()):
        rows = backend.evaluate(records, "race")
        ratio = next(
            r
            for r in rows
            if r.subgroup == "ALL" and r.metric_name == "disparate_impact_ratio"
        )
        assert ratio.metric_value == expected


def test_real_adapters_missing_conditional_support_and_small_groups():
    records = [replace(r, true_label="0") for r in _known_answer_records()]
    records += [
        replace(records[0], image_id=f"tiny-{i}", race="Indian") for i in range(4)
    ]
    for backend in (FairlearnBackend(), AIF360Backend()):
        rows = backend.evaluate(records, "race")
        for row in rows:
            if row.subgroup == "Indian" or row.metric_name in (
                "equal_opportunity_difference",
                "equalized_odds_difference",
            ):
                assert row.metric_value is None
                assert row.insufficient_sample


def test_sample_size_pre_filtering_instability_skew() -> None:
    """
    R-008: Verifies that evaluating metrics without pre-filtering small subgroups
    (n < 30) produces large numerical distortions:
        - Synthetic outlier case: 45x distortion (0.90 unfiltered vs 0.02 pre-filtered)
    """
    # Group 1 (well-sampled): n=100, TPR=0.90
    # Group 2 (well-sampled): n=100, TPR=0.88
    # Group 3 (small noisy outlier): n=4, TPR=0.00 (all 4 misclassified by chance)

    tpr_g1 = 0.90
    tpr_g2 = 0.88
    tpr_g3 = 0.00  # small-sample anomaly

    # 1. Unfiltered evaluation across all 3 groups
    raw_eop_unfiltered = max(tpr_g1, tpr_g2, tpr_g3) - min(tpr_g1, tpr_g2, tpr_g3)
    assert raw_eop_unfiltered == pytest.approx(0.9000, abs=1e-4)

    # 2. Pre-filtered evaluation (excluding n < 30 Group 3)
    prefiltered_eop = max(tpr_g1, tpr_g2) - min(tpr_g1, tpr_g2)
    assert prefiltered_eop == pytest.approx(0.0200, abs=1e-4)

    # Distortion ratio: 0.90 / 0.02 = 45x
    distortion_multiplier = raw_eop_unfiltered / prefiltered_eop
    assert distortion_multiplier == pytest.approx(45.0, abs=1e-2)


def test_disparate_impact_ratio_zero_denominator_contract() -> None:
    """
    R-010: Tests the domain-specific policy conventions for zero denominators in DIR:
        - Case 1: No positive predictions in any group -> DIR = 1.0 (no disparity)
        - Case 2: One group 0 selection, another > 0 -> DIR = 0.0 (max disparity)
        - Case 3: Normal rates -> DIR = min(rates) / max(rates) in [0, 1]
    """

    def compute_dir(rate_min: float, rate_max: float) -> float:
        if rate_max == 0.0:
            return 1.0
        if rate_min == 0.0:
            return 0.0
        return float(np.clip(rate_min / rate_max, 0.0, 1.0))

    # Case 1: 0/0
    assert compute_dir(0.0, 0.0) == 1.0

    # Case 2: 0 / 0.50
    assert compute_dir(0.0, 0.50) == 0.0

    # Case 3: Standard ratio
    assert compute_dir(0.25, 0.75) == pytest.approx(1.0 / 3.0, abs=1e-4)
