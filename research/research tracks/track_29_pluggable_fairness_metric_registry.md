# Track 29 — Pluggable Fairness-Metric Registry
**Stream:** I (Modular Architecture) · **Priority:** 🔴 High · **Owner Focus:** Open (orchestrator-claimed)
**Estimated Time:** 45 min · **Feeds:** fairness/base.py roadmap

## Instructions
1. Claim via orchestrator MCP `claim_task` (account: your assigned user, e.g. user1-user18) using the task ID in `PHASE2_TASK_MAP.md`, OR paste `CONTEXT.md` + `PHASE2_CONTEXT.md` into Claude Desktop first if running manually.
2. Then use the prompt below.
3. Submit via `submit_checkpoint` (result_text = short summary + full markdown deliverable), or save the output as `results/29_pluggable_fairness_metric_registry.md` if running manually.
4. Research-only: no code changes, no repo edits, no git commits/pushes, no sync.ps1 execution.

## Prompt

fairness/base.py implements a Strategy pattern (FairnessBackend ABC, FairlearnBackend/AIF360Backend concrete impls) for the Core Four metrics only. MetricResult.metric_name is currently a Literal of exactly 4 values (schema.py) — locked at M1.

Design a plugin registry so third-party or later-added metrics (e.g. treatment equality, predictive parity) can be registered without modifying the M1-locked Literal type or the core engine.

Cover:
1. How to widen metric_name from a hard Literal to a registry-validated str WITHOUT breaking existing Core-Four-only consumers (report templates, tests) — propose as an additive v2 type, not a schema.py edit.
2. What interface a plugin metric must implement to stay compatible with the existing n>=30 guard, bootstrap CI, and chi-squared pattern in MetricResult.__post_init__.
3. Whether the fair-point asymmetry handling (DIR=1.0 vs others=0) needs to become a per-metric-plugin declared property rather than hardcoded.
