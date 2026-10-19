"""Runtime counterexamples from the October 1 independent verification."""

from __future__ import annotations

import builtins
from dataclasses import replace
from unittest.mock import Mock

import numpy as np
import pandas as pd
import pytest
from fairlearn import metrics as fm

from bias_aperture.cli import main
from bias_aperture.explainability import ShapExplainerEngine
from bias_aperture.fairness.backends import (
    AIF360Backend,
    CrossValidationOrchestrator,
    FairlearnBackend,
)
from bias_aperture.fairness.metrics import compute_group_rates
from bias_aperture.schema import MetricResult, SubjectRecord


def records_fixture():
    """Two n=100 groups: TPR .8/.7, FPR .1/.4."""
    return [
        SubjectRecord(
            f"{race}-{i}",
            race,
            "Male" if i % 2 else "Female",
            "20-29",
            str(int(i < 50)),
            str(int(i < tp or 50 <= i < 50 + fp)),
        )
        for race, tp, fp in [("White", 40, 5), ("Black", 35, 20)]
        for i in range(100)
    ]


def flagged_metric():
    return MetricResult(
        metric_name="demographic_parity_difference",
        subgroup="ALL",
        subgroup_sample_size=200,
        metric_value=0.5,
        ci_lower=0.4,
        ci_upper=0.6,
        p_value=0.001,
    )


@pytest.mark.parametrize("labels", [("a", "b", "c"), ("0", "1", "2"), (0, 1, 2)])
@pytest.mark.parametrize("backend", [FairlearnBackend, AIF360Backend])
def test_public_backend_rejects_multiclass(labels, backend):
    records = [
        replace(r, true_label=labels[i % 3], predicted_label=labels[(i + 1) % 3])
        for i, r in enumerate(records_fixture())
    ]
    with pytest.raises(ValueError, match="One-vs-Rest.*not implemented"):
        backend().evaluate(records, "race")
    with pytest.raises(ValueError, match="at most two task labels"):
        CrossValidationOrchestrator([backend()]).run(records, "race")


@pytest.mark.parametrize("labels", [("a", "b", "c"), ("0", "1", "2")])
def test_cli_rejects_multiclass_without_report(tmp_path, caplog, labels):
    records = [
        replace(r, true_label=labels[i % 3], predicted_label=labels[(i + 1) % 3])
        for i, r in enumerate(records_fixture())
    ]
    source = write_csv(tmp_path, records)
    report = tmp_path / "out.html"
    assert main(["-i", str(source), "-o", str(report)]) == 1
    assert not report.exists()
    assert "at most two task labels" in caplog.text


@pytest.mark.parametrize("bad", [2, 0.7, -1])
def test_binary_rate_primitive_rejects_unencoded_values(bad):
    with pytest.raises(ValueError, match="encoded binary"):
        compute_group_rates(np.array([0, 1]), np.array([0, bad]), np.array(["A", "B"]))


def test_fairlearn_api_is_executed(monkeypatch):
    spies = {}
    for name in ["selection_rate", "true_positive_rate", "false_positive_rate"]:
        spies[name] = Mock(wraps=getattr(fm, name))
        monkeypatch.setattr(fm, name, spies[name])
    results = FairlearnBackend().evaluate(records_fixture(), "race")
    assert all(spy.call_count >= 2 for spy in spies.values())
    assert all(
        0 <= row.metric_value <= 1 for row in results if row.metric_value is not None
    )
    summary = {r.metric_name: r.metric_value for r in results if r.subgroup == "ALL"}
    assert summary["equalized_odds_difference"] == pytest.approx(0.3)
    assert summary["equal_opportunity_difference"] == pytest.approx(0.1)
    assert summary["demographic_parity_difference"] == pytest.approx(0.1)
    assert summary["disparate_impact_ratio"] == pytest.approx(9 / 11)


def write_csv(tmp_path, records):
    from dataclasses import asdict

    source = tmp_path / "predictions.csv"
    pd.DataFrame([asdict(r) for r in records]).to_csv(source, index=False)
    return source


def block_fairlearn(monkeypatch):
    original = builtins.__import__

    def blocked(name, *args, **kwargs):
        if name == "fairlearn" or name.startswith("fairlearn."):
            raise ImportError("Fairlearn deliberately blocked")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked)


