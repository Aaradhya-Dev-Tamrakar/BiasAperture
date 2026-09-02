# PHASE2_TASK_MAP.md — Track ↔ Orchestrator Task ID

Epic (parent): `task_2026-09-02_002`

| Track | Stream | Task ID | Title | Status |
|---|---|---|---|---|
| 21 | G | task_2026-09-02_003 | Continuous / Streaming Audit Mode | pending |
| 22 | G | task_2026-09-02_004 | Multi-Model Comparative Benchmarking & Leaderboard | **⏸ blocked (parked)** — see below |
| 23 | G | task_2026-09-02_005 | Cross-Modal Schema Generalization (v2 Architecture) | **🚫 blocked (dropped)** — see below |
| 24 | G | task_2026-09-02_006 | Automated Bias Root-Cause Clustering | pending |
| 25 | H | task_2026-09-02_007 | Web Dashboard Architecture Evaluation | pending |
| 26 | H | task_2026-09-02_008 | Interactive Drill-Down Report UX | pending |
| 27 | H | task_2026-09-02_009 | Executive / Compliance-Officer Summary Mode | pending |
| 28 | H | task_2026-09-02_010 | Accessibility & Internationalization of Reports | pending |
| 29 | I | task_2026-09-02_011 | Pluggable Fairness-Metric Registry | pending |
| 30 | I | task_2026-09-02_012 | Model-Agnostic Classifier Adapter Layer | pending |
| 31 | I | task_2026-09-02_013 | Config-Driven "Audit-as-Code" Profiles | pending |
| 32 | I | task_2026-09-02_014 | API-First Service Layer | pending |
| 33 | J | task_2026-09-02_015 | Containerized Deployment & Audit-as-a-Service Model | pending |
| 34 | J | task_2026-09-02_016 | Enterprise-Scale Performance Profiling | pending |
| 35 | J | task_2026-09-02_017 | Data Privacy & Governance for Third-Party Client Audits | pending |
| 36 | K | task_2026-09-02_018 | Regulatory Expansion Map Beyond EU AI Act | pending |
| 37 | K | task_2026-09-02_019 | Pricing & Packaging Research for Bias-Audit-as-a-Service | pending |
| 38 | K | task_2026-09-02_020 | Licensing Strategy: Open-Core vs Commercial | pending |

## Decisions applied (2026-09-02, post Aaradhya review)

**Track 23 — DROPPED (blocked, owner_account=user6, not to be claimed):**
Cross-modal generalization dilutes the vision/face-classifier niche that `BiasAperture_NOVELTY_INTEGRATION_DEFENSE.md` argues is BiasAperture's actual defensible gap (general-purpose fairness toolkits already exist — Aequitas, Themis-ML, direct AIF360/Fairlearn). Full reasoning in the task's `blocked_reason`. 16 active tracks remain (was 18).

**Track 22 — PARKED (blocked, owner_account=user6, hold):**
Leaderboard framing shifts the product's buyer mental model (compliance-audit → model-comparison tool) — needs a deliberate re-scoping decision, not default execution. Holds until Track 25 (dashboard architecture) and Track 36 (regulatory expansion) land. Unblock via `unblock_task` + `release_task` once ready to re-open.

**17 active tracks now available to claim** (16 pending + 22 once unparked).

All 20 tasks confirmed created (verified via tool response echo — each returned `status: "pending"`, `parent_id: "task_2026-09-02_002"` except the epic itself).

**Note:** `task_2026-09-02_001` is a connectivity-check ping task created before this batch (the orchestrator MCP timed out twice on read calls — `get_context_bundle`, `cloud-orchestrator-mcp:list_tasks` — before `create_task` succeeded). It carries no project content; safe to ignore or clear.
