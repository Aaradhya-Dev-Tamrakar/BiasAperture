"""Report generation package (Stream Report / WP3).

Exports:
- ``HTMLReportGenerator``: Standalone offline HTML report compiler
- ``ReportContext``: Aggregated context data model for report generation
- ``REGULATORY_MAPPING``: Static metric to EU AI Act / NIST AI RMF mapping
"""

from __future__ import annotations

from bias_aperture.report.generator import (
    REGULATORY_MAPPING,
    HTMLReportGenerator,
    ReportContext,
)
from bias_aperture.report.metadata_registry import (
    ModelMetadata,
    ModelMetadataRegistry,
)
from bias_aperture.report.narrative import (
    METRIC_GLOSSARY,
    PlainLanguageSummary,
    synthesize_plain_language_narrative,
)
from bias_aperture.report.reconciler import (
    ReconciliationIssue,
    ReconciliationSummary,
    ReportReconciler,
)

__all__ = [
    "HTMLReportGenerator",
    "METRIC_GLOSSARY",
    "ModelMetadata",
    "ModelMetadataRegistry",
    "PlainLanguageSummary",
    "REGULATORY_MAPPING",
    "ReconciliationIssue",
    "ReconciliationSummary",
    "ReportContext",
    "ReportReconciler",
    "synthesize_plain_language_narrative",
]
