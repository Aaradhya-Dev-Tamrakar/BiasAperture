# PHASE2_CONTEXT.md — Product Upgrade Sprint (paste alongside CONTEXT.md)

Additive context only. Nothing here overrides `CONTEXT.md` or the M1 schema lock (`schema-lock-m1.md` / `src/bias_aperture/schema.py`) — both remain in force verbatim.

## Where the project actually is (as of Sept 2, 2026)
- WP1–WP4 complete (100%): schema lock, FairFace ingestion (97,698 images verified), Fairlearn+AIF360 dual-backend engine, BCa bootstrap, chi-squared, SHAP explainability.
- WP5 ~90%: inference run complete (10,954/10,954 validation images, schema-valid CSV at `data/processed/fairface_predictions_val.csv`); remaining step is generating/reviewing the audit HTML report and finalizing `report/main.pdf`.
- Real, tested source tree exists: `src/bias_aperture/{schema,model_interface,data_ingestion,explainability,cli}.py` + `fairness/` + `report/` packages, with a full pytest suite (`src/tests/`).

## What Phase 2 is
A separate track from the capstone defense. Capstone-scoped cuts (e.g. §8 Cut #1: "Web UI, keep CLI only — zero grading relevance") are **not binding** here — they were graded-scope decisions, not product decisions, and are explicitly reopened where relevant (see Track 25).

## Non-negotiables that still apply in Phase 2
- Diagnostic-only scope: no retraining, no debiasing, no synthetic data generation.
- M1 schema (`schema.py`) is locked verbatim — race_7 / gender_2 / age_9 labels, `SubjectRecord`, `MetricResult`. Any Phase-2 proposal must be **additive** (new modules/fields/layers), never a modification of the locked fields.
- NFR-001 (α=0.05), NFR-002 (≥1,000 bootstrap resamples), NFR-003 (n≥30 guard, `insufficient_sample` flag) are non-negotiable across every new surface (dashboard, API, streaming mode, etc.) — no track may propose relaxing these for speed or UX convenience.
- Metric-aware fair-point handling (`disparate_impact_ratio` fair point = 1.0; the other three = 0) must be preserved in any new aggregation, scoring, or leaderboard logic.

## Open coordination flags inherited from the original sprint (context only, not this sprint's job to silently resolve)
- Dashboard "pass/fail" semantics — scanning aid vs. compliance verdict (Track 26 is scoped to propose a resolution, still needs Aaradhya/Tisha sign-off).
- EU AI Act sub-clause content ownership, SHAP image/keying guarantees, template test fixtures, Model Card section content — unaffected by Phase 2; do not duplicate this work in the new tracks.

## Deliverable conventions (same as the original 20-track sprint)
- Research-only: no code changes, no repo edits, no git commits/pushes, no `sync.ps1` execution.
- Handoff is `submit_checkpoint`'s `result_text` field: a short summary + the full markdown deliverable.
- Suggested filenames follow `results/NN_description.md`, continuing the existing `research/results/` convention.
- Raise cross-track overlaps as explicit coordination flags (see `research/results/cross_track_conflict_log.md` pattern) — do not silently resolve another track's scope.
