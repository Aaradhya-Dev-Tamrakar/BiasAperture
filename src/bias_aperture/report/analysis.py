"""Pure metric-to-presentation analysis helpers for report generation."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from bias_aperture.schema import ALPHA, MetricResult

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

TOLERANCE_THRESHOLDS: dict[str, dict[str, Any]] = {
    "disparate_impact_ratio": {"direction": "min", "threshold": 0.80},
    "demographic_parity_difference": {"direction": "max", "threshold": 0.10},
    "equalized_odds_difference": {"direction": "max", "threshold": 0.10},
    "equal_opportunity_difference": {"direction": "max", "threshold": 0.10},
}


def is_threshold_breach(metric_name: str, value: float | None) -> bool:
    """Return True if metric value breaches standard fairness tolerance."""
    if value is None:
        return False
    cfg = TOLERANCE_THRESHOLDS.get(metric_name)
    if not cfg:
        return False
    if cfg["direction"] == "min":
        return value < cfg["threshold"]
    return value > cfg["threshold"]


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
            significant = m.p_value is not None and m.p_value < ALPHA
            breached = is_threshold_breach(m.metric_name, m.metric_value)
            if significant and breached:
                status = "FAIL"
            elif significant:
                status = "WARN"
            else:
                status = "PASS"

            groups[g]["metric_bars"].append(
                {
                    "label": short_label,
                    "value": m.metric_value,
                    "null_point": null_point,
                    "deviation": deviation,
                    "p_value": m.p_value,
                    "significant": significant,
                    "breached": breached,
                    "status": status,
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
    flagged_breach_groups = [
        g
        for g in valid_groups
        if any(b.get("status") == "FAIL" for b in g.get("metric_bars", []))
    ]
    flagged_metric_instances = sum(
        1
        for g in valid_groups
        for b in g.get("metric_bars", [])
        if b.get("significant")
    )
    flagged_metric_breach_count = sum(
        1
        for g in valid_groups
        for b in g.get("metric_bars", [])
        if b.get("status") == "FAIL"
    )

    worst_group_label: str | None = None
    worst_metric_label: str | None = None
    worst_metric_value: float | None = None
    worst_is_overall: bool = False

    # 1. Headline summary disparity from Table 1 (subgroup == 'ALL')
    headline_metric_label: str | None = None
    headline_metric_value: float | None = None
    if summary_metrics:
        valid_summary = [m for m in summary_metrics if m.metric_value is not None]
        if valid_summary:

            def _summary_deviation(m: MetricResult) -> float:
                np = _NULL_POINT.get(m.metric_name, 0.0)
                return abs(m.metric_value - np) if m.metric_value is not None else 0.0

            worst_summary_m = max(valid_summary, key=_summary_deviation)
            headline_metric_value = worst_summary_m.metric_value
            short_info = _METRIC_SHORT_LABELS.get(worst_summary_m.metric_name)
            headline_metric_label = (
                short_info[1] if short_info else worst_summary_m.metric_name
            )

    # 2. Dynamically resolve worst demographic cohort strictly from Table 2 subgroups
    candidate_groups = flagged_breach_groups if flagged_breach_groups else valid_groups
    if candidate_groups:
        worst_group = candidate_groups[0]
        worst_group_label = worst_group["label"]
        if worst_group.get("metric_bars"):
            worst_metric_bar = max(
                worst_group["metric_bars"], key=lambda b: b["deviation"]
            )
            worst_metric_label = worst_metric_bar["label"]
            worst_metric_value = worst_metric_bar["value"]
    elif not valid_groups:
        worst_group_label = "None (All cohorts suppressed)"
    else:
        worst_group_label = "None (All groups within tolerance)"

    # Card 3 displays the headline disparity from Table 1 if present
    # (worst_is_overall = True), otherwise falls back to Table 2 worst metric.
    if headline_metric_label is not None:
        display_metric_label = headline_metric_label
        display_metric_value = headline_metric_value
        worst_is_overall = True
    else:
        display_metric_label = worst_metric_label
        display_metric_value = worst_metric_value
        worst_is_overall = False

    return {
        "total_subgroups": len(groups),
        "valid_subgroups": len(valid_groups),
        "insufficient_count": len(insufficient_groups),
        "flagged_significant_count": len(flagged_significant),
        "flagged_breach_count": len(flagged_breach_groups),
        "flagged_metric_instances_count": flagged_metric_instances,
        "flagged_metric_breach_count": flagged_metric_breach_count,
        "worst_group_label": worst_group_label,
        "worst_metric_label": display_metric_label,
        "worst_metric_value": display_metric_value,
        "worst_is_overall": worst_is_overall,
        "headline_metric_label": headline_metric_label,
        "headline_metric_value": headline_metric_value,
    }
