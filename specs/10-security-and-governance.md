# 10 - Security and Governance

**Status:** Scope and governance requirements

## Diagnostic boundary

BiasAperture may ingest data, run or consume predictions, measure disparities, compute statistical evidence, attribute model behavior, and produce reports. It must not retrain, fine-tune, alter model weights, generate synthetic faces, or present mitigation as an audit result.

## Data governance

Document dataset provenance, license, annotation meaning, demographic-label limitations, and any filtering or preprocessing. Treat face images and prediction files as sensitive research data. Keep raw data out of source control where repository policy requires it, and avoid exposing personally identifying content in generated reports.

## Reproducibility and integrity

Record input artifact identity, configuration, package/environment information, random seeds, and output location for repeatable runs. Preserve exact p-values and confidence bounds. Never replace missing or invalid evidence with plausible-looking constants.

Regulatory references in reports are explanatory mappings and do not constitute legal certification. Claims about compliance require human review.
