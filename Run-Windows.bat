@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\run-local.ps1"
if errorlevel 1 (
  echo.
  echo MolOOD Explorer stopped with an error.
  pause
  exit /b 1
)

