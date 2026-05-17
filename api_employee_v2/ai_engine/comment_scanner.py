"""
Parallel Comment Scanner - Runs independently to check social media comments
Sends notifications to WhatsApp when new comments are found
"""

import os
import sys
import time
import requests
import json
from datetime import datetime

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

# Config
WHATSAPP_API = "http://localhost:3001/send"
ADMIN_NUMBER = os.getenv("WHATSAPP_ADMIN_NUMBER", "923491379839").replace("+", "")

# Social Media Config
FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
IG_BUSINESS_ID = os.getenv("IG_BUSINESS_ID") or os.getenv("IG_USER_ID")
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")

# State file
STATE_FILE = os.path.join(PROJECT_ROOT, "KE_AI_Vault", "Logs", "social_state.json")

def load_state():
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
                return set(data.get("replied_ids", []))
    except:
        pass
    return set()

def send_whatsapp(msg):
    try:
        requests.post(WHATSAPP_API, json={"number": ADMIN_NUMBER, "message": msg}, timeout=10)
    except Exception as e:
        print(f"WA Error: {e}")

def check_linkedin():
    """Check LinkedIn for new comments"""
    try:
        from skills.linkedin_skill import LinkedInSkill
        tasks = LinkedInSkill().check_my_comments()
        replied = load_state()
        for task in tasks:
            if task.get("id") not in replied:
                return task
    except Exception as e:
        print(f"LI Error: {e}")
    return None

def check_facebook():
    """Check Facebook for new comments"""
    try:
        replied = load_state()
        posts = requests.get(f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/feed?limit=2&access_token={FB_PAGE_ACCESS_TOKEN}").json().get("data", [])
        for p in posts:
            coms = requests.get(f"https://graph.facebook.com/v19.0/{p['id']}/comments?access_token={FB_PAGE_ACCESS_TOKEN}").json().get("data", [])
            for c in coms:
                if c["id"] not in replied:
                    return {"platform": "facebook", "id": c["id"], "text": c.get("message", ""), "user": c.get("from", {}).get("name", "Unknown")}
    except Exception as e:
        print(f"FB Error: {e}")
    return None

def check_instagram():
    """Check Instagram for new comments"""
    try:
        replied = load_state()
        media = requests.get(f"https://graph.facebook.com/v19.0/{IG_BUSINESS_ID}/media?limit=2&access_token={FB_PAGE_ACCESS_TOKEN}").json().get("data", [])
        for m in media:
            coms = requests.get(f"https://graph.facebook.com/v19.0/{m['id']}/comments?access_token={FB_PAGE_ACCESS_TOKEN}").json().get("data", [])
            for c in coms:
                if c["id"] not in replied:
                    return {"platform": "instagram", "id": c["id"], "text": c.get("text", ""), "user": c.get("username", "Unknown")}
    except Exception as e:
        print(f"IG Error: {e}")
    return None

# Track last notification to avoid spam
last_notification_time = 0
NOTIFICATION_COOLDOWN = 300  # 5 minutes between notifications

def main():
    global last_notification_time
    print("[COMMENT SCANNER] Started - Running in Parallel Mode")

    while True:
        try:
            # Check all platforms
            comment = check_linkedin()
            if not comment:
                comment = check_facebook()
            if not comment:
                comment = check_instagram()

            current_time = time.time()

            if comment and (current_time - last_notification_time) > NOTIFICATION_COOLDOWN:
                print(f"[COMMENT] Found: {comment['platform']} - {comment.get('user', 'Unknown')}")

                # Generate AI reply
                try:
                    from google import genai
                    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
                    prompt = f"User {comment.get('user', 'User')} commented on K-Electric {comment['platform']}: '{comment.get('text', '')[:200]}'. Short helpful reply (under 20 words)."
                    reply = client.models.generate_content(model="gemini-2.0-flash", contents=prompt).text.strip()
                except:
                    reply = "Thank you for engaging with K-Electric! ⚡"

                # Send to WhatsApp
                msg = f"""💬 *NEW COMMENT DETECTED*

━━━━━━━━━━━━━━━━━━━━━━
📝 *Platform:* {comment['platform'].upper()}
👤 *From:* {comment.get('user', 'Unknown')}
💬 *Comment:* {comment.get('text', '')[:150]}...
━━━━━━━━━━━━━━━━━━━━━━

🤖 *AI Reply:*
{reply}

━━━━━━━━━━━━━━━━━━━━━━

🔘 *REPLY WITH:*
✅ *YES* - Post Reply
❌ *NO* - Ignore"""

                send_whatsapp(msg)
                last_notification_time = current_time

        except Exception as e:
            print(f"Error: {e}")

        # Scan every 30 seconds
        time.sleep(30)

if __name__ == "__main__":
    main()