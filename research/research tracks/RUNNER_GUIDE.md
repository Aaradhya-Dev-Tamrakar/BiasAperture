# 🚀 Parallel Research Runner Guide — 20 Claude Desktop Instances

## Quick Start (5 minutes setup)

### Step 1: Open 20 Claude Desktop windows
Each window = one research track. Label them Track 01 through Track 20.

### Step 2: For EVERY window, paste the system context first
Copy the contents of `CONTEXT.md` and paste it as the first message in each Claude Desktop window. This gives Claude the project knowledge it needs.

### Step 3: Paste each track's prompt
Open the corresponding `track_XX_*.md` file, copy the **Prompt** section, and paste it into the matching Claude Desktop window.

### Step 4: Save results
As each Claude Desktop instance finishes, save its output to `results/XX_description.md`.

---

## Priority Order (if reviewing as they finish)

### 🔴 Phase 1 — Critical (read these first)
| Track | File | What it unlocks |
|---|---|---|
| 01 | `track_01_fairface_dataset.md` | data_ingestion.py |
| 03 | `track_03_data_validation.md` | data_ingestion.py |
| 04 | `track_04_predict_analysis.md` | PredictionsFileInterface |
| 05 | `track_05_jinja2_templates.md` | report/ package |
| 08 | `track_08_eu_ai_act.md` | Regulatory mapping |
| 09 | `track_09_fairlearn.md` | fairness/fairlearn_backend.py |
| 10 | `track_10_aif360.md` | fairness/aif360_backend.py |
| 11 | `track_11_bootstrap_ci.md` | fairness/statistics.py |
| 12 | `track_12_chi_squared.md` | fairness/statistics.py |
| 17 | `track_17_strategy_pattern.md` | fairness/base.py |

### 🟡 Phase 2 — Medium (read these second)
| Track | File | What it unlocks |
|---|---|---|
| 02 | `track_02_utkface_comparison.md` | UTKFace cut decision |
| 06 | `track_06_model_cards.md` | Report structure |
| 07 | `track_07_fairface_datasheet.md` | Report dataset section |
| 13 | `track_13_disparate_impact.md` | DIR implementation |
| 14 | `track_14_eod_eop.md` | EOD/EOP implementation |
| 15 | `track_15_shap_integration.md` | explainability.py |
| 18 | `track_18_pytest_patterns.md` | Test suite |
| 19 | `track_19_nist_rmf.md` | NIST compliance |
| 20 | `track_20_competitor_analysis.md` | Novelty defense |

### 🟢 Phase 3 — Low (read last)
| Track | File | What it unlocks |
|---|---|---|
| 16 | `track_16_proxy_detection.md` | Proxy analysis methodology |

---

## After All 20 Complete

### Implementation Order
With all research in hand, implement in this order:

1. `fairness/base.py` — Strategy pattern ABC (from Track 17)
2. `fairness/statistics.py` — Bootstrap CI + chi-squared (from Tracks 11, 12)
3. `fairness/fairlearn_backend.py` — Fairlearn implementation (from Track 09)
4. `fairness/aif360_backend.py` — AIF360 implementation (from Track 10)
5. `data_ingestion.py` — FairFace loading (from Tracks 01, 03, 04)
6. `report/generator.py` — Jinja2 report generation (from Tracks 05, 06, 07, 08)
7. `explainability.py` — SHAP integration (from Tracks 15, 16)
8. Tests — Full test suite (from Track 18)
9. Integration — WP5 orchestrator (from all tracks combined)

### Checklist
- [ ] All 20 results saved to `results/`
- [ ] UTKFace decision made (Track 02)
- [ ] Strategy pattern reviewed by both A and T (Track 17)
- [ ] Regulatory mapping validated against actual EU AI Act text (Track 08)
- [ ] Fairlearn vs AIF360 API differences documented (Tracks 09 vs 10)
- [ ] Bootstrap CI method chosen (BCa vs percentile) (Track 11)
- [ ] Multiple testing correction decided (Track 12)
