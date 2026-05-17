from playwright.sync_api import sync_playwright
import time
import os

VAULT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "KE_AI_Vault"))
LI_SESSION = os.path.join(VAULT_ROOT, ".sessions", "linkedin")
profile_url = "https://www.linkedin.com/in/digital-dreamers-9a15bb3b4/recent-activity/all/"

print("Running pure playwright test...")
with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=LI_SESSION,
        headless=False,
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto(profile_url, wait_until="load", timeout=60000)
    page.wait_for_timeout(5000)
    
    # Scroll a bit
    page.evaluate("window.scrollBy(0, 1000)")
    page.wait_for_timeout(2000)
    
    post_links = page.evaluate("""
        () => {
            const links = document.querySelectorAll('a[href*="/feed/update/urn:li:activity:"]');
            const urls = new Set();
            for (const a of links) {
                const url = a.href.split('?')[0];
                urls.add(url);
            }
            return Array.from(urls);
        }
    """)
    print("Found Post Links:")
    for link in post_links:
        print(link)
