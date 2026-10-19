"""Autonomous compliance report reconciler and self-healing engine.

Audits pre-compiled and dynamic HTML/PDF compliance dossiers for factual,
visual, and structural integrity, and automatically heals/regenerates them
when templates, metadata, or metrics drift. Built entirely on standard library
dependencies (zero third-party HTML parser dependencies).
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

from bias_aperture.report.reconciliation_extraction import (
    extract_metrics_and_context_from_html,
)
from bias_aperture.report.reconciliation_support import (
    ReconciliationIssue,
    ReconciliationSummary,
    _convert_pdf,
    count_pdf_pages,
)

logger = logging.getLogger(__name__)

__all__ = [
    "ReconciliationIssue",
    "ReconciliationSummary",
    "ReportReconciler",
    "count_pdf_pages",
    "extract_metrics_and_context_from_html",
]


class ReportReconciler:
    """Audits and self-heals compliance reports across HTML and PDF formats."""

    def __init__(self, report_dir: Path | str | None = None) -> None:
        if report_dir is None:
            self.report_dir = Path("report")
        else:
            self.report_dir = Path(report_dir)

    @classmethod
    def audit_dossiers(
        cls, report_dir: Path | str | None = None
    ) -> list[ReconciliationIssue]:
        """Audit HTML and companion PDF reports in report_dir against invariants."""
        target_dir = Path(report_dir) if report_dir is not None else Path("report")
        issues: list[ReconciliationIssue] = []
        if not target_dir.exists():
            return [
                ReconciliationIssue(
                    str(target_dir), "MISSING_DIR", f"Directory not found: {target_dir}"
                )
            ]

        html_files = sorted(target_dir.glob("*.html"))
        if not html_files:
            return [
                ReconciliationIssue(
                    str(target_dir),
                    "NO_REPORTS",
                    f"No HTML reports found in: {target_dir}",
                )
            ]

        for html_path in html_files:
            name = html_path.name
            try:
                html_text = html_path.read_text(encoding="utf-8")
            except Exception as exc:
                issues.append(
                    ReconciliationIssue(
                        name, "READ_ERROR", f"Could not read HTML: {exc}"
                    )
                )
                continue

            # 1. Companion PDF Exists, fresh, and not empty
            pdf_path = html_path.with_suffix(".pdf")
            if not pdf_path.exists():
                issues.append(
                    ReconciliationIssue(
                        name, "MISSING_PDF", f"Missing companion PDF: {pdf_path.name}"
                    )
                )
            elif pdf_path.stat().st_size < 1000:
                issues.append(
                    ReconciliationIssue(
                        name,
                        "CORRUPT_PDF",
                        f"PDF is abnormally small ({pdf_path.stat().st_size} bytes)",
                    )
                )
            else:
                # Page count sanity check (guards against the 17-page duplication bug)
                pages = count_pdf_pages(pdf_path)
                if pages > 8:
                    issues.append(
                        ReconciliationIssue(
                            name,
                            "PAGE_BLOAT",
                            f"PDF page count exceeds 8 pages ({pages} pages); "
                            "likely duplicate explainability sections",
                        )
                    )

            # 2. Strict R-015 Offline Contract (Zero external network resources)
            external_scripts = re.findall(
                r'<script[^>]+src=["\'](http[s]?://[^"\']+)["\']', html_text, re.I
            )
            external_links = re.findall(
                r'<link[^>]+href=["\'](http[s]?://[^"\']+)["\']', html_text, re.I
            )
            external_images = re.findall(
                r'<img[^>]+src=["\'](http[s]?://[^"\']+)["\']', html_text, re.I
            )
            external_fonts = re.findall(
                r'@import\s+url\(["\']?(http[s]?://[^"\'\)]+)["\']?\)', html_text, re.I
            )

            if external_scripts or external_links or external_images or external_fonts:
                total_ext = (
                    len(external_scripts)
                    + len(external_links)
                    + len(external_images)
                    + len(external_fonts)
                )
                issues.append(
                    ReconciliationIssue(
                        name,
                        "OFFLINE_BREACH",
                        "Violates R-015 Offline Contract: "
                        f"{total_ext} external network references found",
                    )
                )

            # 3. Factual & Data Integrity Invariants
            # Check for raw NaN / undefined / None leaked into HTML text
            if re.search(r">\s*(?:NaN|undefined|None)\s*<", html_text, re.I):
                issues.append(
                    ReconciliationIssue(
                        name,
                        "RAW_NAN_OR_NONE",
                        "Raw 'NaN', 'undefined', or 'None' rendered in text",
                    )
                )

            # Check for duplicate dataset name suffix e.g. (N=10954) (N=10954)
            if re.search(r"\(N=\d+\)\s*\(N=\d+\)", html_text):
                issues.append(
                    ReconciliationIssue(
                        name,
                        "DUPLICATE_N_LABEL",
                        "Duplicate (N=XXXX) dataset size label in header",
                    )
                )

            # Check that Section 3 explainability is not duplicated 30+ times
            h3_shap_count = len(re.findall(r"Flagged Disparity:\s*<code>", html_text))
            if h3_shap_count > 5:
                issues.append(
                    ReconciliationIssue(
                        name,
                        "EXPLAINABILITY_DUPLICATION",
                        f"Explainer rendered {h3_shap_count} duplicate blocks; "
                        "should be unified in Section 3",
                    )
                )

            # Check that Plain-Language Executive Translation is present
            if "Executive Translation • Non-Technical Review" not in html_text:
                issues.append(
                    ReconciliationIssue(
                        name,
                        "MISSING_PLAIN_LANGUAGE_SUMMARY",
                        "Report is missing plain-language executive translation card",
                    )
                )

        return issues

    @classmethod
    def extract_metrics_and_context_from_html(cls, html_path: Path) -> Any | None:
        """Compatibility delegate to the report-context HTML extractor."""
        return extract_metrics_and_context_from_html(html_path)

    def heal_dossiers(
        self, predictions_csv: Path | None = None
    ) -> ReconciliationSummary:
        """Instance method delegating to heal_all on self.report_dir."""
        return self.heal_all(self.report_dir, predictions_csv=predictions_csv)

    @classmethod
    def heal_all(
        cls,
        report_dir: Path | str | None = None,
        predictions_csv: Path | None = None,
    ) -> ReconciliationSummary:
        """Self-heal all reports in report_dir: regenerate HTML, re-export PDFs."""
        target_dir = Path(report_dir) if report_dir is not None else Path("report")
        if predictions_csv is None:
            default_csv = Path("data/processed/fairface_predictions_val.csv")
            if default_csv.exists():
                predictions_csv = default_csv

        from bias_aperture.cli import AuditPipeline
        from bias_aperture.report.generator import HTMLReportGenerator

        healed: list[str] = []
        html_files = sorted(target_dir.glob("*.html"))

        for html_path in html_files:
            name = html_path.name
            logger.info("Healing compliance report: %s", name)

            # Case A: Binary tasks regenerable from live FairFace validation CSV
            if (
                predictions_csv
                and predictions_csv.exists()
                and name == "audit_report_val_gender.html"
            ):
                pipeline = AuditPipeline()
                pipeline.run(
                    predictions_file=predictions_csv,
                    true_label_col="true_gender",
                    predicted_label_col="predicted_gender",
                    protected_attr="gender",
                    output_report=html_path,
                    model_name="ResNet-34 (FairFace Baseline)",
                    dataset_name="FairFace Benchmark Dataset",
                    explain=True,
                )
                healed.append(name)
            elif (
                predictions_csv
                and predictions_csv.exists()
                and name == "audit_report_val_race_gender_shap.html"
            ):
                pipeline = AuditPipeline()
                pipeline.run(
                    predictions_file=predictions_csv,
                    true_label_col="true_gender",
                    predicted_label_col="predicted_gender",
                    protected_attr="race_gender",
                    race_col="subgroup_race",
                    gender_col="subgroup_gender",
                    age_col="subgroup_age",
                    output_report=html_path,
                    model_name="FairFace ResNet-34 Multi-Task Classifier",
                    dataset_name="FairFace Benchmark Dataset",
                    explain=True,
                )
                healed.append(name)

            # Case B: Multi-backbone/multiclass reports (ViT, ResNet-50, MobileNetV2,
            # race_verified, ...) re-rendered from embedded metrics
            else:
                ctx = cls.extract_metrics_and_context_from_html(html_path)
                if ctx is not None:
                    generator = HTMLReportGenerator()
                    generator.save(ctx, html_path)
                    healed.append(name)

            # Re-export companion PDF
            pdf_path = html_path.with_suffix(".pdf")
            try:
                _convert_pdf(html_path, pdf_path)
            except Exception as e:
                logger.error("Failed to export PDF for %s: %s", name, e)

        # Run final audit
        issues = cls.audit_dossiers(report_dir)
        return ReconciliationSummary(
            total_scanned=len(html_files),
            clean_count=len(html_files) - len({i.report_name for i in issues}),
            issues=issues,
            healed_reports=healed,
        )
