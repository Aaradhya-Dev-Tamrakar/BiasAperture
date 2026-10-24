"""Row and schema validation behavior for prediction ingestion."""

from __future__ import annotations

import logging
from collections import Counter
from typing import Any

import pandas as pd

from bias_aperture.ingestion_contracts import (
    IMAGE_COL_ALIASES,
    RAW_AGE_LABEL_ALIASES,
    IngestionConfig,
    IngestionResult,
    SchemaValidationError,
    ValidationIssue,
    ValidationMode,
    ValidationSeverity,
    ValidationSummary,
)
from bias_aperture.schema import (
    AGE_LABELS,
    GENDER_LABELS,
    RACE_LABELS,
    SubjectRecord,
)

logger = logging.getLogger(__name__)


class IngestionValidator:
    """Reusable schema, row, duplicate, and anomaly validation methods."""

    config: IngestionConfig
    dataset_adapter: Any = None

    def _validate_columns(
        self,
        first_row: dict[str, Any],
        total_count: int,
    ) -> IngestionResult | None:
        """Validate that all required columns are present in the input data.

        Returns None if columns are valid, or a terminal IngestionResult
        with the missing-column errors if not.
        """
        required_cols = [
            self.config.race_col,
            self.config.gender_col,
            self.config.age_col,
            self.config.true_label_col,
            self.config.predicted_label_col,
        ]

        missing_cols = [col for col in required_cols if col not in first_row]
        if not missing_cols:
            return None

        msg = f"Missing required column(s) in input data: {missing_cols}"
        if self.config.validation_mode == ValidationMode.STRICT:
            raise SchemaValidationError(msg)

        logger.warning(msg)
        summary = ValidationSummary(
            total_records_processed=total_count,
            valid_records_passed=0,
            rejected_records_count=total_count,
            issues=[
                ValidationIssue(
                    row_index=None,
                    image_id=None,
                    field_name=col,
                    value=None,
                    issue_type="missing_column",
                    message=f"Column {col!r} is missing from dataset",
                )
                for col in missing_cols
            ],
            issue_counts_by_type={"missing_column": len(missing_cols)},
        )
        ds_name = (
            self.dataset_adapter.name
            if getattr(self, "dataset_adapter", None)
            else "fairface"
        )
        limitations = (
            self.dataset_adapter.label_limitations
            if getattr(self, "dataset_adapter", None)
            else ()
        )
        return IngestionResult(
            records=[],
            validation_summary=summary,
            cohort_profile=None,
            dataset_name=ds_name,
            label_limitations=limitations,
        )

    def _validate_and_convert_row(
        self,
        idx: int,
        row: dict[str, Any],
        image_id_str: str,
        issues: list[ValidationIssue],
        issue_counter: Counter[str],
    ) -> SubjectRecord | None:
        """Validate a single row's fields and convert to SubjectRecord.

        Returns None if the row fails validation (null fields or
        unrecognised taxonomy labels), recording all issues found.
        """
        # Extract raw fields
        raw_race = row.get(self.config.race_col)
        raw_gender = row.get(self.config.gender_col)
        raw_age = row.get(self.config.age_col)
        raw_true = row.get(self.config.true_label_col)
        raw_pred = row.get(self.config.predicted_label_col)

        # Null / NaN check
        null_fields: list[tuple[str, Any]] = []
        for fname, fval in [
            (self.config.race_col, raw_race),
            (self.config.gender_col, raw_gender),
            (self.config.age_col, raw_age),
            (self.config.true_label_col, raw_true),
            (self.config.predicted_label_col, raw_pred),
        ]:
            if pd.isna(fval) or fval is None:
                null_fields.append((fname, fval))

        if null_fields:
            for fn, fv in null_fields:
                issue = ValidationIssue(
                    row_index=idx,
                    image_id=image_id_str,
                    field_name=fn,
                    value=fv,
                    issue_type="null_value",
                    message=(
                        f"Field {fn!r} has null/NaN value for image {image_id_str!r}"
                    ),
                )
                self._handle_issue(issue, issues, issue_counter)
            return None

        # Taxonomy normalisation and validation
        race_str = str(raw_race).strip()
        gender_str = str(raw_gender).strip()
        raw_age_str = str(raw_age).strip()
        age_str = RAW_AGE_LABEL_ALIASES.get(raw_age_str, raw_age_str)

        taxonomy_invalid = False
        if race_str not in RACE_LABELS:
            issue = ValidationIssue(
                row_index=idx,
                image_id=image_id_str,
                field_name=self.config.race_col,
                value=raw_race,
                issue_type="invalid_race_label",
                message=(
                    f"unrecognised race label {raw_race!r} for {image_id_str} — "
                    f"expected one of {RACE_LABELS} (schema locked at M1)"
                ),
            )
            self._handle_issue(issue, issues, issue_counter)
            taxonomy_invalid = True

        if gender_str not in GENDER_LABELS:
            issue = ValidationIssue(
                row_index=idx,
                image_id=image_id_str,
                field_name=self.config.gender_col,
                value=raw_gender,
                issue_type="invalid_gender_label",
                message=(
                    f"unrecognised gender label {raw_gender!r} for "
                    f"{image_id_str} — expected one of {GENDER_LABELS} "
                    "(schema locked at M1)"
                ),
            )
            self._handle_issue(issue, issues, issue_counter)
            taxonomy_invalid = True

        if age_str not in AGE_LABELS:
            issue = ValidationIssue(
                row_index=idx,
                image_id=image_id_str,
                field_name=self.config.age_col,
                value=raw_age,
                issue_type="invalid_age_label",
                message=(
                    f"unrecognised age label {raw_age!r} for {image_id_str} — "
                    f"expected one of {AGE_LABELS} (schema locked at M1)"
                ),
            )
            self._handle_issue(issue, issues, issue_counter)
            taxonomy_invalid = True

        if taxonomy_invalid:
            return None

        return SubjectRecord(
            image_id=image_id_str,
            race=race_str,  # type: ignore[arg-type]
            gender=gender_str,  # type: ignore[arg-type]
            age=age_str,  # type: ignore[arg-type]
            true_label=str(raw_true),
            predicted_label=str(raw_pred),
        )

    def _check_duplicate(
        self,
        idx: int,
        image_id_str: str,
        row_signature: tuple[Any, ...],
        seen_images: dict[str, tuple[Any, ...]],
        issues: list[ValidationIssue],
        issue_counter: Counter[str],
    ) -> bool:
        """Check whether a row is a duplicate and handle dedup strategy.

        Returns True if the row should be skipped (exact or conflicting
        duplicate), False if it should be kept.
        """
        if image_id_str not in seen_images:
            return False

        prev_sig = seen_images[image_id_str]
        if prev_sig == row_signature:
            if self.config.deduplicate_strategy == "drop_exact_or_raise_conflicts":
                issue = ValidationIssue(
                    row_index=idx,
                    image_id=image_id_str,
                    field_name="image_id",
                    value=image_id_str,
                    issue_type="exact_duplicate",
                    message=(f"Duplicate record for image_id {image_id_str!r} dropped"),
                    severity=ValidationSeverity.WARNING,
                )
                issues.append(issue)
                issue_counter["exact_duplicate"] += 1
                return True
            elif self.config.deduplicate_strategy == "drop_duplicates":
                return True
        else:
            # Conflicting duplicate
            issue = ValidationIssue(
                row_index=idx,
                image_id=image_id_str,
                field_name="image_id",
                value=image_id_str,
                issue_type="conflicting_duplicate",
                message=(
                    f"Conflicting duplicate records found for "
                    f"image_id {image_id_str!r}: "
                    f"original={prev_sig}, duplicate={row_signature}"
                ),
            )
            self._handle_issue(issue, issues, issue_counter)
            return True

        return False

    def _resolve_image_col(self, sample_row: dict[str, Any]) -> str:
        """Resolve image identifier column with alias fallback."""
        if self.config.image_id_col in sample_row:
            return self.config.image_id_col
        for alias in IMAGE_COL_ALIASES:
            if alias in sample_row:
                return alias
        if self.config.validation_mode == ValidationMode.STRICT:
            raise SchemaValidationError(
                f"Could not locate image id column {self.config.image_id_col!r} "
                f"or any standard alias in row keys: {list(sample_row.keys())}"
            )
        return self.config.image_id_col

    def _handle_issue(
        self,
        issue: ValidationIssue,
        issue_list: list[ValidationIssue],
        counter: Counter[str],
    ) -> None:
        """Record issue or immediately raise if in STRICT validation mode."""
        if (
            self.config.validation_mode == ValidationMode.STRICT
            and issue.severity == ValidationSeverity.ERROR
        ):
            raise SchemaValidationError(issue.message)
        issue_list.append(issue)
        counter[issue.issue_type] += 1
