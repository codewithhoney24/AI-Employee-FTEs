from playwright.sync_api import sync_playwright
import os
import time

VAULT_ROOT = os.path.abspath("KE_AI_Vault")
LI_SESSION = os.path.join(VAULT_ROOT, ".sessions", "linkedin")
TARGET_POST = "https://www.linkedin.com/feed/update/urn:li:activity:7458797097232855040/"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(user_data_dir=LI_SESSION, headless=True)
    page = context.new_page()
    page.goto(TARGET_POST, wait_until="load")
    page.wait_for_timeout(10000)
    
    # Dump all text to see if comments are in the text stream
    content = page.content()
    print("--- PAGE TEXT DUMP (Sample) ---")
    print(page.locator("body").inner_text()[:2000])
    
    # Try to find elements that look like comments
    print("\n--- ELEMENTS SEARCH ---")
    potential_selectors = [
        "span.comments-comment-item__main-content",
        "div.comments-comment-item",
        "p.comments-comment-item__text",
        ".feed-shared-update-v2__comment-text",
        "span[dir='ltr']"
    ]
    
    for sel in potential_selectors:
        count = page.locator(sel).count()
        print(f"Selector '{sel}': {count} matches")
        if count > 0:
            print(f"   First match: {page.locator(sel).first.inner_text()[:50]}...")

    context.close()
