import time
import os
import re
from playwright.sync_api import sync_playwright

VAULT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "KE_AI_Vault"))
LI_SESSION = os.path.join(VAULT_ROOT, ".sessions", "linkedin")

POST_URL = "https://www.linkedin.com/feed/update/urn:li:activity:7461027753316794368/"

def main():
    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=LI_SESSION,
                headless=True,
                args=["--disable-blink-features=AutomationControlled"]
            )
            page = context.pages[0] if context.pages else context.new_page()
            
            print(f"Opening LinkedIn post: {POST_URL}")
            page.goto(POST_URL, wait_until="load", timeout=60000)
            print("Page loaded. Waiting for comments to render...")
            page.wait_for_timeout(8000)
            
            screenshot_path = "li_replied_comments_verification.png"
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"Saved screenshot to {screenshot_path}")
            
            context.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
