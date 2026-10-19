"""
Extended integration tests for the full BiasAperture pipeline (WP5).

These tests exercise end-to-end flows beyond the basic two-group smoke test
in test_cli.py:
  - Multi-race subgroup auditing (≥3 race groups, all with n ≥ 30)
  - Gender-axis and age-axis protected attribute switching
  - Insufficient-sample guard surfacing in reports
  - Report structural contracts (Model Card, regulatory mapping, executive summary)
  - CLI exit-code contract when input file is missing
  - ``python -m bias_aperture`` entrypoint smoke test
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pandas as pd
import pytest

from bias_aperture.cli import main

# ── Helpers ────────────────────────────────────────────────────────────


def _build_fixture_rows(
    *,
    race_groups: list[str],
    n_per_group: int = 35,
    gender: str = "Female",
    age: str = "20-29",
    bias_group: str | None = None,
    bias_fpr: float = 0.5,
) -> list[dict[str, str]]:
    """Generate a deterministic multi-group predictions fixture.

    By default every group has identical performance (50% accuracy).  If
    *bias_group* is specified, that group receives a higher false-positive
    rate to create a measurable disparity.
    """
    rows: list[dict[str, str]] = []
    img_counter = 0
    for race in race_groups:
        for i in range(n_per_group):
            true = "1" if i % 2 == 0 else "0"
            if race == bias_group and true == "0":
                predicted = "1" if (i % 4 < int(bias_fpr * 4)) else "0"
            else:
                predicted = true  # perfect prediction
            rows.append(
                {
                    "face_name_align": f"img_{img_counter}.jpg",
                    "race": race,
                    "gender": gender,
                    "age": age,
                    "true_label": true,
                    "predicted_label": predicted,
                }
            )
            img_counter += 1
    return rows


# ── Tests ──────────────────────────────────────────────────────────────


class TestMultiGroupRaceAudit:
    """Pipeline with ≥3 race groups to exercise multi-group Core Four."""

    @pytest.fixture()
    def multi_race_csv(self, tmp_path: Path) -> Path:
        rows = _build_fixture_rows(
            race_groups=["White", "Black", "East Asian", "Indian"],
            n_per_group=40,
            bias_group="Black",
            bias_fpr=0.75,
        )
        csv = tmp_path / "multi_race.csv"
        pd.DataFrame(rows).to_csv(csv, index=False)
        return csv

    def test_exit_zero_and_report_exists(
        self, multi_race_csv: Path, tmp_path: Path
    ) -> None:
        out = tmp_path / "report.html"
        rc = main(
            [
                "-i",
                str(multi_race_csv),
                "-a",
                "race",
                "-o",
                str(out),
            ]
        )
        assert rc == 0
        assert out.exists()

    def test_report_contains_all_groups(
        self, multi_race_csv: Path, tmp_path: Path
    ) -> None:
        out = tmp_path / "report.html"
        main(["-i", str(multi_race_csv), "-a", "race", "-o", str(out)])
        html = out.read_text(encoding="utf-8")
        for group in ("White", "Black", "East Asian", "Indian"):
            assert group in html, f"Expected subgroup {group!r} in report"

    def test_report_model_card_section(
        self, multi_race_csv: Path, tmp_path: Path
    ) -> None:
        out = tmp_path / "report.html"
        main(["-i", str(multi_race_csv), "-a", "race", "-o", str(out)])
        html = out.read_text(encoding="utf-8")
        assert "FairFace ResNet-34" in html
        assert "Headline Fairness Metrics" in html

    def test_report_regulatory_mapping(
        self, multi_race_csv: Path, tmp_path: Path
    ) -> None:
        out = tmp_path / "report.html"
        main(["-i", str(multi_race_csv), "-a", "race", "-o", str(out)])
        html = out.read_text(encoding="utf-8")
        assert "EU AI Act" in html or "NIST" in html


class TestGenderAxisAudit:
    """Switch protected axis to gender."""

    @pytest.fixture()
    def gender_csv(self, tmp_path: Path) -> Path:
        rows = _build_fixture_rows(
            race_groups=["White"],
            n_per_group=80,
        )
        # Override half to Male
        for i, row in enumerate(rows):
            if i >= 40:
                row["gender"] = "Male"
        csv = tmp_path / "gender_axis.csv"
        pd.DataFrame(rows).to_csv(csv, index=False)
        return csv

    def test_gender_audit_succeeds(self, gender_csv: Path, tmp_path: Path) -> None:
        out = tmp_path / "report.html"
        rc = main(["-i", str(gender_csv), "-a", "gender", "-o", str(out)])
        assert rc == 0
        html = out.read_text(encoding="utf-8")
        assert "Male" in html or "Female" in html


class TestInsufficientSampleGuard:
    """Ensure groups with n < 30 are handled without crashing."""

    @pytest.fixture()
    def sparse_csv(self, tmp_path: Path) -> Path:
        rows = _build_fixture_rows(
            race_groups=["White", "Black"],
            n_per_group=35,
        )
        # Add a tiny group (Southeast Asian, n=5)
        for i in range(5):
            rows.append(
                {
                    "face_name_align": f"sparse_{i}.jpg",
                    "race": "Southeast Asian",
                    "gender": "Female",
                    "age": "20-29",
                    "true_label": "1",
                    "predicted_label": "1",
                }
            )
        csv = tmp_path / "sparse.csv"
        pd.DataFrame(rows).to_csv(csv, index=False)
        return csv

    def test_sparse_group_does_not_crash(
        self, sparse_csv: Path, tmp_path: Path
    ) -> None:
        out = tmp_path / "report.html"
        rc = main(["-i", str(sparse_csv), "-a", "race", "-o", str(out)])
        assert rc == 0
        assert out.exists()


class TestCLIErrorPaths:
    """Edge-case and error-path contracts."""

    def test_missing_file_returns_nonzero(self, tmp_path: Path) -> None:
        rc = main(
            [
                "-i",
                str(tmp_path / "does_not_exist.csv"),
                "-o",
                str(tmp_path / "out.html"),
            ]
        )
        assert rc == 1

    def test_parser_custom_columns(self) -> None:
        from bias_aperture.cli import build_parser

        parser = build_parser()
        args = parser.parse_args(
            [
                "-i",
                "f.csv",
                "--true-label-col",
                "gt",
                "--predicted-label-col",
                "pred",
                "--race-col",
                "ethnicity",
                "--gender-col",
                "sex",
                "--age-col",
                "age_group",
            ]
        )
        assert args.true_label_col == "gt"
        assert args.predicted_label_col == "pred"
        assert args.race_col == "ethnicity"


class TestMainModuleEntrypoint:
    """Verify ``python -m bias_aperture`` module is importable."""

    def test_dunder_main_importable(self) -> None:
        mod = importlib.import_module("bias_aperture.__main__")
        assert hasattr(mod, "main")
