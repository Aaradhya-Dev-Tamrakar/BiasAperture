# Track 21 — Continuous / Streaming Audit Mode
**Stream:** G (Novelty) · **Priority:** 🔴 High · **Owner Focus:** Open (orchestrator-claimed)
**Estimated Time:** 45 min · **Feeds:** Phase-2 novelty defense, WP6 spec draft

## Instructions
1. Claim via orchestrator MCP `claim_task` (account: your assigned user, e.g. user1-user18) using the task ID in `PHASE2_TASK_MAP.md`, OR paste `CONTEXT.md` + `PHASE2_CONTEXT.md` into Claude Desktop first if running manually.
2. Then use the prompt below.
3. Submit via `submit_checkpoint` (result_text = short summary + full markdown deliverable), or save the output as `results/21_continuous_streaming_audit_mode.md` if running manually.
4. Research-only: no code changes, no repo edits, no git commits/pushes, no sync.ps1 execution.

## Prompt

Design a 'continuous audit' mode that monitors a deployed model's prediction stream over time and flags fairness drift (e.g. DPD trending toward violation across weekly batches) instead of a single snapshot.

Cover:
1. Which drift-detection method fits the existing bootstrap/chi-squared framework without violating n>=30 (sequential testing, CUSUM, rolling-window bootstrap — compare tradeoffs).
2. A minimal ADDITIVE-ONLY schema extension to MetricResult (e.g. timestamp/run_id) — must not modify existing locked M1 fields.
3. Alerting/threshold design (what triggers a flag vs a hard fail).
4. How this differentiates BiasAperture from one-shot toolkits (Aequitas, raw Fairlearn dashboards).

Deliver: findings + a proposed spec section, in markdown.
