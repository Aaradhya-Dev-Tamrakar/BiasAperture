# 08 - Report and Compliance

**Status:** Standalone HTML report implemented; final evidence review active

## Output contract

The report is a standalone HTML file suitable for offline opening. It contains model and dataset metadata, audit configuration, metric rows, statistical evidence, limitations, and governance context. Embedded charts or explainability artifacts must not require an external CDN or service.

Every metric row must show:

- metric name and subgroup;
- subgroup sample size;
- point estimate when reportable;
- 95% confidence interval when defined;
- exact p-value when tested; or
- an explicit `n < 30` insufficient-sample flag.

## Compliance structure

The report is organized using Model Card and Dataset Datasheet ideas. Regulatory notes map findings to relevant EU AI Act data-governance/transparency obligations and NIST AI RMF functions. These mappings provide audit context; they are not legal advice or a certification.

The training-data section must preserve the diagnostic boundary: BiasAperture audits a supplied model and does not train or modify it.

The generated artifact currently used for the case study is `report/audit_report_val_gender.html`. Its contents must be inspected before empirical claims are finalized.
