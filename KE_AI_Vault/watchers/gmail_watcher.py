import os
import time
import shutil
from datetime import datetime

# CONFIG
SOURCE_DIR = "D:/AI-Employee-FTEs/KE_AI_Vault/watchers/mock_data/gmail"
DEST_DIR = "D:/AI-Employee-FTEs/KE_AI_Vault/Needs_Action"
LOG_DIR = "D:/AI-Employee-FTEs/KE_AI_Vault/Logs"

os.makedirs(SOURCE_DIR, exist_ok=True)
os.makedirs(DEST_DIR, exist_ok=True)

def watch():
    print(f"📡 Gmail Watcher active. Monitoring {SOURCE_DIR}...")
    while True:
        files = [f for f in os.listdir(SOURCE_DIR) if f.endswith(".txt")]
        for f in files:
            source_path = os.path.join(SOURCE_DIR, f)
            dest_filename = f"EMAIL_{f.replace('.txt', '.md')}"
            dest_path = os.path.join(DEST_DIR, dest_filename)
            
            print(f"📩 New email detected: {f}")
            with open(source_path, 'r', encoding='utf-8') as src:
                content = src.read()
            
            with open(dest_path, 'w', encoding='utf-8') as dst:
                dst.write(f"---\nfrom: mock-sender@example.com\nsubject: {f}\ndate: {datetime.now().isoformat()}\n---\n\n{content}")
            
            os.remove(source_path)
            print(f"✅ Processed and moved to Needs_Action: {dest_filename}")
            
        time.sleep(10)

if __name__ == "__main__":
    watch()
