"""
End-to-End CLI Pipeline Integration Tests (WP5).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from bias_aperture.cli import build_parser, main


def test_cli_parser_defaults() -> None:
    parser = build_parser()
    args = parser.parse_args(["-i", "dummy_pred.csv"])
    assert args.predictions_file == Path("dummy_pred.csv")
    assert args.protected_attr == "race"
    assert args.output_report == Path("bias_aperture_report.html")
<<<<<<< HEAD
=======
    assert args.explain is True
>>>>>>> feat/wp4-engine


def test_cli_end_to_end_execution(tmp_path: Path) -> None:
    # 1. Create a synthetic predictions CSV file (32 White, 32 Black)
    single_block = [
        ("White", "Female", "20-29", "1", "1"),
        ("White", "Female", "20-29", "1", "1"),
        ("White", "Female", "20-29", "0", "1"),
        ("White", "Female", "20-29", "0", "0"),
        ("Black", "Female", "20-29", "1", "0"),
        ("Black", "Female", "20-29", "1", "1"),
        ("Black", "Female", "20-29", "0", "0"),
        ("Black", "Female", "20-29", "0", "0"),
    ]
    rows = []
    for b in range(8):
        for idx, (race, gender, age, true_lbl, pred_lbl) in enumerate(single_block):
            rows.append(
                {
                    "face_name_align": f"img_{b}_{idx}.jpg",
                    "race": race,
                    "gender": gender,
                    "age": age,
                    "true_label": true_lbl,
                    "predicted_label": pred_lbl,
                }
            )

    df = pd.DataFrame(rows)
    pred_csv = tmp_path / "fairface_predictions.csv"
    df.to_csv(pred_csv, index=False)

    out_report = tmp_path / "audit_output.html"

    # 2. Run CLI main
    exit_code = main(
        [
            "--predictions-file",
            str(pred_csv),
            "--protected-attr",
            "race",
            "--output-report",
            str(out_report),
        ]
    )

    assert exit_code == 0
    assert out_report.exists()
    content = out_report.read_text(encoding="utf-8")
    assert "Headline Fairness Metrics" in content
    assert "0.500" in content  # Known answer for DPD / EOD / EOP
