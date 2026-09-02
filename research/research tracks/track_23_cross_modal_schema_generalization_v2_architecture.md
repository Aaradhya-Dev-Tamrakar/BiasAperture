# Track 23 — Cross-Modal Schema Generalization (v2 Architecture)

> **🚫 DROPPED (2026-09-02, Aaradhya) — do not claim/execute.** Dilutes BiasAperture's defensible vision/face-classifier niche per `BiasAperture_NOVELTY_INTEGRATION_DEFENSE.md`. Live status: `task_2026-09-02_005`, blocked. Full reasoning in `PHASE2_TASK_MAP.md`.

**Stream:** G (Novelty) · **Priority:** 🟡 Medium · **Owner Focus:** Open (orchestrator-claimed)
**Estimated Time:** 60 min · **Feeds:** Phase-2 architecture spec

## Instructions
1. Claim via orchestrator MCP `claim_task` (account: your assigned user, e.g. user1-user18) using the task ID in `PHASE2_TASK_MAP.md`, OR paste `CONTEXT.md` + `PHASE2_CONTEXT.md` into Claude Desktop first if running manually.
2. Then use the prompt below.
3. Submit via `submit_checkpoint` (result_text = short summary + full markdown deliverable), or save the output as `results/23_cross_modal_schema_generalization_v2_architecture.md` if running manually.
4. Research-only: no code changes, no repo edits, no git commits/pushes, no sync.ps1 execution.

## Prompt

Research how the underlying PATTERN (demographic schema + MetricResult shape + n>=30 guard + dual-backend validation) could generalize to audit non-vision modalities (tabular hiring/credit models, voice/speech classifiers, text/NLP classifiers) as a v2 product line — WITHOUT touching the existing locked FairFace schema (schema.py).

Propose:
1. An abstraction layer (e.g. a base DemographicSchema class that FairFaceSchema subclasses/implements) that keeps M1 100% intact as one concrete instantiation.
2. What would need to change per modality (subject identity field, label vocab, protected-attribute sourcing).
3. Which existing components (fairness/base.py Strategy pattern, statistics.py bootstrap/chi-squared) are already modality-agnostic and reusable as-is vs which are FairFace-coupled and need an adapter.

Explicitly confirm in the deliverable that this track proposes ADDITIVE new modules only, zero modification to schema.py.
