# BiasAperture — Discrepancy Ledger

Repo: Aaradhya-Dev-Tamrakar/BiasAperture @ main, commit `0c4fb0538fd67b1a10a6626a5dbd07c0da90a62e` (2026-09-04). Read-only audit, 4 parallel subtasks, merged via orchestrator `task_2026-09-04_001`. EU AI Act Art.10 deadline framing explicitly excluded (separate track). No files edited by any subtask.

Severity key: **HIGH** = examiner-facing / defense-script risk. **MED** = doc-only inconsistency. **LOW** = historical/changelog record, low defense risk.

---

## A — Dataset Scale (108,501 vs 97,698) & UTKFace Status

Ground truth: 97,698 released images (86,744 train + 10,954 val). 108,501 = pre-discard total, not released count. UTKFace = CUT (Cut-List #2), profiled only, never ingested/scored. No "20,000+" hits anywhere.

### Stale dataset-scale figures (still show unqualified 108,501)
| File:Line | Current Text | Severity |
|---|---|---|
| `report/src/backmatter/back.tex:20` | "full 108,501-image FairFace evaluation (NFR-004)" | **HIGH** — in submitted proposal, contradicts requirements.tex:28 in same document |
| `report/main.pdf` p.36 (compiled) | mirrors above | **HIGH** |
| `docs/BiasAperture-AT.md:71,97,239` (+ dup `research/context feed/BiasAperture-AT.md`) | 3 lines, uncorrected historical export | MED |
| `research/research tracks/CONTEXT.md:8` | uncorrected copy (corrected version exists at `research/context feed/CONTEXT.md:8`) | LOW |
| `research/research tracks/track_02, track_03, track_07` | pre-verification track prompts | LOW |
| `research/research tracks/track_34...:13` | self-contradicts in same line (cites 108,501 as "current validated" while confirming only 10,954 actually ran) | MED |
| `research/results/stream_b_report_generation.md:27` | draft report copy, footnoted but unswapped | LOW |

All of `docs/`, `dev-logs/`, `README.md`, `CLAUDE.md`, `requirements.tex`, `CLAIM_LEDGER.md` correctly show 97,698. Root cause: `report/main.tex` backmatter table never synced with requirements.tex's already-correct NFR-004 figure.

### Stale UTKFace status (still framed as active/co-validated)
| File:Line | Current Text | Severity |
|---|---|---|
| `report/src/frontmatter/abstract.tex:4` | "validated against the FairFace and UTKFace benchmark datasets" | **HIGH** — proposal abstract |
| `report/src/chapters/intro.tex:26,33,36` | dual-dataset framing | **HIGH** |
| `report/src/chapters/systemArchitectureAndMethodology.tex:46,75` | "initially FairFace and UTKFace"; "selected dataset...is ingested" | **HIGH** — same file's own cut-list table (line 188) correctly shows UTKFace cut: internal inconsistency |
| `report/src/chapters/literatureReview.tex:18,20,88` | "secondary benchmark" framing (undersells full exclusion) | MED |
| `report/src/chapters/conclusion.tex:6` | lists UTKFace validation as satisfying an objective | **HIGH** |
| `report/main.pdf` | inherits all of the above | **HIGH** |
| `context-summary/high-level-summary.md:51` | "includes support for...FairFace and UTKFace...validation workflows" — omits cut status | MED |
| `dev-logs/weekly-reports/2026-08-27_WK4_report.md:14,20,60` | "secondary validation testbed" — imprecise, undersells full cut | LOW |

`requirements.tex:11` (FR-001) — ambiguous, only defensible as schema-capability language, not implementation-status.

All CLAUDE.md, README.md, specs/, docs/research/* correctly show UTKFace [CUT]/profiled-only.

---

## B — Explainability: SHAP vs. Actual Demographic-Dummy Surrogate

Ground truth: `explainability.py` attempts SHAP, falls back to `explain_surrogate()` (demographic-dummy linear Shapley) on failure. README.md:12 has the correct caveat.

### HIGH severity (examiner-facing script, zero caveat)
All in `docs/PROPOSAL_DEFENSE_GUIDE.md`:
- `:202` — "targeted SHAP explainability provides visual proxy evidence"
- `:230` — "Fairlearn, AIF360, and SHAP are established, high-quality libraries"
- `:287-288` (Q12) — SHAP framed as the operative selected method
- `:290-291` (Q13) — SHAP discussed as operative, no surrogate caveat
- `:343` (Q25) — "conditional triggering of SHAP attribution"
- `:386-387` (Trap 3 coaching) — **explicitly scripts the words to say to the examiner**, verbatim uncaveated SHAP claim

This file is the single highest-risk cluster — it's the literal spoken defense script.

### MED severity (proposal .tex chapters — 10 hits, no surrogate language anywhere)
`intro.tex:33`, `literatureReview.tex:14,70,99`, `requirements.tex:15(FR-005),32(NFR-008),52`, `systemArchitectureAndMethodology.tex:37,55,77` — all describe SHAP as the delivered mechanism.

Also MED: `README.md:32,59,205,213,220` (diagram/feature-bullet layer, inconsistent with README:12/157 which are correct), `docs/research/HIGH_LEVEL_SYNTHESIS.md:16,33,59,74,118` (inconsistent with its own correct lines at :137,:162), `context-summary/low-level-summary.md:34,409,417,438,448,469,508,517,691` (inconsistent with its own correct lines at :601,:682 — line 691 sits 9 lines after a correct caveat and directly contradicts it), `context-summary/high-level-summary.md:104` (contradicts its own "do not describe it as implemented" instruction 30 lines above).

### Image
`report/src/images/architecture_highlevel.jpg` — Explainability box labeled "SHAP" alone. Flagged for regen; cannot edit as image (needs "Surrogate Attribution (SHAP deferred)" label).

### Clean (correctly caveated)
`README.md:12,157`, `docs/BiasAperture-AT.md:346`, `docs/research/HIGH_LEVEL_SYNTHESIS.md:137,162`, `context-summary/high-level-summary.md:69-74`, `context-summary/low-level-summary.md:601,682`.

**Pattern:** every doc that has the correct caveat also has 5–9 uncaveated claims elsewhere in the same file — self-inconsistent, not simply missing.

---

## C — Architecture/Structural Claims vs. Actual `src/`

Verified via full `grep -rn "^class " src/bias_aperture/`, `cli.py` read, YAML dependency check.

**Q1 — YAML config loader exists?** No. Zero hits, no pyyaml dependency, no config file loading path. `cli.py` is pure argparse.

**Q2 — Standalone orchestration layer?** No. Only `CrossValidationOrchestrator` (fairness/backends.py:965) — inside the fairness subpackage, not a top-level module.

**Q3 — Do diagram/doc names match actual classes?** Mostly yes, with one major exception:

| Claimed | Location | Actual | Status |
|---|---|---|---|
| "CLI + YAML config" orchestration box | README Mermaid, `architecture_highlevel.jpg`, `.tex` FR-008 | No YAML anywhere; hardcoded constructor defaults | **OVERSTATED** |
| `architecture_highlevel.jpg` also shows UTKFace as live 20,000+ intake, undifferentiated from FairFace | image | contradicts README's own Mermaid diagram (which dashes UTKFace/CUT correctly) | **STALE** |
| `AuditOrchestrator` (Facade) | `.tex` Design Patterns table | No such class exists; only `CrossValidationOrchestrator` | **STALE** |
| `DirectInferenceAdapter`/`PredictionsFileAdapter` | same table | Actual: `InProcessInterface`, `PredictionsFileInterface` | **STALE** |
| `TestMatrixBuilder` | same table | Actual top-level class: `DataIngestionPipeline` | **STALE** |
| `ReportFactory`/`HTMLReportBuilder` | same table | Actual: `HTMLReportGenerator` | **STALE** |
| `AuditReport` base class | same table | No such class anywhere in `src/` | **STALE** |
| `FairnessBackend`→`AIF360Backend`/`FairlearnBackend` | same table | Matches exactly | MATCHES |

5 of 6 named design-pattern classes in the `.tex` chapter's own pattern table don't exist under any name. `README.md`, `specs/`, `docs/research/MID_LEVEL_ARCHITECTURE.md`, `docs/research/HIGH_LEVEL_SYNTHESIS.md` all match actual code 1:1 — the `.tex` chapter is the sole outlier.

**Bonus (out of scope, flagged only):** `report/generator.py` and `report/templates/generator.py` are near-duplicate/dead-code files defining the same classes twice. Not doc-claimed, not scored above.

---

## D — Milestone/WP Completion Claims vs. CLAIM_LEDGER.md + Test Coverage

`CLAIM_LEDGER.md` v1.4.0: 20 active claims, all capped at VERIFIED/REPRODUCIBLE — **0 claims reach IMPLEMENTED or VALIDATED**, despite README calling WP1–WP4 "Completed 100%". Test count confirmed: 56 (`grep -c 'def test_'` matches README claim).

| WP | Claimed | Ledger Seal | Tests | Status |
|---|---|---|---|---|
| WP1/M1 Schema Lock | "Completed 100%" | No dedicated seal for schema.py lock itself | 14 (schema+model_interface) | NEEDS REVIEW |
| WP2/M2 Data Ingestion | "Completed 100%, 97,698 verified" | R-002, R-004 VERIFIED | 18 (largest suite) | **SUPPORTED** |
| WP3/M3 Report Gen | "Completed 100%"; claims HTML/**PDF** | R-015/R-016 cover HTML only; **zero PDF code, dependency, or seal** | 3 | **UNSUPPORTED (PDF)** / NEEDS REVIEW overall |
| WP4/M4 Detection+SHAP | "Completed 100%" | R-005–R-014 REPRODUCIBLE/VERIFIED | 19 | **SUPPORTED** |
| WP5/M5 Orchestration | "Active 90%, benchmark complete 10,954/10,954" | No R-xxx for CLI orchestration; ledger reserves VALIDATED for full 97,698-image run — actual run is val-split only | 2 (cli.py) + real HTML artifacts on disk corroborate report-generation sub-claim | NEEDS REVIEW |
| WP5 CLI flags | WK4 report: "`bias-aperture audit` CLI with `--backend`, `--bca-bootstrap`" — "Completed" | No seal | `cli.py::build_parser()` has **neither flag, no `audit` subcommand** (flat CLI) | **UNSUPPORTED** |

**Key flags:**
1. WP3's PDF-export claim is entirely unsupported — no code, dependency, or seal.
2. WK4 weekly report's specific CLI flag claim (`--backend`, `--bca-bootstrap`, `audit` subcommand) does not match actual `cli.py`.
3. WP5's "90%" implies near-completion but the ledger's own VALIDATED tier requires the full 97,698-image run, not the 10,954 val-split-only run actually completed — no claim can honestly reach VALIDATED yet.

---

## Cross-Cutting Root Causes

1. **`report/main.tex` (the submitted proposal) is the single largest source of stale claims** — dataset scale (backmatter), UTKFace status (abstract/intro/conclusion/methodology/lit-review), and the Design Patterns table (5 fictitious class names) all originate there, and it's internally self-contradictory in two places (its own cut-list table and NFR-004 figure are correct while surrounding prose isn't).
2. **`docs/PROPOSAL_DEFENSE_GUIDE.md` is the highest-risk single file** — 6 HIGH-severity uncaveated SHAP claims, including a verbatim scripted line to say to the examiner.
3. **Self-contradicting "corrected" docs**: `HIGH_LEVEL_SYNTHESIS.md`, both `context-summary/*.md` files, and `README.md` each contain the correct SHAP-surrogate caveat once, alongside 5–9 uncaveated claims elsewhere in the same file.
4. **`architecture_highlevel.jpg`** carries two separate stale claims (YAML config box; UTKFace shown as live/undifferentiated intake) and needs regeneration — cannot be text-edited.
5. **Two specific WP5 sub-claims (PDF export, CLI flags) are fabricated/aspirational** relative to actual `cli.py` and `report/` code — distinct from the broader "90% vs ledger tier" rounding issue.

---

*Track 2 (fixes) is gated behind per-item sign-off — nothing above has been applied. EU AI Act deadline framing intentionally excluded per scope.*
