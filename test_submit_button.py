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
    
    print("Clicking all Reply buttons to open editors...")
    page.evaluate("""
        () => {
            const btns = document.querySelectorAll('button');
            for (const b of btns) {
                if (b.getAttribute('aria-label') && b.getAttribute('aria-label').toLowerCase().includes('reply')) {
                    b.click();
                }
            }
        }
    """)
    page.wait_for_timeout(2000)
    
    editors = page.locator("[contenteditable='true']").all()
    print(f"Found {len(editors)} editors open.")
    
    if editors:
        editor = editors[-1] # Usually the last one is the nested one opened
        editor.scroll_into_view_if_needed()
        editor.click()
        page.wait_for_timeout(500)
        page.keyboard.type("Testing forced submit...", delay=20)
        page.wait_for_timeout(2000)
        
        page.screenshot(path="li_debug_editor_filled.png", full_page=True)
        
        # Now find the active submit button
        submit_clicked = page.evaluate("""
            () => {
                const btns = document.querySelectorAll('button');
                for (const b of btns) {
                    const text = b.innerText.trim().toLowerCase();
                    if ((text === 'submit' || text === 'post' || text === 'reply' || text === 'comment') && !b.disabled) {
                        // Avoid clicking the reply-opener buttons again
                        if (!b.getAttribute('aria-label') || !b.getAttribute('aria-label').toLowerCase().includes('reply')) {
                            b.click();
                            return true;
                        }
                    }
                }
                
                // Fallback: If no enabled button found, find the disabled one and force it
                for (const b of btns) {
                    const text = b.innerText.trim().toLowerCase();
                    if ((text === 'submit' || text === 'post') && b.disabled) {
                        b.removeAttribute('disabled');
                        b.click();
                        return 'forced';
                    }
                }
                return false;
            }
        """)
        print(f"Submit result: {submit_clicked}")
        page.wait_for_timeout(3000)
        page.screenshot(path="li_test_final.png", full_page=True)
        print("Done. Check screenshots.")
