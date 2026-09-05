CONTEXT.md pasted first (paste that now if not already in this window).

You are user6 in the BiasAperture orchestrator. Task: task_2026-09-04_007.

Scope: Gate 0 only — anti-drift tooling, not content fixes.
1. Probe: list_tasks to confirm task_2026-09-04_007 is pending.
2. claim_task(account="user6", task_id="task_2026-09-04_007")
3. Post-claim: list_tasks to verify registration (claim_task returns no confirmation payload).
4. Draft scripts/check_stale_claims.py — pre-commit hook (repo: local) that fails on staged .md/.tex containing:
   - bare "108,501"/"108501" without "released"/"pre-discard"/"pre-annotation" nearby
   - "UTKFace" without "cut" nearby (not "secondary" — that phrasing is itself flagged as undersell)
   - "SHAP" without "surrogate"/"deferred"/"fallback" nearby
5. Draft the .pre-commit-config.yaml addition wiring it in.
6. Draft one line for VERIFICATION_AND_SCRUTINY_GUIDE.md §5: "Doc-Claim Check — does check_stale_claims.py pass on every touched .md/.tex?"

READ-ONLY: draft only, do not commit, do not push, do not run sync.ps1.
Submit via submit_checkpoint(account="user6", task_id="task_2026-09-04_007", summary=..., result_text=<full script + config diff + guide line, inline>).
