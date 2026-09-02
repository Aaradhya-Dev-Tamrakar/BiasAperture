# Track 24 — Automated Bias Root-Cause Clustering
**Stream:** G (Novelty) · **Priority:** 🟡 Medium · **Owner Focus:** Open (orchestrator-claimed)
**Estimated Time:** 45 min · **Feeds:** Phase-2 novelty defense, explainability.py roadmap

## Instructions
1. Claim via orchestrator MCP `claim_task` (account: your assigned user, e.g. user1-user18) using the task ID in `PHASE2_TASK_MAP.md`, OR paste `CONTEXT.md` + `PHASE2_CONTEXT.md` into Claude Desktop first if running manually.
2. Then use the prompt below.
3. Submit via `submit_checkpoint` (result_text = short summary + full markdown deliverable), or save the output as `results/24_automated_bias_root_cause_clustering.md` if running manually.
4. Research-only: no code changes, no repo edits, no git commits/pushes, no sync.ps1 execution.

## Prompt

Research a step beyond per-disparity SHAP: applying unsupervised clustering (e.g. k-means/HDBSCAN on SHAP attribution vectors) ACROSS all flagged disparities in an audit run, to auto-group recurring proxy-feature patterns ('disparities driven by lighting/skin-tone proxy' vs 'disparities driven by pose/angle proxy').

Cover:
1. Candidate clustering method and why, given typically small numbers of flagged subgroups per audit (n likely <50 — address the small-N clustering validity problem explicitly).
2. How this would present in the report (a new 'Root Cause Themes' section — flag as a report-template coordination item, don't redesign generator.py here).
3. Whether this counts as new research novelty vs still engineering/integration novelty per the project's existing novelty-defense framing (BiasAperture_NOVELTY_INTEGRATION_DEFENSE.md) — be honest, don't oversell it.
