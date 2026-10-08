@echo off
setlocal

if "%~1"=="" goto help
if /i "%~1"=="help" goto help

set "TARGET=%~1"
shift

if /i "%TARGET%"=="test" goto do_test
if /i "%TARGET%"=="lint" goto do_lint
if /i "%TARGET%"=="format" goto do_format
if /i "%TARGET%"=="verify" goto do_verify
if /i "%TARGET%"=="audit" goto do_audit
if /i "%TARGET%"=="pdf" goto do_pdf
if /i "%TARGET%"=="sync" goto do_sync
if /i "%TARGET%"=="install" goto do_install
if /i "%TARGET%"=="clean" goto do_clean

echo Unknown target: %TARGET%
echo Run 'make help' for available targets.
exit /b 1

:do_test
uv run --extra dev pytest %1 %2 %3 %4 %5 %6 %7 %8 %9
exit /b %ERRORLEVEL%

:do_lint
uv run --extra dev ruff check src/ %1 %2 %3 %4 %5 %6 %7 %8 %9
exit /b %ERRORLEVEL%

:do_format
uv run --extra dev ruff format src/ %1 %2 %3 %4 %5 %6 %7 %8 %9
exit /b %ERRORLEVEL%

:do_verify
python scripts\verify.py %1 %2 %3 %4 %5 %6 %7 %8 %9
exit /b %ERRORLEVEL%

:do_audit
uv run --extra dev bias-aperture --predictions data\examples\mock_predictions.json --output reports\ %1 %2 %3 %4 %5 %6 %7 %8 %9
exit /b %ERRORLEVEL%

:do_pdf
python scripts\export_report_pdf.py reports\bias_audit_report.html reports\bias_audit_report.pdf %1 %2 %3 %4 %5 %6 %7 %8 %9
exit /b %ERRORLEVEL%

:do_sync
call "%~dp0scripts\sync.bat" %1 %2 %3 %4 %5 %6 %7 %8 %9
exit /b %ERRORLEVEL%

:do_install
uv sync --extra dev %1 %2 %3 %4 %5 %6 %7 %8 %9
exit /b %ERRORLEVEL%

:do_clean
python -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').glob('.*_cache')]"
exit /b 0

:help
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
