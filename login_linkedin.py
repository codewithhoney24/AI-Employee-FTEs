import os
from playwright.sync_api import sync_playwright

VAULT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "KE_AI_Vault"))
LI_SESSION = os.path.join(VAULT_ROOT, ".sessions", "linkedin")

print(f"Using session directory: {LI_SESSION}")
print("A browser window will open. Please log in to LinkedIn.")
print("The browser will close automatically after 60 seconds or once you close it.")

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=LI_SESSION,
        headless=False,
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://www.linkedin.com/login")
    
    print("Waiting for you to log in... You have 60 seconds.")
    try:
        page.wait_for_timeout(60000)
    except:
        pass
    print("Done! You can run your script now.")
