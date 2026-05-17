from skills.linkedin_skill import LinkedInSkill
from playwright.sync_api import sync_playwright
import time
import os

VAULT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "KE_AI_Vault"))
LI_SESSION = os.path.join(VAULT_ROOT, ".sessions", "linkedin")

print("Starting Submit Button Debug Test...")
skill = LinkedInSkill()

original_submit = skill._submit_reply

def mock_submit(page, container):
    page.screenshot(path="li_debug_before_submit.png", full_page=True)
    print("Taking screenshot before submit...")
    
    # Try the exact JS evaluation that app.py uses
    submit_result = page.evaluate("""
        () => {
            const btns = document.querySelectorAll('button');
            const logs = [];
            for (const b of btns) {
                const text = b.innerText ? b.innerText.trim().toLowerCase() : '';
                if (text === 'submit' || text === 'post' || text === 'reply' || text === 'comment') {
                    logs.push(`Found button: "${text}", Disabled: ${b.disabled}, Aria: ${b.getAttribute('aria-label')}`);
                }
            }
            return logs;
        }
    """)
    for log in submit_result:
        print(log)
        
    result = original_submit(page, container)
    print(f"Submit returned: {result}")
    page.screenshot(path="li_debug_after_submit.png", full_page=True)
    return result

skill._submit_reply = mock_submit

# Choose a target string that actually exists, like "price testing"
result = skill.post_reply("price testing", "Hi there! I am the automated test bot confirming functionality. ⚡")

print(f"Final Result: {result}")
