"""Validation, cohort-profile, and configuration contracts for ingestion."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal

from bias_aperture.schema import (
    SubjectRecord,
)

# Canonical FairFace column names
DEFAULT_IMAGE_COL = "face_name_align"
DEFAULT_RACE_COL = "race"
DEFAULT_GENDER_COL = "gender"
DEFAULT_AGE_COL = "age"

# Common fallback column aliases for image identifiers
IMAGE_COL_ALIASES: tuple[str, ...] = (
    "face_name_align",
    "file",
    "image_id",
    "img_path",
    "filename",
)

# Raw labels emitted by upstream dataset/model implementations.
RAW_AGE_LABEL_ALIASES: dict[str, str] = {
    "more than 70": "70+",
}


class SchemaValidationError(ValueError):
    """
    Raised when data violates the locked schema or taxonomy in STRICT mode.
    """

    pass


class ValidationMode(str, Enum):
    """Validation behavior policy upon encountering invalid or corrupt data."""

    STRICT = "strict"  # Raise SchemaValidationError immediately on first anomaly
    PERMISSIVE = "permissive"  # Collect issues into summary, yield valid records


class ValidationSeverity(str, Enum):
    """Severity classification of validation anomalies."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """Individual data anomaly recorded during ingestion."""

    row_index: int | None
    image_id: str | None
    field_name: str
    value: Any
    issue_type: str
    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR


@dataclass(frozen=True, slots=True)
class ValidationSummary:
    """Aggregated report of data ingestion and validation results."""

    total_records_processed: int
    valid_records_passed: int
    rejected_records_count: int
    issues: list[ValidationIssue]
    issue_counts_by_type: dict[str, int]
    is_valid: bool = field(init=False)

    def __post_init__(self) -> None:
        has_errors = any(
            issue.severity == ValidationSeverity.ERROR for issue in self.issues
        )
        object.__setattr__(
            self,
            "is_valid",
            not has_errors and self.rejected_records_count == 0,
        )


@dataclass(frozen=True, slots=True)
class SubgroupCellStats:
    """Demographic cohort contingency support and eligibility status."""

    subgroup_key: str
    total_n: int
    positive_n: int | None
    negative_n: int | None
    is_nfr003_eligible: bool
    has_positive_support: bool
    has_negative_support: bool
    insufficient_sample_at_ingestion: bool


@dataclass(frozen=True, slots=True)
class SubgroupCohortProfile:
    """Demographic cohort distribution across all axes and composite strata."""

    total_subjects: int
    race_counts: dict[str, SubgroupCellStats]
    gender_counts: dict[str, SubgroupCellStats]
    age_counts: dict[str, SubgroupCellStats]
    intersectional_counts: dict[str, SubgroupCellStats]
    insufficient_subgroups: list[str]
    intersectional_126_counts: dict[str, SubgroupCellStats] = field(
        default_factory=dict
    )

    @property
    def eligible_126_cells(self) -> dict[str, SubgroupCellStats]:
        """Return all 126 intersectional cells meeting NFR-003 sample size (n >= 30)."""
        return {
            k: v
            for k, v in self.intersectional_126_counts.items()
            if v.is_nfr003_eligible
        }

    @property
    def insufficient_126_cells(self) -> dict[str, SubgroupCellStats]:
        """Return all 126 intersectional cells failing NFR-003 sample size (n < 30)."""
        return {
            k: v
            for k, v in self.intersectional_126_counts.items()
            if v.insufficient_sample_at_ingestion
        }

    @property
    def eligible_126_count(self) -> int:
        """Count of 126 intersectional cells with n >= 30."""
        return len(self.eligible_126_cells)

    @property
    def insufficient_126_count(self) -> int:
        """Count of 126 intersectional cells with n < 30."""
        return len(self.insufficient_126_cells)


@dataclass(frozen=True, slots=True)
class IngestionConfig:
    """Configuration options for data ingestion pipeline."""

    true_label_col: str
    predicted_label_col: str
    image_id_col: str = DEFAULT_IMAGE_COL
    race_col: str = DEFAULT_RACE_COL
    gender_col: str = DEFAULT_GENDER_COL
    age_col: str = DEFAULT_AGE_COL
    validation_mode: ValidationMode = ValidationMode.STRICT
    deduplicate_strategy: Literal[
        "keep_all", "drop_exact_or_raise_conflicts", "drop_duplicates"
    ] = "drop_exact_or_raise_conflicts"
    dataset: str = "fairface"


@dataclass(frozen=True, slots=True)
class IngestionResult:
    """Structured output returned by the data ingestion pipeline."""

    records: list[SubjectRecord]
    validation_summary: ValidationSummary
    cohort_profile: SubgroupCohortProfile | None
    dataset_name: str = "fairface"
    label_limitations: tuple[str, ...] = field(default_factory=tuple)
