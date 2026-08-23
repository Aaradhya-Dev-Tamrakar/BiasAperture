# BiasAperture

- A Diagnostic and Evaluative Framework for Auditing Demographic Bias in Facial Analysis Systems \*

A fairness and bias audit system proposal report submitted for the Fusemachines AI Fellowship Program, Kathmandu, Nepal.

**Authors:** Aaradhya Dev Tamrakar, Tisha Manandhar

**Supervisor:** Shreejan Kisee, Teaching Assistant, Fusemachines AI Fellowship

## Abstract

BiasAperture is a proposed diagnostic and evaluative software platform that computes subgroup and intersectional fairness metrics for a third-party facial-analysis model and reports them in a standardised, regulator-legible format. It is organised into five cooperating modules covering data ingestion, model interfacing, fairness-metric computation, explainability, and report generation. Its analytical core computes four disparity metrics — demographic parity difference, equalized odds difference, equal opportunity difference, and disparate impact ratio — using AIF360 and Fairlearn as independent, cross-validating backends, with every reported disparity accompanied by a chi-squared significance test and a bootstrap confidence interval. A SHAP-based explainability layer attributes flagged disparities to input features. Findings are traced to their specific basis under Article 10 of the EU AI Act and the corresponding function of the NIST AI Risk Management Framework. The design is validated against the FairFace benchmark dataset (with UTKFace evaluated and formally cut per Cut-List #2). BiasAperture is scoped strictly as diagnostic: it does not mitigate bias, retrain models, or generate synthetic demographic data.

## Repository Structure

```BiasAperture/
├── .github/                    # GitHub configuration & PR templates
│   └── pull_request_template.md
├── .pre-commit-config.yaml     # Pre-commit hooks (Ruff, formatting, file-size guards)
├── pyproject.toml              # PEP 517/621 package spec & tool configs (Ruff, pytest)
├── uv.lock                     # Deterministic dependency lockfile
├── data/                       # Datasets and test matrices (raw/ and processed/ gitignored)
│   └── README.md               # Dataset sourcing and FairFace setup instructions
├── research/                   # 20-Track Parallel Research Sprint
│   ├── research tracks/        # Track prompts and deliverables (Tracks 01–20)
│   ├── context feed/           # Context documents feeding research tracks
│   └── results/                # Stream syntheses (A–F) and cross-track conflict log
├── report/                     # LaTeX report source and compiled proposal
│   ├── main.tex                # Entry point
│   ├── vars.tex                # Title, authors, supervisor metadata
│   ├── at_fuse_aif.cls         # Document class
│   ├── references.bib
│   ├── main.pdf                # Compiled proposal (tracked; build artifacts are not)
│   └── src/                    # Frontmatter, chapters, backmatter, images
├── docs/                       # TA/reviewer-facing meta-documentation
│   ├── BiasAperture-AT.md      # Master project planning and task assignments (v7)
│   ├── schema-lock-m1.md       # Milestone M1 schema specification
│   ├── literature-review-matrix.md   # Paper matrix (9 papers, Walden format)
│   ├── DATA_GOVERNANCE.md      # Data governance, privacy & special-category protocol
│   ├── research/               # Research Synthesis & Verification Reports
│   │   ├── CLAIM_LEDGER.md         # Auditable Research Claim Ledger (ASSERTED -> VERIFIED -> REPRODUCIBLE)
│   │   ├── HIGH_LEVEL_SYNTHESIS.md (and .pdf)
│   │   ├── MID_LEVEL_ARCHITECTURE.md (and .pdf)
│   │   ├── LOW_LEVEL_SPECIFICATION.md (and .pdf)
│   │   └── VERIFICATION_AND_SCRUTINY_GUIDE.md
│   ├── CHANGELOG.md            # Auto-updated by sync.ps1 on each sync
│   └── fellowship/             # Official AIF guidelines & reference PDFs
├── vendor/                     # Offline TeX dependencies
├── src/                        # Implementation package:
│   ├── bias_aperture/          # Core package
│   │   ├── schema.py           # Locked demographic and metric schema (M1)
│   │   ├── model_interface.py  # ModelInterface & PredictionsFileInterface
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

```Overall Progress: [███████████░░░░░░░░░] 55% (M1 Schema & 20-Track Research Sprint Complete · M2 Ingestion & Reporting In Progress)

```

| Work Package / Milestone                          | Stream / Focus | Primary Owner            | Status      | Progress Bar                  | Deliverables & Implementation State                                                                                        |
| ------------------------------------------------- | -------------- | ------------------------ | ----------- | ----------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| **WP1 / M1: Schema Lock & Baseline**              | Foundations    | Joint                    | Completed   | `[████████████████████] 100%` | Locked schema (`schema.py`), FairFace ResNet-34 baseline fixed, test suite passing (22/22)                                 |
| **WP2 / M2: Data Ingestion & Test Matrix**        | Stream A       | Tisha (`@tiixsha`)       | In Progress | `[███████████░░░░░░░░░]  55%` | 20-track research complete, `ModelInterface` & `PredictionsFileInterface` implemented, alignment & test matrix specs ready |
| **WP3 / M2: Compliance Report Scaffolding**       | Stream B       | Tisha (`@tiixsha`)       | In Progress | `[█████████░░░░░░░░░░░]  45%` | EU AI Act & NIST mapping complete, offline standalone Jinja2 single-file HTML architecture & templates designed            |
| **WP4 / M3: Statistical Detection Engine & SHAP** | Stream C & D   | Aaradhya (`@AaradhyaDT`) | In Progress | `[████████░░░░░░░░░░░░]  40%` | Dual-backend harmonization (AIF360/Fairlearn), BCa bootstrap CI & χ² engine, SHAP attribution design locked                |
| **WP5 / M4: System Orchestration & Case Study**   | Integration    | Joint (Aaradhya/Tisha)   | In Progress | `[███░░░░░░░░░░░░░░░░░]  15%` | Dual-remote automated sync workflow operational, end-to-end integration pipeline & benchmark audit plan staged             |

## Branching & Workstreams

| Branch                 | Stream / Work Package | Primary Owner            | Target Focus & Verification Mandate                                                                |
| ---------------------- | --------------------- | ------------------------ | -------------------------------------------------------------------------------------------------- |
| `main`                 | Production / Base     | Joint                    | Stable base holding M1 schema, documentation, and LaTeX report                                     |
| `feat/stream-data`     | Stream A (WP2)        | Tisha (`@tiixsha`)       | FairFace dataset ingestion, `dlib` 5-point landmark alignment & demographic test-matrix            |
| `feat/stream-report`   | Stream B (WP3)        | Tisha (`@tiixsha`)       | Jinja2 HTML compliance report scaffolding, zero-network offline rendering, EU AI Act mapping       |
| `feat/wp4-engine`      | Stream C (WP4)        | Aaradhya (`@AaradhyaDT`) | Fairness backends harmonization (AIF360 + Fairlearn), BCa bootstrap CIs, and $\chi^2$ significance |
| `feat/wp5-integration` | Stream D (WP5)        | Aaradhya (`@AaradhyaDT`) | SHAP explainability layer, pipeline orchestration, and end-to-end benchmark case studies           |

## Research Verification & Viva Defense Allocation

Empirical claims are verified across independent audit streams as detailed in the [Verification & Scrutiny Guide](docs/research/VERIFICATION_AND_SCRUTINY_GUIDE.md):

- **Tisha Manandhar**: Leads defense on Dataset Integrity (FairFace 97.7k count verification & alignment), Demographic Test Matrix Scaffolding, Regulatory Alignment (EU AI Act Art. 10/13 & NIST AI RMF Measure 2.11), and Standalone Compliance Reporting.
- **Aaradhya Dev Tamrakar**: Leads defense on Statistical Significance Engine ($\chi^2$ asymptotic tests, BCa Bootstrap Confidence Intervals), Dual-Backend Harmonization (AIF360 vs Fairlearn Equalized Odds max-of-gaps), and SHAP Feature Attribution.

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

- **[LaTeX Workshop](https://marketplace.visualstudio.com/items?itemName=James-Yu.latex-workshop)** (James Yu) — compile, preview, autocomplete, SyncTeX
- **[LaTeX Utilities](https://marketplace.visualstudio.com/items?itemName=tecosaur.latex-utilities)** (tecosaur) — glossary/word-count add-ons on top of Workshop

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
