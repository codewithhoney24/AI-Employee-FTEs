import time
import os
import re
from playwright.sync_api import sync_playwright

VAULT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "KE_AI_Vault"))
LI_SESSION = os.path.join(VAULT_ROOT, ".sessions", "linkedin")

POST_URL = "https://www.linkedin.com/feed/update/urn:li:activity:7459179155478364160/?dashCommentUrn=urn%3Ali%3Afsd_comment%3A%287461065703316541440%2Curn%3Ali%3Aactivity%3A7459179155478364160%29"

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
                page.wait_for_timeout(1000)
            
            print("🎯 Finding the target comment (the one in the URL)...")
            # Usually the targeted comment from URL has a specific highlight class
            # or it's just the main comment visible on the screen.
            # Let's try to find ALL comment items and see which ones are visible.
            
            comment_containers = page.locator(".comments-comment-item").all()
            if not comment_containers:
                print("❌ No comments with class '.comments-comment-item' found on the page.")
                
                # Try generic article or div
                articles = page.locator("article").all()
                print(f"🔍 Found {len(articles)} article tags. Checking them...")
                for art in articles:
                    text = art.inner_text()
                    if "Reply" in text or "Like" in text:
                        print(f"✅ Potential comment block found: {text[:50].replace(chr(10), ' ')}...")
                        art.evaluate("el => el.style.border = '4px solid red'")
                        page.wait_for_timeout(2000)
                        
                        print("🖱️ Finding 'Reply' button via JS...")
                        clicked = art.evaluate("""
                            (el) => {
                                let current = el;
                                for (let i = 0; i < 6; i++) {
                                    if (!current) break;
                                    const btns = current.querySelectorAll ? current.querySelectorAll('button') : [];
                                    for (const b of btns) {
                                        const aria = b.getAttribute('aria-label') || '';
                                        const txt = b.innerText || '';
                                        if (aria.toLowerCase().includes('reply') || txt.toLowerCase().trim() === 'reply') {
                                            b.style.border = '4px solid blue'; // Highlight the button
                                            b.click();
                                            return true;
                                        }
                                    }
                                    current = current.parentElement;
                                }
                                return false;
                            }
                        """)
                        if clicked:
                            print("✅ Clicked 'Reply' button! Waiting for editor...")
                            page.wait_for_timeout(3000)
                            
                            editor = art.locator(".ql-editor, div[role='textbox']").first
                            if editor.count() > 0 and editor.is_visible():
                                print("✅ Editor found! Highlighting in GREEN...")
                                editor.evaluate("el => el.style.border = '4px solid green'")
                                editor.focus()
                                page.keyboard.type("Thank you for engaging! ⚡ (Demo Mode)", delay=50)
                                print("✅ Reply typed!")
                            else:
                                print("❌ Editor not found.")
                            break
            else:
                print(f"✅ Found {len(comment_containers)} comment items.")
                target_container = comment_containers[0]
                
                target_container.scroll_into_view_if_needed()
                target_container.evaluate("el => el.style.border = '4px solid red'")
                print(f"🎯 Targeted comment text: {target_container.inner_text()[:50].replace(chr(10), ' ')}")
                page.wait_for_timeout(2000)
                
                print("🖱️ Finding 'Reply' button via JS...")
                clicked = target_container.evaluate("""
                    (el) => {
                        let current = el;
                        for (let i = 0; i < 6; i++) {
                            if (!current) break;
                            const btns = current.querySelectorAll ? current.querySelectorAll('button') : [];
                            for (const b of btns) {
                                const aria = b.getAttribute('aria-label') || '';
                                const txt = b.innerText || '';
                                if (aria.toLowerCase().includes('reply') || txt.toLowerCase().trim() === 'reply') {
                                    b.style.border = '4px solid blue'; // Highlight the button
                                    b.click();
                                    return true;
                                }
                            }
                            current = current.parentElement;
                        }
                        return false;
                    }
                """)
                
                if clicked:
                    print("✅ Clicked 'Reply' button! Waiting for editor...")
                    page.wait_for_timeout(3000)
                    
                    print("✍️ Simulating typing the auto-reply...")
                    editor = target_container.locator(".ql-editor, div[role='textbox']").first
                    if editor.count() > 0 and editor.is_visible():
                        print("✅ Editor found! Highlighting in GREEN...")
                        editor.evaluate("el => el.style.border = '4px solid green'")
                        editor.focus()
                        page.keyboard.type("Thank you for engaging! ⚡ (Demo Mode)", delay=50)
                        print("✅ Reply typed!")
                    else:
                        print("❌ Editor not found.")
                else:
                    print("❌ Reply button not found via JS.")
                
            print("⏳ Leaving browser open for 15 seconds so you can see...")
            page.wait_for_timeout(15000)
            
            context.close()
            print("🏁 Demo complete.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
