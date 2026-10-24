"""Dataset adapters and registry for multi-benchmark ingestion (WP2 / Issue #20)."""

from __future__ import annotations

import logging
import re
from abc import ABC, abstractmethod
from typing import Any

from bias_aperture.schema import AGE_LABELS, GENDER_LABELS, RACE_LABELS

logger = logging.getLogger(__name__)

__all__ = [
    "DatasetAdapter",
    "DatasetRegistry",
    "FairFaceAdapter",
    "UTKFaceAdapter",
    "map_age_to_bracket",
]

# Regex for standard UTKFace filename format: [age]_[gender]_[race]_[date&time].jpg
UTKFACE_FILENAME_PATTERN = re.compile(
    r"^(?P<age>\d+)_(?P<gender>[01])_(?P<race>[0-4])_(?P<timestamp>\d+)"
)


def map_age_to_bracket(age_val: int | float | str) -> str:
    """Map continuous integer or float age to locked FairFace age brackets.

    Brackets: '0-2', '3-9', '10-19', '20-29', '30-39', '40-49', '50-59',
    '60-69', 'more than 70'.
    """
    try:
        age_int = int(float(age_val))
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Invalid age value for bracket mapping: {age_val}") from exc

    if age_int < 0:
        raise ValueError(f"Negative age value encountered: {age_int}")
    if age_int <= 2:
        return "0-2"
    if age_int <= 9:
        return "3-9"
    if age_int <= 19:
        return "10-19"
    if age_int <= 29:
        return "20-29"
    if age_int <= 39:
        return "30-39"
    if age_int <= 49:
        return "40-49"
    if age_int <= 59:
        return "50-59"
    if age_int <= 69:
        return "60-69"
    return "more than 70"


class DatasetAdapter(ABC):
    """Abstract base class for demographic dataset adapters."""

    name: str

    @property
    @abstractmethod
    def supported_attributes(self) -> tuple[str, ...]:
        """Demographic axes supported by the dataset."""
        ...

    @property
    @abstractmethod
    def label_limitations(self) -> tuple[str, ...]:
        """Documented label noise, taxonomy collapse, or sampling caveats."""
        ...

    @abstractmethod
    def normalize_record(self, raw_row: dict[str, Any]) -> dict[str, Any]:
        """Normalize raw dictionary into canonical locked schema vocabularies."""
        ...

    def parse_filename(self, filename: str) -> dict[str, Any] | None:
        """Parse demographic metadata encoded in the filename, if supported."""
        return None


class FairFaceAdapter(DatasetAdapter):
    """Dataset adapter for the canonical FairFace benchmark."""

    name = "fairface"

    @property
    def supported_attributes(self) -> tuple[str, ...]:
        return ("race", "gender", "age")

    @property
    def label_limitations(self) -> tuple[str, ...]:
        return (
            "Balanced 7-race taxonomy sampled across global demographic distributions.",
            (
                "Labels collected via 3-rater consensus Amazon Mechanical Turk "
                "annotations."
            ),
            "Age categorized into 9 distinct intervals.",
        )

    def normalize_record(self, raw_row: dict[str, Any]) -> dict[str, Any]:
        """Pass through standard FairFace row with canonical taxonomy validation."""
        normalized = dict(raw_row)
        # Standardize age alias '70+' -> 'more than 70' if needed
        age_val = normalized.get("age")
        if age_val == "70+":
            normalized["age"] = "more than 70"
        return normalized


