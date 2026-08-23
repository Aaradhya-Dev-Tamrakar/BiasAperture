# Track 03 — Pandas Data Validation Patterns
**Stream:** A (Data Pipeline) · **Priority:** 🔴 Critical · **Owner Focus:** Aaradhya (WP2)
**Estimated Time:** 30 min · **Feeds:** `data_ingestion.py`

## Instructions
1. Paste `CONTEXT.md` into Claude Desktop first
2. Then paste the prompt below
3. Save the output as `results/03_data_validation_patterns.md`

## Prompt

Research Python/pandas patterns for building a robust data ingestion pipeline for demographic face datasets. The pipeline must:
1. Load CSV files (FairFace predict.py output) into a stream of typed dataclass records
2. Validate every row against a locked schema: race ∈ {White, Black, Latino_Hispanic, East Asian, Southeast Asian, Indian, Middle Eastern}, gender ∈ {Male, Female}, age ∈ {0-2, 3-9, 10-19, 20-29, 30-39, 40-49, 50-59, 60-69, 70+}
3. Handle edge cases: missing columns, unexpected labels, NaN values, duplicate image_ids
4. Support both full FairFace (108,501 rows) and stratified dev subsets (n=5,000)
5. Produce summary statistics: per-subgroup counts, flagging any subgroup with n < 30

Provide code examples using pandas + dataclasses. Show both a strict-validation approach (raise on first error) and a permissive approach (collect all errors, report at end).
