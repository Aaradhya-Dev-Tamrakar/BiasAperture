# Stream C Synthesis — Fairness Engine (Tracks 09–14)

**Feeds:** `fairness/fairlearn_backend.py`, `fairness/aif360_backend.py`, `fairness/statistics.py` (WP4) · **Tracks:** 09 (Fairlearn), 10 (AIF360), 11 (bootstrap CI), 12 (chi-squared), 13 (disparate impact ratio), 14 (EOD/EOP)

## Native library coverage — both backends need manual work for the same two metrics

| Core Four metric | Fairlearn | AIF360 |
|---|---|---|
| `demographic_parity_difference` | Native | Native (`statistical_parity_difference`) |
| `equalized_odds_difference` | Native (max-of-gaps) | **No exact equivalent** — native methods (`average_odds_difference`, `average_abs_odds_difference`) are mean-of-gaps, a *different statistic*, not an alternate implementation of the same one. Manual max-based formula required to match Fairlearn's definition (Track 10 §3.2). |
| `equal_opportunity_difference` | Manual (`MetricFrame` + `recall_score`, TPR-only) | Native, same name, same definition |
| `disparate_impact_ratio` | Manual (`MetricFrame.ratio()` on `selection_rate` — equivalent to `demographic_parity_ratio`) | Native (`disparate_impact()`) |

**This asymmetry is load-bearing for the dual-backend divergence feature** (see conflict log #3–#5) — reporting AIF360's native mean-based `average_odds_difference()` under the label `equalized_odds_difference` and diffing it against Fairlearn's max-based output would produce a "divergence" flag that reflects a definitional mismatch, not a genuine disagreement. Tracks 09, 10, and 17 all independently flag this — needs one reconciliation decision, not three.

## Multi-group handling — a real architecture asymmetry, not just an API-style difference

- Fairlearn's `MetricFrame`/`sensitive_features` natively accepts an n-category column (7 races, 9 ages) and reduces internally in one pass.
- AIF360 has **no native multi-group support** — every comparison is binary `privileged_groups`/`unprivileged_groups`. Covering 7 races requires 7 one-vs-rest `ClassificationMetric` instantiations (9 for age), with **no built-in reducer** across those passes — that reduction logic must be hand-written in `AIF360Backend`.
- Runtime-cost consequence: AIF360 needs N one-vs-rest passes per metric vs. Fairlearn's single pass — worth surfacing wherever the acceptance-criteria runtime budget (4hr GPU / 30min CPU) gets allocated across backends (Track 10 §6, Track 14 §7).
- **AIF360's privileged/unprivileged vocabulary must not leak into the report.** There is no normatively "privileged" race group in a demographic-parity audit — "everyone else" is a statistical reference group. Report layer should relabel as `subgroup`/`reference_group` (Track 10 §5 flag, for Track 05/06/08).

## n≥30 guard — computed once, shared, enforced before any library call

- `subgroup_sample_sizes()` must live in `fairness/base.py` and be called by **both** backends rather than each deriving `n` from its own library's internal grouping (Fairlearn/AIF360 group slightly differently at the edges — NaN handling, dtype coercion — which could produce a false-positive divergence for reasons that have nothing to do with fairness). Track 17 §1.1.
- **Neither library has any concept of the n≥30 guard.** Empirically confirmed (Track 14 §4b, live-executed): raw Fairlearn EOP on unfiltered 7-group data = 0.0422; same data with sub-30 groups excluded = 0.0143 — a **3× difference**, not a rounding artifact. The guard must pre-filter *before* calling either library, not just filter the final report rows.
- Empty/single-eligible-group and zero-positive-label edge cases are **handled inconsistently across libraries** (Track 14 §4a, §6, live-executed):
  - Zero-`n_pos` group: Fairlearn's `true_positive_rate` (via `sklearn confusion_matrix(normalize="true")`) silently returns `0.0`, **no warning**. AIF360 returns `NaN` with a `RuntimeWarning`. Neither is safe to pass through — `0.0` masquerades as a real perfect rate, `NaN` corrupts downstream bootstrap/chi-squared math.
  - Single eligible group: Fairlearn does not raise or return NaN — it silently returns that group's own rate as if it were a meaningful "difference." Must be guarded by BiasAperture's own wrapper, never delegated.
  - **BiasAperture must pre-filter with its own `compute_group_rates`-style logic before any library call, for both the n<30 case and the zero-positive-label case.**

## Bootstrap CI (Track 11) — locked implementation approach

- `scipy.stats.bootstrap`'s BCa mode is **unusable** for this project — scipy's own docs state BCa doesn't support multi-sample statistics, and every Core Four metric is a multi-sample (multi-group) statistic. Custom implementation on `numpy.random.Generator` required; `scipy.stats.norm` still used for the BCa percentile math itself.
- Default **BCa**, automatic fallback to **percentile** when the bias-correction or jackknife-acceleration term is degenerate (common near n=30) — never a manual toggle the caller has to remember.
- Stratified (within-subgroup) resampling is non-negotiable per the track's own requirement; resample-index generation is fully vectorized (one `rng.choice` per group), but per-resample metric evaluation is a genuine Python loop since Fairlearn/AIF360 functions aren't vectorizable across a resample axis.
- Jackknife-for-BCa is O(n) separately from the B=1,000 resample loop — for large subgroups this can dominate runtime; mitigated with a randomized delete-d jackknife above a configurable cap (default 500).
- Seeding: one `SeedSequence` per audit run, `spawn()`'d into independent child generators keyed by `(metric_name, subgroup)` — never reuse one literal seed across all 28+ calls (that would silently make every metric's resamples identical). Log the top-level seed in the report's methodology appendix.
- **n<30 returns `(None, None)` immediately, never a best-effort interval** — mirrors `MetricResult.__post_init__`.

