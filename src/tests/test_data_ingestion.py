import json

import pandas as pd
import pytest

from bias_aperture.data_ingestion import (
    DataIngestionPipeline,
    IngestionConfig,
    OvRTransformer,
    SchemaValidationError,
    ValidationMode,
)
from bias_aperture.schema import SubjectRecord


@pytest.fixture
def valid_dataframe():
    return pd.DataFrame(
        {
            "face_name_align": [f"img_{i}.jpg" for i in range(100)],
            "race": ["White"] * 40 + ["Black"] * 35 + ["Indian"] * 25,
            "gender": ["Female"] * 50 + ["Male"] * 50,
            "age": ["20-29"] * 60 + ["30-39"] * 40,
            "true_gender": ["Female"] * 50 + ["Male"] * 50,
            "pred_gender": ["Female"] * 45 + ["Male"] * 55,
        }
    )


@pytest.fixture
def valid_csv(tmp_path, valid_dataframe):
    csv_path = tmp_path / "valid_predictions.csv"
    valid_dataframe.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def valid_json(tmp_path, valid_dataframe):
    json_path = tmp_path / "valid_predictions.json"
    valid_dataframe.to_json(json_path, orient="records")
    return json_path


def test_strict_ingestion_happy_path(valid_csv):
    config = IngestionConfig(
        true_label_col="true_gender",
        predicted_label_col="pred_gender",
        validation_mode=ValidationMode.STRICT,
    )
    pipeline = DataIngestionPipeline(config)
    result = pipeline.ingest_file(valid_csv, task_positive_label="Female")

    assert len(result.records) == 100
    assert result.validation_summary.is_valid is True
    assert result.validation_summary.valid_records_passed == 100
    assert result.validation_summary.rejected_records_count == 0

    # Verify cohort profile
    profile = result.cohort_profile
    assert profile is not None
    assert profile.total_subjects == 100
    assert profile.race_counts["race=White"].total_n == 40
    assert profile.race_counts["race=White"].is_nfr003_eligible is True
    assert profile.race_counts["race=Indian"].total_n == 25
    assert profile.race_counts["race=Indian"].is_nfr003_eligible is False
    assert profile.race_counts["race=Indian"].insufficient_sample_at_ingestion is True
    assert "race=Indian" in profile.insufficient_subgroups


def test_json_ingestion_happy_path(valid_json):
    config = IngestionConfig(
        true_label_col="true_gender",
        predicted_label_col="pred_gender",
    )
    pipeline = DataIngestionPipeline(config)
    result = pipeline.ingest_file(valid_json)

    assert len(result.records) == 100
    assert result.records[0].race == "White"


def test_missing_column_strict_mode_raises(tmp_path):
    csv_path = tmp_path / "missing_cols.csv"
    csv_path.write_text("face_name_align,race,gender\nimg1.jpg,White,Female\n")

    config = IngestionConfig(
        true_label_col="true_label",
        predicted_label_col="pred_label",
        validation_mode=ValidationMode.STRICT,
    )
    pipeline = DataIngestionPipeline(config)

    with pytest.raises(SchemaValidationError, match="Missing required column"):
        pipeline.ingest_file(csv_path)


def test_missing_column_permissive_mode_records_issues(tmp_path):
    csv_path = tmp_path / "missing_cols.csv"
    csv_path.write_text("face_name_align,race,gender\nimg1.jpg,White,Female\n")

    config = IngestionConfig(
        true_label_col="true_label",
        predicted_label_col="pred_label",
        validation_mode=ValidationMode.PERMISSIVE,
    )
    pipeline = DataIngestionPipeline(config)
    result = pipeline.ingest_file(csv_path)

    assert len(result.records) == 0
    assert result.validation_summary.is_valid is False
    assert result.validation_summary.issue_counts_by_type["missing_column"] > 0


def test_invalid_demographic_taxonomy_strict_mode(tmp_path):
    csv_path = tmp_path / "invalid_race.csv"
    csv_path.write_text(
        "face_name_align,race,gender,age,true_label,pred_label\n"
        "img1.jpg,Caucasian,Female,20-29,0,0\n"
    )

    config = IngestionConfig(
        true_label_col="true_label",
        predicted_label_col="pred_label",
        validation_mode=ValidationMode.STRICT,
    )
    pipeline = DataIngestionPipeline(config)

    with pytest.raises(SchemaValidationError, match="unrecognised race label"):
        pipeline.ingest_file(csv_path)


