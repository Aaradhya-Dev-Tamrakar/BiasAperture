# Track 35 — Data Privacy & Governance for Third-Party Client Audits
**Stream:** J (Deployment/Ops) · **Priority:** 🔴 High · **Owner Focus:** Open (orchestrator-claimed)
**Estimated Time:** 45 min · **Feeds:** Phase-2 ops spec — Track 32/33 dependency

## Instructions
1. Claim via orchestrator MCP `claim_task` (account: your assigned user, e.g. user1-user18) using the task ID in `PHASE2_TASK_MAP.md`, OR paste `CONTEXT.md` + `PHASE2_CONTEXT.md` into Claude Desktop first if running manually.
2. Then use the prompt below.
3. Submit via `submit_checkpoint` (result_text = short summary + full markdown deliverable), or save the output as `results/35_data_privacy_and_governance_for_third_party_client_audi.md` if running manually.
4. Research-only: no code changes, no repo edits, no git commits/pushes, no sync.ps1 execution.

## Prompt

A product version of BiasAperture would process a CLIENT's proprietary model outputs and potentially sensitive demographic-labeled data, unlike the capstone's public FairFace benchmark use.

Research a data-governance approach for handling third-party client audits.

Cover:
1. On-prem/air-gapped vs isolated-cloud-tenancy options and which client sensitivity profiles map to each (cross-reference docs/DATA_GOVERNANCE.md in the repo and note explicitly whether this track's recommendations are consistent with or extend it).
2. Data retention policy for predictions files and generated reports (how long, who can access, deletion guarantees).
3. Whether demographic labels themselves (race/gender/age) count as sensitive/special-category data under relevant regimes (GDPR Art.9-adjacent reasoning) even though they're being used FOR fairness auditing, not against the subject — this nuance matters for the product's own compliance posture.
