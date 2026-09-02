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


def test_raw_fairface_age_alias_normalizes_to_locked_label():
    config = IngestionConfig(
        true_label_col="true_label",
        predicted_label_col="pred_label",
        validation_mode=ValidationMode.STRICT,
    )
    pipeline = DataIngestionPipeline(config)

    result = pipeline.ingest_records(
        [
            {
                "face_name_align": "img1.jpg",
                "race": "White",
                "gender": "Female",
                "age": "more than 70",
                "true_label": "0",
                "pred_label": "0",
            }
        ]
    )

    assert result.validation_summary.is_valid is True
    assert result.records[0].age == "70+"
    assert result.cohort_profile is not None
    assert result.cohort_profile.age_counts["age=70+"].total_n == 1


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