def test_invalid_gender_label_strict_mode(tmp_path):
    csv_path = tmp_path / "invalid_gender.csv"
    csv_path.write_text(
        "face_name_align,race,gender,age,true_label,pred_label\n"
        "img1.jpg,White,NonBinary,20-29,0,0\n"
    )

    config = IngestionConfig(
        true_label_col="true_label",
        predicted_label_col="pred_label",
        validation_mode=ValidationMode.STRICT,
    )
    pipeline = DataIngestionPipeline(config)

    with pytest.raises(SchemaValidationError, match="unrecognised gender label"):
        pipeline.ingest_file(csv_path)


def test_invalid_age_label_strict_mode(tmp_path):
    csv_path = tmp_path / "invalid_age.csv"
    csv_path.write_text(
        "face_name_align,race,gender,age,true_label,pred_label\n"
        "img1.jpg,White,Female,25,0,0\n"
    )

    config = IngestionConfig(
        true_label_col="true_label",
        predicted_label_col="pred_label",
        validation_mode=ValidationMode.STRICT,
    )
    pipeline = DataIngestionPipeline(config)

    with pytest.raises(SchemaValidationError, match="unrecognised age label"):
        pipeline.ingest_file(csv_path)


def test_invalid_demographic_taxonomy_permissive_mode(tmp_path):
    csv_path = tmp_path / "invalid_labels.csv"
    csv_path.write_text(
        "face_name_align,race,gender,age,true_label,pred_label\n"
        "img1.jpg,Caucasian,Female,20-29,0,0\n"
        "img2.jpg,White,Unknown,20-29,0,0\n"
        "img3.jpg,Black,Male,100+,0,0\n"
        "img4.jpg,Black,Female,20-29,0,0\n"
    )

    config = IngestionConfig(
        true_label_col="true_label",
        predicted_label_col="pred_label",
        validation_mode=ValidationMode.PERMISSIVE,
    )
    pipeline = DataIngestionPipeline(config)
    result = pipeline.ingest_file(csv_path)

    assert len(result.records) == 1
    assert result.records[0].image_id == "img4.jpg"
    assert result.validation_summary.rejected_records_count == 3
    assert result.validation_summary.issue_counts_by_type["invalid_race_label"] == 1
    assert result.validation_summary.issue_counts_by_type["invalid_gender_label"] == 1
    assert result.validation_summary.issue_counts_by_type["invalid_age_label"] == 1


def test_null_and_nan_handling(tmp_path):
    csv_path = tmp_path / "nulls.csv"
    csv_path.write_text(
        "face_name_align,race,gender,age,true_label,pred_label\n"
        "img1.jpg,,Female,20-29,0,0\n"
        "img2.jpg,White,,20-29,0,0\n"
        ",White,Male,20-29,0,0\n"
        "img4.jpg,White,Male,20-29,0,0\n"
    )

    config = IngestionConfig(
        true_label_col="true_label",
        predicted_label_col="pred_label",
        validation_mode=ValidationMode.PERMISSIVE,
    )
    pipeline = DataIngestionPipeline(config)
    result = pipeline.ingest_file(csv_path)

    assert len(result.records) == 1
    assert result.records[0].image_id == "img4.jpg"
    assert result.validation_summary.issue_counts_by_type["null_value"] >= 2
    assert result.validation_summary.issue_counts_by_type["invalid_image_id"] == 1


