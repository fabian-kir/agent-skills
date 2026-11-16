@echo off
:: ─────────────────────────────────────────────────────────────
::  {{PROJECT_NAME}} — Windows launcher. Double-click to start.
:: ─────────────────────────────────────────────────────────────
setlocal EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo   {{PROJECT_NAME}} -- starting...
echo.

:: ── 1. Find Python 3 ─────────────────────────────────────────
set PYTHON=
python --version >nul 2>&1
if %errorlevel% equ 0 (
  for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
  if "!PYVER:~0,1!"=="3" set PYTHON=python
)
if "!PYTHON!"=="" (
  python3 --version >nul 2>&1
  if %errorlevel% equ 0 set PYTHON=python3
)
if "!PYTHON!"=="" (
  echo   ERROR: Python 3 not found.
  echo   Install from https://www.python.org/downloads/
  echo   Important: tick "Add Python to PATH" during setup.
  pause
  exit /b 1
)
for /f "tokens=2" %%v in ('!PYTHON! --version 2^>^&1') do set PYVER=%%v
echo   Python: !PYVER!

:: ── 2. Virtualenv (device-local, NOT in the shared folder) ───
set VENV_DIR=%LOCALAPPDATA%\{{PROJECT_SLUG}}\venv
if not exist "%VENV_DIR%" (
  echo   Creating local virtualenv ^(off the shared drive^)...
  mkdir "%LOCALAPPDATA%\{{PROJECT_SLUG}}" 2>nul
  !PYTHON! -m venv "%VENV_DIR%"
  if %errorlevel% neq 0 ( echo   ERROR creating virtualenv. & pause & exit /b 1 )
)
call "%VENV_DIR%\Scripts\activate.bat"
if %errorlevel% neq 0 ( echo   ERROR activating virtualenv. & pause & exit /b 1 )

echo   Checking requirements...
pip install -r requirements.txt --quiet --disable-pip-version-check
if %errorlevel% neq 0 ( echo   ERROR installing requirements. & pause & exit /b 1 )

echo.
echo   Ready. Server on http://localhost:{{PORT}}  (Ctrl+C to stop)
echo.
python server.py
pause
