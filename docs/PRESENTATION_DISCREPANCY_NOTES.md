# BiasAperture — Presentation Discrepancy Notes

**File audited:** `BiasAperture_Proposal_Presentation.pptx` (Tisha's slides, 7 September 2026)
**Audited against:** `main` @ `eb1f33e`, `research/results/DISCREPANCY_LEDGER.md` (2026-09-04 audit), `docs/research/CLAIM_LEDGER.md` v1.4.0
**Status:** Not yet applied — flagged for Tisha's review, no slide content has been edited.

---

## 1. Dataset Scale — FairFace 108,501 vs. 97,698

**Slide:** System Architecture (diagram, both instances)
**Current text:** "FairFace dataset — 108,501 images"
**Corrected text:** "FairFace dataset — 97,698 images (released)"

**Why it matters:** 108,501 is the pre-annotation-discard scrape total from Karkkainen & Joo (2021); it was never the released count. `CLAIM_LEDGER.md` R-002 verifies 97,698 by direct CSV line count (86,744 train + 10,954 val), sealed **VERIFIED**. `README.md`, `CLAUDE.md`, and `requirements.tex` NFR-004 already use 97,698 — this slide is the one place still carrying the stale figure, and it's the exact same error already flagged in `report/main.tex` backmatter (Discrepancy Ledger item A, HIGH). An examiner cross-referencing the deck against the report or repo will catch a same-day inconsistency.

---

## 2. UTKFace Shown as Live Secondary Benchmark

**Slides:** System Architecture (diagram), Objectives ("Benchmark Validation" bullet)
**Current text:** "UTKFace dataset — 20,000+ images" (diagram, parallel intake box, undifferentiated from FairFace); "Validate using FairFace and UTKFace with a FairFace-trained CNN baseline" (Objectives)
**Corrected text:** Diagram — relabel box "UTKFace — [CUT, Cut-List #2] profiled only, not ingested"; Objectives bullet — "Benchmark Validation: Validate using FairFace (97,698 images) with a FairFace-trained CNN baseline. UTKFace was evaluated and formally cut from implementation scope (Cut-List #2)."

**Why it matters:** UTKFace is confirmed **cut** — DEX label-noise and misaligned racial taxonomy, documented in `BiasAperture-AT.md` §8 Cut-List #2 and §21. It was profiled only, never scored. This is Discrepancy Ledger item A (HIGH) — the same framing error already present in `abstract.tex`, `intro.tex`, and `conclusion.tex`. Showing it as a parallel, equally-weighted data source directly contradicts the scope-discipline argument the team is using as a defense strength ("explicit scope cuts, not silent drops" — see prior rubric gap-check, "Scope Achievement" row). If an examiner asks "is UTKFace actually used," the honest answer (no) will visibly contradict this slide.

---

## 3. Orchestration Box — "CLI + YAML config"

**Slide:** System Architecture (diagram)
**Current text:** "Orchestration & configuration layer — CLI + YAML config"
**Corrected text:** "Orchestration layer — CLI (argparse)"

**Why it matters:** No YAML loader exists anywhere in `src/` — no `pyyaml` dependency, no config-file code path. `cli.py` is pure argparse. This is Discrepancy Ledger item C, Q1 (OVERSTATED), and the architecture diagram (`architecture_highlevel.jpg`) carries the identical stale claim, already flagged for regeneration. If this is meant as forward-looking/aspirational architecture rather than current state, the slide should say so explicitly (e.g., "planned: YAML config") rather than presenting it as built.

---

## 4. Compliance Report Format — "HTML/PDF"

**Slide:** System Architecture (diagram)
**Current text:** "Compliance report (HTML/PDF)"
**Corrected text:** "Compliance report (HTML)"

**Why it matters:** PDF export has zero supporting code, dependency, or `CLAIM_LEDGER.md` seal — Discrepancy Ledger item D confirms WP3's PDF claim as **UNSUPPORTED**. `report/generator.py` produces HTML only. Same fix applies to the "Expected Output" slide if PDF is implied there.

---

## 5. Article 10 Deadline — Stated as Current

**Slide:** Introduction ("Regulatory Inflection: EU AI Act")
**Current text:** "The EU AI Act (Article 10) enters into force 2 August 2026... This creates an immediate compliance imperative"
**Status:** **Flagged, not corrected here** — held separately per the active discrepancy-audit scope (explicitly excluded from the four-track `task_2026-09-04_001` audit).

**Why it matters:** Regulation (EU) 2026/1744 deferred these obligations — Annex III systems to 2 December 2027, Annex I to 2 August 2028 — after this slide's claim was written. This is load-bearing for the novelty/urgency argument in the deck's framing ("immediate compliance imperative"). Needs its own resolution pass across the report and this deck together, not a one-line slide fix, since the urgency argument itself may need reframing. Do not edit this slide until that separate pass happens.

---

## 6. Core Four Metrics — Slide Numbering Error

**Slide:** Core Four Metrics
**Current text:** Boxes numbered 01, 02, 03, 03 (Disparate Impact Ratio incorrectly shares "03" with Equal Opportunity Difference; no box is numbered 04)
**Corrected text:** Renumber sequentially 01–04.

**Why it matters:** Cosmetic, but visible on the slide as displayed — low defense risk but a one-line fix.

---

## 7. Minor Typo

**Slide:** Introduction (body text)
**Current text:** "race/ethnicity predictionare now widely deployed"
**Corrected text:** "race/ethnicity prediction are now widely deployed"

---

## 8. SHAP Explainability — No Surrogate Caveat

**Slide:** Expected Output ("SHAP Explainability — Visualizations of SHAP feature attribution maps for each flagged disparity")
**Current text:** States SHAP flatly as the delivered mechanism.
**Status:** **Flagged, not corrected here** — genuinely ambiguous whether this slide is describing current implementation or forward-looking proposal scope (the deck is proposal-stage). Not silently resolving per standing instruction.

**Why it matters:** Actual `explainability.py` implements demographic-dummy surrogate attribution; SHAP is attempted first but falls back on failure, and full spatial/pixel-level SHAP is deferred to future work (Discrepancy Ledger item B — this is the single highest-risk cluster repo-wide, with `docs/PROPOSAL_DEFENSE_GUIDE.md` containing a verbatim uncaveated script line for this exact question). If this slide is meant as current-state, it needs the same caveat: "Surrogate feature attribution (SHAP deferred)." If meant as proposed/target scope, no change needed — confirm which before editing.

---

## Summary Table

| # | Slide | Severity | Resolved here? |
|---|---|---|---|
| 1 | System Architecture | HIGH | Yes — corrected text given |
| 2 | System Architecture, Objectives | HIGH | Yes — corrected text given |
| 3 | System Architecture | HIGH | Yes — corrected text given |
| 4 | System Architecture | MED | Yes — corrected text given |
| 5 | Introduction | HIGH | **No — separate track, do not edit yet** |
| 6 | Core Four Metrics | LOW | Yes — corrected text given |
| 7 | Introduction | LOW | Yes — corrected text given |
| 8 | Expected Output | HIGH (if current-state) | **No — needs scope clarification first** |
