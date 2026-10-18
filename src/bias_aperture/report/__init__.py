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
from bias_aperture.report.reconciler import (
    ReconciliationIssue,
    ReconciliationSummary,
    ReportReconciler,
)

__all__ = [
    "HTMLReportGenerator",
    "ModelMetadata",
    "ModelMetadataRegistry",
    "REGULATORY_MAPPING",
    "ReconciliationIssue",
    "ReconciliationSummary",
    "ReportContext",
    "ReportReconciler",
]


