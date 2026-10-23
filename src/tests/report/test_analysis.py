"""Unit tests for report analysis functions: threshold breach,
3-state classification, and cohort resolution.
"""

from __future__ import annotations

from bias_aperture.report.analysis import (
    _build_executive_summary,
    _build_subgroup_matrix,
    is_threshold_breach,
)
from bias_aperture.schema import MetricResult


def test_is_threshold_breach() -> None:
    # DIR breaches when < 0.80
    assert is_threshold_breach("disparate_impact_ratio", 0.79) is True
    assert is_threshold_breach("disparate_impact_ratio", 0.80) is False
    assert is_threshold_breach("disparate_impact_ratio", 0.95) is False

    # Differences breach when > 0.10
    assert is_threshold_breach("demographic_parity_difference", 0.11) is True
    assert is_threshold_breach("demographic_parity_difference", 0.10) is False
    assert is_threshold_breach("demographic_parity_difference", 0.05) is False

    assert is_threshold_breach("equalized_odds_difference", 0.15) is True
    assert is_threshold_breach("equalized_odds_difference", 0.053) is False

    assert is_threshold_breach("equal_opportunity_difference", 0.12) is True
    assert is_threshold_breach("equal_opportunity_difference", 0.000) is False

    # None value safety
    assert is_threshold_breach("disparate_impact_ratio", None) is False


def test_subgroup_matrix_3state_status() -> None:
    metrics = [
        # Subgroup A: Large breach, significant (FAIL)
        MetricResult(
            metric_name="demographic_parity_difference",
            subgroup="GroupA",
            subgroup_sample_size=200,
            metric_value=0.15,
            ci_lower=0.12,
            ci_upper=0.18,
            p_value=0.001,
            insufficient_sample=False,
        ),
        # Subgroup B: Small gap, significant (WARN)
        MetricResult(
            metric_name="demographic_parity_difference",
            subgroup="GroupB",
            subgroup_sample_size=200,
            metric_value=0.03,
            ci_lower=0.01,
            ci_upper=0.05,
            p_value=0.01,
            insufficient_sample=False,
        ),
        # Subgroup C: Small gap, not significant (PASS)
        MetricResult(
            metric_name="demographic_parity_difference",
            subgroup="GroupC",
            subgroup_sample_size=200,
            metric_value=0.02,
            ci_lower=-0.01,
            ci_upper=0.04,
            p_value=0.35,
            insufficient_sample=False,
        ),
    ]

    matrix = _build_subgroup_matrix(metrics)

    bars_a = matrix["GroupA"]["metric_bars"]
    assert bars_a[0]["status"] == "FAIL"
    assert bars_a[0]["breached"] is True

    bars_b = matrix["GroupB"]["metric_bars"]
    assert bars_b[0]["status"] == "WARN"
    assert bars_b[0]["breached"] is False

    bars_c = matrix["GroupC"]["metric_bars"]
    assert bars_c[0]["status"] == "PASS"
    assert bars_c[0]["breached"] is False


def test_worst_group_resolution_resolves_to_actual_subgroup() -> None:
    metrics = [
        MetricResult(
            metric_name="disparate_impact_ratio",
            subgroup="Middle Eastern",
            subgroup_sample_size=500,
            metric_value=0.784,
            ci_lower=0.740,
            ci_upper=0.820,
            p_value=0.0001,
            insufficient_sample=False,
        ),
        MetricResult(
            metric_name="disparate_impact_ratio",
            subgroup="Southeast Asian",
            subgroup_sample_size=600,
            metric_value=0.975,
            ci_lower=0.940,
            ci_upper=1.010,
            p_value=0.0001,
            insufficient_sample=False,
        ),
    ]
    summary_metrics = [
        MetricResult(
            metric_name="disparate_impact_ratio",
            subgroup="ALL",
            subgroup_sample_size=1100,
            metric_value=0.713,
            ci_lower=0.680,
            ci_upper=0.745,
            p_value=0.00001,
            insufficient_sample=False,
        ),
    ]

    groups = _build_subgroup_matrix(metrics)
    valid_groups = list(groups.values())

    exec_summary = _build_executive_summary(
        groups=groups,
        valid_groups=valid_groups,
        insufficient_groups=[],
        summary_metrics=summary_metrics,
    )

    # Worst group must NOT be "Overall (Table 1)"
    assert exec_summary["worst_group_label"] == "Middle Eastern"
    # But headline metric should still reflect Table 1
    assert exec_summary["headline_metric_label"] == "DIR"
    assert exec_summary["headline_metric_value"] == 0.713
    assert exec_summary["worst_is_overall"] is True
