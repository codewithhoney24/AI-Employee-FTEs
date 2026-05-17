# K-Electric AI Employee - Gold Tier Control Script
# This script manages background services and the interactive social watcher.

$LogDir = "logs"
if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir
}

function Stop-Services {
    Write-Host "Cleaning up existing processes on ports 3000, 3001, 5000, 8000..." -ForegroundColor Yellow
    $Ports = @(3000, 3001, 5000, 8000)
    foreach ($Port in $Ports) {
        $Proc = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        if ($Proc) {
            Write-Host "Killing process on port $Port (PID: $($Proc.OwningProcess[0]))..." -ForegroundColor Cyan
            Stop-Process -Id $Proc.OwningProcess[0] -Force -ErrorAction SilentlyContinue
        }
    }
}

function Start-Services {
    Write-Host "Starting Master Agent Services..." -ForegroundColor Green

    # 1. WhatsApp Gateway
    Write-Host "[1/4] Starting WhatsApp Gateway (Port 3001)..."
    $env:NODE_OPTIONS = "--max-old-space-size=256"
    Start-Process -FilePath "node" -ArgumentList "server.js" -WorkingDirectory "api_employee_v2\whatsapp_gateway" -NoNewWindow -RedirectStandardOutput "$LogDir\whatsapp.log" -RedirectStandardError "$LogDir\whatsapp_error.log"
    Start-Sleep -Seconds 3

    # Open WhatsApp FIRST
    Write-Host "Opening WhatsApp..." -ForegroundColor Cyan
    Start-Process "whatsapp:" -ErrorAction SilentlyContinue

    # 2. AI Engine
    Write-Host "[2/4] Starting AI Engine (Port 5000)..."
    $env:SCAN_MODE = "POSTING"
    Start-Process -FilePath "python" -ArgumentList "-u app.py" -WorkingDirectory "api_employee_v2\ai_engine" -NoNewWindow -RedirectStandardOutput "$LogDir\ai_engine.log" -RedirectStandardError "$LogDir\ai_engine_error.log"
    Start-Sleep -Seconds 5

    # 3. FastAPI Backend
    Write-Host "[3/4] Starting Backend API (Port 8000)..."
    Start-Process -FilePath "uvicorn" -ArgumentList "main:app --port 8000 --no-access-log" -WorkingDirectory "backend" -NoNewWindow -RedirectStandardOutput "$LogDir\backend.log" -RedirectStandardError "$LogDir\backend_error.log"
    Start-Sleep -Seconds 2

    # 4. Next.js Dashboard
    Write-Host "[4/4] Starting Dashboard (Port 3000)..."
    Start-Process -FilePath "npm.cmd" -ArgumentList "run dev" -WorkingDirectory "frontend" -NoNewWindow -RedirectStandardOutput "$LogDir\frontend.log" -RedirectStandardError "$LogDir\frontend_error.log"
    Start-Sleep -Seconds 8

    Write-Host "Services Initialized." -ForegroundColor Green

    # Status Check
    Start-Sleep -Seconds 5

    $StatusTable = @()
    $Services = @(
        @{Name="WhatsApp Gateway"; Port=3001},
        @{Name="AI Engine"; Port=5000},
        @{Name="Backend API"; Port=8000},
        @{Name="Dashboard"; Port=3000}
    )

    foreach ($S in $Services) {
        $Conn = Get-NetTCPConnection -LocalPort $S.Port -ErrorAction SilentlyContinue
        $Status = if ($Conn) { "RUNNING" } else { "OFFLINE" }
        $StatusTable += New-Object PSObject -Property @{ Service = $S.Name; Status = $Status }
    }
    $StatusTable | Format-Table -Property Service, Status

    # Open Dashboard
    Write-Host "Opening Dashboard..." -ForegroundColor Cyan
    Start-Process "http://localhost:3000"
}

# Main Execution
Stop-Services
Start-Services

Write-Host "MASTER AGENT IS ACTIVE" -ForegroundColor Green
Write-Host "1. Dashboard: http://localhost:3000"
Write-Host "2. WhatsApp: Open"
Write-Host "3. AI Engine: Running"
Write-Host "=========================================="

Write-Host "Press Ctrl+C to STOP" -ForegroundColor Yellow

# Keep script running
while($true) { Start-Sleep -Seconds 60 }