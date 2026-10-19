"""Tests for the plain-language explainability and narrative engine (WP3)."""

from __future__ import annotations

from bias_aperture.explainability import ExplanationResult
from bias_aperture.report.generator import ReportContext
from bias_aperture.report.narrative import (
    METRIC_GLOSSARY,
    PlainLanguageSummary,
    _humanize_feature_name,
    synthesize_plain_language_narrative,
)
from bias_aperture.schema import MetricResult


def test_humanize_feature_name() -> None:
    assert _humanize_feature_name("race_Black") == "Race (Black)"
    assert _humanize_feature_name("age_20-29") == "Age (20-29)"
    assert _humanize_feature_name("gender_Female") == "Gender (Female)"
    assert _humanize_feature_name("singleword") == "Singleword"


def test_metric_glossary_integrity() -> None:
    core_four = [
        "disparate_impact_ratio",
        "demographic_parity_difference",
        "equalized_odds_difference",
        "equal_opportunity_difference",
    ]
    for m in core_four:
        assert m in METRIC_GLOSSARY
        entry = METRIC_GLOSSARY[m]
        assert "title" in entry
        assert "plain_name" in entry
        assert "plain_question" in entry
        assert "analogy" in entry
        assert "target" in entry
        assert "regulatory" in entry


def test_synthesize_narrative_fail_severe_disparity() -> None:
    context = ReportContext(
        metrics=[
            MetricResult(
                metric_name="disparate_impact_ratio",
                subgroup="race=Black",
                subgroup_sample_size=120,
                metric_value=0.720,
                ci_lower=0.680,
                ci_upper=0.760,
                p_value=0.001,
                insufficient_sample=False,
            )
        ],
        model_name="FairFace ResNet-34",
        protected_axis="race",
        total_subjects=500,
    )
    exec_summary = {
        "flagged_significant_count": 2,
        "valid_subgroups": 4,
        "insufficient_count": 1,
        "worst_group_label": "race=Black",
        "worst_metric_label": "DIR",
        "worst_metric_value": 0.720,
        "worst_is_overall": False,
    }

    summary: PlainLanguageSummary = synthesize_plain_language_narrative(
        context, exec_summary
    )

    assert summary.verdict_badge == "FAIL"
    assert summary.verdict_badge_class == "badge-fail"
    assert "Demographic Disparity Flagged" in summary.verdict_title
    assert "72.0%" in summary.worst_offender_narrative
    assert "80% legal threshold" in summary.worst_offender_narrative
    assert "marked 'N/A' (Suppressed)" in summary.sample_guard_narrative
    assert summary.has_disparities is True


def test_synthesize_narrative_warn_minor_disparity() -> None:
    context = ReportContext(
        metrics=[],
        model_name="FairFace ResNet-34",
        protected_axis="gender",
        total_subjects=600,
    )
    exec_summary = {
        "flagged_significant_count": 1,
        "valid_subgroups": 6,
        "insufficient_count": 0,
        "worst_group_label": "gender=Female",
        "worst_metric_label": "DIR",
        "worst_metric_value": 0.850,
        "worst_is_overall": False,
    }

    summary: PlainLanguageSummary = synthesize_plain_language_narrative(
        context, exec_summary
    )

    assert summary.verdict_badge == "WARN"
    assert summary.verdict_badge_class == "badge-warn"
    assert "Marginal Disparity Observed" in summary.verdict_title
    assert "within the 80% guideline" in summary.worst_offender_narrative
    assert (
        "All evaluated demographic cohorts met or exceeded"
        in summary.sample_guard_narrative
    )


def test_synthesize_narrative_pass_no_disparities() -> None:
    context = ReportContext(
        metrics=[],
        model_name="FairFace ResNet-34",
        protected_axis="race",
        total_subjects=1000,
    )
    exec_summary = {
        "flagged_significant_count": 0,
        "valid_subgroups": 5,
        "insufficient_count": 0,
        "worst_group_label": None,
        "worst_metric_label": None,
        "worst_metric_value": None,
        "worst_is_overall": False,
    }

    summary: PlainLanguageSummary = synthesize_plain_language_narrative(
        context, exec_summary
    )

    assert summary.verdict_badge == "PASS"
    assert summary.verdict_badge_class == "badge-pass"
    assert "Within Defined Fairness Tolerances" in summary.verdict_title
    assert (
        "no statistically significant demographic performance disparities"
        in summary.verdict_narrative
    )
    assert summary.has_disparities is False


def test_synthesize_narrative_with_surrogate_attributions() -> None:
    exp = ExplanationResult(
        subgroup="race=Black",
        metric_name="disparate_impact_ratio",
        feature_attributions={
            "age_20-29": 0.185,
            "gender_Female": 0.142,
            "race_White": 0.055,
        },
    )
    context = ReportContext(
        metrics=[],
        model_name="FairFace ResNet-34",
        protected_axis="race",
        total_subjects=800,
        explanations=[exp],
    )
    exec_summary = {
        "flagged_significant_count": 1,
        "valid_subgroups": 4,
        "insufficient_count": 0,
        "worst_group_label": "race=Black",
        "worst_metric_label": "DPD",
        "worst_metric_value": 0.120,
        "worst_is_overall": False,
    }

    summary: PlainLanguageSummary = synthesize_plain_language_narrative(
        context, exec_summary
    )

    assert summary.has_attributions is True
    assert "surrogate Shapley attribution" in summary.surrogate_drivers_narrative
    assert "Age (20-29)" in summary.surrogate_drivers_narrative
    assert "Gender (Female)" in summary.surrogate_drivers_narrative
    assert len(summary.top_proxy_factors) == 3
