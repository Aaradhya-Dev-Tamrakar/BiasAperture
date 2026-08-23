"""
BiasAperture internal schema — LOCKED at WP1 / Milestone M1.

Per report/src/chapters/systemArchitectureAndMethodology.tex §Project Plan
and Schedule: "WP1 fixes the classifier baseline and the internal
demographic schema every later module must honour." Any change to the
field names, dtypes, or label vocabularies below after M1 is a breaking
change to Stream A (WP2) and Stream B (WP3) and must be re-synced with
both before merging.

Classifier baseline locked this milestone: dchen236/FairFace inference
fork of the FairFace paper's official pretrained ResNet-34
(res34_fair_align_multi_7_20190809.pt), race_7 variant (finer-grained
than race_4 — matches FairFace's own 7 race groups and the requirements
chapter's FairFace-primary dataset choice). See requirements.tex FR-001.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

# ---------------------------------------------------------------------------
# Label vocabularies — verbatim from dchen236/FairFace predict.py output
# columns, race_7 model. Do not reorder: index position is not meaningful
# here (these are the *label strings*, not one-hot indices), but keeping
# insertion order matching the source repo's column order avoids silent
# transcription drift if someone re-derives this from the model later.
# ---------------------------------------------------------------------------

RACE_LABELS: tuple[str, ...] = (
    "White",
    "Black",
    "Latino_Hispanic",
    "East Asian",
    "Southeast Asian",
    "Indian",
    "Middle Eastern",
)

GENDER_LABELS: tuple[str, ...] = ("Male", "Female")

AGE_LABELS: tuple[str, ...] = (
    "0-2",
    "3-9",
    "10-19",
    "20-29",
    "30-39",
    "40-49",
    "50-59",
    "60-69",
    "70+",
)

RaceLabel = Literal[
    "White",
    "Black",
    "Latino_Hispanic",
    "East Asian",
    "Southeast Asian",
    "Indian",
    "Middle Eastern",
]
GenderLabel = Literal["Male", "Female"]
AgeLabel = Literal[
    "0-2", "3-9", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70+"
]

# NFR-003 — Data-Integrity Guard: subgroups below this size are flagged
# "insufficient sample, not reported" rather than assigned a metric value.
MIN_SUBGROUP_SAMPLE_SIZE: int = 30

# NFR-001 — Statistical Rigour: significance threshold.
ALPHA: float = 0.05

# NFR-002 — Uncertainty Quantification: minimum bootstrap resamples for
# any reported 95% confidence interval.
MIN_BOOTSTRAP_RESAMPLES: int = 1_000


@dataclass(frozen=True, slots=True)
class SubjectRecord:
    """
    One row of the common internal schema (FR-001) after ingestion and
    inference — one face image, its demographic annotation, and the
    audited model's prediction for it.

    Field set locked at M1:
        image_id, race, gender, age  — demographic annotation, aligned
            into this schema regardless of source dataset (FairFace or
            UTKFace) or custom-dataset field names (FR-001).
        true_label, predicted_label  — ground-truth and model-predicted
            values for whatever downstream task is being audited (e.g.
            gender classification as the audited task, with race/age as
            the protected subgroup axes — task label semantics are
            audit-specific and not fixed by this schema).
    """

    image_id: str
    race: RaceLabel
    gender: GenderLabel
    age: AgeLabel
    true_label: str
    predicted_label: str


@dataclass(frozen=True, slots=True)
class MetricResult:
    """
    One row of the detection engine's output (FR-003/FR-004), the shape
    Stream B's report template (WP3) is built against from week one so
    that WP5's mock-to-real swap is mechanical.

    Field set locked at M1: metric name, point estimate, confidence
    bounds, p-value, subgroup sample size — plus the subgroup identity
    the row applies to and an explicit insufficient-sample flag per
    NFR-003 (a flagged row has metric_value / p_value / ci as None,
    never a fabricated placeholder number).
    """

    metric_name: Literal[
        "demographic_parity_difference",
        "equalized_odds_difference",
        "equal_opportunity_difference",
        "disparate_impact_ratio",
    ]
    subgroup: str  # e.g. "race=Black" or "race=Black&gender=Female" for
    # intersectional rows — composite key format finalized in WP4, not
    # part of the M1 lock; this field's *presence* is locked, its
    # internal formatting is not.
    subgroup_sample_size: int
    metric_value: float | None
    ci_lower: float | None
    ci_upper: float | None
    p_value: float | None
    insufficient_sample: bool = field(default=False)

    def __post_init__(self) -> None:
        if self.subgroup_sample_size < MIN_SUBGROUP_SAMPLE_SIZE:
            if not self.insufficient_sample:
                raise ValueError(
                    f"subgroup_sample_size={self.subgroup_sample_size} is "
                    f"below MIN_SUBGROUP_SAMPLE_SIZE={MIN_SUBGROUP_SAMPLE_SIZE} "
                    "(NFR-003) but insufficient_sample was not set True."
                )
            if self.metric_value is not None:
                raise ValueError(
                    "insufficient_sample=True rows must not carry a "
                    "computed metric_value (NFR-003: flag, don't fabricate)."
                )
