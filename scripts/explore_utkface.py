"""
scripts/explore_utkface.py — exploration of the raw UTKFace image set.

UTKFace has no label CSV — every image's demographics are encoded in its
filename: [age]_[gender]_[race]_[date&time].jpg
    age:    integer, 0-116
    gender: 0 = male, 1 = female
    race:   0-4 -> White, Black, Asian, Indian, Others (Hispanic/Latino/
            Middle Eastern/etc.)

This script parses and validates those raw integer values directly. It
deliberately does NOT map race onto schema.py's locked RACE_LABELS
(FairFace's 7-category scheme). UTKFace's 5 categories don't split
cleanly into FairFace's 7 (its "Asian" doesn't separate into East/
Southeast Asian, and its "Others" doesn't cleanly separate into
Latino_Hispanic vs Middle Eastern) — that mapping is a judgment call
affecting data integrity project-wide, not something to decide inside
an exploration script. This script reports UTKFace's own raw categories
so that decision can be made with real distribution numbers in hand.

Usage:
    uv run python scripts/explore_utkface.py [IMAGES_DIR]

IMAGES_DIR defaults to data/raw/utkface/detected_faces and is expected
to contain the UTKFace images directly (flat, no subfolders).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

MIN_AGE = 0
MAX_AGE = 116

GENDER_CODES = {"0": "Male", "1": "Female"}
RACE_CODES = {
    "0": "White",
    "1": "Black",
    "2": "Asian",
    "3": "Indian",
    "4": "Others",
}

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png"}


@dataclass
class UtkExplorationReport:
    total_files: int = 0
    valid_files: int = 0
    malformed_filenames: list[tuple[str, str]] = field(default_factory=list)  # (filename, reason)
    age_min: int | None = None
    age_max: int | None = None
    age_bucket_distribution: dict[str, int] = field(default_factory=dict)
    gender_distribution: dict[str, int] = field(default_factory=dict)
    race_distribution: dict[str, int] = field(default_factory=dict)

    @property
    def is_clean(self) -> bool:
        return not self.malformed_filenames


def _age_bucket(age: int) -> str:
    """Bucket raw UTKFace age into human-readable ranges for reporting only.
    NOT the FairFace schema bins — just for a readable summary here."""
    if age <= 2:
        return "0-2"
    if age <= 9:
        return "3-9"
    if age <= 19:
        return "10-19"
    if age <= 29:
        return "20-29"
    if age <= 39:
        return "30-39"
    if age <= 49:
        return "40-49"
    if age <= 59:
        return "50-59"
    if age <= 69:
        return "60-69"
    return "70+"


def parse_utkface_filename(filename: str) -> tuple[int, str, str]:
    """
    Parse a UTKFace filename into (age, gender_code, race_code).
    Raises ValueError with a specific reason if the filename doesn't conform.
    """
    stem = Path(filename).stem
    parts = stem.split("_")

    if len(parts) < 4:
        raise ValueError(
            f"expected 4 underscore-separated fields (age_gender_race_date), "
            f"got {len(parts)}: {parts!r}"
        )

    age_str, gender_str, race_str = parts[0], parts[1], parts[2]

    if not age_str.isdigit():
        raise ValueError(f"non-integer age field: {age_str!r}")
    age = int(age_str)
    if not (MIN_AGE <= age <= MAX_AGE):
        raise ValueError(f"age {age} outside expected range [{MIN_AGE}, {MAX_AGE}]")

    if gender_str not in GENDER_CODES:
        raise ValueError(f"unrecognized gender code: {gender_str!r} (expected 0 or 1)")

    if race_str not in RACE_CODES:
        raise ValueError(f"unrecognized race code: {race_str!r} (expected 0-4)")

    return age, gender_str, race_str


def explore_utkface(images_dir: Path) -> UtkExplorationReport:
    report = UtkExplorationReport()

    if not images_dir.is_dir():
        raise FileNotFoundError(f"images directory not found: {images_dir}")

    for entry in sorted(images_dir.iterdir()):
        if not entry.is_file() or entry.suffix.lower() not in VALID_EXTENSIONS:
            continue

        report.total_files += 1
        try:
            age, gender_code, race_code = parse_utkface_filename(entry.name)
        except ValueError as exc:
            report.malformed_filenames.append((entry.name, str(exc)))
            continue

        report.valid_files += 1
        report.age_min = age if report.age_min is None else min(report.age_min, age)
        report.age_max = age if report.age_max is None else max(report.age_max, age)

        bucket = _age_bucket(age)
        report.age_bucket_distribution[bucket] = report.age_bucket_distribution.get(bucket, 0) + 1

        gender_label = GENDER_CODES[gender_code]
        report.gender_distribution[gender_label] = report.gender_distribution.get(gender_label, 0) + 1

        race_label = RACE_CODES[race_code]
        report.race_distribution[race_label] = report.race_distribution.get(race_label, 0) + 1

    return report


def print_report(report: UtkExplorationReport) -> None:
    print("=== UTKFace exploration ===")
    print(f"  total image files:    {report.total_files}")
    print(f"  valid (parsed) files: {report.valid_files}")
    print(f"  malformed filenames:  {len(report.malformed_filenames)}")
    if report.age_min is not None:
        print(f"  age range:            {report.age_min} - {report.age_max}")

    if report.malformed_filenames:
        print("  -- malformed filename samples (up to 5) --")
        for fname, reason in report.malformed_filenames[:5]:
            print(f"     {fname}: {reason}")

    print("  -- age distribution (readable buckets, NOT the FairFace schema bins) --")
    for k in ("0-2", "3-9", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70+"):
        v = report.age_bucket_distribution.get(k, 0)
        pct = 100 * v / report.valid_files if report.valid_files else 0
        print(f"     {k:20s} {v:7d} ({pct:5.1f}%)")

    print("  -- gender distribution --")
    for k, v in sorted(report.gender_distribution.items(), key=lambda kv: -kv[1]):
        pct = 100 * v / report.valid_files if report.valid_files else 0
        print(f"     {k:20s} {v:7d} ({pct:5.1f}%)")

    print("  -- race distribution (UTKFace's own 5 categories — NOT yet mapped to schema.RACE_LABELS) --")
    for k, v in sorted(report.race_distribution.items(), key=lambda kv: -kv[1]):
        pct = 100 * v / report.valid_files if report.valid_files else 0
        print(f"     {k:20s} {v:7d} ({pct:5.1f}%)")
    print()


def main() -> int:
    images_dir = (
        Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/raw/utkface/detected_faces")
    )

    if not images_dir.exists():
        print(f"ERROR: images directory not found: {images_dir}", file=sys.stderr)
        return 1

    report = explore_utkface(images_dir)
    print_report(report)

    if report.is_clean:
        print("Exploration finished clean — 0 malformed filenames.")
        return 0
    else:
        print("Exploration finished with warnings — see malformed filenames above.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())