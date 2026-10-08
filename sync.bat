@echo off
setlocal
REM ============================================================================
REM Root compatibility forwarder to scripts\sync.bat
REM ============================================================================
call "%~dp0scripts\sync.bat" %*
exit /b %ERRORLEVEL%
