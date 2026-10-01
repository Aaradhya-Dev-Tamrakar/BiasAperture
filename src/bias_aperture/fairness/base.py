"""
Abstract fairness backend and shared sample-guard infrastructure (WP4).

Defines the ``FairnessBackend`` ABC that both ``FairlearnBackend`` and
``AIF360Backend`` implement, plus the shared NFR-003 pre-filtering logic
that prevents sub-30 subgroups from ever reaching metric computation.

Per MID_LEVEL_ARCHITECTURE §2.2: "``subgroup_sample_sizes()`` and
``is_insufficient()`` are defined once in base.py.  Both backends share
this calculation to prevent false divergences caused by divergent
internal pandas/numpy grouping logic."
"""

from __future__ import annotations

import abc
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from bias_aperture.schema import (
    MIN_POSITIVE_SUPPORT,
    MIN_SUBGROUP_SAMPLE_SIZE,
    MetricResult,
    SubjectRecord,
)

# ── Configuration ────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class EligibilityReport:
    """Per-group eligibility status after NFR-003 screening.

    Attributes
    ----------
    group_label : str
        Subgroup identifier (e.g. ``"White"``).
    n : int
        Total sample count in this group.
    n_pos : int
        Count of ground-truth positive samples (Y=1).
    n_neg : int
        Count of ground-truth negative samples (Y=0).
    eligible : bool
        True if the group passes NFR-003 (n ≥ 30).
    eligible_eop : bool
        True if eligible AND positive support ≥ 5.
    eligible_eod : bool
        True if eligible AND both positive and negative support ≥ 5.
    """

    group_label: str
    n: int
    n_pos: int
    n_neg: int
    eligible: bool
    eligible_eop: bool
    eligible_eod: bool


# Minimum positive/negative support now sourced from schema.MIN_POSITIVE_SUPPORT.
# Alias kept for backward compatibility within this module.
_MIN_SUPPORT: int = MIN_POSITIVE_SUPPORT


def encode_binary_labels(
    y_true: Sequence,
    y_pred: Sequence,
) -> tuple[np.ndarray, np.ndarray]:
    """Encode the shared task vocabulary, rejecting unsupported multiclass tasks.

    Preserve the historical default: the sorted second label is positive
    (therefore 1 for 0/1, Male for Female/Male). A sole 1/True label is
    positive; any other sole label is negative. Inspect truth AND predictions
    so an unexpected prediction cannot silently enter a binary calculation.
    """
    truth, predictions = np.asarray(y_true), np.asarray(y_pred)
    labels = sorted(set(truth) | set(predictions))
    if len(labels) > 2:
        raise ValueError(
            f"Binary audits support at most two task labels; found {len(labels)}. "
            "General multiclass One-vs-Rest auditing is not implemented. "
            "Provide a binary task with matching truth and prediction labels."
        )
    if len(labels) == 2:
        mapping = {labels[0]: 0, labels[1]: 1}
    elif labels:
        mapping = {labels[0]: int(labels[0] in ("1", 1, True, "True", "true"))}
    else:
        mapping = {}
    return (
        np.array([mapping[v] for v in truth], dtype=int),
        np.array([mapping[v] for v in predictions], dtype=int),
    )


def screen_subgroups(
    records: Sequence[SubjectRecord],
    protected_attr: str,
) -> list[EligibilityReport]:
    """Screen subgroups for NFR-003 eligibility and support adequacy.

    Parameters
    ----------
    records : Sequence[SubjectRecord]
        Full list of validated ``SubjectRecord`` instances.
    protected_attr : str
        Which demographic axis to stratify on (``"race"``,
        ``"gender"``, ``"age"``).

    Returns
    -------
    list[EligibilityReport]
        One report per observed subgroup, sorted by label.
    """
    groups: dict[str, list[SubjectRecord]] = {}
    for r in records:
        key = getattr(r, protected_attr)
        groups.setdefault(key, []).append(r)

    reports = []
    for label in sorted(groups):
        recs = groups[label]
        n = len(recs)
        eligible = n >= MIN_SUBGROUP_SAMPLE_SIZE

        reports.append(
            EligibilityReport(
                group_label=label,
                n=n,
                n_pos=n,  # placeholder — refined in numeric eval
                n_neg=0,
                eligible=eligible,
                eligible_eop=eligible,
                eligible_eod=eligible,
            )
        )

    return reports