def test_missing_fairlearn_fails_clearly_in_backend_and_cli(
    monkeypatch, tmp_path, caplog
):
    source = write_csv(tmp_path, records_fixture())
    block_fairlearn(monkeypatch)
    with pytest.raises(RuntimeError, match="Fairlearn is unavailable"):
        FairlearnBackend().evaluate(records_fixture(), "race")
    report = tmp_path / "out.html"
    assert main(["-i", str(source), "--backend", "fairlearn", "-o", str(report)]) == 1
    assert not report.exists()
    assert "--extra fairness" in caplog.text


def test_secondary_backend_failure_is_visible_in_report(monkeypatch, tmp_path):
    source = write_csv(tmp_path, records_fixture())
    monkeypatch.setattr(
        AIF360Backend, "evaluate", Mock(side_effect=RuntimeError("offline"))
    )
    report = tmp_path / "out.html"
    assert main(["-i", str(source), "--no-explain", "-o", str(report)]) == 0
    html = report.read_text(encoding="utf-8")
    assert "Cross-library validation incomplete. Unavailable backend(s): aif360" in html
    assert "Both backend executions completed" not in html


def test_unavailable_aif360_canonical_backend_prevents_report(monkeypatch, tmp_path):
    source = write_csv(tmp_path, records_fixture())
    unavailable = AIF360Backend()._unavailable_results(
        ["White", "Black"], 200, "offline"
    )
    monkeypatch.setattr(AIF360Backend, "evaluate", Mock(return_value=unavailable))
    report = tmp_path / "out.html"
    assert main(["-i", str(source), "--backend", "aif360", "-o", str(report)]) == 1
    assert not report.exists()


def test_equivalent_binary_encodings_match_metrics_and_explanations():
    numeric = records_fixture()
    categorical = [
        replace(
            r,
            true_label="Male" if r.true_label == "1" else "Female",
            predicted_label="Male" if r.predicted_label == "1" else "Female",
        )
        for r in numeric
    ]
    backend = FairlearnBackend()
    assert backend.evaluate(numeric, "race") == backend.evaluate(categorical, "race")
    engine = ShapExplainerEngine()
    first = engine.explain_disparity(flagged_metric(), records=numeric)
    second = engine.explain_disparity(flagged_metric(), records=categorical)
    assert first.feature_attributions
    assert first.feature_attributions == pytest.approx(second.feature_attributions)


def test_cli_no_explain_prevents_invocation(monkeypatch, tmp_path):
    source = write_csv(tmp_path, records_fixture())
    spy = Mock(side_effect=AssertionError("explainer must not run"))
    monkeypatch.setattr(ShapExplainerEngine, "explain_disparity", spy)
    assert (
        main(
            [
                "audit",
                "-i",
                str(source),
                "--no-explain",
                "--backend",
                "fairlearn",
                "-o",
                str(tmp_path / "out.html"),
            ]
        )
        == 0
    )
    spy.assert_not_called()


def test_pipeline_retains_attributions_in_generated_report(tmp_path):
    records = [
        replace(r, predicted_label="1" if r.race == "White" else "0")
        for r in records_fixture()
    ]
    source = write_csv(tmp_path, records)
    report = tmp_path / "out.html"
    assert main(["-i", str(source), "--backend", "fairlearn", "-o", str(report)]) == 0
    html = report.read_text(encoding="utf-8")
    assert "Demographic Surrogate Associations" in html
    assert "race_White" in html
    assert "surrogate log-odds" in html


def test_surrogate_unavailable_is_not_reported_as_generated(monkeypatch):
    engine = ShapExplainerEngine()
    assert "unavailable" in engine.explain_disparity(flagged_metric()).details
    assert not engine.should_explain(replace(flagged_metric(), p_value=None))
    from sklearn.linear_model import LogisticRegression

    monkeypatch.setattr(
        LogisticRegression, "fit", Mock(side_effect=RuntimeError("fit failed"))
    )
    result = engine.explain_disparity(flagged_metric(), records=records_fixture())
    assert not result.feature_attributions
    assert "unavailable: fit failed" in result.details
