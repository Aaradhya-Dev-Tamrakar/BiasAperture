# 09 - Verification

**Status:** Active verification specification

## Required checks

1. Unit tests cover schema invariants, ingestion, model interfaces, backend harmonization, known-answer metrics, and report contracts.
2. A known-answer dataset confirms the Core Four metric definitions and edge cases.
3. An end-to-end predictions-file run produces a readable standalone HTML report.
4. The generated report is checked for metric names, sample sizes, confidence intervals, p-values, and insufficient-sample guards.
5. FairFace record counts, label alignment, and subgroup support are recorded as empirical evidence rather than inferred from documentation.
6. Runtime and reproducibility claims include command, input artifact, environment, seed where applicable, and observed result.

## Evidence statuses

- `Implemented`: source behavior exists.
- `Tested`: an automated or repeatable check verifies it.
- `Partially implemented`: a bounded path works but broader behavior is missing.
- `Deferred`: research or future work, not an MVP claim.
- `Needs confirmation`: requires team/TA or final artifact review.

The final report and proposal tables should be derived from sealed evidence in [`docs/research/CLAIM_LEDGER.md`](../docs/research/CLAIM_LEDGER.md), not from unverified planning text.
