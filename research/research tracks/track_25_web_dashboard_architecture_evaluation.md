# Track 25 — Web Dashboard Architecture Evaluation
**Stream:** H (UI/UX) · **Priority:** 🔴 High · **Owner Focus:** Open (orchestrator-claimed)
**Estimated Time:** 45 min · **Feeds:** Phase-2 UI/UX spec — decision needed from Aaradhya/Tisha

## Instructions
1. Claim via orchestrator MCP `claim_task` (account: your assigned user, e.g. user1-user18) using the task ID in `PHASE2_TASK_MAP.md`, OR paste `CONTEXT.md` + `PHASE2_CONTEXT.md` into Claude Desktop first if running manually.
2. Then use the prompt below.
3. Submit via `submit_checkpoint` (result_text = short summary + full markdown deliverable), or save the output as `results/25_web_dashboard_architecture_evaluation.md` if running manually.
4. Research-only: no code changes, no repo edits, no git commits/pushes, no sync.ps1 execution.

## Prompt

The original capstone cut-list (§8, BiasAperture-AT.md) cut a Web UI (Streamlit/Flask) as 'pure UX layer, zero grading relevance' — CLI + standalone Jinja2 HTML report was kept instead. That decision was capstone-scoped, not product-scoped. Re-evaluate it now.

Compare 3 concrete architectures:
1. Streamlit — fastest to ship, weakest for a multi-tenant SaaS.
2. FastAPI backend + React/Vite frontend — more work, real product-grade separation, reuses src/bias_aperture engine as a library.
3. Flask + HTMX — middle ground, server-rendered, minimal JS.

For each: dev-effort estimate relative to the current codebase (CLI + generator.py already exist and could become the API's core), hosting/ops implications, and fit with the existing offline-HTML-report design goal (self-contained reports must keep working as an export option regardless of dashboard choice). End with a recommendation.
