import os
import time
from datetime import datetime

# CONFIG
SOURCE_DIR = "D:/AI-Employee-FTEs/KE_AI_Vault/watchers/mock_data/banking"
DEST_DIR = "D:/AI-Employee-FTEs/KE_AI_Vault/Needs_Action"

os.makedirs(SOURCE_DIR, exist_ok=True)
os.makedirs(DEST_DIR, exist_ok=True)

RATES_FILE = "D:/AI-Employee-FTEs/KE_AI_Vault/Accounting/Rates.md"

def get_pricing_context():
    if os.path.exists(RATES_FILE):
        with open(RATES_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    return "No rates file found."

def watch():
    print(f"📡 Banking Watcher active. Monitoring {SOURCE_DIR}...")
    while True:
        files = [f for f in os.listdir(SOURCE_DIR) if f.endswith(".txt")]
        for f in files:
            source_path = os.path.join(SOURCE_DIR, f)
            dest_filename = f"BANK_{f.replace('.txt', '.md')}"
            dest_path = os.path.join(DEST_DIR, dest_filename)
            
            print(f"💰 New Bank Transaction: {f}")
            with open(source_path, 'r', encoding='utf-8') as src:
                content = src.read()
            
            rates = get_pricing_context()
            
            with open(dest_path, 'w', encoding='utf-8') as dst:
                dst.write(f"---\nsource: Banking\ntype: Transaction\ndate: {datetime.now().isoformat()}\nstatus: needs_audit\n---\n\n# Transaction Details\n{content}\n\n# Audit Reference (Current Rates)\n{rates}")
            
            os.remove(source_path)
            print(f"✅ Processed: {dest_filename}")
            
        time.sleep(10)

if __name__ == "__main__":
    watch()
