"""Headless Blink PDF compilation engine for BiasAperture compliance reports (WP3).

Discovers native Blink browser binaries (Chromium, Google Chrome, Microsoft Edge)
across operating systems (Windows prioritized) and converts standalone HTML
audit dossiers into publication-grade vector PDFs without requiring heavy
native C graphics dependencies.
"""

from __future__ import annotations

import logging
import os
import platform
import shutil
import subprocess
from pathlib import Path

from bias_aperture.report.generator import HTMLReportGenerator, ReportContext

logger = logging.getLogger(__name__)

__all__ = [
    "PDFReportGenerator",
    "convert_html_to_pdf",
    "find_blink_browser",
]


def find_blink_browser() -> Path:
    """Discover an available Blink-based browser binary across platforms.

    Prioritizes Windows standard installations, followed by Linux and macOS.

    Returns
    -------
    Path
        Absolute path to the discovered browser binary.

    Raises
    ------
    FileNotFoundError
        If no supported browser executable is discovered.
    """
    # 1. Environment variable override
    if env_bin := os.environ.get("BIASAPERTURE_BROWSER_BIN"):
        p = Path(env_bin)
        if p.exists():
            return p

    # 2. Executable name discovery in PATH (Windows prioritized)
    search_names = [
        "chrome.exe",
        "msedge.exe",
        "chrome",
        "msedge",
        "google-chrome-stable",
        "google-chrome",
        "chromium-browser",
        "chromium",
        "microsoft-edge-stable",
        "microsoft-edge",
    ]
    for name in search_names:
        if found := shutil.which(name):
            return Path(found)

    # 3. Known OS filesystem locations (Windows prioritized)
    system = platform.system()
    candidates: list[Path] = []

    if system == "Windows":
        candidates = [
            Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
            Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
            Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
            Path(
                os.path.expandvars(
                    r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
                )
            ),
            Path(
                os.path.expandvars(
                    r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"
                )
            ),
        ]
    elif system == "Linux":
        candidates = [
            Path("/usr/bin/google-chrome"),
            Path("/usr/bin/google-chrome-stable"),
            Path("/usr/bin/chromium"),
            Path("/usr/bin/chromium-browser"),
            Path("/usr/bin/microsoft-edge"),
            Path("/usr/bin/microsoft-edge-stable"),
            Path("/snap/bin/chromium"),
        ]
    elif system == "Darwin":
        candidates = [
            Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
            Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
            Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
        ]

    for p in candidates:
        if p.exists():
            return p

    raise FileNotFoundError(
        f"No Blink-based browser (Chrome, Edge, Chromium) discovered on {system}. "
        "Please install Chromium/Chrome/Edge or set BIASAPERTURE_BROWSER_BIN."
    )


def convert_html_to_pdf(
    html_path: Path | str, pdf_path: Path | str | None = None
) -> Path:
    """Convert a standalone HTML report into an immutable vector PDF file.

    Parameters
    ----------
    html_path : Path | str
        Path to source HTML report.
    pdf_path : Path | str | None, optional
        Target path for generated PDF. Defaults to input path with .pdf extension.

    Returns
    -------
    Path
        Path to compiled PDF dossier.
    """
    html_file = Path(html_path).resolve()
    if not html_file.exists():
        raise FileNotFoundError(f"Source HTML report not found: {html_file}")

    if pdf_path is None:
        target_pdf = html_file.with_suffix(".pdf")
    else:
        target_pdf = Path(pdf_path).resolve()

    target_pdf.parent.mkdir(parents=True, exist_ok=True)
    browser_bin = find_blink_browser()

    base_args = [
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        "--no-pdf-header-footer",
        "--generate-pdf-document-outline",
        "--allow-file-access-from-files",
        # Container / headless flags
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        f"--print-to-pdf={target_pdf}",
        str(html_file),
    ]

    # Try modern headless first (--headless=new), with legacy fallback
    cmd = [str(browser_bin), "--headless=new", *base_args]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )

    needs_legacy_fallback = (
        result.returncode != 0 or not target_pdf.exists()
    ) and "unknown flag" in result.stderr.lower()
    if needs_legacy_fallback:
        cmd_legacy = [str(browser_bin), "--headless", *base_args]
        result = subprocess.run(
            cmd_legacy,
            capture_output=True,
            text=True,
            check=False,
        )

    if result.returncode != 0 and not target_pdf.exists():
        raise RuntimeError(
            f"PDF compilation failed (exit code {result.returncode}):\n{result.stderr}"
        )

    return target_pdf


class PDFReportGenerator:
    """Compile standalone compliance reports to A4 PDF via headless Blink."""

    def __init__(self, html_generator: HTMLReportGenerator | None = None) -> None:
        self.html_generator = html_generator or HTMLReportGenerator()

    def save(
        self,
        context: ReportContext,
        output_path: Path | str,
        *,
        keep_html: bool = False,
    ) -> Path:
        """Render HTML context and compile to PDF dossier.

        Parameters
        ----------
        context : ReportContext
            Audit execution context.
        output_path : Path | str
            Destination file path (.pdf).
        keep_html : bool, optional
            Whether to retain the generated intermediate HTML file on disk.

        Returns
        -------
        Path
            Path to generated PDF file.
        """
        target_pdf = Path(output_path).resolve()
        if target_pdf.suffix.lower() != ".pdf":
            target_pdf = target_pdf.with_suffix(".pdf")

        html_path = target_pdf.with_suffix(".html")
        self.html_generator.save(context, html_path)

        try:
            convert_html_to_pdf(html_path, target_pdf)
        finally:
            if not keep_html and html_path.exists():
                try:
                    html_path.unlink()
                except OSError as exc:
                    logger.debug(
                        "Failed to remove intermediate HTML report %s: %s",
                        html_path,
                        exc,
                    )

        return target_pdf
