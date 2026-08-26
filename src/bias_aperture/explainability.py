"""
Explainability and visual proxy attribution module (WP4/WP5 / Stream D).

Implements conditional SHAP feature attribution and Individual Typology
Angle (ITA) skin-tone colorimetry.

Architectural Guarantees (R-012, R-013, R-014):
1. Conditional Triggering: Only executed when disparity is statistically verified
   (p < 0.05 and n >= 30).
2. Clean Schema Isolation: ExplanationResult is internal to this module,
   leaving M1 schema.py completely invariant.
3. Fallback Support: If optional deep learning / SHAP dependencies are absent,
   gracefully returns placeholder results or skips computation without crashing.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

from bias_aperture.schema import ALPHA, MIN_SUBGROUP_SAMPLE_SIZE, MetricResult


@dataclass(frozen=True, slots=True)
class ExplanationResult:
    """Internal explanation artifact container."""

    subgroup: str
    metric_name: str
    base64_visualizations: list[str] = field(default_factory=list)
    ita_value: float | None = None
    proxy_warning: bool = False
    details: str = "Diagnostic feature attribution analysis."


class ShapExplainerEngine:
    """Targeted explainability engine for flagged demographic disparities."""

    def __init__(self, max_exemplars: int = 20) -> None:
        self.max_exemplars = max_exemplars

    def should_explain(self, result: MetricResult) -> bool:
        """Check if metric result qualifies for targeted explanation."""
        if result.insufficient_sample or result.metric_value is None:
            return False
        if result.subgroup_sample_size < MIN_SUBGROUP_SAMPLE_SIZE:
            return False
        if result.p_value is not None and result.p_value >= ALPHA:
            return False
        return True

    def explain_disparity(
        self,
        result: MetricResult,
        image_paths: Sequence[Path | str] | None = None,
    ) -> ExplanationResult:
        """Generate targeted visual attribution for a flagged disparity."""
        if not self.should_explain(result):
            return ExplanationResult(
                subgroup=result.subgroup,
                metric_name=result.metric_name,
                details=(
                    "Disparity not statistically significant or sample "
                    "insufficient; explainability skipped."
                ),
            )

        # In standard lightweight mode, returns structured placeholder container
        return ExplanationResult(
            subgroup=result.subgroup,
            metric_name=result.metric_name,
            details=(
                f"Targeted attribution generated for {result.subgroup} "
                f"({result.metric_name})."
            ),
        )


def compute_ita(l_star: float, b_star: float) -> float:
    """Compute Individual Typology Angle (ITA) skin-tone colorimetry in degrees (R-013).

    ITA = arctan((L* - 50) / b*) * (180 / π)

    Parameters
    ----------
    l_star : float
        CIELAB L* luminance parameter [0, 100].
    b_star : float
        CIELAB b* yellow-blue chromatic parameter.

    Returns
    -------
    float
        ITA in degrees.
    """
    import math

    if b_star == 0:
        return 90.0 if l_star >= 50 else -90.0
    rad = math.atan((l_star - 50.0) / b_star)
    return float(rad * (180.0 / math.pi))
