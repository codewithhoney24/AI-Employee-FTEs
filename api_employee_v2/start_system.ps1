# Start AI Employee API System (v2)

Write-Host "🚀 Starting WhatsApp Gateway (Node.js)..." -ForegroundColor Cyan
Start-Process -NoNewWindow -FilePath "node" -ArgumentList "server.js" -WorkingDirectory "D:\AI-Employee-FTEs\api_employee_v2\whatsapp_gateway"

Write-Host "🧠 Starting AI Engine (Python)..." -ForegroundColor Green
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "app.py" -WorkingDirectory "D:\AI-Employee-FTEs\api_employee_v2\ai_engine"

Write-Host "✅ System started in the background." -ForegroundColor Yellow
Write-Host "Please check the WhatsApp Gateway terminal for the QR code if you are not logged in."
Write-Host "Logs are being output to this terminal."
