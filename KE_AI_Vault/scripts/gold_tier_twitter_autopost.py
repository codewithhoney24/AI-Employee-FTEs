import os
import time
import sys
from datetime import datetime
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# --- CONFIG & CREDENTIALS ---
load_dotenv(dotenv_path="D:/AI-Employee-FTEs/.env")

VAULT_ROOT = "D:/AI-Employee-FTEs/KE_AI_Vault"
TW_SESSION = os.path.join(VAULT_ROOT, ".sessions", "twitter")
WA_SESSION = os.path.join(VAULT_ROOT, ".sessions", "whatsapp")
ADMIN_NUMBER = os.getenv("WHATSAPP_ADMIN_NUMBER", "923491379839")

# Ensure session directories exist
os.makedirs(TW_SESSION, exist_ok=True)
os.makedirs(WA_SESSION, exist_ok=True)

def post_to_twitter(content):
    """
    Handles the Twitter posting flow with the proven Control+Enter strategy.
    """
    print("\n🐦 [TWITTER] Starting Post Automation...")
    
    with sync_playwright() as p:
        try:
            print("STEP 1: Launching Twitter with persistent session...")
            browser = p.chromium.launch_persistent_context(
                user_data_dir=TW_SESSION,
                headless=False,
                slow_mo=500,
                no_viewport=True,
                args=["--disable-blink-features=AutomationControlled", "--start-maximized"]
            )
            page = browser.pages[0] if browser.pages else browser.new_page()
            
            print("STEP 2: Navigating to Twitter Compose...")
            page.goto("https://x.com/compose/post", wait_until="domcontentloaded", timeout=60000)
            # Extra wait for UI stabilization
            time.sleep(10)
            
            # Login check
            if "login" in page.url or page.query_selector('input[name="text"]'):
                print("⚠️ NOT LOGGED IN. Please log in manually.")
                page.wait_for_selector('div[role="textbox"]', timeout=120000)
                print("✅ Login detected.")

            print("STEP 3: Locating Textbox...")
            page.wait_for_selector('div[role="textbox"]', timeout=30000)
            page.click('div[role="textbox"]')
            
            # Clear existing content
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            time.sleep(1)
            
            print("STEP 4: Typing Content...")
            page.keyboard.type(content, delay=50)
            time.sleep(2)

            print("STEP 5: Sending Post Command (Control+Enter)...")
            page.keyboard.press("Control+Enter")
            
            # Secondary fallback: Click button if keyboard fails
            time.sleep(3)
            if page.query_selector('div[role="textbox"]'):
                print("⚠️ Textbox still visible. Trying Button Click...")
                post_btn = page.query_selector('[data-testid="tweetButton"]') or \
                           page.query_selector('button:has-text("Post")')
                if post_btn:
                    post_btn.click(force=True)

            print("STEP 6: Verifying success...")
            # Wait up to 20 seconds for the textbox to disappear
            success_verified = False
            for _ in range(20):
                if not page.query_selector('div[role="textbox"]'):
                    print("✨✨ SUCCESS: POST IS LIVE! ✨✨")
                    success_verified = True
                    break
                time.sleep(1)

            if success_verified:
                time.sleep(2)
                browser.close()
                return True
            else:
                print("❌ FAILED: Post box is still visible after 20s. Check Twitter logs.")
                browser.close()
                return False

        except Exception as e:
            print(f"❌ [TWITTER ERROR]: {e}")
            return False

def run_gold_tier_flow():
    print(f"🚀 [GOLD TIER] Starting Full Auto Pipeline - {datetime.now().strftime('%H:%M:%S')}")
    
    content = "K-Electric is committed to Karachi's energy future! 🚀 Our $2B investment plan is modernizing the grid for a smarter, greener city. #KElectric #Karachi #EnergyInnovation"
    
    with sync_playwright() as p:
        print("\n📱 [PHASE 1] OPENING WHATSAPP FOR BOSS APPROVAL...")
        wa_context = p.chromium.launch_persistent_context(
            user_data_dir=WA_SESSION,
            headless=False,
            slow_mo=500,
            no_viewport=True,
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"]
        )
        wa_page = wa_context.pages[0] if wa_context.pages else wa_context.new_page()
        
        clean_number = "".join(filter(str.isdigit, ADMIN_NUMBER))
        wa_url = f"https://web.whatsapp.com/send?phone={clean_number}"
        
        print(f">>> Navigating to WhatsApp: {clean_number}")
        wa_page.goto(wa_url, wait_until="load")
        
        try:
            print("⏳ Waiting for WhatsApp Web to load...")
            wa_page.wait_for_selector('div[contenteditable="true"]', timeout=60000)
            time.sleep(5)
            
            # Send the approval prompt
            prompt = (
                f"🚀 *KE AI EMPLOYEE: GOLD TIER DRAFT*\n\n"
                f"*CONTENT:* \"{content}\"\n\n"
                f"👇 *BOSS, REPLY:* \n"
                f"✅ *YES* to post on Twitter.\n"
                f"❌ *NO* to cancel."
            )
            
            input_box = wa_page.locator('div[contenteditable="true"]')
            input_box.fill(prompt)
            wa_page.keyboard.press("Enter")
            print("✅ Approval request sent to Boss.")
            
            print("\n" + "="*50)
            print("👂 LISTENING FOR BOSS APPROVAL (YES/NO)...")
            print("="*50)
            
            last_seen_msg = ""
            approved = False
            
            # Loop for 5 minutes
            start_time = time.time()
            while time.time() - start_time < 300:
                try:
                    # Check for new incoming messages
                    incoming = wa_page.query_selector_all('.message-in')
                    if not incoming:
                        time.sleep(2)
                        continue
                    
                    last_bubble = incoming[-1]
                    text_elem = last_bubble.query_selector('span.selectable-text') or last_bubble
                    raw_text = text_elem.inner_text()
                    print(f"DEBUG: Scanned WhatsApp Bubble -> [{raw_text.replace('\n', ' ')}]")
                    msg_text = raw_text.strip().upper()
                    
                    if msg_text == last_seen_msg:
                        time.sleep(2)
                        continue
                    
                    last_seen_msg = msg_text
                    # Ignore our own messages
                    if "GOLD TIER DRAFT" in msg_text:
                        continue
                        
                    print(f"📩 Boss says: [{msg_text}]")
                    
                    if "YES" in msg_text:
                        print("✨ Approval detected! Moving to Twitter...")
                        approved = True
                        break
                    elif "NO" in msg_text:
                        print("🛑 Cancelled by Boss.")
                        input_box.fill("🛑 *TASK CANCELLED:* No problem, Boss.")
                        wa_page.keyboard.press("Enter")
                        break
                        
                except Exception:
                    pass
                time.sleep(2)
            
            wa_context.close()
            
            if approved:
                # RUN THE TWITTER ACTION
                success = post_to_twitter(content)
                if success:
                    print("\n🏁 PIPELINE SUCCESSFUL.")
                else:
                    print("\n❌ PIPELINE FAILED AT TWITTER PHASE.")
            else:
                print("\n🛑 Pipeline ended: No approval or cancelled.")
                
        except Exception as e:
            print(f"🔥 Error in flow: {e}")
            wa_context.close()

if __name__ == "__main__":
    try:
        run_gold_tier_flow()
    except KeyboardInterrupt:
        print("\n👋 Manual Exit.")
        sys.exit(0)
