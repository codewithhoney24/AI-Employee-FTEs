import os
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv(dotenv_path="D:/AI-Employee-FTEs/.env")
VAULT_ROOT = "D:/AI-Employee-FTEs/KE_AI_Vault"
TW_SESSION = os.path.join(VAULT_ROOT, ".sessions", "twitter")

def verify():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=TW_SESSION,
            headless=True,  # Headless for diagnosis
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = context.new_page()
        print(f"Navigating to Twitter Home...")
        page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=60000)
        time.sleep(10)
        
        print(f"Current URL: {page.url}")
        if "login" in page.url:
            print("❌ NOT LOGGED IN")
        else:
            print("✅ LOGGED IN")
            
        # Check for textbox
        print("Navigating to Compose...")
        page.goto("https://x.com/compose/post", wait_until="domcontentloaded", timeout=60000)
        time.sleep(10)
        textbox = page.query_selector('div[role="textbox"]')
        if textbox:
            print("✅ Textbox found")
        else:
            print("❌ Textbox NOT found")
            
        # Check for button
        btn = page.query_selector('div[data-testid="tweetButtonInline"]') or \
              page.query_selector('div[data-testid="tweetButton"]') or \
              page.query_selector('button:has-text("Post")')
        if btn:
            print(f"✅ Post button found: {btn.get_attribute('data-testid') or btn.inner_text()}")
        else:
            print("❌ Post button NOT found")
            
        context.close()

if __name__ == "__main__":
    verify()
