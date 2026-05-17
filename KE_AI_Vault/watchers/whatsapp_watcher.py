import os
import time
from datetime import datetime

# CONFIG
SOURCE_DIR = "D:/AI-Employee-FTEs/KE_AI_Vault/watchers/mock_data/whatsapp"
PENDING_DIR = "D:/AI-Employee-FTEs/KE_AI_Vault/Pending_Approval"
APPROVED_DIR = "D:/AI-Employee-FTEs/KE_AI_Vault/Approved"
DEST_DIR = "D:/AI-Employee-FTEs/KE_AI_Vault/Needs_Action"

os.makedirs(SOURCE_DIR, exist_ok=True)
os.makedirs(PENDING_DIR, exist_ok=True)
os.makedirs(APPROVED_DIR, exist_ok=True)

def watch():
    print(f"📡 WhatsApp Watcher active. Monitoring {SOURCE_DIR}...")
    while True:
        files = [f for f in os.listdir(SOURCE_DIR) if f.endswith(".txt")]
        for f in files:
            source_path = os.path.join(SOURCE_DIR, f)
            with open(source_path, 'r', encoding='utf-8') as src:
                content = src.read().strip().upper()
            
            # CHECK FOR APPROVAL COMMAND
            if content.startswith("YES "):
                filename = content.replace("YES ", "").strip()
                pending_path = os.path.join(PENDING_DIR, filename)
                if os.path.exists(pending_path):
                    print(f"✅ WhatsApp Approval Received for {filename}!")
                    shutil.move(pending_path, os.path.join(APPROVED_DIR, filename))
                    os.remove(source_path)
                    continue
                else:
                    print(f"⚠️ Approval failed: File {filename} not found in Pending.")

            # OTHERWISE TREAT AS REGULAR MESSAGE
            dest_filename = f"WA_{f.replace('.txt', '.md')}"
            dest_path = os.path.join(DEST_DIR, dest_filename)
            print(f"💬 New WhatsApp message: {f}")
            
            with open(dest_path, 'w', encoding='utf-8') as dst:
                dst.write(f"---\nsource: WhatsApp\nfrom: +923001234567\ndate: {datetime.now().isoformat()}\n---\n\n{content}")
            
            os.remove(source_path)
            print(f"✅ Processed: {dest_filename}")
            
        time.sleep(10)

if __name__ == "__main__":
    watch()
