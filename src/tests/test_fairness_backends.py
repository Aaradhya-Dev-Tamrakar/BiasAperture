"""
Integration tests for Fairness Backends and CrossValidationOrchestrator (WP4).
"""

from __future__ import annotations

import pytest

from bias_aperture.fairness.backends import (
    AIF360Backend,
    CrossValidationOrchestrator,
    FairlearnBackend,
)
from bias_aperture.schema import SubjectRecord


def test_fairlearn_and_aif360_backends_on_replicated_matrix() -> None:
    # 8-record known-answer block replicated x8 (n=64, 32 White, 32 Black)
    single_block = [
        ("White", "1", "1"),
        ("White", "1", "1"),
        ("White", "0", "1"),
        ("White", "0", "0"),
        ("Black", "1", "0"),
        ("Black", "1", "1"),
        ("Black", "0", "0"),
        ("Black", "0", "0"),
    ]

    records: list[SubjectRecord] = []
    for block_idx in range(8):
        for rec_idx, (race, true_lbl, pred_lbl) in enumerate(single_block):
            records.append(
                SubjectRecord(
                    image_id=f"img_{block_idx}_{rec_idx}",
                    race=race,  # type: ignore[arg-type]
                    gender="Female",
                    age="20-29",
                    true_label=true_lbl,
                    predicted_label=pred_lbl,
                )
            )

    orchestrator = CrossValidationOrchestrator(
        backends=[FairlearnBackend(), AIF360Backend()]
    )
    results, divergences = orchestrator.run(records, protected_attr="race")

    assert len(divergences) == 0  # Perfect consensus across harmonized backends
    assert len(results) > 0

    # Locate the ALL summary rows
    summary_map = {r.metric_name: r for r in results if r.subgroup == "ALL"}
    assert "demographic_parity_difference" in summary_map
    assert summary_map["demographic_parity_difference"].metric_value == pytest.approx(
        0.500, abs=1e-3
    )
    assert summary_map["equal_opportunity_difference"].metric_value == pytest.approx(
        0.500, abs=1e-3
    )
    assert summary_map["equalized_odds_difference"].metric_value == pytest.approx(
        0.500, abs=1e-3
    )
    assert summary_map["disparate_impact_ratio"].metric_value == pytest.approx(
        0.333, abs=1e-3
    )


def test_subgroup_sample_size_guard_in_backend() -> None:
    # Subgroup with n < 30 should yield insufficient_sample=True and metric_value=None
    records = [
        SubjectRecord(
            image_id=f"img_{i}",
            race="White" if i < 40 else "Black",  # Black has only 5 records (< 30)
            gender="Female",
            age="20-29",
            true_label="1",
            predicted_label="1",
        )
        for i in range(45)
    ]

    backend = FairlearnBackend()
    results = backend.evaluate(records, protected_attr="race")

    black_rows = [r for r in results if r.subgroup == "Black"]
    assert len(black_rows) > 0
    for r in black_rows:
        assert r.insufficient_sample is True
        assert r.metric_value is None
