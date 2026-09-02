# Track 22 — Multi-Model Comparative Benchmarking & Leaderboard

> **⏸ PARKED (2026-09-02, Aaradhya) — do not claim yet.** Holds until Track 25 (Web Dashboard Architecture) and Track 36 (Regulatory Expansion Map) land. Live status: `task_2026-09-02_004`, blocked. Full reasoning in `PHASE2_TASK_MAP.md`.

**Stream:** G (Novelty) · **Priority:** 🔴 High · **Owner Focus:** Open (orchestrator-claimed)
**Estimated Time:** 45 min · **Feeds:** Phase-2 novelty defense

## Instructions
1. Claim via orchestrator MCP `claim_task` (account: your assigned user, e.g. user1-user18) using the task ID in `PHASE2_TASK_MAP.md`, OR paste `CONTEXT.md` + `PHASE2_CONTEXT.md` into Claude Desktop first if running manually.
2. Then use the prompt below.
3. Submit via `submit_checkpoint` (result_text = short summary + full markdown deliverable), or save the output as `results/22_multi_model_comparative_benchmarking_and_leaderboard.md` if running manually.
4. Research-only: no code changes, no repo edits, no git commits/pushes, no sync.ps1 execution.

## Prompt

Research how to extend BiasAperture to audit and RANK multiple models against the same schema and dataset — a 'fairness leaderboard'.

Cover:
1. Normalized scoring approach across the 4 metrics (DPD fair-point 0, DIR fair-point 1 — must handle asymmetry, per existing metric-aware logic principle) into one comparable composite score, with justification and cited precedent (e.g. HELM, model-card leaderboards).
2. How ModelInterface's dual-mode (in-process / predictions-file) supports batch-comparing N models.
3. Report-template implications (comparison table/chart in the Jinja2 report) — flag as a coordination item for whoever owns report templates, don't silently redesign the report.
4. Risk of the leaderboard being read as a bare pass/fail ranking (echo the project's own caution against bare four-fifths-rule thresholds — Watkins et al. 2022, already in the lit review).
