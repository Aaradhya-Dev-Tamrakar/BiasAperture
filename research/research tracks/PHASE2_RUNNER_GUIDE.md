# 🚀 Phase 2 Runner Guide — Product Upgrade Sprint (18 Parallel Orch Executors)

Continues the original `RUNNER_GUIDE.md` (20-track capstone sprint, tracks 01–20, now complete) into a second sprint: tracks 21–38, planning BiasAperture's evolution from capstone to full product.

## Execution model
All 18 tasks already exist as real orchestrator MCP tasks, created under one parent epic:

- **Epic:** `task_2026-09-02_002` — "BiasAperture Phase 2: Product Upgrade Sprint"
- **Subtasks:** `task_2026-09-02_003` … `task_2026-09-02_020` (18 tasks, tracks 21–38)
- See `PHASE2_TASK_MAP.md` for the track ↔ task_id mapping.

Each of your 18 available users claims one task:
```
claim_task(account="userN", task_id="task_2026-09-02_0XX")
```
...works the prompt embedded in that task's `spec` (also mirrored in the matching `track_NN_*.md` file here for readability), and hands off via:
```
submit_checkpoint(task_id="task_2026-09-02_0XX", result_text="<summary + full markdown>")
```

If an executor is running manually in Claude Desktop instead of via the orchestrator, paste `CONTEXT.md` + `PHASE2_CONTEXT.md` first, then the track's prompt, then save to `results/NN_description.md`.

## Streams

| Stream | Focus | Tracks |
|---|---|---|
| **G** — Novelty & Differentiation | Deepens the product's defensible edge beyond the capstone's integration-novelty framing | 21, 24 (22 parked, 23 dropped — see `PHASE2_TASK_MAP.md`) |
| **H** — UI/UX & Product Experience | Reopens the capstone's cut Web UI decision; resolves the open dashboard-semantics flag | 25, 26, 27, 28 |
| **I** — Modular Architecture & Extensibility | Turns locked-but-closed modules (metric set, model interface, CLI) into pluggable, additive layers | 29, 30, 31, 32 |
| **J** — Deployment, Scale & Ops | Containerization, 10–100x scale, client data governance | 33, 34, 35 |
| **K** — Business / Go-to-Market & Regulatory Expansion | Pricing, licensing, regulatory coverage beyond EU AI Act | 36, 37, 38 |

## Status update (2026-09-02)
- **Track 23 — dropped.** Do not claim. See `PHASE2_TASK_MAP.md` for full reasoning.
- **Track 22 — parked/blocked.** Do not claim yet; holds until Tracks 25 and 36 land. See `PHASE2_TASK_MAP.md`.
- 16 tracks are open to claim now.

## Priority order (if reviewing as they finish)

### 🔴 Phase 1 — Critical (read first)
| Track | File | What it unlocks |
|---|---|---|
| 21 | `track_21_continuous_streaming_audit_mode.md` | Novelty differentiator #1, WP6 spec seed |
| 25 | `track_25_web_dashboard_architecture_evaluation.md` | Unblocks Track 32 and the whole UI/UX stream |
| 26 | `track_26_interactive_drill_down_report_ux.md` | Resolves the long-open dashboard-semantics flag |
| 29 | `track_29_pluggable_fairness_metric_registry.md` | Unblocks metric extensibility roadmap |
| 30 | `track_30_model_agnostic_classifier_adapter_layer.md` | Unblocks auditing non-FairFace models |
| 32 | `track_32_api_first_service_layer.md` | Unblocks Tracks 33/37 |
| 35 | `track_35_data_privacy_and_governance_for_third_party_client_audi.md` | Blocking for any real client pilot |
| 36 | `track_36_regulatory_expansion_map_beyond_eu_ai_act.md` | Blocking for any non-EU client claim |

### 🟡 Phase 2 — Medium
| Track | File |
|---|---|
| 23 | `track_23_cross_modal_schema_generalization_v2_architecture.md` |
| 24 | `track_24_automated_bias_root_cause_clustering.md` |
| 27 | `track_27_executive_compliance_officer_summary_mode.md` |
| 28 | `track_28_accessibility_and_internationalization_of_reports.md` |
| 31 | `track_31_config_driven_audit_as_code_profiles.md` |
| 33 | `track_33_containerized_deployment_and_audit_as_a_service_model.md` |
| 34 | `track_34_enterprise_scale_performance_profiling.md` |
| 37 | `track_37_pricing_and_packaging_research_for_bias_audit_as_a_serv.md` |
| 38 | `track_38_licensing_strategy_open_core_vs_commercial.md` |

## After all 18 complete — synthesis order
1. Streams G (21–24) + K (36–38) → refresh `docs/BiasAperture_NOVELTY_INTEGRATION_DEFENSE.md` with a "Phase 2" section — do not overwrite the capstone defense, append.
2. Stream H (25–28) → single "Product UI/UX Spec" doc; Track 26's proposal is the one that needs explicit Aaradhya/Tisha sign-off before anything is built.
3. Stream I (29–32) → "Modular Architecture v2" doc, each proposal checked against schema.py for zero drift from the M1 lock.
4. Stream J (33–35) → "Ops & Deployment" doc; Track 35 gates anything client-facing.
5. Joint review pass → cross_track_conflict_log-style pass over the 18 outputs before any implementation branch is opened (e.g. `feat/phase2-*`).

## Checklist
- [ ] All 18 results captured via `submit_checkpoint` (or saved to `results/` if run manually)
- [ ] Track 25 (dashboard architecture) decision made before starting Track 32 implementation
- [ ] Track 26 (drill-down UX) reviewed and signed off by Aaradhya/Tisha before implementation
- [ ] Track 29/30 proposals checked against `schema.py` — confirmed zero modification to locked fields
- [ ] Track 35 (data governance) reviewed against existing `docs/DATA_GOVERNANCE.md`
- [ ] Track 38 (licensing) explicitly flagged to Aaradhya/Tisha, not auto-applied