def test_exact_and_conflicting_duplicates(tmp_path):
    csv_path = tmp_path / "duplicates.csv"
    csv_path.write_text(
        "face_name_align,race,gender,age,true_label,pred_label\n"
        "img1.jpg,White,Female,20-29,0,0\n"
        "img1.jpg,White,Female,20-29,0,0\n"  # Exact duplicate
        "img2.jpg,Black,Male,30-39,0,0\n"
        "img2.jpg,Black,Male,30-39,1,1\n"  # Conflicting duplicate
    )

    # In strict mode, conflicting duplicate should raise
    config_strict = IngestionConfig(
        true_label_col="true_label",
        predicted_label_col="pred_label",
        validation_mode=ValidationMode.STRICT,
    )
    pipeline_strict = DataIngestionPipeline(config_strict)
    with pytest.raises(SchemaValidationError, match="Conflicting duplicate"):
        pipeline_strict.ingest_file(csv_path)

    # In permissive mode, exact duplicate is warning-dropped, conflicting is rejected
    config_perm = IngestionConfig(
        true_label_col="true_label",
        predicted_label_col="pred_label",
        validation_mode=ValidationMode.PERMISSIVE,
    )
    pipeline_perm = DataIngestionPipeline(config_perm)
    result = pipeline_perm.ingest_file(csv_path)

    assert len(result.records) == 2  # img1 and first img2
    assert result.validation_summary.issue_counts_by_type["exact_duplicate"] == 1
    assert result.validation_summary.issue_counts_by_type["conflicting_duplicate"] == 1


def test_deduplicate_strategy_drop_duplicates(tmp_path):
    csv_path = tmp_path / "drop_dups.csv"
    csv_path.write_text(
        "face_name_align,race,gender,age,true_label,pred_label\n"
        "img1.jpg,White,Female,20-29,0,0\n"
        "img1.jpg,White,Female,20-29,0,0\n"
    )

    config = IngestionConfig(
        true_label_col="true_label",
        predicted_label_col="pred_label",
        deduplicate_strategy="drop_duplicates",
    )
    pipeline = DataIngestionPipeline(config)
    result = pipeline.ingest_file(csv_path)

    assert len(result.records) == 1


def test_deduplicate_strategy_drop_duplicates_still_rejects_conflicts(tmp_path):
    """
    Gap fix: 'drop_duplicates' silently drops EXACT repeats of an image_id,
    but a CONFLICTING duplicate (same image_id, different demographic/label
    signature) always falls through to the 'else' branch in the ingestion
    loop regardless of deduplicate_strategy, so it must still be rejected
    (and raised in STRICT mode) rather than silently kept or dropped.
    """
    csv_path = tmp_path / "drop_dups_conflict.csv"
    csv_path.write_text(
        "face_name_align,race,gender,age,true_label,pred_label\n"
        "img1.jpg,White,Female,20-29,0,0\n"
        "img1.jpg,White,Female,20-29,1,1\n"  # conflicting signature, same id
        "img2.jpg,Black,Male,30-39,0,0\n"
    )

    # STRICT: conflicting duplicate must still raise even under drop_duplicates
    config_strict = IngestionConfig(
        true_label_col="true_label",
        predicted_label_col="pred_label",
        validation_mode=ValidationMode.STRICT,
        deduplicate_strategy="drop_duplicates",
    )
    pipeline_strict = DataIngestionPipeline(config_strict)
    with pytest.raises(SchemaValidationError, match="Conflicting duplicate"):
        pipeline_strict.ingest_file(csv_path)

    # PERMISSIVE: conflicting duplicate rejected & counted, not silently dropped
    config_perm = IngestionConfig(
        true_label_col="true_label",
        predicted_label_col="pred_label",
        validation_mode=ValidationMode.PERMISSIVE,
        deduplicate_strategy="drop_duplicates",
    )
    pipeline_perm = DataIngestionPipeline(config_perm)
    result = pipeline_perm.ingest_file(csv_path)

    assert len(result.records) == 2  # first img1 row + img2
    assert result.records[0].image_id == "img1.jpg"
    assert result.records[0].true_label == "0"
    assert result.validation_summary.issue_counts_by_type["conflicting_duplicate"] == 1
    assert "exact_duplicate" not in result.validation_summary.issue_counts_by_type


