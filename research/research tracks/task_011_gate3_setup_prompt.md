CONTEXT.md pasted first (paste that now if not already in this window).

You are user10 in the BiasAperture orchestrator. Task: task_2026-09-04_011.

Scope: Gate 3 — produce a DECISION BRIEF ONLY. Do not fix, do not recommend a default, do not resolve any item. This task cannot decide anything on its own — output must be options + tradeoffs, ending in a question for each item.

6 items requiring Aaradhya's sign-off:
1. WP3/WP5 unsupported claims — README says "Completed 100%" but PDF export is unbuilt; WK4 report references --backend/--bca-bootstrap/audit CLI flags that don't exist in cli.py. Options: pull the claim, or build the feature before Monday?
2. WP5 "90%" figure — restate as "10,954/97,698 val-split validated" (accurate but smaller-sounding), or keep 90% as-is?
3. architecture_highlevel.jpg — needs regeneration (stale YAML box, undifferentiated UTKFace), cannot be text-edited. Flag only — no image tooling in this task.
4. Duplicate report/generator.py vs report/templates/generator.py — delete one, or leave (out of ledger scope, flag only)?
5. docs/fellowship/BiasAperture_User_Requirement_Document.pdf + BiasAperture_Literature_Review.pdf — submitted PRD/lit-review, PDF-only, no .tex/.md source, contain same stale UTKFace/108,501/SHAP framing (PRD lines 24,50,79,86,96,119,141,194,317,323,329,84,273,20,131,178,219,221,299; lit review 57,79,318-319,349,438-445,504). Options: treat as dated historical snapshot (same treatment BiasAperture-AT.md §13 gives feasibility_study.pdf), or reopen for amendment before Monday?
6. Gate 0 script logic (task_2026-09-04_007's stale-claims detection rules) — sign off before it's written, or request changes?

1. Probe: list_tasks to confirm pending. 2. claim_task(account="user10", task_id="task_2026-09-04_011"). 3. Post-claim list_tasks to verify.
4. Draft the brief — one section per item, options + tradeoffs, no recommendation, ending in an explicit question.

READ-ONLY: brief only, no fixes, no commit, no push, no sync.ps1.
Submit via submit_checkpoint(account="user10", task_id="task_2026-09-04_011", summary=..., result_text=<6-item brief inline>).
