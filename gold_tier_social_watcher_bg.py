import os
import sys
import io
import time
import logging
import re
import requests
import tweepy
import webbrowser
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Unicode Fix for Windows Console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Load all potential .env locations
load_dotenv()
load_dotenv("KE_AI_Vault/facebook/.env")

# Configuration
VAULT_PATH = Path(os.getenv('VAULT_PATH', './KE_AI_Vault')).resolve()
SOCIAL_FOLDER = VAULT_PATH / 'Social_Media'
CHECK_INTERVAL = 60

# API Credentials
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN") or os.getenv("FACEBOOK_ACCESS_TOKEN") or os.getenv("IG_USER_ACCESS_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID") or os.getenv("FACEBOOK_PAGE_ID")
IG_BUSINESS_ID = os.getenv("IG_BUSINESS_ID") or os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID") or os.getenv("IG_USER_ID")

LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_PERSON_URN = os.getenv("LINKEDIN_PERSON_URN")

# WhatsApp Configuration
WHATSAPP_GATEWAY = "http://localhost:3001/send"
ADMIN_NUMBER = os.getenv("WHATSAPP_ADMIN_NUMBER", "923491379839").replace("+", "")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename="logs/watcher_bg.log",
    filemode='a'
)
logger = logging.getLogger(__name__)

class GoldTierSocialWatcherBG:
    def __init__(self):
        self.notified_drafts = set()

    def scan_for_drafts(self):
        drafts = []
        if not SOCIAL_FOLDER.exists():
            return drafts

        for file in SOCIAL_FOLDER.glob("*.md"):
            platform = file.name.split("_")[0].lower()
            if platform == "twitter/x": platform = "twitter"
            
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
            
            posts = re.split(r'---', content)
            for post in posts:
                if "[DRAFT]" in post:
                    caption_match = re.search(r'\*\*Caption\*\*:\s*\n?"(.*?)"', post, re.DOTALL)
                    if not caption_match:
                        caption_match = re.search(r'\*\*Caption\*\*:\s*\n?(.*?)\n\s*\*\*', post, re.DOTALL)
                    
                    if caption_match:
                        caption = caption_match.group(1).strip()
                        drafts.append({
                            "content": caption,
                            "platform": platform,
                            "file": file,
                            "raw_post": post.strip()
                        })
        return drafts

    def send_to_whatsapp(self, draft):
        """Sends the draft to WhatsApp for Master Approval."""
        try:
            msg = (
                f"🚀 *MASTER AGENT: NEW DRAFT READY*\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"📝 *PLATFORM:* {draft['platform'].upper()}\n"
                f"📝 *CONTENT:*\n\n{draft['content']}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"✅ Reply *YES* to post to ALL platforms."
            )
            requests.post(WHATSAPP_GATEWAY, json={
                "number": ADMIN_NUMBER,
                "message": msg
            })
            return True
        except Exception as e:
            logger.error(f"WhatsApp Notify Error: {e}")
            return False

    def run(self):
        print("🤖 Social Media Watcher is running in background (WhatsApp Mode).")
        while True:
            try:
                drafts = self.scan_for_drafts()
                for d in drafts:
                    key = d['content'][:30] + str(d['file'])
                    if key not in self.notified_drafts:
                        if self.send_to_whatsapp(d):
                            self.notified_drafts.add(key)
                            logger.info(f"Notified WhatsApp about draft in {d['file']}")
                
                time.sleep(CHECK_INTERVAL)
            except Exception as e:
                logger.error(f"Watcher Loop Error: {e}")
                time.sleep(10)

if __name__ == "__main__":
    GoldTierSocialWatcherBG().run()
