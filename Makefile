.PHONY: help install test lint format verify audit pdf sync clean

# Cross-platform environment resolution
ifeq ($(OS),Windows_NT)
	PYTHON ?= python
	SYNC_RUNNER = cmd /c scripts\sync.bat
else
	PYTHON ?= python3
	ifneq ($(shell which pwsh 2>/dev/null),)
		SYNC_RUNNER = pwsh -File ./scripts/sync.ps1
	else
		SYNC_RUNNER = ./scripts/sync.sh
	endif
endif

help:
	@echo "BiasAperture — Engineering & Build Automation"
	@echo ""
	@echo "Usage:"
	@echo "  make test        Run full test suite (pytest via uv)"
	@echo "  make lint        Run ruff linter check"
	@echo "  make format      Run ruff code formatter"
	@echo "  make verify      Run deterministic verification suite (AST, lint, SHA integrity)"
	@echo "  make audit       Run CLI audit pipeline on sample predictions"
	@echo "  make pdf         Export HTML compliance report to A4 PDF"
	@echo "  make sync        Synchronize across remotes (compulsory: origin, duo; optional: org)"
	@echo "  make install     Install project and development dependencies via uv"
	@echo "  make clean       Remove bytecode, pytest, and ruff cache artifacts"

install:
	uv sync --extra dev

test:
	uv run --extra dev pytest

lint:
	uv run --extra dev ruff check src/

format:
	uv run --extra dev ruff format src/

verify:
	$(PYTHON) scripts/verify.py

audit:
	uv run --extra dev bias-aperture --predictions data/examples/mock_predictions.json --output reports/

pdf:
	$(PYTHON) scripts/export_report_pdf.py reports/bias_audit_report.html reports/bias_audit_report.pdf

sync:
	$(SYNC_RUNNER) $(ARGS)

clean:
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').glob('.*_cache')]"
