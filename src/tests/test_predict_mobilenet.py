<<<<<<< Updated upstream
"""Regression and unit tests for MobileNetV2 FairFaceDataset and prediction pipeline.

Covers Model 4 integration tests and schema adherence.
"""
=======
"""Regression and unit tests for MobileNetV2 FairFaceDataset and prediction pipeline."""
>>>>>>> Stashed changes

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bias_aperture.cli import main  # noqa: E402
from bias_aperture.data_ingestion import (  # noqa: E402
    DataIngestionPipeline,
    IngestionConfig,
    ValidationMode,
)
from scripts.predict_mobilenet import FairFaceDataset  # noqa: E402


class MockProcessor:
    """Mock processor simulating AutoImageProcessor for testing."""

    def __call__(self, images, return_tensors="pt"):
        import torch

        return {"pixel_values": torch.zeros((1, 3, 224, 224))}


def test_mobilenet_fairface_dataset_valid_read(tmp_path: Path) -> None:
    """Verify that a valid image is loaded correctly with associated metadata."""
    img_dir = tmp_path / "images"
    img_dir.mkdir()

    img_filename = "0001.jpg"
    test_img = Image.new("RGB", (100, 100), color=(128, 64, 32))
    test_img.save(img_dir / img_filename)

    df = pd.DataFrame(
        [
            {
                "file": f"val/{img_filename}",
                "race": "East Asian",
                "gender": "Female",
                "age": "20-29",
            }
        ]
    )

    processor = MockProcessor()
    dataset = FairFaceDataset(df=df, images_dir=img_dir, processor=processor)
    assert len(dataset) == 1

    pixels, meta = dataset[0]
    assert pixels.shape == (3, 224, 224)
    assert meta["image_name"] == img_filename
    assert meta["race"] == "East Asian"
    assert meta["gender"] == "Female"
    assert meta["age"] == "20-29"


def test_mobilenet_fairface_dataset_raises_on_missing_image(
    tmp_path: Path,
) -> None:
<<<<<<< Updated upstream
    """Cohort integrity test: missing or corrupted images MUST raise RuntimeError."""
=======
    """Audit-cohort integrity: missing/corrupted images MUST raise RuntimeError."""
>>>>>>> Stashed changes
    img_dir = tmp_path / "images"
    img_dir.mkdir()

    missing_filename = "missing_0002.jpg"
    df = pd.DataFrame(
        [
            {
                "file": f"val/{missing_filename}",
                "race": "Black",
                "gender": "Male",
                "age": "30-39",
            }
        ]
    )

    processor = MockProcessor()
    dataset = FairFaceDataset(df=df, images_dir=img_dir, processor=processor)

    with pytest.raises(RuntimeError) as exc_info:
        _ = dataset[0]

    assert "Audit-cohort integrity violation" in str(exc_info.value)
    assert "Synthetic image substitution is strictly prohibited" in str(exc_info.value)


@pytest.fixture
def mobilenet_synthetic_csv(tmp_path: Path) -> Path:
    """Construct schema-conforming predictions CSV representing MobileNetV2 outputs."""
    rows = []
    race_groups = [
        "White",
        "Black",
        "Latino_Hispanic",
        "East Asian",
        "Southeast Asian",
        "Indian",
        "Middle Eastern",
    ]
    img_id = 1
    for race in race_groups:
        for i in range(35):
            true_gender = "Male" if i % 2 == 0 else "Female"
            # Simulate slight disparity pattern
            if race == "Black" and true_gender == "Female" and (i % 3 == 0):
                pred_gender = "Male"
            else:
                pred_gender = true_gender

            rows.append(
                {
                    "face_name_align": f"mobilenet_{img_id}.jpg",
                    "race": race,
                    "gender": true_gender,
                    "age": "20-29",
                    "true_label": true_gender,
                    "predicted_label": pred_gender,
                }
            )
            img_id += 1

    csv_path = tmp_path / "fairface_predictions_mobilenet_val.csv"
    pd.DataFrame(rows).to_csv(csv_path, index=False)
    return csv_path


<<<<<<< Updated upstream
def test_mobilenet_ingestion_pipeline_strict(
    mobilenet_synthetic_csv: Path,
) -> None:
    """MobileNet predictions CSV passes DataIngestionPipeline under STRICT mode."""
=======
def test_mobilenet_ingestion_pipeline_strict(mobilenet_synthetic_csv: Path) -> None:
    """MobileNet predictions pass DataIngestionPipeline under STRICT mode."""
>>>>>>> Stashed changes
    pipeline = DataIngestionPipeline(
        config=IngestionConfig(
            validation_mode=ValidationMode.STRICT,
            true_label_col="true_label",
            predicted_label_col="predicted_label",
        )
    )
    result = pipeline.ingest_file(mobilenet_synthetic_csv)
    assert len(result.records) == 7 * 35
    assert result.validation_summary.is_valid is True
    assert result.validation_summary.rejected_records_count == 0


def test_mobilenet_audit_cli_execution(
    mobilenet_synthetic_csv: Path, tmp_path: Path
) -> None:
    """Full end-to-end CLI execution with MobileNetV2 predictions."""
    report_path = tmp_path / "audit_report_mobilenet.html"
    exit_code = main(
        [
            "audit",
            "-i",
            str(mobilenet_synthetic_csv),
            "-a",
            "race",
            "-o",
            str(report_path),
            "--model-name",
            "MobileNetV2 Gender Classifier (rizvandwiki/gender-classification)",
            "--dataset-name",
            "FairFace Benchmark (Validation Split)",
            "--bca-resamples",
            "1000",
            "--backend",
            "dual",
        ]
    )

    assert exit_code == 0
    assert report_path.exists()
    content = report_path.read_text(encoding="utf-8")
    assert "MobileNetV2 Gender Classifier" in content
    assert "Demographic Parity Difference" in content
    assert "Disparate Impact Ratio" in content
    assert "Equal Opportunity Difference" in content
    assert "Equalized Odds Difference" in content
