# Stream E Synthesis — Architecture & Testing (Tracks 17–18)

**Feeds:** `fairness/base.py`, `src/tests/fairness/` (WP4 integration + test suite) · **Tracks:** 17 (Strategy pattern), 18 (pytest patterns)

## `fairness/base.py` design (Track 17 — code delivered, ready for review)

- `FairnessBackend(ABC)` with a single abstract method `compute_metrics(records) -> list[MetricResult]`. `FairlearnBackend`/`AIF360Backend` are the two M1 concrete strategies; a third backend (e.g. a future in-house engine) requires zero change to the orchestrator — pure subclassing.
- **Shared helpers live in `base.py`, not duplicated per backend** (directly addresses the false-positive-divergence risk in Stream C): `subgroup_key()`, `subgroup_sample_sizes()`, `is_insufficient()`, `insufficient_result()`. Both concrete backends must call these rather than deriving `n` from their own library's internal grouping.
- **`CrossValidationOrchestrator`** is written N-way generic from the start (`Sequence[FairnessBackend]`, pairwise divergence loop over however many backends are passed) — adding a third backend later means subclassing + appending to a list, zero change to the orchestrator itself.
- **Per-metric divergence epsilon**, not one global float — `disparate_impact_ratio` (a ratio, ~0–1+, centered near 1) is not comparable on the same scale as the three difference metrics (bounded ~[-1,1]). Default: 0.05 for DPD/EOD/EOP, 0.10 for DIR. Orchestrator raises loudly (not silent skip) if a metric has no configured epsilon.
- Divergence detection distinguishes three cases: **missing on one side** (shape mismatch — worse than a numeric disagreement), **`insufficient_sample` disagreement between backends** (should be structurally impossible if both use the shared helpers — flagged as a backend bug if it ever fires, not a fairness finding), and **`|value_a − value_b| > epsilon`** (genuine numeric divergence).
- **Not implemented, explicitly flagged as open**: a "soft divergence" signal (point estimates agree, but the two backends' 95% CIs don't overlap at all) — would need a Track 11/12 call on how CI comparison should be defined before it's added.
- Bootstrap CI / chi-squared are **per-backend, not post-aggregation** — each backend computes its own CI/p-value from its own resampling over the same population, so the orchestrator can in principle catch "point estimates agree but confidence intervals don't" as a distinct signal (once the soft-divergence flag above is built).

## Track/field-name discrepancies Track 17 caught and worked around

- The calling prompt's field names (`n`, `point_estimate`) don't match the actual locked `schema.py` (`subgroup_sample_size`, `metric_value`) — Track 17's code uses the real locked names throughout; flagged so nobody wires code against the prompt's looser names.
- `subgroup` composite-key format (`race=Black&gender=Female`, `&`-joined) is a **proposal**, not a lock — `schema-lock-m1.md` explicitly leaves this open for WP4 sign-off.

## Test suite architecture (Track 18 — grounded against live repo state)

- Repo state at clone time: 14/14 tests passing, flat `src/tests/` layout, dev deps currently only `pytest`+`ruff` — **no `hypothesis`, `fairlearn`, or `aif360` yet**. `fairness/` and `report/` are docstring-only stubs. Recommend promoting to `src/tests/fairness/` subpackage once WP4 lands (not applied — research-only track).
- **Known-answer tests**: 8-record hand-computed block (4 White + 4 Black gender-classification outcomes) gives exact expected values — DPD=0.5, EOD=0.5, EOP=0.5, DIR=1/3 — replicated ×8 to clear n≥30 for the end-to-end gated path, with the raw n=8 block kept for a pure-math unit test that deliberately bypasses the gate.
- **Edge cases**: empty subgroup (n=0, never a `ZeroDivisionError`/`KeyError`), single-element subgroup, all-correct predictions (TPR=1.0/FPR=0.0 — valid, not an error), all-wrong predictions (full inversion — valid, not an error). Zero-actual-positives-in-subgroup (TPR=0/0, mathematically undefined) is `xfail`'d rather than assumed — explicitly an open design question for whoever owns `fairness/base.py`.
- **NFR-003 engine-level guard test**: distinct from the existing dataclass-level test (`__post_init__` already covers "can't construct a bad row"). This test verifies the backend never even *attempts* the statistical computation for n<30 — via `patch.object` + `assert_not_called()`, not just checking output shape (a compute-then-discard backend would pass an output-shape-only test while still wasting bootstrap cycles).
- **Bootstrap CI properties**: CI-contains-point-estimate (flagged as an expected property, not a mathematical guarantee — percentile-method CIs can technically exclude the point estimate for skewed/ratio metrics near a boundary; a DIR-specific flake here is evidence for Track 11's BCa-vs-percentile decision, not a bug in the test); CI-width-shrinks-with-n (with a 2pp stochastic tolerance, not exact monotonicity).
- **Cross-validation tests** (Fairlearn vs. AIF360 on identical input) and the divergence-flagging test are written against **anticipated APIs** (`fairlearn_backend`/`aif360_backend` fixtures, `base.run_dual_backend`) — none of `fairlearn_backend.py`, `aif360_backend.py`, or `base.py` exist as runnable code yet. Explicitly flagged as a forward spec for Tracks 9/10/17 to implement against, not currently passable.
- **56-case parametrized smoke matrix** (4 metrics × 7 races × 2 backends), each independently `pytest.mark.parametrize`-id'd so a single failing combination is immediately identifiable in CI output.
- **Property-based tests (Hypothesis)**: NFR-003 guard holds for any generated input; no NaN/Inf ever leaks into a `metric_value`; DPD/EOD/EOP are bounded [0,1] for any input (DIR is deliberately excluded from this bound — its directionality convention is undefined, see below). `hypothesis>=6.0` needs adding to `pyproject.toml` dev deps.

## Open flags requiring owner decision

1. `MetricResult.subgroup` pairing convention (vs.-global vs. vs.-privileged-group vs. vs.-pair) — **same cross-cutting flag raised independently in Stream C** by Tracks 11/13/14. Blocks finalizing the known-answer test's assertion shape.
2. Zero-actual-positive/negative subgroup behavior (0/0 TPR/FPR) — `xfail`'d, three candidate resolutions listed, none picked.
3. `disparate_impact_ratio` directionality (bounded-ratio vs. privileged/unprivileged ratio) — **same conflict as Stream C's DIR formula flag** — affects whether the property test's [0,1] bound applies to DIR at all.
4. Bootstrap method (percentile vs. BCa, Track 11's open item) affects whether the CI-containment property test can ever be a hard assertion.
5. `fairlearn`/`aif360`/`hypothesis` all need adding to `pyproject.toml` dev deps — none present yet.
6. Original run-level track/ID mismatch noted by Track 17 (labeled "Track 18" in one calling prompt, actually delivered Track 17 per the orchestrator's own spec) — resolved in this sprint's board (Track 17 = strategy pattern, Track 18 = pytest, both delivered separately, no gap) but flagged here for the record since Track 17's own output raised it.
