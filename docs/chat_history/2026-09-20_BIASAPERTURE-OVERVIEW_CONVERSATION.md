# BiasAperture Overview

- **Source URL:** [https://chatgpt.com/share/6aafec97-2958-83e8-bd65-91a0c6798a6a](https://chatgpt.com/share/6aafec97-2958-83e8-bd65-91a0c6798a6a)
- **Archived Date:** 2026-09-20
- **Total Turns:** 86

---

## Turn 1

### User

Original custom instructions no longer available

---

## Turn 2

### User

https://github.com/Aaradhya-Dev-Tamrakar/BiasAperture
Eval

### Assistant

I’ll assess the repository at its current public state, focusing on research substance, reproducibility, engineering quality, evidence, documentation, and how convincingly the project presents itself.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

The output of this plugin was redacted.

---

### Assistant

# BiasAperture — current evaluation

I inspected the current `main` branch, including the repository structure, implementation, tests, generated reports, specifications, claim ledger, and recent commit history. The repository is substantially more mature than a typical student project, but I found several **important statistical and evidence-integrity problems** that matter because the project presents itself as a fairness auditing framework.

The public repository currently shows **223 commits**, a very substantial documentation/specification surface, and the README claims M1–M4 complete, M5 at 95%, and 78/78 tests passing. 

## Overall assessment

| Dimension | Assessment |
|---|---:|
| Problem framing | **8.5/10** |
| Architecture / modularity | **8.0/10** |
| Data validation | **8.5/10** |
| Testing breadth | **7.5/10** |
| Statistical validity | **5.5/10** |
| Explainability implementation | **5.5/10** |
| Empirical validation | **6.5/10** |
| Reproducibility / evidence discipline | **6.5/10** |
| Documentation / presentation | **9.0/10** |
| Repository engineering | **8.0/10** |

### My overall score: **7.2/10**

That is a **strong capstone/research-engineering artifact**.

It is **not yet safe to characterize the current implementation as a fully audit-grade statistical fairness engine**. The core architecture is good; the main weakness is that some of the statistical evidence attached to the metrics is stronger in the documentation than in the actual implementation.

---

# What is genuinely strong

## 1. The project has a coherent identity

The strongest aspect is that BiasAperture is not presented as “we trained a classifier and measured accuracy.”

The repository has a clear architecture:

**input → schema validation → fairness computation → statistical evidence → explainability → standalone report**

That separation is visible throughout `src/bias_aperture/`, and the repository has corresponding specifications, research records, reports, tests, and presentation material. The project also explicitly limits itself to **diagnosis/evaluation rather than model retraining or debiasing**, which is a good scope boundary. 

The explicit engineering-novelty framing is also intellectually healthier than pretending that DPD, EOD, EOP, DIR, BCa, or SHAP are themselves novel.

---

## 2. The schema and ingestion layer are quite good

The locked `SubjectRecord` / `MetricResult` contracts, fixed FairFace taxonomies, duplicate detection, strict/permissive validation, cohort profiling, and the `n < 30` guard show real software-engineering thinking.

In particular, this pattern is good:

> insufficient evidence → `metric_value=None`

rather than:

> insufficient evidence → fabricate a number anyway

That is exactly the sort of invariant a measurement system should have.

The data-ingestion tests are also much more comprehensive than the average academic prototype.

---

# The major problems

## 3. The biggest issue: the statistical p-values are not metric-specific

This is the most important problem in the repository.

`compute_contingency_chi2()` builds a contingency table from:

**predicted label × demographic group**

It does **not use `y_true` at all**.

That is reasonable for a demographic-parity/selection-rate independence test.

It is **not an appropriate significance test for Equal Opportunity Difference or Equalized Odds Difference**, because those are explicitly conditional on the ground-truth class.

Fairlearn defines equalized odds in terms of **TPR and FPR**, both of which depend on `y_true`. 

Yet the backend computes one `chi2_p` and reuses it for the DPD, EOD, EOP and DIR summary rows.

Conceptually, the current pipeline is doing something like:

```text
prediction vs demographic group
              ↓
          one p-value
              ↓
    ┌────┬────┬────┬────┐
    DPD  EOD  EOP  DIR
```

That is not statistically equivalent to testing four different hypotheses.

### What it should do

At minimum:

```text
DPD → selection-rate/group association test

EOP → TPR-by-group test
      i.e. condition on Y=1

EOD → separate TPR and FPR disparity evidence
      + multiplicity adjustment

DIR → selection-rate ratio with its own uncertainty/evidence
```

This is a **P0 correction**.

---

# 4. Your BCa claim is stronger than your implementation

The statistics module describes itself as a BCa bootstrap engine, but there are two distinct issues.

### Summary rows

The generic bootstrap routine does perform stratified resampling and attempts BCa correction.

However, for large samples it switches from ordinary leave-one-out jackknife to:

> delete-d / subsampled jackknife

with roughly 100 jackknife blocks.

That is not the textbook ordinary BCa acceleration calculation, and I do not see a documented correction establishing that this approximation is equivalent to the required BCa acceleration estimate.

Since your real report contains **N=10,954**, the large-`n` branch is directly relevant to the actual case study.

### Per-subgroup rows

This is more serious.

The subgroup CIs in `backends.py` are simply:

```python
max(0.0, metric - 0.05)
min(1.0, metric + 0.05)
```

Those are not bootstrap confidence intervals.

So the project currently has:

```text
summary metric → bootstrap CI
subgroup metric → ±0.05 heuristic interval
```

while the documentation describes a more uniform statistical treatment.

That should be fixed before calling the report's uncertainty layer rigorous.

---

# 5. Holm-Bonferroni is implemented, but apparently not actually applied

The function:

```python
holm_bonferroni_correction(...)
```

exists and is tested.

That is good.

But I did not find the backend pipeline actually applying the correction to the generated `MetricResult.p_value` values.

So there is a difference between:

**“we have implemented Holm correction”**

and:

**“the reported hypothesis tests are FWER-adjusted.”**

For an intersectional fairness auditor, that distinction matters substantially.

This should become part of the actual result-generation pipeline, with something like:

```text
raw p
adjusted p
hypothesis family
adjustment method
```

in the result artifact.

---

# 6. There is a subtle but important error in the AIF360/Fairlearn novelty argument

This one is particularly worth fixing because it affects the **research claim itself**.

The repository's Claim Ledger argues that AIF360's “native Equalized Odds Difference” uses an average-gap formulation and therefore differs from Fairlearn's max-gap formulation.

However, the current AIF360 documentation distinguishes:

- `equalized_odds_difference()` → **greater of the absolute TPR and FPR differences**
- `average_odds_difference()` → **average of the TPR and FPR differences**

That is explicit in AIF360's current documentation. 

So the repository appears to be conflating:

```text
AIF360 average_odds_difference()
```

with

```text
AIF360 equalized_odds_difference()
```

Your own test is actually testing the **average-odds** formulation, not demonstrating that AIF360's `equalized_odds_difference()` itself differs from Fairlearn.

This matters because one of your central “backend harmonization” arguments is built around that distinction.

### This should be rewritten

The defensible statement is closer to:

> AIF360 exposes multiple odds-related metrics with different aggregation conventions; BiasAperture explicitly selects and normalizes a common max-gap contract.

That is materially more accurate than saying the two libraries inherently disagree about what `equalized_odds_difference` means.

---

# 7. “Dual backend” is not actually guaranteed to mean two independent implementations

This is probably the most important engineering flaw after the p-values.

`AIF360Backend` catches **any exception** during AIF360 execution and falls back to:

```python
FairlearnBackend()
```

Then the object still exists as the AIF360 backend in the orchestrator.

That can produce:

```text
Fairlearn backend → value X
AIF360 backend → fallback to Fairlearn implementation → value X
```

and the orchestrator can interpret that as:

> perfect cross-backend consensus

when there was actually **only one computational implementation**.

That makes the apparent consensus evidence misleading.

### Correct behavior

Use something like:

```text
AIF360 available → execute AIF360

AIF360 unavailable → backend status = unavailable

Never:
AIF360 unavailable → silently pretend consensus
```

Then the report can explicitly say:

```text
Backend consensus: unavailable
Reason: AIF360 dependency/runtime failure
```

That is much stronger audit engineering.

---

# 8. SHAP is currently overstated

The explainability module has a real surrogate attribution implementation, which is useful.

But there is a documentation/code mismatch.

When no `records` are provided, the code effectively does:

```python
import shap
```

and then returns text saying:

> “Targeted SHAP PartitionExplainer attribution generated”

It does **not actually instantiate and execute `PartitionExplainer` in that branch**.

When records are provided, the code instead performs a logistic-regression surrogate attribution:

```text
demographic one-hot features
        ↓
LogisticRegression
        ↓
w * (x - E[x])
        ↓
"Shapley" attribution
```

So the honest description of the current implementation is:

> **demographic surrogate feature attribution inspired by additive Shapley decomposition**

not:

> full SHAP image explainability.

Your own documentation is partly aware of this—the current specs explicitly say image-native/spatial SHAP is deferred. That is good. The code and claim ledger should be made equally strict.

---

# 9. The model interface is architecturally present but operationally incomplete

`InProcessInterface` is still:

```python
raise NotImplementedError(...)
```

The actual CLI does not consume the abstract model interface for inference. It primarily consumes a predictions file.

So the current operational system is:

```text
CSV / JSON predictions
        ↓
    BiasAperture
```

not:

```text
PyTorch / TensorFlow model
        ↓
ModelInterface
        ↓
BiasAperture
```

That distinction matters because the README and architecture discuss model-agnostic auditing much more broadly.

The repository should either:

1. implement real model adapters, or
2. explicitly narrow the current claim to **predictions-file auditing**.

The second option would be perfectly defensible for a capstone.

---

# 10. “Intersectional support” is stronger in the data layer than in the execution layer

You have:

- race × gender cohort profiling
- `OvRTransformer`
- intersectional sample-size tracking

That is good infrastructure.

But the actual CLI's `--protected-attr` choices are:

```text
race
gender
age
```

There is no direct CLI path like:

```text
race × gender
```

through the fairness engine.

So I would describe the current state as:

> **intersectional cohort profiling infrastructure exists**

rather than:

> **the complete intersectional fairness audit pipeline is operational**

That distinction will matter during defense.

---

# 11. Requirements traceability has drifted

This is another sign that the repository has grown faster than the verification layer.

The current requirements traceability document references things such as:

```text
src/bias_aperture/fairness/engine.py
src/tests/test_fairness_engine.py
src/tests/test_statistics.py
```

but those paths are not currently present on `main`.

Meanwhile the actual tests include:

```text
test_fairness_backends.py
test_fairness_statistics.py
test_integration.py
...
```

That means the repository has a good **traceability concept**, but the traceability map itself is no longer perfectly synchronized with the executable tree.

This is exactly the sort of thing a reviewer can find quickly.

---

# 12. FR-010 / NFR-009 appear ahead of the implementation

The requirements documentation says regulatory evidence traceability, manifests, SHA-256 integrity, etc. are implemented.

But in the current CLI/report path I inspected, I do not see the claimed run-manifest generation and bundle-integrity mechanism.

There is a `drive-manifest.json`, but that is a synchronization manifest, not the same thing as an audit-run provenance manifest.

So these claims should be split into:

```text
implemented
planned
external synchronization
```

rather than being allowed to blur together.

---

# 13. Your empirical evidence is good in form, but not as strong as the repository's presentation suggests

The checked-in generated report is useful:

- FairFace validation set
- N=10,954
- race audit
- actual generated HTML

That is much better than having only synthetic tests.

But most of the automated verification suite is still based on **synthetic known-answer datasets**.

That is good for mathematical contracts.

It is not the same as:

```text
fresh FairFace download
→ actual model inference
→ exact prediction artifact
→ current code
→ fresh report
→ fresh hash
→ CI-verifiable evidence
```

So I would classify the repository as:

**strong reproducible software testing + partially reproducible empirical case study**

rather than fully end-to-end reproducible research.

---

# What the testing architecture gets right

There are actually **15 test files** in `src/tests`, including:

```text
data ingestion
schema
model interface
fairness metrics
fairness backends
backend harmonization
statistics
explainability
report generation
offline report contract
CLI
integration
known-answer verification
```

That breadth is a genuine strength.

The known-answer tests are especially useful because they establish explicit values like:

```text
DPD = 0.500
EOP = 0.500
EOD = 0.500
DIR ≈ 0.333
```

on a controlled matrix.

However, the third-party backend “harmonization” tests are mostly **mathematical contract tests**, not live integration tests against the two external libraries. That means they prove your intended mathematics, not necessarily that the installed AIF360 and Fairlearn versions actually produce the assumptions you claim.

---

# The repository's regulatory positioning is mostly sensible

The regulatory framing is one of the better parts of the documentation, provided you keep the distinction between:

**audit context**

and

**legal certification**

.

EU AI Act Article 10 explicitly includes examination of datasets for possible biases that could lead to discrimination, while Article 13 deals with transparency and information to deployers. 

NIST AI RMF 1.0 Measure 2.11 explicitly calls for fairness and bias to be evaluated and the results documented. 

So your mapping is reasonable as a **traceability layer**.

It should not be presented as:

> “BiasAperture certifies EU AI Act compliance.”

Your own specification actually handles this distinction correctly; preserve that wording.

---

# Current repository maturity

One interesting point from the commit history:

The latest commit I found, `a9257c9` on **September 16, 2026**, is a Drive/Notebook synchronization metadata update. The more substantive code/documentation work is concentrated around September 5–7.

So the repository currently looks less like an actively evolving software project and more like a **near-frozen capstone artifact with synchronized research infrastructure**.

For your use case, that is not necessarily bad. In fact, it gives the project a clearer “submission baseline” character.

The public root currently describes the project as M1–M4 complete and M5 active at 95%, while also saying 78/78 tests pass. 

I would treat the 78/78 figure as a **repository-stated result**, not a freshly independently verified CI result: the GitHub status/workflow information I could retrieve for the examined commits did not expose live passing checks.

---

# What I would fix before calling this v1.0

## P0 — statistical correctness

### 1. Separate hypothesis tests

Implement distinct inference for:

```text
DPD
EOP / TPR disparity
EOD / TPR disparity
EOD / FPR disparity
DIR / selection disparity
```

and attach:

```text
test_name
raw_p
adjusted_p
hypothesis_family
```

to the result.

### 2. Remove fake ±0.05 confidence intervals

Every reported interval should come from an actual documented estimator.

### 3. Correct the BCa implementation

Either implement a defensible standard BCa algorithm for the large-n case, or label the large-n approach as an approximation and validate it empirically.

---

## P0 — backend integrity

Change:

```text
AIF360 failure
    ↓
Fairlearn fallback
```

to:

```text
AIF360 failure
    ↓
backend unavailable
    ↓
no false "consensus"
```

Then add a live integration test which genuinely invokes both third-party libraries.

---

## P1 — correct the AIF360 research claims

Specifically distinguish:

```text
equalized_odds_difference
```

from:

```text
average_odds_difference
```

because current AIF360 documentation explicitly treats them differently. 

This is a relatively small code/documentation change but a significant improvement in research credibility.

---

## P1 — make the explainability claim exact

Either actually execute `PartitionExplainer`, or rename the current functionality everywhere to:

> demographic surrogate attribution

That would still be a perfectly respectable feature.

---

## P1 — synchronize the evidence ledger

Make the repository mechanically verify:

```text
requirements → source files → tests → CI
```

and fail if a referenced implementation/test path no longer exists.

That fits the overall philosophy of BiasAperture extremely well.

---

# The most important conceptual change

Right now the project is trying to be three things simultaneously:

```text
1. fairness research project
2. software engineering platform
3. compliance/audit infrastructure
```

The repository is strongest as **#2 + #3**.

Trying to make the statistical machinery look more rigorous than it currently is actually weakens the project.

The strongest defensible positioning is:

> **BiasAperture is an open, reproducible fairness-audit engineering framework that operationalizes established fairness metrics and evidence workflows for facial-analysis systems.**

That is already substantial.

You do **not** need to claim a new fairness theory.

---

# Final verdict

### What I would say about the repository today

**Engineering:** strong.

**Architecture:** strong.

**Documentation:** unusually strong.

**Research organization:** strong.

**Data integrity:** strong.

**Statistical implementation:** currently the main weakness.

**Explainability:** useful but overstated in places.

**Empirical reproducibility:** good foundation, not yet airtight.

### Most important sentence

> **BiasAperture has crossed the threshold from “student prototype” into a serious research-engineering artifact, but it has not yet crossed the threshold into a statistically defensible audit instrument.**

That is actually a good place to be. The architecture and evidence infrastructure are already there; the remaining work is concentrated in a relatively small number of high-impact correctness issues rather than requiring a redesign.

Relevant source files:  
urlfairness/backends.pyhttps://github.com/Aaradhya-Dev-Tamrakar/BiasAperture/blob/main/src/bias_aperture/fairness/backends.py  
urlfairness/statistics.pyhttps://github.com/Aaradhya-Dev-Tamrakar/BiasAperture/blob/main/src/bias_aperture/fairness/statistics.py  
urlexplainability.pyhttps://github.com/Aaradhya-Dev-Tamrakar/BiasAperture/blob/main/src/bias_aperture/explainability.py  
urlrequirements traceabilityhttps://github.com/Aaradhya-Dev-Tamrakar/BiasAperture/blob/main/specs/11-requirements-traceability.md

---

If you want, I can:

- Suggest concrete code fixes for p-value calculation and hypothesis tests
- Outline steps to correct BCa bootstrap implementation and confidence intervals
- Plan backend integrity improvements and live dual-backend testing

---
