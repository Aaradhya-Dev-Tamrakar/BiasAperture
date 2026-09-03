# Track 31 — Config-Driven "Audit-as-Code" Profiles
**Stream:** I (Modular Architecture) · **Priority:** 🟡 Medium · **Owner Focus:** Open (orchestrator-claimed)
**Estimated Time:** 30 min · **Feeds:** cli.py roadmap

## Instructions
1. Claim via orchestrator MCP `claim_task` (account: your assigned user, e.g. user1-user18) using the task ID in `PHASE2_TASK_MAP.md`, OR paste `CONTEXT.md` + `PHASE2_CONTEXT.md` into Claude Desktop first if running manually.
2. Then use the prompt below.
3. Submit via `submit_checkpoint` (result_text = short summary + full markdown deliverable), or save the output as `results/31_config_driven_audit_as_code_profiles.md` if running manually.
4. Research-only: no code changes, no repo edits, no git commits/pushes, no sync.ps1 execution.

## Prompt

cli.py currently orchestrates a fixed audit flow (predictions file -> fairness engine -> SHAP -> Jinja2 report) via CLI flags.

Design a YAML/JSON 'audit profile' format so a repeatable audit configuration (which metrics to run, which subgroup intersections, alpha/bootstrap-resample overrides within NFR-001/002 bounds, which regulatory mapping to attach) can be versioned and reused per client or per regulation, instead of re-specifying CLI flags each run.

Cover:
1. A minimal schema for the profile file with examples (e.g. an 'EU-AI-Act-default.yaml' vs a stricter client-specific profile).
2. Validation rules — a profile must not be able to relax NFR-003's n>=30 guard or NFR-001's alpha below documented bounds without an explicit, logged override.
3. How this fits a future CI/CD integration (Track 32) as a natural input artifact.
