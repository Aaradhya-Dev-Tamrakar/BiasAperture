# BiasAperture

* A Diagnostic and Evaluative Framework for Auditing Demographic Bias in Facial Analysis Systems *

A fairness and bias audit system proposal report submitted for the Fusemachines AI Fellowship Program, Kathmandu, Nepal.

**Authors:** Aaradhya Dev Tamrakar, Tisha Manandhar
**Supervisor:** Shreejan Kisee, Teaching Assistant, Fusemachines AI Fellowship

## Abstract

BiasAperture is a proposed diagnostic and evaluative software platform that computes subgroup and intersectional fairness metrics for a third-party facial-analysis model and reports them in a standardised, regulator-legible format. It is organised into five cooperating modules covering data ingestion, model interfacing, fairness-metric computation, explainability, and report generation. Its analytical core computes four disparity metrics — demographic parity difference, equalized odds difference, equal opportunity difference, and disparate impact ratio — using AIF360 and Fairlearn as independent, cross-validating backends, with every reported disparity accompanied by a chi-squared significance test and a bootstrap confidence interval. A SHAP-based explainability layer attributes flagged disparities to input features. Findings are traced to their specific basis under Article 10 of the EU AI Act and the corresponding function of the NIST AI Risk Management Framework. The design is validated against the FairFace and UTKFace benchmark datasets. BiasAperture is scoped strictly as diagnostic: it does not mitigate bias, retrain models, or generate synthetic demographic data.

## Repository Structure

```BiasAperture/
├── .github/                    # GitHub configuration & PR templates
│   └── pull_request_template.md
├── .pre-commit-config.yaml     # Pre-commit hooks (Ruff, formatting, file-size guards)
├── pyproject.toml              # PEP 517/621 package spec & tool configs (Ruff, pytest)
├── uv.lock                     # Deterministic dependency lockfile
├── data/                       # Datasets and test matrices (raw/ and processed/ gitignored)
│   └── README.md               # Dataset sourcing and FairFace setup instructions
├── dev-logs/                   # Dated developer logs & master audit walkthroughs
├── research/                   # 20-Track Parallel Research Sprint
│   ├── research tracks/        # Track prompts and deliverables (Tracks 01–20)
│   ├── context feed/           # Context documents feeding research tracks
│   └── results/                # Stream syntheses (A–F) and cross-track conflict log
├── scripts/                    # Dataset exploration and verification scripts
│   ├── explore_fairface.py     # FairFace disk verification & attribute profiling
│   └── explore_utkface.py      # UTKFace comparison & DEX noise analysis
├── report/                     # LaTeX report source and compiled proposal
│   ├── main.tex                # Entry point
│   ├── vars.tex                # Title, authors, supervisor metadata
│   ├── at_fuse_aif.cls         # Document class
│   ├── references.bib
│   ├── main.pdf                # Compiled proposal (tracked; build artifacts are not)
│   └── src/                    # Frontmatter, chapters, backmatter, images
├── docs/                       # TA/reviewer-facing meta-documentation
│   ├── BiasAperture-AT.md      # Master project planning and task assignments (v10)
│   ├── PROPOSAL_DEFENSE_GUIDE.md # Comprehensive Viva defense Q&A guide
│   ├── PRE_PROPOSAL_READING_GUIDE.md # Reading guide & executive brief
│   ├── BiasAperture_NOVELTY_INTEGRATION_DEFENSE.md # Novelty & prior-art defense
│   ├── schema-lock-m1.md       # Milestone M1 schema specification
│   ├── literature-review-matrix.md   # Paper matrix (9 papers, Walden format)
│   ├── CHANGELOG.md            # Auto-updated by sync.ps1 on each sync
│   └── fellowship/             # Official AIF guidelines & reference PDFs
├── vendor/                     # Offline TeX dependencies
├── src/                        # Implementation package:
│   ├── bias_aperture/          # Core package
│   │   ├── schema.py           # Locked demographic and metric schema (M1)
│   │   ├── model_interface.py  # ModelInterface & PredictionsFileInterface
│   │   ├── data_ingestion.py   # FairFace ingestion & validation pipeline
│   │   ├── explainability.py   # SHAP & ITA explainability layer
│   │   ├── cli.py              # CLI entry point orchestrator (`bias-aperture`)
│   │   ├── fairness/           # WP4 detection engine package
│   │   └── report/             # WP3 report generation package
│   └── tests/                  # Automated pytest unit test suite (conftest.py, tests)
├── sync.ps1                    # Local git workflow: stage, conventional-commit, pull --rebase, push
├── LICENSE                     # MIT
├── AGENT.md                    # Universal AI agent & developer guidelines
├── CLAUDE.md                   # Claude assistant instructions
├── ANTIGRAVITY.md              # Google Antigravity & Gemini instructions
└── README.md
```

## Project Progress & Roadmap

```
Overall Progress: [██████░░░░░░░░░░░░░░] 32% (Milestone M1 Schema Locked)
```

