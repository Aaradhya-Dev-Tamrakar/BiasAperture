# Track 20 — Competitor Deep Analysis
**Stream:** F (Defense) · **Priority:** 🟡 Medium · **Owner Focus:** Both
**Estimated Time:** 45 min · **Feeds:** Novelty defense, literature review

## Instructions
1. Paste `CONTEXT.md` into Claude Desktop first
2. Then paste the prompt below
3. Save the output as `results/20_competitor_analysis.md`

## Prompt

Perform a deep competitive analysis of existing fairness/bias audit tools against BiasAperture. For each tool below, document:
1. What it does (actual capabilities, not marketing)
2. Can it ingest face-classifier predictions with multi-valued demographics (7 race groups)?
3. Does it compute all 4 of: DPD, EOD, EOP, DIR?
4. Does it provide bootstrap CIs and chi-squared p-values?
5. Does it map metrics to regulatory requirements (EU AI Act, NIST RMF)?
6. Does it generate compliance reports?
7. Does it integrate SHAP explainability?

Tools to analyze:
- **Aequitas** (DSSG, University of Chicago)
- **FairTest** (Columbia University)
- **Google What-If Tool**
- **FairSight** (visual analytics)
- **FAT Forensics**
- **Themis-ML**
- **JFAM** (Algorithm Audit, Stanford AI Audit Competition 2023)

Output a comparison matrix (tool × capability) and a "gap analysis" showing what BiasAperture uniquely provides.
