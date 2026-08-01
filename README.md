# BiasAperture

* A Diagnostic and Evaluative Framework for Auditing Demographic Bias in Facial Analysis Systems *

A fairness and bias audit system proposal report submitted for the Fusemachines AI Fellowship Program, Kathmandu, Nepal.

**Authors:** Aaradhya Dev Tamrakar, Tisha Manandhar
**Supervisor:** Shreejan Kisee, Teaching Assistant, Fusemachines AI Fellowship

## Abstract

BiasAperture is a proposed diagnostic and evaluative software platform that computes subgroup and intersectional fairness metrics for a third-party facial-analysis model and reports them in a standardised, regulator-legible format. It is organised into five cooperating modules covering data ingestion, model interfacing, fairness-metric computation, explainability, and report generation. Its analytical core computes four disparity metrics — demographic parity difference, equalized odds difference, equal opportunity difference, and disparate impact ratio — using AIF360 and Fairlearn as independent, cross-validating backends, with every reported disparity accompanied by a chi-squared significance test and a bootstrap confidence interval. A SHAP-based explainability layer attributes flagged disparities to input features. Findings are traced to their specific basis under Article 10 of the EU AI Act and the corresponding function of the NIST AI Risk Management Framework. The design is validated against the FairFace and UTKFace benchmark datasets. BiasAperture is scoped strictly as diagnostic: it does not mitigate bias, retrain models, or generate synthetic demographic data.

## Repository Structure

```BiasAperture/
├── report/                     # Report source (build this)
│   ├── main.tex                # Entry point
│   ├── vars.tex                # Title, authors, supervisor metadata
│   ├── at_fuse_aif.cls         # Document class (renamed from AaradhyaTisha_fuse_aif.cls)
│   ├── references.bib
│   ├── main.pdf                # Compiled proposal (tracked; build artifacts are not)
│   └── src/
│       ├── frontmatter/        # Cover, acknowledgements, abstract, TOC, abbreviations, symbols
│       ├── chapters/           # Intro, literature review, requirements, methodology, conclusion
│       ├── backmatter/         # Appendices: budget, timeline, schema, risk register
│       └── images/
├── vendor/                     # Offline copies of newtx, IEEEtran, kastrup (renamed from
│                                # "Agent dependencies") for environments without live CTAN/network
│                                # access. Not read by any .tex file — extract and install into
│                                # your local TeX tree only if pdflatex reports these missing.
├── LICENSE                     # MIT
└── README.md
```

**Changes from previous layout:** `LaTex/` → `report/`; `Agent dependencies/` → `vendor/` (no spaces); `AaradhyaTisha_fuse_aif.cls` → `at_fuse_aif.cls`; the stale `BiasAperture.zip` snapshot and tracked build artifacts (`.aux`, `.bbl`, `.toc`, etc.) have been removed from version control — they were already covered by `.gitignore` but had been committed prior to it being added.

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
