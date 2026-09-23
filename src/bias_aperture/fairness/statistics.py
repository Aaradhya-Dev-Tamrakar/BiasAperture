"""
Statistical rigor engine (WP4 / Stream C).

Implements statistical hypothesis testing and uncertainty quantification:
1. Vectorized Stratified BCa Bootstrap Confidence Intervals (R-009)
   - Fixed observed subgroup strata resampling
   - Jackknife acceleration parameter calculation
   - Bias correction parameter estimation
   - Empirical percentile fallback when |a| > 0.5 or boundaries degenerate
2. Chi-Squared Independence Testing (NFR-001)
   - Contingency table construction across demographic strata
   - Scipy chi2_contingency with continuity correction
   - Fisher's Exact Test fallback for 2x2 tables with expected count < 5
3. Holm-Bonferroni Step-Down FWER Adjustment (R-011)
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, replace

import numpy as np
from scipy import stats

from bias_aperture.schema import ALPHA, MIN_BOOTSTRAP_RESAMPLES, MetricResult


@dataclass(frozen=True, slots=True)
class StatTestResult:
    """Outcome of a metric-specific statistical significance test."""

    test_name: str
    statistic: float
    raw_p: float
    dof: int
    hypothesis_family: str


# ── Chi-Squared & Contingency Testing ─────────────────────────────────


def compute_contingency_chi2(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sensitive: np.ndarray,
) -> tuple[float, float, int]:
    """Compute Pearson's chi-squared test of independence across demographic groups.

    Constructs a 2 x K contingency table of positive/negative predictions across
    the K unique subgroups in ``sensitive``.

    Parameters
    ----------
    y_true : np.ndarray
        Ground-truth labels (shape: (n,)).
    y_pred : np.ndarray
        Binary predictions (0 or 1, shape: (n,)).
    sensitive : np.ndarray
        Protected attribute labels (shape: (n,)).

    Returns
    -------
    tuple[float, float, int]
        (chi2_statistic, p_value, degrees_of_freedom).
    """
    y_pred = np.asarray(y_pred, dtype=int)
    sensitive = np.asarray(sensitive)

    groups = np.unique(sensitive)
    if len(groups) < 2:
        return 0.0, 1.0, 0

    table = []
    for g in groups:
        mask = sensitive == g
        yp = y_pred[mask]
        pos = int((yp == 1).sum())
        neg = int((yp == 0).sum())
        table.append([pos, neg])

    table_arr = np.array(table).T  # Shape: (2, K)

    # If 2x2 and any expected count < 5, fallback to Fisher's exact
    if table_arr.shape == (2, 2):
        row_sums = table_arr.sum(axis=1)
        col_sums = table_arr.sum(axis=0)
        total = table_arr.sum()
        if total > 0:
            expected = np.outer(row_sums, col_sums) / total
            if (expected < 5).any():
                res = stats.fisher_exact(table_arr)
                return float(res.statistic), float(res.pvalue), 1

    try:
        chi2, p_val, dof, _ = stats.chi2_contingency(table_arr)
        return float(chi2), float(p_val), int(dof)
    except Exception:
        return 0.0, 1.0, len(groups) - 1


def holm_bonferroni_correction(
    p_values: Sequence[float],
) -> list[float]:
    """Apply Holm-Bonferroni step-down procedure for FWER control (R-011).

    Given M hypotheses with sorted p-values p_(1) <= ... <= p_(M):
        p_(k)^adj = min(1, max_{j <= k} [ (M - j + 1) * p_(j) ])

    Parameters
    ----------
    p_values : Sequence[float]
        Unadjusted p-values.

    Returns
    -------
    list[float]
        Adjusted p-values preserving the original input order.
    """
    m = len(p_values)
    if m == 0:
        return []

    p_arr = np.asarray(p_values, dtype=float)
    order = np.argsort(p_arr)
    sorted_p = p_arr[order]

    adjusted = np.empty(m, dtype=float)
    running_max = 0.0
    for j in range(m):
        multiplier = m - j
        val = multiplier * sorted_p[j]
        running_max = max(running_max, val)
        adjusted[j] = min(1.0, running_max)

    # Revert back to original ordering
    out = np.empty(m, dtype=float)
    out[order] = adjusted
    return [float(x) for x in out]


def compute_metric_specific_test(
    metric_name: str,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sensitive: np.ndarray,
) -> StatTestResult:
    """Compute significance test tailored to the specific fairness metric.

    - demographic_parity_difference / DPD:
        Chi-squared test of independence between binary predictions and protected group
        (testing H0: P(Y_hat=1 | A=a) = P(Y_hat=1 | A=b)).
        Family: "selection_rate"
    - equal_opportunity_difference / EOP:
        Chi-squared test of independence conditioned on positive ground-truth Y_true = 1
        (testing H0: TPR_a = TPR_b across demographic groups).
        Conditions strictly on positive ground-truth instances.
        Family: "conditional_odds"
    - equalized_odds_difference / EOD:
        Joint hypothesis test evaluating both TPR equality (Y_true = 1)
        and FPR equality (Y_true = 0). Computes conditional chi-squared tests
        on both ground-truth strata and combines significance via Bonferroni
        union-intersection testing.
        Family: "conditional_odds"
    - disparate_impact_ratio / DIR:
        Chi-squared test of independence between selection rates across
        protected groups.
        Family: "selection_rate"
    """
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    sensitive = np.asarray(sensitive)

    m_lower = metric_name.lower()

    if "equal_opportunity" in m_lower or m_lower == "eop":
        pos_mask = y_true == 1
        if pos_mask.sum() == 0 or len(np.unique(sensitive[pos_mask])) < 2:
            return StatTestResult(
                test_name="equal_opportunity_tpr_chi2",
                statistic=0.0,
                raw_p=1.0,
                dof=0,
                hypothesis_family="conditional_odds",
            )
        stat, p_val, dof = compute_contingency_chi2(
            y_true[pos_mask], y_pred[pos_mask], sensitive[pos_mask]
        )
        return StatTestResult(
            test_name="equal_opportunity_tpr_chi2",
            statistic=stat,
            raw_p=p_val,
            dof=dof,
            hypothesis_family="conditional_odds",
        )

    if "equalized_odds" in m_lower or m_lower == "eod":
        pos_mask = y_true == 1
        neg_mask = y_true == 0

        p_tpr, stat_tpr, dof_tpr = 1.0, 0.0, 0
        if pos_mask.sum() > 0 and len(np.unique(sensitive[pos_mask])) >= 2:
            stat_tpr, p_tpr, dof_tpr = compute_contingency_chi2(
                y_true[pos_mask], y_pred[pos_mask], sensitive[pos_mask]
            )

        p_fpr, stat_fpr, dof_fpr = 1.0, 0.0, 0
        if neg_mask.sum() > 0 and len(np.unique(sensitive[neg_mask])) >= 2:
            stat_fpr, p_fpr, dof_fpr = compute_contingency_chi2(
                y_true[neg_mask], y_pred[neg_mask], sensitive[neg_mask]
            )

        joint_p = float(min(1.0, 2.0 * min(p_tpr, p_fpr)))
        joint_stat = float(max(stat_tpr, stat_fpr))
        joint_dof = int(max(dof_tpr, dof_fpr))

        return StatTestResult(
            test_name="equalized_odds_joint_chi2",
            statistic=joint_stat,
            raw_p=joint_p,
            dof=joint_dof,
            hypothesis_family="conditional_odds",
        )

    if "disparate_impact" in m_lower or m_lower == "dir":
        stat, p_val, dof = compute_contingency_chi2(y_true, y_pred, sensitive)
        return StatTestResult(
            test_name="disparate_impact_chi2",
            statistic=stat,
            raw_p=p_val,
            dof=dof,
            hypothesis_family="selection_rate",
        )

    stat, p_val, dof = compute_contingency_chi2(y_true, y_pred, sensitive)
    return StatTestResult(
        test_name="demographic_parity_chi2",
        statistic=stat,
        raw_p=p_val,
        dof=dof,
        hypothesis_family="selection_rate",
    )


def adjust_family_pvalues(results: list[MetricResult]) -> list[MetricResult]:
    """Apply Holm-Bonferroni FWER step-down adjustment across families (R-011).

    Groups MetricResult instances by `hypothesis_family`. For each family, collects
    unadjusted p-values from non-insufficient results that have a valid `raw_p_value`,
    runs `holm_bonferroni_correction`, and returns updated MetricResult instances with:
    - `adjusted_p_value` set to the FWER-adjusted p-value
    - `p_value` set to the adjusted p-value
    - `adjustment_method` set to "holm_bonferroni"
    """
    if not results:
        return []

    families: dict[str, list[int]] = {}
    for idx, res in enumerate(results):
        if res.insufficient_sample or res.raw_p_value is None:
            continue
        fam = res.hypothesis_family or "default"
        families.setdefault(fam, []).append(idx)

    adjusted_map: dict[int, float] = {}
    for _fam, indices in families.items():
        raw_ps = [results[i].raw_p_value for i in indices]  # type: ignore[misc]
        adj_ps = holm_bonferroni_correction(raw_ps)
        for i, adj in zip(indices, adj_ps, strict=True):
            adjusted_map[i] = adj

    updated: list[MetricResult] = []
    for idx, res in enumerate(results):
        if idx in adjusted_map:
            adj = adjusted_map[idx]
            updated.append(
                replace(
                    res,
                    p_value=adj,
                    adjusted_p_value=adj,
                    adjustment_method="holm_bonferroni",
                )
            )
        else:
            updated.append(res)

    return updated


# ── Stratified BCa Bootstrap Confidence Intervals ─────────────────────


def compute_stratified_bootstrap_ci(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sensitive: np.ndarray,
    metric_fn: Callable[[np.ndarray, np.ndarray, np.ndarray], float],
    n_resamples: int = MIN_BOOTSTRAP_RESAMPLES,
    alpha: float = ALPHA,
    seed: int | None = 42,
) -> tuple[float, float]:
    """Compute 95% stratified BCa bootstrap confidence interval (R-009).

    Resampling is strictly conducted *within* each observed sensitive stratum
    to preserve group sample sizes. Computes jackknife acceleration parameter
    and bias correction, falling back to percentile interval if degenerate or
    |a| > 0.5.

    Parameters
    ----------
    y_true : np.ndarray
        Ground-truth labels (shape: (n,)).
    y_pred : np.ndarray
        Predicted labels (shape: (n,)).
    sensitive : np.ndarray
        Sensitive attribute labels (shape: (n,)).
    metric_fn : Callable[[np.ndarray, np.ndarray, np.ndarray], float]
        Function computing point metric value from (y_true, y_pred, sensitive).
    n_resamples : int
        Number of bootstrap replications (default >= 1000).
    alpha : float
        Significance level (default 0.05 for 95% CI).
    seed : int | None
        PRNG seed for deterministic reproducibility.

    Returns
    -------
    tuple[float, float]
        (ci_lower, ci_upper) in [0, 1] range.
    """
    n_resamples = max(n_resamples, MIN_BOOTSTRAP_RESAMPLES)
    rng = np.random.default_rng(seed)

    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    sensitive = np.asarray(sensitive)
    n = len(sensitive)

    if n == 0:
        return 0.0, 1.0

    # Point estimate on full sample
    theta_hat = float(metric_fn(y_true, y_pred, sensitive))

    # Stratified indices
    groups = np.unique(sensitive)
    group_indices = {g: np.where(sensitive == g)[0] for g in groups}

    # Generate bootstrap replicates
    boot_thetas = np.empty(n_resamples, dtype=float)
    valid_count = 0

    for _b in range(n_resamples):
        resampled_idx_list = []
        for _g, idx in group_indices.items():
            if len(idx) > 0:
                sampled = rng.choice(idx, size=len(idx), replace=True)
                resampled_idx_list.append(sampled)
        boot_idx = np.concatenate(resampled_idx_list)

        try:
            val = float(
                metric_fn(y_true[boot_idx], y_pred[boot_idx], sensitive[boot_idx])
            )
            if not np.isnan(val) and not np.isinf(val):
                boot_thetas[valid_count] = val
                valid_count += 1
        except Exception:
            continue

    if valid_count < int(0.9 * n_resamples):
        # Degenerate sampling support: fallback to empirical percentiles
        # if sufficient, else point estimate
        if valid_count >= 20:
            low = float(np.percentile(boot_thetas[:valid_count], 100 * (alpha / 2)))
            high = float(
                np.percentile(boot_thetas[:valid_count], 100 * (1 - alpha / 2))
            )
            return float(np.clip(low, 0.0, 1.0)), float(np.clip(high, 0.0, 1.0))
        return float(np.clip(theta_hat, 0.0, 1.0)), float(np.clip(theta_hat, 0.0, 1.0))

    valid_thetas = boot_thetas[:valid_count]

    # Percentile fallback helper
    def percentile_ci() -> tuple[float, float]:
        low = float(np.percentile(valid_thetas, 100 * (alpha / 2)))
        high = float(np.percentile(valid_thetas, 100 * (1 - alpha / 2)))
        return float(np.clip(low, 0.0, 1.0)), float(np.clip(high, 0.0, 1.0))

    # 1. Bias correction z0
    prop_less = np.mean(valid_thetas < theta_hat)
    if prop_less <= 0.0 or prop_less >= 1.0:
        return percentile_ci()

    z0 = stats.norm.ppf(prop_less)

    # 2. Jackknife acceleration parameter a
    # For small to moderate n (n <= 300), standard leave-one-out jackknife is evaluated.
    # For large n (n > 300), we employ a delete-d subsampled block jackknife
    # approximation (Shao & Tu, 1995; Efron & Tibshirani, 1993, Ch. 11), using
    # d = max(1, n // 100) blocks to maintain tractable acceleration parameter
    # estimation while preserving asymptotic convergence.
    try:
        if n <= 300:
            jack_thetas = np.empty(n, dtype=float)
            for i in range(n):
                j_idx = np.delete(np.arange(n), i)
                jack_thetas[i] = metric_fn(
                    y_true[j_idx], y_pred[j_idx], sensitive[j_idx]
                )
            jack_mean = np.mean(jack_thetas)
            diff = jack_mean - jack_thetas
            num = np.sum(diff**3)
            denom = 6.0 * (np.sum(diff**2) ** 1.5)
            a = num / denom if denom != 0 else 0.0
        else:
            # Subsample jackknife delete-d (100 blocks)
            d = max(1, n // 100)
            n_sub = n // d
            jack_thetas = np.empty(n_sub, dtype=float)
            for k in range(n_sub):
                j_idx = np.delete(np.arange(n), slice(k * d, (k + 1) * d))
                jack_thetas[k] = metric_fn(
                    y_true[j_idx], y_pred[j_idx], sensitive[j_idx]
                )
            jack_mean = np.mean(jack_thetas)
            diff = jack_mean - jack_thetas
            num = np.sum(diff**3)
            denom = 6.0 * (np.sum(diff**2) ** 1.5)
            a = num / denom if denom != 0 else 0.0

        if abs(a) > 0.5 or np.isnan(a):
            return percentile_ci()

        # 3. BCa percentiles
        z_alpha = stats.norm.ppf(alpha / 2)
        z_1_alpha = stats.norm.ppf(1 - alpha / 2)

        denom1 = 1 - a * (z0 + z_alpha)
        denom2 = 1 - a * (z0 + z_1_alpha)

        if denom1 == 0 or denom2 == 0:
            return percentile_ci()

        a1 = stats.norm.cdf(z0 + (z0 + z_alpha) / denom1)
        a2 = stats.norm.cdf(z0 + (z0 + z_1_alpha) / denom2)

        if not (0.0 < a1 < 1.0 and 0.0 < a2 < 1.0):
            return percentile_ci()

        ci_low = float(np.percentile(valid_thetas, 100 * a1))
        ci_high = float(np.percentile(valid_thetas, 100 * a2))

        return float(np.clip(ci_low, 0.0, 1.0)), float(np.clip(ci_high, 0.0, 1.0))
    except Exception:
        return percentile_ci()


def _evaluate_subgroup_metric(
    metric_name: str,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sensitive: np.ndarray,
    subgroup: str,
) -> float | None:
    """Evaluate point metric comparing a subgroup to the global baseline."""
    grp_mask = sensitive == subgroup
    if grp_mask.sum() == 0:
        return None

    m_lower = metric_name.lower()
    total_n = len(y_pred)
    if total_n == 0:
        return None

    if "demographic_parity" in m_lower or m_lower == "dpd":
        grp_sel = float(y_pred[grp_mask].mean())
        global_sel = float(y_pred.mean())
        return abs(grp_sel - global_sel)

    if "equal_opportunity" in m_lower or m_lower == "eop":
        pos_total = (y_true == 1).sum()
        grp_pos = (grp_mask & (y_true == 1)).sum()
        if pos_total == 0 or grp_pos == 0:
            return None
        grp_tpr = float(y_pred[grp_mask & (y_true == 1)].mean())
        global_tpr = float(y_pred[y_true == 1].mean())
        return abs(grp_tpr - global_tpr)

    if "equalized_odds" in m_lower or m_lower == "eod":
        pos_total = (y_true == 1).sum()
        neg_total = (y_true == 0).sum()
        grp_pos = (grp_mask & (y_true == 1)).sum()
        grp_neg = (grp_mask & (y_true == 0)).sum()
        if pos_total == 0 or neg_total == 0 or grp_pos == 0 or grp_neg == 0:
            return None
        grp_tpr = float(y_pred[grp_mask & (y_true == 1)].mean())
        global_tpr = float(y_pred[y_true == 1].mean())
        grp_fpr = float(y_pred[grp_mask & (y_true == 0)].mean())
        global_fpr = float(y_pred[y_true == 0].mean())
        return max(abs(grp_tpr - global_tpr), abs(grp_fpr - global_fpr))

    if "disparate_impact" in m_lower or m_lower == "dir":
        grp_sel = float(y_pred[grp_mask].mean())
        global_sel = float(y_pred.mean())
        if global_sel > 0:
            return float(min(grp_sel, global_sel) / max(grp_sel, global_sel))
        return 1.0

    return None


def compute_subgroup_bootstrap_ci(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sensitive: np.ndarray,
    subgroup: str,
    metric_name: str,
    n_resamples: int = 200,
    alpha: float = ALPHA,
    seed: int | None = 42,
) -> tuple[float | None, float | None]:
    """Compute empirical percentile bootstrap confidence interval for a subgroup metric.

    Resamples with replacement stratified by protected group, evaluating disparity
    between the target subgroup and the overall population on each resample.
    Returns (None, None) if sample size or validity criteria are not met.
    """
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    sensitive = np.asarray(sensitive)

    groups = np.unique(sensitive)
    if subgroup not in groups:
        return None, None

    if (sensitive == subgroup).sum() < 30:
        return None, None

    point_est = _evaluate_subgroup_metric(
        metric_name, y_true, y_pred, sensitive, subgroup
    )
    if point_est is None:
        return None, None

    rng = np.random.default_rng(seed)
    group_indices = {g: np.where(sensitive == g)[0] for g in groups}

    boot_thetas = np.empty(n_resamples, dtype=float)
    valid_count = 0

    for _b in range(n_resamples):
        resampled_idx_list = []
        for _g, idx in group_indices.items():
            if len(idx) > 0:
                sampled = rng.choice(idx, size=len(idx), replace=True)
                resampled_idx_list.append(sampled)
        boot_idx = np.concatenate(resampled_idx_list)

        val = _evaluate_subgroup_metric(
            metric_name,
            y_true[boot_idx],
            y_pred[boot_idx],
            sensitive[boot_idx],
            subgroup,
        )
        if val is not None and not np.isnan(val) and not np.isinf(val):
            boot_thetas[valid_count] = val
            valid_count += 1

    if valid_count < 20:
        return float(np.clip(point_est, 0.0, 1.0)), float(np.clip(point_est, 0.0, 1.0))

    valid = boot_thetas[:valid_count]
    low = float(np.percentile(valid, 100 * (alpha / 2)))
    high = float(np.percentile(valid, 100 * (1 - alpha / 2)))
    return float(np.clip(low, 0.0, 1.0)), float(np.clip(high, 0.0, 1.0))
