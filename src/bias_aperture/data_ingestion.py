"""
Data Ingestion & Invariant Validation Engine — WP2 (Stream A).

Transforms raw prediction outputs (CSV, JSON, DataFrames, dictionaries)
into validated, strongly-typed SubjectRecord streams according to the
locked M1 schema (src/bias_aperture/schema.py).

Features:
- Dual-mode validation: STRICT (fail-fast) vs PERMISSIVE (profiling summary).
- Exact demographic taxonomy validation (RACE_LABELS, GENDER_LABELS, AGE_LABELS).
- Duplicate handling with conflict detection across image IDs.
- Subgroup cohort profiling: sample sizes (n_a), positive support (n_{Y=1,a}),
  negative support (n_{Y=0,a}), and NFR-003 threshold screening (n >= 30).
- Multi-class One-vs-Rest (OvR) transformation for targets with M > 2 classes.
"""

from __future__ import annotations

import json
import logging
from collections import Counter
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

import pandas as pd

from bias_aperture.ingestion_contracts import (
    DEFAULT_AGE_COL,
    DEFAULT_GENDER_COL,
    DEFAULT_IMAGE_COL,
    DEFAULT_RACE_COL,
    IMAGE_COL_ALIASES,
    RAW_AGE_LABEL_ALIASES,
    IngestionConfig,
    IngestionResult,
    SchemaValidationError,
    SubgroupCellStats,
    SubgroupCohortProfile,
    ValidationIssue,
    ValidationMode,
    ValidationSeverity,
    ValidationSummary,
)
from bias_aperture.ingestion_validation import IngestionValidator
from bias_aperture.schema import (
    AGE_LABELS,
    GENDER_LABELS,
    MIN_POSITIVE_SUPPORT,
    MIN_SUBGROUP_SAMPLE_SIZE,
    RACE_LABELS,
    SubjectRecord,
    format_intersectional_key,
)
from bias_aperture.transformations import OvRTransformer

logger = logging.getLogger(__name__)

__all__ = [
    "DEFAULT_AGE_COL",
    "DEFAULT_GENDER_COL",
    "DEFAULT_IMAGE_COL",
    "DEFAULT_RACE_COL",
    "IMAGE_COL_ALIASES",
    "IngestionConfig",
    "IngestionResult",
    "OvRTransformer",
    "RAW_AGE_LABEL_ALIASES",
    "SchemaValidationError",
    "SubgroupCellStats",
    "SubgroupCohortProfile",
    "ValidationIssue",
    "ValidationMode",
    "ValidationSeverity",
    "ValidationSummary",
    "DataIngestionPipeline",
    "IngestionValidator",
    "AGE_LABELS",
    "GENDER_LABELS",
    "MIN_POSITIVE_SUPPORT",
    "MIN_SUBGROUP_SAMPLE_SIZE",
    "RACE_LABELS",
    "format_intersectional_key",
]


