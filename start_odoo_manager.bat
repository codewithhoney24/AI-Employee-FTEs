@echo off
REM K-Electric AI Employee - Odoo & Business Manager
REM Start Odoo and Business Services in the background using PowerShell Manager

echo ============================================================
echo K-Electric AI Employee - ODOO MANAGER
echo Starting Odoo, Accounting, and Business Services...
echo ============================================================
echo.

REM Check for PowerShell
powershell -Command "exit" >nul 2>&1
if errorlevel 1 (
    echo ERROR: PowerShell is required to run this script!
    pause
    exit /b 1
)

REM Run the PowerShell manager script for Odoo
powershell -ExecutionPolicy Bypass -File odoo_manager_control.ps1

echo.
echo ============================================================
echo Odoo Manager has been stopped.
echo ============================================================
pause
