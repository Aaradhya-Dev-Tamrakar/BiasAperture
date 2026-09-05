# AGENT.md — Developer & AI Agent Guidelines

This repository contains **BiasAperture**, a demographic bias auditing platform for computer vision models. All AI coding agents operating on this codebase must follow the rules and constraints below.

---

## 1. Non-Negotiable Project Constraints

1. **Strict Diagnostic Scope**:
   - The platform **only** ingests datasets, runs model inferences, measures demographic disparities, computes statistical confidence, attributes features with surrogate attribution (SHAP deferred), and outputs compliance reports.
   - **DO NOT** implement model retraining, fine-tuning, weights debiasing, or synthetic image generation.

2. **Schema Invariance (Milestone M1)**:
   - Any modification to `src/bias_aperture/schema.py` (`SubjectRecord`, `MetricResult`, label taxonomies) is a **breaking change** across both development streams.
   - Subgroups with $n < 30$ samples must **never** carry computed values; they must have `insufficient_sample=True` and `metric_value=None` (enforced by `MetricResult.__post_init__`).

3. **Statistical Integrity**:
   - Every reported disparity metric must be accompanied by:
     - Chi-squared significance test ($p$-value, $\alpha=0.05$).
     - 95% Bootstrap Confidence Interval ($B \ge 1,000$ resamples).
     - Explicit sample size $n$.

---

## 2. Directory Layout & Module Ownership

```
BiasAperture/
├── src/
│   ├── bias_aperture/
│   │   ├── schema.py              # Locked demographic and metric schemas (M1)
│   │   ├── model_interface.py     # PredictionsFileInterface & InProcessInterface
│   │   ├── data_ingestion.py      # Stream Data (WP2) — FairFace loading & alignment
│   │   ├── report/                # Stream Report (WP3) — HTML & Jinja2 generation
│   │   ├── fairness/              # WP4 — Fairlearn & AIF360 backends, statistics
│   │   └── explainability.py      # WP4 (FR-005) — surrogate attribution on flagged disparities (SHAP deferred)
│   └── tests/                     # Pytest suite
├── docs/                          # Meta-documentation, schema lock, literature matrix
├── report/                        # LaTeX report source and compiled main.pdf
├── sync.ps1                       # Multi-remote sync script (origin & duo compulsory, org mirror)
└── pyproject.toml                 # Ruff & pytest configuration
```

---

## 3. Build & Test Commands

- **Run all tests**: `uv run --extra dev pytest`
- **Lint code**: `uv run --extra dev ruff check src/`
- **Format code**: `uv run --extra dev ruff format src/`
- **Sync remotes**: `pwsh -File .\sync.ps1 -m "type(scope): summary"`

---

## 4. Git & Branching Strategy

- **`main`**: Canonical baseline and active research/development branch. All verification, documentation, and reporting converge directly here.
- **Historical Stream Checkpoints (Preserved)**:
  - `feat/stream-data`: Stream A (WP2) — Data ingestion & test matrix (fully absorbed into `main`).
  - `feat/stream-report`: Stream B (WP3) — Report template scaffolding (fully absorbed into `main`).
  - `feat/ui-ux-report`: UI/UX & Jinja2 design iterations (fully absorbed into `main`).
  - `feat/wp4-engine`: WP4 — Fairness backends & statistical testing (fully absorbed into `main`).
  - `feat/wp5-integration`: WP5 — Orchestration & mock-to-real integration (fully absorbed into `main`).
  - `update-literature-review`: PR #1 matrix & literature expansion (merged into `main`).
    _(Note: These branches are intentionally preserved as milestone snapshots across remotes; new work should branch from or target `main` directly)._

Always write conventional commit messages: `feat:`, `fix:`, `docs:`, `chore:`, `test:`, `refactor:`.
