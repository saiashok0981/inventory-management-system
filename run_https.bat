@echo off
REM Run HTTPS Server - Windows Batch File

echo.
echo ============================================================
echo Checking Python installation...
echo ============================================================

python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

echo.
echo ============================================================
echo Starting HTTPS Server...
echo ============================================================
echo.
echo Server URL: https://localhost:8000
echo Docs:       https://localhost:8000/docs
echo ReDoc:      https://localhost:8000/redoc
echo.
echo Note: You may see SSL certificate warnings - this is normal
echo       for self-signed certificates in local development.
echo.

python run_https.py

