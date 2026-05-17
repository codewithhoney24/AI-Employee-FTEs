from skills.linkedin_skill import LinkedInSkill
from playwright.sync_api import sync_playwright
import time
import os

VAULT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "KE_AI_Vault"))
LI_SESSION = os.path.join(VAULT_ROOT, ".sessions", "linkedin")

print("Starting Live Demo of LinkedIn Comment Reply...")
skill = LinkedInSkill()

# Inject screenshot taking into the actual skill for the demo
original_submit = skill._submit_reply

def mock_submit(page, container):
    result = original_submit(page, container)
    if result:
        print("Taking proof screenshot...")
        page.wait_for_timeout(3000)
        page.screenshot(path="KE_AI_Vault/Logs/li_live_demo.png", full_page=True)
    return result

skill._submit_reply = mock_submit

# Choose a target string that actually exists, like "price testing"
# (Wait, let's use the exact text the AI engine would pass)
result = skill.post_reply("price testing", "Hi there! I am the automated test bot confirming functionality. ⚡")

print(f"Final Result: {result}")
