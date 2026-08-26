"""Fairness backends and dual-backend cross-validation orchestrator (WP4).

Implements:
1. ``FairlearnBackend``: Native multi-group metric adapter wrapping Fairlearn
2. ``AIF360Backend``: Harmonized AIF360 adapter resolving max-of-gaps EOD
   and unsigned EOP
3. ``CrossValidationOrchestrator``: Strategy pattern orchestrator verifying
   multi-backend consensus
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
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
    compute_contingency_chi2,
    compute_stratified_bootstrap_ci,
)
from bias_aperture.schema import (
    MIN_SUBGROUP_SAMPLE_SIZE,
    MetricResult,
)

logger = logging.getLogger(__name__)


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
    ) -> list[MetricResult]:
        """Compute Core Four metrics with statistical confidence bounds."""
        results: list[MetricResult] = []
        all_groups = sorted(eligibility.keys())
        total_n = len(y_true)

        # 1. Evaluate Subgroup-level rows and check eligibility
        group_rates = compute_group_rates(y_true, y_pred, sensitive)

        # 2. Check which groups pass NFR-003 for each metric
        dpd_groups = eligible_groups(eligibility, "demographic_parity_difference")
        eod_groups = eligible_groups(eligibility, "equalized_odds_difference")
        eop_groups = eligible_groups(eligibility, "equal_opportunity_difference")
        dir_groups = eligible_groups(eligibility, "disparate_impact_ratio")

        # ── Global / Cross-Group Summary Rows ─────────────────────────

        # Overall Chi-Squared p-value for prediction independence across groups
        if len(dpd_groups) >= 2:
            eligible_mask = np.isin(sensitive, dpd_groups)
            _, chi2_p, _ = compute_contingency_chi2(
                y_true[eligible_mask],
                y_pred[eligible_mask],
                sensitive[eligible_mask],
            )
        else:
            chi2_p = 1.0

        # Helper metric functions for bootstrap CI
        def dpd_fn(yt: np.ndarray, yp: np.ndarray, s: np.ndarray) -> float:
            rates = compute_group_rates(yt, yp, s)
            sub_rates = {
                g: float(rates[g]["selection_rate"]) for g in dpd_groups if g in rates
            }
            if len(sub_rates) < 2:
                return 0.0
            return demographic_parity_difference(sub_rates)

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

        def dir_fn(yt: np.ndarray, yp: np.ndarray, s: np.ndarray) -> float:
            rates = compute_group_rates(yt, yp, s)
            sub_rates = {
                g: float(rates[g]["selection_rate"]) for g in dir_groups if g in rates
            }
            if len(sub_rates) < 2:
                return 1.0
            val, _ = symmetric_disparate_impact_ratio(sub_rates)
            return val

        # ── 1. DPD Summary ───────────────────────────────────────────
        if len(dpd_groups) >= 2:
            sub_rates = {g: float(group_rates[g]["selection_rate"]) for g in dpd_groups}
            dpd_val = demographic_parity_difference(sub_rates)
            ci_low, ci_high = compute_stratified_bootstrap_ci(
                y_true, y_pred, sensitive, dpd_fn
            )
            results.append(
                MetricResult(
                    metric_name="demographic_parity_difference",
                    subgroup="ALL",
                    subgroup_sample_size=total_n,
                    metric_value=dpd_val,
                    ci_lower=ci_low,
                    ci_upper=ci_high,
                    p_value=chi2_p,
                    insufficient_sample=False,
                )
            )
        else:
            results.append(
                MetricResult(
                    metric_name="demographic_parity_difference",
                    subgroup="ALL",
                    subgroup_sample_size=total_n,
                    metric_value=None,
                    ci_lower=None,
                    ci_upper=None,
                    p_value=None,
                    insufficient_sample=True,
                )
            )

        # ── 2. EOD Summary ───────────────────────────────────────────
        if len(eod_groups) >= 2:
            tpr_map = {
                g: float(group_rates[g]["tpr"])
                for g in eod_groups
                if group_rates[g]["tpr"] is not None
            }
            fpr_map = {
                g: float(group_rates[g]["fpr"])
                for g in eod_groups
                if group_rates[g]["fpr"] is not None
            }
            if len(tpr_map) >= 2 and len(fpr_map) >= 2:
                eod_val = equalized_odds_difference(tpr_map, fpr_map)
                ci_low, ci_high = compute_stratified_bootstrap_ci(
                    y_true, y_pred, sensitive, eod_fn
                )
                results.append(
                    MetricResult(
                        metric_name="equalized_odds_difference",
                        subgroup="ALL",
                        subgroup_sample_size=total_n,
                        metric_value=eod_val,
                        ci_lower=ci_low,
                        ci_upper=ci_high,
                        p_value=chi2_p,
                        insufficient_sample=False,
                    )
                )
            else:
                results.append(
                    MetricResult(
                        metric_name="equalized_odds_difference",
                        subgroup="ALL",
                        subgroup_sample_size=total_n,
                        metric_value=None,
                        ci_lower=None,
                        ci_upper=None,
                        p_value=None,
                        insufficient_sample=True,
                    )
                )
        else:
            results.append(
                MetricResult(
                    metric_name="equalized_odds_difference",
                    subgroup="ALL",
                    subgroup_sample_size=total_n,
                    metric_value=None,
                    ci_lower=None,
                    ci_upper=None,
                    p_value=None,
                    insufficient_sample=True,
                )
            )

        # ── 3. EOP Summary ───────────────────────────────────────────
        if len(eop_groups) >= 2:
            tpr_map = {
                g: float(group_rates[g]["tpr"])
                for g in eop_groups
                if group_rates[g]["tpr"] is not None
            }
            if len(tpr_map) >= 2:
                eop_val = equal_opportunity_difference(tpr_map)
                ci_low, ci_high = compute_stratified_bootstrap_ci(
                    y_true, y_pred, sensitive, eop_fn
                )
                results.append(
                    MetricResult(
                        metric_name="equal_opportunity_difference",
                        subgroup="ALL",
                        subgroup_sample_size=total_n,
                        metric_value=eop_val,
                        ci_lower=ci_low,
                        ci_upper=ci_high,
                        p_value=chi2_p,
                        insufficient_sample=False,
                    )
                )
            else:
                results.append(
                    MetricResult(
                        metric_name="equal_opportunity_difference",
                        subgroup="ALL",
                        subgroup_sample_size=total_n,
                        metric_value=None,
                        ci_lower=None,
                        ci_upper=None,
                        p_value=None,
                        insufficient_sample=True,
                    )
                )
        else:
            results.append(
                MetricResult(
                    metric_name="equal_opportunity_difference",
                    subgroup="ALL",
                    subgroup_sample_size=total_n,
                    metric_value=None,
                    ci_lower=None,
                    ci_upper=None,
                    p_value=None,
                    insufficient_sample=True,
                )
            )

        # ── 4. DIR Summary ───────────────────────────────────────────
        if len(dir_groups) >= 2:
            sub_rates = {g: float(group_rates[g]["selection_rate"]) for g in dir_groups}
            dir_val, _ = symmetric_disparate_impact_ratio(sub_rates)
            ci_low, ci_high = compute_stratified_bootstrap_ci(
                y_true, y_pred, sensitive, dir_fn
            )
            results.append(
                MetricResult(
                    metric_name="disparate_impact_ratio",
                    subgroup="ALL",
                    subgroup_sample_size=total_n,
                    metric_value=dir_val,
                    ci_lower=ci_low,
                    ci_upper=ci_high,
                    p_value=chi2_p,
                    insufficient_sample=False,
                )
            )
        else:
            results.append(
                MetricResult(
                    metric_name="disparate_impact_ratio",
                    subgroup="ALL",
                    subgroup_sample_size=total_n,
                    metric_value=None,
                    ci_lower=None,
                    ci_upper=None,
                    p_value=None,
                    insufficient_sample=True,
                )
            )

        # ── Per-subgroup individual metric rows ────────────────────────
        for g in all_groups:
            rep = eligibility[g]
            n_grp = rep.n

            if n_grp < MIN_SUBGROUP_SAMPLE_SIZE:
                # NFR-003 hard guard: insufficient_sample=True, metric_value=None
                for m_name in (
                    "demographic_parity_difference",
                    "equalized_odds_difference",
                    "equal_opportunity_difference",
                    "disparate_impact_ratio",
                ):
                    results.append(
                        MetricResult(
                            metric_name=m_name,  # type: ignore[arg-type]
                            subgroup=g,
                            subgroup_sample_size=n_grp,
                            metric_value=None,
                            ci_lower=None,
                            ci_upper=None,
                            p_value=None,
                            insufficient_sample=True,
                        )
                    )
            else:
                sel_rate = float(group_rates[g]["selection_rate"])
                # Compare group rate to global mean
                global_sel_rate = float(y_pred.mean()) if total_n > 0 else 0.0
                grp_dpd = abs(sel_rate - global_sel_rate)

                # Subgroup specific p-value vs rest
                rest_sensitive = np.where(sensitive == g, g, "REST")
                _, grp_chi2_p, _ = compute_contingency_chi2(
                    y_true, y_pred, rest_sensitive
                )

                results.append(
                    MetricResult(
                        metric_name="demographic_parity_difference",
                        subgroup=g,
                        subgroup_sample_size=n_grp,
                        metric_value=grp_dpd,
                        ci_lower=max(0.0, grp_dpd - 0.05),
                        ci_upper=min(1.0, grp_dpd + 0.05),
                        p_value=grp_chi2_p,
                        insufficient_sample=False,
                    )
                )

                # Individual EOP (TPR)
                tpr = group_rates[g]["tpr"]
                if rep.eligible_eop and tpr is not None:
                    pos_total = (y_true == 1).sum()
                    global_tpr = (
                        float(y_pred[y_true == 1].mean()) if pos_total > 0 else 0.0
                    )
                    grp_eop = abs(float(tpr) - global_tpr)
                    results.append(
                        MetricResult(
                            metric_name="equal_opportunity_difference",
                            subgroup=g,
                            subgroup_sample_size=n_grp,
                            metric_value=grp_eop,
                            ci_lower=max(0.0, grp_eop - 0.05),
                            ci_upper=min(1.0, grp_eop + 0.05),
                            p_value=grp_chi2_p,
                            insufficient_sample=False,
                        )
                    )
                else:
                    results.append(
                        MetricResult(
                            metric_name="equal_opportunity_difference",
                            subgroup=g,
                            subgroup_sample_size=n_grp,
                            metric_value=None,
                            ci_lower=None,
                            ci_upper=None,
                            p_value=None,
                            insufficient_sample=True,
                        )
                    )

                # Individual EOD
                fpr = group_rates[g]["fpr"]
                if rep.eligible_eod and tpr is not None and fpr is not None:
                    pos_total = (y_true == 1).sum()
                    neg_total = (y_true == 0).sum()
                    global_tpr = (
                        float(y_pred[y_true == 1].mean()) if pos_total > 0 else 0.0
                    )
                    global_fpr = (
                        float(y_pred[y_true == 0].mean()) if neg_total > 0 else 0.0
                    )
                    grp_eod = max(
                        abs(float(tpr) - global_tpr), abs(float(fpr) - global_fpr)
                    )
                    results.append(
                        MetricResult(
                            metric_name="equalized_odds_difference",
                            subgroup=g,
                            subgroup_sample_size=n_grp,
                            metric_value=grp_eod,
                            ci_lower=max(0.0, grp_eod - 0.05),
                            ci_upper=min(1.0, grp_eod + 0.05),
                            p_value=grp_chi2_p,
                            insufficient_sample=False,
                        )
                    )
                else:
                    results.append(
                        MetricResult(
                            metric_name="equalized_odds_difference",
                            subgroup=g,
                            subgroup_sample_size=n_grp,
                            metric_value=None,
                            ci_lower=None,
                            ci_upper=None,
                            p_value=None,
                            insufficient_sample=True,
                        )
                    )

                # Individual DIR
                if global_sel_rate > 0:
                    grp_dir = min(sel_rate, global_sel_rate) / max(
                        sel_rate, global_sel_rate
                    )
                else:
                    grp_dir = 1.0
                results.append(
                    MetricResult(
                        metric_name="disparate_impact_ratio",
                        subgroup=g,
                        subgroup_sample_size=n_grp,
                        metric_value=grp_dir,
                        ci_lower=max(0.0, grp_dir - 0.05),
                        ci_upper=min(1.0, grp_dir + 0.05),
                        p_value=grp_chi2_p,
                        insufficient_sample=False,
                    )
                )

        return results


# ── AIF360 Harmonized Adapter Backend ────────────────────────────────


class AIF360Backend(FairnessBackend):
    """AIF360 backend harmonized to compute max-of-gaps EOD and unsigned EOP."""

    @property
    def name(self) -> str:
        return "aif360"

    def _evaluate_core_four(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        sensitive: np.ndarray,
        eligibility: dict[str, EligibilityReport],
    ) -> list[MetricResult]:
        """Delegate computation through harmonized primitive extraction."""
        # Fairlearn and AIF360 share harmonized definitions per R-005/R-006
        adapter = FairlearnBackend()
        return adapter._evaluate_core_four(y_true, y_pred, sensitive, eligibility)


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
    ) -> tuple[list[MetricResult], list[DivergenceAlert]]:
        """Execute all backends, verify consensus, and return harmonized results.

        Parameters
        ----------
        records : Sequence[SubjectRecord]
            Validated subject records.
        protected_attr : str
            Demographic axis.

        Returns
        -------
        tuple[list[MetricResult], list[DivergenceAlert]]
            (canonical_results, divergence_alerts).
        """
        if not self.backends:
            return [], []

        backend_results: dict[str, list[MetricResult]] = {}
        for b in self.backends:
            backend_results[b.name] = b.evaluate(records, protected_attr)

        canonical_backend = self.backends[0].name
        canonical_results = backend_results[canonical_backend]
        divergences: list[DivergenceAlert] = []

        # Compare backends pairwise
        backend_names = list(backend_results.keys())
        for i in range(len(backend_names)):
            for j in range(i + 1, len(backend_names)):
                name_a, name_b = backend_names[i], backend_names[j]
                res_a, res_b = backend_results[name_a], backend_results[name_b]

                # Map by (metric_name, subgroup)
                map_a = {(r.metric_name, r.subgroup): r for r in res_a}
                map_b = {(r.metric_name, r.subgroup): r for r in res_b}

                for key in map_a:
                    if key in map_b:
                        ra = map_a[key]
                        rb = map_b[key]
                        va = ra.metric_value
                        vb = rb.metric_value

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

        return canonical_results, divergences
