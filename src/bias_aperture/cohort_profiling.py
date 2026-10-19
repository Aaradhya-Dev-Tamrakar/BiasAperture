"""Demographic cohort support counts and intersectional eligibility profiles."""

from __future__ import annotations

from collections.abc import Sequence

from bias_aperture.ingestion_contracts import SubgroupCellStats, SubgroupCohortProfile
from bias_aperture.schema import (
    AGE_LABELS,
    GENDER_LABELS,
    MIN_POSITIVE_SUPPORT,
    MIN_SUBGROUP_SAMPLE_SIZE,
    RACE_LABELS,
    SubjectRecord,
    format_intersectional_key,
)


def compute_cohort_profile(
    records: Sequence[SubjectRecord],
    *,
    task_positive_label: str | None = None,
) -> SubgroupCohortProfile:
    """
    Compute demographic support counts and NFR-003 eligibility across
    unitary demographic axes and composite intersectional slices.
    """
    total = len(records)
    race_groups: dict[str, list[SubjectRecord]] = {r: [] for r in RACE_LABELS}
    gender_groups: dict[str, list[SubjectRecord]] = {g: [] for g in GENDER_LABELS}
    age_groups: dict[str, list[SubjectRecord]] = {a: [] for a in AGE_LABELS}
    intersectional_groups: dict[str, list[SubjectRecord]] = {}

    for rec in records:
        if rec.race in race_groups:
            race_groups[rec.race].append(rec)
        if rec.gender in gender_groups:
            gender_groups[rec.gender].append(rec)
        if rec.age in age_groups:
            age_groups[rec.age].append(rec)

        inter_key = format_intersectional_key(race=rec.race, gender=rec.gender)
        intersectional_groups.setdefault(inter_key, []).append(rec)

    def _build_stats(
        subgroup_key: str, sub_records: list[SubjectRecord]
    ) -> SubgroupCellStats:
        n_sub = len(sub_records)
        pos_n: int | None = None
        neg_n: int | None = None

        if task_positive_label is not None:
            pos_n = sum(
                1 for r in sub_records if str(r.true_label) == str(task_positive_label)
            )
            neg_n = n_sub - pos_n
            has_pos = pos_n >= MIN_POSITIVE_SUPPORT
            has_neg = neg_n >= MIN_POSITIVE_SUPPORT
        else:
            has_pos = True
            has_neg = True

        is_eligible = n_sub >= MIN_SUBGROUP_SAMPLE_SIZE
        is_insufficient = n_sub < MIN_SUBGROUP_SAMPLE_SIZE

        return SubgroupCellStats(
            subgroup_key=subgroup_key,
            total_n=n_sub,
            positive_n=pos_n,
            negative_n=neg_n,
            is_nfr003_eligible=is_eligible,
            has_positive_support=has_pos,
            has_negative_support=has_neg,
            insufficient_sample_at_ingestion=is_insufficient,
        )

    race_counts = {
        f"race={r}": _build_stats(f"race={r}", race_groups[r]) for r in RACE_LABELS
    }
    gender_counts = {
        f"gender={g}": _build_stats(f"gender={g}", gender_groups[g])
        for g in GENDER_LABELS
    }
    age_counts = {
        f"age={a}": _build_stats(f"age={a}", age_groups[a]) for a in AGE_LABELS
    }
    inter_counts = {k: _build_stats(k, v) for k, v in intersectional_groups.items()}

    inter_126_counts = compute_126_intersectional_matrix(
        records, task_positive_label=task_positive_label
    )

    insufficient_keys: list[str] = [
        k
        for d in (race_counts, gender_counts, age_counts, inter_counts)
        for k, v in d.items()
        if v.insufficient_sample_at_ingestion
    ]

    return SubgroupCohortProfile(
        total_subjects=total,
        race_counts=race_counts,
        gender_counts=gender_counts,
        age_counts=age_counts,
        intersectional_counts=inter_counts,
        insufficient_subgroups=insufficient_keys,
        intersectional_126_counts=inter_126_counts,
    )


def compute_126_intersectional_matrix(
    records: Sequence[SubjectRecord],
    *,
    task_positive_label: str | None = None,
) -> dict[str, SubgroupCellStats]:
    """Compute the full 7 x 9 x 2 = 126 intersectional grid (FR-002, NFR-003).

    Systematically enumerates all 126 intersectional demographic cells defined
    by the locked FairFace taxonomies (RACE_LABELS, AGE_LABELS, GENDER_LABELS).
    Guarantees that every cell is represented, calculating exact sample sizes
    and flagging whether n >= 30 (eligible) or n < 30 (insufficient / sparse).
    """
    cell_records: dict[tuple[str, str, str], list[SubjectRecord]] = {
        (r, a, g): [] for r in RACE_LABELS for a in AGE_LABELS for g in GENDER_LABELS
    }

    for rec in records:
        key = (rec.race, rec.age, rec.gender)
        if key in cell_records:
            cell_records[key].append(rec)

    stats_map: dict[str, SubgroupCellStats] = {}
    for (r, a, g), sub_records in cell_records.items():
        cell_key = f"race={r}&age={a}&gender={g}"
        n_sub = len(sub_records)
        pos_n: int | None = None
        neg_n: int | None = None

        if task_positive_label is not None:
            pos_n = sum(
                1
                for rec in sub_records
                if str(rec.true_label) == str(task_positive_label)
            )
            neg_n = n_sub - pos_n
            has_pos = pos_n >= 5
            has_neg = neg_n >= 5
        else:
            has_pos = True
            has_neg = True

        is_eligible = n_sub >= MIN_SUBGROUP_SAMPLE_SIZE
        is_insufficient = n_sub < MIN_SUBGROUP_SAMPLE_SIZE

        stats_map[cell_key] = SubgroupCellStats(
            subgroup_key=cell_key,
            total_n=n_sub,
            positive_n=pos_n,
            negative_n=neg_n,
            is_nfr003_eligible=is_eligible,
            has_positive_support=has_pos,
            has_negative_support=has_neg,
            insufficient_sample_at_ingestion=is_insufficient,
        )

    return stats_map
