@echo off
REM K-Electric AI Employee - Gold Tier Full Automation (V2 Optimized)
REM Start ALL Services in the background using PowerShell Manager

echo ============================================================
echo K-Electric AI Employee - GOLD TIER (Optimized)
echo Starting Services in the background...
echo ============================================================
echo.

REM Check for PowerShell
powershell -Command "exit" >nul 2>&1
if errorlevel 1 (
    echo ERROR: PowerShell is required to run this script!
    pause
    exit /b 1
)

REM Run the PowerShell manager script
REM This will:
REM 1. Kill old processes
REM 2. Start background services (WhatsApp, AI Engine, Backend, Dashboard)
REM 3. Redirect logs to .\logs\
REM 4. Start the interactive Social Watcher in THIS window.

powershell -ExecutionPolicy Bypass -File gold_tier_control.ps1

echo.
echo ============================================================
echo All services have been stopped.
echo ============================================================
pause

