# Cross-Track Conflict & Discrepancy Log — BiasAperture 20-Track Research Sprint

Every conflict, discrepancy, and unresolved cross-track dependency found across Tracks 01–20. Nothing here is resolved — each item names the tracks that raised it and who needs to make the call. Ordered roughly by blocking severity.

## Blocking — needed before WP4 implementation starts

**1. Equalized-odds definitional mismatch between backends**
Fairlearn's `equalized_odds_difference` = max(TPR-gap, FPR-gap) (worst-case). AIF360's native `average_odds_difference`/`average_abs_odds_difference` = mean(TPR-gap, FPR-gap) — a *different statistic*, not an alternate implementation of the same one. Raised independently by **Tracks 09, 10, and 17**. Reporting AIF360's native value under the label `equalized_odds_difference` and diffing it against Fairlearn's output would flag a "divergence" that's actually just a definitional artifact. Track 10 proposes a manual max-based formula on AIF360's exposed TPR/FPR primitives as the fix, but this needs sign-off from whoever owns the divergence-flagging logic (Track 17 / WP4 integration owner), not a unilateral choice by either backend track.

**2. Disparate impact ratio — two incompatible formulas share the name**
AIF360-style: directional `P(favorable|unprivileged)/P(favorable|privileged)`, range 0→∞, requires an analyst-designated privileged group. Fairlearn-style: symmetric `min(rate)/max(rate)` across all groups, bounded [0,1], no reference-group designation. Raised independently by **Tracks 09, 10, 13, and 18**. Track 13 recommends reporting both a worst-case headline row (Fairlearn-style) and a full pairwise matrix as diagnostic detail, with a fixed lower/higher direction convention — but this is a proposal, not a lock, and needs the same Track 17/WP4 sign-off as #1.

**3. AIF360's `equal_opportunity_difference` is signed; Fairlearn's and the source paper's convention is unsigned**
Confirmed via live source execution (**Track 14**, empirically tested, not just read): AIF360 returns `TPR_unprivileged − TPR_privileged` (can be negative); Fairlearn/Hardt et al. use `max−min` (always ≥0). Numerically identical results (0.293 vs −0.293) will be **incorrectly flagged as a backend divergence** unless the AIF360 adapter applies `abs()` before storing `metric_value`. This is a concrete, easy-to-miss implementation bug waiting to happen if #1/#2's reconciliation work doesn't also catch this.

**4. `MetricResult`'s per-subgroup row shape doesn't fit cross-group scalar metrics**
EOD, EOP, and DIR are each inherently a *comparison across groups* (one number describing the spread), not a per-subgroup value — but the locked schema is one row per `subgroup`. Raised independently by **Tracks 11, 13, 14, and 18**, each converging on the same three candidate resolutions (single summary row / one-row-per-group-as-deviation-from-overall / one-row-per-pair) without picking one. **Recommend a single joint decision from whoever owns `fairness/base.py` (Track 17) and Track 13** — all four Core Four metrics need one consistent answer, not four ad hoc ones.

**5. n≥30 guard produces materially different numbers if applied inconsistently**
Empirically measured (**Track 14**): raw Fairlearn EOP on unfiltered 7-group FairFace data = 0.0422; the same data with sub-30 groups excluded first = 0.0143 — a 3× difference. Neither Fairlearn nor AIF360 has any native concept of the guard (**Tracks 09, 14** both confirm) — it must be applied to the input arrays *before* either library is called, not just filtered from the final report rows. This is a design requirement, not a live disagreement, but is listed here because getting the order wrong silently produces a materially wrong number, not an obviously-broken one.

## Needs owner decision — not blocking implementation start, but unresolved

**6. Zero-denominator DIR edge case has no schema field**
A well-sampled subgroup pair can still produce a mathematically undefined ratio (0/0) or an unrepresentable one (x/0 → ∞) — a different failure mode from the n<30 guard, which the locked `MetricResult` has no field for. **Track 13** proposes two non-conflicting options (overload `insufficient_sample`, or add a new field requiring M1 re-sync) without choosing. Schema owner call.

**7. Chi-squared p-value combination for equalized odds' two strata**
EOD requires two separate chi-squared tests (TPR-stratum, FPR-stratum); no convention exists yet for combining the two p-values (report both / take the more conservative / stratified CMH test). **Track 12** flags to **Track 14**; Track 14's own output doesn't resolve it either.

**8. Multiple-testing correction family boundary undecided**
**Track 12** implements Holm-Bonferroni (recommended over plain Bonferroni) but leaves open whether correction is applied per protected attribute or globally across all subgroups×metrics — changes what "significant" means in every downstream report row. Reporting/schema-semantics decision, Stream B territory.

**9. AIF360's privileged/unprivileged vocabulary risks leaking into the report**
There is no normatively "privileged" race group in a 7-category non-ordinal demographic-parity audit — AIF360's API forces this framing internally. **Track 10** flags for **Track 05/06 (report templates)** and **Track 08 (regulatory mapping)** to relabel as `subgroup`/`reference_group` at the report layer; not fixable inside the backend itself.

**10. Regulatory-tag storage mechanism undecided**
No field on `MetricResult` currently carries an EU Art. 10 sub-clause tag or a NIST subcategory tag. **Track 08** recommends a non-invasive static `metric_name → regulatory_tags` lookup table in `report/` over a new schema field (which would trigger the M1 re-sync process) but doesn't decide unilaterally. **Track 19** independently proposes an analogous `nist_subcategory` tag with the same open question.

