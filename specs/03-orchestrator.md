# 03 - Orchestrator

**Status:** Implemented for the predictions-file CLI path

## Run flow

1. Parse the predictions-file path, protected attribute, task columns, demographic column mappings, and output path.
2. Load and normalize rows through the model/data interfaces.
3. Validate demographic labels and task values.
4. Select the protected axis and subgroup rows.
5. Run one or more fairness backends.
6. Attach significance and confidence evidence.
7. Run explainability only for eligible flagged results.
8. Render the standalone HTML report.
9. Return a non-zero failure rather than emitting a misleading report when input or schema validation fails.

Example entry point:

```powershell
uv run bias-aperture --predictions-file data/processed/fairface_predictions_val.csv --protected-attr gender --true-label-col true_gender --predicted-label-col predicted_gender --race-col subgroup_race --gender-col subgroup_gender --age-col subgroup_age --output-report report/audit_report_val_gender.html
```

## Handoff contract

The ingestion stage provides records. The fairness stage provides `MetricResult`-shaped output. The report stage consumes those rows plus model, dataset, and governance metadata. No stage should infer missing schema values by fabrication.

## Failure behavior

Malformed columns, unmapped labels, invalid records, and impossible metric inputs are validation failures. Small subgroups are valid input but produce an explicit insufficient-sample result. Explainability failure must not turn an otherwise valid metric row into a claim of fairness.
