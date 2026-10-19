"""
Unit tests for backend integrity, isolation, and failure reporting.
Verifies that backend outages emit DivergenceAlerts rather than
silently masking failures.
"""

from __future__ import annotations

import math
from unittest.mock import patch

from bias_aperture.fairness.backends import (
    AIF360Backend,
    CrossValidationOrchestrator,
    FairlearnBackend,
)
from bias_aperture.schema import SubjectRecord


def _make_dummy_records(n_per_group: int = 40) -> list[SubjectRecord]:
    records: list[SubjectRecord] = []
    # Group 1: White (higher positive rate)
    for i in range(n_per_group):
        records.append(
            SubjectRecord(
                image_id=f"white_{i}",
                race="White",
                gender="Female",
                age="20-29",
                true_label="1" if i < 30 else "0",
                predicted_label="1" if i < 30 else "0",
            )
        )
    # Group 2: Black (lower positive rate)
    for i in range(n_per_group):
        records.append(
            SubjectRecord(
                image_id=f"black_{i}",
                race="Black",
                gender="Female",
                age="20-29",
                true_label="1" if i < 20 else "0",
                predicted_label="1" if i < 15 else "0",
            )
        )
    return records


def test_aif360_backend_failure_isolation_emits_divergence_alert() -> None:
    """When AIF360 fails, orchestrator must flag divergence, not silently mask."""
    records = _make_dummy_records(40)
    orchestrator = CrossValidationOrchestrator(
        backends=[FairlearnBackend(), AIF360Backend()]
    )

    # Force AIF360 evaluate to simulate backend failure / fallback
    with patch.object(
        AIF360Backend, "evaluate", side_effect=RuntimeError("AIF360 internal error")
    ):
        canonical_results, divergences = orchestrator.run(
            records, protected_attr="race"
        )

    # Fairlearn still produces canonical results
    assert len(canonical_results) > 0

    # Divergence alerts must have been emitted for the unavailable AIF360 backend
    assert len(divergences) > 0
    nan_divergences = [d for d in divergences if math.isnan(d.difference)]
    assert len(nan_divergences) > 0
    assert any(d.backend_b.lower() == "aif360" for d in nan_divergences)


def test_live_cross_backend_consensus() -> None:
    """When both backends run normally, both produce results and statistical tests."""
    records = _make_dummy_records(40)
    orchestrator = CrossValidationOrchestrator(
        backends=[FairlearnBackend(), AIF360Backend()]
    )

    canonical_results, divergences = orchestrator.run(records, protected_attr="race")

    assert len(canonical_results) > 0
    # Every canonical result should have raw_p_value and adjusted_p_value populated
    for res in canonical_results:
        if not res.insufficient_sample and res.subgroup == "ALL":
            assert res.raw_p_value is not None
            assert res.adjusted_p_value is not None
            assert res.hypothesis_family in (
                "selection_rate",
                "tpr_conditional",
                "conditional_odds",
            )
            assert res.adjustment_method == "holm_bonferroni"
            assert res.ci_lower is not None
            assert res.ci_upper is not None
