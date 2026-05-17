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
CHECK_INTERVAL = 30

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
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class GoldTierSocialWatcher:
    def __init__(self):
        self.processed_drafts = set()
        self.notified_drafts = set()
        
    def start(self):
        print("\n" + "="*80)
        print("🚀 GOLD TIER SOCIAL WATCHER - K-ELECTRIC")
        print("="*80)
        print(f"  Monitoring: {SOCIAL_FOLDER}")
        print("  Platforms: Twitter, Facebook, Instagram, LinkedIn")
        print("  Press Ctrl+C to stop")
        print("="*80)

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
                f"🚀 *MASTER AGENT: NEW DRAFT DETECTED*\n"
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

    def post_to_twitter(self, content):
        try:
            client = tweepy.Client(
                consumer_key=TWITTER_API_KEY,
                consumer_secret=TWITTER_API_SECRET,
                access_token=TWITTER_ACCESS_TOKEN,
                access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
            )
            response = client.create_tweet(text=content)
            return response.data['id']
        except Exception as e:
            logger.error(f"Twitter Error: {e}")
            return None

    def post_to_facebook(self, content):
        try:
            url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/feed"
            payload = {"message": content, "access_token": FB_PAGE_ACCESS_TOKEN}
            r = requests.post(url, data=payload)
            res = r.json()
            return res.get("id")
        except Exception as e:
            logger.error(f"Facebook Error: {e}")
            return None

    def post_to_instagram(self, content):
        try:
            if not IG_BUSINESS_ID: return None
            image_url = "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?auto=format&fit=crop&w=1000"
            container_url = f"https://graph.facebook.com/v19.0/{IG_BUSINESS_ID}/media"
            container_payload = {"caption": content, "image_url": image_url, "access_token": FB_PAGE_ACCESS_TOKEN}
            r1 = requests.post(container_url, data=container_payload)
            res1 = r1.json()
            if "id" in res1:
                publish_url = f"https://graph.facebook.com/v19.0/{IG_BUSINESS_ID}/media_publish"
                r2 = requests.post(publish_url, data={"creation_id": res1["id"], "access_token": FB_PAGE_ACCESS_TOKEN})
                return r2.json().get("id")
            return None
        except Exception as e:
            logger.error(f"Instagram Error: {e}")
            return None

    def post_to_linkedin(self, content):
        """Post content to LinkedIn and return the post URN if successful.
        Returns the URN from the 'x-linkedin-id' header.
        """
        try:
            if not LINKEDIN_ACCESS_TOKEN or not LINKEDIN_PERSON_URN:
                return None
            url = "https://api.linkedin.com/rest/posts"
            headers = {
                "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
                "X-Restli-Protocol-Version": "2.0.0",
                "LinkedIn-Version": "202404",
                "Content-Type": "application/json"
            }
            payload = {
                "author": LINKEDIN_PERSON_URN,
                "commentary": content,
                "visibility": "PUBLIC",
                "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": []},
                "lifecycleState": "PUBLISHED"
            }
            r = requests.post(url, headers=headers, json=payload)
            if r.status_code == 201:
                return r.headers.get("x-linkedin-id") or "SUCCESS"
            return None
        except Exception as e:
            logger.error(f"LinkedIn Error: {e}")
            return None

    def fetch_linkedin_comments(self, post_urn):
        """Fetch comment URNs for a LinkedIn post.
        Returns a list of comment URNs.
        """
        try:
            if not LINKEDIN_ACCESS_TOKEN:
                return []
            post_id = post_urn.split(":")[-1]
            url = f"https://api.linkedin.com/v2/socialActions/urn:li:share:{post_id}/comments"
            headers = {"Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}"}
            r = requests.get(url, headers=headers)
            if r.status_code != 200:
                logger.error(f"LinkedIn comments fetch failed: {r.status_code} {r.text}")
                return []
            data = r.json()
            return [c.get('entity') for c in data.get('elements', []) if c.get('entity')]
        except Exception as e:
            logger.error(f"LinkedIn fetch comments error: {e}")
            return []

    def get_linkedin_comment_text(self, comment_urn):
        """Fetch the text of a LinkedIn comment given its URN.
        Returns the comment message string or empty string on failure.
        """
        try:
            if not LINKEDIN_ACCESS_TOKEN:
                return ""
            # The comment URN can be used directly in the endpoint path
            # Example: https://api.linkedin.com/v2/comments/{comment_urn}
            url = f"https://api.linkedin.com/v2/comments/{comment_urn}"
            headers = {"Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}"}
            r = requests.get(url, headers=headers)
            if r.status_code != 200:
                logger.error(f"Failed to fetch comment {comment_urn}: {r.status_code} {r.text}")
                return ""
            data = r.json()
            # LinkedIn comment payload may have 'message' -> 'text'
            return data.get('message', {}).get('text', '')
        except Exception as e:
            logger.error(f"Error fetching comment {comment_urn}: {e}")
            return ""

    def reply_to_linkedin_comment(self, comment_urn, reply_text):
        """Reply to a LinkedIn comment identified by its URN. Returns True on success."""
        try:
            if not LINKEDIN_ACCESS_TOKEN:
                return False
            url = "https://api.linkedin.com/rest/comments"
            headers = {
                "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
                "X-Restli-Protocol-Version": "2.0.0",
                "Content-Type": "application/json"
            }
            payload = {"object": comment_urn, "message": {"text": reply_text}}
            r = requests.post(url, headers=headers, json=payload)
            return r.status_code in (200, 201)
        except Exception as e:
            logger.error(f"LinkedIn reply error: {e}")
            return False

    def update_vault_status(self, draft, new_status):
        try:
            with open(draft["file"], "r", encoding="utf-8") as f:
                content = f.read()
            updated_post = draft["raw_post"].replace("[DRAFT]", f"[{new_status}]")
            new_content = content.replace(draft["raw_post"], updated_post)
            with open(draft["file"], "w", encoding="utf-8") as f:
                f.write(new_content)
            return True
        except Exception as e:
            logger.error(f"Vault Update Error: {e}")
            return False

    def show_prompt(self, draft):
        print("\n" + "="*80)
        print("📢 NEW SOCIAL MEDIA DRAFT DETECTED!")
        print("="*80)
        print(f"  Platform: {draft['platform'].upper()}")
        print(f"  Source  : {draft['file'].name}")
        print("\n" + "-"*80)
        print("📄 CONTENT:")
        print("-"*80)
        print(draft['content'])
        print("\n" + "-"*80)
        print("\n🤔 ACTION:")
        print("-"*80)
        print("  [A] Approve & Post to ALL + Open WhatsApp")
        print("  [E] Edit in Notepad")
        print("  [R] Reject (Cancel)")
        print("  [Q] Skip")
        print("-"*80)
        
        while True:
            try:
                choice = input("\n✅ Choice (A/E/R/Q): ").strip().upper()
            except EOFError:
                # Non‑interactive environment – auto‑approve for testing
                return 'A'
            if choice in ['A', 'E', 'R', 'Q']:
                return choice

    def handle_action(self, choice, draft):
        if choice == 'A':
            print(f"\n🔥 MASTER AGENT: Processing Multi-Platform Post...")
            
            # Open WhatsApp Business (Beta) app if available, fallback to standard WhatsApp
            print("📱 Opening WhatsApp Business (Beta) app...")
            try:
                import webbrowser, sys
                if sys.platform == "win32":
                    # Attempt protocol URLs
                    webbrowser.open("whatsapp-beta:")
                    webbrowser.open("whatsapp:")
                else:
                    webbrowser.open("whatsapp-beta:")
                    webbrowser.open("whatsapp:")
            except Exception:
                pass
            
            # Post to ALL platforms (Master logic)
            results = {
                "Twitter": self.post_to_twitter(draft['content']),
                "Facebook": self.post_to_facebook(draft['content']),
                "Instagram": self.post_to_instagram(draft['content']),
                "LinkedIn": self.post_to_linkedin(draft['content'])
            }
            
            success_count = len([v for v in results.values() if v])
            if success_count > 0:
                print(f"✅ SUCCESS: Posted to {success_count} platforms.")
                status_msg = "✅ *MASTER POST SUCCESSFUL*\n\n" + "\n".join([f"{k}: OK" if v else f"{k}: FAIL" for k,v in results.items()])
                requests.post(WHATSAPP_GATEWAY, json={"number": ADMIN_NUMBER, "message": status_msg})
                self.update_vault_status(draft, "POSTED")
                # Auto-reply to recent LinkedIn comments if any
                linkedin_urn = results.get("LinkedIn")
                if linkedin_urn:
                    comments = self.fetch_linkedin_comments(linkedin_urn)
                    print(f"DEBUG: Found {len(comments)} comments on LinkedIn post {linkedin_urn}")
                    for c_urn in comments:
                        # Retrieve comment text and reply only if it mentions "kelectric"
                        comment_text = self.get_linkedin_comment_text(c_urn)
                        print(f"DEBUG: Comment URN={c_urn} text=\"{comment_text}\"")
                        if "kelectric" in comment_text.lower():
                            print(f"DEBUG: Comment mentions 'kelectric', sending reply...")
                            self.reply_to_linkedin_comment(c_urn, "Thank you for your comment! 🙏")
                        else:
                            print(f"DEBUG: Comment does not mention 'kelectric', skipping reply.")
                return True
            else:
                print("❌ MASTER POST FAILED on all platforms. Check credentials/logs.")
                return False

        elif choice == 'E':
            temp_file = Path("temp_edit.txt")
            temp_file.write_text(draft['content'], encoding='utf-8')
            print("\n📝 Opening Notepad...")
            os.system(f'notepad "{temp_file}"')
            new_content = temp_file.read_text(encoding='utf-8').strip()
            temp_file.unlink()
            print(f"\n📄 UPDATED CONTENT:\n{new_content}")
            confirm = input("\nPost to ALL? (y/n): ").strip().lower()
            if confirm == 'y':
                draft['content'] = new_content
                return self.handle_action('A', draft)
            return False

        elif choice == 'R':
            print("❌ Draft Rejected.")
            self.update_vault_status(draft, "CANCELLED")
            return True

        elif choice == 'Q':
            print("⏭️ Skipped.")
            return True

    def run(self):
        self.start()
        try:
            while True:
                drafts = self.scan_for_drafts()
                for d in drafts:
                    key = d['content'][:30] + str(d['file'])
                    if key not in self.notified_drafts:
                        print(f"\n🔔 Notifying WhatsApp about new draft...")
                        self.send_to_whatsapp(d)
                        self.notified_drafts.add(key)

                    if key not in self.processed_drafts:
                        choice = self.show_prompt(d)
                        if self.handle_action(choice, d):
                            self.processed_drafts.add(key)
                
                time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("\n⏹️ Watcher Stopped.")

if __name__ == "__main__":
    GoldTierSocialWatcher().run()
