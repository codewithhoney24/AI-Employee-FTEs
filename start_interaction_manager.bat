@echo off
REM K-Electric AI Employee - Interaction Manager (Comments/Likes)
REM Start Interaction Services in the background using PowerShell Manager

echo ============================================================
echo K-Electric AI Employee - INTERACTION MANAGER
echo Starting Interaction Services (Comments/Likes Detection)...
echo ============================================================
echo.

REM Check for PowerShell
powershell -Command "exit" >nul 2>&1
if errorlevel 1 (
    echo ERROR: PowerShell is required to run this script!
    pause
    exit /b 1
)

REM Run the PowerShell manager script for interactions
powershell -ExecutionPolicy Bypass -File interaction_manager_control.ps1

echo.
echo ============================================================
echo Interaction Manager has been stopped.
echo ============================================================
pause
