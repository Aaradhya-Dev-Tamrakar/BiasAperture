"""Argument definitions and parser construction for the command-line interface."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any


def _add_audit_arguments(parser: argparse.ArgumentParser) -> None:
    """Configure arguments for the audit command."""
    parser.add_argument(
        "--config",
        "-c",
        type=Path,
        default=None,
        help=(
            "Path to YAML audit configuration file (e.g., configs/audit_default.yaml)."
        ),
    )
    parser.add_argument(
        "--predictions-file",
        "-i",
        type=Path,
        default=None,
        help="Path to predictions CSV/JSON file.",
    )
    parser.add_argument(
        "--true-label-col",
        type=str,
        default="true_label",
        help="Column name containing ground-truth labels (default: true_label).",
    )
    parser.add_argument(
        "--predicted-label-col",
        type=str,
        default="predicted_label",
        help="Column name containing predictions (default: predicted_label).",
    )
    parser.add_argument(
        "--race-col",
        type=str,
        default="race",
        help="Column name containing race labels (default: race).",
    )
    parser.add_argument(
        "--gender-col",
        type=str,
        default="gender",
        help="Column name containing gender labels (default: gender).",
    )
    parser.add_argument(
        "--age-col",
        type=str,
        default="age",
        help="Column name containing age labels (default: age).",
    )
    parser.add_argument(
        "--protected-attr",
        "-a",
        type=str,
        default="race",
        choices=["race", "gender", "age", "race_gender"],
        help=(
            "Demographic protected axis (default: race, "
            "supports intersectional: race_gender)."
        ),
    )
    parser.add_argument(
        "--backend",
        type=str,
        default="dual",
        choices=["dual", "fairlearn", "aif360"],
        help=(
            "Fairness metric computation backend: dual consensus (default), "
            "fairlearn, or aif360."
        ),
    )
    parser.add_argument(
        "--bca-resamples",
        "--bca-bootstrap",
        dest="bca_resamples",
        type=int,
        default=1000,
        help="Number of stratified BCa bootstrap resamples (default: 1000, min: 1000).",
    )
    parser.add_argument(
        "--output-report",
        "-o",
        type=Path,
        default=Path("bias_aperture_report.html"),
        help="Output report destination path.",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="FairFace ResNet-34 Multi-Task Classifier",
        help="Model name for Model Card presentation.",
    )
    parser.add_argument(
        "--dataset-name",
        type=str,
        default="FairFace Benchmark Dataset",
        help="Dataset name for presentation.",
    )
    parser.add_argument(
        "--model-description",
        type=str,
        default=None,
        help=(
            "Custom model description for Model Card presentation (auto-resolved if "
            "omitted)."
        ),
    )
    parser.add_argument(
        "--explain",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "Enable demographic surrogate attribution on flagged "
            "disparities (default: True)."
        ),
    )


def build_parser(
    config_defaults: dict[str, Any] | None = None,
) -> argparse.ArgumentParser:
    """Construct CLI argument parser supporting both flat and subcommand invocation.

    Parameters
    ----------
    config_defaults : dict[str, Any] | None
        Optional dictionary of default parameter values loaded from a
        YAML configuration.
    """
    parser = argparse.ArgumentParser(
        prog="bias-aperture",
        description=(
            "BiasAperture: Diagnostic Demographic Bias Auditing "
            "Platform for Computer Vision."
        ),
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=False)
    audit_parser = subparsers.add_parser(
        "audit",
        help="Audit demographic fairness of predictions.",
        description="Audit demographic fairness of model predictions.",
    )
    _add_audit_arguments(audit_parser)
    _add_audit_arguments(parser)

    if config_defaults:
        parser.set_defaults(**config_defaults)
        audit_parser.set_defaults(**config_defaults)

    return parser
