"""Unit and integration tests for YAML audit configuration (WP5 / Issue #19)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from bias_aperture.cli import build_parser, main
from bias_aperture.config import AuditConfig, load_audit_config


def test_load_audit_config_nested(tmp_path: Path) -> None:
    """Verify loading structured configuration with 'audit' and 'report' sections."""
    cfg_file = tmp_path / "audit_nested.yaml"
    cfg_file.write_text(
        """
audit:
  predictions_file: "test_preds.csv"
  protected_attr: "gender"
  backend: "fairlearn"
  bca_resamples: 1500
  explain: false

report:
  output_report: "custom_report.html"
  model_name: "Custom ResNet"
  dataset_name: "Custom Dataset"
  model_description: "Audit description for testing."
""",
        encoding="utf-8",
    )

    loaded = load_audit_config(cfg_file)
    assert loaded["protected_attr"] == "gender"
    assert loaded["backend"] == "fairlearn"
    assert loaded["bca_resamples"] == 1500
    assert loaded["explain"] is False
    assert loaded["output_report"] == Path("custom_report.html")
    assert loaded["model_name"] == "Custom ResNet"
    assert loaded["dataset_name"] == "Custom Dataset"
    assert loaded["model_description"] == "Audit description for testing."


def test_load_audit_config_flat(tmp_path: Path) -> None:
    """Verify loading flat key-value YAML configuration."""
    cfg_file = tmp_path / "audit_flat.yaml"
    cfg_file.write_text(
        """
predictions_file: "flat_preds.csv"
protected_attr: "race"
backend: "aif360"
bca_resamples: 2000
explain: true
output_report: "flat_report.html"
""",
        encoding="utf-8",
    )

    loaded = load_audit_config(cfg_file)
    assert loaded["protected_attr"] == "race"
    assert loaded["backend"] == "aif360"
    assert loaded["bca_resamples"] == 2000
    assert loaded["explain"] is True
    assert loaded["output_report"] == Path("flat_report.html")


def test_load_audit_config_missing_file() -> None:
    """Verify FileNotFoundError when config file does not exist."""
    with pytest.raises(FileNotFoundError, match="Audit configuration file not found"):
        load_audit_config("nonexistent_audit_config_file_xyz.yaml")


def test_load_audit_config_malformed_yaml(tmp_path: Path) -> None:
    """Verify ValueError when YAML syntax is invalid."""
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text("audit: [unclosed list", encoding="utf-8")
    with pytest.raises(ValueError, match="Malformed YAML"):
        load_audit_config(bad_yaml)


def test_load_audit_config_invalid_root(tmp_path: Path) -> None:
    """Verify ValueError when YAML root is not a mapping."""
    list_yaml = tmp_path / "list.yaml"
    list_yaml.write_text("- item1\n- item2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="expected mapping"):
        load_audit_config(list_yaml)


def test_load_audit_config_invalid_protected_attr(tmp_path: Path) -> None:
    """Verify validation rejection of invalid protected attributes."""
    cfg_file = tmp_path / "invalid_attr.yaml"
    cfg_file.write_text("protected_attr: religion\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid 'protected_attr'"):
        load_audit_config(cfg_file)


def test_load_audit_config_invalid_backend(tmp_path: Path) -> None:
    """Verify validation rejection of unknown backend names."""
    cfg_file = tmp_path / "invalid_backend.yaml"
    cfg_file.write_text("backend: unknown_backend\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid 'backend'"):
        load_audit_config(cfg_file)


def test_load_audit_config_bca_resamples_too_low(tmp_path: Path) -> None:
    """Verify rejection of bootstrap resample budget below statistical minimum."""
    cfg_file = tmp_path / "low_bca.yaml"
    cfg_file.write_text("bca_resamples: 500\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Must be >= 1000"):
        load_audit_config(cfg_file)


def test_load_audit_config_invalid_format(tmp_path: Path) -> None:
    """Verify validation rejection of unsupported report formats."""
    cfg_file = tmp_path / "invalid_fmt.yaml"
    cfg_file.write_text("format: docx\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid 'format'"):
        load_audit_config(cfg_file)


def test_audit_config_dataclass_methods(tmp_path: Path) -> None:
    """Verify AuditConfig.from_yaml and to_dict methods."""
    cfg_file = tmp_path / "audit_obj.yaml"
    cfg_file.write_text(
        """
audit:
  protected_attr: "age"
  backend: "dual"
  bca_resamples: 1200
