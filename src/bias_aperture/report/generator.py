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
from bias_aperture.report.metadata_registry import ModelMetadataRegistry
from bias_aperture.schema import ALPHA, MetricResult

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
            "has_explanation": primary is not None
            and bool(primary.feature_attributions),
        }


# ── Report Analytical Helpers (R12) ──────────────────────────────────

# Null-point map: DIR is centred on 1.0, differences on 0.0.
_NULL_POINT: dict[str, float] = {
    "demographic_parity_difference": 0.0,
    "equalized_odds_difference": 0.0,
    "equal_opportunity_difference": 0.0,
    "disparate_impact_ratio": 1.0,
}

_METRIC_SHORT_LABELS: dict[str, tuple[str, str]] = {
    "demographic_parity_difference": ("dpd", "DPD"),
    "equalized_odds_difference": ("eod", "EOD"),
    "equal_opportunity_difference": ("eop", "EOP"),
    "disparate_impact_ratio": ("dir", "DIR"),
}


def _build_subgroup_matrix(
    subgroup_metrics: Sequence[MetricResult],
) -> dict[str, dict[str, Any]]:
    """Group subgroup metrics by label and compute deviation/significance.

    Pure analytical function that converts flat MetricResult rows into
    the nested dictionary structure required by the Jinja2 template.
    Separated from the generator class so it is independently unit-testable.
    """
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
                "metric_bars": [],
                "max_deviation": 0.0,
                "min_p_value": None,
            }
        if m.metric_value is not None:
            val_str = f"{m.metric_value:.3f}"
            short_info = _METRIC_SHORT_LABELS.get(m.metric_name)
            if short_info:
                groups[g][short_info[0]] = val_str
                short_label = short_info[1]
            else:
                short_label = m.metric_name

            null_point = _NULL_POINT.get(m.metric_name, 0.0)
            deviation = abs(m.metric_value - null_point)
            groups[g]["metric_bars"].append(
                {
                    "label": short_label,
                    "value": m.metric_value,
                    "null_point": null_point,
                    "deviation": deviation,
                    "p_value": m.p_value,
                    "significant": m.p_value is not None and m.p_value < ALPHA,
                }
            )
            groups[g]["max_deviation"] = max(groups[g]["max_deviation"], deviation)
            if m.p_value is not None:
                prior = groups[g]["min_p_value"]
                groups[g]["min_p_value"] = (
                    m.p_value if prior is None else min(prior, m.p_value)
                )
    # Enforce canonical order matching Table 2 columns: DPD, EOD, EOP, DIR
    metric_order = {"DPD": 0, "EOD": 1, "EOP": 2, "DIR": 3}
    for g in groups:
        groups[g]["metric_bars"].sort(key=lambda b: metric_order.get(b["label"], 99))
    return groups


def _build_executive_summary(
    groups: dict[str, dict[str, Any]],
    valid_groups: list[dict[str, Any]],
    insufficient_groups: list[dict[str, Any]],
    summary_metrics: Sequence[MetricResult] | None = None,
) -> dict[str, Any]:
    """Compute the executive-summary strip for the report header.

    Counts + worst-offender identification, computed once so the
    Jinja2 template does no aggregation logic of its own.
    """
    flagged_significant = [
        g
        for g in valid_groups
        if g["min_p_value"] is not None and g["min_p_value"] < ALPHA
    ]
    flagged_metric_instances = sum(
        1
        for g in valid_groups
        for b in g.get("metric_bars", [])
        if b.get("significant")
    )

    worst_group_label: str | None = None
    worst_metric_label: str | None = None
    worst_metric_value: float | None = None
    worst_is_overall: bool = False

    # Prefer cross-group headline disparity from Table 1 (subgroup == 'ALL')
    if summary_metrics:
        valid_summary = [m for m in summary_metrics if m.metric_value is not None]
        if valid_summary:

            def _summary_deviation(m: MetricResult) -> float:
                np = _NULL_POINT.get(m.metric_name, 0.0)
                return abs(m.metric_value - np) if m.metric_value is not None else 0.0

            worst_summary_m = max(valid_summary, key=_summary_deviation)
            worst_metric_value = worst_summary_m.metric_value
            worst_group_label = "Overall (Table 1)"
            short_info = _METRIC_SHORT_LABELS.get(worst_summary_m.metric_name)
            worst_metric_label = (
                short_info[1] if short_info else worst_summary_m.metric_name
            )
            worst_is_overall = True

    # Fallback to Table 2 subgroup rows if summary_metrics was absent or unpopulated
    if worst_metric_value is None and valid_groups:
        worst_group = valid_groups[0]
        worst_group_label = worst_group["label"]
        if worst_group.get("metric_bars"):
            worst_metric_bar = max(
                worst_group["metric_bars"], key=lambda b: b["deviation"]
            )
            worst_metric_label = worst_metric_bar["label"]
            worst_metric_value = worst_metric_bar["value"]

    return {
        "total_subgroups": len(groups),
        "valid_subgroups": len(valid_groups),
        "insufficient_count": len(insufficient_groups),
        "flagged_significant_count": len(flagged_significant),
        "flagged_metric_instances_count": flagged_metric_instances,
        "worst_group_label": worst_group_label,
        "worst_metric_label": worst_metric_label,
        "worst_metric_value": worst_metric_value,
        "worst_is_overall": worst_is_overall,
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

        resolved_attributions = list(context.attributions or context.explanations)
        global_explanation = context.get_global_explanation()

        return {
            "context": context,
            "summary_metrics": summary_metrics,
            "subgroup_matrix": valid_groups,
            "insufficient_groups": insufficient_groups,
            "exec_summary": exec_summary,
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
