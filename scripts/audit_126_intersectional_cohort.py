"""
audit_126_intersectional_cohort.py

Audits the complete 7 x 9 x 2 = 126 Race x Age x Gender intersectional contingency grid
on the FairFace validation split (data/processed/fairface_predictions_val.csv, 10,954 records).

Enforces sample size reportability guard (NFR-003, n >= 30) per EU AI Act Article 10(5).
Outputs the structured audit dossier to docs/research/INTERSECTIONAL_COHORT_AUDIT_126.md.
"""

from collections import defaultdict
from pathlib import Path

from bias_aperture.data_ingestion import (
    DataIngestionPipeline,
    IngestionConfig,
    ValidationMode,
)
from bias_aperture.schema import (
    AGE_LABELS,
    GENDER_LABELS,
    MIN_SUBGROUP_SAMPLE_SIZE,
    RACE_LABELS,
)


def run_audit(
    val_csv: Path, output_md: Path | None = None
) -> dict[str, int | dict]:
    """Execute 126 intersectional cohort audit on validation dataset."""
    if not val_csv.exists():
        raise FileNotFoundError(f"Validation dataset not found: {val_csv}")

    print(f"[*] Ingesting and validating cohort from: {val_csv}...")
    config = IngestionConfig(
        true_label_col="true_label",
        predicted_label_col="predicted_label",
        image_id_col="face_name_align",
        race_col="race",
        gender_col="gender",
        age_col="age",
        validation_mode=ValidationMode.PERMISSIVE,
    )
    pipeline = DataIngestionPipeline(config)
    res = pipeline.ingest_file(val_csv)

    records = res.records
    total_subjects = len(records)
    print(f"[*] Successfully ingested {total_subjects} valid subject records.")

    matrix_126 = DataIngestionPipeline.compute_126_intersectional_matrix(records)

    total_cells = len(matrix_126)
    assert total_cells == 126, f"Expected 126 cells, got {total_cells}"

    eligible_cells = {k: v for k, v in matrix_126.items() if v.is_nfr003_eligible}
    sparse_cells = {
        k: v for k, v in matrix_126.items() if v.insufficient_sample_at_ingestion
    }

    n_eligible = len(eligible_cells)
    n_sparse = len(sparse_cells)
    sum_n = sum(v.total_n for v in matrix_126.values())

    print("=" * 60)
    print(" 126-COHORT INTERSECTIONAL AUDIT SUMMARY")
    print("=" * 60)
    print(f"Total Cohort Size (N):              {total_subjects:,}")
    print(f"Sum of Cell Counts:                 {sum_n:,} (Consistency Check: {'PASS' if sum_n == total_subjects else 'FAIL'})")
    print(f"Total Intersectional Cells:         126 (7 Races x 9 Ages x 2 Genders)")
    print(f"Eligible Cells (n >= {MIN_SUBGROUP_SAMPLE_SIZE}):            {n_eligible} ({n_eligible / 126 * 100:.1f}%)")
    print(f"Sparse Cells (n < {MIN_SUBGROUP_SAMPLE_SIZE}, NFR-003):      {n_sparse} ({n_sparse / 126 * 100:.1f}%)")
    print("=" * 60)

    # Breakdown by Race
    race_stats = defaultdict(lambda: {"total": 0, "eligible_cells": 0, "sparse_cells": 0})
    for k, cell in matrix_126.items():
        # format: race=...&age=...&gender=...
        parts = dict(p.split("=") for p in k.split("&"))
        r = parts["race"]
        race_stats[r]["total"] += cell.total_n
        if cell.is_nfr003_eligible:
            race_stats[r]["eligible_cells"] += 1
        else:
            race_stats[r]["sparse_cells"] += 1

    # Breakdown by Age
    age_stats = defaultdict(lambda: {"total": 0, "eligible_cells": 0, "sparse_cells": 0})
    for k, cell in matrix_126.items():
        parts = dict(p.split("=") for p in k.split("&"))
        a = parts["age"]
        age_stats[a]["total"] += cell.total_n
        if cell.is_nfr003_eligible:
            age_stats[a]["eligible_cells"] += 1
        else:
            age_stats[a]["sparse_cells"] += 1

    if output_md:
        output_md.parent.mkdir(parents=True, exist_ok=True)
        print(f"[*] Writing comprehensive markdown audit to: {output_md}...")
        _write_markdown_audit(
            output_md,
            total_subjects=total_subjects,
            matrix_126=matrix_126,
            race_stats=race_stats,
            age_stats=age_stats,
            n_eligible=n_eligible,
            n_sparse=n_sparse,
        )
        print(f"[SUCCESS] Audit report written to {output_md}")

    return {
        "total_subjects": total_subjects,
        "n_eligible": n_eligible,
        "n_sparse": n_sparse,
        "eligible_pct": n_eligible / 126 * 100,
        "sparse_pct": n_sparse / 126 * 100,
    }


