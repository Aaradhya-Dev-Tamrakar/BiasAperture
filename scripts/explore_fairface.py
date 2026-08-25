"""
scripts/explore_fairface.py — exploration of the raw FairFace label CSVs
(fairface_label_train.csv / fairface_label_val.csv).

Loads each split's CSV, validates age/gender/race against the locked
vocabularies in schema.py, resolves each row's image path against
detected_faces/, and confirms the image exists on disk. Prints a
per-split summary: row counts, malformed rows, missing image files,
and age/gender/race distributions.

Operates on raw demographic annotations only (age, gender, race,
service_test) — no predictions. Building SubjectRecord instances with
true_label/predicted_label is a separate step, done after a model has
been run.

Usage:
    uv run python scripts/explore_fairface.py [DATA_ROOT]

DATA_ROOT defaults to data/raw/fairface and is expected to contain:
    fairface_label_train.csv
    fairface_label_val.csv
    detected_faces/
        train/
        val/
"""

from __future__ import annotations

import csv
import sys
from dataclasses import dataclass, field
from pathlib import Path

from bias_aperture.schema import AGE_LABELS, GENDER_LABELS, RACE_LABELS

EXPECTED_COLUMNS = {"file", "age", "gender", "race", "service_test"}

# Raw FairFace CSVs use 'more than 70'; schema.py's locked AGE_LABELS uses '70+'.
AGE_LABEL_ALIASES = {"more than 70": "70+"}


@dataclass
class SplitReport:
    split: str
    total_rows: int = 0
    valid_rows: int = 0
    missing_image_files: list[str] = field(default_factory=list)
    malformed_rows: list[tuple[int, str]] = field(default_factory=list)
    age_distribution: dict[str, int] = field(default_factory=dict)
    gender_distribution: dict[str, int] = field(default_factory=dict)
    race_distribution: dict[str, int] = field(default_factory=dict)

    @property
    def is_clean(self) -> bool:
        return not self.missing_image_files and not self.malformed_rows


def _parse_bool(raw: str) -> bool:
    v = raw.strip().lower()
    if v in ("true", "1", "yes"):
        return True
    if v in ("false", "0", "no"):
        return False
    raise ValueError(f"unrecognized boolean value: {raw!r}")


def explore_split(csv_path: Path, images_root: Path, split: str) -> SplitReport:
    report = SplitReport(split=split)

    if not csv_path.is_file():
        raise FileNotFoundError(f"label CSV not found: {csv_path}")

    race_set = set(RACE_LABELS)
    gender_set = set(GENDER_LABELS)
    age_set = set(AGE_LABELS)

    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or not EXPECTED_COLUMNS.issubset(set(reader.fieldnames)):
            raise ValueError(
                f"{csv_path} header {reader.fieldnames} is missing expected "
                f"columns {EXPECTED_COLUMNS}"
            )

        for line_no, row in enumerate(reader, start=2):  # header consumes line 1
            report.total_rows += 1
            try:
                image_id = row["file"].strip()
                age = row["age"].strip()
                age = AGE_LABEL_ALIASES.get(age, age)
                gender = row["gender"].strip()
                race = row["race"].strip()
                _parse_bool(row["service_test"])  # validated, value unused here

                if not image_id:
                    raise ValueError("empty file path")
                if age not in age_set:
                    raise ValueError(f"unrecognized age label: {age!r}")
                if gender not in gender_set:
                    raise ValueError(f"unrecognized gender label: {gender!r}")
                if race not in race_set:
                    raise ValueError(f"unrecognized race label: {race!r}")

            except (KeyError, ValueError) as exc:
                report.malformed_rows.append((line_no, str(exc)))
                continue

            image_path = images_root / image_id
            if not image_path.is_file():
                report.missing_image_files.append(image_id)
                continue

            report.valid_rows += 1
            report.age_distribution[age] = report.age_distribution.get(age, 0) + 1
            report.gender_distribution[gender] = report.gender_distribution.get(gender, 0) + 1
            report.race_distribution[race] = report.race_distribution.get(race, 0) + 1

    return report


def print_report(report: SplitReport) -> None:
    print(f"=== FairFace [{report.split}] exploration ===")
    print(f"  total rows read:      {report.total_rows}")
    print(f"  valid rows:           {report.valid_rows}")
    print(f"  malformed rows:       {len(report.malformed_rows)}")
    print(f"  missing image files:  {len(report.missing_image_files)}")

    if report.malformed_rows:
        print("  -- malformed row samples (up to 5) --")
        for line_no, reason in report.malformed_rows[:5]:
            print(f"     line {line_no}: {reason}")

    if report.missing_image_files:
        print("  -- missing file samples (up to 5) --")
        for path in report.missing_image_files[:5]:
            print(f"     {path}")

    for label, dist in (
        ("age", report.age_distribution),
        ("gender", report.gender_distribution),
        ("race", report.race_distribution),
    ):
        print(f"  -- {label} distribution --")
        for k, v in sorted(dist.items(), key=lambda kv: -kv[1]):
            pct = 100 * v / report.valid_rows if report.valid_rows else 0
            print(f"     {k:20s} {v:7d} ({pct:5.1f}%)")
    print()


def main() -> int:
    data_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/raw/fairface")

    if not data_root.exists():
        print(f"ERROR: data root not found: {data_root}", file=sys.stderr)
        return 1

    images_root = data_root / "detected_faces"
    exit_code = 0
    total_valid = 0

    for split in ("train", "val"):
        csv_path = data_root / f"fairface_label_{split}.csv"
        report = explore_split(csv_path, images_root, split)
        print_report(report)
        total_valid += report.valid_rows
        if not report.is_clean:
            exit_code = 1

    print(f"TOTAL valid records across all splits: {total_valid}")
    print(
        "\nExploration finished with warnings — see malformed/missing rows above."
        if exit_code
        else "\nExploration finished clean — 0 malformed rows, 0 missing files."
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())