import json

import pytest

from bias_aperture.model_interface import (
    InProcessInterface,
    PredictionsFileInterface,
)


@pytest.fixture
def valid_csv(tmp_path):
    p = tmp_path / "preds.csv"
    p.write_text(
        "face_name_align,race,gender,age,gt_gender\n"
        "img1.jpg,Black,Female,20-29,Female\n"
        "img2.jpg,White,Male,30-39,Male\n"
        "img3.jpg,East Asian,Female,10-19,Male\n"
    )
    return p


@pytest.fixture
def valid_json(tmp_path):
    p = tmp_path / "preds.json"
    p.write_text(
        json.dumps(
            {
                "records": [
                    {
                        "face_name_align": "img4.jpg",
                        "race": "Indian",
                        "gender": "Male",
                        "age": "40-49",
                        "gt_gender": "Male",
                    }
                ]
            }
        )
    )
    return p


def test_csv_happy_path(valid_csv):
    iface = PredictionsFileInterface(
        valid_csv, true_label_col="gt_gender", predicted_label_col="gender"
    )
    records = list(iface.get_predictions())
    assert len(records) == 3
    assert records[2].true_label == "Male"
    assert records[2].predicted_label == "Female"


def test_json_happy_path(valid_json):
    iface = PredictionsFileInterface(
        valid_json, true_label_col="gt_gender", predicted_label_col="gender"
    )
    records = list(iface.get_predictions())
    assert len(records) == 1
    assert records[0].race == "Indian"


def test_unrecognised_race_label_rejected(tmp_path):
    p = tmp_path / "bad.csv"
    p.write_text(
        "face_name_align,race,gender,age,gt_gender\n"
        "img5.jpg,Caucasian,Female,20-29,Female\n"
    )
    iface = PredictionsFileInterface(
        p, true_label_col="gt_gender", predicted_label_col="gender"
    )
    with pytest.raises(ValueError, match="unrecognised race label"):
        list(iface.get_predictions())


def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        PredictionsFileInterface(
            "/nonexistent/path.csv",
            true_label_col="x",
            predicted_label_col="y",
        )


def test_unsupported_extension_rejected(tmp_path):
    p = tmp_path / "preds.txt"
    p.write_text("nonsense")
    iface = PredictionsFileInterface(p, true_label_col="x", predicted_label_col="y")
    with pytest.raises(ValueError, match="unsupported predictions-file extension"):
        list(iface.get_predictions())


def test_in_process_interface_not_implemented():
    iface = InProcessInterface(model=object(), framework="pytorch")
    with pytest.raises(NotImplementedError, match="see WP2"):
        list(iface.get_predictions())


def test_in_process_interface_rejects_bad_framework():
    with pytest.raises(ValueError, match="framework must be"):
        InProcessInterface(model=object(), framework="jax")