## Chi-squared testing (Track 12) — locked implementation approach

- `chi2_contingency` (test of independence) is correct for all four metrics; `chisquare` (goodness-of-fit) is the wrong primitive — it answers a data-validation question, not a fairness question.
- Table construction per metric: DPD/DIR use all rows unconditional on `y_true`; EOP uses only `y_true==positive` rows; EOD requires **two separate tests** (TPR-stratum and FPR-stratum) whose p-values must be combined by some convention — **flagged to Track 14, not decided in Track 12.**
- Yates' correction (`correction=True`) safe to leave on unconditionally — only engages at dof=1 (gender axis), no-op elsewhere.
- Expected cell count < 5: 2×2 tables fall back to `fisher_exact` automatically. **r×c tables (race 2×7, age 2×9) have no exact-test fallback in the current scipy-only stack** — function emits a `UserWarning` instead; adding `statsmodels` or a permutation approximation is an open dependency decision, not resolved.
- Multiple-testing correction: **Holm-Bonferroni recommended over plain Bonferroni** (same FWER guarantee, uniformly more powerful — matters because excess conservatism in an audit tool directly means missed real disparities). The **family boundary** (per-attribute vs. global correction across all subgroups×metrics) is a reporting-semantics decision, not resolved here — changes what "significant" means downstream.
- p-value and bootstrap CI are **complementary, not redundant** — recommend the report layer flag any case where they disagree (CI excludes the null but χ² p≥α, or vice versa) as a "borderline/inconsistent" case, directly analogous to the existing backend-divergence pattern.

## Disparate Impact Ratio (Track 13)

