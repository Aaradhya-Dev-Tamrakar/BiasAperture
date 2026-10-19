"""Cross-backend execution and divergence detection."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass

from bias_aperture.fairness.backend_adapters import AIF360Backend, FairlearnBackend
from bias_aperture.fairness.base import FairnessBackend, encode_binary_labels
from bias_aperture.schema import MetricResult

logger = logging.getLogger(__name__)


# ── Cross-Validation Orchestrator ─────────────────────────────────────


@dataclass(frozen=True, slots=True)
class DivergenceAlert:
    """Record of mathematical divergence between backends."""

    metric_name: str
    subgroup: str
    backend_a: str
    value_a: float | None
    backend_b: str
    value_b: float | None
    difference: float
    tolerance: float


class CrossValidationOrchestrator:
    """Orchestrates multi-backend execution and detects algorithmic divergence."""

    def __init__(
        self,
        backends: Sequence[FairnessBackend] | None = None,
        tolerance_difference: float = 0.05,
        tolerance_ratio: float = 0.10,
    ) -> None:
        if backends is None:
            self.backends: list[FairnessBackend] = [
                FairlearnBackend(),
                AIF360Backend(),
            ]
        else:
            self.backends = list(backends)
        self.tolerance_difference = tolerance_difference
        self.tolerance_ratio = tolerance_ratio
        self.backend_failures: dict[str, str] = {}

    def run(
        self,
        records: Sequence,
        protected_attr: str,
        n_bootstrap_resamples: int = 1000,
    ) -> tuple[list[MetricResult], list[DivergenceAlert]]:
        """Execute all backends, verify consensus, and return harmonized results.

        Parameters
        ----------
        records : Sequence[SubjectRecord]
            Validated subject records.
        protected_attr : str
            Demographic axis.
        n_bootstrap_resamples : int
            Number of bootstrap iterations (B >= 1000, NFR-002).

        Returns
        -------
        tuple[list[MetricResult], list[DivergenceAlert]]
            (canonical_results, divergence_alerts).
        """
        self.backend_failures = {}
        if not self.backends:
            return [], []

        # Validate outside backend failure isolation: invalid task input must
        # propagate to the caller rather than become an empty success report.
        encode_binary_labels(
            [r.true_label for r in records], [r.predicted_label for r in records]
        )

        backend_results: dict[str, list[MetricResult]] = {}
        for b in self.backends:
            try:
                backend_results[b.name] = b.evaluate(
                    records,
                    protected_attr,
                    n_bootstrap_resamples=n_bootstrap_resamples,
                )
                unavailable = [
                    r.adjustment_method
                    for r in backend_results[b.name]
                    if "unavailable" in (r.adjustment_method or "")
                ]
                if unavailable:
                    self.backend_failures[b.name] = str(unavailable[0])
            except Exception as exc:
                logger.error("Backend %s failed during evaluation: %s", b.name, exc)
                self.backend_failures[b.name] = str(exc)
                backend_results[b.name] = []

        canonical_backend = self.backends[0].name
        canonical_results = backend_results.get(canonical_backend, [])
        if not canonical_results or any(
            "unavailable" in (r.adjustment_method or "") for r in canonical_results
        ):
            raise RuntimeError(
                f"Canonical backend {canonical_backend} is unavailable; "
                "no audit report can be produced. Check dependencies and backend logs."
            )
        divergences: list[DivergenceAlert] = self._detect_divergences(backend_results)

        return canonical_results, divergences

    def _detect_divergences(
        self,
        backend_results: dict[str, list[MetricResult]],
    ) -> list[DivergenceAlert]:
        """Compare backend results pairwise and flag mathematical divergences.

        Extracted from `run()` so the divergence-detection logic is
        independently testable and the orchestrator's `run()` reads as
        a linear pipeline.
        """
        divergences: list[DivergenceAlert] = []
        backend_names = list(backend_results.keys())

        for i in range(len(backend_names)):
            for j in range(i + 1, len(backend_names)):
                name_a, name_b = backend_names[i], backend_names[j]
                res_a, res_b = backend_results[name_a], backend_results[name_b]

                # Map by (metric_name, subgroup)
                map_a = {(r.metric_name, r.subgroup): r for r in res_a}
                map_b = {(r.metric_name, r.subgroup): r for r in res_b}

                all_keys = set(map_a.keys()) | set(map_b.keys())
                for key in sorted(all_keys):
                    ra = map_a.get(key)
                    rb = map_b.get(key)
                    va = ra.metric_value if ra else None
                    vb = rb.metric_value if rb else None

                    if va is not None and vb is not None:
                        diff = abs(va - vb)
                        tol = (
                            self.tolerance_ratio
                            if key[0] == "disparate_impact_ratio"
                            else self.tolerance_difference
                        )
                        if diff > tol:
                            divergences.append(
                                DivergenceAlert(
                                    metric_name=key[0],
                                    subgroup=key[1],
                                    backend_a=name_a,
                                    value_a=va,
                                    backend_b=name_b,
                                    value_b=vb,
                                    difference=diff,
                                    tolerance=tol,
                                )
                            )
                    elif (
                        va is not None
                        and vb is None
                        and ra
                        and not ra.insufficient_sample
                    ) or (
                        va is None
                        and vb is not None
                        and rb
                        and not rb.insufficient_sample
                    ):
                        divergences.append(
                            DivergenceAlert(
                                metric_name=key[0],
                                subgroup=key[1],
                                backend_a=name_a,
                                value_a=va,
                                backend_b=name_b,
                                value_b=vb,
                                difference=float("nan"),
                                tolerance=0.0,
                            )
                        )

        return divergences