| Work Package / Milestone | Stream / Focus | Status | Progress Bar | Deliverables & Implementation State |
|---|---|---|---|---|
| **WP1 / M1: Schema Lock & Baseline** | Foundations / Joint | Completed | `[████████████████████] 100%` | Locked schema (`schema.py`), FairFace ResNet-34 baseline fixed, test suite passing (14/14) |
| **WP2 / M2: Data Ingestion & Test Matrix** | Stream A (Aaradhya) | In Progress | `[██████░░░░░░░░░░░░░░]  30%` | Directory scaffolding (`data/`), FairFace sourcing guide, data ingestion pipeline in progress |
| **WP3 / M2: Compliance Report Scaffolding** | Stream B (Aaradhya/Tisha) | In Progress | `[████░░░░░░░░░░░░░░░░]  20%` | Package scaffolding (`report/`), Model Card & Jinja2 HTML generation structure in progress |
| **WP4 / M3: Statistical Detection Engine & SHAP** | WP4 (Tisha) | In Progress | `[██░░░░░░░░░░░░░░░░░░]  10%` | Fairness package scaffolded (`fairness/`), AIF360/Fairlearn backends, bootstrap CIs & SHAP planned |
| **WP5 / M4: System Orchestration & Case Study** | Integration / Joint | Planned | `[░░░░░░░░░░░░░░░░░░░░]   0%` | Mock-to-real swap, full FairFace benchmark audit run, and final report bundle export |

## Branching & Workstreams

| Branch | Stream / Work Package | Primary Owner | Description |
|---|---|---|---|
| `main` | Production / Base | Joint | Stable base holding M1 schema, docs, and report |
| `feat/stream-data` | Stream A (WP2) | Aaradhya (`@AaradhyaDT`) | FairFace dataset ingestion & test-matrix construction |
| `feat/stream-report` | Stream B (WP3) | Aaradhya (`@AaradhyaDT`), Tisha review | Jinja2 HTML compliance report scaffolding |
| `feat/wp4-engine` | WP4 | Tisha (`@tiixsha`) | Fairness computation backends, statistics, and SHAP |

## Python Development, Testing & Code Style

The project follows the [Khwopa / TA Engineering Standards](https://github.com/Khwopa-College-of-Engineering-KHCE/Image-Super-Resolution/tree/standards) for Python code style and testing:

```bash
# Run unit test suite
uv run --extra dev pytest

# Run linter and auto-formatter
uv run --extra dev ruff check --fix
uv run --extra dev ruff format

# Install pre-commit hooks (optional for local commits)
pre-commit install
```

## Local Git Workflow & Auto-Sync (`sync.ps1`)

```powershell
.\sync.ps1                                  # stage all, conventional-commit, pull --rebase, push
.\sync.ps1 -m "feat(scope): detailed summary"  # same, with an explicit commit message
.\sync.ps1 -PullOnly                        # git pull --autostash only, no commit/push
```

Every run (except `-PullOnly`) appends a timestamp entry to `docs/CHANGELOG.md` before committing.

## Building the Report

Requires a full TeX Live distribution (the class pulls in `booktabs`, `array`, `glossaries`, `newtxmath`, `siunitx`, `algorithmicx`, and others).

```bash
cd report
pdflatex -interaction=nonstopmode main.tex
makeglossaries main
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

The `makeglossaries` step is required — it sorts the raw abbreviation and symbol entries the class writes during the first pass into the `.acr`/`.sls` files the later passes typeset. Skipping it leaves the List of Abbreviations and List of Symbols pages blank. Overleaf runs this automatically; a plain local `pdflatex` invocation does not unless your editor or `latexmkrc` is configured to call it.

If `newtxmath.sty`, `IEEEtran.bst`, or `binhex.tex` are reported missing, install the corresponding package from `vendor/` into your local TeX tree (or via `tlmgr`/your package manager) rather than editing the source.

Build artifacts (`.aux`, `.bbl`, `.toc`, `.synctex.gz`, etc.) are git-ignored; only the source and the compiled `report/main.pdf` are tracked.

## VS Code Setup

Recommended extensions for editing/compiling `report/`:

* **[LaTeX Workshop](https://marketplace.visualstudio.com/items?itemName=James-Yu.latex-workshop)** (James Yu) — compile, preview, autocomplete, SyncTeX
* **[LaTeX Utilities](https://marketplace.visualstudio.com/items?itemName=tecosaur.latex-utilities)** (tecosaur) — glossary/word-count add-ons on top of Workshop

Skip generic "LaTeX" language-support extensions (e.g. Mathematic Inc's) — redundant with Workshop and can conflict on snippets/keybindings.

Workshop's default recipes don't run `makeglossaries`, which this build requires (see above). Add a custom recipe in `.vscode/settings.json`:

```json
{
  "latex-workshop.latex.tools": [
    {
      "name": "pdflatex",
      "command": "pdflatex",
      "args": ["-interaction=nonstopmode", "-synctex=1", "%DOC%"]
    },
    {
      "name": "makeglossaries",
      "command": "makeglossaries",
      "args": ["%DOCFILE%"]
    },
    {
      "name": "bibtex",
      "command": "bibtex",
      "args": ["%DOCFILE%"]
    }
  ],
  "latex-workshop.latex.recipes": [
    {
      "name": "pdflatex ➔ makeglossaries ➔ bibtex ➔ pdflatex ×2",
      "tools": ["pdflatex", "makeglossaries", "bibtex", "pdflatex", "pdflatex"]
    }
  ],
  "latex-workshop.latex.recipe.default": "lastUsed",
  "latex-workshop.latex.outDir": "%DIR%"
}
```

Set `report/main.tex` as the root file if Workshop doesn't auto-detect it.

## License

MIT — see [LICENSE](LICENSE).
