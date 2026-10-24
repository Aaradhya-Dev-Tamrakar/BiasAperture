"""Tests for gated spatial attribution and offline visualization."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from bias_aperture.explainability import (
    SpatialShapEngine,
    classify_ita,
    compute_ita,
    render_spatial_svg,
)
from bias_aperture.schema import MetricResult, SubjectRecord


def _metric(value: float) -> MetricResult:
    return MetricResult(
        metric_name="demographic_parity_difference",
        subgroup="race=Black",
        subgroup_sample_size=40,
        metric_value=value,
        ci_lower=value - 0.02,
        ci_upper=value + 0.02,
        p_value=0.01,
    )


def _records() -> list[SubjectRecord]:
    return [
        SubjectRecord(
            image_id=f"image-{index}",
            race="Black" if index % 2 else "White",
            gender="Female",
            age="20-29",
            true_label="1",
            predicted_label=str(index % 2),
        )
        for index in range(40)
    ]


def test_compute_ita_accepts_rgb_patch_and_classifies() -> None:
    patch = np.full((4, 4, 3), [180, 120, 80], dtype=np.uint8)
    ita = compute_ita(patch)

    assert ita == pytest.approx(-10.5, abs=2.0)
    assert classify_ita(ita) == "Brown"


def test_spatial_shap_gating_skips_unflagged_disparity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = SpatialShapEngine()
    called = False

    def fail_if_called(*args: object, **kwargs: object) -> None:
        nonlocal called
        called = True

    monkeypatch.setattr(engine, "_run_spatial_shap", fail_if_called)
    result = engine.explain_disparity(
        _metric(0.02),
        image_paths=[Path("missing.jpg")],
        records=_records(),
    )

    assert called is False
    assert "below spatial SHAP threshold" in result.details
    assert result.feature_attributions


def test_spatial_shap_falls_back_when_image_is_unavailable() -> None:
    result = SpatialShapEngine().explain_disparity(
        _metric(0.3),
        image_paths=[Path("missing.jpg")],
        records=_records(),
    )

    assert result.proxy_warning is True
    assert result.feature_attributions
    assert "Spatial SHAP unavailable" in result.details


def test_render_spatial_svg_is_self_contained() -> None:
    svg = render_spatial_svg(np.array([[0.2, -0.4], [0.0, 0.1]]), 42.0)

    assert svg.startswith("<svg")
    assert 'xmlns="http://www.w3.org/2000/svg"' in svg
    assert "ITA 42.0 deg (Light)" in svg
    assert "http://" not in svg.replace("http://www.w3.org/2000/svg", "")
    assert "<script" not in svg
