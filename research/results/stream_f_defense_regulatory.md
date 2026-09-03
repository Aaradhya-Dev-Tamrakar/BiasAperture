# Stream F Synthesis — Defense & Regulatory (Tracks 19–20)

**Feeds:** novelty defense doc, report methodology/limitations sections · **Tracks:** 19 (NIST AI RMF mapping), 20 (competitor analysis)

## NIST AI RMF mapping (Track 19)

- Four functions: **Govern** (org policy/accountability, cross-cutting), **Map** (context/representativeness), **Measure** (TEVV — where BiasAperture's actual output lives), **Manage** (mitigate/accept/document residual risk, consumes Measure's output).
- **Core Four → Measure 2.11** (fairness/bias evaluated and documented) primarily, each with a distinct secondary tie: EOD also touches Measure 2.3 (performance under deployment-like conditions, since it spans both error types); EOP's validity is conditional on Measure 2.2 (representativeness) — directly why the n≥30 guard exists; DIR doubles as a Govern 1.1 input given its direct legal referent (four-fifths lineage).
- **The n≥30/`insufficient_sample` guard is a direct structural realization of Measure 1.1** — NIST requires risks that can't be measured for a given case to be properly documented, not silently omitted. `insufficient_sample=True, metric_value=None` *is* that documentation obligation encoded as a dataclass invariant — a stronger NIST-alignment claim than "we used a sensible threshold," worth stating explicitly in the report methodology.
- Dual-backend divergence flagging is analogized to Measure 1.3 (independent assessors) — **flagged explicitly as an analogy, not a literal fit**: 1.3 is written for human reviewers, not two software implementations of the same metric family. Report should say "in the spirit of Measure 1.3," not claim direct subcategory satisfaction.
- SHAP → Measure 2.9 (explainability) directly, and supports Measure 2.11 indirectly (distinguishing a real disparity from a Kurian-et-al.-style proxy artifact is itself a documentation-quality requirement).
- **Real divergence between frameworks, not just phrasing**: NIST's Manage function explicitly allows "accept" as a valid response with documented residual risk; Art. 10 compliance in a legal sense generally does not treat unmitigated bias as a valid closing state for a high-risk system. Report must not imply the two frameworks converge here.
- **Scope-boundary finding (load-bearing, not in the original track prompt's 5 items)**: BiasAperture only instruments the **Measure** function. It produces *inputs* consumable by Map and Manage via its report artifacts but does **not** perform Govern (org policy) or Manage (mitigation decisions) itself — mirrors the project's own diagnostic-only boundary. Draft compliance statement (Track 19 §5) explicitly states "no claim of NIST AI RMF compliance is made," consistent with the framework's voluntary, non-certifiable nature — recommend using this wording verbatim rather than looser language elsewhere in the report.
- NIST is increasingly referenced by regional AI law as a benchmark for reasonable care (e.g. Colorado AI Act treats NIST/ISO 42001 alignment as an affirmative defense) — a defense-framing point independent of EU AI Act exposure, useful for a US-context reader.

## Competitor analysis (Track 20 — 7 tools surveyed, live-verified)

| Tool | Face/7-race ingestion | Computes Core Four | Bootstrap CI + χ² | Regulatory mapping | Compliance report | SHAP | 2026 status |
|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| Aequitas | ✗ | ✗ (own rate/ratio family) | ✗ | ✗ | ✗ plots only | ✗ | Active |
| FairTest | ✗ | ✗ (own metric family) | Partial | ✗ | ✗ bug report | ✗ | Dead (Py2, ~2017) |
| Google What-If Tool | ✗ | ✗ interactive only | ✗ | ✗ | ✗ dashboard only | ✗ | Stagnant (sibling active) |
| FairSight | ✗ | ✗ ranking metrics | ✗ | ✗ | ✗ | ✗ | Unmaintained research prototype |
| FAT Forensics | ✗ | ✗ own implementations | ✗ | ✗ | ✗ library only | ✗ (own module) | Active, low-velocity |
| Themis-ML | ✗ | ✗ own metrics | Partial | ✗ | ✗ | ✗ | Effectively unmaintained |
| JFAM (Algorithm Audit) | ✗ | ✗ *different paradigm by design* | Partial | ✗ | Partial | ✗ | **Active, real-world deployed** (Dutch govt audit, 250k+ students) |
| **BiasAperture (M1 lock)** | ✓ | ✓ dual-backend cross-validated | ✓ | ✓ | ✓ | ✓ | In development |

- **No competitor combines more than one or two of the five differentiators** — face-native ingestion at this exact granularity, named cross-validated Core Four, statistical rigor as a hard guard, regulatory-mapped output, SHAP wired via a Strategy pattern to flagged disparities specifically. The claimed contribution is the **combination**, not inventing any single piece.
- **Honest, non-dismissive framing recommended**: several surveyed tools are more mature or more real-world-deployed than a capstone project will be — JFAM in particular is already in production for a government audit; BiasAperture is not. The defensible claim stays narrow: *no existing tool bridges FairFace-scale face-classifier output to a regulatory-mapped, dual-backend, statistically-guarded compliance report in one pipeline.*
- **JFAM's unsupervised/unlabeled-group paradigm is a genuine limitation of any fixed-taxonomy tool, BiasAperture included** — it can surface disparities in groupings a fixed 7-race/2-gender/9-age schema cannot, by construction. Recommend a one-paragraph Limitations note in the final report naming this honestly, rather than the defense implying strict superiority.
- Aequitas's rate/ratio framework and Themis-ML's mitigation scope are legitimately different design goals, not omissions — avoid defense language that implies these tools are simply worse.

## Open flags requiring owner decision

1. `nist_subcategory` tag on report rows, parallel to Track 08's `eu_ai_act_article` tag — additive to the report layer, not `schema.py`; a WP3/WP5 template decision, not decided here.
2. Report copy must distinguish "NIST-informed" from "EU AI Act Article 10 compliance evidence" — conflating a voluntary-framework alignment claim with legal-obligation evidence is a defense-framing risk, flagged for whoever finalizes report boilerplate.
3. JFAM limitation note — narrative-only, Stream B/report-owner territory, not a schema change.
