import time
import os
import re
from playwright.sync_api import sync_playwright

VAULT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "KE_AI_Vault"))
LI_SESSION = os.path.join(VAULT_ROOT, ".sessions", "linkedin")

POST_URL = "https://www.linkedin.com/feed/update/urn:li:activity:7459179155478364160/?dashCommentUrn=urn%3Ali%3Afsd_comment%3A%287461065703316541440%2Curn%3Ali%3Aactivity%3A7459179155478364160%29"

# Target the specific comment text we saw in your screenshot
COMMENT_TEXT = "complaint ,bill"

def main():
    print("🚀 Starting Live LinkedIn Debug for user's URL...")
    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=LI_SESSION,
                headless=False,  # Visible to user
                viewport={"width": 1280, "height": 800},
                args=["--disable-blink-features=AutomationControlled"]
            )
            page = context.pages[0] if context.pages else context.new_page()
            
            print(f"🌐 Navigating to URL: {POST_URL}")
            page.goto(POST_URL, wait_until="load", timeout=60000)
            page.wait_for_timeout(8000)
            
            print("📜 Scrolling down to load the specific comment...")
            for _ in range(3):
                page.mouse.wheel(0, 800)
                page.wait_for_timeout(2000)
            
            print(f"🎯 Looking for comment containing: '{COMMENT_TEXT}'")
            
            # Find the element containing the text
            safe = re.escape(COMMENT_TEXT)
            pattern = re.compile(safe, re.IGNORECASE)

            strategies = [
                lambda: page.locator("article").filter(has_text=pattern).first,
                lambda: page.locator(".comments-comment-item").filter(has_text=pattern).first,
                lambda: page.locator("div.update-components-comment").filter(has_text=pattern).first,
                lambda: page.get_by_text(COMMENT_TEXT[:10], exact=False).first,
            ]

            container = None
            for i, strategy in enumerate(strategies):
                try:
                    el = strategy()
                    if el.is_visible(timeout=3000):
                        print(f"✅ Comment Container found via strategy {i+1}")
                        container = el
                        break
                except:
                    continue
            
            if container:
                print("✅ Highlighting it in RED...")
                container.scroll_into_view_if_needed()
                # Highlight the comment container
                container.evaluate("el => el.style.border = '4px solid red'")
                page.wait_for_timeout(2000)
                
                print("🖱️ Finding 'Reply' button via JS...")
                clicked = container.evaluate("""
                    (el) => {
                        let current = el;
                        for (let i = 0; i < 8; i++) {
                            if (!current) break;
                            const btns = current.querySelectorAll ? current.querySelectorAll('button') : [];
                            for (const b of btns) {
                                const aria = b.getAttribute('aria-label') || '';
                                const txt = b.innerText || '';
                                // Check aria-label or inner text or even SVG titles if possible
                                if (aria.toLowerCase().includes('reply') || txt.toLowerCase().trim() === 'reply' || b.innerHTML.includes('Reply')) {
                                    b.style.border = '4px solid blue'; // Highlight the button
                                    b.click();
                                    return true;
                                }
                            }
                            current = current.parentElement;
                        }
                        // Fallback: If no button has text/aria 'reply', click the SECOND button in the block
                        // (Usually: 1st is Like, 2nd is Reply)
                        let parentBlock = el;
                        for(let i=0; i<5; i++){
                           if(!parentBlock) break;
                           const buttons = parentBlock.querySelectorAll('button');
                           if(buttons.length >= 2){
                               buttons[1].style.border = '4px solid blue';
                               buttons[1].click();
                               return true;
                           }
                           parentBlock = parentBlock.parentElement;
                        }
                        
                        return false;
                    }
                """)
                
                if clicked:
                    print("✅ Clicked 'Reply' button! Waiting for editor...")
                    page.wait_for_timeout(3000)
                    
                    print("✍️ Simulating typing the auto-reply...")
                    # The editor is usually inside the container after reply is clicked
                    editor = page.locator(".ql-editor, div[role='textbox']").filter(has_text="").first
                    # In Playwright python you usually do .locator("...", state="visible") but let's just use .first like before
                    editor = page.locator(".ql-editor, div[role='textbox']").first
                    if editor.count() > 0:
                        print("✅ Editor found! Highlighting in GREEN...")
                        editor.evaluate("el => el.style.border = '4px solid green'")
                        editor.focus()
                        page.keyboard.type("Thank you for your complaint/bill query! ⚡ (Demo Mode)", delay=50)
                        print("✅ Reply typed! (Not submitting to avoid spam)")
                    else:
                        print("❌ Editor not found.")
                else:
                    print("❌ Reply button not found via JS traverse.")
                    
            else:
                print("❌ Comment not found on page. The element is likely inside a shadow DOM or different structure.")
            
            print("⏳ Leaving browser open for 15 seconds so you can see...")
            page.wait_for_timeout(15000)
            
            context.close()
            print("🏁 Demo complete.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
