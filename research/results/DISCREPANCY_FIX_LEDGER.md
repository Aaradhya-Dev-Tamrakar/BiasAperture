# BiasAperture — Gate 0–3 Merged Results

Parent: `task_2026-09-04_006` · Merged via `merge_results` (text-kind, gather-only, no auto-synthesis) · 2026-09-05
Repo: `Aaradhya-Dev-Tamrakar/BiasAperture @ main` · All 5 children read-only throughout — **nothing written/committed to the repo**. Every diff below is a draft pending your sign-off.

Conflicts: none. Status: 007, 008, 009, 010, 011 all `done`.

---

## Cross-cutting flags (surfaced across checkpoints, not previously in the ledger)

1. **Full-repo smoke test (007):** beyond the 6 required test cases, a full scan found **370 violations repo-wide** (24 bare-108,501 / 211 unqualified SHAP / 135 uncaveated UTKFace) — far more than the ledger's originally-scoped HIGH/MED item list.
2. **README.md:157 judgment call (007):** table row has both an unqualified SHAP mention (row label) and a qualified one (row end), >16 tokens apart. Script flags the label mention even though the ledger called the whole line "correct." Left as a flagged edge case, not auto-resolved.
3. **Prose leak outside Gate 1b's table scope (009):** `systemArchitectureAndMethodology.tex` line 8 (prose, not the table) still says `DirectInferenceAdapter`/`PredictionsFileAdapter` — the fictitious names the table fix removes. Not fixed, since task scope was table-only.
4. **Gate 2 ↔ ledger scope gap (010):** 3 legitimately-ledgered MED SHAP citations (`literatureReview.tex:14,70,99`) were never assigned to Gate 2's item list. Plus ~15 unledgered bare SHAP/UTKFace mentions in `docs/BiasAperture-AT.md` that the ledger never scoped for this file at all. **Recommendation from the task: open a Gate 2b.**
5. **architecture_highlevel.jpg undercount (011):** ledger's Cluster C names 2 stale elements in this image; direct inspection this pass found **5** (adds: bare-108,501 FairFace box, HTML/PDF compliance-report box — both previously uncounted for this specific image).
6. **generator.py duplication resolved (011):** `src/bias_aperture/report/generator.py` is **live** (imported by `report/__init__.py`, `cli.py`, tests). `src/bias_aperture/report/templates/generator.py` is **dead code** (zero imports, no `__init__.py`). Files are byte-identical except a trailing newline.

---

## Gate 0 — Anti-Drift Guard Script (`task_2026-09-04_007`, user6)

**Summary:** Drafted `scripts/check_stale_claims.py` (3 rules), `.pre-commit-config.yaml` diff, and `VERIFICATION_AND_SCRUTINY_GUIDE.md` §5 diff. Tested against repo @ commit `dda62d2`, read-only. 6/6 test matrix correct, zero false pos/neg.

### 1. `scripts/check_stale_claims.py` (full content)

```python
#!/usr/bin/env python3
"""
check_stale_claims.py — pre-commit guard against stale/overstated claims
in BiasAperture's .md/.tex documentation.

Guards three specific undersell/oversell drift patterns catalogued in
research/results/DISCREPANCY_LEDGER.md:

  1. Bare FairFace image counts (108,501 / 108501, including LaTeX
     `108{,}501` spacing groups) cited without a "released" /
     "pre-discard" / "pre-annotation" qualifier nearby. 108,501 is the
     pre-discard/pre-annotation total; 97,698 is the actual released
     count on disk (ledger §A).
  2. UTKFace mentioned without a nearby "cut" qualifier. "Secondary" is
     NOT an acceptable substitute — the ledger explicitly names
     "secondary benchmark" framing itself as the undersell pattern,
     since it implies UTKFace is still an active dataset rather than
     cut per Cut-List #2 (ledger §A).
  3. SHAP mentioned without a nearby "surrogate" / "deferred" /
     "fallback" qualifier. Current implementation attempts SHAP and
     falls back to demographic-dummy surrogate attribution on failure
     (ledger §B) — SHAP must not be described as the unqualified,
     operative mechanism.

Word-proximity ("~15 words") is measured within the same paragraph
(blank-line-delimited block), not the whole file, so an unrelated
qualifier many paragraphs away cannot silently clear a violation.

Exit status: 1 if any violation is found (blocks the commit), 0 if
clean. Intended to run as a `repo: local` pre-commit hook against
staged `.md`/`.tex` files (see .pre-commit-config.yaml).
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass

# "~15 words" per spec; 16 covers the tightest real known-clean case
# (specs/07-explainability.md:9, SHAP..."are deferred" spans a 16-token
# gap once list/adjective clauses are counted) without materially
# loosening the guard elsewhere.
WINDOW = 16

WORD_RE = re.compile(r"[\w'-]+")
PARA_SPLIT_RE = re.compile(r"\n[ \t]*\n")


@dataclass(frozen=True)
class Rule:
    name: str
    target: re.Pattern[str]
    qualifiers: tuple[re.Pattern[str], ...]
    message: str


RULES: tuple[Rule, ...] = (
    Rule(
        name="bare-108501",
        # matches 108,501 / 108501 / LaTeX 108{,}501 spacing groups
        target=re.compile(r"\b108[\s{},]*501\b"),
        qualifiers=(
            re.compile(r"\breleased\b", re.IGNORECASE),
            re.compile(r"\bpre-discard\b", re.IGNORECASE),
            re.compile(r"\bpre-annotation\b", re.IGNORECASE),
        ),
        message=(
            "bare 108,501/108501 without 'released'/'pre-discard'/"
            "'pre-annotation' within ~15 words — distinguish the "
            "pre-discard total from the 97,698 released/on-disk count "
            "(DISCREPANCY_LEDGER.md §A)"
        ),
    ),
    Rule(
        name="utkface-not-cut",
        target=re.compile(r"\bUTKFace\b", re.IGNORECASE),
        qualifiers=(re.compile(r"\bcut\b", re.IGNORECASE),),
        message=(
            "UTKFace without 'cut' within ~15 words — 'secondary' does "
            "not satisfy this guard, it IS the undersell pattern being "
            "caught (UTKFace was cut per Cut-List #2, "
            "DISCREPANCY_LEDGER.md §A)"
        ),
    ),
    Rule(
        name="shap-not-qualified",
        target=re.compile(r"\bSHAP\b"),
        qualifiers=(
            re.compile(r"\bsurrogate\b", re.IGNORECASE),
            re.compile(r"\bdeferred\b", re.IGNORECASE),
            re.compile(r"\bfallback\b", re.IGNORECASE),
        ),
        message=(
            "SHAP without 'surrogate'/'deferred'/'fallback' within "
            "~15 words — current implementation falls back to "
            "demographic-dummy surrogate attribution, not real SHAP "
            "(DISCREPANCY_LEDGER.md §B)"
        ),
    ),
)


def _paragraphs_with_offset(text: str) -> list[tuple[int, str]]:
    """Split text into (start_offset, paragraph_text) pairs on blank lines."""
    paras: list[tuple[int, str]] = []
    pos = 0
    for para in PARA_SPLIT_RE.split(text):
        idx = text.index(para, pos)
        paras.append((idx, para))
        pos = idx + len(para)
    return paras


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def check_text(text: str) -> list[tuple[int, str, str]]:
    """Return (line_number, rule_name, message) for each violation."""
    violations: list[tuple[int, str, str]] = []
    for para_start, para in _paragraphs_with_offset(text):
        tokens = list(WORD_RE.finditer(para))
        for rule in RULES:
            for m in rule.target.finditer(para):
                tok_idx = next(
                    (i for i, t in enumerate(tokens) if t.start() >= m.start()),
                    len(tokens) - 1,
                )
                lo = max(0, tok_idx - WINDOW)
                hi = min(len(tokens), tok_idx + WINDOW + 1)
                if hi <= lo:
                    window_text = para[m.start() : m.end()]
                else:
                    window_text = para[tokens[lo].start() : tokens[hi - 1].end()]
                if not any(q.search(window_text) for q in rule.qualifiers):
                    abs_offset = para_start + m.start()
                    violations.append(
                        (_line_number(text, abs_offset), rule.name, rule.message)
                    )
    return violations


def main(argv: list[str]) -> int:
    paths = [p for p in argv if p.endswith((".md", ".tex"))]
    exit_code = 0
    for path in paths:
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            print(f"check_stale_claims: cannot read {path}: {e}", file=sys.stderr)
            exit_code = 1
            continue
        for line_no, rule_name, message in check_text(text):
            print(f"{path}:{line_no}: [{rule_name}] {message}")
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
```

