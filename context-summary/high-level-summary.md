# BiasAperture — High-Level Summary

## Project overview

BiasAperture is a diagnostic and evaluative framework for auditing demographic bias in facial analysis systems. It is designed to assess whether a third-party model behaves differently across demographic groups such as race, gender, and age, and to report the results in a regulator-legible, evidence-based format.

The project is explicitly scoped as diagnostic: it measures and explains bias, but does not retrain, mitigate, or debias models.

## Core purpose

The system is meant to answer a practical question:

> Does the model produce unequal outcomes for different demographic subgroups?

To answer this, the project ingests benchmark data, connects to a model or prediction stream, computes fairness metrics across subgroups, tests the statistical significance of observed disparities, explains the likely drivers of those disparities, and packages the findings into a compliance-oriented report.

## Main goals

- detect demographic disparity in model behavior
- compare performance across demographic subgroups and intersections
- compute fairness metrics using multiple backends as validation
- evaluate statistical confidence and significance
- explain model behavior with attribution-based methods
- produce a structured report suitable for review and governance use

## Key fairness metrics

The analytical core of the project focuses on four primary disparity metrics:

- demographic parity difference
- equalized odds difference
- equal opportunity difference
- disparate impact ratio

These metrics are computed using independent fairness backends such as Fairlearn and AIF360, which provides cross-validation and robustness in the evaluation pipeline.

## Statistical integrity requirements

The project does not report raw disparity numbers without supporting evidence. Every disparity result is expected to include:

- a chi-squared significance test
- a p-value with alpha = 0.05
- a 95% bootstrap confidence interval
- a sample size n
- explicit handling of small-sample subgroups

A key rule is the minimum subgroup sample-size guard: subgroups with n < 30 must not be assigned computed values. Instead, they should be marked as insufficient sample and the associated metric value should be null.

## Data pipeline

BiasAperture relies on dataset ingestion and validation as a foundation. The repository uses FairFace as its primary benchmark dataset (UTKFace was profiled and cut per Cut-List #2), with data profiling and validation workflows to ensure the demographic metadata and groupings are consistent.

The project treats data quality as central to fairness auditing because subgroup analysis is only trustworthy when the dataset and metadata are appropriately structured.

## Model integration and evaluation workflow

The general workflow is:

1. ingest dataset and demographic labels
2. prepare demographic bins and subgroup definitions
3. run or load model predictions
4. compare outputs across groups
5. compute fairness metrics and confidence intervals
6. test statistical significance
7. identify important intersectional disparities
8. explain flagged issues through attribution methods
9. generate final audit report

## Explainability layer

The project includes a surrogate attribution layer to connect disparities with
the demographic-dummy features used by the current implementation. Richer
spatial/pixel SHAP and ITA skin-tone proxy analysis remains a deferred design
item; do not describe it as implemented.

## Reporting and compliance

BiasAperture is designed to translate technical findings into a more formal audit or compliance artifact. The reporting layer is built to align with governance expectations and includes mappings to:

- EU AI Act Article 10
- NIST AI Risk Management Framework
- documentation practices such as model cards and datasheets

This makes the platform relevant beyond a pure research prototype: it functions as a structured audit and review artifact.

## Repository structure

The repository is organized into a few main areas:

- source implementation under src/bias_aperture
- tests under src/tests
- datasets and processed files under data
- research and governance material under docs and research
- LaTeX report sources under report
- automation and workflow scripts under scripts and sync.ps1

## Project status

The README indicates the project is in the final integration and reporting phase. Core milestones include:

- schema lock and baseline definition
- data ingestion and test matrix setup
- fairness metric engine and statistical validation
- surrogate explainability support (SHAP deferred)
- orchestration and final report generation

The Phase-2 Product Upgrade Sprint is a separate research-only effort covering
Tracks 21–38. Track 22 is parked, Track 23 is dropped, and 16 tracks are
currently available to claim. See `research/results/synth_phase2.md` for the
merged findings and open owner decisions.

## Scope boundaries

BiasAperture intentionally avoids several activities:

- model retraining
- fine-tuning or debiasing
- synthetic demographic data generation
- broad mitigation workflows

The framework is designed to diagnose fairness issues, not to fix them by changing the model itself.

## Why the project matters

This project sits at the intersection of fairness auditing, statistical testing, explainable AI, and AI governance. It provides a structured way to evaluate whether a facial-analysis system is equitable across demographic groups and to communicate evidence in a way that is useful for technical, research, and regulatory review.

## Short summary

BiasAperture is a fairness diagnostic platform for facial analysis systems that measures subgroup disparities, validates them statistically, explains their drivers, and presents findings in a compliance-oriented report without modifying the model itself.
