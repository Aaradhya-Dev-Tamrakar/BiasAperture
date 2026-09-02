# Track 27 — Executive / Compliance-Officer Summary Mode
**Stream:** H (UI/UX) · **Priority:** 🟡 Medium · **Owner Focus:** Open (orchestrator-claimed)
**Estimated Time:** 30 min · **Feeds:** Phase-2 report UX spec

## Instructions
1. Claim via orchestrator MCP `claim_task` (account: your assigned user, e.g. user1-user18) using the task ID in `PHASE2_TASK_MAP.md`, OR paste `CONTEXT.md` + `PHASE2_CONTEXT.md` into Claude Desktop first if running manually.
2. Then use the prompt below.
3. Submit via `submit_checkpoint` (result_text = short summary + full markdown deliverable), or save the output as `results/27_executive_compliance_officer_summary_mode.md` if running manually.
4. Research-only: no code changes, no repo edits, no git commits/pushes, no sync.ps1 execution.

## Prompt

Design an audience-adaptive reporting mode: a plain-language executive summary layer that sits above the existing technical report — not a replacement for it. Every claim in the summary must still trace to the underlying metric row; no unsupported simplification.

Cover:
1. What belongs in a 1-page plain-language summary (avoid jargon like 'disparate impact ratio' — propose plain phrasing without losing statistical accuracy).
2. How to avoid the same pass/fail-verdict trap flagged in Track 26 — cross-reference that track's proposal.
3. Toggle/mode-switch UX between technical and executive views within one report artifact, keeping the self-contained/offline design goal intact.
