"""
BiasAperture Command-Line Interface (WP5 / System Orchestration).

Wires together the complete end-to-end diagnostic auditing pipeline:
    PredictionsFile / CSV / JSON
        ──► DataIngestionPipeline (Validation & Cohort Profiling)
        ──► CrossValidationOrchestrator (Fairlearn + AIF360 Consensus)
        ──► HTMLReportGenerator (Standalone Offline HTML Dossier)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from bias_aperture.data_ingestion import DataIngestionPipeline, IngestionConfig
from bias_aperture.explainability import ShapExplainerEngine
from bias_aperture.fairness import CrossValidationOrchestrator
from bias_aperture.report import HTMLReportGenerator, ReportContext


def build_parser() -> argparse.ArgumentParser:
    """Construct CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="bias-aperture",
        description=(
            "BiasAperture: Diagnostic Demographic Bias Auditing "
            "Platform for Computer Vision."
        ),
    )
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
        "--protected-attr",
        "-a",
        type=str,
        default="race",
        choices=["race", "gender", "age"],
        help="Demographic protected axis (default: race).",
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
        action="store_true",
        default=True,
        help=(
            "Enable conditional SHAP / surrogate explainability on flagged "
            "disparities (default: True)."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Main CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)

    pred_file = args.predictions_file
    if not pred_file.exists():
        print(f"[ERROR] Predictions file not found: {pred_file}", file=sys.stderr)
        return 1

    print("=" * 70)
    print(" BiasAperture — Demographic Bias Auditing Platform")
    print("=" * 70)
    print(f"[*] Ingesting predictions from: {pred_file}")
    print(f"[*] Protected demographic axis: {args.protected_attr}")

    # 1. Ingestion Pipeline
    ingestion = DataIngestionPipeline(
        config=IngestionConfig(
            true_label_col=args.true_label_col,
            predicted_label_col=args.predicted_label_col,
        )
    )
    result = ingestion.ingest_file(pred_file)
    records = result.records
    summary = result.validation_summary

    print(
        f"[*] Ingested {len(records)} valid records "
        f"({len(summary.issues)} validation warnings/errors)."
    )
    if not records:
        print("[ERROR] No valid SubjectRecords extracted.", file=sys.stderr)
        return 1

    # 2. Fairness Engine Execution
    print("[*] Running dual-backend fairness estimation (Fairlearn + AIF360)...")
    orchestrator = CrossValidationOrchestrator()
    metrics, divergences = orchestrator.run(records, protected_attr=args.protected_attr)

    print(f"[*] Evaluated {len(metrics)} metric rows across demographic strata.")
    if divergences:
        print(f"[!] Warning: {len(divergences)} cross-backend divergences detected.")

    # 3. Conditional Explainability Engine (SHAP / Proxy Attribution)
    if args.explain:
        print(
            "[*] Running conditional SHAP explainability engine on "
            "flagged disparities..."
        )
        explainer = ShapExplainerEngine()
        explained_count = 0
        for m in metrics:
            if explainer.should_explain(m):
                exp_res = explainer.explain_disparity(m, records=records)
                explained_count += 1
                if exp_res.feature_attributions:
                    top_feat = list(exp_res.feature_attributions.items())[0]
                    print(
                        f"    -> Flagged [{m.metric_name} | {m.subgroup}]: "
                        f"top proxy driver = {top_feat[0]} ({top_feat[1]:.3f})"
                    )
        print(
            f"[*] Generated targeted attributions for {explained_count} "
            "statistically flagged disparities."
        )

    # 4. Report Generation
    print(f"[*] Compiling offline compliance report to: {args.output_report}...")
    context = ReportContext(
        metrics=metrics,
        model_name=args.model_name,
        dataset_name=args.dataset_name,
        protected_axis=args.protected_attr,
        total_subjects=len(records),
    )
    generator = HTMLReportGenerator()
    saved_path = generator.save(context, args.output_report)

    print(f"[SUCCESS] Audit complete. Standalone report saved to:\n    {saved_path}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
