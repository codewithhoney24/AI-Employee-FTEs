@echo off
set /p service="Enter service name (whatsapp, ai_engine, backend, frontend): "
if exist logs\%service%.log (
    powershell -Command "Get-Content logs\%service%.log -Wait -Tail 20"
) else (
    echo Log file logs\%service%.log not found.
)
pause
