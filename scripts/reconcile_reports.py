#!/usr/bin/env python3
"""
CLI runner for autonomous compliance report reconciliation and audit.

Usage:
  python scripts/reconcile_reports.py --check   # Audit mode (exit code 0 if all clean, 1 if issues found)
  python scripts/reconcile_reports.py --heal    # Self-healing mode (re-renders HTML and re-exports PDFs)
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Ensure src is in python path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from bias_aperture.report.reconciler import ReportReconciler

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("reconcile_reports")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reconcile and verify BiasAperture compliance reports.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--check",
        action="store_true",
        help="Audit compliance dossiers for invariant violations without modifying files.",
    )
    group.add_argument(
        "--heal",
        action="store_true",
        help="Self-heal all compliance dossiers: re-render HTML with latest templates and re-export PDFs.",
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=ROOT / "report",
        help="Directory containing compliance reports (default: report/).",
    )

    args = parser.parse_args()
    reconciler = ReportReconciler(report_dir=args.report_dir)

    if args.check:
        print("\nAuditing compliance dossiers in:", args.report_dir)
        issues = reconciler.audit_dossiers()
        if not issues:
            print(
                "  [PASS] All compliance dossiers and companion PDFs are healthy and in sync."
            )
            return 0

        print(f"  [FAIL] Detected {len(issues)} discrepancy/invariant violations:")
        for issue in issues:
            print(
                f"    - [{issue.issue_type}] {issue.report_name}: {issue.description}"
            )
        print(
            "\nAction required: Run 'python scripts/reconcile_reports.py --heal' (or 'make reconcile') to self-heal."
        )
        return 1

    if args.heal:
        print("\nSelf-healing compliance dossiers in:", args.report_dir)
        summary = reconciler.heal_dossiers()
        print(f"  Scanned: {summary.total_scanned}")
        print(f"  Healed:  {len(summary.healed_reports)}")
        if not summary.issues:
            print(
                "  [SUCCESS] All compliance dossiers and companion PDFs healed and verified clean."
            )
            return 0

        print(f"  [WARNING] Remaining issues after heal ({len(summary.issues)}):")
        for issue in summary.issues:
            print(
                f"    - [{issue.issue_type}] {issue.report_name}: {issue.description}"
            )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