- Two structurally different formulas both called "DIR": **AIF360-style** (directional, `unprivileged/privileged`, range 0→∞, requires an analyst-designated reference group) vs. **Fairlearn-style** (`min_rate/max_rate`, symmetric, bounded [0,1], no reference-group designation needed). Not interchangeable — see conflict log #4.
- **No principled "privileged" race group exists** for a 7-category non-ordinal axis. Recommendation: report **both** a worst-case min/max headline row (one number per audit, Fairlearn-native) and a full 21-pair pairwise matrix as supplementary diagnostic detail (direction convention: always lower-rate/higher-rate, bounded [0,1]) — avoids ever asserting a race is "privileged."
- Zero-denominator edge case (`0/0` undefined, or ratio→∞) has **no field in the locked `MetricResult` schema** — distinct failure mode from the n<30 `insufficient_sample` guard (well-sampled groups, mathematically undefined ratio). Two non-conflicting options flagged for the schema owner: overload `insufficient_sample` (simple but conflates two meanings) or add a new field (breaking change, requires M1 re-sync). **Not decided by this track.**
- Legal grounding: the four-fifths rule originates in 1972 California FEPC guidelines, federalized via 1978 UGESP (29 CFR 1607) — a Title VII enforcement screening heuristic, not a statistically derived fairness criterion. Watkins et al. 2022's "epistemic trespassing" critique is the project's own stated justification for never reporting DIR as a bare pass/fail — every row must carry the CI band relative to 0.8 (below / straddles / above), not just the point estimate.

## Equalized Odds / Equal Opportunity (Track 14 — empirically cross-validated, not just theoretical)

- Formal definitions per Hardt, Price & Srebro 2016; operational "difference" metric is `max−min` across groups (unsigned, matches Fairlearn's `between_groups` default and is the natural n-group generalization — mean-pairwise dilutes the worst-case signal, which is exactly the wrong thing for a bias-audit tool).
- **AIF360's `equal_opportunity_difference` is signed** (`TPR_unprivileged − TPR_privileged`, can be negative) while the paper's convention and Fairlearn's are **unsigned** (`max−min`, always ≥0). Confirmed via source inspection, not documentation. If BiasAperture's divergence check compares raw AIF360 output against raw Fairlearn output without `abs()`, numerically identical results (0.293 vs −0.293) get incorrectly flagged as a divergence. **AIF360 adapter must `abs()` before storing `metric_value`.**
- `equalized_odds_difference`'s "worse of TPR-gap/FPR-gap" convention loses information relative to Hardt et al.'s joint-equality definition — a system with TPR-gap=0.01/FPR-gap=0.30 scores identically to one with both gaps at 0.30. Confirmed identical between Fairlearn and the standalone implementation, so this is a fidelity gap from the source paper, not a backend divergence — worth documenting in the report methodology section regardless.

## Cross-cutting architectural flag (Tracks 11, 13, 14 all raise the same underlying question independently)

`MetricResult`'s row shape (one row per `subgroup`) doesn't map cleanly onto metrics that are inherently **cross-group** scalars (EOD/EOP: one number describing the spread across all groups; DIR: same issue). Three options observed, none picked by any track:
- (a) single summary row (`subgroup="ALL"`), simplest, loses which group pair drove the gap
- (b) one row per contributing group = deviation-from-overall (fits existing shape without a schema change, but changes what "the value for this subgroup" means)
- (c) one row per pair (most faithful, breaks the `subgroup` field's implicit single-group semantics elsewhere, ×21 rows per metric)

**Recommend one joint decision from whoever owns `fairness/base.py` (Track 17) and Track 13, before WP4 implementation starts** — all four Core Four metrics need one consistent answer, not four different ad hoc ones per metric.

## Open flags requiring owner decision

1. Equalized-odds cross-backend definitional reconciliation (mean-of-gaps vs. max-of-gaps) — blocks meaningful divergence flagging for this one metric.
2. EOD's two-stratum (TPR/FPR) chi-squared p-value combination convention.
3. `MetricResult` row-shape for cross-group scalar metrics (EOD/EOP/DIR) — one decision needed across three tracks.
4. Zero-denominator DIR edge case — new field vs. overloaded `insufficient_sample`.
5. Multiple-testing correction family boundary (per-attribute vs. global).
6. `_MIN_SUBGROUP_SAMPLE_SIZE` is redefined locally in Track 11's standalone module rather than imported from `schema.py` — integrator must import the real constant, not keep a second copy.
