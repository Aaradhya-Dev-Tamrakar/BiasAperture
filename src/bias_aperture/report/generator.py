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

from bias_aperture.explainability import ExplanationResult
from bias_aperture.report.analysis import (
    _METRIC_SHORT_LABELS,
    _build_executive_summary,
    _build_subgroup_matrix,
)
from bias_aperture.report.metadata_registry import ModelMetadataRegistry
from bias_aperture.report.narrative import (
    METRIC_GLOSSARY,
    PlainLanguageSummary,
    synthesize_plain_language_narrative,
)
from bias_aperture.schema import MetricResult

__all__ = [
    "HTMLReportGenerator",
    "PlainLanguageSummary",
    "REGULATORY_MAPPING",
    "ReportContext",
]

# Static regulatory mapping table (Claim Ledger R-017, R-018)
REGULATORY_MAPPING: dict[str, str] = {
    "demographic_parity_difference": "EU AI Act Art. 10(2)(f) / NIST Measure 2.11",
    "equalized_odds_difference": "EU AI Act Art. 10(2)(g) / NIST Measure 2.11",
    "equal_opportunity_difference": "EU AI Act Art. 10(3) / NIST Measure 2.11",
    "disparate_impact_ratio": "EEOC 4/5ths Rule / EU AI Act Annex IV §2(g)",
}

_DEFAULT_MODEL_DESC: str = (
    "ImageNet-pretrained ResNet-34 terminating in an 18-unit linear head "
    "sliced for race (7), gender (2), and age (9) classification."
)


@dataclass(frozen=True, slots=True)
class ReportContext:
    """Aggregated context data model for report generation."""

    metrics: Sequence[MetricResult]
    model_name: str = "FairFace ResNet-34 Multi-Task Classifier"
    dataset_name: str = "FairFace Benchmark (7-Race)"
    protected_axis: str = "race"
    total_subjects: int = 0
    model_description: str = _DEFAULT_MODEL_DESC
    timestamp: str = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )
    )
    regulatory_map: dict[str, str] = field(
        default_factory=lambda: dict(REGULATORY_MAPPING)
    )
    explanations: Sequence[ExplanationResult] = field(default_factory=list)
    attributions: Sequence[ExplanationResult] = field(default_factory=tuple)
    backend: str = "unspecified"
    backend_status: str = "Execution status was not supplied."

    def __post_init__(self) -> None:
        if not self.attributions and self.explanations:
            object.__setattr__(self, "attributions", tuple(self.explanations))
        elif not self.explanations and self.attributions:
            object.__setattr__(self, "explanations", list(self.attributions))

        # Dynamically auto-resolve model description if using default
        # description with a non-default model
        if (
            self.model_description == _DEFAULT_MODEL_DESC or not self.model_description
        ) and self.model_name:
            if (
                self.model_name != "FairFace ResNet-34 Multi-Task Classifier"
                or not self.model_description
            ):
                resolved_meta = ModelMetadataRegistry.resolve(
                    self.model_name, self.protected_axis
                )
                object.__setattr__(self, "model_description", resolved_meta.description)

    def get_global_explanation(self) -> dict[str, Any]:
        """Consolidate surrogate attributions into a deduplicated explanation."""
        resolved = list(self.attributions or self.explanations)
        primary: ExplanationResult | None = None
        triggered_pairs: list[dict[str, str]] = []

        for exp in resolved:
            if exp.feature_attributions:
                if primary is None:
                    primary = exp
                short_info = _METRIC_SHORT_LABELS.get(exp.metric_name)
                metric_disp = short_info[1] if short_info else exp.metric_name
                subgroup_disp = exp.subgroup
                triggered_pairs.append(
                    {
                        "subgroup": subgroup_disp,
                        "metric_name": metric_disp,
                    }
                )

        # Deduplicate and sort triggered pairs
        seen = set()
        deduped_pairs = []
        for p in triggered_pairs:
            key = (p["subgroup"], p["metric_name"])
            if key not in seen:
                seen.add(key)
                deduped_pairs.append(p)
        deduped_pairs.sort(key=lambda p: (p["subgroup"], p["metric_name"]))

        return {
            "primary_explanation": primary,
            "triggered_pairs": deduped_pairs,
            "feature_importances": primary.feature_attributions if primary else {},
            "spatial_visualizations": [
                visualization
                for explanation in resolved
                for visualization in explanation.base64_visualizations
                if visualization.lstrip().startswith("<svg")
            ],
            "has_explanation": primary is not None
            and bool(primary.feature_attributions)
            or any(
                explanation.base64_visualizations for explanation in resolved
            ),
        }


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
        """Format metrics into structured presentation dictionaries.

        Delegates analytical computation to standalone helpers so this
        method is a thin composition point.
        """
        summary_metrics = [m for m in context.metrics if m.subgroup == "ALL"]
        subgroup_metrics = [m for m in context.metrics if m.subgroup != "ALL"]

        groups = _build_subgroup_matrix(subgroup_metrics)

        valid_groups = [g for g in groups.values() if not g["insufficient_sample"]]
        insufficient_groups = [g for g in groups.values() if g["insufficient_sample"]]

        valid_groups.sort(
            key=lambda g: (
                -g["max_deviation"],
                g["min_p_value"] if g["min_p_value"] is not None else 1.0,
            )
        )

        exec_summary = _build_executive_summary(
            groups, valid_groups, insufficient_groups, summary_metrics
        )

        plain_summary = synthesize_plain_language_narrative(context, exec_summary)
        resolved_attributions = list(context.attributions or context.explanations)
        global_explanation = context.get_global_explanation()

        return {
            "context": context,
            "summary_metrics": summary_metrics,
            "subgroup_matrix": valid_groups,
            "insufficient_groups": insufficient_groups,
            "exec_summary": exec_summary,
            "plain_summary": plain_summary,
            "metric_glossary": METRIC_GLOSSARY,
            "has_attributions": bool(resolved_attributions),
            "attributions": resolved_attributions,
            "global_explanation": global_explanation,
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
        """
        html = self.generate(context)
        out = Path(output_path).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        return out
