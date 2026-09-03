# Track 36 — Regulatory Expansion Map Beyond EU AI Act
**Stream:** K (Business/Regulatory) · **Priority:** 🔴 High · **Owner Focus:** Open (orchestrator-claimed)
**Estimated Time:** 45 min · **Feeds:** Report regulatory-mapping roadmap

## Instructions
1. Claim via orchestrator MCP `claim_task` (account: your assigned user, e.g. user1-user18) using the task ID in `PHASE2_TASK_MAP.md`, OR paste `CONTEXT.md` + `PHASE2_CONTEXT.md` into Claude Desktop first if running manually.
2. Then use the prompt below.
3. Submit via `submit_checkpoint` (result_text = short summary + full markdown deliverable), or save the output as `results/36_regulatory_expansion_map_beyond_eu_ai_act.md` if running manually.
4. Research-only: no code changes, no repo edits, no git commits/pushes, no sync.ps1 execution.

## Prompt

Current regulatory mapping covers EU AI Act Article 10 (10(2)-10(5), already validated against EUR-Lex per BiasAperture-AT.md §14) and NIST AI RMF (AI 100-1). Sufficient for a capstone case study; a product needs broader coverage.

Research and map additional regulatory frameworks BiasAperture's existing MetricResult output could be tagged against, following the SAME 'metric row -> specific clause' methodological template already used for Article 10 (cite Buscemi et al. 2025, already in lit review, as the template).

Cover at minimum:
1. US state-level AI laws relevant to biometric/facial-analysis systems (e.g. Colorado AI Act, NYC Local Law 144, Illinois BIPA) — note which are audit-mandate laws vs disclosure-only.
2. ISO/IEC 42001 (AI management systems) as a certifiable-standard angle distinct from EU/US statute.
3. One sector-specific example (e.g. financial services model-risk-management guidance) to show the mapping generalizes beyond facial-analysis-specific law.

For each, state clearly whether it's confirmed via source-checking (like the project's existing EUR-Lex verification) or needs legal review before being shipped as a compliance claim.
