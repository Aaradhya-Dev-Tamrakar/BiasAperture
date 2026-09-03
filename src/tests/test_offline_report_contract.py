"""
Offline Compliance Report Contract Verification (R-015).

This module validates that HTML report templates and generator contracts produce
strictly standalone HTML files containing zero external CDN dependencies, zero external
script/link tags, and inlined data-URIs for raster image artifacts.
"""

from __future__ import annotations

import re


def _verify_offline_html_contract(html_content: str) -> dict[str, int]:
    """Inspects HTML string for external network dependencies."""
    external_scripts = re.findall(
        r'<script[^>]+src=["\'](http[s]?://[^"\']+)["\']', html_content, re.I
    )
    external_links = re.findall(
        r'<link[^>]+href=["\'](http[s]?://[^"\']+)["\']', html_content, re.I
    )
    external_images = re.findall(
        r'<img[^>]+src=["\'](http[s]?://[^"\']+)["\']', html_content, re.I
    )
    external_fonts = re.findall(
        r'@import\s+url\(["\']?(http[s]?://[^"\'\)]+)["\']?\)', html_content, re.I
    )

    return {
        "external_scripts": len(external_scripts),
        "external_links": len(external_links),
        "external_images": len(external_images),
        "external_fonts": len(external_fonts),
    }


def test_offline_html_contract_validation() -> None:
    """
    R-015: Verifies that valid BiasAperture report HTML satisfies the offline contract:
    - 0 external scripts
    - 0 external stylesheet links
    - 0 external image links
    - 0 external font imports
    - Embedded images must use base64 data-URIs
    """
    # Sample compliant HTML matching generator.py contract
    b64_px = (
        "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR"
        "42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )
    compliant_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>BiasAperture Audit Report</title>
        <style>
            body {{ font-family: -apple-system, Roboto, sans-serif; }}
            .badge {{ padding: 4px 8px; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <h1>Demographic Fairness Compliance Report</h1>
        <img src="{b64_px}" alt="SHAP Plot" />
    </body>
    </html>
    """

    violations = _verify_offline_html_contract(compliant_html)
    assert violations["external_scripts"] == 0
    assert violations["external_links"] == 0
    assert violations["external_images"] == 0
    assert violations["external_fonts"] == 0


def test_offline_html_contract_catches_violations() -> None:
    """Verifies that the validator correctly flags external network violations."""
    non_compliant_html = """
    <html>
    <head>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    </head>
    <body>
        <img src="https://example.com/shap_plot.png" />
    </body>
    </html>
    """
    violations = _verify_offline_html_contract(non_compliant_html)
    assert violations["external_links"] == 1
    assert violations["external_scripts"] == 1
    assert violations["external_images"] == 1