""",
        encoding="utf-8",
    )

    obj = AuditConfig.from_yaml(cfg_file)
    assert obj.protected_attr == "age"
    assert obj.backend == "dual"
    assert obj.bca_resamples == 1200
    assert obj.explain is True  # default preserved

    d = obj.to_dict()
    assert d["protected_attr"] == "age"
    assert d["bca_resamples"] == 1200


def test_cli_parser_defaults_with_config(tmp_path: Path) -> None:
    """Verify build_parser integrates config defaults correctly."""
    cfg_file = tmp_path / "defaults.yaml"
    cfg_file.write_text(
        """
protected_attr: "gender"
backend: "fairlearn"
bca_resamples: 2500
""",
        encoding="utf-8",
    )

    loaded = load_audit_config(cfg_file)
    parser = build_parser(config_defaults=loaded)
    args = parser.parse_args(["-i", "preds.csv"])
    assert args.protected_attr == "gender"
    assert args.backend == "fairlearn"
    assert args.bca_resamples == 2500


def test_cli_flags_override_config_defaults(tmp_path: Path) -> None:
    """Verify CLI flags take precedence over YAML configuration defaults."""
    pred_csv = tmp_path / "synthetic_preds.csv"
    _create_synthetic_csv(pred_csv)

    cfg_file = tmp_path / "override_test.yaml"
    cfg_file.write_text(
        f"""
audit:
  predictions_file: "{pred_csv.as_posix()}"
  protected_attr: "gender"
  backend: "fairlearn"
  bca_resamples: 1000
""",
        encoding="utf-8",
    )

    out_report = tmp_path / "override_report.html"

    # Override protected_attr to "race" and backend to "dual" via CLI flags
    rc = main(
        [
            "--config",
            str(cfg_file),
            "--protected-attr",
            "race",
            "--backend",
            "dual",
            "-o",
            str(out_report),
        ]
    )
    assert rc == 0
    assert out_report.exists()
    content = out_report.read_text(encoding="utf-8")
    assert "Protected Attribute: race" in content or "race" in content


def test_cli_config_missing_predictions_file(tmp_path: Path) -> None:
    """Verify exit code 2 when neither config nor CLI specifies predictions file."""
    cfg_file = tmp_path / "no_pred.yaml"
    cfg_file.write_text("protected_attr: race\n", encoding="utf-8")
    rc = main(["--config", str(cfg_file)])
    assert rc == 2


def test_cli_config_nonexistent_file() -> None:
    """Verify exit code 1 when --config points to non-existent file."""
    rc = main(["--config", "nonexistent_file_definitely_not_here.yaml"])
    assert rc == 1


def test_cli_end_to_end_from_config(tmp_path: Path) -> None:
    """Verify running complete audit directly from a YAML configuration file."""
    pred_csv = tmp_path / "complete_audit_preds.csv"
    _create_synthetic_csv(pred_csv)

    out_report = tmp_path / "config_driven_report.html"

    cfg_file = tmp_path / "full_audit.yaml"
    cfg_file.write_text(
        f"""
audit:
  predictions_file: "{pred_csv.as_posix()}"
  protected_attr: "race"
  backend: "dual"
  bca_resamples: 1000
  explain: true

report:
  output_report: "{out_report.as_posix()}"
  model_name: "Declarative Model Card"
  dataset_name: "Declarative FairFace Benchmark"
""",
        encoding="utf-8",
    )

    rc = main(["--config", str(cfg_file)])
    assert rc == 0
    assert out_report.exists()
    content = out_report.read_text(encoding="utf-8")
    assert "Headline Fairness Metrics" in content
    assert "Declarative Model Card" in content
    assert "Declarative FairFace Benchmark" in content


def _create_synthetic_csv(path: Path) -> None:
    """Generate minimal valid FairFace prediction dataset for audit testing."""
    single_block = [
        ("White", "Female", "20-29", "1", "1"),
        ("White", "Female", "20-29", "1", "1"),
        ("White", "Female", "20-29", "0", "1"),
        ("White", "Female", "20-29", "0", "0"),
        ("Black", "Female", "20-29", "1", "0"),
        ("Black", "Female", "20-29", "1", "1"),
        ("Black", "Female", "20-29", "0", "0"),
        ("Black", "Female", "20-29", "0", "0"),
    ]
    rows = []
    for b in range(8):
        for idx, (race, gender, age, true_lbl, pred_lbl) in enumerate(single_block):
            rows.append(
                {
                    "face_name_align": f"img_{b}_{idx}.jpg",
                    "race": race,
                    "gender": gender,
                    "age": age,
                    "true_label": true_lbl,
                    "predicted_label": pred_lbl,
                }
            )
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)