def test_deduplicate_strategy_keep_all(tmp_path):
    """
    Gap fix: under 'keep_all', an EXACT duplicate matches neither the
    'drop_exact_or_raise_conflicts' nor 'drop_duplicates' branch, so the
    loop falls through and appends the record again. This locks in that
    (surprising but current) behavior: keep_all really does keep both rows,
    including the repeated image_id, rather than raising or deduplicating.
    """
    csv_path = tmp_path / "keep_all.csv"
    csv_path.write_text(
        "face_name_align,race,gender,age,true_label,pred_label\n"
        "img1.jpg,White,Female,20-29,0,0\n"
        "img1.jpg,White,Female,20-29,0,0\n"  # exact duplicate
        "img2.jpg,Black,Male,30-39,0,0\n"
    )

    config = IngestionConfig(
        true_label_col="true_label",
        predicted_label_col="pred_label",
        deduplicate_strategy="keep_all",
    )
    pipeline = DataIngestionPipeline(config)
    result = pipeline.ingest_file(csv_path)

    assert len(result.records) == 3
    ids = [r.image_id for r in result.records]
    assert ids.count("img1.jpg") == 2
    assert result.validation_summary.rejected_records_count == 0
    assert "exact_duplicate" not in result.validation_summary.issue_counts_by_type
    assert (
        "conflicting_duplicate" not in result.validation_summary.issue_counts_by_type
    )


def test_deduplicate_strategy_keep_all_still_rejects_conflicts(tmp_path):
    """A genuinely conflicting duplicate is rejected under keep_all too,
    since the conflict check happens before the strategy is consulted."""
    csv_path = tmp_path / "keep_all_conflict.csv"
    csv_path.write_text(
        "face_name_align,race,gender,age,true_label,pred_label\n"
        "img1.jpg,White,Female,20-29,0,0\n"
        "img1.jpg,White,Female,20-29,1,1\n"  # conflicting signature
    )

    config = IngestionConfig(
        true_label_col="true_label",
        predicted_label_col="pred_label",
        validation_mode=ValidationMode.PERMISSIVE,
        deduplicate_strategy="keep_all",
    )
    pipeline = DataIngestionPipeline(config)
    result = pipeline.ingest_file(csv_path)

    assert len(result.records) == 1
    assert result.validation_summary.issue_counts_by_type["conflicting_duplicate"] == 1


def test_image_column_alias_resolution(tmp_path):
    csv_path = tmp_path / "file_alias.csv"
    csv_path.write_text(
        "file,race,gender,age,true_label,pred_label\nface1.jpg,White,Female,20-29,0,0\n"
    )

    config = IngestionConfig(
        true_label_col="true_label",
        predicted_label_col="pred_label",
    )
    pipeline = DataIngestionPipeline(config)
    result = pipeline.ingest_file(csv_path)

    assert len(result.records) == 1
    assert result.records[0].image_id == "face1.jpg"


@pytest.mark.parametrize("alias_col", ["image_id", "img_path", "filename"])
def test_image_column_alias_resolution_other_aliases(tmp_path, alias_col):
    """Gap fix: only the 'file' alias was previously tested, but
    IMAGE_COL_ALIASES also includes image_id, img_path, and filename."""
    csv_path = tmp_path / f"{alias_col}_alias.csv"
    csv_path.write_text(
        f"{alias_col},race,gender,age,true_label,pred_label\n"
        "face1.jpg,White,Female,20-29,0,0\n"
    )

    config = IngestionConfig(
        true_label_col="true_label",
        predicted_label_col="pred_label",
    )
    pipeline = DataIngestionPipeline(config)
    result = pipeline.ingest_file(csv_path)

    assert len(result.records) == 1
    assert result.records[0].image_id == "face1.jpg"


def test_resolve_image_col_strict_mode_raises_when_no_alias_present(tmp_path):
    """Gap fix: STRICT mode should raise SchemaValidationError when none
    of the standard image-id aliases exist in the input columns at all."""
    csv_path = tmp_path / "no_image_col.csv"
    csv_path.write_text(
        "race,gender,age,true_label,pred_label\nWhite,Female,20-29,0,0\n"
    )

    config = IngestionConfig(
        true_label_col="true_label",
        predicted_label_col="pred_label",
        validation_mode=ValidationMode.STRICT,
    )
    pipeline = DataIngestionPipeline(config)

    with pytest.raises(SchemaValidationError, match="Could not locate image id column"):
        pipeline.ingest_file(csv_path)


