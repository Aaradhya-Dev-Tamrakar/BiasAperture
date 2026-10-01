# AGENTS.md — Universal Developer & AI Agent Guidelines

> **Canonical System Guidelines**: This file serves as the single source of truth for all AI coding agents (Claude, Google DeepMind Antigravity, GitHub Copilot, OpenAI Codex, Cursor, Windsurf, etc.) and human developers contributing to **BiasAperture**. All assistant-specific instruction files (`CLAUDE.md`, `ANTIGRAVITY.md`, `AGENT.md`, `.github/copilot-instructions.md`) redirect directly here.

---

## 1. Project Overview & Non-Negotiable Constraints

### 1.1 Mission & Fellowship Context
- **Project**: BiasAperture (Demographic Bias Auditing Framework for Computer Vision Models).
- **Program**: Capstone Project for Fusemachines AI Fellowship (AIF) 2026.
- **Authors**: Aaradhya Dev Tamrakar (`@AaradhyaDT`) & Tisha Manandhar (`@tiixsha`).
- **Supervisor**: Shreejan Kisee (Technical Advisor, Fusemachines AI Fellowship).
- **Core Benchmark**: FairFace (97,698 released images on disk, 7 race groups). Secondary dataset UTKFace was evaluated and dropped (`[CUT]` per Cut-List #2 / Track 02).
- **Regulatory & Governance Mapping**: EU AI Act Article 10 & Annex IV, NIST AI RMF (Govern, Map, Measure).

### 1.2 Strict Diagnostic Scope
- BiasAperture is strictly a **diagnostic and evaluative platform**. It ingests datasets, runs model inferences, measures demographic disparities, computes statistical confidence, attributes features via surrogate attribution (SHAP deferred), and compiles compliance reports.
- **DO NOT** implement model retraining, fine-tuning, weights debiasing, or synthetic image generation.

### 1.3 Statistical & Safety Guards
- **NFR-001 (Significance Guard)**: Every reported disparity metric must carry a Chi-squared ($\chi^2$) asymptotic significance test ($p$-value, $\alpha=0.05$) with Fisher's exact test fallback where expected counts are low.
- **NFR-002 (Uncertainty Guard)**: Every reported disparity metric must include a 95% Bootstrap Confidence Interval ($B \ge 1,000$ resamples; BCa bootstrap).
- **NFR-003 (Sample Size Guard)**: `MIN_SUBGROUP_SAMPLE_SIZE = 30`. Subgroups with $n < 30$ samples must **never** carry computed values; they must have `insufficient_sample=True` and `metric_value=None` (enforced by `MetricResult.__post_init__`). Never fabricate values for small sample bins.

---

## 2. Frozen Schema & Taxonomies (Milestone M1 Lock)

Any modification to `src/bias_aperture/schema.py` (`SubjectRecord`, `MetricResult`, label taxonomies) is a **breaking change** across all development streams.

### 2.1 Locked Demographic Taxonomies
- **Race Labels (7)**: `White`, `Black`, `Latino_Hispanic`, `East Asian`, `Southeast Asian`, `Indian`, `Middle Eastern`
- **Gender Labels (2)**: `Male`, `Female`
- **Age Labels (9)**: `0-2`, `3-9`, `10-19`, `20-29`, `30-39`, `40-49`, `50-59`, `60-69`, `70+`

### 2.2 Core Four Disparity Metrics
1. `demographic_parity_difference`
2. `equalized_odds_difference`
3. `equal_opportunity_difference`
4. `disparate_impact_ratio`

---

## 3. Directory Layout & Architecture

### 3.1 Repository Layout
```
BiasAperture/
├── src/
│   ├── bias_aperture/
│   │   ├── schema.py              # Locked demographic & metric schemas (M1)
│   │   ├── model_interface.py     # Model adapter interface (PredictionsFileInterface & InProcessInterface)
│   │   ├── data_ingestion.py      # Stream Data (WP2) — FairFace loading, alias resolution & alignment
│   │   ├── explainability.py      # WP4 (FR-005) — surrogate attribution on flagged disparities (SHAP deferred)
│   │   ├── fairness/              # Detection engine package (WP4)
│   │   │   ├── base.py            # FairnessBackend interface & result types
│   │   │   ├── backends.py        # Harmonized FairlearnBackend & AIF360Backend
│   │   │   ├── metrics.py         # Pure mathematical implementations & OvR decomposition
│   │   │   └── statistics.py      # Bootstrap CI, Chi-square tests & divergence alerts
│   │   └── report/                # Stream Report (WP3) — HTML & Jinja2 generation
│   │       ├── generator.py       # Standalone zero-network HTML report compiler
│   │       └── templates/         # Offline Jinja2 report templates (report.html.j2)
│   └── tests/                     # Pytest suite (85 passing unit & integration tests)
├── docs/                          # Meta-documentation, schema lock, literature matrix
├── report/                        # LaTeX report source and compiled main.pdf
├── sync.ps1                       # Multi-remote sync script (origin & duo compulsory, org mirror)
├── sync.bat                       # Windows friction-free execution wrapper
└── pyproject.toml                 # Ruff & pytest configuration
```

### 3.2 Design Patterns & Coding Standards
- **Design Patterns**:
  - **Strategy Pattern**: Applied to fairness computation backends via `FairnessBackend` base class (`FairlearnBackend`, `AIF360Backend`).
  - **Adapter Pattern**: Applied to model inference via `ModelInterface` (`PredictionsFileInterface`, `InProcessInterface`).
- **Code Standards & Docstrings**:
  - PEP 8 compliance, 88-character line limit enforced strictly by `ruff`.
  - Strict type hints throughout (`from __future__ import annotations`, `typing`, `dataclasses`).
  - **Docstring Standard (NumPy Format)**: All modules, classes, methods, and functions must strictly adhere to the **NumPy Docstring Standard** (`numpydoc`). Standard sections include `Parameters`, `Returns`, `Yields`, `Raises`, `Attributes`, and `Notes`. Parameter types and return types must be specified in the type signature and detailed semantically in docstrings (e.g. shapes like `shape: (n,)`, ranges like `in [0, 1]`). Do not use Google-style (`Args:`) or Sphinx-style (`:param:`) docstrings.

---

## 4. Phase 2 Research Sprint Guidelines

Phase 2 is a separate research-only product-upgrade sprint covering **Tracks 21–38**:
- Consult `research/research tracks/PHASE2_CONTEXT.md` and `research/results/synth_phase2.md` before proposing or implementing product-upgrade work.
- **Track Status**: Track 22 is parked, Track 23 is dropped.
- **Constraint**: Phase 2 additions must remain strictly **additive** to the M1 schema and maintain the non-negotiable **diagnostic-only scope**.

---

## 5. Graphify Knowledge Graph Tooling

For architecture discovery, relationship tracing, or code location, leverage the local Graphify knowledge graph:
- **Query**: `graphify query "<question>"` when `graphify-out/graph.json` exists.
- **Path Tracing**: `graphify path "<A>" "<B>"` for component relationships.
- **Concept Deep-Dive**: `graphify explain "<concept>"` for focused architecture concepts.
- **Navigation**: Check `graphify-out/wiki/index.md` for broad navigation, or `graphify-out/GRAPH_REPORT.md` for comprehensive architecture reviews.
- **Rule of Thumb**: Only read raw source files when modifying specific code or when the graph lacks recent details.

---

## 6. Build, Test & Synchronization Commands

### 6.1 Dependency Management & Testing
We use `uv` for deterministic Python dependency management:
```powershell
# Run the complete test suite (85 tests passing)
uv run --extra dev pytest

# Lint code standards
uv run --extra dev ruff check src/

# Auto-fix lint and import sorting
uv run --extra dev ruff check --fix src/

# Format code (88-character line limit)
uv run --extra dev ruff format src/
```

### 6.2 Multi-Remote Synchronization (`sync.bat` / `sync.ps1`)
All repository version control operations must run through the sync utility to keep multi-remotes (`origin` and `duo` compulsory, `org` mirror) aligned:
```powershell
# Routine synchronization with conventional commit & issue reference
.\sync.bat -m "feat(scope): descriptive summary (#<issue_number>)"

# Safe pull only with autostash
.\sync.bat -PullOnly
```
*(On non-Windows or direct PowerShell environments, `pwsh -File .\sync.ps1` can also be used).*

### 6.3 Automated Issue Linking & Audit Trail Convention
- Always tag issue numbers in commit messages using `(#<issue_number>)` or `#<issue_number>`.
- The `.github/workflows/audit-trail-linker.yml` workflow automatically appends a verified 40-character SHA-1 audit comment directly to the corresponding GitHub issue upon push to `main`.

---

## 7. Git & Branching Strategy

- **`main`**: The canonical baseline and active research/development branch. All verification, documentation, and reporting converge directly here.
- **Historical Stream Checkpoints (Preserved)**:
  - `feat/stream-data`: Stream A (WP2) — Data ingestion & test matrix (fully absorbed into `main`).
  - `feat/stream-report`: Stream B (WP3) — Report template scaffolding (fully absorbed into `main`).
  - `feat/ui-ux-report`: UI/UX & Jinja2 design iterations (fully absorbed into `main`).
  - `feat/wp4-engine`: WP4 — Fairness backends & statistical testing (fully absorbed into `main`).
  - `feat/wp5-integration`: WP5 — Orchestration & mock-to-real integration (fully absorbed into `main`).
  - `update-literature-review`: PR #1 matrix & literature expansion (merged into `main`).
  *(Note: These branches are preserved as milestone checkpoints across remotes; all active work must branch from or merge directly into `main`).*

---

## 8. Report & Artifact Integrity

- **LaTeX Source & PDF**: Only tracked LaTeX source files (`report/src/`) and the compiled `report/main.pdf` are preserved in version control.
- **Build Artifact Hygiene**: Intermediate LaTeX build artifacts (`.aux`, `.bbl`, `.toc`, `.log`, `.fls`, `.fdb_latexmk`, etc.) must remain gitignored.
- **Primary Project References**:
  - `docs/BiasAperture-AT.md` (Master planning and trait-based task breakdown)
  - `docs/schema-lock-m1.md` (Locked M1 schema reference)
  - `docs/literature-review-matrix.md` (Foundational research papers)
  - `docs/research/` (`HIGH_LEVEL_SYNTHESIS.md`, `MID_LEVEL_ARCHITECTURE.md`, `LOW_LEVEL_SPECIFICATION.md`)
  - `report/src/chapters/systemArchitectureAndMethodology.tex` (Architecture, WBS, and Cut-List)
