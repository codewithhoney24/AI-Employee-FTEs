"""
ApproveAndTweetSkill – encapsulates the whole human‑in‑the‑loop flow as a single skill.
It:
  1. Generates a fresh K‑Electric business tweet.
  2. Sends a draft to WhatsApp and waits (configurable timeout) for an explicit reply:
     * YES – proceed to post.
     * NO  – cancel.
     * EDIT – prompt on the console for new tweet content, then continue waiting for YES/NO.
  3. If approved, opens Twitter (Playwright) and posts the tweet.
The skill returns a detailed dict so the executor (or any caller) can see what happened.
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# Load environment (WhatsApp admin number, etc.)
load_dotenv(dotenv_path="D:/AI-Employee-FTEs/.env")

VAULT_ROOT = "D:/AI-Employee-FTEs/KE_AI_Vault"
TW_SESSION = os.path.join(VAULT_ROOT, ".sessions", "twitter")
WA_SESSION = os.path.join(VAULT_ROOT, ".sessions", "whatsapp")
ADMIN_NUMBER = os.getenv("WHATSAPP_ADMIN_NUMBER", "923491379839")

# ---------------------------------------------------------------------------
def generate_content() -> str:
    """Create a unique tweet for the K‑Electric growth update."""
    base = (
        "K‑Electric business update: our growth initiatives are driving revenue +5% QoQ. "
        "#KElectric #Automation"
    )
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{base} (msg @ {ts})"

# ---------------------------------------------------------------------------
class ApproveAndTweetSkill:
    """Skill that performs the approval‑then‑tweet workflow.

    No input ``context`` is required – everything is driven from env vars.
    Returns a dict with keys:
        - approved (bool)
        - posted (bool)
        - tweet_content (str)
        - status_message (str)
    """

    def run(self, context: dict = None) -> dict:
        content = generate_content()
        approved, final_content = self._handle_whatsapp_approval(content)
        if not approved:
            return {
                "approved": False,
                "posted": False,
                "tweet_content": final_content,
                "status_message": "User denied approval or timeout – tweet cancelled.",
            }
        posted = self._post_to_twitter(final_content)
        return {
            "approved": True,
            "posted": posted,
            "tweet_content": final_content,
            "status_message": "Tweet posted successfully." if posted else "Tweet posting failed.",
        }

    # -----------------------------------------------------------------------
    def _handle_whatsapp_approval(self, content: str):
        """Open WhatsApp, send draft, and wait for YES/NO/EDIT.
        Returns (approved: bool, final_content: str).
        """
        # Auto‑approve shortcut for testing (set WHATSAPP_AUTO_APPROVE=YES)
        if os.getenv("WHATSAPP_AUTO_APPROVE", "").upper() == "YES":
            print("⚡ Auto‑approve flag detected – bypassing WhatsApp and approving.")
            return True, content
        approved = False
        final_content = content
        with sync_playwright() as p:
            wa_context = p.chromium.launch_persistent_context(
                user_data_dir=WA_SESSION,
                headless=False,
                slow_mo=500,
                no_viewport=True,
                args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
            )
            wa_page = wa_context.pages[0] if wa_context.pages else wa_context.new_page()
            clean_number = "".join(filter(str.isdigit, ADMIN_NUMBER))
            wa_url = f"https://web.whatsapp.com/send?phone={clean_number}"
            wa_page.goto(wa_url, wait_until="load")
            try:
                wa_page.wait_for_selector('div[contenteditable="true"]', timeout=60000)
                time.sleep(3)
                prompt = (
                    f"🚀 *DEMO MODE: DRAFT READY*\n\n"
                    f"*CONTENT:* \"{final_content}\"\n\n"
                    "👇 *Reply YES to post, NO to cancel, EDIT to change text.*"
                )
                wa_page.locator('div[contenteditable="true"]').fill(prompt)
                wa_page.keyboard.press("Enter")
                print("✅ Draft sent – waiting for reply (60 s timeout).")
                start = time.time()
                while time.time() - start < 60:
                    try:
                        incoming = wa_page.query_selector_all('.message-in')
                        if incoming:
                            last_msg = incoming[-1].inner_text().strip().upper()
                            if "YES" in last_msg and "DEMO MODE" not in last_msg:
                                approved = True
                                print(f"📩 Approval received: [{last_msg}]")
                                break
                            if "NO" in last_msg and "DEMO MODE" not in last_msg:
                                # Auto‑approve shortcut for testing (set WHATSAPP_AUTO_APPROVE=YES)
        if os.getenv("WHATSAPP_AUTO_APPROVE", "").upper() == "YES":
            print("⚡ Auto‑approve flag detected – bypassing WhatsApp and approving.")
            return True, content
        approved = False
                                print(f"❌ Denial received: [{last_msg}]")
                                break
                            if "EDIT" in last_msg and "DEMO MODE" not in last_msg:
                                print("✏️ Edit requested – type new tweet content and press Enter:")
                                new_text = sys.stdin.readline().strip()
                                if new_text:
                                    final_content = new_text
                                    print(f"✅ Updated tweet content: {final_content}")
                                # continue waiting for final YES/NO after edit
                    except Exception as e:
                        print(f"⚠️ Error checking WhatsApp messages: {e}")
                    time.sleep(1)
            except Exception as e:
                print(f"⚠️ WhatsApp interaction failed: {e}")
                # Auto‑approve shortcut for testing (set WHATSAPP_AUTO_APPROVE=YES)
        if os.getenv("WHATSAPP_AUTO_APPROVE", "").upper() == "YES":
            print("⚡ Auto‑approve flag detected – bypassing WhatsApp and approving.")
            return True, content
        approved = False
            finally:
                wa_context.close()
        return approved, final_content

    # -----------------------------------------------------------------------
    def _post_to_twitter(self, content: str) -> bool:
        """Open Twitter, type *content*, and attempt to post.
        Returns True on success, False otherwise.
        """
        with sync_playwright() as p:
            tw_context = p.chromium.launch_persistent_context(
                user_data_dir=TW_SESSION,
                headless=False,
                slow_mo=500,
                no_viewport=True,
                args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
            )
            tw_page = tw_context.pages[0] if tw_context.pages else tw_context.new_page()
            try:
                tw_page.goto("https://x.com/compose/post", wait_until="domcontentloaded", timeout=60000)
                time.sleep(4)
                if "login" in tw_page.url:
                    print("⚠️ Manual login required – please log in to Twitter.")
                    tw_page.wait_for_selector('div[role="textbox"]', timeout=60000)
                tw_page.wait_for_selector('div[role="textbox"]', timeout=30000)
                tw_page.click('div[role="textbox"]')
                tw_page.keyboard.press("Control+A")
                tw_page.keyboard.press("Backspace")
                tw_page.fill('div[role="textbox"]', content)
                time.sleep(1)
                tw_page.keyboard.press("Control+Enter")
                # fallback button click if needed
                time.sleep(3)
                if tw_page.query_selector('div[role="textbox"]'):
                    btn = tw_page.query_selector('div[data-testid="tweetButtonInline"]') or \
                          tw_page.query_selector('div[data-testid="tweetButton"]')
                    if btn:
                        btn.click(force=True)
                time.sleep(8)
                if not tw_page.query_selector('div[role="textbox"]'):
                    print("✨✨ SUCCESS: Tweet posted! ✨✨")
                    return True
                else:
                    print("⚠️ Tweet box still present – posting may have failed.")
                    return False
            except Exception as e:
                print(f"❌ Twitter posting error: {e}")
                return False
            finally:
                tw_context.close()

__all__ = ["ApproveAndTweetSkill"]
