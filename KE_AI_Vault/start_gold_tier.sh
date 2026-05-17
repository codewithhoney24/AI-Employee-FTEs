#!/bin/bash

# K-Electric AI Employee - Gold Tier Master Startup Script (Linux/Mac)

echo "🚀 Starting Gold Tier AI Employee System..."

# 1. Start Backend
python3 backend/main.py &

# 2. Start Orchestrator
python3 KE_AI_Vault/scripts/gemini_orchestrator.py &

# 3. Start Social Executor
python3 KE_AI_Vault/scripts/social_executor.py &

# 4. Start Watchers
watchers=(
    "KE_AI_Vault/watchers/gmail_watcher.py"
    "KE_AI_Vault/watchers/whatsapp_watcher.py"
    "KE_AI_Vault/watchers/facebook_watcher.py"
    "KE_AI_Vault/watchers/instagram_watcher.py"
    "KE_AI_Vault/watchers/twitter_watcher.py"
    "KE_AI_Vault/watchers/odoo_sync_watcher.py"
    "KE_AI_Vault/watchers/banking_watcher.py"
)

for watcher in "${watchers[@]}"; do
    echo "  → Starting: $watcher"
    python3 "$watcher" &
done

echo "✅ GOLD TIER SYSTEM IS LIVE!"
wait
