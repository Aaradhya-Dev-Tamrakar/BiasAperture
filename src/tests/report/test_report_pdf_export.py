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
