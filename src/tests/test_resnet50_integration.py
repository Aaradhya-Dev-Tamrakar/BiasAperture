"""
ResNet-50 Integration & Schema Compliance Tests (Model 3).

Verifies:
  1. Ingestion of ResNet-50 prediction CSV schema
     (face_name_align, race, gender, age, true_label, predicted_label)
  2. Strict validation and alignment against locked demographic taxonomies
  3. Auditing with dual consensus fairness backends (Fairlearn + AIF360)
  4. Core Four metric generation with BCa bootstrap CIs and chi-squared significance
  5. HTML compliance dossier rendering with Model Card metadata for ResNet-50
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from bias_aperture.cli import main
from bias_aperture.data_ingestion import (
    DataIngestionPipeline,
    IngestionConfig,
    ValidationMode,
)


@pytest.fixture
def resnet50_synthetic_csv(tmp_path: Path) -> Path:
    """Construct a schema-conforming predictions CSV representing ResNet-50 outputs."""
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
            if race == "Black" and true_gender == "Female" and (i % 3 == 0):
                pred_gender = "Male"
            else:
                pred_gender = true_gender

            rows.append(
                {
                    "face_name_align": f"{img_id}.jpg",
                    "race": race,
                    "gender": true_gender,
                    "age": "20-29",
                    "true_label": true_gender,
                    "predicted_label": pred_gender,
                }
            )
            img_id += 1

    csv_path = tmp_path / "fairface_predictions_resnet50_val.csv"
    pd.DataFrame(rows).to_csv(csv_path, index=False)
    return csv_path


def test_resnet50_ingestion_pipeline_strict(
    resnet50_synthetic_csv: Path,
) -> None:
    """ResNet-50 predictions CSV passes DataIngestionPipeline under STRICT mode."""
    pipeline = DataIngestionPipeline(
        config=IngestionConfig(
            validation_mode=ValidationMode.STRICT,
            true_label_col="true_label",
            predicted_label_col="predicted_label",
        )
    )
    result = pipeline.ingest_file(resnet50_synthetic_csv)
    assert len(result.records) == 7 * 35
    assert result.validation_summary.is_valid is True
    assert result.validation_summary.rejected_records_count == 0


def test_resnet50_audit_cli_execution(
    resnet50_synthetic_csv: Path, tmp_path: Path
) -> None:
    """Full end-to-end CLI execution with ResNet-50 predictions."""
    report_path = tmp_path / "audit_report_resnet50.html"
    exit_code = main(
        [
            "audit",
            "-i",
            str(resnet50_synthetic_csv),
            "-a",
            "race",
            "-o",
            str(report_path),
            "--model-name",
            "ResNet-50 Gender Classifier (crangana/trained-gender)",
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
    assert "ResNet-50 Gender Classifier" in content
    assert "Demographic Parity Difference" in content
    assert "Disparate Impact Ratio" in content
    assert "Equal Opportunity Difference" in content
    assert "Equalized Odds Difference" in content