class DataIngestionPipeline(IngestionValidator):
    """
    Ingests, validates, profiles, and standardizes demographic prediction datasets.
    """

    def __init__(self, config: IngestionConfig) -> None:
        self.config = config

    def ingest_file(
        self,
        path: str | Path,
        *,
        task_positive_label: str | None = None,
    ) -> IngestionResult:
        """Ingest records from a CSV or JSON file on disk."""
        target_path = Path(path)
        if not target_path.exists():
            raise FileNotFoundError(f"predictions file not found: {target_path}")

        suffix = target_path.suffix.lower()
        if suffix == ".csv":
            df = pd.read_csv(target_path)
            return self.ingest_dataframe(df, task_positive_label=task_positive_label)
        elif suffix == ".json":
            with target_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                data = data.get("records", data.get("data", [data]))
            return self.ingest_records(data, task_positive_label=task_positive_label)
        else:
            raise ValueError(
                f"unsupported predictions-file extension: {suffix} "
                "(FR-002 specifies CSV or JSON only)"
            )

    def ingest_dataframe(
        self,
        df: pd.DataFrame,
        *,
        task_positive_label: str | None = None,
    ) -> IngestionResult:
        """Ingest records from a pandas DataFrame."""
        rows = df.to_dict(orient="records")
        return self.ingest_records(rows, task_positive_label=task_positive_label)

    def ingest_records(
        self,
        rows: Iterable[dict[str, Any]],
        *,
        task_positive_label: str | None = None,
    ) -> IngestionResult:
        """Ingest and validate an iterable of dictionary rows."""
        resolved_rows = list(rows)
        total_count = len(resolved_rows)

        if total_count == 0:
            summary = ValidationSummary(
                total_records_processed=0,
                valid_records_passed=0,
                rejected_records_count=0,
                issues=[],
                issue_counts_by_type={},
            )
            profile = self.compute_cohort_profile(
                [], task_positive_label=task_positive_label
            )
            return IngestionResult(
                records=[],
                validation_summary=summary,
                cohort_profile=profile,
            )

        # Stage 1: Column presence validation
        first_row = resolved_rows[0]
        actual_image_col = self._resolve_image_col(first_row)
        col_result = self._validate_columns(first_row, total_count)
        if col_result is not None:
            return col_result

        # Stage 2: Per-row validation, taxonomy normalisation, dedup
        valid_records: list[SubjectRecord] = []
        issues: list[ValidationIssue] = []
        seen_images: dict[str, tuple[Any, Any, Any, Any, Any]] = {}
        issue_counter: Counter[str] = Counter()

        for idx, row in enumerate(resolved_rows):
            # 2a: Image ID extraction
            row_image_id = row.get(actual_image_col)
            if pd.isna(row_image_id) or str(row_image_id).strip() == "":
                issue = ValidationIssue(
                    row_index=idx,
                    image_id=None,
                    field_name=actual_image_col,
                    value=row_image_id,
                    issue_type="invalid_image_id",
                    message=f"Missing or empty image identifier at row {idx}",
                )
                self._handle_issue(issue, issues, issue_counter)
                continue

            image_id_str = str(row_image_id)

            # 2b: Per-row field validation and taxonomy normalisation
            record = self._validate_and_convert_row(
                idx, row, image_id_str, issues, issue_counter
            )
            if record is None:
                continue

            # 2c: Duplicate detection and conflict resolution
            row_signature = (
                record.race,
                record.gender,
                record.age,
                record.true_label,
                record.predicted_label,
            )
            if self._check_duplicate(
                idx, image_id_str, row_signature, seen_images, issues, issue_counter
            ):
                continue

            seen_images[image_id_str] = row_signature
            valid_records.append(record)

        summary = ValidationSummary(
            total_records_processed=total_count,
            valid_records_passed=len(valid_records),
            rejected_records_count=total_count - len(valid_records),
            issues=issues,
            issue_counts_by_type=dict(issue_counter),
        )

        profile = self.compute_cohort_profile(
            valid_records, task_positive_label=task_positive_label
        )

        return IngestionResult(
            records=valid_records,
            validation_summary=summary,
            cohort_profile=profile,
        )

    @classmethod
    def compute_cohort_profile(
        cls,
        records: Sequence[SubjectRecord],
        *,
        task_positive_label: str | None = None,
    ) -> SubgroupCohortProfile:
        """Compute subgroup support through the cohort-profiling module."""
        from bias_aperture.cohort_profiling import compute_cohort_profile

        return compute_cohort_profile(records, task_positive_label=task_positive_label)

    @classmethod
    def compute_126_intersectional_matrix(
        cls,
        records: Sequence[SubjectRecord],
        *,
        task_positive_label: str | None = None,
    ) -> dict[str, SubgroupCellStats]:
        """Compute the complete 126-cell grid through the profiling module."""
        from bias_aperture.cohort_profiling import compute_126_intersectional_matrix

        return compute_126_intersectional_matrix(
            records, task_positive_label=task_positive_label
        )
