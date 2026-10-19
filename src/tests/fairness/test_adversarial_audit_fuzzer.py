"""Unit tests for BiasAperture Adversarial Audit Fuzzer."""

from bias_aperture.fairness.adversarial_audit_fuzzer import BiasAdversarialAuditFuzzer
from bias_aperture.schema import MIN_SUBGROUP_SAMPLE_SIZE


def test_generate_boundary_starvation_cohort():
    fuzzer = BiasAdversarialAuditFuzzer()
    cohort = fuzzer.generate_boundary_starvation_cohort()
    assert len(cohort) == (MIN_SUBGROUP_SAMPLE_SIZE - 1) + (
        MIN_SUBGROUP_SAMPLE_SIZE + 1
    )
    under_count = sum(1 for r in cohort if r.race == "Black")
    safe_count = sum(1 for r in cohort if r.race == "White")
    assert under_count == 29
    assert safe_count == 31


def test_generate_intersectional_skew_cohort():
    fuzzer = BiasAdversarialAuditFuzzer(seed=123)
    cohort = fuzzer.generate_intersectional_skew_cohort(total_subjects=100)
    assert len(cohort) == 100
    assert all(r.true_label == "1" for r in cohort)
    assert any(r.predicted_label in ("0", "1") for r in cohort)


def test_evaluate_demographic_parity_barrier():
    fuzzer = BiasAdversarialAuditFuzzer()
    h_safe, stat_safe = fuzzer.evaluate_demographic_parity_barrier(
        0.04, max_tolerable_gap=0.10
    )
    assert h_safe > 0.0
    assert stat_safe == "PARITY_SAFE"

    h_breach, stat_breach = fuzzer.evaluate_demographic_parity_barrier(
        0.18, max_tolerable_gap=0.10
    )
    assert h_breach < 0.0
    assert stat_breach == "DISPARITY_BREACH"


def test_run_full_adversarial_gauntlet():
    fuzzer = BiasAdversarialAuditFuzzer()
    results = fuzzer.run_full_adversarial_gauntlet()
    assert len(results["reports"]) >= 2
    assert results["runtime_ms"] < 250.0
    assert results["min_subgroup_limit"] == 30
