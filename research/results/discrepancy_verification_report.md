# Discrepancy Ledger — Independent Verification Report

Verified against live files on `feat/stream-report` @ `7063688` (2026-09-05).

---

## Summary Verdict

**The ledger is overwhelmingly accurate.** Every HIGH-severity claim I checked is confirmed by the source files. However, there are a few nuances — some items are slightly mischaracterized, and the ledger itself has notable coverage gaps, particularly in the README.

| Cluster | Claims Checked | Confirmed | Mischaracterized | Missed by Ledger |
|:--------|:-:|:-:|:-:|:-:|
| **A — Dataset Scale** | 7 | 7 ✅ | 0 | 2 |
| **B — SHAP vs Surrogate** | 10 | 10 ✅ | 0 | 1 |
| **C — Architecture/Structural** | 8 | 8 ✅ | 1 (nuance) | 1 |
| **D — WP Completion** | 5 | 5 ✅ | 0 | 0 |

---

## Cluster A — Dataset Scale (108,501 vs 97,698) & UTKFace

### ✅ Confirmed Discrepancies

| Ledger Claim | Verification | Status |
|:---|:---|:---:|
| [back.tex:20](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/report/src/backmatter/back.tex#L20) — "full 108{,}501-image FairFace" | **CONFIRMED.** Line reads exactly `full 108{,}501-image FairFace evaluation (NFR-004)` with no qualifier. | ✅ |
| [abstract.tex:4](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/report/src/frontmatter/abstract.tex#L4) — "validated against the FairFace and UTKFace benchmark datasets" | **CONFIRMED.** UTKFace framed as active co-validation, no mention of cut status. | ✅ |
| [intro.tex:26](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/report/src/chapters/intro.tex#L26) — "principally FairFace and UTKFace" | **CONFIRMED.** Dual-dataset framing, no cut caveat. | ✅ |
| [intro.tex:33](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/report/src/chapters/intro.tex#L33) — "validated against FairFace and UTKFace" in Scope | **CONFIRMED.** Same dual-dataset claim, no "cut" language. | ✅ |
| [systemArchitectureAndMethodology.tex:46](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/report/src/chapters/systemArchitectureAndMethodology.tex#L46) — "initially FairFace and UTKFace" | **CONFIRMED.** Frames UTKFace as active dataset for ingestion. Same file's own cut-list table (:188) correctly marks UTKFace as cut — internal self-contradiction confirmed. | ✅ |
| [conclusion.tex:6](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/report/src/chapters/conclusion.tex#L6) — "validation against FairFace and UTKFace" | **CONFIRMED.** Claims UTKFace validation satisfies an objective. | ✅ |
| [literatureReview.tex:20](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/report/src/chapters/literatureReview.tex#L20) — UTKFace as "secondary benchmark" | **CONFIRMED.** Says "uses UTKFace only as a secondary benchmark" — undersells the full exclusion. | ✅ |

### 🔍 Missed by the Ledger

1. **[README.md:20](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/README.md#L20) — Mermaid diagram still says `108,501 images`.**
   The ledger's Cluster A table doesn't list the README Mermaid diagram as a stale 108,501 hit. The fix ledger's Gate 2 section notes the FF node "already correct" at `:20` showing `97,698 images` — but **that is wrong**. The actual file right now reads:
   ```
   FF[("FairFace dataset<br/>108,501 images")]
   ```
   This is a **confirmed stale claim in the README diagram that the ledger missed AND the fix ledger misreported as "already correct."**

2. **[README.md:52](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/README.md#L52) — "consumes the FairFace (108,501 images)".**
   Also a bare 108,501 in the README's architecture bullets. Not listed in the ledger's Cluster A stale-figures table. The ledger says "All of `docs/`, `dev-logs/`, `README.md`... correctly show 97,698" — **this is factually wrong for the README**. The README has two bare 108,501 hits (lines 20 and 52).

> [!CAUTION]
> The fix ledger (Gate 2, §README.md diagram bullets) claims `FF node (:20) "97,698 images" — already correct, no fix`. This is **incorrect** — the actual file says `108,501 images`. This is a critical error in the fix ledger's own verification.

---

## Cluster B — Explainability: SHAP vs Surrogate

### Ground Truth Confirmed

Verified [explainability.py](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/src/bias_aperture/explainability.py):
- Class is `ShapExplainerEngine` (line 50)
- `explain_disparity()` (line 66): if `records` are supplied → calls `explain_surrogate()` first (line 85). Only if no records AND SHAP import succeeds does it use SHAP (line 88–98). On exception → falls back to surrogate message (line 99–107).
- `explain_surrogate()` (line 109): fits a `LogisticRegression` on demographic dummies — this is the actual working path.
- **The ledger's ground truth is correct**: SHAP is attempted but the default/working path is the demographic-dummy surrogate.

### ✅ Confirmed Discrepancies

| Ledger Claim | Verification | Status |
|:---|:---|:---:|
| [PROPOSAL_DEFENSE_GUIDE.md:202](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/docs/PROPOSAL_DEFENSE_GUIDE.md#L202) — "targeted SHAP explainability provides visual proxy evidence" | **CONFIRMED.** Unqualified SHAP as operative mechanism. | ✅ |
| [:230](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/docs/PROPOSAL_DEFENSE_GUIDE.md#L230) — "Fairlearn, AIF360, and SHAP are established, high-quality libraries" | **CONFIRMED.** Lists SHAP as co-equal foundational tool. | ✅ |
| [:287-288](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/docs/PROPOSAL_DEFENSE_GUIDE.md#L287-L288) Q12 — "We selected SHAP because..." | **CONFIRMED.** Frames SHAP as the chosen, operative method. | ✅ |
| [:290-291](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/docs/PROPOSAL_DEFENSE_GUIDE.md#L290-L291) Q13 — "Our explainability layer provides..." | **CONFIRMED.** Discusses SHAP as operative, no surrogate caveat. | ✅ |
| [:343](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/docs/PROPOSAL_DEFENSE_GUIDE.md#L343) Q25 — "conditional triggering of SHAP attribution" | **CONFIRMED.** Bare SHAP, no fallback/surrogate mentioned. | ✅ |
| [:386-387](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/docs/PROPOSAL_DEFENSE_GUIDE.md#L386-L387) Trap 3 — scripted defense lines | **CONFIRMED.** "Don't say" / "Do say" both use unqualified SHAP with no surrogate caveat. This is the literal verbatim script for the examiner. Highest risk item. | ✅ |
| [literatureReview.tex:14](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/report/src/chapters/literatureReview.tex#L14) — "requiring SHAP-based feature attribution on every flagged disparity" | **CONFIRMED.** Unqualified SHAP as mandatory mechanism. | ✅ |
| [literatureReview.tex:70](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/report/src/chapters/literatureReview.tex#L70) — "Motivated the SHAP-based explainability layer" | **CONFIRMED.** In summary table. | ✅ |
| [literatureReview.tex:99](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/report/src/chapters/literatureReview.tex#L99) — "SHAP-based diagnosis of the proxy-variable risk" | **CONFIRMED.** Closing paragraph, unqualified. | ✅ |
| [systemArchitectureAndMethodology.tex:37](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/report/src/chapters/systemArchitectureAndMethodology.tex#L37) — Key Libraries column lists "SHAP" for Explainability Layer | **CONFIRMED.** Table cell shows SHAP as the key library. | ✅ |

### 🔍 Missed by the Ledger

1. **[README.md:55](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/README.md#L55) — "attributes flagged disparities to input features via **SHAP**".**
   The ledger's Cluster B MED list mentions `README.md:32,59,205,213,220` but **not line 55**. This is a prominent bullet in the architecture section, right alongside the diagram, with bare unqualified "SHAP" as the sole mechanism. The ledger missed this specific line.

---

## Cluster C — Architecture/Structural Claims

### ✅ Confirmed Discrepancies

| Ledger Claim | Verification | Status |
|:---|:---|:---:|
| No YAML config loader | **CONFIRMED.** `grep` for `yaml`/`pyyaml`/`PyYAML` in `src/bias_aperture/` returns zero results. [cli.py](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/src/bias_aperture/cli.py) is pure `argparse`. | ✅ |
| `DirectInferenceAdapter` / `PredictionsFileAdapter` don't exist | **CONFIRMED.** Grep returns zero results. Actual classes are `InProcessInterface` (line 53) and `PredictionsFileInterface` (line 83) in [model_interface.py](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/src/bias_aperture/model_interface.py#L53). | ✅ |
| `TestMatrixBuilder` doesn't exist | **CONFIRMED.** Actual class: `DataIngestionPipeline` at [data_ingestion.py:167](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/src/bias_aperture/data_ingestion.py#L167). | ✅ |
| `ReportFactory` / `HTMLReportBuilder` don't exist | **CONFIRMED.** Actual class: `HTMLReportGenerator` at [generator.py:54](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/src/bias_aperture/report/generator.py#L54). | ✅ |
| `AuditReport` base class doesn't exist | **CONFIRMED.** Zero results across entire `src/bias_aperture/`. | ✅ |
| `AuditOrchestrator` doesn't exist | **CONFIRMED.** Only `CrossValidationOrchestrator` at [backends.py:965](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/src/bias_aperture/fairness/backends.py#L965). | ✅ |
| `FairnessBackend`→`AIF360Backend`/`FairlearnBackend` matches | **CONFIRMED.** Both exist exactly at [backends.py:457](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/src/bias_aperture/fairness/backends.py#L457) and [backends.py:46](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/src/bias_aperture/fairness/backends.py#L46), with parent `FairnessBackend` at [base.py:205](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/src/bias_aperture/fairness/base.py#L205). | ✅ |
| Duplicate `generator.py` is dead code | **CONFIRMED.** [report/templates/generator.py](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/src/bias_aperture/report/templates/generator.py) (8,985 bytes) has zero imports anywhere. [report/__init__.py](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/src/bias_aperture/report/__init__.py) imports from `bias_aperture.report.generator` (the top-level file). No `__init__.py` in `templates/`. Dead code confirmed. | ✅ |

### ⚠️ Nuance

- **[systemArchitectureAndMethodology.tex:8](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/report/src/chapters/systemArchitectureAndMethodology.tex#L8) — Design Principles prose.**
  The ledger's Cluster C table doesn't mention this line, but the fix ledger's Gate 1b flags it as out-of-scope prose. Confirmed: line 8 references `DirectInferenceAdapter`, `PredictionsFileAdapter` in the Design Principles prose section — **these are the same fictitious names**, just outside the table. The ledger itself missed this (it only scoped the table at lines 89–100).

### 🔍 Missed by the Ledger

1. **[README.md:16](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/README.md#L16) — "CLI + YAML **orchestration and configuration layer**".**
   The ledger flags the YAML config claim for the Mermaid diagram and the `.tex` chapter but **doesn't mention that the README prose (line 16) also says "CLI + YAML"**. Since the ledger says "README.md ... correctly show..." this is another README gap.

---

## Cluster D — WP Completion Claims

### ✅ Confirmed Discrepancies

| Ledger Claim | Verification | Status |
|:---|:---|:---:|
| WP3 PDF export — no code or dependency | **CONFIRMED.** Grep for `pdf`/`PDF`/`weasyprint`/`reportlab`/`pdfkit` in `src/bias_aperture/report/` returns zero results. [README.md:56](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/README.md#L56) still claims "HTML/PDF compliance reports". HTML-only in practice. | ✅ |
| WK4 report claims `bias-aperture audit` CLI with `--backend`, `--bca-bootstrap` | **CONFIRMED.** [WK4_report.md:39](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/dev-logs/weekly-reports/2026-08-27_WK4_report.md#L39) claims all three. Actual [cli.py](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/src/bias_aperture/cli.py): flat `ArgumentParser` (line 23–105), no `add_subparsers()`, no `audit` subcommand, no `--backend`, no `--bca-bootstrap`. Only `--explain` exists from the claimed set. | ✅ |
| WP5 "90%" — val-split only, not full dataset | **CONFIRMED.** [README.md:154](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/README.md#L154) shows `10,954/10,954` against val-split. 10,954 / 97,698 = 11.2% of full release. | ✅ |
| WP1–WP4 "Completed 100%" but CLAIM_LEDGER has 0 IMPLEMENTED/VALIDATED | **CONFIRMED.** Ledger observation matches — progression gap between "Completed" claims and claim-tier evidence. | ✅ |
| README.md:48 Mermaid shows "Compliance report (HTML / PDF)" | **CONFIRMED.** Stale — HTML only in practice. | ✅ |

---

## Critical Finding: Fix Ledger Error

> [!WARNING]
> The **DISCREPANCY_FIX_LEDGER.md** (Gate 2, line 402) states:
> ```
> FF node (:20) "97,698 images" — already correct, no fix.
> ```
> This is **factually wrong**. The actual [README.md:20](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/README.md#L20) reads:
> ```
> FF[("FairFace dataset<br/>108,501 images")]
> ```
> The fix ledger appears to have checked a different version of the README, or misread the line. **This means the README Mermaid diagram was excluded from all gate fixes based on a false premise.**

---

## Items Missed Entirely by Both Ledgers

| File:Line | Issue | Severity |
|:---|:---|:---|
| [README.md:20](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/README.md#L20) | Mermaid diagram: `108,501 images` (bare, no qualifier) | **HIGH** — first thing visible in README |
| [README.md:52](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/README.md#L52) | Architecture bullet: `FairFace (108,501 images)` | **HIGH** — README body |
| [README.md:16](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/README.md#L16) | "CLI + YAML orchestration" (no YAML exists) | **MED** — README body |
| [README.md:55](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/README.md#L55) | "attributes flagged disparities to input features via **SHAP**" (bare, no surrogate) | **MED** — README architecture bullets |
| [README.md:56](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/README.md#L56) | "HTML/PDF compliance reports" (no PDF implementation) | **MED** — README architecture bullets |
| [README.md:27](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/README.md#L27) | Mermaid: `ORCH["Orchestration & configuration layer<br/>CLI + YAML config"]` | **MED** — no YAML |
| [README.md:31](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/README.md#L31) | Mermaid: `EXP["Explainability layer<br/><b>SHAP</b>"]` | **MED** — bare SHAP in diagram |
| [README.md:48](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/README.md#L48) | Mermaid: `COMP["Compliance report (HTML / PDF)"]` | **MED** — no PDF |
| [systemArchitectureAndMethodology.tex:8](file:///c:/Users/Aaradhya/Downloads/_Organized/Fuse%20AI%20Fellowship/Capstone%20Project/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models/report/src/chapters/systemArchitectureAndMethodology.tex#L8) | Prose mentions `DirectInferenceAdapter`, `PredictionsFileAdapter` (fictitious) | **MED** — .tex prose outside table |

---

## Overall Assessment

> [!IMPORTANT]
> **The DISCREPANCY_LEDGER.MD is substantively correct in every claim I verified.** All HIGH-severity items are real and accurately described. The ground truth (97,698 released images, surrogate fallback as working path, fictitious class names in .tex table) is solid.

> [!WARNING]
> **The ledger has a significant blind spot around the README.md.** It asserts "All of `docs/`, `dev-logs/`, `README.md` … correctly show 97,698" — but the README actually contains **two bare 108,501 mentions** (lines 20 and 52), **three YAML-config references** (lines 16, 27), **two bare SHAP claims** (lines 31, 55), and **two HTML/PDF claims** (lines 48, 56). The README is arguably the single most examiner-visible file after the proposal itself, making these omissions higher-risk than they first appear.

> [!CAUTION]
> **The fix ledger (Gate 2) has a factual error**: it claims README.md:20 "already correct" when it still says `108,501 images`. Any fixes applied based on that gate will leave this stale claim untouched.
