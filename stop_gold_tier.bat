@echo off
REM Stop Gold Tier Services

echo ============================================================
echo Stopping K-Electric AI Employee Services
echo ============================================================

echo Stopping Python processes...
powershell -Command "Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force"

echo Stopping Node processes...
powershell -Command "Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force"

echo Stopping Chrome/Chromium...
powershell -Command "Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force"

echo.
echo All services stopped!
echo ============================================================
pause