# Track 05 — Jinja2 HTML Report Template Patterns
**Stream:** B (Report Generation) · **Priority:** 🔴 Critical · **Owner Focus:** Aaradhya (WP3)
**Estimated Time:** 45 min · **Feeds:** `report/` package

## Instructions
1. Paste `CONTEXT.md` into Claude Desktop first
2. Then paste the prompt below
3. Save the output as `results/05_jinja2_report_templates.md`

## Prompt

Research Jinja2 HTML template patterns for generating bias audit compliance reports. The report must render:
1. A summary dashboard: overall pass/fail per metric, worst-performing subgroup highlighted
2. Per-metric tables with columns: subgroup, n, point_estimate, ci_lower, ci_upper, p_value, insufficient_sample flag
3. Conditional formatting: red for statistically significant disparities (p < 0.05), grey for insufficient sample
4. A regulatory mapping section: each metric row tagged with EU AI Act Article 10 sub-clause
5. SHAP attribution visualizations (placeholder slots for images)
6. Export-friendly: single self-contained HTML file with embedded CSS (no external dependencies)

Provide a complete Jinja2 template example with sample CSS. The data source is a list of MetricResult dataclass instances with fields: metric_name, subgroup, subgroup_sample_size, metric_value, ci_lower, ci_upper, p_value, insufficient_sample.
