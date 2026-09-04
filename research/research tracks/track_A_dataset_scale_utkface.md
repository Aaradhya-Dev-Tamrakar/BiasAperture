# Track A — Dataset Scale & UTKFace Claims

## Setup (paste first, before the Prompt section below)

You have access to the orchestrator MCP. Account: **user2**.

Repo: https://github.com/Aaradhya-Dev-Tamrakar/BiasAperture (main branch). Clone fresh, **READ-ONLY** — do not edit, commit, or push anything in this task.

Steps:
1. `orchestrator-mcp:claim_task` with account=`user2`, task_id=`task_2026-09-04_002`
2. Do the work exactly as described in the returned task spec (also reproduced below).
3. When done, `orchestrator-mcp:submit_checkpoint` with account=`user2`, task_id=`task_2026-09-04_002`, a short summary, and `result_text` = your full markdown table findings.

Do not run `sync.ps1`, do not commit, do not modify any file in the repo. This is a research/audit task only.

---

## Prompt (task spec)

**SUBTASK A — Dataset scale & UTKFace claims.**

Clone/fetch `Aaradhya-Dev-Tamrakar/BiasAperture` main (READ-ONLY, no writes/commits).

Grep entire repo for `108,501` | `108501` | `97,698` | `97698` | `20,000+` and every UTKFace mention.

For each hit, record file:line, exact claim text, and whether it matches verified ground truth:
- **97,698** = 86,744 train + 10,954 val, per `docs/research/CLAIM_LEDGER.md` R-002
- **UTKFace** = CUT from implementation per Cut-List #2, profiled only (not a live pipeline input)

Flag any file NOT yet corrected. Check at minimum:
- `report/main.tex`
- `report/main.pdf` text layer if extractable
- `docs/PROPOSAL_DEFENSE_GUIDE.md`
- `docs/PRE_PROPOSAL_READING_GUIDE.md`
- `docs/BiasAperture-AT.md`
- `research/context feed/*`
- `research/research tracks/*`
- `dev-logs/*`
- `context-summary/*`
- `specs/*`

### Output format

Markdown table:

| Claim | File:Line | Current Text | Verified Correct Value | Status (MATCHES/STALE) |
|---|---|---|---|---|

Do not edit any file.