def screen_numeric_groups(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sensitive: np.ndarray,
) -> dict[str, EligibilityReport]:
    """Screen numeric arrays for per-metric eligibility.

    This is the authoritative screening function used by backends
    before metric computation.  It evaluates the full support conditions
    from LOW_LEVEL_SPECIFICATION §3.3.1.

    Parameters
    ----------
    y_true, y_pred : np.ndarray
        Binary ground-truth and predictions, shape (n,).
    sensitive : np.ndarray
        Sensitive attribute labels, shape (n,).

    Returns
    -------
    dict[str, EligibilityReport]
        Keyed by group label string.
    """
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    sensitive = np.asarray(sensitive)

    reports: dict[str, EligibilityReport] = {}
    for label in np.unique(sensitive):
        mask = sensitive == label
        yt = y_true[mask]
        n = int(mask.sum())
        n_pos = int((yt == 1).sum())
        n_neg = int((yt == 0).sum())

        eligible = n >= MIN_SUBGROUP_SAMPLE_SIZE
        eligible_eop = eligible and n_pos >= _MIN_SUPPORT
        eligible_eod = eligible and n_pos >= _MIN_SUPPORT and n_neg >= _MIN_SUPPORT

        reports[str(label)] = EligibilityReport(
            group_label=str(label),
            n=n,
            n_pos=n_pos,
            n_neg=n_neg,
            eligible=eligible,
            eligible_eop=eligible_eop,
            eligible_eod=eligible_eod,
        )

    return reports


def eligible_groups(
    reports: dict[str, EligibilityReport],
    metric_name: str,
) -> list[str]:
    """Return labels of groups eligible for a given metric.

    Parameters
    ----------
    reports : dict[str, EligibilityReport]
        Output from ``screen_numeric_groups``.
    metric_name : str
        One of the Core Four metric names.

    Returns
    -------
    list[str]
        Sorted list of eligible group labels.
    """
    result = []
    for label, report in sorted(reports.items()):
        if metric_name in (
            "demographic_parity_difference",
            "disparate_impact_ratio",
        ):
            if report.eligible:
                result.append(label)
        elif metric_name == "equal_opportunity_difference":
            if report.eligible_eop:
                result.append(label)
        elif metric_name == "equalized_odds_difference":
            if report.eligible_eod:
                result.append(label)
        else:
            if report.eligible:
                result.append(label)
    return result


# ── Abstract Backend ─────────────────────────────────────────────────


class FairnessBackend(abc.ABC):
    """Abstract base class for fairness metric backends.

    Subclasses implement ``_evaluate_core_four`` which computes the
    Core Four metrics on pre-screened data.  The base class handles
    NFR-003 screening and ``MetricResult`` construction.
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Human-readable backend identifier."""

    @abc.abstractmethod
    def _evaluate_core_four(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        sensitive: np.ndarray,
        eligibility: dict[str, EligibilityReport],
        n_bootstrap_resamples: int = 1000,
    ) -> list[MetricResult]:
        """Compute Core Four metrics on pre-screened arrays.

        Implementations must only compute metrics for groups that pass
        the eligibility check for each specific metric.  Groups that
        fail should produce ``MetricResult`` rows with
        ``insufficient_sample=True`` and ``metric_value=None``.

        Parameters
        ----------
        y_true, y_pred : np.ndarray
            Binary labels, shape (n,).
        sensitive : np.ndarray
            Sensitive attribute labels, shape (n,).
        eligibility : dict[str, EligibilityReport]
            Per-group eligibility from ``screen_numeric_groups``.
        n_bootstrap_resamples : int
            Number of bootstrap iterations (B >= 1000, NFR-002).

        Returns
        -------
        list[MetricResult]
            One row per (metric, subgroup) pair, plus summary rows.
        """

    def evaluate(
        self,
        records: Sequence[SubjectRecord],
        protected_attr: str,
        true_label_col: str = "true_label",
        pred_label_col: str = "predicted_label",
        n_bootstrap_resamples: int = 1000,
    ) -> list[MetricResult]:
        """Run the full evaluation pipeline with NFR-003 screening.

        Parameters
        ----------
        records : Sequence[SubjectRecord]
            Validated subject records.
        protected_attr : str
            Demographic axis (``"race"``, ``"gender"``, ``"age"``).
        true_label_col, pred_label_col : str
            Attribute names on ``SubjectRecord`` for Y and Ŷ.

        Returns
        -------
        list[MetricResult]
            Complete metric results including insufficient-sample flags.
        """
        # Extract aligned arrays
        y_true = np.array([getattr(r, true_label_col) for r in records])
        y_pred = np.array([getattr(r, pred_label_col) for r in records])
        if (
            len(records) > 0
            and not hasattr(records[0], protected_attr)
            and "_" in protected_attr
        ):
            parts = protected_attr.split("_")
            sensitive = np.array(
                ["_".join(str(getattr(r, p)) for p in parts) for r in records]
            )
        else:
            sensitive = np.array([getattr(r, protected_attr) for r in records])

        y_true_bin, y_pred_bin = encode_binary_labels(y_true, y_pred)

        # NFR-003 screening
        eligibility = screen_numeric_groups(y_true_bin, y_pred_bin, sensitive)

        return self._evaluate_core_four(
            y_true_bin,
            y_pred_bin,
            sensitive,
            eligibility,
            n_bootstrap_resamples=n_bootstrap_resamples,
        )
