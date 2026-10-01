@echo off
setlocal
pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0sync.ps1" %*
if %ERRORLEVEL% NEQ 0 (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0sync.ps1" %*
)
endlocal
