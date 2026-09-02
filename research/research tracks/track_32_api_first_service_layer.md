# Track 32 — API-First Service Layer
**Stream:** I (Modular Architecture) · **Priority:** 🔴 High · **Owner Focus:** Open (orchestrator-claimed)
**Estimated Time:** 60 min · **Feeds:** Phase-2 architecture spec — depends on Track 25 dashboard decision

## Instructions
1. Claim via orchestrator MCP `claim_task` (account: your assigned user, e.g. user1-user18) using the task ID in `PHASE2_TASK_MAP.md`, OR paste `CONTEXT.md` + `PHASE2_CONTEXT.md` into Claude Desktop first if running manually.
2. Then use the prompt below.
3. Submit via `submit_checkpoint` (result_text = short summary + full markdown deliverable), or save the output as `results/32_api_first_service_layer.md` if running manually.
4. Research-only: no code changes, no repo edits, no git commits/pushes, no sync.ps1 execution.

## Prompt

The engine (src/bias_aperture) is already decoupled from the CLI entry point (cli.py) — fairness/, report/, explainability.py, data_ingestion.py are importable as a library.

Design a REST (or gRPC) service layer wrapping the existing engine for CI/CD and third-party integration (e.g. a company runs a bias audit as a pipeline step on every model release).

Cover:
1. Minimal endpoint set (submit predictions file/job, poll status, fetch report/JSON results) mapped onto existing engine calls — cite which existing modules each endpoint would call.
2. Auth and rate-limiting considerations given this may process a client's proprietary model outputs (cross-reference Track 35 for data-governance depth, don't duplicate it here).
3. Sync vs async job model given audit runtime can be non-trivial at scale (cross-reference Track 34, don't duplicate).
4. How this relates to Track 25's dashboard options — the API should be the dashboard's backend, not a parallel reimplementation.
