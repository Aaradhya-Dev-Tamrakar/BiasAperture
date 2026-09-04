# Track C — Architecture/Module Structural Claims vs. Actual `src/` Code

## Setup (paste first, before the Prompt section below)

You have access to the orchestrator MCP. Account: **user4**.

Repo: https://github.com/Aaradhya-Dev-Tamrakar/BiasAperture (main branch). Clone fresh, **READ-ONLY** — do not edit, commit, or push anything in this task.

Steps:
1. `orchestrator-mcp:claim_task` with account=`user4`, task_id=`task_2026-09-04_004`
2. Do the work exactly as described in the returned task spec (also reproduced below).
3. When done, `orchestrator-mcp:submit_checkpoint` with account=`user4`, task_id=`task_2026-09-04_004`, a short summary, and `result_text` = your full markdown table findings.

Do not run `sync.ps1`, do not commit, do not modify any file in the repo. This is a research/audit task only.

---

## Prompt (task spec)

**SUBTASK C — Architecture/module structural claims vs actual `src/` code.**

Clone/fetch same repo READ-ONLY.

**Ground truth** = actual structure of `src/bias_aperture/`:
- `ls src/bias_aperture/`
- `cat src/bias_aperture/cli.py` imports
- Check for any YAML config loader anywhere in `src/`
- Check for a literal "orchestration layer" class/module, vs. just `CrossValidationOrchestrator` inside `fairness/backends.py`

Compare against:
- `README.md` Mermaid diagram (Orchestration & configuration layer / CLI+YAML config box, module names/labels)
- `report/src/images/architecture_highlevel.jpg` (describe what it depicts vs. actual — flag as image, cannot edit)
- `report/src/chapters/systemArchitectureAndMethodology.tex`
- `docs/research/MID_LEVEL_ARCHITECTURE.md`
- `docs/research/HIGH_LEVEL_SYNTHESIS.md`
- `specs/01-architecture.md`
- `specs/03-orchestrator.md`

Specifically verify:
1. Does a YAML config loader actually exist anywhere in `src/`?
2. Is there a literal "orchestration layer" class/module, or just `CrossValidationOrchestrator` inside `fairness/backends.py`?
3. Do module names in diagrams match actual file/class names?

### Output format

Markdown table:

| Claimed Structure | Doc Location | Actual src/ State | Status (MATCHES/OVERSTATED/STALE) |
|---|---|---|---|

Do not edit any file.
