"""
BiasAperture internal schema — LOCKED at WP1 / Milestone M1.

Per report/src/chapters/systemArchitectureAndMethodology.tex §Project Plan
and Schedule: "WP1 fixes the classifier baseline and the internal
demographic schema every later module must honour." Any change to the
field names, dtypes, or label vocabularies below after M1 is a breaking
change to Stream A (WP2) and Stream B (WP3) and must be re-synced with
both before merging.

Classifier baseline locked this milestone: dchen236/FairFace (and
joojs/fairface) inference fork of the FairFace paper's official pretrained
ResNet-34 (fairface_alldata_20191111.pt, with res34_fair_align_multi_7_20190809.pt
as alternative), race_7 variant (finer-grained than race_4 — matches FairFace's
own 7 race groups and the requirements chapter's FairFace-primary dataset
choice). See requirements.tex FR-001.
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
    """One row of the common internal schema (FR-001) after ingestion and inference.

    Captures one face image, its demographic annotation, and the audited model's
    prediction for it.

    Attributes
    ----------
    image_id : str
        Unique identifier or filepath of the evaluated image.
    race : RaceLabel
        Demographic race annotation conforming to the locked 7-category taxonomy.
    gender : GenderLabel
        Demographic gender annotation conforming to the locked 2-category taxonomy.
    age : AgeLabel
        Demographic age group annotation conforming to the locked 9-bucket taxonomy.
    true_label : str
        Ground-truth label for the audited downstream classification task.
    predicted_label : str
        Model-predicted label for the audited downstream classification task.
    """

    image_id: str
    race: RaceLabel
    gender: GenderLabel
    age: AgeLabel
    true_label: str
    predicted_label: str


@dataclass(frozen=True, slots=True)
class MetricResult:
    """One row of the detection engine's output (FR-003/FR-004).

    Field set locked at M1: metric name, point estimate, confidence
    bounds, p-value, subgroup sample size, plus the subgroup identity
    and an explicit insufficient-sample flag per NFR-003.

    Attributes
    ----------
    metric_name : str
        Disparity metric evaluated (one of the Core Four disparity metrics).
    subgroup : str
        Subgroup stratum identifier (e.g. ``"race=Black"`` or ``"ALL"``).
    subgroup_sample_size : int
        Number of cohort samples in this subgroup ($n$).
    metric_value : float or None
        Computed disparity estimate, or None if insufficient sample ($n < 30$).
    ci_lower : float or None
        Lower bound of the 95% BCa bootstrap confidence interval.
    ci_upper : float or None
        Upper bound of the 95% BCa bootstrap confidence interval.
    p_value : float or None
        Statistical significance test p-value.
    insufficient_sample : bool, default=False
        Flag set True when $n < 30$ per NFR-003.
    raw_p_value : float or None, default=None
        Unadjusted asymptotic p-value prior to multiple testing correction.
    adjusted_p_value : float or None, default=None
        FWER-adjusted p-value after Holm-Bonferroni step-down correction.
    hypothesis_family : str or None, default=None
        Statistical hypothesis family grouping.
    adjustment_method : str or None, default=None
        Identifier of multiple hypothesis testing procedure applied.
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
    raw_p_value: float | None = field(default=None)
    adjusted_p_value: float | None = field(default=None)
    hypothesis_family: str | None = field(default=None)
    adjustment_method: str | None = field(default=None)

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
