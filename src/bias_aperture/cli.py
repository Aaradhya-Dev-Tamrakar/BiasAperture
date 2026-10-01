"""
BiasAperture Command-Line Interface (WP5 / System Orchestration).

Wires together the complete end-to-end diagnostic auditing pipeline:
    PredictionsFile / CSV / JSON
        ──► DataIngestionPipeline (Validation & Cohort Profiling)
        ──► CrossValidationOrchestrator (Fairlearn + AIF360 Consensus)
        ──► HTMLReportGenerator (Standalone Offline HTML Dossier)

Modularity (R3): Business logic extracted into AuditPipeline so the
CLI's main() is a thin argument-parsing shell. AuditPipeline is
independently importable and testable without argv parsing.

Logging (R5): All output goes through the standard logging module.
A StreamHandler is configured once in main() so terminal output is
preserved while remaining filterable and redirectable.
"""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass
from pathlib import Path

from bias_aperture.data_ingestion import DataIngestionPipeline, IngestionConfig
from bias_aperture.explainability import ExplanationResult, ShapExplainerEngine
from bias_aperture.fairness import (
    AIF360Backend,
    CrossValidationOrchestrator,
    FairlearnBackend,
)
from bias_aperture.report import HTMLReportGenerator, ReportContext
from bias_aperture.schema import MetricResult

logger = logging.getLogger(__name__)


# ── Reusable Pipeline Runner (R3) ─────────────────────────────────────


@dataclass(frozen=True, slots=True)
class AuditResult:
    """Structured output of a complete audit pipeline execution."""

    records_ingested: int
    validation_warnings: int
    metrics: list[MetricResult]
    divergence_count: int
    explained_count: int
    report_path: Path | None


