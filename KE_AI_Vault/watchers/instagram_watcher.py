import os
import time
from datetime import datetime

# CONFIG
SOURCE_DIR = "D:/AI-Employee-FTEs/KE_AI_Vault/watchers/mock_data/instagram"
DEST_DIR = "D:/AI-Employee-FTEs/KE_AI_Vault/Needs_Action"

os.makedirs(SOURCE_DIR, exist_ok=True)
os.makedirs(DEST_DIR, exist_ok=True)

def watch():
    print(f"📡 Instagram Watcher active. Monitoring {SOURCE_DIR}...")
    while True:
        files = [f for f in os.listdir(SOURCE_DIR) if f.endswith(".txt")]
        for f in files:
            source_path = os.path.join(SOURCE_DIR, f)
            dest_filename = f"IG_{f.replace('.txt', '.md')}"
            dest_path = os.path.join(DEST_DIR, dest_filename)
            
            print(f"📸 New Instagram DM: {f}")
            with open(source_path, 'r', encoding='utf-8') as src:
                content = src.read()
            
            with open(dest_path, 'w', encoding='utf-8') as dst:
                dst.write(f"---\nsource: Instagram\ntype: DM\ndate: {datetime.now().isoformat()}\n---\n\n{content}")
            
            os.remove(source_path)
            print(f"✅ Processed: {dest_filename}")
            
        time.sleep(10)

if __name__ == "__main__":
    watch()
