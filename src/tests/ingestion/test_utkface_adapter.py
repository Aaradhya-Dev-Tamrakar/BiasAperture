"""Unit and integration tests for dataset adapters and UTKFace (WP2 / Issue #20)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from bias_aperture.cli import build_parser
from bias_aperture.data_ingestion import DataIngestionPipeline, IngestionConfig
from bias_aperture.dataset_adapters import (
    DatasetRegistry,
    FairFaceAdapter,
    UTKFaceAdapter,
    map_age_to_bracket,
)
from bias_aperture.schema import AGE_LABELS, GENDER_LABELS, RACE_LABELS


def test_fairface_adapter_defaults() -> None:
    """Verify FairFaceAdapter properties and normalization."""
    adapter = FairFaceAdapter()
    assert adapter.name == "fairface"
    assert "race" in adapter.supported_attributes
    assert len(adapter.label_limitations) >= 1

    row = {
        "face_name_align": "img1.jpg",
        "race": "White",
        "gender": "Female",
        "age": "70+",
    }
    norm = adapter.normalize_record(row)
    assert norm["age"] == "more than 70"


def test_utkface_adapter_properties() -> None:
    """Verify UTKFaceAdapter metadata, properties, and quality caveats."""
    adapter = UTKFaceAdapter()
    assert adapter.name == "utkface"
    assert set(adapter.supported_attributes) == {"race", "gender", "age"}
    # Explicit quality caveats must be documented
    limitations = " ".join(adapter.label_limitations)
    assert "DEX" in limitations
    assert "taxonomy collapse" in limitations.lower()


def test_utkface_filename_parsing() -> None:
    """Verify parsing of standard UTKFace filename convention."""
    adapter = UTKFaceAdapter()

    # 26-year-old male (0), White (0)
    parsed_1 = adapter.parse_filename("26_0_0_20170116180356182.jpg")
    assert parsed_1 is not None
    assert parsed_1["age"] == "20-29"
    assert parsed_1["gender"] == "Male"
    assert parsed_1["race"] == "White"

    # 45-year-old female (1), Black (1)
    parsed_2 = adapter.parse_filename("part1/45_1_1_20170116180356182.jpg.chip.jpg")
    assert parsed_2 is not None
    assert parsed_2["age"] == "40-49"
    assert parsed_2["gender"] == "Female"
    assert parsed_2["race"] == "Black"

    # 8-year-old female (1), Asian (2) -> mapped to East Asian
    parsed_3 = adapter.parse_filename("8_1_2_20170116180356182.jpg")
    assert parsed_3 is not None
    assert parsed_3["age"] == "3-9"
    assert parsed_3["gender"] == "Female"
    assert parsed_3["race"] == "East Asian"

    # 72-year-old male (0), Others (4) -> mapped to Latino_Hispanic
    parsed_4 = adapter.parse_filename("72_0_4_20170116180356182.jpg")
    assert parsed_4 is not None
    assert parsed_4["age"] == "more than 70"
    assert parsed_4["gender"] == "Male"
    assert parsed_4["race"] == "Latino_Hispanic"


def test_utkface_filename_parsing_invalid() -> None:
    """Verify invalid or non-standard filenames return None."""
    adapter = UTKFaceAdapter()
    assert adapter.parse_filename("random_image_name.jpg") is None
    assert adapter.parse_filename("not_an_image.csv") is None


def test_utkface_normalization_from_numeric_columns() -> None:
    """Verify normalization of tabular UTKFace records with numeric codes."""
    adapter = UTKFaceAdapter()
    row = {
        "face_name_align": "img_01.jpg",
        "age": 35,
        "gender": 1,
        "race": 3,  # Indian
        "true_label": 1,
        "predicted_label": 1,
    }
    norm = adapter.normalize_record(row)
    assert norm["age"] == "30-39"
    assert norm["gender"] == "Female"
    assert norm["race"] == "Indian"
    assert norm["race"] in RACE_LABELS
    assert norm["gender"] in GENDER_LABELS
    assert norm["age"] in AGE_LABELS


def test_map_age_to_bracket_boundaries() -> None:
    """Verify all age bracket partition boundaries."""
    assert map_age_to_bracket(0) == "0-2"
    assert map_age_to_bracket(2) == "0-2"
    assert map_age_to_bracket(3) == "3-9"
    assert map_age_to_bracket(9) == "3-9"
    assert map_age_to_bracket(10) == "10-19"
    assert map_age_to_bracket(19) == "10-19"
    assert map_age_to_bracket(20) == "20-29"
    assert map_age_to_bracket(29) == "20-29"
    assert map_age_to_bracket(30) == "30-39"
    assert map_age_to_bracket(39) == "30-39"
    assert map_age_to_bracket(40) == "40-49"
    assert map_age_to_bracket(49) == "40-49"
    assert map_age_to_bracket(50) == "50-59"
    assert map_age_to_bracket(59) == "50-59"
    assert map_age_to_bracket(60) == "60-69"
    assert map_age_to_bracket(69) == "60-69"
    assert map_age_to_bracket(70) == "more than 70"
    assert map_age_to_bracket(95) == "more than 70"

    with pytest.raises(ValueError, match="Negative age"):
        map_age_to_bracket(-5)

    with pytest.raises(ValueError, match="Invalid age"):
        map_age_to_bracket("unparseable_age")


def test_dataset_registry() -> None:
    """Verify dynamic registry resolution and error states."""
    assert "fairface" in DatasetRegistry.list_datasets()
    assert "utkface" in DatasetRegistry.list_datasets()

    ff = DatasetRegistry.get("fairface")
    assert isinstance(ff, FairFaceAdapter)

    utk = DatasetRegistry.get("utkface")
    assert isinstance(utk, UTKFaceAdapter)

    with pytest.raises(ValueError, match="Unknown dataset 'imagenet'"):
        DatasetRegistry.get("imagenet")


def test_data_ingestion_pipeline_with_utkface_adapter(tmp_path: Path) -> None:
    """Verify full end-to-end ingestion pipeline with UTKFace adapter."""
    # Create 35 synthetic UTKFace records
    rows = []
    for i in range(35):
        rows.append(
            {
                "face_name_align": f"img_{i}.jpg",
                "race": 0 if i % 2 == 0 else 1,  # 0: White, 1: Black
                "gender": 1,  # Female
                "age": 25,  # 20-29
                "true_label": 1 if i % 3 == 0 else 0,
                "predicted_label": 1 if i % 2 == 0 else 0,
            }
        )
    df = pd.DataFrame(rows)

    pipeline = DataIngestionPipeline(
        config=IngestionConfig(
            true_label_col="true_label",
            predicted_label_col="predicted_label",
            race_col="race",
            gender_col="gender",
            age_col="age",
            dataset="utkface",
        )
    )

    res = pipeline.ingest_dataframe(df)
    assert len(res.records) == 35
    assert res.dataset_name == "utkface"
    assert len(res.label_limitations) >= 3

    # Verify all records conform to Milestone M1 locked schema vocabularies
    for rec in res.records:
        assert rec.race in ("White", "Black")
        assert rec.gender == "Female"
        assert rec.age == "20-29"


def test_cli_parser_dataset_flag() -> None:
    """Verify CLI parser parses --dataset flag correctly."""
    parser = build_parser()
    args = parser.parse_args(["-i", "dummy.csv", "--dataset", "utkface"])
    assert args.dataset == "utkface"
