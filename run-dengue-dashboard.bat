@echo off
powershell -NoLogo -ExecutionPolicy Bypass -File "%~dp0run-dengue-dashboard.ps1"
exit /b %ERRORLEVEL%
