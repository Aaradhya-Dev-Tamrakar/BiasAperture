# ANTIGRAVITY.md — Google Antigravity & Gemini Coding Guidelines

## Mission & Purpose
This file provides specialized context and execution instructions for **Google DeepMind Antigravity** agents operating within the **BiasAperture** repository.

---

## Key Context & Metadata
- **Project**: BiasAperture (Capstone Project for Fusemachines AI Fellowship 2026)
- **Authors**: Aaradhya Dev Tamrakar (`AaradhyaDT`) & Tisha Manandhar (`tiixsha`)
- **Supervisor**: Shreejan Kisee (TA, Fusemachines AI Fellowship)
- **Primary References**:
  - `docs/BiasAperture-AT.md` (Master planning and trait-based task breakdown)
  - `docs/schema-lock-m1.md` (Locked M1 schema reference)
  - `docs/literature-review-matrix.md` (9 foundational research papers)
  - `docs/research/` (`HIGH_LEVEL_SYNTHESIS.md`, `MID_LEVEL_ARCHITECTURE.md`, `LOW_LEVEL_SPECIFICATION.md`)
  - `report/src/chapters/systemArchitectureAndMethodology.tex` (Architecture, WBS, and Cut-List)

---

## Role & Task Ownership Allocation

| Workstream | Branch | Primary Owner | Target Focus & Implementation State |
|---|---|---|---|
| **Stream Data (WP2)** | `feat/stream-data` | **Tisha (`@tiixsha`)** | FairFace ingestion & validation, disk count audit (97.7k), `dlib` 5-point alignment, demographic test matrix (100% complete) |
| **Stream Report (WP3)** | `feat/stream-report` | **Tisha (`@tiixsha`)** | Jinja2 offline HTML report template, Model Cards & Datasheets structure, EU AI Act & NIST mapping (100% complete) |
| **WP4 Detection Engine** | `feat/wp4-engine` | **Aaradhya (`@AaradhyaDT`)** | Pure-math metrics, Fairlearn + AIF360 backends, chi-squared tests, BCa bootstrap CIs (100% complete) |
| **WP5 Integration & CLI** | `feat/wp5-integration` | **Aaradhya (`@AaradhyaDT`)** / Joint | Conditional SHAP attribution, `bias-aperture` CLI facade, benchmark case studies (54/54 tests passing) |

---

## Operating Invariants for Antigravity

1. **Powershell & UV Tool Execution**:
   - Always run Python commands and tests via `uv`:
     ```powershell
     uv run --extra dev pytest
     uv run --extra dev ruff check src/
     uv run --extra dev ruff format src/
     ```
   - Sync remotes across configured endpoints (`origin` and `duo` compulsory, `org` optional mirror) via `pwsh`:
     ```powershell
     pwsh -File .\sync.ps1 -m "feat(module): description"
     ```

2. **Schema Protection**:
   - Never alter `SubjectRecord` or `MetricResult` field signatures in `src/bias_aperture/schema.py` without explicit multi-stream synchronization.
   - Enforce NFR-003 sample-size guard ($n \ge 30$) in all metric computations.

3. **Report Integrity**:
   - Only tracked LaTeX source and compiled `report/main.pdf` are preserved in version control.
   - LaTeX build artifacts (`.aux`, `.bbl`, `.toc`, `.log`, etc.) must remain gitignored.
