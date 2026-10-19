"""Shared reconciliation result contracts and low-level document helpers."""

from __future__ import annotations

import html
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ReconciliationIssue:
    """Represents a discovered discrepancy or policy violation in a report."""

    report_name: str
    issue_type: str
    message: str

    @property
    def description(self) -> str:
        return self.message


@dataclass(frozen=True, slots=True)
class ReconciliationSummary:
    """Summary of reconciliation audit or self-healing pass."""

    total_scanned: int
    clean_count: int
    issues: list[ReconciliationIssue]
    healed_reports: list[str]

    @property
    def scanned_count(self) -> int:
        return self.total_scanned

    @property
    def healed_count(self) -> int:
        return len(self.healed_reports)

    @property
    def is_clean(self) -> bool:
        return len(self.issues) == 0


def count_pdf_pages(pdf_path: Path) -> int:
    """Count PDF pages deterministically without external dependencies."""
    if not pdf_path.exists():
        return 0
    try:
        content = pdf_path.read_bytes()
        # Count /Type /Page objects (excluding /Pages)
        matches = re.findall(rb"/Type\s*/Page\b", content)
        return len(matches)
    except Exception:
        return 0


def _strip_tags(text: str) -> str:
    """Strip HTML tags and unescape HTML entities to plain text."""
    clean = re.sub(r"<[^>]+>", "", text)
    return html.unescape(clean).strip()


def _convert_pdf(html_path: Path, pdf_path: Path) -> None:
    """Invoke the Blink PDF exporter via function call or subprocess."""
    try:
        from scripts.export_report_pdf import convert_html_to_pdf

        convert_html_to_pdf(html_path, pdf_path)
    except (ImportError, ModuleNotFoundError):
        repo_root = Path(__file__).resolve().parent.parent.parent.parent
        script = repo_root / "scripts" / "export_report_pdf.py"
        res = subprocess.run(
            [sys.executable, str(script), str(html_path), str(pdf_path)],
            capture_output=True,
            text=True,
        )
        if res.returncode != 0:
            raise RuntimeError(
                f"PDF export failed for {html_path}: {res.stderr or res.stdout}"
            ) from None