def test_resolve_image_col_permissive_mode_falls_back_to_configured_name(tmp_path):
    """In PERMISSIVE mode, an absent image column should not raise; it
    falls back to the configured image_id_col name and rows are then
    rejected downstream as 'missing_column' / 'invalid_image_id' issues."""
    csv_path = tmp_path / "no_image_col.csv"
    csv_path.write_text(
        "race,gender,age,true_label,pred_label\nWhite,Female,20-29,0,0\n"
    )

    config = IngestionConfig(
        true_label_col="true_label",
        predicted_label_col="pred_label",
        validation_mode=ValidationMode.PERMISSIVE,
    )
    pipeline = DataIngestionPipeline(config)
    result = pipeline.ingest_file(csv_path)

    # Should not raise; should complete with zero valid records.
    assert len(result.records) == 0


def test_json_dict_with_records_key(tmp_path):
    """Gap fix: ingest_file must unwrap a top-level JSON object of the
    form {"records": [...]}."""
    json_path = tmp_path / "records_wrapped.json"
    payload = {
        "records": [
            {
                "face_name_align": "img1.jpg",
                "race": "White",
                "gender": "Female",
                "age": "20-29",
                "true_label": "0",
                "pred_label": "0",
            }
        ]
    }
    json_path.write_text(json.dumps(payload))

    config = IngestionConfig(
        true_label_col="true_label",
        predicted_label_col="pred_label",
    )
    pipeline = DataIngestionPipeline(config)
    result = pipeline.ingest_file(json_path)

    assert len(result.records) == 1
    assert result.records[0].image_id == "img1.jpg"


def test_json_dict_with_data_key(tmp_path):
    """Gap fix: ingest_file must unwrap a top-level JSON object of the
    form {"data": [...]}."""
    json_path = tmp_path / "data_wrapped.json"
    payload = {
        "data": [
            {
                "face_name_align": "img1.jpg",
                "race": "Black",
                "gender": "Male",
                "age": "30-39",
                "true_label": "1",
                "pred_label": "1",
            }
        ]
    }
    json_path.write_text(json.dumps(payload))

    config = IngestionConfig(
        true_label_col="true_label",
        predicted_label_col="pred_label",
    )
    pipeline = DataIngestionPipeline(config)
    result = pipeline.ingest_file(json_path)

    assert len(result.records) == 1
    assert result.records[0].image_id == "img1.jpg"


def test_json_dict_single_record_without_wrapper_key(tmp_path):
    """Gap fix: a bare JSON object with neither 'records' nor 'data' keys
    should be treated as a single-record dataset, per
    data.get("records", data.get("data", [data]))."""
    json_path = tmp_path / "single_record.json"
    payload = {
        "face_name_align": "img1.jpg",
        "race": "Indian",
        "gender": "Female",
        "age": "40-49",
        "true_label": "0",
        "pred_label": "1",
    }
    json_path.write_text(json.dumps(payload))

    config = IngestionConfig(
        true_label_col="true_label",
        predicted_label_col="pred_label",
    )
    pipeline = DataIngestionPipeline(config)
    result = pipeline.ingest_file(json_path)

    assert len(result.records) == 1
    assert result.records[0].image_id == "img1.jpg"


def test_file_not_found():
    config = IngestionConfig(
        true_label_col="true_label",
        predicted_label_col="pred_label",
    )
    pipeline = DataIngestionPipeline(config)
    with pytest.raises(FileNotFoundError):
        pipeline.ingest_file("nonexistent_file.csv")


def test_unsupported_extension(tmp_path):
    txt_path = tmp_path / "preds.txt"
    txt_path.write_text("text")

    config = IngestionConfig(
        true_label_col="true_label",
        predicted_label_col="pred_label",
    )
    pipeline = DataIngestionPipeline(config)
    with pytest.raises(ValueError, match="unsupported predictions-file extension"):
        pipeline.ingest_file(txt_path)


def test_empty_dataset_handling():
    config = IngestionConfig(
        true_label_col="true_label",
        predicted_label_col="pred_label",
    )
    pipeline = DataIngestionPipeline(config)
    result = pipeline.ingest_records([])

    assert len(result.records) == 0
    assert result.validation_summary.valid_records_passed == 0
    assert result.cohort_profile.total_subjects == 0


