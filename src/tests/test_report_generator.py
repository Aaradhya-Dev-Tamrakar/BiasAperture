"""
Unit tests for Report Generator & HTML Compliance Compilation (WP3).
"""

from __future__ import annotations

from pathlib import Path

from bias_aperture.report.generator import HTMLReportGenerator, ReportContext
from bias_aperture.schema import MetricResult
from tests.test_offline_report_contract import _verify_offline_html_contract


def test_html_report_generator_offline_compliance(
    mock_core_four_results: list[MetricResult], tmp_path: Path
) -> None:
    # Add a summary row and a sub-30 row to test all branches
    full_metrics = list(mock_core_four_results) + [
        MetricResult(
            metric_name="demographic_parity_difference",
            subgroup="ALL",
            subgroup_sample_size=300,
            metric_value=0.045,
            ci_lower=0.020,
            ci_upper=0.070,
            p_value=0.002,
            insufficient_sample=False,
        ),
        MetricResult(
            metric_name="equalized_odds_difference",
            subgroup="race=Indian",
            subgroup_sample_size=15,
            metric_value=None,
            ci_lower=None,
            ci_upper=None,
            p_value=None,
            insufficient_sample=True,
        ),
    ]

    context = ReportContext(
        metrics=full_metrics,
        total_subjects=315,
    )

    generator = HTMLReportGenerator()
    html_out = generator.generate(context)

    # 1. Assert offline HTML contract
    violations = _verify_offline_html_contract(html_out)
    assert violations["external_scripts"] == 0
    assert violations["external_links"] == 0
    assert violations["external_images"] == 0
    assert violations["external_fonts"] == 0

    # 2. Check content rendering
    assert "Headline Fairness Metrics" in html_out
    assert "FairFace ResNet-34" in html_out
    assert "Flagged: n &lt; 30 (NFR-003)" in html_out or "n < 30" in html_out

    # 3. Test saving to disk
    out_file = tmp_path / "compliance_report.html"
    saved_path = generator.save(context, out_file)
    assert saved_path.exists()
    assert saved_path.read_text(encoding="utf-8") == html_out
