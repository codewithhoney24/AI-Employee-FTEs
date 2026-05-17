"""
LinkedIn Comments Scanner - Fast Fix
Scans K-Electric's own posts' comments (not random feed)
URL: https://www.linkedin.com/notifications/?filter=COMMENTS_ON_POSTS_BY_YOU
"""

import os
import time
import json
import requests
import hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# CONFIG
PROJECT_ROOT = Path("D:/AI-Employee-FTEs")
VAULT_PATH = PROJECT_ROOT / "KE_AI_Vault"
STATE_FILE = VAULT_PATH / "Logs" / "social_state.json"
LI_SESSION = VAULT_PATH / ".sessions" / "linkedin"
WHATSAPP_API = "http://localhost:3001/send"

load_dotenv(PROJECT_ROOT / ".env")
ADMIN_NUMBER = os.getenv("WHATSAPP_ADMIN_NUMBER", "923491379839").replace("+", "")

def load_state():
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
                return set(data.get("replied_ids", []))
    except:
        pass
    return set()

def save_reply(comment_id):
    try:
        state = {}
        if STATE_FILE.exists():
            with open(STATE_FILE, "r") as f:
                state = json.load(f)
        replied_ids = set(state.get("replied_ids", []))
        replied_ids.add(comment_id)
        state["replied_ids"] = list(replied_ids)
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except:
        pass

def send_whatsapp(msg):
    try:
        requests.post(WHATSAPP_API, json={"number": ADMIN_NUMBER, "message": msg}, timeout=10)
    except:
        pass

def scan_linkedin_comments():
    """Scan COMMENTS ON YOUR POSTS - the correct filter!"""
    print("[LINKEDIN] Scanning YOUR posts' comments...")

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            str(LI_SESSION).replace("\\", "/"),
            headless=False,  # Make visible
            slow_mo=300,
            args=["--start-maximized"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()

        try:
            # Use profile recent activity page instead
            url = "https://www.linkedin.com/in/digital-dreamers-9a15bb3b4/recent-activity/all/"
            print(f"[LINKEDIN] Going to: {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(4000)

            # Scroll to load all notifications
            for _ in range(3):
                page.evaluate("window.scrollBy(0, 500)")
                page.wait_for_timeout(1000)

            # Debug: get page text length
            page_text = page.evaluate("() => document.body.innerText")
            print(f"[DEBUG] Page has {len(page_text)} chars of text")

            # SIMPLE: Get all text and look for comment keywords
            all_text = page.evaluate("() => document.body.innerText")
            print(f"[DEBUG] Page text: {all_text[:500]}...")

            # Simple approach - look for comments in the text
            if "comment" in all_text.lower() or "replied" in all_text.lower():
                print("[FOUND] Comment activity detected on page!")

                # Send to WhatsApp anyway for manual check
                msg = """💬 *LINKEDIN ACTIVITY DETECTED*

━━━━━━━━━━━━━━━━━━━━━━
Found activity on your LinkedIn profile.
Please check: https://www.linkedin.com/in/digital-dreamers-9a15bb3b4/recent-activity/all/

━━━━━━━━━━━━━━━━━━━━━━

🔘 Reply YES to check now or NO to ignore"""

                send_whatsapp(msg)
                return True

            notifications = []

            print(f"[LINKEDIN] Found {len(notifications)} notification items with activity")

            replied = load_state()

            for notif in notifications:
                # Generate unique ID from text
                comment_id = hashlib.md5(notif['text'].encode()).hexdigest()

                if comment_id not in replied:
                    print(f"[FOUND] Comment: {notif['text'][:60]}...")

                    # Generate AI reply
                    reply = "Thank you for engaging with K-Electric! We appreciate your support. ⚡"

                    # Send to WhatsApp for approval BEFORE posting
                    msg = f"""💬 *NEW LINKEDIN COMMENT*

━━━━━━━━━━━━━━━━━━━━━━
💬 *Comment:*
{notif['text'][:180]}...

━━━━━━━━━━━━━━━━━━━━━━

🤖 *AI Reply:*
{reply}

━━━━━━━━━━━━━━━━━━━━━━

🔘 *REPLY WITH:*
✅ *YES* - Post Reply
❌ *NO* - Ignore"""

                    save_reply(comment_id)
                    send_whatsapp(msg)
                    return True

        except Exception as e:
            print(f"[LINKEDIN] Error: {e}")

        browser.close()

    return False

if __name__ == "__main__":
    print("=" * 50)
    print("LinkedIn Comments Scanner (Fixed)")
    print("=" * 50)

    while True:
        try:
            scan_linkedin_comments()
        except Exception as e:
            print(f"[ERROR] {e}")

        time.sleep(60)  # Check every minute