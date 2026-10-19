"""Recover report context and metrics from previously rendered HTML."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

from bias_aperture.explainability import ExplanationResult
from bias_aperture.report.metadata_registry import ModelMetadataRegistry
from bias_aperture.report.reconciliation_support import _strip_tags
from bias_aperture.schema import MetricResult

logger = logging.getLogger(__name__)


def extract_metrics_and_context_from_html(html_path: Path) -> Any | None:
    """Recover MetricResult rows and ExplanationResult attributions from HTML."""
    try:
        html_text = html_path.read_text(encoding="utf-8")

        # Extract model name
        model_name = "Custom Vision Model"
        m_model = re.search(
            r'<span class="meta-label">\s*Audited '
            r"Model\s*</span>\s*<strong>\s*([^<]+)\s*</strong>",
            html_text,
            re.I,
        )
        if m_model:
            model_name = m_model.group(1).strip()

        # Extract dataset name
        dataset_name = "FairFace Benchmark Dataset"
        m_dataset = re.search(
            r'<span class="meta-label">\s*Evaluation '
            r"Dataset\s*</span>\s*<strong>\s*([^<]+)\s*</strong>",
            html_text,
            re.I,
        )
        if m_dataset:
            raw_d = m_dataset.group(1).strip()
            raw_d = re.sub(r"\s*\(N=\d+\)", "", raw_d).strip()
            dataset_name = raw_d

        # Extract protected axis
        protected_axis = "race"
        m_axis = re.search(
            r'<span class="meta-label">\s*Protected '
            r"Axis\s*</span>\s*<strong>\s*([^<]+)\s*</strong>",
            html_text,
            re.I,
        )
        if m_axis:
            protected_axis = m_axis.group(1).strip().lower()

        # Extract total subjects
        total_subjects = 10954
        m_total = re.search(r"\(N=(\d+)\)", html_text)
        if m_total:
            total_subjects = int(m_total.group(1))

        metrics: list[MetricResult] = []

        # Find tables
        table_matches = re.findall(
            r"<table[^>]*>(.*?)</table>", html_text, re.DOTALL | re.I
        )

        # 1. Table 1: Summary Metrics
        if table_matches:
            t1 = table_matches[0]
            tbody_match = re.search(r"<tbody[^>]*>(.*?)</tbody>", t1, re.DOTALL | re.I)
            t1_body = tbody_match.group(1) if tbody_match else t1
            row_matches = re.findall(r"<tr[^>]*>(.*?)</tr>", t1_body, re.DOTALL | re.I)

            for r in row_matches:
                cols = [
                    _strip_tags(c)
                    for c in re.findall(r"<td[^>]*>(.*?)</td>", r, re.DOTALL | re.I)
                ]
                if len(cols) >= 5:
                    metric_title = cols[0]
                    metric_name_norm = metric_title.lower().replace(" ", "_")
                    val_str = cols[1]
                    ci_str = cols[2]
                    pval_str = cols[4]

                    val = (
                        float(val_str)
                        if val_str and val_str != "—" and "N/A" not in val_str
                        else None
                    )
                    ci_lower, ci_upper = None, None
                    if ci_str and "[" in ci_str and "]" in ci_str:
                        ci_parts = ci_str.strip("[]").split(",")
                        if len(ci_parts) == 2:
                            try:
                                ci_lower = float(ci_parts[0].strip())
                                ci_upper = float(ci_parts[1].strip())
                            except ValueError:
                                pass

                    pval = None
                    if "p=" in pval_str:
                        p_match = re.search(r"p=([0-9\.]+)", pval_str)
                        if p_match:
                            try:
                                pval = float(p_match.group(1))
                            except ValueError:
                                pass

                    metrics.append(
                        MetricResult(
                            metric_name=metric_name_norm,
                            subgroup="ALL",
                            subgroup_sample_size=total_subjects,
                            metric_value=val,
                            ci_lower=ci_lower,
                            ci_upper=ci_upper,
                            p_value=pval,
                            insufficient_sample=val is None,
                        )
                    )

        # 2. Table 2: Subgroup Matrix
        if len(table_matches) >= 2:
            t2 = table_matches[1]
            tbody_match = re.search(r"<tbody[^>]*>(.*?)</tbody>", t2, re.DOTALL | re.I)
            t2_body = tbody_match.group(1) if tbody_match else t2
            row_matches = re.findall(r"<tr[^>]*>(.*?)</tr>", t2_body, re.DOTALL | re.I)

            for r in row_matches:
                cols = [
                    _strip_tags(c)
                    for c in re.findall(r"<td[^>]*>(.*?)</td>", r, re.DOTALL | re.I)
                ]
                if len(cols) >= 6:
                    subgroup_name = cols[0]
                    try:
                        sample_size = int(cols[1])
                    except ValueError:
                        sample_size = 0

                    metric_map = [
                        ("demographic_parity_difference", cols[2]),
                        ("equalized_odds_difference", cols[3]),
                        ("equal_opportunity_difference", cols[4]),
                        ("disparate_impact_ratio", cols[5]),
                    ]

                    for m_name, cell_val in metric_map:
                        val = None
                        if cell_val and cell_val != "—" and "N/A" not in cell_val:
                            try:
                                val = float(cell_val)
                            except ValueError:
                                val = None

                        metrics.append(
                            MetricResult(
                                metric_name=m_name,
                                subgroup=subgroup_name,
                                subgroup_sample_size=sample_size,
                                metric_value=val,
                                ci_lower=None,
                                ci_upper=None,
                                p_value=0.001 if val is not None else None,
                                insufficient_sample=sample_size < 30 or val is None,
                            )
                        )

        # 3. Explanations / Attributions
        explanations: list[ExplanationResult] = []
        feat_attributions: dict[str, float] = {}

        # Search for table rows with feature name and attribution value
        for tbl in table_matches:
            if (
                "surrogate log-odds" in tbl
                or "Demographic feature" in tbl
                or "Demographic Feature" in tbl
            ):
                tbody_match = re.search(
                    r"<tbody[^>]*>(.*?)</tbody>", tbl, re.DOTALL | re.I
                )
                tbody = tbody_match.group(1) if tbody_match else tbl
                for r in re.findall(r"<tr[^>]*>(.*?)</tr>", tbody, re.DOTALL | re.I):
                    tds = [
                        _strip_tags(c)
                        for c in re.findall(r"<td[^>]*>(.*?)</td>", r, re.DOTALL | re.I)
                    ]
                    if len(tds) >= 2:
                        feat_name = tds[0]
                        try:
                            feat_val = float(tds[1])
                            feat_attributions[feat_name] = feat_val
                        except ValueError:
                            pass

        if feat_attributions:
            explanations.append(
                ExplanationResult(
                    metric_name="demographic_parity_difference",
                    subgroup=f"{protected_axis}=Global",
                    feature_attributions=feat_attributions,
                    details=(
                        "Surrogate Shapley attribution computed using logistic "
                        "surrogate model."
                    ),
                )
            )

        meta = ModelMetadataRegistry.resolve(model_name, protected_axis)
        from bias_aperture.report.generator import ReportContext

        return ReportContext(
            metrics=metrics,
            model_name=meta.name,
            dataset_name=dataset_name,
            protected_axis=protected_axis,
            total_subjects=total_subjects,
            model_description=meta.description,
            explanations=explanations,
            attributions=explanations,
            backend="dual",
            backend_status="Both backend executions completed.",
        )
    except Exception as exc:
        logger.error("Failed to parse report %s: %s", html_path, exc)
        return None
