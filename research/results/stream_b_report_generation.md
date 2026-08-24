# Stream B Synthesis — Report Generation (Tracks 05–08)

**Feeds:** `report/` package (WP3) · **Tracks:** 05 (Jinja2 templates), 06 (Model Cards mapping), 07 (FairFace datasheet), 08 (EU AI Act mapping)

## Architecture (Track 05 — ready to implement)

- `report/generator.py` (data transform, filters) + `report/templates/report.html.jinja` (single authoring template, macro-based partials) + `report/static/report.css` (real file, inlined at render time). Output is one flat self-contained `.html` file — zero external `<link>`/`<script src>`, no CDN, no web fonts; SHAP PNGs base64-inlined via `data:image/png;base64,...`.
- `Environment(autoescape=select_autoescape(...), trim_blocks=True, lstrip_blocks=True)` — autoescape kept on even though `subgroup` values come from a locked vocabulary, as defense-in-depth.
- Row status buckets, in priority order: `insufficient_sample=True` → grey/muted, badge "— Insufficient sample"; `p_value < ALPHA` → red-tinted, "⚠ Disparity detected"; else → neutral, "✓ No significant disparity". `disparate_impact_ratio`'s fair point is **1.0, not 0** — ranking/deviation logic must use `abs(1.0 - value)` for DIR specifically, not a shared `abs(value)` across all four metrics.
- Dashboard "pass/fail" is explicitly designed as a **scanning aid, not a compliance verdict** (grounded in the project's own Watkins et al. 2022 four-fifths-rule critique, already in the lit review) — full per-subgroup detail stays one scroll away. **Flag: this framing needs a 5-minute confirm with Aaradhya/Tisha before `generator.py` is built for real** — it's an interpretive convention, not part of the M1 schema lock.
- Regulatory-tag interface contract (consumed from Track 08, not authored in Track 05): `RegulatoryMap = dict[metric_name, list[{"article": str, "note": str}]]`. Stub content in Track 05's example must not ship — needs Track 08's verified clause text first.
- SHAP interface contract (consumed from Track 15): `dict["{metric_name}::{subgroup}" -> Path]`, PNG only, one slot per significant+sufficient-sample row. If Track 15 lands on SVG, `image_to_data_uri`'s MIME type needs a one-line change.

## Model Cards mapping (Track 06 — Mitchell et al. 2019, 9 sections)

- **Model Details / Intended Use**: no `MetricResult` source — static "audit run context" object (model name/version/date/org/license) must be threaded into the Jinja2 context by WP5's orchestration layer; **not a schema.py change.**
- **Factors**: directly the locked `RACE_LABELS`/`GENDER_LABELS`/`AGE_LABELS` — auto-populated.
- **Metrics**: Core Four + justification (Hardt et al. for EOD/EOP, Watkins et al. for DIR-never-bare-ratio) + CI methodology (NFR-002) + significance (NFR-001). No hard-coded pass/fail decision thresholds in the diagnostic output itself.
- **Evaluation Data**: defers to the FairFace Datasheet (Track 07) rather than re-deriving it; realized per-subgroup n comes from `MetricResult.subgroup_sample_size` rollup.
- **Training Data: explicit stated N/A** — BiasAperture never trains/retrains anything; must render as a stated section with reasoning, not be omitted (an omitted section reads as an oversight, not a scope boundary).
- **Quantitative Analyses**: near-total mechanical mapping to the full `MetricResult` list, split unitary (single-axis) vs. intersectional (composite key) — matches the paper's own split. Backend-divergence flag is additive rigor beyond the paper's spec.
- **Ethical Considerations / Caveats**: synthesis sections — surface which rows have `p_value < ALPHA`; note the Kurian et al. 2024 proxy-feature caveat (race-category "worse performance" isn't provably the demographic label itself); disclose known limitations honestly (snapshot-in-time, insufficient-sample ≠ evidence of fairness, backend divergence needs investigation before citing either number).
- **Build-vs-buy verdict on `model-card-toolkit`: don't use it.** TFX/MLMD-coupled, pulls in dependencies with a history of version-pinning conflicts, no recent releases, and its default template doesn't know about EU AI Act tagging, dual-backend divergence, or `insufficient_sample` semantics — would need overriding anyway. Custom Jinja2 (Track 05's approach) is the one and only rendering mechanism for both the Model Card section and the rest of the report.

## FairFace Datasheet (Track 07 — Gebru et al. 2018/2021 framework, drafted)

- Motivation, funding (NSF SMA-1831848 + Hellman Fellowship + UCLA), composition (108,501 images — see conflict log #2), collection (YFCC-100M / Flickr CC BY + CC BY-SA only, demographically-adaptive incremental sampling, 50×50px min face size), annotation (3-AMT-worker majority vote, re-panel on disagreement, discard on second failure, model-assisted re-verification) all drafted and ready.
- **Consent gap, stated plainly**: no consent process involving the photographed individuals — only transitive consent via the original Flickr uploader's CC license choice. Structural to every YFCC-100M-derived face dataset, not unique to FairFace. Narrows but doesn't eliminate exposure for BiasAperture's diagnostic-only use.
- **Labels are perceived, not self-identified** — report copy should consistently say "perceived race/age," never bare "race/age," when labeling `MetricResult` rows for a non-technical reader.
- **Reference-classifier's own documented disparity is citable**: 92.8% (White) vs. 63.9% (non-White) race-accuracy on FairFace's own external validation tables. Worth stating explicitly in the benchmark-classifier limitations section — the very model BiasAperture audits is self-documented by its creators as exhibiting the kind of disparity the tool is built to detect.
- **Distribution risk**: hosted as bulk Google Drive archives, not a versioned registry — linkrot risk. Ingestion docs should record the exact archive checksum/date pulled.

## EU AI Act Article 10 mapping (Track 08 — sub-clause level, ready to consume)

- **10(2)(f) bias examination** → all four Core Four metrics jointly. **10(2)(g) detect/prevent/mitigate** → BiasAperture satisfies only the *detect* half by explicit design; report must say so, not imply full coverage.
- **10(3) statistical adequacy** → this is what the n≥30 guard and ≥1,000-resample bootstrap CI *evidence*, not apologize for.
- **10(4) context-specific characteristics** (domain shift) → no BiasAperture metric measures this; needs a caveat paragraph, not a metric — deployer must independently assess whether their population matches FairFace's.
- **10(5) legal basis for processing special-category data** → **currently unowned across all 20 tracks.** Not a Core Four metric, not the Datasheet, not Model Cards. Recommend an explicit sub-item of Track 05/06 report scaffolding.
- Annex IV §2(g) is the clause the entire detection engine (WP4) exists to satisfy; §5 (risk management) and §9 (post-market monitoring) are explicitly out of scope for a point-in-time diagnostic tool — state as a deliberate, documented boundary, not a silent omission.
- No schema.py field currently carries a per-row Art. 10 sub-clause tag. Recommended non-invasive path: a static `metric_name → regulatory_tags` lookup table maintained in `report/`, not a new `MetricResult` field (which would require the M1 re-sync process).

## Open flags requiring owner decision

1. Dashboard pass/fail framing as scanning-aid — needs Aaradhya/Tisha 5-min confirm (Track 05).
2. Art. 10(5) legal-basis statement has no owner across all 20 tracks — recommend folding into Track 05/06 scaffolding.
3. Regulatory-tag storage: static lookup table (recommended, non-invasive) vs. new `MetricResult` field (breaking, needs re-sync) — Track 08 does not decide unilaterally.
4. SHAP image format/keying guarantee (PNG vs SVG) — Track 15 dependency.
