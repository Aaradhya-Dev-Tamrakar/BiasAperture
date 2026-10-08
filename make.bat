@echo off
setlocal

set "TARGET=%~1"
if "%TARGET%"=="" set "TARGET=help"

set "ARGS="
:arg_loop
shift
if "%~1"=="" goto dispatch
set "ARGS=%ARGS% %1"
goto arg_loop

:dispatch
if /i "%TARGET%"=="help" (
    echo BiasAperture — Engineering ^& Build Automation
    echo.
    echo Usage:
    echo   make test        Run full test suite [pytest via uv]
    echo   make lint        Run ruff linter check
    echo   make format      Run ruff code formatter
    echo   make verify      Run deterministic verification suite [AST, lint, SHA integrity]
    echo   make audit       Run CLI audit pipeline on sample predictions
    echo   make pdf         Export HTML compliance report to A4 PDF
    echo   make sync        Synchronize across remotes [compulsory: origin, duo; optional: org]
    echo   make install     Install project and development dependencies via uv
    echo   make clean       Remove bytecode, pytest, and ruff cache artifacts
    exit /b 0
)

if /i "%TARGET%"=="test" (
    uv run --extra dev pytest%ARGS%
    exit /b %ERRORLEVEL%
)

if /i "%TARGET%"=="lint" (
    uv run --extra dev ruff check src/%ARGS%
    exit /b %ERRORLEVEL%
)

if /i "%TARGET%"=="format" (
    uv run --extra dev ruff format src/%ARGS%
    exit /b %ERRORLEVEL%
)

if /i "%TARGET%"=="verify" (
    python scripts\verify.py%ARGS%
    exit /b %ERRORLEVEL%
)

if /i "%TARGET%"=="audit" (
    uv run --extra dev bias-aperture --predictions data\examples\mock_predictions.json --output reports\%ARGS%
    exit /b %ERRORLEVEL%
)

if /i "%TARGET%"=="pdf" (
    python scripts\export_report_pdf.py reports\bias_audit_report.html reports\bias_audit_report.pdf%ARGS%
    exit /b %ERRORLEVEL%
)

if /i "%TARGET%"=="sync" (
    call "%~dp0scripts\sync.bat"%ARGS%
    exit /b %ERRORLEVEL%
)

if /i "%TARGET%"=="install" (
    uv sync --extra dev%ARGS%
    exit /b %ERRORLEVEL%
)

if /i "%TARGET%"=="clean" (
    python -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').glob('.*_cache')]"
    exit /b 0
)

echo Unknown target: %TARGET%
echo Run 'make help' for available targets.
exit /b 1
