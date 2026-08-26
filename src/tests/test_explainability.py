"""
Unit tests for Explainability & ITA calculations (WP4/WP5).
"""

from __future__ import annotations

import pytest

from bias_aperture.explainability import ShapExplainerEngine, compute_ita
from bias_aperture.schema import MetricResult


def test_compute_ita() -> None:
    # L*=50 -> ITA = 0 degrees
    assert compute_ita(50.0, 10.0) == pytest.approx(0.0, abs=1e-4)

    # L*=60, b*=10 -> arctan(1) = 45 degrees
    assert compute_ita(60.0, 10.0) == pytest.approx(45.0, abs=1e-4)


def test_shap_explainer_selective_triggering() -> None:
    engine = ShapExplainerEngine()

    # Case 1: Significant disparity (p < 0.05, n >= 30) -> Should explain
    res_sig = MetricResult(
        metric_name="demographic_parity_difference",
        subgroup="race=Black",
        subgroup_sample_size=100,
        metric_value=0.25,
        ci_lower=0.20,
        ci_upper=0.30,
        p_value=0.01,
        insufficient_sample=False,
    )
    assert engine.should_explain(res_sig) is True
    exp_sig = engine.explain_disparity(res_sig)
    assert "Targeted attribution generated" in exp_sig.details

    # Case 2: Non-significant disparity (p >= 0.05) -> Skip
    res_nonsig = MetricResult(
        metric_name="demographic_parity_difference",
        subgroup="race=White",
        subgroup_sample_size=100,
        metric_value=0.02,
        ci_lower=0.0,
        ci_upper=0.05,
        p_value=0.45,
        insufficient_sample=False,
    )
    assert engine.should_explain(res_nonsig) is False
    exp_nonsig = engine.explain_disparity(res_nonsig)
    assert "skipped" in exp_nonsig.details

    # Case 3: Insufficient sample (n < 30) -> Skip
    res_small = MetricResult(
        metric_name="demographic_parity_difference",
        subgroup="race=Indian",
        subgroup_sample_size=10,
        metric_value=None,
        ci_lower=None,
        ci_upper=None,
        p_value=None,
        insufficient_sample=True,
    )
    assert engine.should_explain(res_small) is False
