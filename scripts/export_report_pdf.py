"""Cross-Platform Headless PDF Exporter for BiasAperture Compliance Reports.

Discovers the native Blink engine (Chromium / Chrome / Edge) to
deterministically compile standalone HTML audit dossiers into vector-crisp,
paginated PDFs without requiring heavy C-dependencies (Cairo/Pango/TeX).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from bias_aperture.report.pdf import convert_html_to_pdf, find_blink_browser

__all__ = [
    "compile_all_case_study_reports",
    "convert_html_to_pdf",
    "find_blink_browser",
    "main",
]


def compile_all_case_study_reports(report_dir: Path) -> list[Path]:
    """Compile all HTML compliance reports found in report directory to PDF."""
    html_files = sorted(report_dir.glob("*.html"))
    compiled: list[Path] = []
    for h in html_files:
        out_pdf = h.with_suffix(".pdf")
        print(f"Compiling: {h.name} -> {out_pdf.name}...")
        res = convert_html_to_pdf(h, out_pdf)
        compiled.append(res)
    return compiled


def main() -> None:
    """CLI entrypoint for standalone PDF compilation."""
    parser = argparse.ArgumentParser(
        description="Convert BiasAperture standalone HTML reports to PDF dossiers."
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        help="Path to input HTML file (or use --all to compile all reports in report/)",
    )
    parser.add_argument(
        "output",
        nargs="?",
        type=Path,
        help="Optional path to output PDF file.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Compile all HTML reports in the report/ directory to companion PDFs.",
    )

    args = parser.parse_args()

    if args.all or args.input is None:
        root_dir = Path(__file__).resolve().parent.parent
        report_dir = root_dir / "report"
        if not report_dir.exists():
            print(f"Report directory not found at: {report_dir}", file=sys.stderr)
            sys.exit(1)
        outputs = compile_all_case_study_reports(report_dir)
        print(f"\nSuccessfully compiled {len(outputs)} PDF reports in {report_dir}.")
    else:
        out = convert_html_to_pdf(args.input, args.output)
        print(f"Successfully exported PDF dossier: {out}")


if __name__ == "__main__":
    main()
