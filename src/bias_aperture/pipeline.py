"""Reusable audit execution pipeline, independent of CLI argument parsing."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

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
        model_description: str | None = None,
        dataset: str = "fairface",
    ) -> AuditResult:
        """Execute the full audit pipeline and return structured results."""

        # 1. Ingestion
        logger.info("Ingesting predictions from: %s", predictions_file)
        logger.info("Dataset benchmark adapter: %s", dataset)
        logger.info("Protected demographic axis: %s", protected_attr)
        logger.info("Computational backend: %s", backend)
        logger.info("Bootstrap resamples (BCa): %d", bca_resamples)

        if (
            dataset.lower() == "utkface"
            and dataset_name == "FairFace Benchmark Dataset"
        ):
            dataset_name = "UTKFace Benchmark Dataset"

        # Self-healing column name resolution for standard FairFace CSV layouts
        if predictions_file.suffix.lower() == ".csv" and predictions_file.exists():
            try:
                with predictions_file.open("r", encoding="utf-8") as f:
                    first_line = f.readline().strip()
                headers = [h.strip() for h in first_line.split(",")]
                if race_col not in headers and "subgroup_race" in headers:
                    race_col = "subgroup_race"
                if gender_col not in headers and "subgroup_gender" in headers:
                    gender_col = "subgroup_gender"
                if age_col not in headers and "subgroup_age" in headers:
                    age_col = "subgroup_age"
                if true_label_col not in headers:
                    if f"true_{protected_attr}" in headers:
                        true_label_col = f"true_{protected_attr}"
                    elif protected_attr == "race_gender" and "true_race" in headers:
                        true_label_col = "true_race"
                if predicted_label_col not in headers:
                    if f"predicted_{protected_attr}" in headers:
                        predicted_label_col = f"predicted_{protected_attr}"
                    elif (
                        protected_attr == "race_gender" and "predicted_race" in headers
                    ):
                        predicted_label_col = "predicted_race"
            except Exception as exc:
                logger.debug("Column auto-detection skipped: %s", exc)

        ingestion = DataIngestionPipeline(
            config=IngestionConfig(
                true_label_col=true_label_col,
                predicted_label_col=predicted_label_col,
                race_col=race_col,
                gender_col=gender_col,
                age_col=age_col,
                dataset=dataset,
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
                metrics=metrics,
                records=records,
                output_report=output_report,
                model_name=model_name,
                dataset_name=dataset_name,
                protected_attr=protected_attr,
                explanations=explanations,
                backend=backend,
                backend_status=(
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
                model_description=model_description,
                dataset_limitations=result.label_limitations,
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
        model_description: str | None = None,
        dataset_limitations: tuple[str, ...] = (),
    ) -> Path:
        """Compile and save the offline compliance report."""
        logger.info("Compiling offline compliance report to: %s...", output_report)
        context_kwargs: dict[str, Any] = {
            "metrics": metrics,
            "model_name": model_name,
            "dataset_name": dataset_name,
            "protected_axis": protected_attr,
            "total_subjects": len(records),
            "explanations": explanations,
            "attributions": explanations,
            "backend": backend,
            "backend_status": backend_status,
            "dataset_limitations": dataset_limitations,
        }
        if model_description:
            context_kwargs["model_description"] = model_description

        context = ReportContext(**context_kwargs)
        generator = HTMLReportGenerator()
        saved_path = generator.save(context, output_report)
        logger.info("Audit complete. Standalone report saved to: %s", saved_path)
        return saved_path