class UTKFaceAdapter(DatasetAdapter):
    """Dataset adapter for UTKFace with label remapping & noise caveats."""

    name = "utkface"

    # UTKFace race mapping: 0: White, 1: Black, 2: Asian, 3: Indian, 4: Others
    UTK_RACE_MAP: dict[Any, str] = {
        0: "White",
        1: "Black",
        2: "East Asian",  # Taxonomy collapse: conflates East Asian and Southeast Asian
        3: "Indian",
        4: "Latino_Hispanic",  # Collapses Latino, Middle Eastern, etc.
        "0": "White",
        "1": "Black",
        "2": "East Asian",
        "3": "Indian",
        "4": "Latino_Hispanic",
        "white": "White",
        "black": "Black",
        "asian": "East Asian",
        "indian": "Indian",
        "others": "Latino_Hispanic",
        "other": "Latino_Hispanic",
    }

    UTK_GENDER_MAP: dict[Any, str] = {
        0: "Male",
        1: "Female",
        "0": "Male",
        "1": "Female",
        "male": "Male",
        "female": "Female",
        "m": "Male",
        "f": "Female",
    }

    @property
    def supported_attributes(self) -> tuple[str, ...]:
        return ("race", "gender", "age")

    @property
    def label_limitations(self) -> tuple[str, ...]:
        return (
            "DEX (Deep EXpectation) age estimates contain +/- 5 year label noise.",
            (
                "Race taxonomy collapse: 5-class model conflates East Asian and "
                "Southeast Asian."
            ),
            (
                "Category 4 ('Others') collapses Latino, Middle Eastern, "
                "and indigenous groups."
            ),
            "Intersectional distributions have substantial cohort sample imbalances.",
        )

    def parse_filename(self, filename: str) -> dict[str, Any] | None:
        """Extract age, gender, and race from standard UTKFace filename."""
        base_name = filename.split("/")[-1].split("\\")[-1]
        match = UTKFACE_FILENAME_PATTERN.match(base_name)
        if not match:
            return None

        raw_age = int(match.group("age"))
        raw_gender = int(match.group("gender"))
        raw_race = int(match.group("race"))

        return {
            "age": map_age_to_bracket(raw_age),
            "gender": self.UTK_GENDER_MAP.get(raw_gender, "Male"),
            "race": self.UTK_RACE_MAP.get(raw_race, "White"),
        }

    def normalize_record(self, raw_row: dict[str, Any]) -> dict[str, Any]:
        """Normalize raw UTKFace tabular or filename data into canonical schema."""
        normalized = dict(raw_row)

        # 1. Attempt extraction from filename if demographic columns are missing
        img_id = normalized.get("face_name_align") or normalized.get("image_id") or ""
        parsed = self.parse_filename(str(img_id)) if img_id else None

        # 2. Race normalization
        race_val = normalized.get("race")
        if race_val is not None:
            race_key = str(race_val).strip().lower()
            if race_val in self.UTK_RACE_MAP:
                normalized["race"] = self.UTK_RACE_MAP[race_val]
            elif race_key in self.UTK_RACE_MAP:
                normalized["race"] = self.UTK_RACE_MAP[race_key]
            elif race_val not in RACE_LABELS and parsed and "race" in parsed:
                normalized["race"] = parsed["race"]
        elif parsed and "race" in parsed:
            normalized["race"] = parsed["race"]

        # 3. Gender normalization
        gender_val = normalized.get("gender")
        if gender_val is not None:
            gender_key = str(gender_val).strip().lower()
            if gender_val in self.UTK_GENDER_MAP:
                normalized["gender"] = self.UTK_GENDER_MAP[gender_val]
            elif gender_key in self.UTK_GENDER_MAP:
                normalized["gender"] = self.UTK_GENDER_MAP[gender_key]
            elif gender_val not in GENDER_LABELS and parsed and "gender" in parsed:
                normalized["gender"] = parsed["gender"]
        elif parsed and "gender" in parsed:
            normalized["gender"] = parsed["gender"]

        # 4. Age normalization
        age_val = normalized.get("age")
        if age_val is not None:
            if age_val in AGE_LABELS:
                normalized["age"] = age_val
            elif age_val == "70+":
                normalized["age"] = "more than 70"
            else:
                try:
                    normalized["age"] = map_age_to_bracket(age_val)
                except ValueError:
                    if parsed and "age" in parsed:
                        normalized["age"] = parsed["age"]
        elif parsed and "age" in parsed:
            normalized["age"] = parsed["age"]

        return normalized


class DatasetRegistry:
    """Central registry for dataset adapters."""

    _registry: dict[str, type[DatasetAdapter]] = {
        "fairface": FairFaceAdapter,
        "utkface": UTKFaceAdapter,
    }

    @classmethod
    def register(cls, adapter_cls: type[DatasetAdapter]) -> type[DatasetAdapter]:
        """Register a new dataset adapter class."""
        cls._registry[adapter_cls.name.lower()] = adapter_cls
        return adapter_cls

    @classmethod
    def get(cls, name: str) -> DatasetAdapter:
        """Retrieve an initialized dataset adapter instance by name."""
        key = name.strip().lower()
        if key not in cls._registry:
            valid = sorted(cls._registry.keys())
            raise ValueError(
                f"Unknown dataset '{name}'. Available registered datasets: {valid}"
            )
        return cls._registry[key]()

    @classmethod
    def list_datasets(cls) -> list[str]:
        """Return list of registered dataset names."""
        return sorted(cls._registry.keys())
