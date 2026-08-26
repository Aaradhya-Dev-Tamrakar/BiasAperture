"""
Compliance report generator engine (WP3 / Stream B).

Compiles demographic disparity audit metrics into a standalone offline HTML
compliance report adhering to the Mitchell et al. (2019) Model Card structure
and Gebru et al. (2018) Datasheet format with regulatory mapping tables
(EU AI Act Article 10, NIST AI RMF Measure 2.11).
"""

from __future__ import annotations

import datetime
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from bias_aperture.schema import MetricResult

# Static regulatory mapping table (Claim Ledger R-017, R-018)
REGULATORY_MAPPING: dict[str, str] = {
    "demographic_parity_difference": "EU AI Act Art. 10(2)(f) / NIST Measure 2.11",
    "equalized_odds_difference": "EU AI Act Art. 10(2)(g) / NIST Measure 2.11",
    "equal_opportunity_difference": "EU AI Act Art. 10(3) / NIST Measure 2.11",
    "disparate_impact_ratio": "EEOC 4/5ths Rule / EU AI Act Annex IV §2(g)",
}


@dataclass(frozen=True, slots=True)
class ReportContext:
    """Aggregated context data model for report generation."""

    metrics: Sequence[MetricResult]
    model_name: str = "FairFace ResNet-34 Multi-Task Classifier"
    dataset_name: str = "FairFace Benchmark (7-Race)"
    protected_axis: str = "race"
    total_subjects: int = 0
    model_description: str = (
        "ImageNet-pretrained ResNet-34 terminating in an 18-unit linear head "
        "sliced for race (7), gender (2), and age (9) classification."
    )
    timestamp: str = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )
    )
    regulatory_map: dict[str, str] = field(
        default_factory=lambda: dict(REGULATORY_MAPPING)
    )


class HTMLReportGenerator:
    """Standalone HTML compliance report compiler."""

    def __init__(self, template_dir: Path | None = None) -> None:
        if template_dir is None:
            template_dir = Path(__file__).parent / "templates"
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True,
        )

    def _prepare_template_context(self, context: ReportContext) -> dict[str, Any]:
        """Format metrics into structured presentation dictionaries."""
        summary_metrics = [m for m in context.metrics if m.subgroup == "ALL"]
        subgroup_metrics = [m for m in context.metrics if m.subgroup != "ALL"]

        # Group subgroup metrics by subgroup label
        groups: dict[str, dict[str, Any]] = {}
        for m in subgroup_metrics:
            g = m.subgroup
            if g not in groups:
                groups[g] = {
                    "label": g,
                    "sample_size": m.subgroup_sample_size,
                    "insufficient_sample": m.insufficient_sample,
                    "dpd": "—",
                    "eod": "—",
                    "eop": "—",
                    "dir": "—",
                }
            if m.metric_value is not None:
                val_str = f"{m.metric_value:.3f}"
                if m.metric_name == "demographic_parity_difference":
                    groups[g]["dpd"] = val_str
                elif m.metric_name == "equalized_odds_difference":
                    groups[g]["eod"] = val_str
                elif m.metric_name == "equal_opportunity_difference":
                    groups[g]["eop"] = val_str
                elif m.metric_name == "disparate_impact_ratio":
                    groups[g]["dir"] = val_str

        subgroup_matrix = list(groups.values())

        return {
            "context": context,
            "summary_metrics": summary_metrics,
            "subgroup_matrix": subgroup_matrix,
        }

    def generate(self, context: ReportContext) -> str:
        """Render the standalone HTML report string.

        Parameters
        ----------
        context : ReportContext
            Audit execution context and metric results.

        Returns
        -------
        str
            Rendered single-file HTML text.
        """
        template = self.env.get_template("report.html.j2")
        render_dict = self._prepare_template_context(context)
        return template.render(**render_dict)

    def save(self, context: ReportContext, output_path: Path | str) -> Path:
        """Generate and write the report to disk.

        Parameters
        ----------
        context : ReportContext
            Audit execution context.
        output_path : Path | str
            Destination file path (.html).

        Returns
        -------
        Path
            Absolute path to the written report.
        """
        html = self.generate(context)
        out = Path(output_path).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        return out
