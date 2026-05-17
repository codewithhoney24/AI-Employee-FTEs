from skills.linkedin_skill import LinkedInSkill
from playwright.sync_api import sync_playwright
import time
import os

VAULT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "KE_AI_Vault"))
LI_SESSION = os.path.join(VAULT_ROOT, ".sessions", "linkedin")
target_post = "https://www.linkedin.com/feed/update/urn:li:activity:7458797097232855040/"

print("Running pure playwright test...")
with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=LI_SESSION,
        headless=False,
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto(target_post, wait_until="load", timeout=60000)
    page.wait_for_timeout(6000)
    
    container = page.locator(".comments-comment-item").filter(has_text="Details").first
    if not container.is_visible():
        container = page.get_by_text("Details", exact=False).first
    
    if container.is_visible():
        container.scroll_into_view_if_needed()
        page.evaluate("""
            (ctx) => {
                const btns = ctx.querySelectorAll('button, span, a');
                for (const b of btns) {
                    if (/^Reply$/i.test(b.innerText.trim())) {
                        b.click();
                        return true;
                    }
                }
            }
        """, container.element_handle())
        page.wait_for_timeout(2000)
        
        # Fill via keyboard
        editor = page.locator("[contenteditable='true']").last
        if editor.is_visible():
            editor.click()
            page.wait_for_timeout(500)
            page.keyboard.type("Thanks for reaching out! We will share details soon. ⚡", delay=50)
            page.wait_for_timeout(1000)
            
            # Click post
            btn = page.get_by_role("button", name="Post").last
            if btn.is_visible() and not btn.is_disabled():
                btn.click()
                print("Clicked Post successfully!")
            else:
                print("Post button disabled or not visible")
                page.evaluate("""
                    () => {
                        const btns = document.querySelectorAll('button');
                        for (const b of btns) {
                            if (/^(post|submit)$/i.test(b.innerText.trim()) && !b.disabled) {
                                b.click();
                                return true;
                            }
                        }
                    }
                """)
                print("Tried JS click on active Post button")
            
            page.wait_for_timeout(4000)
        else:
            print("Editor not visible")
    else:
        print("Container not found")
