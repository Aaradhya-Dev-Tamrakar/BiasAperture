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
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Literal

import pandas as pd

from bias_aperture.schema import (
    AGE_LABELS,
    GENDER_LABELS,
    MIN_SUBGROUP_SAMPLE_SIZE,
    RACE_LABELS,
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


@dataclass(frozen=True, slots=True)
class IngestionResult:
    """Structured output returned by the data ingestion pipeline."""

    records: list[SubjectRecord]
    validation_summary: ValidationSummary
    cohort_profile: SubgroupCohortProfile | None


class DataIngestionPipeline:
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

        # Check required columns presence in sample row
        first_row = resolved_rows[0]
        actual_image_col = self._resolve_image_col(first_row)

        required_cols = [
            self.config.race_col,
            self.config.gender_col,
            self.config.age_col,
            self.config.true_label_col,
            self.config.predicted_label_col,
        ]

        missing_cols = [col for col in required_cols if col not in first_row]
        if missing_cols:
            msg = f"Missing required column(s) in input data: {missing_cols}"
            if self.config.validation_mode == ValidationMode.STRICT:
                raise SchemaValidationError(msg)
            else:
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
                return IngestionResult(
                    records=[],
                    validation_summary=summary,
                    cohort_profile=None,
                )

        valid_records: list[SubjectRecord] = []
        issues: list[ValidationIssue] = []
        seen_images: dict[str, tuple[Any, Any, Any, Any, Any]] = {}
        issue_counter: Counter[str] = Counter()

        for idx, row in enumerate(resolved_rows):
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

            # Demographic fields extraction
            raw_race = row.get(self.config.race_col)
            raw_gender = row.get(self.config.gender_col)
            raw_age = row.get(self.config.age_col)
            raw_true = row.get(self.config.true_label_col)
            raw_pred = row.get(self.config.predicted_label_col)

            # Check for NaN / null values
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
                            f"Field {fn!r} has null/NaN value for "
                            f"image {image_id_str!r}"
                        ),
                    )
                    self._handle_issue(issue, issues, issue_counter)
                continue

            # Check label vocabularies
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
                continue

            # Duplicate image_id check & conflict resolution
            row_signature = (
                race_str,
                gender_str,
                age_str,
                str(raw_true),
                str(raw_pred),
            )
            if image_id_str in seen_images:
                prev_sig = seen_images[image_id_str]
                if prev_sig == row_signature:
                    if (
                        self.config.deduplicate_strategy
                        == "drop_exact_or_raise_conflicts"
                    ):
                        issue = ValidationIssue(
                            row_index=idx,
                            image_id=image_id_str,
                            field_name="image_id",
                            value=image_id_str,
                            issue_type="exact_duplicate",
                            message=(
                                f"Duplicate record for image_id {image_id_str!r} "
                                "dropped"
                            ),
                            severity=ValidationSeverity.WARNING,
                        )
                        issues.append(issue)
                        issue_counter["exact_duplicate"] += 1
                        continue
                    elif self.config.deduplicate_strategy == "drop_duplicates":
                        continue
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
                    continue

            seen_images[image_id_str] = row_signature

            # Record is valid
            record = SubjectRecord(
                image_id=image_id_str,
                race=race_str,  # type: ignore[arg-type]
                gender=gender_str,  # type: ignore[arg-type]
                age=age_str,  # type: ignore[arg-type]
                true_label=str(raw_true),
                predicted_label=str(raw_pred),
            )
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

    @classmethod
    def compute_cohort_profile(
        cls,
        records: Sequence[SubjectRecord],
        *,
        task_positive_label: str | None = None,
    ) -> SubgroupCohortProfile:
        """
        Compute demographic support counts and NFR-003 eligibility across
        unitary demographic axes and composite intersectional slices.
        """
        total = len(records)
        race_groups: dict[str, list[SubjectRecord]] = {r: [] for r in RACE_LABELS}
        gender_groups: dict[str, list[SubjectRecord]] = {g: [] for g in GENDER_LABELS}
        age_groups: dict[str, list[SubjectRecord]] = {a: [] for a in AGE_LABELS}
        intersectional_groups: dict[str, list[SubjectRecord]] = {}

        for rec in records:
            if rec.race in race_groups:
                race_groups[rec.race].append(rec)
            if rec.gender in gender_groups:
                gender_groups[rec.gender].append(rec)
            if rec.age in age_groups:
                age_groups[rec.age].append(rec)

            inter_key = f"race={rec.race}&gender={rec.gender}"
            intersectional_groups.setdefault(inter_key, []).append(rec)

        def _build_stats(
            subgroup_key: str, sub_records: list[SubjectRecord]
        ) -> SubgroupCellStats:
            n_sub = len(sub_records)
            pos_n: int | None = None
            neg_n: int | None = None

            if task_positive_label is not None:
                pos_n = sum(
                    1
                    for r in sub_records
                    if str(r.true_label) == str(task_positive_label)
                )
                neg_n = n_sub - pos_n
                has_pos = pos_n >= 5
                has_neg = neg_n >= 5
            else:
                has_pos = True
                has_neg = True

            is_eligible = n_sub >= MIN_SUBGROUP_SAMPLE_SIZE
            is_insufficient = n_sub < MIN_SUBGROUP_SAMPLE_SIZE

            return SubgroupCellStats(
                subgroup_key=subgroup_key,
                total_n=n_sub,
                positive_n=pos_n,
                negative_n=neg_n,
                is_nfr003_eligible=is_eligible,
                has_positive_support=has_pos,
                has_negative_support=has_neg,
                insufficient_sample_at_ingestion=is_insufficient,
            )

        race_counts = {
            f"race={r}": _build_stats(f"race={r}", race_groups[r]) for r in RACE_LABELS
        }
        gender_counts = {
            f"gender={g}": _build_stats(f"gender={g}", gender_groups[g])
            for g in GENDER_LABELS
        }
        age_counts = {
            f"age={a}": _build_stats(f"age={a}", age_groups[a]) for a in AGE_LABELS
        }
        inter_counts = {k: _build_stats(k, v) for k, v in intersectional_groups.items()}

        insufficient_keys: list[str] = [
            k
            for d in (race_counts, gender_counts, age_counts, inter_counts)
            for k, v in d.items()
            if v.insufficient_sample_at_ingestion
        ]

        return SubgroupCohortProfile(
            total_subjects=total,
            race_counts=race_counts,
            gender_counts=gender_counts,
            age_counts=age_counts,
            intersectional_counts=inter_counts,
            insufficient_subgroups=insufficient_keys,
        )


