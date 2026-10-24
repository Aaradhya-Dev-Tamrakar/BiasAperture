"""Test suite for HTML to PDF compilation engine (scripts/export_report_pdf.py).

Validates:
- Discovery of host Blink browser (Chrome / Edge / Chromium)
- Deterministic PDF generation without external dependencies
- Verification of --no-pdf-header-footer invariant (zero local URI leaks)
- Error handling for missing input HTML files
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.export_report_pdf import convert_html_to_pdf, find_blink_browser


def test_convert_html_to_pdf_missing_file_raises(tmp_path: Path) -> None:
    """Ensure FileNotFoundError is raised when input file does not exist."""
    missing_file = tmp_path / "non_existent_report.html"
    with pytest.raises(FileNotFoundError, match="Source HTML report not found"):
        convert_html_to_pdf(missing_file)


def test_find_blink_browser_or_skip() -> None:
    """Verifies that find_blink_browser returns an existing binary when installed."""
    try:
        browser = find_blink_browser()
        assert browser.exists()
        assert browser.is_file()
    except FileNotFoundError:
        pytest.skip("No Blink browser installed on this host environment.")


def test_html_to_pdf_export_and_clean_header_footer(tmp_path: Path) -> None:
    """Verifies compilation of HTML to PDF without browser header/footer leaks."""
    try:
        find_blink_browser()
    except FileNotFoundError:
        pytest.skip("No Blink browser installed on this host environment.")

    # Minimal standalone HTML report
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>BiasAperture Unit Test Report</title>
    <style>
        @page { size: A4; margin: 12mm 15mm; }
        body { font-family: sans-serif; color: #0f172a; }
        h1 { font-size: 18pt; }
        .badge { background: #dcfce7; color: #15803d; padding: 4px 8px; }
    </style>
</head>
<body>
    <h1>Demographic Fairness Compliance Report</h1>
    <p>Testing deterministic PDF compilation for BiasAperture.</p>
    <span class="badge">PASS</span>
</body>
</html>
"""
    test_html = tmp_path / "test_report.html"
    test_html.write_text(html_content, encoding="utf-8")
    test_pdf = tmp_path / "test_report.pdf"

    # Export to PDF
    out = convert_html_to_pdf(test_html, test_pdf)
    assert out.exists()
    assert out == test_pdf
    assert test_pdf.stat().st_size > 500

    # Verify PDF magic bytes
    with open(test_pdf, "rb") as f:
        header = f.read(5)
    assert header == b"%PDF-"

    # Verify no file:/// URI leak in extracted text
    try:
        import pypdf

        reader = pypdf.PdfReader(str(test_pdf))
        assert len(reader.pages) >= 1
        page_text = reader.pages[0].extract_text()
        assert "Demographic Fairness Compliance Report" in page_text
        assert "file:///" not in page_text
    except ImportError:
        pass  # pypdf optional for basic compilation check


def test_pdf_report_generator_and_keep_html(tmp_path: Path, monkeypatch) -> None:
    """Verify PDFReportGenerator invocation and keep_html parameter handling."""
    from bias_aperture.report import PDFReportGenerator, ReportContext
    from bias_aperture.schema import MetricResult

    context = ReportContext(
        metrics=[
            MetricResult(
                metric_name="demographic_parity_difference",
                subgroup="ALL",
                subgroup_sample_size=100,
                metric_value=0.05,
                ci_lower=0.01,
                ci_upper=0.09,
                p_value=0.12,
            )
        ]
    )

    # Monkeypatch convert_html_to_pdf to mock external browser invocation
    converted_calls = []

    def mock_convert(html_path, pdf_path):
        converted_calls.append((Path(html_path), Path(pdf_path)))
        Path(pdf_path).write_bytes(b"%PDF-1.4 dummy")
        return Path(pdf_path)

    import bias_aperture.report.pdf as pdf_mod

    monkeypatch.setattr(pdf_mod, "convert_html_to_pdf", mock_convert)

    gen = PDFReportGenerator()
    out_pdf = tmp_path / "audit_output.pdf"

    # Test with keep_html=False (intermediate html removed)
    res = gen.save(context, out_pdf, keep_html=False)
    assert res.exists()
    assert res == out_pdf
    assert not out_pdf.with_suffix(".html").exists()
    assert len(converted_calls) == 1

    # Test with keep_html=True (intermediate html preserved)
    out_pdf_2 = tmp_path / "audit_output_both.pdf"
    res_2 = gen.save(context, out_pdf_2, keep_html=True)
    assert res_2.exists()
    assert out_pdf_2.with_suffix(".html").exists()


