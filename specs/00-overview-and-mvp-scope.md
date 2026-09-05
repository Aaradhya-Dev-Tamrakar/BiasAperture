# 00 - Overview and MVP Scope

**Status:** Living specification index  
**Project:** BiasAperture  
**Scope:** Phase 1 diagnostic audit pipeline

## Purpose

This folder is the implementation-facing specification set for BiasAperture. It explains the system boundary, data contracts, execution flow, audit methods, reporting output, and verification evidence in a form that can be reviewed beside the source code.

The project audits demographic disparities in facial-analysis predictions. It does not retrain models, fine-tune weights, debias model parameters, or generate synthetic faces.

## Phase 1 MVP

The MVP accepts a FairFace-aligned predictions file, validates it against the locked internal schema, computes the Core Four disparity metrics across demographic axes, attaches statistical evidence, optionally produces targeted explainability output, and writes a standalone HTML compliance report.

The current case study is FairFace validation data and a FairFace ResNet-34 prediction export. UTKFace was cut (per Cut-List #2); web UI, PDF export, and direct in-process inference remain outside the current implemented path unless explicitly enabled and verified.

## Authority and status

- **Normative schema:** [schema lock](../docs/schema-lock-m1.md) and the enforced definitions in [`src/bias_aperture/schema.py`](../src/bias_aperture/schema.py).
- **Detailed algorithms:** [low-level specification](../docs/research/LOW_LEVEL_SPECIFICATION.md), interpreted together with current source and tests.
- **Architecture reference:** [mid-level architecture](../docs/research/MID_LEVEL_ARCHITECTURE.md).
- **Acceptance criteria and scope decisions:** [BiasAperture-AT](../docs/BiasAperture-AT.md).
- **Historical or research-only material:** documents under `docs/research/` and `research/` are informative unless explicitly marked normative.

Each document uses status labels such as `Implemented`, `Tested`, `Deferred`, and `Needs confirmation`. A proposal is not an implementation claim.

## Documents

| Document | Coverage |
| --- | --- |
| [01 - Architecture](01-architecture.md) | Components and data flow |
| [02 - Data model](02-data-model.md) | Input and output contracts |
| [03 - Orchestrator](03-orchestrator.md) | CLI execution and handoffs |
| [04 - Intake and classification](04-intake-and-classification.md) | File ingestion and audit targets |
| [05 - Audit engine](05-audit-engine.md) | Core Four metrics and backends |
| [06 - Statistics and confidence](06-statistics-and-confidence.md) | Significance, bootstrap, and guards |
| [07 - Explainability](07-explainability.md) | Targeted attribution behavior |
| [08 - Report and compliance](08-report-and-compliance.md) | HTML and regulatory output |
| [09 - Verification](09-verification.md) | Tests and empirical evidence |
| [10 - Security and governance](10-security-and-governance.md) | Safety, provenance, and boundaries |
| [11 - Requirements traceability](11-requirements-traceability.md) | Requirement-to-evidence mapping |

## Change rule

Changes to the M1 schema are breaking changes. Update the schema lock, implementation, affected tests, and both workstreams together. New Phase 2 ideas must be labeled research-only and must not silently expand the MVP.
