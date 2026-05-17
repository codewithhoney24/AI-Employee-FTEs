"""
Simple LinkedIn Comment Checker - Fast & Direct
Uses existing browser session to check notifications
"""

import os
import sys
import time
import json
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

WHATSAPP_API = "http://localhost:3001/send"
ADMIN_NUMBER = os.getenv("WHATSAPP_ADMIN_NUMBER", "923491379839").replace("+", "")
STATE_FILE = os.path.join(PROJECT_ROOT, "KE_AI_Vault", "Logs", "social_state.json")
LI_SESSION = os.path.join(PROJECT_ROOT, "KE_AI_Vault", ".sessions", "linkedin")

def load_state():
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
                return set(data.get("replied_ids", []))
    except:
        pass
    return set()

def save_reply(comment_id):
    try:
        state = {}
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                state = json.load(f)
        replied_ids = set(state.get("replied_ids", []))
        replied_ids.add(comment_id)
        state["replied_ids"] = list(replied_ids)
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except:
        pass

def send_whatsapp(msg):
    try:
        requests.post(WHATSAPP_API, json={"number": ADMIN_NUMBER, "message": msg}, timeout=10)
        print(f"WA sent: {msg[:50]}...")
    except Exception as e:
        print(f"WA Error: {e}")

def check_linkedin_simple():
    """Simple direct check of LinkedIn notifications"""
    print("[LINKEDIN] Checking notifications...")

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            LI_SESSION,
            headless=False,  # Keep visible so user can see
            slow_mo=500
        )
        page = browser.pages[0] if browser.pages else browser.new_page()

        try:
            # Go to notifications - longer timeout
            page.goto("https://www.linkedin.com/notifications/", wait_until="load", timeout=45000)
            page.wait_for_timeout(5000)

            # Scroll down to load more content
            print("[SCROLL] Scrolling to load notifications...")
            for i in range(3):
                page.evaluate("window.scrollBy(0, 800)")
                page.wait_for_timeout(1500)
            page.wait_for_timeout(2000)

            # Get all notification items - simplified approach
            # Get the page text to see what's there
            page_text = page.evaluate("() => document.body.innerText")
            print(f"[DEBUG] Page text length: {len(page_text)} chars")

            # Try to find any links that look like notifications
            all_links = page.evaluate("""
                () => {
                    const anchors = document.querySelectorAll('a');
                    const results = [];
                    anchors.forEach(a => {
                        if (a.href && a.href.length > 20) {
                            results.push(a.href.substring(0, 150));
                        }
                    });
                    return results;
                }
            """)
            print(f"[DEBUG] Total links found: {len(all_links)}")
            # Print first 10 links
            for i, l in enumerate(all_links[:10]):
                print(f"  Link {i+1}: {l[:80]}...")

            # Get notification items - look for anything that looks like an activity/notification
            notifications = page.evaluate("""
                () => {
                    let results = [];
                    // Get all list items and divs that might be notifications
                    const allElements = document.querySelectorAll('li, div[role="listitem"]');
                    allElements.forEach(el => {
                        const text = el.innerText || "";
                        // Look for text that mentions activities
                        if (text.length > 30 && (text.includes('comment') || text.includes('replied') || text.includes('liked') || text.includes('reaction'))) {
                            results.push(text.substring(0, 200));
                        }
                    });
                    return results.slice(0, 10);
                }
            """)

            print(f"[LINKEDIN] Found {len(notifications)} notification items with activity keywords")

            replied = load_state()

            # Check for comment-related notifications
            for notif in notifications:
                text = notif['text'].lower()
                link = notif['link']

                # Look for comment/mention patterns
                if any(k in text for k in ['comment', 'replied', 'mentioned', 'liked', '反应']):
                    # Extract comment ID from link
                    comment_id = link.split('?')[0][-20:] if link else f"li_{hash(text)}"

                    if comment_id not in replied and len(text) > 20:
                        print(f"[FOUND] Comment: {text[:60]}...")

                        # Generate simple reply
                        reply = "Thank you for engaging with K-Electric! We appreciate your support. ⚡"

                        # Send to WhatsApp
                        msg = f"""💬 *NEW LINKEDIN COMMENT*

━━━━━━━━━━━━━━━━━━━━━━
💬 *Comment:*
{notif['text'][:150]}...

━━━━━━━━━━━━━━━━━━━━━━

🤖 *AI Reply:*
{reply}

━━━━━━━━━━━━━━━━━━━━━━

🔘 *REPLY WITH:*
✅ *YES* - Post Reply
❌ *NO* - Ignore"""

                        send_whatsapp(msg)
                        return True

        except Exception as e:
            print(f"[LINKEDIN] Error: {e}")

        browser.close()

    return False

# Also check for own posts' comments
def check_own_posts_comments():
    """Check comments on your own posts"""
    print("[LINKEDIN] Checking own posts...")

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            LI_SESSION,
            headless=False,
            slow_mo=100
        )
        page = browser.pages[0] if browser.pages else browser.new_page()

        try:
            # Go to your posts
            page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(3000)
            page.evaluate("window.scrollBy(0, 2000)")
            page.wait_for_timeout(2000)

            # Get posts with comments
            posts = page.evaluate("""
                () => {
                    const items = document.querySelectorAll('.feed-shared-update-v2');
                    const results = [];
                    items.forEach(item => {
                        const text = item.querySelector('.feed-shared-text')?.innerText || "";
                        const comments = item.querySelectorAll('.comments-comment-item').length;
                        if (comments > 0) {
                            results.push({
                                post: text.substring(0, 100),
                                comments: comments,
                                link: item.querySelector('a')?.href || ""
                            });
                        }
                    });
                    return results;
                }
            """)

            print(f"[LINKEDIN] Found {len(posts)} posts with comments")

            replied = load_state()

            for post in posts:
                comment_id = f"post_{hash(post['post'])}"
                if comment_id not in replied and post['comments'] > 0:
                    print(f"[FOUND] Post with {post['comments']} comments")

                    msg = f"""💬 *LINKEDIN POST HAS {post['comments']} NEW COMMENTS*

━━━━━━━━━━━━━━━━━━━━━━
📝 *Post:*
{post['post']}...

━━━━━━━━━━━━━━━━━━━━━━

Click YES to check and reply to comments."""

                    send_whatsapp(msg)
                    return True

        except Exception as e:
            print(f"[LINKEDIN] Posts Error: {e}")

        browser.close()

    return False

if __name__ == "__main__":
    print("=" * 50)
    print("Simple LinkedIn Comment Checker Started")
    print("=" * 50)

    # Try notifications first, then own posts
    while True:
        try:
            if not check_linkedin_simple():
                if not check_own_posts_comments():
                    print("[WAIT] No new comments...")
        except Exception as e:
            print(f"[ERROR] {e}")

        time.sleep(60)  # Check every minute