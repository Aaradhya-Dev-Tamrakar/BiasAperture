"""Command-line entry point for BiasAperture audits."""

from __future__ import annotations

import logging
import sys

from bias_aperture.cli_parser import _add_audit_arguments, build_parser
from bias_aperture.pipeline import AuditPipeline, AuditResult

logger = logging.getLogger(__name__)

__all__ = [
    "AuditPipeline",
    "AuditResult",
    "_add_audit_arguments",
    "build_parser",
    "main",
]


def _configure_logging() -> None:
    """Set up root logging with a human-readable StreamHandler for CLI use."""
    root = logging.getLogger("bias_aperture")
    if not root.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("[%(levelname)s] %(name)s: %(message)s"))
        root.addHandler(handler)
        root.setLevel(logging.INFO)


def main(argv: list[str] | None = None) -> int:
    """Main CLI entrypoint — thin shell delegating to AuditPipeline."""
    if argv is None:
        argv = sys.argv[1:]

    # Support both `bias-aperture audit ...` and `bias-aperture ...`
    if argv and argv[0] == "audit":
        argv = argv[1:]

    parser = build_parser()
    args = parser.parse_args(argv)

    _configure_logging()

    if args.bca_resamples < 1000:
        logger.error(
            "--bca-resamples must be >= 1000 for statistical validity "
            "(NFR-002), got %d",
            args.bca_resamples,
        )
        return 1

    pred_file = args.predictions_file
    if not pred_file.exists():
        logger.error("Predictions file not found: %s", pred_file)
        return 1

    logger.info("=" * 60)
    logger.info(" BiasAperture — Demographic Bias Auditing Platform")
    logger.info("=" * 60)

    pipeline = AuditPipeline()
    try:
        result = pipeline.run(
            predictions_file=pred_file,
            true_label_col=args.true_label_col,
            predicted_label_col=args.predicted_label_col,
            race_col=args.race_col,
            gender_col=args.gender_col,
            age_col=args.age_col,
            protected_attr=args.protected_attr,
            backend=args.backend,
            bca_resamples=args.bca_resamples,
            output_report=args.output_report,
            model_name=args.model_name,
            dataset_name=args.dataset_name,
            explain=args.explain,
            model_description=getattr(args, "model_description", None),
            report_format=getattr(args, "format", None),
        )
    except (ValueError, RuntimeError) as exc:
        logger.error("Audit failed: %s", exc)
        return 1

    if result.records_ingested == 0:
        return 1

    logger.info("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