**11. Article 10(5) "legal basis for special-category data processing" statement has no owner**
Not a Core Four metric, not the FairFace Datasheet, not Model Cards — falls through all 20 tracks' current scope division. **Track 08** flags it should become an explicit Track 05/06 report-scaffolding sub-item.

**12. `ExplanationResult` and "proxy attribution note" are new artifacts outside the locked schema**
Both **Track 15** (SHAP output shape) and **Track 16** (proxy-finding note) propose new result types that don't exist in `schema.py`'s `MetricResult`/`SubjectRecord`. Neither track adds them unilaterally — both explicitly flag for schema-owner sign-off before implementation.

**13. Dashboard "pass/fail" framing needs a design confirm, not just a build**
**Track 05** implements the dashboard as a scanning aid (grounded in the project's own four-fifths-rule critique) rather than a compliance verdict, but flags this as an interpretive convention needing a 5-minute confirm with Aaradhya/Tisha before `generator.py` is built for real — it is not part of the M1 schema lock.

**14. SHAP image format (PNG vs SVG) is an assumed contract, not a locked one**
**Track 05**'s template consumes a `dict[str, Path]` keyed `"{metric_name}::{subgroup}"` assuming PNG; **Track 15** confirms PNG is the right choice but if that changes, `image_to_data_uri`'s hardcoded MIME type needs a one-line fix — flagged so it isn't silently mismatched at integration.

## Documentation/data corrections needed (not architectural, but currently wrong in project docs)

**15. Reference checkpoint filename — CONTEXT.md/schema-lock-m1.md/model_interface.py docstring name the wrong file**
They cite `res34_fair_align_multi_7_20190809.pt`. Verified independently by **Tracks 01 and 04** (both read the live `dchen236/FairFace` source directly) that `predict.py` actually loads `fairface_alldata_20191111.pt` by default — the older filename only appears commented-out in the sibling `predict_bbox.py`. Both tracks agree on the finding; this is a doc-vs-reality gap, not a disagreement between tracks. Needs a decision: update docs to match reality, or confirm the older checkpoint is deliberately swapped in via the commented line, or empirically test whether the two checkpoints' predictions differ enough to matter.

**16. Dataset size — 108,501 (as cited everywhere) vs 97,698 (actual released train+val label files)**
**Track 01** found the gap; **CONTEXT.md**, the **acceptance-criteria doc** (4hr GPU runtime target), and **Track 03**'s own "full dataset (108,501 rows)" note all currently repeat the higher, apparently-incorrect figure. Track 01's best inference (not confirmed in the paper) is that 108,501 was the pre-annotation-discard count, not the released count. Any runtime/sizing target keyed to 108,501 is measuring against a number larger than what `data_ingestion.py` will ever actually see on disk.

**17. Preprocessing method — MTCNN (as named in the track-prompt/CONTEXT.md assumption) is wrong; the real pipeline is dlib**
**Track 07** flags the correction; **Track 04**'s independent, source-verified analysis already had it right (dlib CNN detector + `get_face_chips`) with no MTCNN dependency anywhere in the repo. No actual disagreement between the two tracks — just a stale assumption in project docs that both tracks' correct findings should be reconciled against.

**18. Two different "file path" columns exist and are not interchangeable**
`face_name_align` (an inference-time artifact `predict.py` generates fresh each run) vs. the officially released label CSVs' native path column (commonly `file`, per third-party sources — **Track 01** could not independently verify this byte-for-byte in this environment). Only matters if native label files are ever ingested directly instead of/alongside `predict.py` output — `model_interface.py` doesn't handle that second shape today.

## Process notes (not content conflicts — flagging for the record)

**19. Track/task-ID mismatches surfaced by the executors themselves**
**Track 17**'s report notes its run was framed as "Track 18" in the calling prompt, but the actual claimed task and prompt file were genuinely Track 17 (Strategy pattern) per the orchestrator's own spec. **Track 18**'s report independently notes the reverse — its run was framed as "Track 19" but the claimed task/file were genuinely Track 18 (pytest). Both trace to the same underlying prompt-labeling drift; this sprint's actual task board (verified via `list_tasks`) shows all 20 tracks 01–20 claimed and completed by the correct owners with no gap, so the content itself is not affected — flagged only so the labeling inconsistency in the original dispatch prompts doesn't get treated as a data problem.

**20. Naming-collision risk flagged proactively (not yet a real collision)**
**Track 03** proposes an ingestion-level `insufficient_sample_at_ingestion` flag (raw row-count check, pre-computation) and deliberately does *not* reuse `MetricResult.insufficient_sample` (a post-computation, statistically-gated flag) for it — flagging the distinction now so a future implementer doesn't collapse two different meanings into one name.

**21. Local constant duplication — drift risk, not yet a live conflict**
**Track 11**'s standalone bootstrap module redefines `_MIN_SUBGROUP_SAMPLE_SIZE = 30` locally rather than importing `schema.MIN_SUBGROUP_SAMPLE_SIZE`, by design (kept the research deliverable standalone/copy-pasteable). Explicitly flagged that whoever integrates this into `fairness/statistics.py` for real must import the schema constant, not carry a second copy forward.
