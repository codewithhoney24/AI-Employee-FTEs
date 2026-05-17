"""
LinkedInSkill - Automates finding and commenting on relevant LinkedIn posts.
Uses Playwright for browser automation and Gemini for smart drafting.

post_reply() uses 5-strategy Reply button detection + JS click fallback.
"""

import os
import re
import time
import requests
import json
from playwright.sync_api import sync_playwright
from google import genai
from dotenv import load_dotenv

load_dotenv("../../.env", override=True)
ADMIN_NUMBER = os.getenv("WHATSAPP_ADMIN_NUMBER", "923491379839")
WHATSAPP_API = "http://localhost:3001/send"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

VAULT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../KE_AI_Vault"))
LI_SESSION = os.path.join(VAULT_ROOT, ".sessions", "linkedin")


class LinkedInSkill:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
        self.notifications_url = "https://www.linkedin.com/notifications/?filter=all"
        self.keywords = ["k electric", "k-electric", "kelectric", "price", "details", "bill", "complaint", "new connection", "test", "congrats", "well done", "good job", "excellent", "update", "hi", "hello", "info"]
        # Playwright browser reuse attributes
        self._playwright = None
        self._context = None
        self._page = None

    # ─────────────────────────────────────────────
    # PUBLIC: Check for new comments
    # ─────────────────────────────────────────────

    def check_my_comments(self):
        print("🔍 [LINKEDIN] Checking for interactions (Background Mode)...", flush=True)
        return self._run_browser_task("comments", headless=True)

    # ─────────────────────────────────────────────
    # BROWSER RUNNER
    # ─────────────────────────────────────────────

    def _run_browser_task(self, mode="discovery", headless=False):
        try:
            with sync_playwright() as p:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=LI_SESSION,
                    headless=headless,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--disable-dev-shm-usage",
                        "--no-sandbox",
                        "--disable-gpu"
                    ]
                )
                page = context.pages[0] if context.pages else context.new_page()
                # Set a global timeout for the entire page
                page.set_default_timeout(20000)
                try:
                    if mode == "comments":
                        return self._do_comment_check(page)
                    else:
                        return self._do_discovery(page)
                except Exception as e:
                    print(f"❌ [LINKEDIN] Task Error: {e}", flush=True)
                    return []
                finally:
                    context.close()
        except Exception as e:
            print(f"❌ [LINKEDIN] Playwright Error: {e}", flush=True)
            return []

    # ─────────────────────────────────────────────
    # COMMENT CHECK
    # ─────────────────────────────────────────────

    def _get_recent_post_urls(self, page):
        """Directly find posts with comments from the feed"""
        print(f"🌐 [LINKEDIN] Scanning feed for posts with comments", flush=True)
        try:
            page.goto("https://www.linkedin.com/in/digital-dreamers-9a15bb3b4/recent-activity/all/", wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(4000)
            page.evaluate("window.scrollBy(0, 1500)")
            page.wait_for_timeout(2000)

            # Extract proper feed links from the recent activity page
            all_links = page.evaluate("""
                () => {
                    const anchors = document.querySelectorAll('a');
                    const links = [];
                    anchors.forEach(a => {
                        const href = a.href || "";
                        if (href.includes('urn:li:activity:')) {
                            // Extract the URN
                            const urnMatch = href.match(/(urn:li:activity:\d+)/);
                            if (urnMatch && urnMatch[1]) {
                                links.push('https://www.linkedin.com/feed/update/' + urnMatch[1] + '/');
                            }
                        } else if (href.includes('feed/update') || href.includes('/posts/')) {
                            links.push(href.split('?')[0]); 
                        }
                    });
                    return links;
                }
            """)

            # Remove duplicates
            unique_links = list(set(all_links))[:10]
            print(f"[DEBUG] Found {len(unique_links)} unique feed links")

            return unique_links

        except Exception as e:
            print(f"[ERROR] Feed scan error: {e}")

        return []

    def _do_comment_check(self, page):
        found_comments = []
        
        post_urls = self._get_recent_post_urls(page)
        if not post_urls:
            print("💤 [LINKEDIN] No recent posts found in notifications.", flush=True)
            return found_comments

        for target_post in post_urls:
            print(f"🌐 [LINKEDIN] Scanning post: {target_post}", flush=True)
            try:
                page.goto(target_post, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(4000)
                
                # Click load more comments if available
                self._expand_comments(page)

                # Strategy 1: Search ONLY within comment containers
                comment_items = page.locator(".comments-comment-item").all()
                for item in comment_items:
                    try:
                        # 1. Author Check
                        author_el = item.locator(".comments-post-meta__name-text").first
                        author = author_el.inner_text().strip() if author_el.count() > 0 else "LinkedIn User"
                        if "K-Electric" in author: continue

                        # 2. Content Check
                        text_el = item.locator(".comments-comment-item__main-content").first
                        if text_el.count() == 0: continue
                        text = text_el.inner_text().strip()
                        
                        # 3. Keyword Match - Be more inclusive, detect all comments
                        is_relevant = any(kw.lower() in text.lower() for kw in self.keywords)

                        # Also detect if user is tagged or mentioned
                        if "kelectric" in text.lower() or "@k-electric" in text.lower():
                            is_relevant = True

                        # Accept all non-spam comments (length check)
                        if 3 < len(text) < 500:
                            print(f"🎯 [LINKEDIN] Detected relevant comment: {text[:50]}...", flush=True)
                            import hashlib
                            stable_id = hashlib.md5((text + target_post).encode()).hexdigest()
                            
                            if not any(c["id"] == f"li_{stable_id}" for c in found_comments):
                                found_comments.append({
                                    "platform": "linkedin",
                                    "user": author,
                                    "text": text,
                                    "id": f"li_{stable_id}",
                                    "type": "comment_reply",
                                    "target_post": target_post
                                })
                    except Exception as e:
                        print(f"⚠️ [LINKEDIN] Item scan err: {e}")
                        continue
            except Exception as e:
                print(f"⚠️ [LINKEDIN] Error scanning {target_post}: {e}")
                continue

        if not found_comments:
            print("💤 [LINKEDIN] No new comments detected across recent posts.", flush=True)
        return found_comments

    def _do_discovery(self, page):
        return []


    # ─────────────────────────────────────────────
    # POST REPLY — 5-Strategy + JS Fallback
    # ─────────────────────────────────────────────

    def _ensure_browser(self, target_url):
        """Initialize Playwright browser context once and navigate to target URL."""
        if self._playwright is None:
            # Start Playwright instance and create persistent context
            self._playwright = sync_playwright().start()
            self._context = self._playwright.chromium.launch_persistent_context(
                user_data_dir=LI_SESSION,
                headless=False,
                args=["--disable-blink-features=AutomationControlled"]
            )
            self._page = self._context.pages[0] if self._context.pages else self._context.new_page()
        # Navigate to the target post (or stay on current if already there)
        self._page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
        self._page.wait_for_timeout(6000)

    def _close_browser(self):
        """Close Playwright resources when done."""
        if self._context is not None:
            self._context.close()
            self._context = None
        if self._playwright is not None:
            self._playwright.stop()
            self._playwright = None
        self._page = None

    def post_reply(self, comment_context, reply_text, 
    target_post_url=None):
        """Reply to a LinkedIn comment using a persistent browser session.
        Opens the target post only once per script run.
        """
        print(f"🚀 [LINKEDIN] Attempting to reply to: {comment_context[:40]}...", flush=True)
        try:
            url_to_visit = target_post_url if target_post_url else "https://www.linkedin.com/feed/update/urn:li:activity:7458797097232855040/"
            # Ensure browser is ready and navigated
            self._ensure_browser(url_to_visit)
            page = self._page

            # ── Step 1: Expand all comments ──
            self._expand_comments(page)

            # ── Step 2: Find the comment container ──
            container = self._find_comment_container(page, comment_context)
            if container is None:
                print("❌ [LINKEDIN] Comment container not found.", flush=True)
                page.screenshot(path="li_debug_reply_fail.png", full_page=True)
                return False

            print("✅ [LINKEDIN] Container found. Scrolling into view...", flush=True)
            container.scroll_into_view_if_needed()
            page.wait_for_timeout(1000)

            # ── Step 3: Click Reply button ──
            clicked = self._click_reply_button(page, container)
            if not clicked:
                print("❌ [LINKEDIN] All Reply button strategies failed.", flush=True)
                page.screenshot(path="li_debug_reply_fail.png", full_page=True)
                return False

            page.wait_for_timeout(2000)

            # ── Step 4: Fill the reply editor ──
            filled = self._fill_editor(page, container, reply_text)
            if not filled:
                print("❌ [LINKEDIN] Could not fill reply editor.", flush=True)
                page.screenshot(path="li_debug_reply_fail.png", full_page=True)
                return False

            page.wait_for_timeout(1000)
            page.screenshot(path="li_debug_pre_submit.png", full_page=True)

            # ── Step 5: Submit ──
            submitted = self._submit_reply(page, container)
            if submitted:
                page.screenshot(path="li_debug_post_submit.png", full_page=True)
                print("✅ [LINKEDIN] Reply posted successfully!", flush=True)
                return True
            else:
                print("❌ [LINKEDIN] Submit button not found.", flush=True)
                page.screenshot(path="li_debug_reply_fail.png", full_page=True)
                return False
        except Exception as e:
            print(f"❌ [LINKEDIN] post_reply error: {e}", flush=True)
            return False
        # Note: browser stays open for subsequent replies; call _close_browser() when done.


    # ─────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────

    def _expand_comments(self, page):
        """Click 'Load more comments' buttons up to 3 times."""
        try:
            for _ in range(3):
                btns = page.get_by_role(
                    "button",
                    name=re.compile(r"load more|show previous|view \d+ more", re.IGNORECASE)
                ).all()
                clicked_any = False
                for btn in btns:
                    try:
                        if btn.is_visible():
                            btn.click()
                            page.wait_for_timeout(2000)
                            clicked_any = True
                    except:
                        continue
                if not clicked_any:
                    break
        except:
            pass

    def _find_comment_container(self, page, comment_context):
        """
        Try multiple selectors to find the comment block containing comment_context.
        Returns a Locator (element handle) or None.
        """
        safe = re.escape(comment_context)
        pattern = re.compile(safe, re.IGNORECASE)

        strategies = [
            # LinkedIn's comment item class (most reliable)
            lambda: page.locator(".comments-comment-item").filter(has_text=pattern).first,
            # Article tag (older layout)
            lambda: page.locator("article").filter(has_text=pattern).first,
            # Generic list item
            lambda: page.locator("li").filter(has_text=pattern).first,
            # Any div — use partial text match (no regex, exact=False)
            lambda: page.locator("div").filter(has_text=comment_context[:30]).last,
            # get_by_text broad match
            lambda: page.get_by_text(comment_context[:20], exact=False).first,
        ]

        for i, strategy in enumerate(strategies):
            try:
                el = strategy()
                if el.is_visible(timeout=3000):
                    print(f"✅ [LINKEDIN] Container found via strategy {i+1}", flush=True)
                    return el
            except:
                continue

        return None

    def _click_reply_button(self, page, container):
        """
        Click the Reply button to open the editor. Traverse up the DOM to find it.
        """
        try:
            # Most reliable: Button with aria-label containing reply in the same block
            clicked = container.evaluate("""
                (el) => {
                    let current = el;
                    for (let i = 0; i < 8; i++) {
                        if (!current) break;
                        const btns = current.querySelectorAll ? current.querySelectorAll('button') : [];
                        for (const b of btns) {
                            const aria = b.getAttribute('aria-label') || '';
                            const txt = b.innerText || '';
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
                print("✅ [LINKEDIN] Reply clicked via JS (aria-label tree traversal)", flush=True)
                return True
        except: pass

        # Fallback to Playwright native
        try:
            btn = container.get_by_role("button", name=re.compile(r"Reply", re.IGNORECASE)).first
            if btn.is_visible(timeout=1000):
                self._safe_click(btn, page)
                return True
        except: pass

        return False

    def _fill_editor(self, page, container, reply_text):
        """Find the reply editor and fill it with reply_text using press_sequentially for React events."""
        try:
            # The editor is usually inside the container after reply is clicked
            editor = page.locator(".ql-editor, div[role='textbox']").first
            if editor.count() > 0:
                editor.scroll_into_view_if_needed()
                editor.click()
                page.wait_for_timeout(500)
                editor.press_sequentially(reply_text, delay=50)
                page.wait_for_timeout(1000)
                print("✅ [LINKEDIN] Editor filled successfully (press_sequentially)", flush=True)
                return True
        except Exception as e:
            print(f"❌ [LINKEDIN] Fill error: {e}")
            
        return False

    def _submit_reply(self, page, container):
        """Find and click the Post/Submit button relative to the comment container."""
        try:
            # Method 1: Press Control+Enter while the editor is focused
            try:
                page.keyboard.press("Control+Enter")
                page.wait_for_timeout(2000)
            except: pass
            
            submit_result = page.evaluate("""
                () => {
                    // Find all editors and pick the one that has text
                    const editors = document.querySelectorAll("[contenteditable='true']");
                    let activeEditor = null;
                    for (let i = editors.length - 1; i >= 0; i--) {
                        if (editors[i].innerText.trim().length > 0) {
                            activeEditor = editors[i];
                            break;
                        }
                    }

                    if (activeEditor) {
                        let parent = activeEditor.parentElement;
                        for (let i = 0; i < 15; i++) {
                            if (!parent) break;
                            const btns = parent.querySelectorAll('button');
                            for (const b of btns) {
                                const text = b.innerText ? b.innerText.trim().toLowerCase() : '';
                                if ((text === 'post' || text === 'reply' || text === 'submit' || text === 'comment') && !b.disabled) {
                                    b.click();
                                    return 'editor-parent-exact';
                                }
                            }
                            parent = parent.parentElement;
                        }
                    }
                    
                    // Fallback to global reverse
                    const allBtns = document.querySelectorAll('button');
                    for (let i = allBtns.length - 1; i >= 0; i--) {
                        const b = allBtns[i];
                        const text = b.innerText ? b.innerText.trim().toLowerCase() : '';
                        if ((text === 'submit' || text === 'post' || text === 'reply' || text === 'comment')) {
                            const aria = b.getAttribute('aria-label') || '';
                            if (!aria.toLowerCase().includes('reply to') && !aria.toLowerCase().includes('view more') && !b.disabled) {
                                b.click();
                                return 'global-reverse';
                            }
                        }
                    }
                    return false;
                }
            """)
            if submit_result:
                print(f"✅ [LINKEDIN] Submitted successfully. Method: {submit_result}", flush=True)
                page.wait_for_timeout(3000)
                return True
                
            # If the editor is gone, Control+Enter probably worked
            editors = page.locator("[contenteditable='true']").all()
            if not editors or not editors[-1].is_visible():
                print("✅ [LINKEDIN] Submitted successfully. Method: Control+Enter", flush=True)
                return True
                
        except: pass

        return False

    def _safe_click(self, element, page):
        """Try normal click first, fall back to JS click."""
        try:
            element.click(timeout=3000)
        except:
            try:
                element.evaluate("el => el.click()")
            except:
                pass


if __name__ == "__main__":
    skill = LinkedInSkill()
    print(skill.check_my_comments())
    skill._close_browser()
