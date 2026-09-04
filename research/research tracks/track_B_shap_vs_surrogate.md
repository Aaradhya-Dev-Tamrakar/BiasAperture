# Track B — Explainability Method Claims (SHAP vs. Demographic-Dummy Surrogate)

## Setup (paste first, before the Prompt section below)

You have access to the orchestrator MCP. Account: **user3**.

Repo: https://github.com/Aaradhya-Dev-Tamrakar/BiasAperture (main branch). Clone fresh, **READ-ONLY** — do not edit, commit, or push anything in this task.

Steps:
1. `orchestrator-mcp:claim_task` with account=`user3`, task_id=`task_2026-09-04_003`
2. Do the work exactly as described in the returned task spec (also reproduced below).
3. When done, `orchestrator-mcp:submit_checkpoint` with account=`user3`, task_id=`task_2026-09-04_003`, a short summary, and `result_text` = your full markdown table findings.

Do not run `sync.ps1`, do not commit, do not modify any file in the repo. This is a research/audit task only.

---

## Prompt (task spec)

**SUBTASK B — Explainability method claims (SHAP vs demographic-dummy surrogate).**

Clone/fetch same repo READ-ONLY.

**Ground truth:** actual implementation in `src/bias_aperture/explainability.py` uses demographic-dummy surrogate attribution (per `README.md` abstract, ~line 12: *"current explainability implementation uses demographic-dummy surrogate attribution; richer spatial SHAP and ITA analysis remain deferred"*).

Search entire repo for every claim that SHAP is the (sole/current) explainability method, **without** a surrogate/deferred caveat, in at minimum:
- `report/src/chapters/*.tex` (`intro.tex`, `literatureReview.tex`, `requirements.tex` FR-005/NFR-008, `systemArchitectureAndMethodology.tex`)
- `report/src/images/architecture_highlevel.jpg` (note only — cannot edit images, flag as image needing regen)
- `docs/PROPOSAL_DEFENSE_GUIDE.md` (esp. Q12/Q13 answers and the quoted defense script)
- `docs/PRE_PROPOSAL_READING_GUIDE.md`
- `docs/BiasAperture-AT.md`
- `README.md` (recheck current state)
- `docs/research/*SYNTHESIS*.md`
- `context-summary/*`

For each hit: file:line, exact claim, whether a surrogate-caveat is present nearby or absent.

### Output format

Markdown table:

| Location | Claim Text | Caveat Present? (Y/N) | Severity |
|---|---|---|---|

Severity legend:
- **HIGH** = examiner-facing script assumes SHAP runs live (e.g. defense Q&A script)
- **MED** = doc only, not examiner-facing in real time
- **LOW** = historical record / superseded note

Do not edit any file.
