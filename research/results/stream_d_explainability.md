# Stream D Synthesis — Explainability (Tracks 15–16)

**Feeds:** `explainability.py` (FR-005) · **Tracks:** 15 (SHAP integration), 16 (proxy variable detection)

## SHAP variant selection (Track 15)

- **PartitionExplainer as default** — model-agnostic, black-box (only needs `f(images) -> probs`), works identically whether the audited model came in via `InProcessInterface` or `PredictionsFileInterface` re-wrapped as a scoring function. This matches the project's existing black-box-friendly design bias (`PredictionsFileInterface` is the non-negotiable cut-list core).
- **GradientExplainer as opt-in fast path** when `InProcessInterface` + a real PyTorch object is available — much faster (seconds vs. tens of minutes at scale) but requires direct tensor/autograd access, so it cannot be used against predictions-file-only audits.
- **DeepExplainer deprioritized** — known hook-compatibility issues with in-place ReLU/BatchNorm patterns in modern `torchvision.models.resnet34`; SHAP's own docs steer new PyTorch image work away from it.
- Realistic volume is bounded by flagged `MetricResult` rows × a bounded seeded sample per subgroup (Track 15 recommends k=min(n,20)), **not** the full 108,501-image corpus — keeps even the slow CPU path tractable. Runtime estimates in Track 15 §1 are engineering estimates, **not benchmarked** — flag for empirical validation once real hardware is available.

## Trigger point and interface (Track 15)

- SHAP runs as a **post-processing step on the detection engine's output**: `MetricResult` rows → filter by an upstream `is_flagged` predicate (owned by fairness-engine/report-generation logic, not this stream) → `ExplainerBackend.explain_subgroup(...)`.
- Proposed `ExplanationResult` dataclass (image_id, subgroup, task_head, predicted_class, shap_values, base_value, backend, png_path) is **explicitly not a `schema.py` edit** — needs schema-owner sign-off before implementation.
- Proposed `ExplainerBackend` ABC is meant to mirror `FairnessBackend`'s Strategy pattern but **needs reconciliation with Track 17's actual ABC conventions**, not independent implementation.
- Visualization: `shap.plots.image` → matplotlib figure → base64 PNG for Jinja2 embedding. **PNG over SVG** — the heatmap layer is rasterized regardless of container format; SVG buys nothing but text crispness.

## Proxy variable detection methodology (Track 16 — builds on Track 15's SHAP primitives)

- Two complementary signals: (1) **attribution-shift** — compare spatial distribution of high-SHAP-attribution pixels between a flagged subgroup and the general population; systematic shift toward demographically-correlated regions (skin, hair) rather than task-relevant regions (eyes, nose structure) is the proxy signature. (2) **corroborating objective signal** — Individual Typology Angle (ITA, a CIELAB-derived colorimetric skin-tone measure) computed independently within the segmented skin region, checked for the same subgroup difference. Agreement between the two independent signals (mirroring the project's own dual-backend cross-validation philosophy) is stronger evidence than either alone.
- **Prerequisite**: only run on subgroups already passing `insufficient_sample=False` (n≥30) — reuses the existing guard rather than a separate threshold.
- Pipeline: DeepSHAP/GradientSHAP (not KernelSHAP — intractable at image resolution) → per-image maps for flagged subgroup + comparison set → **pretrained face-parsing segmentation** (e.g. BiSeNet-style, off-the-shelf, no custom training needed) reduces raw pixel maps to per-region SHAP-mass vectors (raw pixel diffing is too high-variance at n≥30) → reuse the **same bootstrap-CI machinery already locked for the Core Four metrics** (≥1,000 resamples, α=0.05) on the per-region difference, rather than inventing a second statistical convention → task-relevance sanity check (occlude the flagged region, confirm it doesn't meaningfully affect task-label accuracy independent of subgroup) before calling a region a genuine proxy candidate.
- **Reporting anchor**: Article 13 (transparency — explains *why* a subgroup diverges, not just that it does) and Article 15 (accuracy/robustness — reliance on a race-correlated pixel region is itself a robustness weakness, independent of whether it also produces a fairness disparity, worth stating as its own finding). Reuses Track 08's Art. 10 tag set rather than inventing a second regulatory taxonomy.

## Real limitations — must be in the report, not just the code (Track 16 §5)

1. **Theoretical impossibility result** (Bilodeau et al. 2022): any attribution method that is both complete and linear — which SHAP and Integrated Gradients both are — cannot reliably distinguish local effects or spuriousness of features beyond random guessing, for any nontrivial model class. This is a structural limitation of the method family, not an implementation bug.
2. **Adversarial defeat is demonstrated**, not hypothetical — published attacks craft classifiers that remain highly discriminatory while off-the-shelf LIME/SHAP fail to flag the protected-attribute-correlated features, with SHAP values for the protected feature driven effectively to zero. No claim BiasAperture's audited models are adversarial, but the report must not overstate what "no SHAP signal" proves.
3. **Credit-splitting**: when a proxy signal is jointly carried by multiple correlated regions (skin tone *and* hair texture), Shapley's fair-division property splits credit across them — individual region attribution can fall below significance even though the sum clearly wouldn't. Region-level aggregation partially mitigates but doesn't eliminate this; joint multi-region testing flagged as future work, not built.
4. **Recommended report framing**: state a positive finding as "candidate proxy channel identified" (actionable), and an absence as "no proxy channel identified under this method" — never "confirmed absence of proxy reliance." Matches Article 13's own disclosure requirement for known method blind spots.

## Open flags requiring owner decision

1. `ExplanationResult` schema — needs sign-off before any `schema.py`-adjacent field is added.
2. `ExplainerBackend` ABC needs reconciliation with Track 17's actual `FairnessBackend` conventions, not parallel independent design.
3. Sampling seed convention (k=20 per subgroup) needs to align with Track 11's bootstrap seeding convention — not yet locked anywhere.
4. Face-landmark/parsing-network dependency (for region segmentation) is not currently in the tech stack (`CONTEXT.md`) — new dependency decision, not made here.
5. A "proxy attribution note" is a new report artifact not present in `schema.py`'s `MetricResult` — needs explicit re-sync before implementation touches the schema.
6. Runtime benchmarks in Track 15 §1 are estimates only — flag for empirical validation before treating as a capacity-planning number.
