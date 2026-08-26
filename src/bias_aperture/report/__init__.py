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

__all__ = [
    "HTMLReportGenerator",
    "REGULATORY_MAPPING",
    "ReportContext",
]
