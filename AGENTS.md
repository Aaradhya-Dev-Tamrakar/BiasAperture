# AGENTS.md — Developer & AI Agent Guidelines

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
├── scripts/                       # Orchestration, sync, and verification scripts
│   ├── sync.ps1                   # Full PowerShell synchronization engine
│   ├── sync.bat                   # Windows execution wrapper
│   ├── sync.sh                    # POSIX shell execution wrapper
│   └── verify.py                  # Deterministic verification suite
├── Makefile                       # Universal POSIX build & sync interface
├── make.bat                       # Zero-dependency Windows make dispatcher
└── pyproject.toml                 # Ruff & pytest configuration
```

---

## 3. Build & Test Commands

- **Universal Makefile Entrypoints** (Recommended across POSIX & build pipelines):
  - **Run tests**: `make test` (or `uv run --extra dev pytest`)
  - **Lint code**: `make lint` (or `uv run --extra dev ruff check src/`)
  - **Format code**: `make format` (or `uv run --extra dev ruff format src/`)
  - **Deterministic verification**: `make verify` (or `python scripts/verify.py`)
  - **Generate audit report**: `make audit`
  - **Export companion PDF**: `make pdf`
  - **Clean cache artifacts**: `make clean`
- **Cross-Platform Multi-Remote Sync**:
  - **Universal**: `make sync ARGS="-m 'type(scope): summary (#issue)'"` (or `make sync -m "..."` on Windows)
  - **Windows**: `.\sync.bat -m "type(scope): summary (#issue)"` (or `.\scripts\sync.bat`)
  - **Linux / macOS**: `./scripts/sync.sh -m "type(scope): summary (#issue)"` (or `pwsh -File ./scripts/sync.ps1`)

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

Always write conventional commit messages: `feat:`, `fix:`, `docs:`, `chore:`, `test:`, `refactor:`. Include issue references (e.g., `(#22)` or `#22`) so that the `.github/workflows/audit-trail-linker.yml` CI workflow automatically attaches verified SHA-1 audit comments directly to the relevant GitHub issue.

- **Peer Review Protocol**:
  - When Aaradhya opens a PR: assign `AaradhyaDT` and request review from `tiixsha` (`gh pr create --assignee AaradhyaDT --reviewer tiixsha`).
  - When Tisha (`tiixsha`) opens a PR: assign `tiixsha` and request review from `AaradhyaDT` (`gh pr create --assignee tiixsha --reviewer AaradhyaDT`).

---

## 5. Report Harmonization & Export Standards (HTML & PDF)

All compliance dossiers generated by BiasAperture must adhere to the **`compliance-report-harmonizer`** standard:

1. **Harmonized Lexicon**:
   - **Harmonized**: Disparate backend primitives (Fairlearn group rates vs. AIF360 classification metrics) and regulatory articles (EU AI Act vs. NIST AI RMF) must be reconciled into consistent point estimates and compliance cross-references.
   - **Standardized**: Ingestion and reporting strictly adhere to Milestone M1 schema invariants ($n < 30$ sample suppression, 95% BCa bootstrap CIs, Pearson's $\chi^2$ significance tests).
   - **Uniform**: Visual card hierarchy, badge semantics (`PASS` = green, `WARN` = amber, `FAIL` = red, `GUARD` = indigo), and typography are identical across browser and print.
   - **Interoperable**: Dossiers operate simultaneously as air-gapped web dashboards, paginated A4 PDFs, and machine-readable `schema.org` JSON-LD.
   - **Cohesive**: Narrative descriptions, SVG metric whiskers, and datasheets fit together without contradictions.

2. **Offline Contract (R-015)**:
   - Exactly **0** external network requests: no external CDN scripts, no Google Fonts, no remote stylesheets, no external images.
   - All charts must be rendered as **raw inline `<svg>`** elements via Jinja2 macros.

3. **Dual-Format Output & Cross-Platform Headless Blink PDF Engine**:
   - Every audit output should provide both a standalone HTML dossier and an immutable A4 companion PDF.
   - PDF compilation must use `python scripts/export_report_pdf.py <report.html> <report.pdf>`.
   - **Platform Discovery Priority**:
     1. **Windows (Primary Development Environment)**: Automatically resolves `chrome.exe` and `msedge.exe` in `Program Files` and `LocalAppData`.
     2. **Linux (Servers, Containers & GitHub Actions CI)**: Resolves `google-chrome-stable`, `chromium-browser`, and `/usr/bin/chromium` using `--no-sandbox` and `--disable-setuid-sandbox` container flags.
     3. **macOS**: Resolves `/Applications/Google Chrome.app` or Homebrew chromium.


