# K-Electric AI Employee - Gold Tier Master Startup Script (Windows)

Write-Host ">>> Starting Gold Tier AI Employee System..." -ForegroundColor Yellow

# 1. Start Backend (Dashboard API)
Write-Host ">>> Launching Backend API..." -ForegroundColor Cyan
Start-Process python -ArgumentList "backend/main.py" -WindowStyle Hidden

# 2. Start Orchestrator (The Brain)
Write-Host ">>> Launching Gemini Orchestrator..." -ForegroundColor Magenta
Start-Process python -ArgumentList "KE_AI_Vault/scripts/gemini_orchestrator.py" -WindowStyle Hidden

# 3. Start Social Executor (Visual Hands / Playwright)
Write-Host ">>> Launching Social Executor (Browser Automation)..." -ForegroundColor Green
Start-Process python -ArgumentList "KE_AI_Vault/scripts/social_executor.py"

# 3b. Start Approval Bridge (WhatsApp Notifier)
Write-Host ">>> Launching Approval Bridge (WhatsApp Notifier)..." -ForegroundColor Cyan
Start-Process python -ArgumentList "KE_AI_Vault/scripts/approval_bridge.py"

# 4. Start Watchers (The Senses)
Write-Host ">>> Activating All Watchers (Gmail, WhatsApp, FB, IG, X, Odoo, Banking)..." -ForegroundColor Yellow
$watchers = @(
    "KE_AI_Vault/watchers/gmail_watcher.py",
    "KE_AI_Vault/watchers/whatsapp_watcher.py",
    "KE_AI_Vault/watchers/facebook_watcher.py",
    "KE_AI_Vault/watchers/instagram_watcher.py",
    "KE_AI_Vault/watchers/twitter_watcher.py",
    "KE_AI_Vault/watchers/odoo_sync_watcher.py",
    "KE_AI_Vault/watchers/banking_watcher.py"
)

foreach ($watcher in $watchers) {
    if (Test-Path $watcher) {
        Write-Host "  -> Starting: $watcher"
        Start-Process python -ArgumentList $watcher -WindowStyle Hidden
    } else {
        Write-Host "  !! Not Found: $watcher" -ForegroundColor Red
    }
}

Write-Host "`nDONE: GOLD TIER SYSTEM IS LIVE!" -ForegroundColor Green
Write-Host "Dashboard: http://localhost:3000"
Write-Host "Social Executor window open. Watchers running in background."
Write-Host "To stop everything, run: Stop-Process -Name python"