### 2. Diff — `.pre-commit-config.yaml`

```diff
--- .pre-commit-config.yaml
+++ .pre-commit-config.yaml (patched)
@@ -14,3 +14,11 @@
       - id: check-yaml
       - id: check-added-large-files
         args: ['--maxkb=1000']
+
+  - repo: local
+    hooks:
+      - id: check-stale-claims
+        name: Check for stale/overstated claims (dataset scale, UTKFace, SHAP)
+        entry: python scripts/check_stale_claims.py
+        language: system
+        files: \.(md|tex)$
```

Validated: parses as valid YAML (3 repos, local hook id=check-stale-claims confirmed).

### 3. Diff — `docs/research/VERIFICATION_AND_SCRUTINY_GUIDE.md` (§5)

```diff
--- docs/research/VERIFICATION_AND_SCRUTINY_GUIDE.md
+++ docs/research/VERIFICATION_AND_SCRUTINY_GUIDE.md (patched)
@@ -260,3 +260,4 @@
 - [ ] **Visual Check**: Does the HTML report render offline with 0 network calls?
 - [ ] **Test Check**: Are all tests passing with `uv run --extra dev pytest` and formatted with `ruff`?
 - [ ] **Sync Check**: Are all changes synchronized with conventional commits via `sync.ps1`?
+- [ ] **Claims Check**: Does `scripts/check_stale_claims.py` pass with zero violations on all staged `.md`/`.tex` files?
```

### 4. Test matrix (6/6 correct, zero false negatives/positives)

| #   | File:Line                              | Expected | Actual | Rule(s) triggered                                                                                  |
| --- | -------------------------------------- | -------- | ------ | -------------------------------------------------------------------------------------------------- |
| 1   | report/src/backmatter/back.tex:20      | FAIL     | FAIL   | bare-108501 (`108{,}501` LaTeX spacing group matched)                                              |
| 2   | report/src/frontmatter/abstract.tex:4  | FAIL     | FAIL   | utkface-not-cut + shap-not-qualified (whole abstract is one paragraph; no "cut" anywhere in it)    |
| 3   | docs/PROPOSAL_DEFENSE_GUIDE.md:386-388 | FAIL     | FAIL   | shap-not-qualified at :386 and :387 (line 388 is blank, no target there — expected)                |
| 4   | README.md:12                           | PASS     | PASS   | none (canonical caveat sentences both satisfy their rules)                                         |
| 5   | specs/07-explainability.md:9           | PASS     | PASS   | none — tightest real case: SHAP→"deferred" gap is 16 tokens; WINDOW calibrated to 16 to cover this |
| 6   | data/README.md:26                      | PASS     | PASS   | none (qualifier 3 tokens away)                                                                     |

**Iteration note:** first draft used WINDOW=15 (naive reading of "~15 words"); case 5 requires 16 tokens once list-of-nouns phrasing is tokenized, so WINDOW was bumped to 16 without loosening the other two SHAP cases. Re-ran full matrix: 6/6 correct.

**Full-repo smoke test** (127 md/tex files, beyond the required matrix): **370 total violations** (24 bare-108501, 211 shap-not-qualified, 135 utkface-not-cut), zero script crashes, zero false positives/negatives against any of DISCREPANCY_LEDGER.md's explicitly-cited HIGH lines or explicitly-cited "Clean" lines.

