import pytest

from bias_aperture.schema import (
    AGE_LABELS,
    GENDER_LABELS,
    MIN_SUBGROUP_SAMPLE_SIZE,
    RACE_LABELS,
    MetricResult,
    SubjectRecord,
)


def test_label_vocabulary_sizes():
    assert len(RACE_LABELS) == 7  # FairFace race_7, locked at M1
    assert len(GENDER_LABELS) == 2
    assert len(AGE_LABELS) == 9


def test_subject_record_construction():
    r = SubjectRecord(
        image_id="img1",
        race="Black",
        gender="Female",
        age="20-29",
        true_label="Female",
        predicted_label="Female",
    )
    assert r.image_id == "img1"


def test_metric_result_valid_row():
    m = MetricResult(
        metric_name="demographic_parity_difference",
        subgroup="race=Black",
        subgroup_sample_size=50,
        metric_value=0.03,
        ci_lower=0.01,
        ci_upper=0.05,
        p_value=0.02,
    )
    assert m.insufficient_sample is False


def test_nfr003_small_sample_without_flag_raises():
    with pytest.raises(ValueError, match="insufficient_sample was not set"):
        MetricResult(
            metric_name="disparate_impact_ratio",
            subgroup="race=Latino_Hispanic",
            subgroup_sample_size=MIN_SUBGROUP_SAMPLE_SIZE - 1,
            metric_value=0.9,
            ci_lower=None,
            ci_upper=None,
            p_value=None,
        )


def test_nfr003_flagged_row_with_metric_value_raises():
    with pytest.raises(ValueError, match="must not carry a computed metric_value"):
        MetricResult(
            metric_name="disparate_impact_ratio",
            subgroup="race=Latino_Hispanic",
            subgroup_sample_size=10,
            metric_value=0.9,
            ci_lower=None,
            ci_upper=None,
            p_value=None,
            insufficient_sample=True,
        )


def test_nfr003_correct_flagged_row():
    m = MetricResult(
        metric_name="disparate_impact_ratio",
        subgroup="race=Latino_Hispanic",
        subgroup_sample_size=10,
        metric_value=None,
        ci_lower=None,
        ci_upper=None,
        p_value=None,
        insufficient_sample=True,
    )
    assert m.insufficient_sample is True
    assert m.metric_value is None


def test_boundary_sample_size_exactly_min_does_not_require_flag():
    # n == MIN_SUBGROUP_SAMPLE_SIZE is NOT below threshold, so no flag needed.
    m = MetricResult(
        metric_name="equal_opportunity_difference",
        subgroup="race=Indian",
        subgroup_sample_size=MIN_SUBGROUP_SAMPLE_SIZE,
        metric_value=0.01,
        ci_lower=-0.01,
        ci_upper=0.03,
        p_value=0.4,
    )
    assert m.insufficient_sample is False
