# Stream A Synthesis — Data Pipeline (Tracks 01–04)

**Feeds:** `data_ingestion.py`, `model_interface.py` (WP2) · **Tracks:** 01 (FairFace profile), 02 (UTKFace comparison), 03 (validation patterns), 04 (predict.py source analysis)

## Locked findings (verified against primary source, safe to build on)

- **Output columns, exact order** (Track 01 + 04, cross-confirmed against real `test_outputs.csv` bytes and `predict.py` source):
  `face_name_align, race, race4, gender, age, race_scores_fair, race_scores_fair_4, gender_scores_fair, age_scores_fair`. `PredictionsFileInterface` correctly reads only `race`/`gender`/`age`/`face_name_align` + caller-specified label columns; extra columns are expected and safely ignored.
- **Both race models always run** (Track 04) — no `--race4` flag exists; `race`/`race_scores_fair` (7-way) and `race4`/`race_scores_fair_4` (4-way) are both computed every run. Consuming only `race` is correct.
- **Preprocessing pipeline** (Track 04, line-cited): dlib CNN face detector → 5-point landmark alignment → `get_face_chips(size=300, padding=0.25)` → torchvision resize to 224×224 + ImageNet mean/std normalize. **Not MTCNN** — Track 07 independently flagged the same correction from the datasheet side; both tracks agree, no conflict.
- **Model architecture:** ResNet-34, ImageNet-pretrained backbone, single 18-unit FC head sliced `[0:7]`=race, `[7:9]`=gender, `[9:18]`=age, three manual softmaxes over disjoint slices — not three separate heads.
- **Score columns are unparseable as-is:** `race_scores_fair` etc. are `numpy.ndarray.__str__()` reprs — space-separated, scientific notation, can contain embedded newlines. Not valid JSON, not CSV-list. `PredictionsFileInterface` doesn't touch these today (fine); any future confidence-weighted or SHAP-adjacent work needs a regex float-extraction parser, not `json.loads`/`ast.literal_eval`.
- **Zero-face images are silently dropped** by `detect_face()` (printed warning, row never written) — `data_ingestion.py` must reconcile input-row-count vs. output-row-count itself; `predict.py` gives no per-image success flag.
- **Multi-face images produce multiple rows** (`{basename}_face0/1/...`), each a legitimate independent `SubjectRecord`. No multi-label rows are possible by construction (argmax-only categorical output).
- **Race×gender distribution** (7×2, from Krishnapriya et al. 2020 reproducing FairFace's own released counts): race balanced 9–19% per group; gender skews 53% male / 47% female consistently across every race bucket. **Intersectional cells range 22 to 2,972 images** — a large fraction of the 126 race×age×gender cells will legitimately fall under n=30 and must show `insufficient_sample=True`, not compute — this is expected dataset shape, not a defect.
- **UTKFace recommendation: CUT** (Track 02, confirms cut-list Order #2). Reasons: only 3/7 FairFace race categories map cleanly (White/Black/Indian); Asian and Others each collapse two locked categories with no way to recover the split; DEX-based age labels are model-estimated (not independently human-annotated like FairFace), with documented weakest accuracy exactly in the 0–15 and 65–100 ranges — the same bins already fragile under the n≥30 guard; no official CSV (filename-embedded labels only); no train/val/test split. If overridden: restrict to White/Black/Indian only, run the real per-cell histogram before any disparity claim, add the missing bib entry regardless.

## Validation architecture (Track 03 — ready to implement against Track 01/04's confirmed column names)

- Two-pass, two-mode design: **strict/fail-fast** (mirrors existing `PredictionsFileInterface`) and **permissive/collect-all** (for exploratory profiling), both built on shared vectorized pandas validators so the two entry points can't drift.
- Missing-column check before any row-level work (`SchemaError`, not per-row).
- `.isin()` boolean-mask validation for race/gender/age against the locked label tuples; explicit handling for case/whitespace drift, race_4-vocabulary contamination, age-bin delimiter drift — flagged as policy decisions (normalize vs. reject), not silently resolved.
- NaN handling: `image_id` NaN is always a hard reject (can't join back to an image); demographic-field NaN may be recoverable. `pd.read_csv(na_values=[...])` must be explicit — a literal string `"nan"` in a cell is **not** caught by default `.isna()`.
- Duplicate `image_id` handling: exact-duplicate rows are safe to drop; same-id-different-values rows must always surface as an error, never silently `keep="first"`.
- Full dataset (~97,698 rows, see conflict log #1) fits in memory as one `pd.read_csv()` — no chunking needed at this scale.
- Stratified dev subset (n=5,000 target): proportional stratified sampling recommended as default (will show *more* `insufficient_sample` flags than the full run — expected, not a bug); fixed-per-cell sampling only if the dev subset is meant to validate the guard logic itself.
- Row→`SubjectRecord` conversion: keep `df.to_dict(orient="records")` (already what `model_interface.py` does) — fastest of the three pandas idioms at this scale, don't introduce `.itertuples()`/`.iterrows()` as a second pattern.
- New ingestion-level diagnostic flag proposed: `insufficient_sample_at_ingestion` (raw row-count check) — **deliberately not named** `insufficient_sample` to avoid colliding with `MetricResult`'s locked field, which means something more specific (a suppressed computed-metric row).

## Open flags requiring owner decision (not resolved by any track)

1. **Checkpoint filename mismatch** — see conflict log #1.
2. **108,501 vs 97,698 image count** — see conflict log #2.
3. **Two distinct "file path" columns** (`face_name_align` inference artifact vs. native label CSV's `file` column) — only matters if native label files are ever ingested directly; `model_interface.py` doesn't handle that shape today.
4. **Label normalization policy** (case/whitespace) before `.isin()` validation — affects what "matches the locked vocabulary" means.
5. **Strict/permissive unification** — whether `data_ingestion.py`'s validator and `model_interface.py`'s existing inline validation become one shared module or stay separate.
6. **Proportional vs. fixed-per-cell dev subset** — no locked doc specifies which.
7. **Intersectional counting at ingestion time** — explicitly deferred; `subgroup` composite-key format is unlocked until WP4 per `schema-lock-m1.md`.
