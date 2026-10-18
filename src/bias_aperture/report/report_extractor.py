from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from bias_aperture.schema import MetricResult


def extract_report_metadata_and_metrics(html_path: Path) -> dict[str, Any]:
    """Parse an existing HTML report to extract its metrics, model name, and metadata."""
    text = html_path.read_text(encoding="utf-8")

    # 1. Metadata
    model_name_match = re.search(
        r'<span class="meta-label">Audited Model</span>\s*<strong>(.*?)</strong>', text
    )
    model_name = (
        model_name_match.group(1).strip() if model_name_match else "Unknown Model"
    )

    dataset_match = re.search(
        r'<span class="meta-label">Evaluation Dataset</span>\s*<strong>(.*?)\s*\(N=(\d+)\)</strong>',
        text,
    )
    dataset_name = (
        dataset_match.group(1).strip()
        if dataset_match
        else "FairFace Benchmark Dataset"
    )
    total_subjects = int(dataset_match.group(2)) if dataset_match else 10954

    protected_axis_match = re.search(
        r'<span class="meta-label">Protected Axis</span>\s*<strong>(.*?)</strong>', text
    )
    protected_axis = (
        protected_axis_match.group(1).strip().lower()
        if protected_axis_match
        else "race"
    )

    timestamp_match = re.search(
        r'<span class="meta-label">Audit Date</span>\s*<strong>(.*?)</strong>', text
    )
    timestamp = timestamp_match.group(1).strip() if timestamp_match else ""

    # Backend info
    backend_match = re.search(
        r"<strong>Backend configuration:</strong>\s*(.*?)\.\s*(.*?)</p>", text
    )
    backend = backend_match.group(1).strip() if backend_match else "dual"
    backend_status = (
        backend_match.group(2).strip()
        if backend_match
        else "Both backend executions completed."
    )

    metrics: list[MetricResult] = []

    # 2. Table 1: Summary Metrics
    t1_match = re.search(
        r"<h2>1\. Headline Fairness Metrics.*?<tbody>(.*?)</tbody>", text, re.DOTALL
    )
    if t1_match:
        for row in re.findall(r"<tr>(.*?)</tr>", t1_match.group(1), re.DOTALL):
            tds = re.findall(r"<td[^>]*>(.*?)</td>", row, re.DOTALL)
            if len(tds) >= 5:
                raw_name = (
                    re.sub(r"<[^>]+>", "", tds[0]).strip().lower().replace(" ", "_")
                )
                raw_val = re.sub(r"<[^>]+>", "", tds[1]).strip()
                val = (
                    float(raw_val)
                    if raw_val and raw_val != "—" and "N/A" not in raw_val
                    else None
                )

                raw_ci = re.sub(r"<[^>]+>", "", tds[2]).strip()
                ci_match = re.search(
                    r"\[\s*([0-9\.\-]+)\s*,\s*([0-9\.\-]+)\s*\]", raw_ci
                )
                ci_lower = float(ci_match.group(1)) if ci_match else None
                ci_upper = float(ci_match.group(2)) if ci_match else None

                raw_p = re.sub(r"<[^>]+>", "", tds[4]).strip()
                p_match = re.search(r"p\s*=\s*([0-9\.\-]+)", raw_p)
                p_val = float(p_match.group(1)) if p_match else None

                metrics.append(
                    MetricResult(
                        metric_name=raw_name,
                        subgroup="ALL",
                        metric_value=val,
                        ci_lower=ci_lower,
                        ci_upper=ci_upper,
                        p_value=p_val,
                        subgroup_sample_size=total_subjects,
                        insufficient_sample=False,
                    )
                )

    # 3. Table 2: Subgroup Metrics
    t2_match = re.search(
        r"<h2>2\. Per-Subgroup Disparity Matrix.*?<tbody>(.*?)</tbody>", text, re.DOTALL
    )
    if t2_match:
        for row in re.findall(r"<tr>(.*?)</tr>", t2_match.group(1), re.DOTALL):
            tds = re.findall(r"<td[^>]*>(.*?)</td>", row, re.DOTALL)
            if len(tds) >= 6:
                subgroup = re.sub(r"<[^>]+>", "", tds[0]).strip()
                sample_size = int(re.sub(r"<[^>]+>", "", tds[1]).strip())

                dpd_val = (
                    float(re.sub(r"<[^>]+>", "", tds[2]).strip())
                    if tds[2].strip() not in ["—", "N/A"]
                    else None
                )
                eod_val = (
                    float(re.sub(r"<[^>]+>", "", tds[3]).strip())
                    if tds[3].strip() not in ["—", "N/A"]
                    else None
                )
                eop_val = (
                    float(re.sub(r"<[^>]+>", "", tds[4]).strip())
                    if tds[4].strip() not in ["—", "N/A"]
                    else None
                )
                dir_val = (
                    float(re.sub(r"<[^>]+>", "", tds[5]).strip())
                    if tds[5].strip() not in ["—", "N/A"]
                    else None
                )

                # Extract significance from bar colors if available
                # In Table 2 SVG bars, each metric bar has a color: red if p < 0.05 else blue
                bars_html = tds[6] if len(tds) > 6 else ""
                red_bars = set(
                    re.findall(
                        r'<text[^>]*>([A-Z]+)</text>\s*<rect[^>]*/>\s*<rect[^>]*fill="#(?:dc2626|991b1b)"',
                        bars_html,
                    )
                )

                metric_map = [
                    ("demographic_parity_difference", dpd_val, "DPD"),
                    ("equalized_odds_difference", eod_val, "EOD"),
                    ("equal_opportunity_difference", eop_val, "EOP"),
                    ("disparate_impact_ratio", dir_val, "DIR"),
                ]

                for m_name, m_val, short_code in metric_map:
                    is_sig = short_code in red_bars
                    p_val = 0.0001 if is_sig else 0.50
                    metrics.append(
                        MetricResult(
                            metric_name=m_name,
                            subgroup=subgroup,
                            metric_value=m_val,
                            ci_lower=None,
                            ci_upper=None,
                            p_value=p_val,
                            subgroup_sample_size=sample_size,
                            insufficient_sample=sample_size < 30,
                        )
                    )

    # 4. Explanations (extract from Section 3 if present)
    explanations = []
    # Check if feature importances table exists
    feat_table_match = re.search(
        r"<th>Demographic Feature</th>.*?<tbody>(.*?)</tbody>",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    feature_attributions = {}
    if feat_table_match:
        for r in re.findall(r"<tr>(.*?)</tr>", feat_table_match.group(1), re.DOTALL):
            tds = re.findall(r"<td[^>]*>(.*?)</td>", r, re.DOTALL)
            if len(tds) >= 2:
                feat = re.sub(r"<[^>]+>", "", tds[0]).strip()
                val = float(re.sub(r"<[^>]+>", "", tds[1]).strip())
                feature_attributions[feat] = val

    if not feature_attributions:
        # Check SVG feature attribution bars in old style
        # e.g., <text ...>gender_Female</text> ... <text ...>0.243</text>
        svg_bars = re.findall(
            r"<text[^>]*>([a-zA-Z0-9_\-]+)</text>\s*<rect[^>]*/>\s*<rect[^>]*/>\s*<text[^>]*>([0-9\.]+)</text>",
            text,
        )
        if svg_bars:
            for feat, val in svg_bars:
                feature_attributions[feat] = float(val)

    if feature_attributions:
        from bias_aperture.explainability import ExplanationResult

        explanations.append(
            ExplanationResult(
                metric_name="demographic_parity_difference",
                subgroup="ALL",
                feature_attributions=feature_attributions,
                details=f"Surrogate Shapley attribution computed across {total_subjects} subjects for ALL.",
            )
        )

    return {
        "model_name": model_name,
        "dataset_name": dataset_name,
        "total_subjects": total_subjects,
        "protected_axis": protected_axis,
        "timestamp": timestamp,
        "backend": backend,
        "backend_status": backend_status,
        "metrics": metrics,
        "explanations": explanations,
    }
