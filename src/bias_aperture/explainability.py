"""
Explainability and visual proxy attribution module (WP4/WP5 / Stream D).

Implements conditional SHAP feature attribution, additive Shapley surrogate
attribution, and Individual Typology Angle (ITA) skin-tone colorimetry.

Architectural Guarantees (R-012, R-013, R-014):
1. Conditional Triggering: Only executed when disparity is statistically verified
   (p < 0.05 and n >= 30).
2. Clean Schema Isolation: ExplanationResult is internal to this module,
   leaving M1 schema.py completely invariant.
3. Fallback Support: If optional deep learning / C-extension dependencies
   are absent or fail, gracefully falls back to exact linear Shapley surrogate
   attribution without crashing.
"""

from __future__ import annotations

import logging
import math
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from bias_aperture.fairness.base import encode_binary_labels
from bias_aperture.schema import (
    ALPHA,
    MIN_SUBGROUP_SAMPLE_SIZE,
    MetricResult,
    SubjectRecord,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ExplanationResult:
    """Internal explanation artifact container."""

    subgroup: str
    metric_name: str
    feature_attributions: dict[str, float] = field(default_factory=dict)
    base64_visualizations: list[str] = field(default_factory=list)
    ita_value: float | None = None
    ita_category: str | None = None
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
        if result.p_value is None or result.p_value >= ALPHA:
            return False
        return True

    def explain_disparity(
        self,
        result: MetricResult,
        image_paths: Sequence[Path | str] | None = None,
        records: Sequence[SubjectRecord] | None = None,
    ) -> ExplanationResult:
        """Generate targeted visual or proxy attribution for a flagged disparity."""
        if not self.should_explain(result):
            return ExplanationResult(
                subgroup=result.subgroup,
                metric_name=result.metric_name,
                details=(
                    "Disparity not statistically significant or sample "
                    "insufficient; explainability skipped."
                ),
            )

        # 1. If records are supplied, compute surrogate demographic Shapley attributions
        if records:
            return self.explain_surrogate(result, records)

        # 2. If records are omitted, return diagnostic status
        # (image-native SHAP deferred)
        return ExplanationResult(
            subgroup=result.subgroup,
            metric_name=result.metric_name,
            details=(
                "Surrogate explanation unavailable: subject records were not supplied. "
                "Image-native spatial SHAP is deferred to v2."
            ),
        )

    def explain_surrogate(
        self,
        result: MetricResult,
        records: Sequence[SubjectRecord],
    ) -> ExplanationResult:
        """Compute exact additive Shapley attributions over demographic proxy axes.

        Uses the additive property: phi_i = w_i * (x_i - E[x_i]) for linear surrogate
        models, quantifying how protected and proxy axes drive predictions.
        """
        try:
            import pandas as pd
            from sklearn.linear_model import LogisticRegression

            # Extract demographic feature matrix
            r_list = [r.race for r in records]
            g_list = [r.gender for r in records]
            a_list = [r.age for r in records]
            _, y_pred = encode_binary_labels(
                [r.true_label for r in records], [r.predicted_label for r in records]
            )

            df = pd.DataFrame({"race": r_list, "gender": g_list, "age": a_list})
            df_dummies = pd.get_dummies(df, drop_first=False)
            X = df_dummies.values.astype(float)
            feature_names = list(df_dummies.columns)

            if len(np.unique(y_pred)) < 2 or X.shape[0] < 5:
                return ExplanationResult(
                    subgroup=result.subgroup,
                    metric_name=result.metric_name,
                    details="Insufficient variance for surrogate explanation.",
                )

            # Fit surrogate model
            clf = LogisticRegression(max_iter=200).fit(X, y_pred)
            weights = clf.coef_[0]
            baseline = X.mean(axis=0)

            # Additive Shapley values per feature
            shapley_values = (X - baseline) * weights
            mean_importance = np.abs(shapley_values).mean(axis=0)

            attributions = {
                name: float(imp)
                for name, imp in zip(feature_names, mean_importance, strict=False)
            }

            # Sort by attribution magnitude
            sorted_attr = dict(
                sorted(attributions.items(), key=lambda item: item[1], reverse=True)[
                    :10
                ]
            )

            return ExplanationResult(
                subgroup=result.subgroup,
                metric_name=result.metric_name,
                feature_attributions=sorted_attr,
                details=(
                    f"Surrogate Shapley attribution computed across {len(records)} "
                    f"subjects for {result.subgroup}. These demographic surrogate "
                    "associations summarize prediction log-odds across the full audit; "
                    "they do not explain images, causation, or the disparity itself."
                ),
            )
        except Exception as exc:
            logger.warning("Surrogate explainability encountered error: %s", exc)
            return ExplanationResult(
                subgroup=result.subgroup,
                metric_name=result.metric_name,
                details=f"Surrogate explanation unavailable: {exc}",
            )


def _rgb_to_lab(rgb_patch: np.ndarray) -> tuple[float, float]:
    """Convert the mean RGB colour of a patch to CIELAB L* and b*."""
    rgb = np.asarray(rgb_patch, dtype=float)
    if rgb.ndim == 1:
        if rgb.size != 3:
            raise ValueError("rgb_patch must contain three channels")
        rgb = rgb.reshape(1, 1, 3)
    if rgb.ndim != 3 or rgb.shape[-1] != 3:
        raise ValueError("rgb_patch must have shape (height, width, 3)")
    values = np.clip(rgb.mean(axis=(0, 1)) / 255.0, 0.0, 1.0)
    linear = np.where(
        values <= 0.04045,
        values / 12.92,
        ((values + 0.055) / 1.055) ** 2.4,
    )
    xyz = np.array(
        [
            [0.4124564, 0.3575761, 0.1804375],
            [0.2126729, 0.7151522, 0.0721750],
            [0.0193339, 0.1191920, 0.9503041],
        ]
    ) @ linear
    reference = xyz / np.array([0.95047, 1.0, 1.08883])
    delta = 6 / 29
    transformed = np.where(
        reference > delta**3,
        np.cbrt(reference),
        reference / (3 * delta**2) + 4 / 29,
    )
    return float(116 * transformed[1] - 16), float(
        200 * (transformed[2] - transformed[1])
    )


def compute_ita(
    rgb_patch: float | Sequence[float] | np.ndarray, b_star: float | None = None
) -> float:
    """Compute Individual Typology Angle (ITA) skin-tone colorimetry in degrees (R-013).

    ITA = arctan((L* - 50) / b*) * (180 / π)

    Parameters
    ----------
    rgb_patch : float or array-like
        Either a CIELAB L* value when ``b_star`` is supplied (legacy API),
        or an RGB patch with shape ``(height, width, 3)`` and values in
        ``[0, 255]``.
    b_star : float, optional
        CIELAB b* value for the legacy ``compute_ita(l_star, b_star)`` API.

    Returns
    -------
    float
        ITA in degrees.
    """
    if b_star is None:
        l_star, b_value = _rgb_to_lab(np.asarray(rgb_patch))
    else:
        l_star, b_value = float(rgb_patch), float(b_star)
    if b_value == 0:
        return 90.0 if l_star >= 50 else -90.0
    rad = math.atan((l_star - 50.0) / b_value)
    return float(rad * (180.0 / math.pi))


def classify_ita(ita_value: float) -> str:
    """Map an ITA value to the six Fitzpatrick skin-tone categories."""
    if ita_value > 55:
        return "Very Light"
    if ita_value > 41:
        return "Light"
    if ita_value > 28:
        return "Intermediate"
    if ita_value > 10:
        return "Tan"
    if ita_value > -30:
        return "Brown"
    return "Dark"


def render_spatial_svg(
    attribution_map: np.ndarray,
    ita_value: float | None = None,
    ita_category: str | None = None,
) -> str:
    """Render an attribution grid as standalone inline SVG.

    The output contains no external references and is safe to embed in an
    air-gapped HTML dossier.
    """
    values = np.asarray(attribution_map, dtype=float)
    if values.ndim != 2 or values.size == 0:
        raise ValueError("attribution_map must be a non-empty two-dimensional array")
    peak = float(np.max(np.abs(values))) or 1.0
    cells: list[str] = []
    for row, col in np.ndindex(values.shape):
        normalized = float(values[row, col] / peak)
        opacity = min(1.0, max(0.08, abs(normalized)))
        color = "#b91c1c" if normalized >= 0 else "#1d4ed8"
        cells.append(
            f'<rect x="{col}" y="{row}" width="1" height="1" '
            f'fill="{color}" opacity="{opacity:.3f}"/>'
        )
    label = ""
    if ita_value is not None:
        category = ita_category or classify_ita(ita_value)
        label = (
            f'<text x="0" y="{values.shape[0] + 1}" font-size="1.5">'
            f'ITA {ita_value:.1f} deg ({category})</text>'
        )
    return (
        f'<svg class="spatial-attribution" xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {values.shape[1]} {values.shape[0] + (2 if label else 0)}" '
        f'role="img" aria-label="Spatial attribution heatmap">'
        + "".join(cells)
        + label
        + "</svg>"
    )


class SpatialShapEngine:
    """Compute gated image attributions and fall back to the surrogate engine."""

    def __init__(
        self,
        max_exemplars: int = 8,
        disparity_threshold: float = 0.1,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.max_exemplars = max_exemplars
        self.disparity_threshold = disparity_threshold
        self.timeout_seconds = timeout_seconds
        self.surrogate = ShapExplainerEngine(max_exemplars=max_exemplars)

    def is_flagged(self, result: MetricResult) -> bool:
        """Return whether the metric is eligible for compute-heavy spatial SHAP."""
        return (
            self.surrogate.should_explain(result)
            and result.metric_value is not None
            and abs(result.metric_value) >= self.disparity_threshold
        )

    @staticmethod
    def gpu_available() -> bool:
        try:
            import torch

            return bool(torch.cuda.is_available())
        except (ImportError, RuntimeError):
            return False

    def explain_disparity(
        self,
        result: MetricResult,
        image_paths: Sequence[Path | str] | None = None,
        records: Sequence[SubjectRecord] | None = None,
        predict: Callable[[np.ndarray], np.ndarray] | None = None,
    ) -> ExplanationResult:
        """Run spatial SHAP only for flagged disparities, with safe fallback."""
        if not self.surrogate.should_explain(result):
            return ExplanationResult(
                subgroup=result.subgroup,
                metric_name=result.metric_name,
                details=(
                    "Disparity not statistically significant or sample "
                    "insufficient; explainability skipped."
                ),
            )
        if not self.is_flagged(result):
            return self._fallback(
                result, records, "Disparity below spatial SHAP threshold."
            )
        try:
            paths = [Path(path) for path in (image_paths or [])]
            if not paths or any(not path.is_file() for path in paths):
                raise FileNotFoundError("one or more image paths could not be resolved")
            if not self.gpu_available():
                raise RuntimeError("GPU unavailable for spatial SHAP")
            if predict is None:
                raise ValueError("a prediction callable is required for spatial SHAP")
            executor = ThreadPoolExecutor(max_workers=1)
            future = executor.submit(self._run_spatial_shap, paths, predict)
            try:
                attribution_map, ita_value = future.result(
                    timeout=self.timeout_seconds
                )
            finally:
                executor.shutdown(wait=False, cancel_futures=True)
            category = classify_ita(ita_value) if ita_value is not None else None
            return ExplanationResult(
                subgroup=result.subgroup,
                metric_name=result.metric_name,
                base64_visualizations=[
                    render_spatial_svg(attribution_map, ita_value, category)
                ],
                ita_value=ita_value,
                ita_category=category,
                details="Spatial SHAP attribution computed with an inline SVG heatmap.",
            )
        except (
            FileNotFoundError,
            ImportError,
            RuntimeError,
            TimeoutError,
            ValueError,
            OSError,
        ) as exc:
            logger.info(
                "Spatial SHAP unavailable; using surrogate attribution: %s", exc
            )
            return self._fallback(
                result, records, "Spatial SHAP unavailable; surrogate attribution used."
            )

    def _fallback(
        self,
        result: MetricResult,
        records: Sequence[SubjectRecord] | None,
        reason: str,
    ) -> ExplanationResult:
        if records:
            fallback = self.surrogate.explain_surrogate(result, records)
            return ExplanationResult(
                subgroup=fallback.subgroup,
                metric_name=fallback.metric_name,
                feature_attributions=fallback.feature_attributions,
                proxy_warning=True,
                details=f"{reason} {fallback.details}",
            )
        return ExplanationResult(
            subgroup=result.subgroup,
            metric_name=result.metric_name,
            proxy_warning=True,
            details=(
                f"{reason} Subject records were not supplied for surrogate "
                "attribution."
            ),
        )

    def _run_spatial_shap(
        self,
        paths: Sequence[Path],
        predict: Callable[[np.ndarray], np.ndarray],
    ) -> tuple[np.ndarray, float | None]:
        from PIL import Image

        images = [np.asarray(Image.open(path).convert("RGB")) for path in paths]
        batch = np.stack(images[: self.max_exemplars])
        import shap

        masker = shap.maskers.Image("blur(16,16)", batch[0].shape)
        explainer = shap.PartitionExplainer(predict, masker)
        explanation: Any = explainer(batch, max_evals=100)
        values = np.asarray(explanation.values)
        spatial = np.mean(np.abs(values), axis=tuple(range(values.ndim - 3)))
        if spatial.ndim == 3:
            spatial = np.mean(spatial, axis=-1)
        ita = compute_ita(batch[0])
        return np.asarray(spatial), ita


# Canonical alias reflecting diagnostic surrogate attribution capability
SurrogateAttributionEngine = ShapExplainerEngine
