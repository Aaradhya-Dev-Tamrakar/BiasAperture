"""Shared test fixtures for BiasAperture test suite."""

import pytest

from bias_aperture.schema import MetricResult, SubjectRecord


@pytest.fixture
def sample_subject_records() -> list[SubjectRecord]:
    """Provide a diverse list of SubjectRecords across race and gender categories."""
    return [
        SubjectRecord(
            image_id="val/1.jpg",
            race="Black",
            gender="Female",
            age="20-29",
            true_label="Female",
            predicted_label="Female",
        ),
        SubjectRecord(
            image_id="val/2.jpg",
            race="White",
            gender="Male",
            age="30-39",
            true_label="Male",
            predicted_label="Male",
        ),
        SubjectRecord(
            image_id="val/3.jpg",
            race="Indian",
            gender="Male",
            age="40-49",
            true_label="Male",
            predicted_label="Male",
        ),
        SubjectRecord(
            image_id="val/4.jpg",
            race="East Asian",
            gender="Female",
            age="10-19",
            true_label="Female",
            predicted_label="Male",
        ),
        SubjectRecord(
            image_id="val/5.jpg",
            race="Latino_Hispanic",
            gender="Female",
            age="50-59",
            true_label="Female",
            predicted_label="Female",
        ),
        SubjectRecord(
            image_id="val/6.jpg",
            race="Middle Eastern",
            gender="Male",
            age="20-29",
            true_label="Male",
            predicted_label="Male",
        ),
        SubjectRecord(
            image_id="val/7.jpg",
            race="Southeast Asian",
            gender="Female",
            age="30-39",
            true_label="Female",
            predicted_label="Female",
        ),
    ]


@pytest.fixture
def mock_core_four_results() -> list[MetricResult]:
    """Provide a valid mock dictionary of Core Four MetricResults."""
    return [
        MetricResult(
            metric_name="demographic_parity_difference",
            subgroup="race=Black",
            subgroup_sample_size=150,
            metric_value=0.042,
            ci_lower=0.015,
            ci_upper=0.071,
            p_value=0.008,
            insufficient_sample=False,
        ),
        MetricResult(
            metric_name="equalized_odds_difference",
            subgroup="race=Black",
            subgroup_sample_size=150,
            metric_value=0.038,
            ci_lower=0.011,
            ci_upper=0.065,
            p_value=0.012,
            insufficient_sample=False,
        ),
        MetricResult(
            metric_name="equal_opportunity_difference",
            subgroup="race=Black",
            subgroup_sample_size=150,
            metric_value=0.029,
            ci_lower=0.005,
            ci_upper=0.054,
            p_value=0.031,
            insufficient_sample=False,
        ),
        MetricResult(
            metric_name="disparate_impact_ratio",
            subgroup="race=Black",
            subgroup_sample_size=150,
            metric_value=0.892,
            ci_lower=0.821,
            ci_upper=0.963,
            p_value=0.004,
            insufficient_sample=False,
        ),
    ]
