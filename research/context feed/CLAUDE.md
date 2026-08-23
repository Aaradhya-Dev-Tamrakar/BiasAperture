# CLAUDE.md — Assistant Instructions for BiasAperture

## Project Overview
**BiasAperture** is a diagnostic and evaluative framework for auditing demographic bias in third-party facial analysis systems submitted for the Fusemachines AI Fellowship (AIF) 2026.
- **Diagnostic Scope**: BiasAperture detects and reports bias; it does **not** mitigate bias, retrain models, or generate synthetic faces.
- **Benchmark Datasets**: Primary: FairFace (108,501 images, 7 race groups); Secondary: UTKFace.
- **Regulatory Mapping**: EU AI Act Article 10 & Annex IV, NIST AI RMF (Govern, Map, Measure).

---

## Commands & Workflows

### Environment & Testing
We use `uv` for deterministic dependency and environment management.

```bash
# Run pytest test suite
uv run --extra dev pytest

# Run linter and check code standards
uv run --extra dev ruff check src/

# Auto-fix lint and sorting issues
uv run --extra dev ruff check --fix src/

# Format code (88-char limit per TA standard)
uv run --extra dev ruff format src/
```

### Git & Sync Workflow
Never push directly without running the sync script or adhering to conventional commits.

```powershell
# Auto-sync to both remotes (origin and fuseai)
.\sync.ps1 -m "feat(scope): your descriptive message"

# Pull only with autostash
.\sync.ps1 -PullOnly
```

---

## Architecture & Locked Contracts

### 1. Schema Invariants (M1 Lock — `src/bias_aperture/schema.py`)
- **Race Labels (7)**: `White`, `Black`, `Latino_Hispanic`, `East Asian`, `Southeast Asian`, `Indian`, `Middle Eastern`
- **Gender Labels (2)**: `Male`, `Female`
- **Age Labels (9)**: `0-2`, `3-9`, `10-19`, `20-29`, `30-39`, `40-49`, `50-59`, `60-69`, `70+`
- **Core Four Disparity Metrics**:
  - `demographic_parity_difference`
  - `equalized_odds_difference`
  - `equal_opportunity_difference`
  - `disparate_impact_ratio`

### 2. Statistical & Safety Guards
- **NFR-003 (Sample Size Guard)**: `MIN_SUBGROUP_SAMPLE_SIZE = 30`. Subgroups with $n < 30$ **must** set `insufficient_sample=True` and `metric_value=None`. Never fabricate values for small sample bins.
- **NFR-001 (Significance)**: $\alpha = 0.05$ (Chi-squared test with exact $p$-values).
- **NFR-002 (Uncertainty)**: $\ge 1,000$ bootstrap resamples for 95% confidence intervals (`ci_lower`, `ci_upper`).

---

## Active Workstreams & Branch Mapping
- `main` — Stable baseline holding locked schema, docs, and proposal LaTeX.
- `feat/stream-data` — **Stream A (Data Pipeline)**: FairFace ingestion, validation, test matrix generation (Aaradhya).
- `feat/stream-report` — **Stream B (Report Scaffolding)**: Jinja2 HTML report templates, Model Cards / Datasheets structure (Aaradhya drafts, Tisha reviews).
- `feat/wp4-engine` — **WP4 (Detection Engine)**: Fairlearn & AIF360 backends, statistical validation, SHAP explainability (Tisha).

---

## Coding Standards
- **Style**: PEP 8 compliance, 88 character line limit enforced by `ruff`.
- **Typing**: Strict type hints (`from __future__ import annotations`, `typing`, `dataclasses`).
- **Interfaces**: Strategy pattern for fairness backends (`FairnessBackend`), Adapter pattern for model interface (`ModelInterface`).