def test_cli_parser_format_flag() -> None:
    """Verify --format flag parsing in build_parser."""
    from bias_aperture.cli_parser import build_parser

    parser = build_parser()
    args_pdf = parser.parse_args(["-i", "dummy.csv", "--format", "pdf"])
    assert args_pdf.format == "pdf"

    args_both = parser.parse_args(["-i", "dummy.csv", "-f", "both"])
    assert args_both.format == "both"

    args_default = parser.parse_args(["-i", "dummy.csv"])
    assert args_default.format is None


def test_pipeline_generate_report_format_resolution(
    tmp_path: Path, monkeypatch
) -> None:
    """Verify AuditPipeline._generate_report resolves format and delegates correctly."""
    from bias_aperture.pipeline import AuditPipeline
    from bias_aperture.schema import MetricResult

    metrics = [
        MetricResult(
            metric_name="demographic_parity_difference",
            subgroup="ALL",
            subgroup_sample_size=100,
            metric_value=0.04,
            ci_lower=0.01,
            ci_upper=0.08,
            p_value=0.20,
        )
    ]

    saved_calls = []

    def mock_pdf_save(self, ctx, out_path, *, keep_html=False):
        saved_calls.append(("pdf", Path(out_path), keep_html))
        Path(out_path).write_bytes(b"%PDF-1.4 dummy")
        if keep_html:
            Path(out_path).with_suffix(".html").write_text(
                "dummy html", encoding="utf-8"
            )
        return Path(out_path)

    def mock_html_save(self, ctx, out_path):
        saved_calls.append(("html", Path(out_path), False))
        Path(out_path).write_text("dummy html", encoding="utf-8")
        return Path(out_path)

    from bias_aperture.report import HTMLReportGenerator, PDFReportGenerator

    monkeypatch.setattr(PDFReportGenerator, "save", mock_pdf_save)
    monkeypatch.setattr(HTMLReportGenerator, "save", mock_html_save)

    # 1. Auto-detection from .pdf suffix when format is None
    pdf_target = tmp_path / "report_auto.pdf"
    res1 = AuditPipeline._generate_report(
        metrics=metrics,
        records=[1] * 100,
        output_report=pdf_target,
        model_name="TestModel",
        dataset_name="TestDataset",
        protected_attr="race",
        explanations=[],
        backend="dual",
        backend_status="OK",
        report_format=None,
    )
    assert res1 == pdf_target
    assert saved_calls[-1][0] == "pdf"
    assert saved_calls[-1][2] is False

    # 2. Explicit format="both"
    both_target = tmp_path / "report_dual.html"
    res2 = AuditPipeline._generate_report(
        metrics=metrics,
        records=[1] * 100,
        output_report=both_target,
        model_name="TestModel",
        dataset_name="TestDataset",
        protected_attr="race",
        explanations=[],
        backend="dual",
        backend_status="OK",
        report_format="both",
    )
    assert res2 == both_target.with_suffix(".pdf")
    assert saved_calls[-1][0] == "pdf"
    assert saved_calls[-1][2] is True

    # 3. Explicit format="html"
    html_target = tmp_path / "report_explicit.html"
    res3 = AuditPipeline._generate_report(
        metrics=metrics,
        records=[1] * 100,
        output_report=html_target,
        model_name="TestModel",
        dataset_name="TestDataset",
        protected_attr="race",
        explanations=[],
        backend="dual",
        backend_status="OK",
        report_format="html",
    )
    assert res3 == html_target
    assert saved_calls[-1][0] == "html"
