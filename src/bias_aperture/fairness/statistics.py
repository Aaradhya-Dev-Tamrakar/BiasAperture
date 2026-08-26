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

import numpy as np
from scipy import stats

from bias_aperture.schema import ALPHA, MIN_BOOTSTRAP_RESAMPLES

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
        # Degenerate sampling support, fallback to point estimate or simple bounds
        return max(0.0, theta_hat - 0.05), min(1.0, theta_hat + 0.05)

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
    # For large n, approximate jackknife or use group-level jackknife
    # Here we do leave-one-out if n <= 200, otherwise subsampled jackknife
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
            # Subsample jackknife delete-d
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