def _write_markdown_audit(
    output_path: Path,
    *,
    total_subjects: int,
    matrix_126: dict,
    race_stats: dict,
    age_stats: dict,
    n_eligible: int,
    n_sparse: int,
) -> None:
    """Render markdown dossier for 126-cohort intersectional audit."""
    content = []
    content.append("# BiasAperture — 126-Cohort Intersectional Audit Matrix")
    content.append("")
    content.append("**Project:** BiasAperture (Demographic Bias Auditing Platform for Computer Vision)  ")
    content.append("**Work Package:** WP2 (Stream A: Data Ingestion & Governance) & WP3 (Reporting)  ")
    content.append("**Author:** Tisha Manandhar (`tiixsha`)  ")
    content.append("**Dataset:** FairFace Benchmark Validation Cohort (`data/processed/fairface_predictions_val.csv`)  ")
    content.append("**Sample Size Threshold:** $n \\ge 30$ (NFR-003, EU AI Act Article 10(5))  ")
    content.append("**Taxonomy Lock:** Milestone M1 (7 Races × 9 Age Bins × 2 Genders = 126 Cells)  ")
    content.append("")
    content.append("---")
    content.append("")
    content.append("## 1. Executive Summary")
    content.append("")
    content.append(
        "Under **EU AI Act Article 10(5)** and **NFR-003**, demographic auditing cannot rely exclusively "
        "on 1D marginal distributions (e.g. race alone or gender alone). Deeply marginalized intersectional "
        "subgroups may experience compounding error rates that remain obscured in aggregate performance figures."
    )
    content.append("")
    content.append(
        "However, intersectional partitioning rapidly dilutes sample sizes. Measuring performance disparities on "
        f"undersized subgroups ($n < {MIN_SUBGROUP_SAMPLE_SIZE}$) introduces statistical noise and invalidates "
        "asymptotic assumptions (Claim **R-008**, **R-009**). BiasAperture strictly enforces reportability suppression: "
        f"cells with $n < {MIN_SUBGROUP_SAMPLE_SIZE}$ are flagged as `insufficient_sample=True` with metric suppression."
    )
    content.append("")
    content.append("### Key Audit Metrics:")
    content.append(f"- **Evaluated Cohort Size:** {total_subjects:,} subjects")
    content.append(f"- **Total Intersectional Slices:** 126 (7 Races × 9 Age Bins × 2 Genders)")
    content.append(
        f"- **Statistically Reportable Cells ($n \\ge {MIN_SUBGROUP_SAMPLE_SIZE}$):** "
        f"**{n_eligible} / 126** ({n_eligible / 126 * 100:.1f}%)"
    )
    content.append(
        f"- **Sparse / Suppressed Cells ($n < {MIN_SUBGROUP_SAMPLE_SIZE}$):** "
        f"**{n_sparse} / 126** ({n_sparse / 126 * 100:.1f}%)"
    )
    content.append("")
    content.append("---")
    content.append("")
    content.append("## 2. Marginal Subgroup Distributions & Coverage Rates")
    content.append("")
    content.append("### A. By Protected Racial Category (18 Intersectional Slices per Race)")
    content.append("")
    content.append("| Racial Category | Total Sample ($n$) | Eligible Slices ($n \\ge 30$) | Sparse Slices ($n < 30$) | Intersectional Coverage |")
    content.append("|:---|:---:|:---:|:---:|:---:|")
    for r in RACE_LABELS:
        st = race_stats[r]
        tot = st["total"]
        el = st["eligible_cells"]
        sp = st["sparse_cells"]
        cov = el / 18 * 100
        content.append(f"| **{r}** | {tot:,} | {el} / 18 | {sp} / 18 | {cov:.1f}% |")
    content.append("")
    content.append("### B. By Age Group (14 Intersectional Slices per Age Bin)")
    content.append("")
    content.append("| Age Bracket | Total Sample ($n$) | Eligible Slices ($n \\ge 30$) | Sparse Slices ($n < 30$) | Intersectional Coverage |")
    content.append("|:---|:---:|:---:|:---:|:---:|")
    for a in AGE_LABELS:
        st = age_stats[a]
        tot = st["total"]
        el = st["eligible_cells"]
        sp = st["sparse_cells"]
        cov = el / 14 * 100
        content.append(f"| **{a}** | {tot:,} | {el} / 14 | {sp} / 14 | {cov:.1f}% |")
    content.append("")
    content.append("---")
    content.append("")
    content.append("## 3. Comprehensive 126-Cell Contingency Matrix")
    content.append("")
    content.append("The table below details all 126 demographic intersections. Cells tagged with `🚨 Sparse (n < 30)` ")
    content.append("are systematically screened from downstream disparity computations and marked `insufficient_sample=True`.")
    content.append("")
    content.append("| # | Race | Age Bracket | Gender | Sample Size ($n$) | NFR-003 Eligibility Status |")
    content.append("|:---:|:---|:---:|:---:|:---:|:---:|")

    idx = 1
    for r in RACE_LABELS:
        for a in AGE_LABELS:
            for g in GENDER_LABELS:
                k = f"race={r}&age={a}&gender={g}"
                cell = matrix_126[k]
                status = "✅ Eligible (n ≥ 30)" if cell.is_nfr003_eligible else "🚨 Sparse (n < 30)"
                content.append(f"| {idx} | {r} | {a} | {g} | {cell.total_n} | {status} |")
                idx += 1

    content.append("")
    content.append("---")
    content.append("")
    content.append("## 4. Viva Defense & Regulatory Audit Notes")
    content.append("")
    content.append(
        "1. **Infant & Geriatric Sparsity:** Across all racial cohorts, the extreme age brackets (`0-2`, `60-69`, `70+`) "
        "consistently yield the lowest representation, demonstrating empirical risk of undersized cohort bias in real-world CV deployments."
    )
    content.append(
        "2. **Harmonized Disparity Safeguard:** In accordance with Milestone M1 and Claim R-008, BiasAperture's dual backends "
        "(Fairlearn & AIF360) evaluate disparities across eligible strata while generating transparent regulatory disclosures "
        "for unmeasurable sparse cohorts per NIST AI RMF Measure 1.1."
    )
    content.append("")

    output_path.write_text("\n".join(content), encoding="utf-8")


if __name__ == "__main__":
    val_path = Path("data/processed/fairface_predictions_val.csv")
    out_path = Path("docs/research/INTERSECTIONAL_COHORT_AUDIT_126.md")
    run_audit(val_path, out_path)
