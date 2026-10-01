"""Fairness backends and dual-backend cross-validation orchestrator (WP4).

Implements:
1. ``FairlearnBackend``: Native multi-group metric adapter wrapping Fairlearn
2. ``AIF360Backend``: Harmonized AIF360 adapter resolving max-of-gaps EOD
   and unsigned EOP
3. ``CrossValidationOrchestrator``: Strategy pattern orchestrator verifying
   multi-backend consensus

Helper decomposition (R1 modularity):
- ``_make_insufficient_result``: Factory for NFR-003 flagged rows
- ``_make_*_fn``: Bootstrap metric-function closure factories
- ``_build_summary_row``: Single global summary MetricResult builder
- ``_build_subgroup_rows``: Per-demographic-group MetricResult builder
- ``_build_core_metric_results``: Thin orchestrator wiring helpers together
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Sequence
from dataclasses import dataclass

import numpy as np

from bias_aperture.fairness.base import (
    EligibilityReport,
    FairnessBackend,
    eligible_groups,
)
from bias_aperture.fairness.metrics import (
    compute_group_rates,
    demographic_parity_difference,
    equal_opportunity_difference,
    equalized_odds_difference,
    symmetric_disparate_impact_ratio,
)
from bias_aperture.fairness.statistics import (
    adjust_family_pvalues,
    compute_metric_specific_test,
    compute_stratified_bootstrap_ci,
    compute_subgroup_bootstrap_ci,
)
from bias_aperture.schema import (
    MIN_SUBGROUP_SAMPLE_SIZE,
    MetricResult,
)

logger = logging.getLogger(__name__)


# ── MetricResult Factory Helpers ──────────────────────────────────────


def _make_insufficient_result(
    metric_name: str,
    subgroup: str,
    sample_size: int,
    **kwargs: object,
) -> MetricResult:
    """Factory for MetricResult rows flagged as insufficient under NFR-003.

    Centralises the pattern of setting metric_value/ci/p_value to None
    with insufficient_sample=True, eliminating duplicated construction blocks.
    """
    return MetricResult(
        metric_name=metric_name,  # type: ignore[arg-type]
        subgroup=subgroup,
        subgroup_sample_size=sample_size,
        metric_value=None,
        ci_lower=None,
        ci_upper=None,
        p_value=None,
        raw_p_value=None,
        insufficient_sample=True,
        **kwargs,  # type: ignore[arg-type]
    )


# ── Bootstrap Metric-Function Closure Factories ───────────────────────
# Each factory returns a closure that captures a specific eligible-group
# list so the bootstrap resampler only evaluates groups that passed
# NFR-003 screening.


def _make_dpd_fn(
    dpd_groups: list[str],
) -> Callable[[np.ndarray, np.ndarray, np.ndarray], float]:
    """Return a bootstrap-compatible DPD metric function."""

    def dpd_fn(yt: np.ndarray, yp: np.ndarray, s: np.ndarray) -> float:
        rates = compute_group_rates(yt, yp, s)
        sub_rates = {
            g: float(rates[g]["selection_rate"]) for g in dpd_groups if g in rates
        }
        if len(sub_rates) < 2:
            return 0.0
        return demographic_parity_difference(sub_rates)

    return dpd_fn


def _make_eod_fn(
    eod_groups: list[str],
) -> Callable[[np.ndarray, np.ndarray, np.ndarray], float]:
    """Return a bootstrap-compatible EOD metric function."""

    def eod_fn(yt: np.ndarray, yp: np.ndarray, s: np.ndarray) -> float:
        rates = compute_group_rates(yt, yp, s)
        tpr_map = {
            g: float(rates[g]["tpr"])
            for g in eod_groups
            if g in rates and rates[g]["tpr"] is not None
        }
        fpr_map = {
            g: float(rates[g]["fpr"])
            for g in eod_groups
            if g in rates and rates[g]["fpr"] is not None
        }
        if len(tpr_map) < 2 or len(fpr_map) < 2:
            return 0.0
        return equalized_odds_difference(tpr_map, fpr_map)

    return eod_fn


def _make_eop_fn(
    eop_groups: list[str],
) -> Callable[[np.ndarray, np.ndarray, np.ndarray], float]:
    """Return a bootstrap-compatible EOP metric function."""

    def eop_fn(yt: np.ndarray, yp: np.ndarray, s: np.ndarray) -> float:
        rates = compute_group_rates(yt, yp, s)
        tpr_map = {
            g: float(rates[g]["tpr"])
            for g in eop_groups
            if g in rates and rates[g]["tpr"] is not None
        }
        if len(tpr_map) < 2:
            return 0.0
        return equal_opportunity_difference(tpr_map)

    return eop_fn


def _make_dir_fn(
    dir_groups: list[str],
) -> Callable[[np.ndarray, np.ndarray, np.ndarray], float]:
    """Return a bootstrap-compatible DIR metric function."""

    def dir_fn(yt: np.ndarray, yp: np.ndarray, s: np.ndarray) -> float:
        rates = compute_group_rates(yt, yp, s)
        sub_rates = {
            g: float(rates[g]["selection_rate"]) for g in dir_groups if g in rates
        }
        if len(sub_rates) < 2:
            return 1.0
        val, _ = symmetric_disparate_impact_ratio(sub_rates)
        return val

    return dir_fn


# ── Summary Row Builder ───────────────────────────────────────────────


def _build_summary_row(
    metric_name: str,
    eligible_grps: list[str],
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sensitive: np.ndarray,
    group_rates: dict[str, dict[str, float | None]],
    metric_fn: Callable[[np.ndarray, np.ndarray, np.ndarray], float],
    compute_value_fn: Callable[[dict[str, dict[str, float | None]], list[str]], float],
    n_bootstrap_resamples: int,
    total_n: int,
) -> MetricResult:
    """Build a single global summary MetricResult row for one Core Four metric.

    Handles eligibility gating, hypothesis testing, bootstrap CI, and
    point-estimate computation for the cross-group (subgroup='ALL') row.
    """
    if len(eligible_grps) < 2:
        return _make_insufficient_result(metric_name, "ALL", total_n)

    eligible_mask = np.isin(sensitive, eligible_grps)
    test = compute_metric_specific_test(
        metric_name,
        y_true[eligible_mask],
        y_pred[eligible_mask],
        sensitive[eligible_mask],
    )
    metric_value = compute_value_fn(group_rates, eligible_grps)
    ci_low, ci_high = compute_stratified_bootstrap_ci(
        y_true, y_pred, sensitive, metric_fn, n_resamples=n_bootstrap_resamples
    )
    return MetricResult(
        metric_name=metric_name,  # type: ignore[arg-type]
        subgroup="ALL",
        subgroup_sample_size=total_n,
        metric_value=metric_value,
        ci_lower=ci_low,
        ci_upper=ci_high,
        p_value=test.raw_p,
        raw_p_value=test.raw_p,
        hypothesis_family=test.hypothesis_family,
        insufficient_sample=False,
    )


# ── Per-Subgroup Row Builder ──────────────────────────────────────────


def _build_subgroup_rows(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sensitive: np.ndarray,
    group_rates: dict[str, dict[str, float | None]],
    eligibility: dict[str, EligibilityReport],
    total_n: int,
) -> list[MetricResult]:
    """Build per-subgroup MetricResult rows for all Core Four metrics.

    For each demographic group, computes the group-vs-global disparity
    for DPD, EOP, EOD, and DIR (where eligible), and returns the
    corresponding MetricResult rows with hypothesis tests and bootstrap CIs.
    """
    results: list[MetricResult] = []
    all_groups = sorted(eligibility.keys())

    for g in all_groups:
        rep = eligibility[g]
        n_grp = rep.n

        if n_grp < MIN_SUBGROUP_SAMPLE_SIZE:
            for m_name in (
                "demographic_parity_difference",
                "equalized_odds_difference",
                "equal_opportunity_difference",
                "disparate_impact_ratio",
            ):
                results.append(_make_insufficient_result(m_name, g, n_grp))
            continue

        rest_sensitive = np.where(sensitive == g, g, "REST")
        sel_rate = float(group_rates[g]["selection_rate"])
        global_sel_rate = float(y_pred.mean()) if total_n > 0 else 0.0

        # Subgroup DPD
        grp_dpd = abs(sel_rate - global_sel_rate)
        grp_dpd_test = compute_metric_specific_test(
            "demographic_parity_difference", y_true, y_pred, rest_sensitive
        )
        grp_dpd_ci = compute_subgroup_bootstrap_ci(
            y_true, y_pred, sensitive, g, "demographic_parity_difference"
        )
        results.append(
            MetricResult(
                metric_name="demographic_parity_difference",
                subgroup=g,
                subgroup_sample_size=n_grp,
                metric_value=grp_dpd,
                ci_lower=grp_dpd_ci[0],
                ci_upper=grp_dpd_ci[1],
                p_value=grp_dpd_test.raw_p,
                raw_p_value=grp_dpd_test.raw_p,
                hypothesis_family=grp_dpd_test.hypothesis_family,
                insufficient_sample=False,
            )
        )

        # Subgroup EOP
        tpr = group_rates[g]["tpr"]
        if rep.eligible_eop and tpr is not None:
            pos_total = (y_true == 1).sum()
            global_tpr = float(y_pred[y_true == 1].mean()) if pos_total > 0 else 0.0
            grp_eop = abs(float(tpr) - global_tpr)
            grp_eop_test = compute_metric_specific_test(
                "equal_opportunity_difference", y_true, y_pred, rest_sensitive
            )
            grp_eop_ci = compute_subgroup_bootstrap_ci(
                y_true, y_pred, sensitive, g, "equal_opportunity_difference"
            )
            results.append(
                MetricResult(
                    metric_name="equal_opportunity_difference",
                    subgroup=g,
                    subgroup_sample_size=n_grp,
                    metric_value=grp_eop,
                    ci_lower=grp_eop_ci[0],
                    ci_upper=grp_eop_ci[1],
                    p_value=grp_eop_test.raw_p,
                    raw_p_value=grp_eop_test.raw_p,
                    hypothesis_family=grp_eop_test.hypothesis_family,
                    insufficient_sample=False,
                )
            )
        else:
            results.append(
                _make_insufficient_result("equal_opportunity_difference", g, n_grp)
            )

        # Subgroup EOD
        fpr = group_rates[g]["fpr"]
        if rep.eligible_eod and tpr is not None and fpr is not None:
            pos_total = (y_true == 1).sum()
            neg_total = (y_true == 0).sum()
            global_tpr = float(y_pred[y_true == 1].mean()) if pos_total > 0 else 0.0
            global_fpr = float(y_pred[y_true == 0].mean()) if neg_total > 0 else 0.0
            grp_eod = max(abs(float(tpr) - global_tpr), abs(float(fpr) - global_fpr))
            grp_eod_test = compute_metric_specific_test(
                "equalized_odds_difference", y_true, y_pred, rest_sensitive
            )
            grp_eod_ci = compute_subgroup_bootstrap_ci(
                y_true, y_pred, sensitive, g, "equalized_odds_difference"
            )
            results.append(
                MetricResult(
                    metric_name="equalized_odds_difference",
                    subgroup=g,
                    subgroup_sample_size=n_grp,
                    metric_value=grp_eod,
                    ci_lower=grp_eod_ci[0],
                    ci_upper=grp_eod_ci[1],
                    p_value=grp_eod_test.raw_p,
                    raw_p_value=grp_eod_test.raw_p,
                    hypothesis_family=grp_eod_test.hypothesis_family,
                    insufficient_sample=False,
                )
            )
        else:
            results.append(
                _make_insufficient_result("equalized_odds_difference", g, n_grp)
            )

        # Subgroup DIR
        if global_sel_rate > 0:
            grp_dir = min(sel_rate, global_sel_rate) / max(sel_rate, global_sel_rate)
        else:
            grp_dir = 1.0
        grp_dir_test = compute_metric_specific_test(
            "disparate_impact_ratio", y_true, y_pred, rest_sensitive
        )
        grp_dir_ci = compute_subgroup_bootstrap_ci(
            y_true, y_pred, sensitive, g, "disparate_impact_ratio"
        )
        results.append(
            MetricResult(
                metric_name="disparate_impact_ratio",
                subgroup=g,
                subgroup_sample_size=n_grp,
                metric_value=grp_dir,
                ci_lower=grp_dir_ci[0],
                ci_upper=grp_dir_ci[1],
                p_value=grp_dir_test.raw_p,
                raw_p_value=grp_dir_test.raw_p,
                hypothesis_family=grp_dir_test.hypothesis_family,
                insufficient_sample=False,
            )
        )

    return results


# ── Core Metric Results Orchestrator ──────────────────────────────────


def _build_core_metric_results(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sensitive: np.ndarray,
    group_rates: dict[str, dict[str, float | None]],
    eligibility: dict[str, EligibilityReport],
    n_bootstrap_resamples: int = 1000,
) -> list[MetricResult]:
    """Assemble canonical MetricResult list from group rate matrices.

    Orchestrates _build_summary_row (global rows) and
    _build_subgroup_rows (per-group rows), then applies Holm-Bonferroni
    FWER p-value adjustment across hypothesis families.
    """
    total_n = len(y_true)

    # Eligible groups per metric
    dpd_groups = eligible_groups(eligibility, "demographic_parity_difference")
    eod_groups = eligible_groups(eligibility, "equalized_odds_difference")
    eop_groups = eligible_groups(eligibility, "equal_opportunity_difference")
    dir_groups = eligible_groups(eligibility, "disparate_impact_ratio")

    # Bootstrap metric-function closures
    dpd_fn = _make_dpd_fn(dpd_groups)
    eod_fn = _make_eod_fn(eod_groups)
    eop_fn = _make_eop_fn(eop_groups)
    dir_fn = _make_dir_fn(dir_groups)

    # Point-estimate computation functions for summary rows
    def _dpd_val(gr: dict[str, dict[str, float | None]], grps: list[str]) -> float:
        return demographic_parity_difference(
            {g: float(gr[g]["selection_rate"]) for g in grps}
        )

    def _eod_val(gr: dict[str, dict[str, float | None]], grps: list[str]) -> float:
        tpr_map = {g: float(gr[g]["tpr"]) for g in grps if gr[g]["tpr"] is not None}
        fpr_map = {g: float(gr[g]["fpr"]) for g in grps if gr[g]["fpr"] is not None}
        if len(tpr_map) < 2 or len(fpr_map) < 2:
            return 0.0
        return equalized_odds_difference(tpr_map, fpr_map)

    def _eop_val(gr: dict[str, dict[str, float | None]], grps: list[str]) -> float:
        tpr_map = {g: float(gr[g]["tpr"]) for g in grps if gr[g]["tpr"] is not None}
        if len(tpr_map) < 2:
            return 0.0
        return equal_opportunity_difference(tpr_map)

    def _dir_val(gr: dict[str, dict[str, float | None]], grps: list[str]) -> float:
        val, _ = symmetric_disparate_impact_ratio(
            {g: float(gr[g]["selection_rate"]) for g in grps}
        )
        return val

    # ── Global Summary Rows ────────────────────────────────────────
    results: list[MetricResult] = []

    summary_specs: list[tuple[str, list[str], Callable, Callable]] = [
        ("demographic_parity_difference", dpd_groups, dpd_fn, _dpd_val),
        ("equalized_odds_difference", eod_groups, eod_fn, _eod_val),
        ("equal_opportunity_difference", eop_groups, eop_fn, _eop_val),
        ("disparate_impact_ratio", dir_groups, dir_fn, _dir_val),
    ]

    for metric_name, grps, boot_fn, val_fn in summary_specs:
        results.append(
            _build_summary_row(
                metric_name,
                grps,
                y_true,
                y_pred,
                sensitive,
                group_rates,
                boot_fn,
                val_fn,
                n_bootstrap_resamples,
                total_n,
            )
        )

    # ── Per-Subgroup Rows ──────────────────────────────────────────
    results.extend(
        _build_subgroup_rows(
            y_true, y_pred, sensitive, group_rates, eligibility, total_n
        )
    )

    return adjust_family_pvalues(results)


# ── Native Pure-Math / Fairlearn Backend ──────────────────────────────


class FairlearnBackend(FairnessBackend):
    """Fairness backend utilizing Fairlearn-aligned metric definitions."""

    @property
    def name(self) -> str:
        return "fairlearn"

    def _evaluate_core_four(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        sensitive: np.ndarray,
        eligibility: dict[str, EligibilityReport],
        n_bootstrap_resamples: int = 1000,
    ) -> list[MetricResult]:
        """Compute Core Four metrics with statistical confidence bounds."""
        group_rates = compute_group_rates(y_true, y_pred, sensitive)
        return _build_core_metric_results(
            y_true,
            y_pred,
            sensitive,
            group_rates,
            eligibility,
            n_bootstrap_resamples=n_bootstrap_resamples,
        )


# ── AIF360 Harmonized Adapter Backend ────────────────────────────────


class AIF360Backend(FairnessBackend):
    """AIF360 backend harmonized to compute max-of-gaps EOD and unsigned EOP.

    Directly leverages AIF360's BinaryLabelDataset and ClassificationMetric
    to compute subgroup metrics, applying BiasAperture's mathematical harmonization
    contracts (R-005 through R-010) for cross-validation consistency.
    """

    @property
    def name(self) -> str:
        return "aif360"

    def _evaluate_core_four(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        sensitive: np.ndarray,
        eligibility: dict[str, EligibilityReport],
        n_bootstrap_resamples: int = 1000,
    ) -> list[MetricResult]:
        """Compute Core Four metrics using native AIF360 dataset & metrics."""
        try:
            import pandas as pd
            from aif360.datasets import BinaryLabelDataset
            from aif360.metrics import ClassificationMetric

            # Encode sensitive attributes to numeric codes for AIF360
            unique_groups, group_indices = np.unique(sensitive, return_inverse=True)
            df_true = pd.DataFrame({"prot_attr": group_indices, "label": y_true})
            df_pred = pd.DataFrame({"prot_attr": group_indices, "label": y_pred})

            bld_true = BinaryLabelDataset(
                df=df_true,
                label_names=["label"],
                protected_attribute_names=["prot_attr"],
                favorable_label=1,
                unfavorable_label=0,
            )
            bld_pred = BinaryLabelDataset(
                df=df_pred,
                label_names=["label"],
                protected_attribute_names=["prot_attr"],
                favorable_label=1,
                unfavorable_label=0,
            )

            # Extract per-group selection rate, TPR, and FPR using ClassificationMetric
            group_rates: dict[str, dict[str, float | None]] = {}
            for g_code, g_name in enumerate(unique_groups):
                # Unprivileged: current group; Privileged: all other groups
                unprivileged = [{"prot_attr": g_code}]
                privileged = [
                    {"prot_attr": c} for c in range(len(unique_groups)) if c != g_code
                ]

                # If only 1 group exists, privileged cannot be formed
                if not privileged:
                    privileged = unprivileged

                cm = ClassificationMetric(
                    bld_true,
                    bld_pred,
                    unprivileged_groups=unprivileged,
                    privileged_groups=privileged,
                )

                sel_rate = float(cm.selection_rate(privileged=False))
                try:
                    raw_tpr = cm.true_positive_rate(privileged=False)
                    tpr_val: float | None = float(raw_tpr)
                    if np.isnan(tpr_val):
                        tpr_val = None
                except Exception:
                    tpr_val = None

                try:
                    raw_fpr = cm.false_positive_rate(privileged=False)
                    fpr_val: float | None = float(raw_fpr)
                    if np.isnan(fpr_val):
                        fpr_val = None
                except Exception:
                    fpr_val = None

                group_rates[str(g_name)] = {
                    "selection_rate": sel_rate,
                    "tpr": tpr_val,
                    "fpr": fpr_val,
                }

        except Exception as exc:
            logger.error(
                "AIF360 native execution failed (%s); marking backend unavailable.",
                exc,
            )
            all_groups = sorted(eligibility.keys())
            total_n = len(y_true)
            return self._unavailable_results(all_groups, total_n, str(exc))

        return _build_core_metric_results(
            y_true,
            y_pred,
            sensitive,
            group_rates,
            eligibility,
            n_bootstrap_resamples=n_bootstrap_resamples,
        )

    def _unavailable_results(
        self, all_groups: Sequence[str], total_n: int, reason: str
    ) -> list[MetricResult]:
        """Produce unavailable MetricResults when AIF360 execution fails."""
        results: list[MetricResult] = []
        for m_name in (
            "demographic_parity_difference",
            "equalized_odds_difference",
            "equal_opportunity_difference",
            "disparate_impact_ratio",
        ):
            # Global row
            results.append(
                _make_insufficient_result(
                    m_name,
                    "ALL",
                    total_n,
                    adjustment_method=f"aif360_unavailable: {reason}",
                )
            )
            # Subgroup rows
            for g in all_groups:
                results.append(
                    _make_insufficient_result(
                        m_name,
                        g,
                        0,
                        adjustment_method=f"aif360_unavailable: {reason}",
                    )
                )
        return results


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
        if not self.backends:
            return [], []

        backend_results: dict[str, list[MetricResult]] = {}
        for b in self.backends:
            try:
                backend_results[b.name] = b.evaluate(
                    records,
                    protected_attr,
                    n_bootstrap_resamples=n_bootstrap_resamples,
                )
            except Exception as exc:
                logger.error("Backend %s failed during evaluation: %s", b.name, exc)
                backend_results[b.name] = []

        canonical_backend = self.backends[0].name
        canonical_results = backend_results.get(canonical_backend, [])
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
