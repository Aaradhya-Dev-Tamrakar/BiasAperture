CONTEXT.md pasted first (paste that now if not already in this window).

You are user7 in the BiasAperture orchestrator. Task: task_2026-09-04_008.

Scope: Gate 1 HIGH-severity text fixes only — report/ .tex chapters + docs/PROPOSAL_DEFENSE_GUIDE.md. 12 items, draft diffs, no Design Patterns table (that's 009).

Canonical phrasing anchor — adapt grammar, not substance, do not freehand-reword per file:
- Dataset scale: "97,698" (README.md:12 wording)
- UTKFace: "current case study uses FairFace; UTKFace was profiled and cut from the implementation scope"
- SHAP: "current explainability implementation uses demographic-dummy surrogate attribution; richer spatial SHAP and ITA analysis remain deferred"

Fix locations:
- back.tex:20 — 97,698
- abstract.tex:4; intro.tex:26,33,36; systemArchitectureAndMethodology.tex:46,75; conclusion.tex:6 — UTKFace/cut-list framing
- PROPOSAL_DEFENSE_GUIDE.md:202,230,287-288,290-291,343,386-387 — SHAP surrogate caveat (Trap 3 script line at 386-387 is highest priority — it's said out loud at defense)

1. Probe: list_tasks to confirm pending. 2. claim_task(account="user7", task_id="task_2026-09-04_008"). 3. Post-claim list_tasks to verify.
4. Draft each fix as a diff (old line → new line, file:line cited).
5. Note: main.pdf recompile needed after — flag, don't attempt.

READ-ONLY: draft diffs only, no commit, no push, no sync.ps1.
Submit via submit_checkpoint(account="user7", task_id="task_2026-09-04_008", summary=..., result_text=<all 12 diffs inline>).
