"""Unit tests for ReportReconciler and self-healing report engine."""

from __future__ import annotations

from pathlib import Path

from bias_aperture.report.metadata_registry import ModelMetadataRegistry
from bias_aperture.report.reconciler import (
    ReconciliationSummary,
    ReportReconciler,
)


def test_metadata_registry_known_models():
    """Verify ModelMetadataRegistry auto-resolves known architecture metadata."""
    resnet34 = ModelMetadataRegistry.resolve(
        "FairFace ResNet-34 Multi-Task Classifier", "race"
    )
    assert resnet34.parameters == "21.3 Million"
    assert "ResNet-34" in resnet34.architecture
    assert "Kärkkäinen" in resnet34.citation

    resnet50 = ModelMetadataRegistry.resolve(
        "ResNet-50 Gender Classifier (crangana/trained-gender)", "race"
    )
    assert resnet50.parameters == "25.6 Million"
    assert "ResNet-50" in resnet50.architecture

    mobilenet = ModelMetadataRegistry.resolve(
        "MobileNetV2 0.35 Rep Gender Classifier (Seeed SSCMA)", "race"
    )
    assert mobilenet.parameters == "3.5 Million"
    assert "MobileNetV2" in mobilenet.architecture

    vit = ModelMetadataRegistry.resolve(
        "HuggingFace ViT-B/16 Gender Classifier", "race"
    )
    assert vit.parameters == "86.6 Million"
    assert "ViT-B/16" in vit.architecture


def test_metadata_registry_unknown_model_fallback():
    """Verify unindexed models dynamically construct transparent descriptions."""
    unknown = ModelMetadataRegistry.resolve("CustomDeepNet-X99", "gender")
    assert "CustomDeepNet-X99" in unknown.name
    assert "Diagnostic" in unknown.intended_use
    assert "Custom Facial Analysis Model" in unknown.architecture


def test_reconciler_audit_detects_missing_directory(tmp_path: Path):
    """Verify ReportReconciler reports missing directories gracefully."""
    non_existent = tmp_path / "does_not_exist"
    issues = ReportReconciler.audit_dossiers(non_existent)
    assert len(issues) == 1
    assert issues[0].issue_type == "MISSING_DIR"


def test_reconciler_audit_detects_empty_directory(tmp_path: Path):
    """Verify ReportReconciler reports directories with no HTML files."""
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()
    issues = ReportReconciler.audit_dossiers(empty_dir)
    assert len(issues) == 1
    assert issues[0].issue_type == "NO_REPORTS"


def test_reconciler_audit_clean_on_live_reports():
    """Verify all 7 pre-compiled dossiers in report/ pass deterministic audit."""
    reconciler = ReportReconciler(Path("report"))
    issues = reconciler.audit_dossiers()
    assert issues == [], (
        f"Expected 0 audit issues, got {len(issues)}: {[i.message for i in issues]}"
    )


def test_reconciler_summary_properties():
    """Verify ReconciliationSummary property aliases function correctly."""
    summary = ReconciliationSummary(
        total_scanned=7,
        clean_count=7,
        issues=[],
        healed_reports=["rep1.html", "rep2.html"],
    )
    assert summary.scanned_count == 7
    assert summary.healed_count == 2
    assert summary.is_clean is True
