"""
ModelInterface — FR-002 (Dual-Mode Model Interface), WBS 1.2.

"The system shall obtain predictions from a target facial-analysis model
either by direct in-process inference against a supplied PyTorch or
TensorFlow model object, or by batch ingestion of a precomputed
predictions file in CSV or JSON format."

Two concrete implementations of one abstract contract:
    - PredictionsFileInterface: implemented now. This is the
      non-negotiable-core mode per the descoping table (cutlist #4 keeps
      this if in-process inference is cut) and is what dchen236/FairFace's
      predict.py already produces as CSV output, so it is also the
      lowest-friction path to a real Stream A test matrix.
    - InProcessInterface: abstract contract only at M1. Concrete
      PyTorch/TensorFlow adapters are WP2 (Stream A) work once the
      classifier baseline's actual weights are wired in — left as
      NotImplementedError here rather than a fabricated stub so a call
      fails loudly instead of silently returning nothing.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Iterable, Iterator

import pandas as pd

from bias_aperture.schema import AGE_LABELS, GENDER_LABELS, RACE_LABELS, SubjectRecord

# Column names as produced by dchen236/FairFace's predict.py (race_7
# model). This is the one place a swap to a different classifier baseline
# would require an edit — every other module consumes SubjectRecord, not
# these raw column names.
_FAIRFACE_RACE_COL = "race"
_FAIRFACE_GENDER_COL = "gender"
_FAIRFACE_AGE_COL = "age"
_FAIRFACE_IMAGE_COL = "face_name_align"  # dchen236/FairFace's output column


class ModelInterface(ABC):
    """Abstract contract both concrete interfaces satisfy (FR-002)."""

    @abstractmethod
    def get_predictions(self) -> Iterator[SubjectRecord]:
        """Yield one SubjectRecord per subject, in the locked schema."""
        raise NotImplementedError


class InProcessInterface(ModelInterface):
    """
    Direct in-process inference against a supplied PyTorch or TensorFlow
    model object.

    Not implemented at M1 — WBS 1.2 scopes "predictions-file ingestion
    path" as the WP1 deliverable; the in-process adapter is Stream A
    (WP2) work once the FairFace classifier's actual weights file is
    available in the working environment. Concrete subclasses
    (e.g. TorchModelInterface) should be added under this class rather
    than modifying the schema or PredictionsFileInterface.
    """

    def __init__(self, model: Any, *, framework: str) -> None:
        if framework not in ("pytorch", "tensorflow"):
            raise ValueError(
                f"framework must be 'pytorch' or 'tensorflow', got {framework!r}"
            )
        self.model = model
        self.framework = framework

    def get_predictions(self) -> Iterator[SubjectRecord]:
        raise NotImplementedError(
            "In-process inference adapter not yet implemented — see WP2. "
            "Use PredictionsFileInterface with a precomputed predictions "
            "file in the interim (this is also the non-negotiable-core "
            "path per the report's descoping table)."
        )


class PredictionsFileInterface(ModelInterface):
    """
    Batch ingestion of a precomputed predictions file (CSV or JSON).

    Expects the FairFace race_7 baseline's output columns as produced by
    dchen236/FairFace's predict.py. true_label / predicted_label are
    read from caller-specified columns since the audited *task* label
    (e.g. gender-classification correctness) is audit-specific, not
    fixed by the demographic schema itself.
    """

    def __init__(
        self,
        path: str | Path,
        *,
        true_label_col: str,
        predicted_label_col: str,
    ) -> None:
        self.path = Path(path)
        self.true_label_col = true_label_col
        self.predicted_label_col = predicted_label_col
        if not self.path.exists():
            raise FileNotFoundError(f"predictions file not found: {self.path}")

    def _load_rows(self) -> Iterable[dict[str, Any]]:
        if self.path.suffix.lower() == ".csv":
            df = pd.read_csv(self.path)
            yield from df.to_dict(orient="records")
        elif self.path.suffix.lower() == ".json":
            with self.path.open() as f:
                data = json.load(f)
            if isinstance(data, dict):
                data = data.get("records", data.get("data", [data]))
            yield from data
        else:
            raise ValueError(
                f"unsupported predictions-file extension: {self.path.suffix} "
                "(FR-002 specifies CSV or JSON only)"
            )

    def get_predictions(self) -> Iterator[SubjectRecord]:
        for row in self._load_rows():
            race = row[_FAIRFACE_RACE_COL]
            gender = row[_FAIRFACE_GENDER_COL]
            age = row[_FAIRFACE_AGE_COL]

            if race not in RACE_LABELS:
                raise ValueError(
                    f"unrecognised race label {race!r} for "
                    f"{row.get(_FAIRFACE_IMAGE_COL, '<unknown image>')} — "
                    f"expected one of {RACE_LABELS} (schema locked at M1)"
                )
            if gender not in GENDER_LABELS:
                raise ValueError(
                    f"unrecognised gender label {gender!r} for "
                    f"{row.get(_FAIRFACE_IMAGE_COL, '<unknown image>')} — "
                    f"expected one of {GENDER_LABELS} (schema locked at M1)"
                )
            if age not in AGE_LABELS:
                raise ValueError(
                    f"unrecognised age label {age!r} for "
                    f"{row.get(_FAIRFACE_IMAGE_COL, '<unknown image>')} — "
                    f"expected one of {AGE_LABELS} (schema locked at M1)"
                )

            yield SubjectRecord(
                image_id=str(row[_FAIRFACE_IMAGE_COL]),
                race=race,
                gender=gender,
                age=age,
                true_label=str(row[self.true_label_col]),
                predicted_label=str(row[self.predicted_label_col]),
            )
