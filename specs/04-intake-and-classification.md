# 04 - Intake and Audit Classification

**Status:** File intake implemented and tested

## Supported intake

The primary MVP path reads a CSV or JSON prediction export. Source-specific columns are mapped into the common schema, including FairFace demographic columns and caller-selected `true_label` and `predicted_label` columns.

The FairFace baseline uses the race-7 taxonomy, two gender labels, and nine age bins. UTKFace was cut (per Cut-List #2) and is not part of the current case-study claim.

## Audit target

The audited task is defined by `true_label` and `predicted_label`. The protected attribute is selected independently, such as gender, race, age, or an intersectional grouping. This distinction prevents demographic annotations from being confused with the task being evaluated.

For multi-class targets, the audit engine may evaluate one-vs-rest class indicators. The per-class support must remain visible when macro summaries are used.

## Validation modes

- **Strict:** fail on missing required columns, invalid labels, malformed identifiers, and contradictory duplicates.
- **Profiling:** collect row-level anomalies for exploratory inspection without silently converting them into valid audit records.

The exact mode and supported source adapters must follow the current implementation. Direct in-process inference is an optional/deferred path and is not required for the predictions-file MVP.