**Disambiguation flag:** README.md:157 has two SHAP mentions in one table row — an unqualified one in the row's label and a qualified one at the row's end, >16 tokens apart. Ledger calls line 157 "correct" as a whole line; this per-mention guard still flags the first occurrence. Judgment call, left as-is (per-mention proximity is the more defensible reading).

No files written/staged/committed at any point (`git status --porcelain` empty throughout).

---

## Gate 1 — HIGH-Severity Fixes (`task_2026-09-04_008`, user7)

**Summary:** 14 hunks across 6 files, all anchored to README.md:12's two canonical sentences. Verified via `git apply --check` against a scratch copy. Repo untouched. Count note: task spec said "12 HIGH items"; ledger's explicit file:line list resolves to 14 line-level locations — reconciles if "12" counts ledger rows/bullets rather than raw lines (report/main.pdf's HIGH mention excluded as a non-editable compiled artifact). All listed locations are covered.

```diff
--- a/report/src/backmatter/back.tex
+++ b/report/src/backmatter/back.tex
@@ -19,3 +19,3 @@
         Cloud GPU compute (NFR-004 target) & Google Colab, free-tier T4-class GPU for full-dataset evaluation runs & Free \\
-        Cloud GPU compute (contingency) & Google Colab Pro, if free-tier quota is exhausted during the full 108{,}501-image FairFace evaluation (NFR-004) & \$10/month \\
+        Cloud GPU compute (contingency) & Google Colab Pro, if free-tier quota is exhausted during the full 97{,}698-image FairFace evaluation (NFR-004) & \$10/month \\
         Cloud storage & Google Drive, dataset and checkpoint storage during development & Free (existing quota) \\

--- a/report/src/frontmatter/abstract.tex
+++ b/report/src/frontmatter/abstract.tex
@@ -3,3 +3,3 @@

-Automated facial analysis systems are widely deployed despite well-documented accuracy disparities across demographic subgroups, and independent, reproducible auditing of these systems remains rare in practice. This report proposes BiasAperture, a diagnostic and evaluative software platform that computes subgroup and intersectional fairness metrics for a third-party facial-analysis model and reports them in a standardised, regulator-legible format. The platform is organised into five cooperating modules covering data ingestion, model interfacing, fairness-metric computation, explainability, and report generation. Its analytical core computes four disparity metrics, demographic parity difference, equalized odds difference, equal opportunity difference, and disparate impact ratio, using AIF360 and Fairlearn as independent, cross-validating backends, with every reported disparity accompanied by a chi-squared significance test and a bootstrap confidence interval rather than a bare threshold. A SHAP-based explainability layer attributes flagged disparities to input features, distinguishing genuinely demographic effects from unrelated confounds. Findings are assembled into an exportable, Model-Cards- and Datasheets-structured report in which every metric is traced to its specific basis under Article~10 of the EU AI Act and the corresponding function of the NIST AI Risk Management Framework. The design is validated against the FairFace and UTKFace benchmark datasets, with a FairFace-trained convolutional-network baseline serving as the platform's own case study. BiasAperture is scoped strictly as diagnostic: it identifies and statistically characterises disparities but does not mitigate bias, retrain models, or generate synthetic demographic data.
+Automated facial analysis systems are widely deployed despite well-documented accuracy disparities across demographic subgroups, and independent, reproducible auditing of these systems remains rare in practice. This report proposes BiasAperture, a diagnostic and evaluative software platform that computes subgroup and intersectional fairness metrics for a third-party facial-analysis model and reports them in a standardised, regulator-legible format. The platform is organised into five cooperating modules covering data ingestion, model interfacing, fairness-metric computation, explainability, and report generation. Its analytical core computes four disparity metrics, demographic parity difference, equalized odds difference, equal opportunity difference, and disparate impact ratio, using AIF360 and Fairlearn as independent, cross-validating backends, with every reported disparity accompanied by a chi-squared significance test and a bootstrap confidence interval rather than a bare threshold. The current explainability implementation uses demographic-dummy surrogate attribution to attribute flagged disparities to input features, distinguishing genuinely demographic effects from unrelated confounds; richer spatial SHAP and ITA analysis remain deferred. Findings are assembled into an exportable, Model-Cards- and Datasheets-structured report in which every metric is traced to its specific basis under Article~10 of the EU AI Act and the corresponding function of the NIST AI Risk Management Framework. The current case study uses FairFace; UTKFace was profiled and cut from the implementation scope, with a FairFace-trained convolutional-network baseline serving as the platform's own case study. BiasAperture is scoped strictly as diagnostic: it identifies and statistically characterises disparities but does not mitigate bias, retrain models, or generate synthetic demographic data.


--- a/report/src/chapters/intro.tex
+++ b/report/src/chapters/intro.tex
@@ -25,3 +25,3 @@
     \item To generate a standardised, exportable fairness report, structurally informed by the Model Cards \cite{mitchell2019modelcards} and Datasheets for Datasets \cite{gebru2018datasheets} documentation conventions, that communicates subgroup performance disparities in a form accessible to both technical and non-technical stakeholders.
-    \item To validate the platform's design against publicly available, demographically annotated benchmark datasets, principally FairFace \cite{karkkainen2021fairface} and UTKFace.
+    \item To validate the platform's design against publicly available, demographically annotated benchmark datasets; the current case study uses FairFace \cite{karkkainen2021fairface}, while UTKFace was profiled and cut from the implementation scope.
     \item To map every computed fairness metric to a specific obligation under Article~10 and Annex~IV of the \gls{eu} \gls{ai} Act and to the corresponding function of the \gls{nist} \gls{ai} \gls{rmf}, so the platform's output is directly usable as compliance evidence.
@@ -32,3 +32,3 @@
 \subsection{Scope}
-BiasAperture is scoped as a strictly diagnostic and evaluative platform. In scope are: (i) demographic subgroup and intersectional performance evaluation of a supplied facial-analysis classifier; (ii) computation of four disparity metrics, \gls{dpd}, \gls{eod}, \gls{eop}, and \gls{dir}, backed by chi-squared significance testing and bootstrap confidence intervals; (iii) \gls{shap}-based explainability to help identify which visual features are associated with a detected disparity; and (iv) automated generation of a Model-Cards- and Datasheets-style \gls{html} fairness report, with each metric traceable to its \gls{eu} \gls{ai} Act and \gls{nist} \gls{ai} \gls{rmf} basis. The platform is validated against the FairFace \cite{karkkainen2021fairface} and UTKFace benchmark datasets, with a FairFace-trained \gls{cnn} baseline serving as the minimum case study.
+BiasAperture is scoped as a strictly diagnostic and evaluative platform. In scope are: (i) demographic subgroup and intersectional performance evaluation of a supplied facial-analysis classifier; (ii) computation of four disparity metrics, \gls{dpd}, \gls{eod}, \gls{eop}, and \gls{dir}, backed by chi-squared significance testing and bootstrap confidence intervals; (iii) explainability to help identify which visual features are associated with a detected disparity --- the current explainability implementation uses demographic-dummy surrogate attribution, and richer spatial \gls{shap} and ITA analysis remain deferred; and (iv) automated generation of a Model-Cards- and Datasheets-style \gls{html} fairness report, with each metric traceable to its \gls{eu} \gls{ai} Act and \gls{nist} \gls{ai} \gls{rmf} basis. The current case study uses FairFace \cite{karkkainen2021fairface}; UTKFace was profiled and cut from the implementation scope, with a FairFace-trained \gls{cnn} baseline serving as the minimum case study.

@@ -35,2 +35,2 @@
 \subsection{Limitations}
-Consistent with these boundaries, BiasAperture does not attempt to mitigate bias, retrain or fine-tune models, or generate synthetic demographic data; its function is strictly diagnostic, not corrective. It reports where disparities exist and their statistical strength, but it does not prescribe or apply any remediation. Its findings are only as reliable as the label quality of the benchmark dataset supplied, a known limitation for UTKFace's model-estimated age labels in particular, and every reported subgroup below a minimum sample size of \gls{symb:n} \(\geq 30\) is flagged as statistically insufficient rather than scored. Full-dataset evaluation is bounded by a documented runtime target rather than guaranteed instantaneous; and if project timeline pressure requires descoping, the platform's own cut-list (\cref{chap:methodology}) defines, in order, which secondary capabilities are dropped first, while the diagnostic core, ingestion, one model interface, the fairness engine, one report format, and the scope-boundary statement itself, is never cut.
\ No newline at end of file
+Consistent with these boundaries, BiasAperture does not attempt to mitigate bias, retrain or fine-tune models, or generate synthetic demographic data; its function is strictly diagnostic, not corrective. It reports where disparities exist and their statistical strength, but it does not prescribe or apply any remediation. Its findings are only as reliable as the label quality of the benchmark dataset supplied; the current case study uses FairFace, since UTKFace, whose model-estimated age labels were a known limitation, was profiled and cut from the implementation scope, and every reported subgroup below a minimum sample size of \gls{symb:n} \(\geq 30\) is flagged as statistically insufficient rather than scored. Full-dataset evaluation is bounded by a documented runtime target rather than guaranteed instantaneous; and if project timeline pressure requires descoping, the platform's own cut-list (\cref{chap:methodology}) defines, in order, which secondary capabilities are dropped first, while the diagnostic core, ingestion, one model interface, the fairness engine, one report format, and the scope-boundary statement itself, is never cut.
\ No newline at end of file

--- a/report/src/chapters/systemArchitectureAndMethodology.tex
+++ b/report/src/chapters/systemArchitectureAndMethodology.tex
@@ -45,3 +45,3 @@
 \subsection{Data Ingestion and Preprocessing Module}
-This module loads a selected benchmark dataset, initially FairFace and UTKFace, or a compatible custom dataset, validates image integrity, standardises image resolution and colour space via OpenCV, and aligns demographic annotation fields (race or ethnicity, perceived gender, age group) into the locked internal schema (\cref{sec:schedule}). It rejects corrupted or unreadable files and enforces that every image carries a complete, correctly typed set of demographic labels before any downstream computation proceeds.
+This module loads a selected benchmark dataset --- with the current case study using FairFace, since UTKFace was profiled and cut from the implementation scope --- or a compatible custom dataset, validates image integrity, standardises image resolution and colour space via OpenCV, and aligns demographic annotation fields (race or ethnicity, perceived gender, age group) into the locked internal schema (\cref{sec:schedule}). It rejects corrupted or unreadable files and enforces that every image carries a complete, correctly typed set of demographic labels before any downstream computation proceeds.

@@ -74,3 +74,3 @@

-The workflow begins with the auditor configuring the audit: specifying the benchmark or custom dataset, the target model, or a predictions file, and the metrics to compute. The system then branches on the model access mode. If a model object is supplied, predictions are obtained by direct in-process inference against the PyTorch or TensorFlow model; otherwise, predictions are obtained by batch ingestion of a precomputed CSV or JSON file. Both branches converge on a common path, in which the selected dataset, FairFace or UTKFace, is ingested and validated, and predictions are generated over the resulting test matrix.
+The workflow begins with the auditor configuring the audit: specifying the benchmark or custom dataset, the target model, or a predictions file, and the metrics to compute. The system then branches on the model access mode. If a model object is supplied, predictions are obtained by direct in-process inference against the PyTorch or TensorFlow model; otherwise, predictions are obtained by batch ingestion of a precomputed CSV or JSON file. Both branches converge on a common path, in which the selected dataset --- the current case study uses FairFace, since UTKFace was profiled and cut from the implementation scope --- is ingested and validated, and predictions are generated over the resulting test matrix.


--- a/report/src/chapters/conclusion.tex
+++ b/report/src/chapters/conclusion.tex
@@ -5,3 +5,3 @@

-This report has proposed BiasAperture, a diagnostic and evaluative software platform for auditing demographic accuracy disparities in third-party facial analysis models, and specified it in enough detail to be built against by a two-person team over an eight-week schedule. \Cref{chap:litreview} showed that a mature fairness-metrics and mitigation-techniques literature exists without a corresponding reusable auditing artefact, at precisely the moment the \gls{eu} \gls{ai} Act's Article~10 obligations make that gap a compliance question rather than only an academic one. \Cref{chap:requirements,chap:methodology} then specified how the platform closes it, against each of \cref{chap:intro}'s five specific objectives in turn: a modular architecture built around FR-001 and FR-002 satisfies the first; AIF360 and Fairlearn as independent, cross-validating backends for the four Core~Four metrics, with chi-squared and bootstrap significance testing, satisfy the second; a report structured against the Model Cards and Datasheets conventions surveyed in \cref{chap:litreview} satisfies the third; validation against FairFace and UTKFace, with a FairFace-trained \gls{cnn} baseline as the minimum case study, satisfies the fourth; and the Article~10 and \gls{nist} \gls{ai} \gls{rmf} mapping detailed in \cref{sec:regmapping} satisfies the fifth.
+This report has proposed BiasAperture, a diagnostic and evaluative software platform for auditing demographic accuracy disparities in third-party facial analysis models, and specified it in enough detail to be built against by a two-person team over an eight-week schedule. \Cref{chap:litreview} showed that a mature fairness-metrics and mitigation-techniques literature exists without a corresponding reusable auditing artefact, at precisely the moment the \gls{eu} \gls{ai} Act's Article~10 obligations make that gap a compliance question rather than only an academic one. \Cref{chap:requirements,chap:methodology} then specified how the platform closes it, against each of \cref{chap:intro}'s five specific objectives in turn: a modular architecture built around FR-001 and FR-002 satisfies the first; AIF360 and Fairlearn as independent, cross-validating backends for the four Core~Four metrics, with chi-squared and bootstrap significance testing, satisfy the second; a report structured against the Model Cards and Datasheets conventions surveyed in \cref{chap:litreview} satisfies the third; validation against the current case study, which uses FairFace since UTKFace was profiled and cut from the implementation scope, with a FairFace-trained \gls{cnn} baseline as the minimum case study, satisfies the fourth; and the Article~10 and \gls{nist} \gls{ai} \gls{rmf} mapping detailed in \cref{sec:regmapping} satisfies the fifth.


--- a/docs/PROPOSAL_DEFENSE_GUIDE.md
+++ b/docs/PROPOSAL_DEFENSE_GUIDE.md
@@ -201,3 +201,3 @@

-> "BiasAperture is architected as a modular diagnostic pipeline. Demographic data and model outputs enter through the ingestion module and are validated against our locked schema. Predictions are obtained either from a local PyTorch model or batch-ingested from a standard CSV or JSON predictions file. The core engine calculates four disparity metrics using heterogeneous implementation cross-checking across Fairlearn and AIF360. Where statistically significant disparities occur, targeted SHAP explainability provides visual proxy evidence. Finally, a self-contained offline HTML report is compiled using Model Cards and Datasheets conventions."
+> "BiasAperture is architected as a modular diagnostic pipeline. Demographic data and model outputs enter through the ingestion module and are validated against our locked schema. Predictions are obtained either from a local PyTorch model or batch-ingested from a standard CSV or JSON predictions file. The core engine calculates four disparity metrics using heterogeneous implementation cross-checking across Fairlearn and AIF360. Where statistically significant disparities occur, the current explainability implementation, using demographic-dummy surrogate attribution, provides visual proxy evidence; richer spatial SHAP and ITA analysis remain deferred. Finally, a self-contained offline HTML report is compiled using Model Cards and Datasheets conventions."

@@ -229,3 +229,3 @@
 1. **Acknowledge the Foundational Tools:**
-   > "Fairlearn, AIF360, and SHAP are established, high-quality libraries. We do not claim to have invented new fairness metrics or new statistical tests."
+   > "Fairlearn and AIF360 are established, high-quality libraries, and the current explainability implementation uses demographic-dummy surrogate attribution, with richer spatial SHAP and ITA analysis remaining deferred. We do not claim to have invented new fairness metrics or new statistical tests."

@@ -287,3 +287,3 @@
-**Q12: "Why choose SHAP over other explainability methods like LIME?"**
-> "We selected SHAP because it provides a theoretically grounded additive attribution framework and supports the black-box explanation path required by our prediction-file interface. The choice is architectural, not a claim that SHAP produces causal explanations."
+**Q12: "Why choose SHAP over other explainability methods like LIME?"**
+> "The current explainability implementation uses demographic-dummy surrogate attribution; richer spatial SHAP and ITA analysis remain deferred. We selected SHAP because it provides a theoretically grounded additive attribution framework and supports the black-box explanation path required by our prediction-file interface. The choice is architectural, not a claim that SHAP produces causal explanations."

@@ -290,3 +290,3 @@
-**Q13: "Can SHAP feature attributions prove that a model is biased due to facial features?"**
-> "No, and we explicitly document this limitation. In accordance with Bilodeau et al. (2022) impossibility theorems, additive feature attribution methods cannot guarantee distinguishing spurious correlations from causal features in neural networks. Our explainability layer provides exploratory proxy evidence, not causal proof."
+**Q13: "Can SHAP feature attributions prove that a model is biased due to facial features?"**
+> "No, and we explicitly document this limitation. In accordance with Bilodeau et al. (2022) impossibility theorems, additive feature attribution methods cannot guarantee distinguishing spurious correlations from causal features in neural networks. The current explainability implementation uses demographic-dummy surrogate attribution and provides exploratory proxy evidence, not causal proof; richer spatial SHAP and ITA analysis remain deferred."

@@ -342,3 +342,3 @@
 **Q25: "What is the primary technical risk in the upcoming implementation phase?"**
-> "The primary technical risk is handling computational runtime for full-dataset bootstrap resampling and explainability. We mitigate this through vectorized bootstrap implementations, stratified development subsets ($n=5,000$), and conditional triggering of SHAP attribution only on flagged disparities."
+> "The primary technical risk is handling computational runtime for full-dataset bootstrap resampling and explainability. We mitigate this through vectorized bootstrap implementations, stratified development subsets ($n=5,000$), and conditional triggering of attribution only on flagged disparities; the current explainability implementation uses demographic-dummy surrogate attribution, with richer spatial SHAP and ITA analysis remaining deferred."

@@ -386,3 +386,3 @@
-- **Don't say:** *"SHAP explains why the model is biased."*
-- **Do say:** *"SHAP provides feature attributions that highlight visual proxy correlations associated with detected disparities, subject to known non-causal theoretical bounds."*
+- **Don't say:** *"SHAP explains why the model is biased."*
+- **Do say:** *"The current explainability implementation uses demographic-dummy surrogate attribution, which provides feature attributions that highlight visual proxy correlations associated with detected disparities, subject to known non-causal theoretical bounds; richer spatial SHAP and ITA analysis remain deferred."*
```

---

## Gate 1b — Design Patterns Table Fix (`task_2026-09-04_009`, user8)

**Summary:** Diff drafted (not applied), grep-verified against a fresh clone.

**Fresh grep verification** (`grep -rn '^class ' src/bias_aperture/`):

```
src/bias_aperture/data_ingestion.py:167:class DataIngestionPipeline:
src/bias_aperture/model_interface.py:53:class InProcessInterface(ModelInterface):
src/bias_aperture/model_interface.py:83:class PredictionsFileInterface(ModelInterface):
src/bias_aperture/report/templates/generator.py:54:class HTMLReportGenerator:
src/bias_aperture/report/generator.py:54:class HTMLReportGenerator:
src/bias_aperture/fairness/backends.py:965:class CrossValidationOrchestrator:
```

No `AuditOrchestrator`, `TestMatrixBuilder`, `ReportFactory`, `HTMLReportBuilder`, `AuditReport`, `DirectInferenceAdapter`, or `PredictionsFileAdapter` found anywhere under `src/bias_aperture/`.

All 5 replacement classes confirmed to exist exactly as named in DISCREPANCY_LEDGER.md cluster C. `AuditReport` has no equivalent — row dropped per spec.

```diff
--- a/report/src/chapters/systemArchitectureAndMethodology.tex
+++ b/report/src/chapters/systemArchitectureAndMethodology.tex
@@ -90,12 +90,11 @@
         \toprule
         \textbf{Pattern} & \textbf{Module} & \textbf{Structure} & \textbf{Rationale} \\
         \midrule
-        Adapter & Model Interface & {\ttfamily\footnotesize Model\-Interface} $\to$ {\ttfamily\scriptsize Direct\-Inference\-Adapter} / {\ttfamily\scriptsize Predictions\-File\-Adapter} & Cutting direct inference (\cref{sec:cutlist}, item 4) means simply not instantiating one adapter; downstream code is unchanged \\
+        Adapter & Model Interface & {\ttfamily\footnotesize Model\-Interface} $\to$ {\ttfamily\scriptsize In\-Process\-Interface} / {\ttfamily\scriptsize Predictions\-File\-Interface} & Cutting direct inference (\cref{sec:cutlist}, item 4) means simply not instantiating one interface; downstream code is unchanged \\
         Strategy & Fairness Metrics Engine & {\ttfamily\footnotesize Fairness\-Backend} $\to$ {\ttfamily\footnotesize AIF360Backend} / {\ttfamily\footnotesize Fairlearn\-Backend} & Cutting AIF360 (\cref{sec:cutlist}, item 5) is a backend swap, not a rewrite; the four metrics are interchangeable strategies \\
-        Builder & Data Ingestion & {\ttfamily\footnotesize Test\-Matrix\-Builder} & Matches the multi-step curation (acquisition, integrity check, schema alignment) the module performs \\
-        Factory & Report Generation & {\ttfamily\footnotesize Report\-Factory} $\to$ {\ttfamily\footnotesize HTMLReport\-Builder} & Keeps the \gls{html} report path untouched regardless of which export formats are in scope \\
-        Template Method & Report Generation & {\ttfamily\footnotesize Audit\-Report} base class & Fixes the Model Cards / Datasheets section skeleton while allowing subclasses to fill format-specific hooks \\
-        Facade & Orchestration & {\ttfamily\footnotesize Audit\-Orchestrator} & Hides the ingestion $\to$ interface $\to$ engine $\to$ report sequence behind one call \\
+        Builder & Data Ingestion & {\ttfamily\footnotesize Data\-Ingestion\-Pipeline} & Matches the multi-step curation (acquisition, integrity check, schema alignment) the module performs \\
+        Factory & Report Generation & {\ttfamily\footnotesize HTMLReport\-Generator} & Keeps the \gls{html} report path untouched regardless of which export formats are in scope \\
+        Facade & Orchestration & {\ttfamily\footnotesize Cross\-Validation\-Orchestrator} & Hides the ingestion $\to$ interface $\to$ engine $\to$ report sequence behind one call \\
         \bottomrule
     \end{tabular}
 \end{table}
```

**Verification:** brace balance on patched rows = 12/12 (matched). Zero fictitious names remain in table. No other `.tex` file references `AuditReport` or `AuditOrchestrator` (grep clean, no dangling `\ref`/`\label` dependents). Row count: 6→5 (Template Method/AuditReport row dropped, no replacement).

**Flag (out of scope for this task):** prose in the same file (line 8, outside `\label{sec:patterns}` table) also names `DirectInferenceAdapter`/`PredictionsFileAdapter` — table-only per task spec, needs a follow-up gate.

File not modified on disk; read-only clone throughout.

---

## Gate 2 — MED-Severity Fixes (`task_2026-09-04_010`, user9)

**Summary:** README diagram assessed (1 text fix + 1 structural item flagged for Gate 3); `track_34` read fully, confirmed qualifier-swap-only; cross-check grep found zero misses within the assigned 15 items but surfaced a ledger-vs-task-spec scope gap. **Recommends opening a Gate 2b.**

### README.md diagram bullets

Mermaid block at README.md:18–54.

- `FF` node (:20) "97,698 images" — already correct, no fix.
- `UTK` node (:21) "[CUT] profiled only" + dashed `classDef cut` styling — diagram already visually differentiates UTKFace as cut. No fix.
- `EXP` node (:32) "Explainability layer<br/><b>SHAP</b>" — bare SHAP, text-only fix sufficient.

```diff
- EXP["Explainability layer<br/><b>SHAP</b>"]
+ EXP["Explainability layer<br/><b>Surrogate Attribution</b><br/>(SHAP deferred)"]
```

**Structural flag for Gate 3 (not fixed here):** `ORCH` node (:28) "Orchestration & configuration layer<br/>CLI + YAML config" — ledger cluster C confirms no YAML config loader exists anywhere in `src/` (zero hits, no pyyaml dependency, `cli.py` is pure argparse). This depicts a nonexistent architectural component — recommend bundling with the `architecture_highlevel.jpg` regen decision already in Gate 3.

### track_34 (read in full)

File is a Phase-2 research-track PROMPT template (Stream J, Track 34), not a status document. Confirmed the qualifier-swap alone resolves it — no deeper rewrite needed.

```diff
- Current validated runtime target (BiasAperture-AT.md §9): full FairFace (108,501 img) <=4hr GPU; stratified dev subset (n=5,000) <=30min CPU. Actual verified run processed 10,954 validation images successfully.
+ Current validated runtime target (BiasAperture-AT.md §9): full FairFace (97,698 released images; 108,501 pre-discard) <=4hr GPU; stratified dev subset (n=5,000) <=30min CPU. Actual verified run processed 10,954 validation images successfully.
```

### Cross-check grep results (all 15-item files)

**108,501/108501:** No new hits beyond the 5 already diffed. README's diagram FF node confirmed clean. Zero misses.

**UTKFace without "cut":** New hits found outside the original 15-item list — flagged, not fixed:

- `literatureReview.tex:18` — Datasheets discussion of provenance, historical/methodological, not a status claim.
- `requirements.tex:11` (FR-001) — ledger itself declines to flag this ("only defensible as schema-capability language").
- `systemArchitectureAndMethodology.tex:46,75` — ledgered, but as Gate 1 HIGH items, not Gate 2's.
- `systemArchitectureAndMethodology.tex:188` — cut-list table itself, correctly says "keep FairFace only."
- `README.md:80,155,192` — consistent with cut status.
- `HIGH_LEVEL_SYNTHESIS.md:179` — "Formally dropped" — correct.
- **`docs/BiasAperture-AT.md` (+dup) `:76,232,278,329,379,441`** — bare "FairFace + UTKFace" framing in the historical decision-log. **Not ledgered anywhere for this file beyond the three 108,501 lines** — a genuine gap in the ledger's own scope for this file.

**SHAP without surrogate/deferred/fallback:** New hits, all outside this task's item list:

- **`literatureReview.tex:14,70,99`** — **these ARE ledgered** (ledger section B lists them) but were **not included in Gate 2's assigned item list** for this file (task_010 was only assigned `:18,20,88`, which are the UTKFace/dataset items). **Real miss between the ledger and the task spec.**
- `requirements.tex:11` — covered above.
- **`docs/BiasAperture-AT.md` (+dup)** — 14 additional bare-SHAP hits (`:36,62,145,228,291,310,317,327,329,331,356,382,439,441,443`) — not ledgered at all for this file.
- `README.md:194` — bare SHAP in an open question, not in ledger's list for this file.
- `dev-logs/weekly-reports/2026-08-27_WK4_report.md:107` — not in ledger's `:14,20,60` list for this file.
- `stream_b_report_generation.md:7,12,47` — not in ledger's `:27` citation for this file.

**Summary:** No misses within the originally-assigned 15 items. Cross-check surfaced a separate, real gap: the ledger's own MED coverage appears broader than what task_010 was assigned — notably `literatureReview.tex:14,70,99` and `docs/BiasAperture-AT.md`'s many uncaveated mentions never ledgered at all. **Recommend deciding whether to open a Gate 2b for these before Gate 3.**

No edits, commits, or sync.ps1 invocations made — read-only throughout.

---

## Gate 3 — Decision-Support Brief (`task_2026-09-04_011`, user10)

**Summary:** Items 1–5 researched (item 6 correctly skipped per spec — Aaradhya sign-off only, no research needed). Read-only, no edits. Cross-verified against and extends the prior DISCREPANCY_LEDGER.md with independent firsthand checks; net-new deltas found in items 3 and 4. **Facts only — no recommendations**, per task constraint.

### Item 1 — WP3 PDF-export claim + WP5 CLI flag claim

`cli.py::build_parser()` (full file read): single flat `argparse.ArgumentParser`, no `add_subparsers()`. 10 flags total: `--predictions-file/-i`, `--true-label-col`, `--predicted-label-col`, `--race-col`, `--gender-col`, `--age-col`, `--protected-attr/-a`, `--output-report/-o`, `--model-name`, `--dataset-name`, `--explain`. **No `audit` subcommand. No `--backend`. No `--bca-bootstrap`.**

Claim source: `dev-logs/weekly-reports/2026-08-27_WK4_report.md:39` — claims a `bias-aperture audit` CLI with `--explain`, `--backend`, `--bca-bootstrap`, marked "Completed." Only `--explain` exists.

WP3 PDF claim (`README.md:60`): report module "renders...HTML/PDF compliance reports." Verified: zero PDF-related imports anywhere in `src/bias_aperture/report/*.py`, zero PDF dependency in `pyproject.toml`. **HTML-only in practice.**

**Effort estimate:**

| Sub-claim          | Current state                                                               | Effort to ADD                                                                                                         | Effort to CORRECT claim only     |
| ------------------ | --------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| `audit` subcommand | Flat parser, no subparsers                                                  | Moderate: restructure `build_parser()`, move all 10 flags under `audit`, update `main()`, update 2 existing CLI tests | Trivial: reword one dev-log line |
| `--backend`        | `CrossValidationOrchestrator.run()` has no backend param — always runs both | Non-trivial + touches a locked invariant (CONTEXT.md's dual-backend design). Needs a scope decision first             | Trivial                          |
| `--bca-bootstrap`  | `statistics.py:136` bootstrap fn already takes `n_resamples` param          | Small-to-moderate: capability exists at function level, needs CLI plumbing threaded through                           | Trivial                          |

### Item 2 — WP5 "90%" claim

10,954 / 97,698 = **11.21%** (computed).

Ground truth: 97,698 = 86,744 train + 10,954 val (confirmed via official FairFace CSV line counts). So 10,954 IS the complete validation split, not a partial run.

`README.md:158` already frames the processed-image figure as `10,954/10,954` (against the val-split denominator = 100%), not against 97,698. The "90%" attaches to **WP5 workstream/milestone completion** (report review + main.pdf finalization outstanding) — not image-processing coverage. "90% workstream" and "11.2% of full release" measure different things and aren't in direct conflict on their face.

Separate, more precise point: the project's own CLAIM_LEDGER.md tier system reserves "VALIDATED" for a full 97,698-image run; the actual completed run is val-split-only. No claim can reach "VALIDATED" tier yet regardless of how "90%" is read.

### Item 3 — architecture_highlevel.jpg stale elements

Image directly viewed. **Full stale-element list, 5 total** (ledger's Cluster C only names 2):

**Per ledger Cluster C (2 items):**

1. "Orchestration & configuration layer: CLI + YAML config" box — verified stale (zero yaml dependency, zero `import yaml`, `cli.py` is pure argparse).
2. UTKFace box: "20,000+ images," solid arrow, equal visual weight to FairFace — verified stale against README's own Mermaid, which already correctly dashes/labels it `[CUT]`.

**Filed under Cluster B, flagged since task scoped "cluster C":** 3. "Explainability layer: SHAP" box, no caveat — actual behavior falls back to `explain_surrogate()`.

**Not filed under any cluster — found via direct image inspection this pass (net-new, 2 items):** 4. "FairFace dataset — 108,501 images" box. Stale per Cluster A/CLAIM_LEDGER R-002 (released count is 97,698). Cluster A's own table doesn't list this image among its hits — genuinely uncounted occurrence. 5. "Compliance report (HTML/PDF)" box. Stale per same evidence as Item 1. Not tied to this image anywhere in the existing ledger.

### Item 4 — report/generator.py vs report/templates/generator.py

Path note: no `generator.py` exists under the top-level LaTeX `report/` dir — this is `src/bias_aperture/report/generator.py` vs `src/bias_aperture/report/templates/generator.py`.

**Diff:** byte-identical except one trailing-newline difference (223 vs 224 lines).

**Import resolution:**

- `src/bias_aperture/report/__init__.py` imports from `bias_aperture.report.generator` (top-level file).
- `cli.py:20` imports `HTMLReportGenerator`, `ReportContext` from `bias_aperture.report` → resolves to top-level file.
- `src/tests/test_report_generator.py:9` imports directly from the top-level file.
- `src/bias_aperture/report/templates/generator.py`: **zero references anywhere**, case-insensitive grep confirmed. No `__init__.py` in `templates/`, so it isn't even set up as an importable subpackage.
- `templates/`'s actual role: holds `report.html.j2`, the Jinja2 template the live generator.py loads.

**Verdict: `src/bias_aperture/report/templates/generator.py` is dead code. `src/bias_aperture/report/generator.py` is live.** This resolves an item the ledger flagged as "Bonus (out of scope)... not resolved."

### Item 5 — fellowship PDFs: source-file check + §13 precedent

**Source search (repo-wide):**

- `docs/fellowship/` has 5 PDFs; only `BiasAperture_User_Requirement_Document.pdf` and `BiasAperture_Literature_Review.pdf` are in question.
- No `.tex`/`.md` source anywhere for either.
- No `.docx`/`.odt` anywhere in the repo.
- No `docs/fellowship/src/` or similar staging dir.
- No Google Docs/LibreOffice signatures in either PDF's byte stream.

**New this pass:** `pdfinfo` shows Creator/Producer = "Microsoft® Word for Microsoft 365" for both (URD created 2026-08-13; Lit Review created 2026-08-18). A `.docx` source almost certainly existed at authoring time but was never committed to this repo — more precise than "no source ever existed": it's **"no source is trackable in-repo."**

**§13 precedent** (docs/BiasAperture-AT.md, "Outstanding Action Items"): concerns `feasibility_study.pdf`, another already-submitted PDF-only artifact with no live source, which had two known content gaps. Resolution pattern actually followed (v3→v5, still open as of latest entry):

1. Both gaps logged as explicit "Outstanding Action Item" table rows rather than the PDF being hand-edited/reconstructed.
2. Where the same content need arose in a document WITH a live compilable source, the fix was applied there instead (e.g. FR-005 added to requirements.tex) — the log explicitly notes this resolves the requirement in one document while `feasibility_study.pdf` itself remains separately outstanding.
3. The PDF itself was never directly patched across 3+ tracked revisions — the gap is carried forward as a known, transparent, unresolved item.

Reported as-found per the task's ask; no application of this pattern proposed for the two new PDFs.

**Item 6:** skipped per spec (Aaradhya sign-off item, no research needed).

---

## Open decision points (yours, not resolved here)

- Open a **Gate 2b** for the ledger-vs-task-spec SHAP citation gap (`literatureReview.tex:14,70,99`) and the ~15 unledgered `docs/BiasAperture-AT.md` mentions?
- Fix the leftover fictitious-class prose at `systemArchitectureAndMethodology.tex:8` (outside Gate 1b's table-only scope)?
- `architecture_highlevel.jpg` regen — now 5 confirmed stale elements, not 2.
- Delete `src/bias_aperture/report/templates/generator.py` (confirmed dead code) — Gate 3 said flag-only, no edits made.
- README.md:157's SHAP-mention edge case in the anti-drift script — accept the flag as designed, or loosen the rule?
- Gate 3 items 1, 2, 5 still need your actual sign-off (this brief is facts only, no recommendation made).
