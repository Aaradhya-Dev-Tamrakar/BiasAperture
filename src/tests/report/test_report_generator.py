"""
Unit tests for Report Generator & HTML Compliance Compilation (WP3).
"""

from __future__ import annotations

from pathlib import Path

from bias_aperture.report.generator import HTMLReportGenerator, ReportContext
from bias_aperture.schema import MetricResult
from tests.report.test_offline_report_contract import _verify_offline_html_contract


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
    assert "Executive Translation • Non-Technical Review" in html_out
    assert "Disparity Impact" in html_out
    assert "How to Read These Metrics (In Plain English)" in html_out
    assert "Disparate Impact Ratio (DIR)" in html_out

    # 3. Test saving to disk
    out_file = tmp_path / "compliance_report.html"
    saved_path = generator.save(context, out_file)
    assert saved_path.exists()
    assert saved_path.read_text(encoding="utf-8") == html_out


def test_executive_summary_card3_sources_from_summary_metrics(
    mock_core_four_results: list[MetricResult],
) -> None:
    # Summary metrics with overall DPD = 0.053, EOD = 0.244
    full_metrics = list(mock_core_four_results) + [
        MetricResult(
            metric_name="demographic_parity_difference",
            subgroup="ALL",
            subgroup_sample_size=1000,
            metric_value=0.053,
            ci_lower=0.030,
            ci_upper=0.075,
            p_value=0.001,
            insufficient_sample=False,
        ),
        MetricResult(
            metric_name="equalized_odds_difference",
            subgroup="ALL",
            subgroup_sample_size=1000,
            metric_value=0.244,
            ci_lower=0.210,
            ci_upper=0.280,
            p_value=0.0001,
            insufficient_sample=False,
        ),
    ]

    context = ReportContext(metrics=full_metrics, total_subjects=1000)
    generator = HTMLReportGenerator()
    html_out = generator.generate(context)

    # Executive Summary Card 3 must display EOD = 0.244 as worst overall headline metric
    assert "Worst headline metric (Overall)" in html_out
    assert "EOD = 0.244" in html_out


def test_canonical_metric_bar_order(mock_core_four_results: list[MetricResult]) -> None:
    from bias_aperture.report.generator import _build_subgroup_matrix

    groups = _build_subgroup_matrix(mock_core_four_results)
    for g_data in groups.values():
        if len(g_data["metric_bars"]) > 1:
            labels = [b["label"] for b in g_data["metric_bars"]]
            order = {"DPD": 0, "EOD": 1, "EOP": 2, "DIR": 3}
            ranks = [order.get(lbl, 99) for lbl in labels]
            assert ranks == sorted(ranks), f"Bars out of canonical order: {labels}"
