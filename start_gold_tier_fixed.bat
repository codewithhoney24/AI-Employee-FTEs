@echo off
REM K-Electric AI Employee - Gold Tier FIXED
REM Proper Sequence: Bridge -> Executor -> Scanner

echo ============================================================
echo K-Electric AI Employee - GOLD TIER (FIXED)
echo ============================================================
echo.

REM Stop existing processes
echo [STOP] Cleaning up old processes...
powershell -Command "Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force"
powershell -Command "Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force"
timeout /t 2 /nobreak >nul

REM Start Services in CORRECT sequence
echo.
echo [START] 1. WhatsApp Gateway...
cd /d D:\AI-Employee-FTEs\api_employee_v2\whatsapp_gateway
start /B node server.js > D:\AI-Employee-FTEs\logs\whatsapp.log 2>&1
timeout /t 5 /nobreak >nul

echo [START] 2. AI Engine (WhatsApp Bridge + Approval)...
cd /d D:\AI-Employee-FTEs\api_employee_v2\ai_engine
start /B python -u app.py > D:\AI-Employee-FTEs\logs\ai_engine.log 2>&1
timeout /t 5 /nobreak >nul

echo [START] 3. LinkedIn Comments Scanner...
cd /d D:\AI-Employee-FTEs\KE_AI_Vault\scripts
start /B python -u linkedin_comments_scanner.py > D:\AI-Employee-FTEs\logs\linkedin_scanner.log 2>&1

echo.
echo ============================================================
echo All Services Started!
echo.
echo Running Services:
echo   - WhatsApp Gateway (Port 3001)
echo   - AI Engine (Port 5000)
echo   - LinkedIn Scanner (Background)
echo.
echo Check logs in .\logs\
echo ============================================================
echo.
echo Press any key to exit (services keep running)...
pause >nul