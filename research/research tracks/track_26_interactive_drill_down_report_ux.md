# Track 26 — Interactive Drill-Down Report UX
**Stream:** H (UI/UX) · **Priority:** 🔴 High · **Owner Focus:** Open (orchestrator-claimed)
**Estimated Time:** 45 min · **Feeds:** Resolves open coordination flag — pass/fail dashboard semantics (needs Aaradhya/Tisha sign-off)

## Instructions
1. Claim via orchestrator MCP `claim_task` (account: your assigned user, e.g. user1-user18) using the task ID in `PHASE2_TASK_MAP.md`, OR paste `CONTEXT.md` + `PHASE2_CONTEXT.md` into Claude Desktop first if running manually.
2. Then use the prompt below.
3. Submit via `submit_checkpoint` (result_text = short summary + full markdown deliverable), or save the output as `results/26_interactive_drill_down_report_ux.md` if running manually.
4. Research-only: no code changes, no repo edits, no git commits/pushes, no sync.ps1 execution.

## Prompt

There is an existing open coordination flag from the original report-template sprint: whether the report's top-level verdict should read as a 'scanning aid' (draw attention to what to look at) vs a 'compliance verdict' (implies legal pass/fail) — never resolved. Watkins et al. 2022 (in lit review) is the project's own cited caution against bare threshold pass/fail framing.

Propose a concrete UX resolution — a 3-tier drill-down structure:
1. Top-level summary view using non-verdict scanning language (e.g. 'X of Y subgroups flagged for review', not 'PASS/FAIL').
2. Subgroup-level detail view showing the metric value, CI, p-value, n, and insufficient_sample flag per NFR-003.
3. SHAP evidence view for any flagged subgroup.

Deliver wireframe-level descriptions (layout, information hierarchy, what's collapsed vs expanded by default) — not visual mockups. Explicitly state this deliverable is a PROPOSAL requiring Aaradhya/Tisha sign-off before implementation.
