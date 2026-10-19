"""Plain-language explainability and executive narrative synthesis engine (WP3).

Translates statistical demographic fairness audit metrics, confidence intervals,
and surrogate feature attributions into natural-language explanations for
non-technical stakeholders (compliance officers, legal counsel, and business owners).

Preserves Milestone M1 schema invariance and the R-015 offline contract (zero external
dependencies, pure deterministic rule-based evaluation).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from bias_aperture.report.generator import ReportContext

# Plain-language metric reference dictionary
METRIC_GLOSSARY: dict[str, dict[str, str]] = {
    "disparate_impact_ratio": {
        "title": "Disparate Impact Ratio (DIR)",
        "plain_name": "Selection Rate Ratio / 80% Rule",
        "plain_question": (
            "Are different groups selected or predicted positively at similar rates?"
        ),
        "analogy": (
            "Compares the positive prediction rate of a demographic group against the "
            "highest-selected group. Under the US EEOC 4/5ths (80%) rule, if the "
            "highest group is selected 80% of the time, all other groups should be "
            "selected at least 64% of the time (80% of 80%). A ratio below 0.80 "
            "indicates adverse impact."
        ),
        "target": "Ideal = 1.00; Safe threshold ≥ 0.80",
        "regulatory": "EEOC 4/5ths Rule / EU AI Act Annex IV §2(g)",
    },
    "demographic_parity_difference": {
        "title": "Demographic Parity Difference (DPD)",
        "plain_name": "Positive Rate Percentage Gap",
        "plain_question": (
            "What is the absolute percentage point difference in positive predictions "
            "between groups?"
        ),
        "analogy": (
            "Measures whether the model favors one group over another in raw volume of "
            "positive predictions. A difference of 0.15 means individuals from one "
            "group are 15 percentage points more likely to receive a positive "
            "prediction than individuals from another group."
        ),
        "target": "Ideal = 0.00; Safe threshold ≤ 0.10",
        "regulatory": "EU AI Act Art. 10(2)(f) / NIST AI RMF Measure 2.11",
    },
    "equalized_odds_difference": {
        "title": "Equalized Odds Difference (EOD)",
        "plain_name": "Error Rate Equality Gap",
        "plain_question": (
            "Does the model make mistakes (false positives and false negatives) at "
            "equal rates across all groups?"
        ),
        "analogy": (
            "Ensures the model is equally accurate for all demographics. It verifies "
            "that qualified individuals have an equal chance of being accepted, and "
            "unqualified individuals have an equal chance of being rejected, "
            "regardless of identity."
        ),
        "target": "Ideal = 0.00; Safe threshold ≤ 0.10",
        "regulatory": "EU AI Act Art. 10(2)(g) / NIST AI RMF Measure 2.11",
    },
    "equal_opportunity_difference": {
        "title": "Equal Opportunity Difference (EOP)",
        "plain_name": "True Positive Opportunity Gap",
        "plain_question": (
            "Do qualified individuals have an equal chance of being correctly "
            "identified across demographic backgrounds?"
        ),
        "analogy": (
            "Focuses strictly on true positive outcomes (e.g. qualified applicants or "
            "correct identity matches). A difference of 0.08 means qualified "
            "individuals in one group are 8 percentage points less likely to be "
            "correctly recognized."
        ),
        "target": "Ideal = 0.00; Safe threshold ≤ 0.10",
        "regulatory": "EU AI Act Art. 10(3) / NIST AI RMF Measure 2.11",
    },
}


@dataclass(frozen=True, slots=True)
class PlainLanguageSummary:
    """Four-pillar non-technical executive narrative container."""

    verdict_badge: str
    verdict_badge_class: str
    verdict_title: str
    verdict_narrative: str
    worst_offender_narrative: str
    surrogate_drivers_narrative: str
    sample_guard_narrative: str
    has_disparities: bool
    has_attributions: bool
    top_proxy_factors: list[tuple[str, str, float]] = field(default_factory=list)


def _humanize_feature_name(raw_name: str) -> str:
    """Convert one-hot encoded or raw feature names to readable descriptions."""
    parts = raw_name.split("_", 1)
    if len(parts) == 2:
        axis, val = parts[0].strip().title(), parts[1].strip()
        return f"{axis} ({val})"
    return raw_name.replace("_", " ").title()


def synthesize_plain_language_narrative(
    context: ReportContext,
    exec_summary: dict[str, Any],
) -> PlainLanguageSummary:
    """Synthesize a deterministic plain-language narrative from audit context."""
    flagged_sig_count: int = exec_summary.get("flagged_significant_count", 0)
    valid_subgroups: int = exec_summary.get("valid_subgroups", 0)
    insufficient_count: int = exec_summary.get("insufficient_count", 0)
    worst_group_label: str | None = exec_summary.get("worst_group_label")
    worst_metric_label: str | None = exec_summary.get("worst_metric_label")
    worst_metric_val: float | None = exec_summary.get("worst_metric_value")
    worst_is_overall: bool = exec_summary.get("worst_is_overall", False)

    # 1. Determine Verdict Level and Badge
    has_disparities = flagged_sig_count > 0
    verdict_badge = "PASS"
    verdict_badge_class = "badge-pass"

    if has_disparities:
        # Check severity of the disparity breach
        is_severe = False
        if worst_metric_val is not None:
            if worst_metric_label == "DIR" and worst_metric_val < 0.80:
                is_severe = True
            elif (
                worst_metric_label in ("DPD", "EOD", "EOP") and worst_metric_val > 0.15
            ):
                is_severe = True

        if is_severe or flagged_sig_count >= max(1, valid_subgroups // 2):
            verdict_badge = "FAIL"
            verdict_badge_class = "badge-fail"
            verdict_title = (
                "Demographic Disparity Flagged: Remediation & Review Required"
            )
        else:
            verdict_badge = "WARN"
            verdict_badge_class = "badge-warn"
            verdict_title = (
                "Marginal Disparity Observed: Supervisory Review Recommended"
            )
    else:
        verdict_badge = "PASS"
        verdict_badge_class = "badge-pass"
        verdict_title = "Within Defined Fairness Tolerances"

    # 2. Verdict Narrative
    total_audited = context.total_subjects
    model_name = context.model_name
    protected_axis = context.protected_axis.capitalize()

    if not has_disparities:
        verdict_narrative = (
            f"The audited model ({model_name}) demonstrated no statistically "
            f"significant demographic performance disparities across the "
            f"{valid_subgroups} analyzed {protected_axis} cohorts "
            f"(N={total_audited} subjects). Subgroup outcomes remained within "
            f"calibrated statistical tolerances (p ≥ 0.05)."
        )
    else:
        verdict_narrative = (
            f"The audit of {model_name} identified statistically verified "
            f"demographic disparities affecting {flagged_sig_count} of the "
            f"{valid_subgroups} evaluated {protected_axis} cohorts "
            f"(N={total_audited} subjects, statistical significance p < 0.05). "
            "These performance gaps exceed random statistical fluctuation, "
            "indicating systematic differences in model predictions."
        )

    # 3. Worst-Offender Cohort Narrative
    if worst_metric_val is not None and worst_metric_label and worst_group_label:
        if worst_metric_label == "DIR":
            val_pct = round(worst_metric_val * 100, 1)
            gap_pct = round((1.0 - worst_metric_val) * 100, 1)
            breach_text = (
                f"below the standard 80% legal threshold (a {gap_pct}% shortfall)"
                if worst_metric_val < 0.80
                else "within the 80% guideline but exhibiting observable divergence"
            )
            worst_offender_narrative = (
                f"The highest demographic divergence occurred for "
                f"{worst_group_label}, where the Disparate Impact Ratio (DIR) "
                f"was {worst_metric_val:.3f}. In plain terms, subjects in this "
                f"group received positive predictions at only {val_pct}% the rate "
                f"of the benchmark group—{breach_text}."
            )
        elif worst_metric_label == "DPD":
            diff_pct = round(worst_metric_val * 100, 1)
            worst_offender_narrative = (
                f"The largest absolute gap was observed for {worst_group_label}, "
                f"showing a Demographic Parity Difference (DPD) of "
                f"{worst_metric_val:.3f}. This reflects a {diff_pct} "
                "percentage-point gap in positive prediction rates compared to the "
                "baseline cohort."
            )
        else:
            diff_pct = round(worst_metric_val * 100, 1)
            metric_full_name = (
                "Equalized Odds" if worst_metric_label == "EOD" else "Equal Opportunity"
            )
            worst_offender_narrative = (
                f"The most substantial error rate disparity affected "
                f"{worst_group_label}, with an {metric_full_name} Difference of "
                f"{worst_metric_val:.3f}. This indicates an accuracy / error "
                f"divergence of approximately {diff_pct} percentage points "
                "relative to other demographic cohorts."
            )
        if worst_is_overall:
            worst_offender_narrative += " (Observed at the global cross-group level)."
    else:
        worst_offender_narrative = (
            "No individual subgroup exhibited statistically flagged disparity bounds."
        )

    # 4. Plain-Language Surrogate Proxy Drivers Narrative
    global_exp = context.get_global_explanation()
    has_attributions = global_exp.get("has_explanation", False)
    feature_importances: dict[str, float] = global_exp.get("feature_importances", {})
    top_factors: list[tuple[str, str, float]] = []

    if has_attributions and feature_importances:
        sorted_feats = sorted(
            feature_importances.items(), key=lambda kv: kv[1], reverse=True
        )[:3]
        for raw_name, imp in sorted_feats:
            top_factors.append((raw_name, _humanize_feature_name(raw_name), imp))

        factor_names = [f"'{h_name}'" for _, h_name, _ in top_factors]
        factors_str = ", ".join(factor_names[:2])
        if len(factor_names) > 2:
            factors_str += f", and {factor_names[2]}"

        surrogate_drivers_narrative = (
            "When evaluating which characteristics most strongly correlate with "
            "the observed classification differences, surrogate Shapley "
            f"attribution identified {factors_str} as the primary demographic "
            "proxy factors. These reflect statistical associations within the "
            "dataset rather than direct physical causation."
        )
    else:
        surrogate_drivers_narrative = (
            "Surrogate proxy attribution was not triggered because demographic "
            "disparities remained within statistical tolerances, "
            "or subject records were not supplied for secondary modeling."
        )

    # 5. Sample Size Integrity Explanation (n < 30)
    if insufficient_count > 0:
        sample_guard_narrative = (
            f"To prevent misleading claims, results for {insufficient_count} "
            "demographic cohorts were marked 'N/A' (Suppressed). In accordance "
            "with statistical integrity safeguards (NFR-003), any group with "
            "fewer than 30 subjects (n < 30) is automatically suppressed because "
            "small sample sizes yield high statistical noise and unreliable "
            "compliance conclusions."
        )
    else:
        sample_guard_narrative = (
            "All evaluated demographic cohorts met or exceeded the minimum "
            "sample size threshold (n ≥ 30 subjects per NFR-003), "
            "ensuring statistical reliability across all reported metrics."
        )

    return PlainLanguageSummary(
        verdict_badge=verdict_badge,
        verdict_badge_class=verdict_badge_class,
        verdict_title=verdict_title,
        verdict_narrative=verdict_narrative,
        worst_offender_narrative=worst_offender_narrative,
        surrogate_drivers_narrative=surrogate_drivers_narrative,
        sample_guard_narrative=sample_guard_narrative,
        has_disparities=has_disparities,
        has_attributions=has_attributions,
        top_proxy_factors=top_factors,
    )
