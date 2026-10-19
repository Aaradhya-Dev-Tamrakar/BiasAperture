"""Regression and unit tests for FairFaceImageDataset and ViT prediction pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest
from PIL import Image

# Ensure scripts directory is importable
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.predict_vit import (  # noqa: E402
    FairFaceImageDataset,
    normalize_gender_label,
)


def test_fairface_image_dataset_valid_read(tmp_path: Path) -> None:
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

    dataset = FairFaceImageDataset(image_dir=img_dir, df=df)
    assert len(dataset) == 1

    loaded_img, metadata = dataset[0]
    assert isinstance(loaded_img, Image.Image)
    assert loaded_img.size == (100, 100)
    assert metadata["face_name_align"] == img_filename
    assert metadata["race"] == "East Asian"
    assert metadata["gender"] == "Female"
    assert metadata["age"] == "20-29"


def test_fairface_image_dataset_raises_on_missing_image(tmp_path: Path) -> None:
    """Audit-cohort integrity test: missing images raise RuntimeError."""
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

    dataset = FairFaceImageDataset(image_dir=img_dir, df=df)

    with pytest.raises(RuntimeError) as exc_info:
        _ = dataset[0]

    err_msg = str(exc_info.value)
    assert "Audit-cohort integrity violation" in err_msg
    assert missing_filename in err_msg
    assert "Synthetic image substitution is strictly prohibited" in err_msg


def test_fairface_image_dataset_raises_on_corrupted_image(tmp_path: Path) -> None:
    """Audit-cohort integrity test: corrupted images raise RuntimeError."""
    img_dir = tmp_path / "images"
    img_dir.mkdir()

    corrupt_filename = "corrupted_0003.jpg"
    corrupt_path = img_dir / corrupt_filename
    corrupt_path.write_bytes(b"NOT_A_VALID_IMAGE_FILE_CONTENT")

    df = pd.DataFrame(
        [
            {
                "file": f"val/{corrupt_filename}",
                "race": "Latino_Hispanic",
                "gender": "Female",
                "age": "40-49",
            }
        ]
    )

    dataset = FairFaceImageDataset(image_dir=img_dir, df=df)

    with pytest.raises(RuntimeError) as exc_info:
        _ = dataset[0]

    err_msg = str(exc_info.value)
    assert "Audit-cohort integrity violation" in err_msg
    assert corrupt_filename in err_msg
    assert "Synthetic image substitution is strictly prohibited" in err_msg


def test_normalize_gender_label() -> None:
    """Verify gender label normalization logic."""
    assert normalize_gender_label("female") == "Female"
    assert normalize_gender_label("woman") == "Female"
    assert normalize_gender_label("Female ") == "Female"
    assert normalize_gender_label("male") == "Male"
    assert normalize_gender_label("man") == "Male"
    assert normalize_gender_label("Male") == "Male"
