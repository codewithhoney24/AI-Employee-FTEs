import os
import time
import sys
import random

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# =========================================================
# CONFIG
# =========================================================

load_dotenv("D:/AI-Employee-FTEs/.env")

VAULT_ROOT = "D:/AI-Employee-FTEs/KE_AI_Vault"

TW_SESSION = os.path.join(VAULT_ROOT, ".sessions", "twitter")
WA_SESSION = os.path.join(VAULT_ROOT, ".sessions", "whatsapp")

ADMIN_NUMBER = os.getenv("WHATSAPP_ADMIN_NUMBER", "923491379839")

# =========================================================
# AI POST
# =========================================================

def get_ai_post():
    posts = [
        "K-Electric is accelerating Karachi's growth with a $2B investment plan ⚡ #KElectric #Karachi",
        "Smart grids & AI are transforming Karachi's power infrastructure ⚡ #Innovation #KElectric",
        "KE integrated renewable energy into the grid 🌿 #GreenEnergy #Pakistan",
        "Industrial growth in Karachi is powered by KE ⚡🏗️ #PakistanEconomy",
    ]
    return random.choice(posts)

# =========================================================
# TWITTER
# =========================================================

def launch_twitter(p):
    browser = p.chromium.launch_persistent_context(
        user_data_dir=TW_SESSION,
        headless=False,
        slow_mo=500,
        no_viewport=True,
        args=["--start-maximized"]
    )

    page = browser.pages[0] if browser.pages else browser.new_page()
    return browser, page


def open_twitter_draft(page, content):
    print("\n[STEP 1] Opening Twitter Draft...")

    page.goto("https://x.com/compose/post", wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    box = page.locator('div[data-testid="tweetTextarea_0"]').first
    box.wait_for(state="visible", timeout=30000)

    box.click()
    page.keyboard.press("Control+A")
    page.keyboard.press("Backspace")
    page.keyboard.insert_text(content)

    print("✅ Draft Ready")


# =========================================================
# 🔥 FIXED POST FUNCTION
# =========================================================

def post_twitter(page):

    print("\n[STEP 3] Posting Tweet NOW...")

    # 🔥 FORCE FOCUS + CLEAN STATE
    page.bring_to_front()
    page.wait_for_timeout(2000)
    page.keyboard.press("Escape")

    # 🔥 ensure compose is still valid
    try:
        page.wait_for_selector(
            'div[data-testid="tweetTextarea_0"]',
            timeout=20000
        )
    except:
        print("⚠ Compose lost → reloading...")
        page.reload()
        page.wait_for_timeout(6000)

    # =====================================================
    # FIND BUTTON
    # =====================================================
    try:
        btn = page.locator(
            'button[data-testid="tweetButtonInline"], button[data-testid="tweetButton"]'
        ).first

        btn.wait_for(state="visible", timeout=20000)
        btn.scroll_into_view_if_needed()
        page.wait_for_timeout(1500)

        # METHOD 1
        try:
            btn.click(timeout=5000)
            print("🚀 Clicked (Playwright)")
        except:
            print("⚠ Playwright failed → JS click")

            # METHOD 2 JS fallback
            page.evaluate("""
            () => {
                const btn =
                    document.querySelector('button[data-testid="tweetButtonInline"]') ||
                    document.querySelector('button[data-testid="tweetButton"]') ||
                    [...document.querySelectorAll('button')].find(b =>
                        b.innerText.includes('Post') || b.innerText.includes('Tweet')
                    );

                if (btn) btn.click();
            }
            """)

            print("🚀 Clicked (JS)")

        page.wait_for_timeout(2000)

        # METHOD 3 keyboard fallback
        page.keyboard.press("Control+Enter")

    except Exception as e:
        print("❌ Post error:", e)
        return False

    # =====================================================
    # VERIFY
    # =====================================================
    print("⏳ Verifying Tweet...")

    for _ in range(15):
        try:
            if page.locator('div[data-testid="tweetTextarea_0"]').count() == 0:
                print("✅ TWEET LIVE")
                return True
        except:
            pass

        page.wait_for_timeout(1000)

    print("❌ Not confirmed")
    return False


# =========================================================
# WHATSAPP
# =========================================================

def launch_whatsapp(p):
    browser = p.chromium.launch_persistent_context(
        user_data_dir=WA_SESSION,
        headless=False,
        slow_mo=500,
        no_viewport=True,
        args=["--start-maximized"]
    )

    page = browser.pages[0] if browser.pages else browser.new_page()
    return browser, page


def open_whatsapp_chat(page):

    number = "".join(filter(str.isdigit, ADMIN_NUMBER))

    print("\n[STEP 2] Opening WhatsApp...")

    page.goto(f"https://web.whatsapp.com/send?phone={number}", wait_until="load")

    page.wait_for_selector('div[contenteditable="true"]', timeout=60000)

    print("✅ WhatsApp Ready")


def send_whatsapp(page, msg):

    box = page.locator('div[contenteditable="true"]').last
    box.click()

    page.keyboard.insert_text(msg)
    page.keyboard.press("Enter")


# =========================================================
# COMMAND LISTENER
# =========================================================

def wait_for_commands(wa_page, tw_page, content):

    last_seen = ""

    while True:

        try:
            msgs = wa_page.locator('.message-in span.selectable-text')
            count = msgs.count()

            if count == 0:
                time.sleep(1)
                continue

            raw = msgs.nth(count - 1).inner_text()
            msg = raw.strip().upper()

            if msg == last_seen:
                time.sleep(1)
                continue

            last_seen = msg
            print("\n📩 COMMAND:", raw)

            # =================================================
            # YES FIXED
            # =================================================
            if msg == "YES":
                print("✅ APPROVED")

                tw_page.bring_to_front()
                tw_page.wait_for_timeout(2000)

                # 🔥 FORCE REFRESH (IMPORTANT FIX)
                tw_page.reload(wait_until="domcontentloaded")
                tw_page.wait_for_timeout(6000)

                return post_twitter(tw_page)

            # =================================================
            # NO
            # =================================================
            if msg == "NO":
                print("❌ CANCELLED")
                return False

            # =================================================
            # EDIT
            # =================================================
            if msg.startswith("EDIT"):
                new_text = raw[4:].strip()

                if new_text:
                    content = new_text

                    update_twitter_draft(tw_page, content)

                    send_whatsapp(
                        wa_page,
                        f"""🔁 UPDATED DRAFT:

{content}

Reply:
YES / NO / EDIT"""
                    )

        except Exception as e:
            print("Listener error:", e)

        time.sleep(1)


# =========================================================
# MAIN
# =========================================================

def run():

    print("\n🚀 MASTER AI AGENT STARTED\n")

    content = get_ai_post()
    print("🧠 AI POST:\n", content)

    with sync_playwright() as p:

        # TWITTER
        tw_browser, tw_page = launch_twitter(p)
        open_twitter_draft(tw_page, content)

        # WHATSAPP
        wa_browser, wa_page = launch_whatsapp(p)
        open_whatsapp_chat(wa_page)

        send_whatsapp(
            wa_page,
            f"""🚀 KE AI EMPLOYEE DRAFT READY

CONTENT:
{content}

Reply:
YES = Approve
NO = Cancel
EDIT your_new_text = Modify"""
        )

        print("\nWAITING FOR APPROVAL...\n")

        result = wait_for_commands(wa_page, tw_page, content)

        if result:
            print("\n🎉 POSTED SUCCESSFULLY")
        else:
            print("\n🛑 STOPPED")

        time.sleep(5)

        wa_browser.close()
        tw_browser.close()


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\nEXIT")
        sys.exit(0)