def test_cohort_profile_contingency_support():
    records = [
        SubjectRecord(f"img_{i}", "White", "Female", "20-29", "1", "1")
        for i in range(35)
    ] + [
        SubjectRecord(f"img_{i + 35}", "White", "Female", "20-29", "0", "0")
        for i in range(5)
    ]

    profile = DataIngestionPipeline.compute_cohort_profile(
        records, task_positive_label="1"
    )
    white_stats = profile.race_counts["race=White"]
    assert white_stats.total_n == 40
    assert white_stats.positive_n == 35
    assert white_stats.negative_n == 5
    assert white_stats.is_nfr003_eligible is True
    assert white_stats.has_positive_support is True
    assert white_stats.has_negative_support is True
    assert white_stats.insufficient_sample_at_ingestion is False

    inter_stats = profile.intersectional_counts["race=White&gender=Female"]
    assert inter_stats.total_n == 40
    assert inter_stats.is_nfr003_eligible is True


def test_cohort_profile_insufficient_positive_or_negative_support(tmp_path):
    """
    Gap fix: has_positive_support / has_negative_support are only True when
    the respective count is >= 5. Previously only the "both sufficient"
    case was tested; this locks in the failure branches for each side.
    """
    # 32 total: 3 positive (< 5) / 29 negative (>= 5) -> only negative support
    records_low_pos = [
        SubjectRecord(f"img_{i}", "Black", "Male", "20-29", "1", "1") for i in range(3)
    ] + [
        SubjectRecord(f"img_{i + 3}", "Black", "Male", "20-29", "0", "0")
        for i in range(29)
    ]
    profile_low_pos = DataIngestionPipeline.compute_cohort_profile(
        records_low_pos, task_positive_label="1"
    )
    black_stats = profile_low_pos.race_counts["race=Black"]
    assert black_stats.total_n == 32
    assert black_stats.positive_n == 3
    assert black_stats.negative_n == 29
    assert black_stats.has_positive_support is False
    assert black_stats.has_negative_support is True
    assert black_stats.is_nfr003_eligible is True  # total_n >= 30

    # 32 total: 29 positive (>= 5) / 3 negative (< 5) -> only positive support
    records_low_neg = [
        SubjectRecord(f"img_{i}", "Indian", "Male", "20-29", "1", "1")
        for i in range(29)
    ] + [
        SubjectRecord(f"img_{i + 29}", "Indian", "Male", "20-29", "0", "0")
        for i in range(3)
    ]
    profile_low_neg = DataIngestionPipeline.compute_cohort_profile(
        records_low_neg, task_positive_label="1"
    )
    indian_stats = profile_low_neg.race_counts["race=Indian"]
    assert indian_stats.positive_n == 29
    assert indian_stats.negative_n == 3
    assert indian_stats.has_positive_support is True
    assert indian_stats.has_negative_support is False


def test_ovr_transformer():
    records = [
        SubjectRecord("1", "White", "Female", "20-29", "White", "White"),
        SubjectRecord("2", "Black", "Male", "30-39", "Black", "White"),
        SubjectRecord("3", "Indian", "Female", "40-49", "Indian", "Indian"),
        SubjectRecord(
            "4", "East Asian", "Male", "50-59", "East Asian", "Southeast Asian"
        ),
    ]

    classes = OvRTransformer.get_classes(records)
    assert set(classes) == {"Black", "East Asian", "Indian", "Southeast Asian", "White"}

    # Binarize for "White"
    white_ovr = OvRTransformer.binarize(records, "White")
    assert len(white_ovr) == 4
    assert white_ovr[0].true_label == "1" and white_ovr[0].predicted_label == "1"
    assert white_ovr[1].true_label == "0" and white_ovr[1].predicted_label == "1"
    assert white_ovr[2].true_label == "0" and white_ovr[2].predicted_label == "0"
    assert white_ovr[3].true_label == "0" and white_ovr[3].predicted_label == "0"

    # Decompose all
    ovr_dict = OvRTransformer.decompose_all(records)
    assert len(ovr_dict) == 5
    assert "Black" in ovr_dict
    assert ovr_dict["Black"][1].true_label == "1"