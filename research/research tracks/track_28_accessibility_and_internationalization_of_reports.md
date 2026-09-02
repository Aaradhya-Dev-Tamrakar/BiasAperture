# Track 28 — Accessibility & Internationalization of Reports
**Stream:** H (UI/UX) · **Priority:** 🟡 Medium · **Owner Focus:** Open (orchestrator-claimed)
**Estimated Time:** 45 min · **Feeds:** Phase-2 report UX spec

## Instructions
1. Claim via orchestrator MCP `claim_task` (account: your assigned user, e.g. user1-user18) using the task ID in `PHASE2_TASK_MAP.md`, OR paste `CONTEXT.md` + `PHASE2_CONTEXT.md` into Claude Desktop first if running manually.
2. Then use the prompt below.
3. Submit via `submit_checkpoint` (result_text = short summary + full markdown deliverable), or save the output as `results/28_accessibility_and_internationalization_of_reports.md` if running manually.
4. Research-only: no code changes, no repo edits, no git commits/pushes, no sync.ps1 execution.

## Prompt

report/generator.py produces a self-contained Jinja2 HTML report (CSS with system font stack, print media query, base64-inlined charts/images — zero external dependencies by design).

1. Run a WCAG 2.1 AA-level desk audit against the DESIGN as documented — color contrast for pass/fail or flagged-vs-not styling, keyboard navigability if interactivity is added per Track 26, alt-text for base64-inlined SHAP charts, semantic HTML/table structure for screen readers. List concrete gaps and fixes, don't just cite the standard.
2. Scaffold an i18n approach for the report template (string externalization strategy compatible with Jinja2, keeping the zero-external-dependency constraint — no CDN-hosted i18n libraries). Note which content is genuinely translatable (UI chrome, section headers) vs which must stay in English/numeric (metric names, statistical notation) for regulatory precision.
