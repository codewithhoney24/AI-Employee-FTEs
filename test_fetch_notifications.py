from playwright.sync_api import sync_playwright
import time
import os
import re

VAULT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "KE_AI_Vault"))
LI_SESSION = os.path.join(VAULT_ROOT, ".sessions", "linkedin")
notifications_url = "https://www.linkedin.com/notifications/?filter=all"

print("Scanning Notifications...")
with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=LI_SESSION,
        headless=False,
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto(notifications_url, wait_until="load", timeout=60000)
    page.wait_for_timeout(5000)
    
    # Scroll a bit
    page.evaluate("window.scrollBy(0, 1000)")
    page.wait_for_timeout(2000)
    
    # Grab first few links to see what they look like
    links = page.evaluate("""
        () => {
            const anchors = document.querySelectorAll('a');
            const hrefs = [];
            for (const a of anchors) {
                if (a.href && !a.href.includes('javascript') && !a.href.includes('#')) {
                    hrefs.push(a.innerText.trim().substring(0, 20) + " -> " + a.href);
                }
            }
            return hrefs;
        }
    """)
    print("Found Links:")
    for l in set(links):
        if "urn:li:" in l.lower() or "post" in l.lower() or "activity" in l.lower():
            print(l)
            
    page.screenshot(path="li_notifications.png", full_page=True)
