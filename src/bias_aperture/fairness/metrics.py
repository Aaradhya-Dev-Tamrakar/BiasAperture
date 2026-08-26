"""
Core Four fairness metric calculators (WP4 / Stream C).

Pure mathematical implementations computed from raw confusion-matrix
primitives — no external library dependencies beyond numpy.  These
functions encode the harmonised definitions locked in the Claim Ledger
(R-005 through R-010) and the LOW_LEVEL_SPECIFICATION §2.

All difference metrics return values in [0, 1].
Disparate Impact Ratio returns values in [0, 1] with 1.0 = parity.
"""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np

# ── Demographic Parity Difference (DPD) ──────────────────────────────


def demographic_parity_difference(
    selection_rates: Mapping[str, float],
) -> float:
    """Compute DPD = max_a P(Ŷ=1|A=a) − min_a P(Ŷ=1|A=a).

    Parameters
    ----------
    selection_rates : Mapping[str, float]
        Mapping from subgroup label to positive-prediction rate.

    Returns
    -------
    float
        Unsigned difference in [0, 1].

    Raises
    ------
    ValueError
        If fewer than 2 subgroups are supplied.
    """
    rates = list(selection_rates.values())
    if len(rates) < 2:
        raise ValueError(f"DPD requires at least 2 subgroups, got {len(rates)}.")
    return float(max(rates) - min(rates))


# ── Equalized Odds Difference (EOD) ──────────────────────────────────


def equalized_odds_difference(
    tpr_by_group: Mapping[str, float],
    fpr_by_group: Mapping[str, float],
) -> float:
    """Compute EOD = max(|ΔTPR|, |ΔFPR|) (Hardt et al. / Fairlearn).

    This is the *worst-case max-gap* definition per R-005, not the
    AIF360 native mean-gap.

    Parameters
    ----------
    tpr_by_group : Mapping[str, float]
        True positive rate per subgroup.
    fpr_by_group : Mapping[str, float]
        False positive rate per subgroup.

    Returns
    -------
    float
        Unsigned worst-case gap in [0, 1].
    """
    tpr_vals = list(tpr_by_group.values())
    fpr_vals = list(fpr_by_group.values())
    if len(tpr_vals) < 2 or len(fpr_vals) < 2:
        raise ValueError("EOD requires at least 2 subgroups with TPR and FPR.")
    tpr_gap = max(tpr_vals) - min(tpr_vals)
    fpr_gap = max(fpr_vals) - min(fpr_vals)
    return float(max(tpr_gap, fpr_gap))


# ── Equal Opportunity Difference (EOP) ───────────────────────────────


def equal_opportunity_difference(
    tpr_by_group: Mapping[str, float],
) -> float:
    """Compute EOP = max_a TPR_a − min_a TPR_a (unsigned, per R-006).

    Parameters
    ----------
    tpr_by_group : Mapping[str, float]
        True positive rate per subgroup.

    Returns
    -------
    float
        Unsigned TPR gap in [0, 1].
    """
    tpr_vals = list(tpr_by_group.values())
    if len(tpr_vals) < 2:
        raise ValueError("EOP requires at least 2 subgroups with TPR.")
    return float(max(tpr_vals) - min(tpr_vals))


# ── Symmetric Disparate Impact Ratio (DIR) ───────────────────────────


def symmetric_disparate_impact_ratio(
    selection_rates: Mapping[str, float],
) -> tuple[float, bool]:
    """Compute DIR = min(rates) / max(rates) ∈ [0, 1] (R-007, R-010).

    Uses the symmetric bounded form without requiring a reference group
    designation.  Zero-denominator edge cases follow the R-010 contract:
    - 0/0 → 1.0 (no relative disparity) + warning flag
    - x/0 is impossible when max=0 implies all rates=0
    - 0/x → 0.0 (complete disparate exclusion)

    Parameters
    ----------
    selection_rates : Mapping[str, float]
        Mapping from subgroup label to positive-prediction rate.

    Returns
    -------
    tuple[float, bool]
        (dir_value, absolute_selection_warning).
        ``absolute_selection_warning`` is True when *all* rates are 0.0.
    """
    rates = list(selection_rates.values())
    if len(rates) < 2:
        raise ValueError(f"DIR requires at least 2 subgroups, got {len(rates)}.")

    rate_max = max(rates)
    rate_min = min(rates)

    # R-010 zero-denominator contract
    if rate_max == 0.0:
        return 1.0, True  # no positive selections anywhere

    if rate_min == 0.0:
        return 0.0, False  # complete disparate exclusion

    return float(np.clip(rate_min / rate_max, 0.0, 1.0)), False


# ── Confusion-matrix primitive extractors ────────────────────────────


def compute_group_rates(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sensitive: np.ndarray,
) -> dict[str, dict[str, float | int]]:
    """Compute per-group confusion-matrix rates from aligned arrays.

    Parameters
    ----------
    y_true : np.ndarray
        Ground-truth binary labels (0 or 1), shape (n,).
    y_pred : np.ndarray
        Predicted binary labels (0 or 1), shape (n,).
    sensitive : np.ndarray
        Sensitive attribute labels, shape (n,).

    Returns
    -------
    dict[str, dict[str, float | int]]
        Per-group dict with keys: ``n``, ``n_pos``, ``n_neg``,
        ``selection_rate``, ``tpr``, ``fpr``.
        TPR/FPR are ``None`` when the denominator is zero (no
        positive or negative ground-truth samples in that group).
    """
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    sensitive = np.asarray(sensitive)

    groups: dict[str, dict[str, float | int]] = {}
    for label in np.unique(sensitive):
        mask = sensitive == label
        yt = y_true[mask]
        yp = y_pred[mask]
        n = int(mask.sum())

        pos_mask = yt == 1
        neg_mask = yt == 0
        n_pos = int(pos_mask.sum())
        n_neg = int(neg_mask.sum())

        selection_rate = float(yp.mean()) if n > 0 else 0.0
        tpr = float(yp[pos_mask].mean()) if n_pos > 0 else None
        fpr = float(yp[neg_mask].mean()) if n_neg > 0 else None

        groups[str(label)] = {
            "n": n,
            "n_pos": n_pos,
            "n_neg": n_neg,
            "selection_rate": selection_rate,
            "tpr": tpr,
            "fpr": fpr,
        }

    return groups
