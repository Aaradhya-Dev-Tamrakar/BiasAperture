# Track 17 — Strategy Pattern for Dual Fairness Backends
**Stream:** E (Architecture) · **Priority:** 🔴 Critical · **Owner Focus:** Both
**Estimated Time:** 30 min · **Feeds:** `fairness/base.py` architecture

## Instructions
1. Paste `CONTEXT.md` into Claude Desktop first
2. Then paste the prompt below
3. Save the output as `results/17_strategy_pattern_design.md`

## Prompt

Design a Python Strategy pattern implementation for BiasAperture's dual fairness backends (Fairlearn + AIF360). Requirements:

1. **Abstract base class:** `FairnessBackend` with method `compute_metrics(records: list[SubjectRecord]) → list[MetricResult]`
2. **Concrete implementations:** `FairlearnBackend` and `AIF360Backend`
3. **Cross-validation orchestrator:** runs both backends, compares results, flags divergences
4. **MetricResult schema:** each result includes metric_name, subgroup, n, point_estimate, ci_lower, ci_upper, p_value, insufficient_sample
5. **Divergence detection:** if Fairlearn and AIF360 disagree on a metric by more than ε, flag it in the report

Also design:
- How the backends handle the n < 30 guard (insufficient_sample)
- How bootstrap CI and chi-squared tests integrate (are they per-backend or post-aggregation?)
- How the Strategy pattern enables adding a third backend later without modifying existing code

Provide complete Python code with type hints, dataclasses, and ABC. Follow PEP 8, 88-char line limit.