class AuditPipeline:
    """Reusable end-to-end audit runner decoupled from CLI argument parsing.

    Encapsulates the four-stage pipeline (ingestion → fairness engine →
    explainability → report generation) so it can be invoked
    programmatically from tests, notebooks, or the CLI without
    duplicating orchestration logic.
    """

    def run(
        self,
        predictions_file: Path,
        *,
        true_label_col: str = "true_label",
        predicted_label_col: str = "predicted_label",
        race_col: str = "race",
        gender_col: str = "gender",
        age_col: str = "age",
        protected_attr: str = "race",
        backend: str = "dual",
        bca_resamples: int = 1000,
        output_report: Path | None = None,
        model_name: str = "FairFace ResNet-34 Multi-Task Classifier",
        dataset_name: str = "FairFace Benchmark Dataset",
        explain: bool = True,
    ) -> AuditResult:
        """Execute the full audit pipeline and return structured results."""

        # 1. Ingestion
        logger.info("Ingesting predictions from: %s", predictions_file)
        logger.info("Protected demographic axis: %s", protected_attr)
        logger.info("Computational backend: %s", backend)
        logger.info("Bootstrap resamples (BCa): %d", bca_resamples)

        ingestion = DataIngestionPipeline(
            config=IngestionConfig(
                true_label_col=true_label_col,
                predicted_label_col=predicted_label_col,
                race_col=race_col,
                gender_col=gender_col,
                age_col=age_col,
            )
        )
        result = ingestion.ingest_file(predictions_file)
        records = result.records
        summary = result.validation_summary

        logger.info(
            "Ingested %d valid records (%d validation warnings/errors).",
            len(records),
            len(summary.issues),
        )
        if not records:
            logger.error("No valid SubjectRecords extracted.")
            return AuditResult(
                records_ingested=0,
                validation_warnings=len(summary.issues),
                metrics=[],
                divergence_count=0,
                explained_count=0,
                report_path=None,
            )

        # 2. Fairness Engine
        logger.info("Running fairness estimation backend(s) [%s]...", backend)
        orchestrator = self._select_orchestrator(backend)
        metrics, divergences = orchestrator.run(
            records,
            protected_attr=protected_attr,
            n_bootstrap_resamples=bca_resamples,
        )

        logger.info("Evaluated %d metric rows across demographic strata.", len(metrics))
        if divergences:
            logger.warning("%d cross-backend divergences detected.", len(divergences))

        # 3. Conditional Explainability
        explanations: list[ExplanationResult] = []
        if explain:
            explanations = self._run_explainability(metrics, records)
        explained_count = sum(bool(e.feature_attributions) for e in explanations)

        # 4. Report Generation
        saved_path: Path | None = None
        if output_report is not None:
            saved_path = self._generate_report(
                metrics,
                records,
                output_report,
                model_name,
                dataset_name,
                protected_attr,
                explanations,
                backend,
                (
                    "Cross-library validation incomplete. Unavailable backend(s): "
                    + ", ".join(orchestrator.backend_failures)
                    if orchestrator.backend_failures
                    else (
                        f"Both backend executions completed; {len(divergences)} "
                        "point-estimate discrepancies detected."
                        if backend == "dual"
                        else "Single backend execution; no cross-library validation."
                    )
                ),
            )

        return AuditResult(
            records_ingested=len(records),
            validation_warnings=len(summary.issues),
            metrics=metrics,
            divergence_count=len(divergences),
            explained_count=explained_count,
            report_path=saved_path,
        )

    @staticmethod
    def _select_orchestrator(backend: str) -> CrossValidationOrchestrator:
        """Instantiate the orchestrator with the requested backend(s)."""
        if backend == "fairlearn":
            return CrossValidationOrchestrator(backends=[FairlearnBackend()])
        elif backend == "aif360":
            return CrossValidationOrchestrator(backends=[AIF360Backend()])
        return CrossValidationOrchestrator()

    @staticmethod
    def _run_explainability(
        metrics: list[MetricResult],
        records: list,
    ) -> list[ExplanationResult]:
        """Retain surrogate associations and unavailable statuses for reporting."""
        logger.info(
            "Running demographic surrogate attribution on flagged disparities..."
        )
        explainer = ShapExplainerEngine()
        explanations = []
        for m in metrics:
            if explainer.should_explain(m):
                exp_res = explainer.explain_disparity(m, records=records)
                explanations.append(exp_res)
                if exp_res.feature_attributions:
                    top_feat = list(exp_res.feature_attributions.items())[0]
                    logger.info(
                        "    -> Flagged [%s | %s]: top proxy driver = %s (%.3f)",
                        m.metric_name,
                        m.subgroup,
                        top_feat[0],
                        top_feat[1],
                    )
        explained_count = sum(bool(e.feature_attributions) for e in explanations)
        logger.info(
            "Generated targeted attributions for %d statistically flagged disparities.",
            explained_count,
        )
        return explanations

    @staticmethod
    def _generate_report(
        metrics: list[MetricResult],
        records: list,
        output_report: Path,
        model_name: str,
        dataset_name: str,
        protected_attr: str,
        explanations: list[ExplanationResult],
        backend: str,
        backend_status: str,
    ) -> Path:
        """Compile and save the offline compliance report."""
        logger.info("Compiling offline compliance report to: %s...", output_report)
        context = ReportContext(
            metrics=metrics,
            model_name=model_name,
            dataset_name=dataset_name,
            protected_axis=protected_attr,
            total_subjects=len(records),
            explanations=explanations,
            backend=backend,
            backend_status=backend_status,
        )
        generator = HTMLReportGenerator()
        saved_path = generator.save(context, output_report)
        logger.info("Audit complete. Standalone report saved to: %s", saved_path)
        return saved_path


# ── CLI Argument Parsing ──────────────────────────────────────────────


def _add_audit_arguments(parser: argparse.ArgumentParser) -> None:
    """Configure arguments for the audit command."""
    parser.add_argument(
        "--predictions-file",
        "-i",
        type=Path,
        required=True,
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
        "--explain",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "Enable demographic surrogate attribution on flagged "
            "disparities (default: True)."
        ),
    )


def build_parser() -> argparse.ArgumentParser:
    """Construct CLI argument parser supporting both flat and subcommand invocation."""
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
    return parser


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
