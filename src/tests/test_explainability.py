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
    assert (
        "Targeted attribution generated" in exp_sig.details
        or "Targeted SHAP PartitionExplainer attribution generated" in exp_sig.details
    )


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


def test_shap_surrogate_attribution_on_records() -> None:
    from bias_aperture.schema import SubjectRecord

    # Create records with correlation between race=Black and predicted_label="0"
    records = []
    for i in range(50):
        records.append(
            SubjectRecord(
                image_id=f"img_w_{i}",
                race="White",
                gender="Female",
                age="20-29",
                true_label="1",
                predicted_label="1",
            )
        )
        records.append(
            SubjectRecord(
                image_id=f"img_b_{i}",
                race="Black",
                gender="Female",
                age="20-29",
                true_label="1",
                predicted_label="0",
            )
        )

    engine = ShapExplainerEngine()
    res_sig = MetricResult(
        metric_name="demographic_parity_difference",
        subgroup="race=Black",
        subgroup_sample_size=50,
        metric_value=1.0,
        ci_lower=0.9,
        ci_upper=1.0,
        p_value=0.001,
        insufficient_sample=False,
    )

    exp = engine.explain_disparity(res_sig, records=records)
    assert "Surrogate Shapley attribution computed" in exp.details
    assert len(exp.feature_attributions) > 0
    # Race features should have strong attribution
    race_attrs = [k for k in exp.feature_attributions if "race" in k]
    assert len(race_attrs) > 0
