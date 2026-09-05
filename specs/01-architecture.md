# 01 - Architecture

**Status:** Partly implemented; see status labels below

## Pipeline

```text
Predictions CSV/JSON
        |
        v
PredictionsFileInterface -> SubjectRecord validation
        |
        v
CLI / audit orchestration
        |
        v
Fairness backend(s) -> statistical evidence -> MetricResult rows
        |
        v
Targeted explainability for eligible flagged results
        |
        v
Jinja2 report generator -> standalone HTML
```

## Components

| Component | Responsibility | Status |
| --- | --- | --- |
| `model_interface.py` | Adapt prediction files or in-process model output to records | File adapter implemented; in-process path is limited/deferred |
| `data_ingestion.py` | Validate and normalize demographic and task columns | Implemented and tested |
| `fairness/` | Compute and harmonize disparity metrics | Implemented and tested |
| `fairness/statistics.py` | Add p-values and confidence intervals | Implemented; verify report evidence end to end |
| `explainability.py` | Produce attribution evidence for eligible disparities | Current surrogate path implemented; richer spatial analysis deferred |
| `report/` | Render model-card and datasheet-oriented HTML | Implemented and tested offline |
| `cli.py` | Connect input, audit, and report stages | Implemented for predictions-file workflow |

## Design rules

Fairness backends follow a Strategy-style interface so independent implementations can be compared. Input adapters follow an Adapter-style boundary so the audit engine consumes one internal record shape. The schema boundary is the controlling contract between all stages.

The architecture is diagnostic only. No stage owns training, retraining, weight modification, or synthetic data creation.

## Deferred architecture

A web UI, PDF export, multi-dataset production workflow, and richer image-native SHAP/ITA pipeline are deferred (surrogate attribution is implemented) and not required to claim the current MVP. They may be researched separately, but must preserve the M1 schema and statistical safeguards.

See the [mid-level architecture reference](../docs/research/MID_LEVEL_ARCHITECTURE.md) for design rationale and [verification](09-verification.md) for evidence expectations.
