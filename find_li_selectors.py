from playwright.sync_api import sync_playwright
import os

VAULT_ROOT = os.path.abspath("KE_AI_Vault")
LI_SESSION = os.path.join(VAULT_ROOT, ".sessions", "linkedin")
TARGET_POST = "https://www.linkedin.com/feed/update/urn:li:activity:7458797097232855040/"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(user_data_dir=LI_SESSION, headless=True)
    page = context.new_page()
    page.goto(TARGET_POST, wait_until="load")
    page.wait_for_timeout(10000)
    
    print("Searching for 'price testing'...")
    # Find the element containing the text
    element = page.get_by_text("price testing").first
    if element.is_visible():
        # Get its tag and class
        tag = element.evaluate("el => el.tagName")
        classes = element.evaluate("el => el.className")
        parent_classes = element.evaluate("el => el.parentElement.className")
        grandparent_classes = element.evaluate("el => el.parentElement.parentElement.className")
        
        print(f"✅ Found!")
        print(f"   Tag: {tag}")
        print(f"   Class: {classes}")
        print(f"   Parent Class: {parent_classes}")
        print(f"   Grandparent Class: {grandparent_classes}")
    else:
        print("❌ Could not find text 'price testing'")

    context.close()
