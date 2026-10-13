"""
Unit tests for SHAP Explainability reporting integration (Issue #24).
Verifies that targeted surrogate Shapley attributions are rendered into the HTML report
while strictly maintaining the offline contract (zero CDNs/external scripts).
"""

from __future__ import annotations

from pathlib import Path

from bias_aperture.explainability import ExplanationResult
from bias_aperture.report.generator import HTMLReportGenerator, ReportContext
from bias_aperture.schema import MetricResult
from tests.test_offline_report_contract import _verify_offline_html_contract


def test_html_report_with_shap_attributions(
    mock_core_four_results: list[MetricResult], tmp_path: Path
) -> None:
    # 1. Prepare sample metrics and attributions
    attributions = [
        ExplanationResult(
            metric_name="demographic_parity_difference",
            subgroup="race=Black",
            feature_attributions={
                "race_Black": 0.285,
                "gender_Female": 0.042,
                "age_20-29": 0.015,
            },
            details=(
                "Surrogate Shapley attribution computed using decision tree surrogate."
            ),
        ),
        ExplanationResult(
            metric_name="equalized_odds_difference",
            subgroup="gender=Female",
            feature_attributions={
                "gender_Female": 0.190,
                "race_White": 0.033,
            },
            details="Surrogate Shapley attribution computed.",
        ),
    ]

    context = ReportContext(
        metrics=mock_core_four_results,
        total_subjects=200,
        attributions=attributions,
    )

    generator = HTMLReportGenerator()
    html_out = generator.generate(context)

    # 2. Strict Offline Contract Verification
    violations = _verify_offline_html_contract(html_out)
    assert violations["external_scripts"] == 0
    assert violations["external_links"] == 0
    assert violations["external_images"] == 0
    assert violations["external_fonts"] == 0

    # 3. Content Assertions
    assert "3. Targeted Disparity Explainability &amp; Proxy Attributions" in html_out
    assert "Non-Causal Disclaimer" in html_out
    assert "Bilodeau et al." in html_out
    assert "race_Black" in html_out
    assert "0.285" in html_out
    assert "gender_Female" in html_out
    assert '<svg class="inline-chart"' in html_out

    # 4. Save test
    out_file = tmp_path / "report_with_shap.html"
    saved = generator.save(context, out_file)
    assert saved.exists()
    assert "Targeted Disparity Explainability" in saved.read_text(encoding="utf-8")


def test_html_report_without_shap_attributions(
    mock_core_four_results: list[MetricResult],
) -> None:
    context = ReportContext(
        metrics=mock_core_four_results,
        total_subjects=200,
        attributions=[],
    )

    generator = HTMLReportGenerator()
    html_out = generator.generate(context)

    # When no attributions exist, section 3 should not be rendered
    assert "Targeted Disparity Explainability" not in html_out
    # Governance section remains present
    assert "Governance Documentation &amp; Intended Use" in html_out
