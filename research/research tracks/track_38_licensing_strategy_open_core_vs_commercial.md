# Track 38 — Licensing Strategy: Open-Core vs Commercial
**Stream:** K (Business/GTM) · **Priority:** 🟡 Medium · **Owner Focus:** Open (orchestrator-claimed)
**Estimated Time:** 30 min · **Feeds:** Phase-2 business case

## Instructions
1. Claim via orchestrator MCP `claim_task` (account: your assigned user, e.g. user1-user18) using the task ID in `PHASE2_TASK_MAP.md`, OR paste `CONTEXT.md` + `PHASE2_CONTEXT.md` into Claude Desktop first if running manually.
2. Then use the prompt below.
3. Submit via `submit_checkpoint` (result_text = short summary + full markdown deliverable), or save the output as `results/38_licensing_strategy_open_core_vs_commercial.md` if running manually.
4. Research-only: no code changes, no repo edits, no git commits/pushes, no sync.ps1 execution.

## Prompt

The repo currently ships under MIT LICENSE (full permissive open source) as a capstone/portfolio project.

Research an open-core licensing strategy for a product transition: what would stay MIT/open-source (candidate: the core engine — fairness/, statistics, the locked schema, CLI, offline HTML report per Track 25's baseline) vs what would be commercial/enterprise-gated (candidate: the hosted dashboard/API from Tracks 25/32, continuous audit mode from Track 21, multi-tenant SaaS ops from Track 33, client data-governance tooling from Track 35).

Cover:
1. 2-3 real open-core precedents in adjacent developer-tooling or compliance-tooling space and how they drew this line.
2. Risk of the current MIT license on the whole repo undermining a future commercial layer if not restructured before wider release: flag this as a decision needed from Aaradhya/Tisha, don't unilaterally recommend re-licensing already-public code.
