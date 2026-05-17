import os
import sys
import requests
import time
import re
from dotenv import load_dotenv

# =========================
# CONFIG & ENV
# =========================

# Ensure we are in the right directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "../../.env"), override=True)
load_dotenv(os.path.join(BASE_DIR, "../../KE_AI_Vault/facebook/.env"), override=True)

WHATSAPP_API = "http://localhost:3001/send"
ADMIN_NUMBER = os.getenv("WHATSAPP_ADMIN_NUMBER", "923491379839").replace("+", "")
VAULT_PATH = os.path.abspath(os.path.join(BASE_DIR, "../../KE_AI_Vault"))

# =========================
# VAULT PARSER
# =========================

def scan_vault_for_drafts():
    social_folder = os.path.join(VAULT_PATH, "Social_Media")
    if not os.path.exists(social_folder):
        return None

    files = [f for f in os.listdir(social_folder) if f.endswith(".md")]
    for filename in files:
        platform = filename.split("_")[0].lower()
        if platform == "twitter": continue # Skip Twitter
        
        filepath = os.path.join(social_folder, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        posts = re.split(r'---', content)
        for post in posts:
            if "[DRAFT]" in post:
                caption_match = re.search(r'\*\*Caption\*\*:\s*\n?"(.*?)"', post, re.DOTALL)
                if not caption_match:
                    caption_match = re.search(r'\*\*Caption\*\*:\s*\n?(.*?)\n\s*\*\*', post, re.DOTALL)
                
                if caption_match:
                    caption = caption_match.group(1).strip()
                else:
                    lines = [line.strip() for line in post.split('\n') if line.strip()]
                    valid_lines = []
                    for line in lines:
                        if line.startswith('#') or line.startswith('**Status**'): continue
                        if "[DRAFT]" in line: break
                        valid_lines.append(line)
                    caption = "\n".join(valid_lines).strip().replace('"', '')

                if caption:
                    return {"content": caption, "platform": platform, "file": filepath, "raw_post": post.strip()}
    return None

def send_whatsapp(msg):
    try:
        print(f"📤 Sending WhatsApp notification...")
        r = requests.post(WHATSAPP_API, json={"number": ADMIN_NUMBER, "message": msg}, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"❌ WhatsApp Error: {e}")
        return False

# =========================
# RALPH WIGGUM WATCHER
# =========================

def run_watcher():
    print("🚀 RALPH WIGGUM WATCHER: Started (Separate Process)")
    print(f"📂 Monitoring: {VAULT_PATH}")
    
    while True:
        try:
            # Check if AI Engine is currently processing something
            # (We use a simple state check or just let it notify)
            # For simplicity, we check if the draft is still [DRAFT] in vault
            
            draft = scan_vault_for_drafts()
            if draft:
                print(f"🎯 Draft Detected: {draft['platform']}")
                
                msg = (
                    f"🚀 *RALPH WIGGUM: TASK DETECTED*\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n"
                    f"📝 *PLATFORM:* {draft['platform'].upper()}\n"
                    f"📝 *CONTENT:*\n\n{draft['content']}\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n"
                    f"✅ *YES* - Execute Task\n"
                    f"❌ *NO* - Reject Task"
                )
                
                if send_whatsapp(msg):
                    print("✅ Notification delivered. Waiting for approval...")
                    # Wait 5 minutes before reminding, or wait for status change
                    time.sleep(300) 
                else:
                    print("⚠️ Notify failed. Retrying in 30s...")
                    time.sleep(30)
            else:
                print("💤 No pending drafts. Standing by...")
                time.sleep(60)
                
        except Exception as e:
            print(f"🚨 Watcher Error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    run_watcher()