class OvRTransformer:
    r"""
    Multi-Class One-vs-Rest (OvR) evaluation helper.

    Transforms a multi-class SubjectRecord dataset into an M-way set of
    binary tasks $Y^{(m)} = \mathbb{I}(Y = c_m)$ and
    $\hat{Y}^{(m)} = \mathbb{I}(\hat{Y} = c_m)$ preserving demographic axes.
    """

    @staticmethod
    def get_classes(
        records: Sequence[SubjectRecord],
        axis: Literal["true", "predicted", "both"] = "both",
    ) -> list[str]:
        """Extract unique classes present across true, predicted, or both labels."""
        classes: set[str] = set()
        for r in records:
            if axis in ("true", "both"):
                classes.add(str(r.true_label))
            if axis in ("predicted", "both"):
                classes.add(str(r.predicted_label))
        return sorted(classes)

    @staticmethod
    def binarize(
        records: Sequence[SubjectRecord],
        target_class: str,
        *,
        positive_label: str = "1",
        negative_label: str = "0",
    ) -> list[SubjectRecord]:
        """
        Binarize ground truth and predictions against the specified target class.
        """
        target_str = str(target_class)
        binarized: list[SubjectRecord] = []
        for r in records:
            y_bin = (
                positive_label if str(r.true_label) == target_str else negative_label
            )
            y_hat_bin = (
                positive_label
                if str(r.predicted_label) == target_str
                else negative_label
            )
            binarized.append(
                SubjectRecord(
                    image_id=r.image_id,
                    race=r.race,
                    gender=r.gender,
                    age=r.age,
                    true_label=y_bin,
                    predicted_label=y_hat_bin,
                )
            )
        return binarized

    @classmethod
    def decompose_all(
        cls,
        records: Sequence[SubjectRecord],
        classes: Sequence[str] | None = None,
        *,
        positive_label: str = "1",
        negative_label: str = "0",
    ) -> dict[str, list[SubjectRecord]]:
        """
        Decompose a multi-class dataset into M distinct binary OvR datasets.
        """
        target_classes = (
            list(classes) if classes is not None else cls.get_classes(records)
        )
        return {
            c: cls.binarize(
                records,
                c,
                positive_label=positive_label,
                negative_label=negative_label,
            )
            for c in target_classes
        }
