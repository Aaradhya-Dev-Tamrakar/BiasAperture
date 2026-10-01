@echo off
pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0sync.ps1" %*
