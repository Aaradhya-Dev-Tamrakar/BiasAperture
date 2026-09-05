CONTEXT.md pasted first (paste that now if not already in this window).

You are user8 in the BiasAperture orchestrator. Task: task_2026-09-04_009.

Scope: Gate 1b only — the .tex Design Patterns table naming 5 fictitious classes.

Strike and replace:
- AuditOrchestrator → CrossValidationOrchestrator
- DirectInferenceAdapter/PredictionsFileAdapter → InProcessInterface/PredictionsFileInterface
- TestMatrixBuilder → DataIngestionPipeline
- ReportFactory/HTMLReportBuilder → HTMLReportGenerator
- AuditReport → (none — strike, no replacement; confirm no real equivalent exists in src/ before finalizing)

1. Probe: list_tasks to confirm pending. 2. claim_task(account="user8", task_id="task_2026-09-04_009"). 3. Post-claim list_tasks to verify.
4. Locate the exact .tex file/line for the Design Patterns table.
5. Cross-check each replacement class name actually exists in src/ (grep before asserting).
6. Draft the table diff.

READ-ONLY: draft diff only, no commit, no push, no sync.ps1.
Submit via submit_checkpoint(account="user8", task_id="task_2026-09-04_009", summary=..., result_text=<table diff + src/ grep evidence inline>).
