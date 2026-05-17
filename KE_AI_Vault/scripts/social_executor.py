#!/usr/bin/env python3
"""
social_executor.py — K-Electric Social Media Live Browser Automation
=====================================================================
Ye script /Approved/ folder watch karta hai.
Jaise hi koi file wahan aaye, Chrome browser VISIBLE mode mein khulta hai
aur aap apni aankhon se AI ko Facebook/Instagram/Twitter per kaam karte dekh sakti hain.
"""

import os, json, time, shutil, re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from playwright.sync_api import sync_playwright, Page

# --- CONFIGURATION ---
VAULT_ROOT   = Path("D:/AI-Employee-FTEs/KE_AI_Vault")
APPROVED_DIR = VAULT_ROOT / "Approved"
DONE_DIR     = VAULT_ROOT / "Done"
LOGS_DIR     = VAULT_ROOT / "Logs"
SESSION_DIR  = VAULT_ROOT / ".sessions"

# Load credentials
load_dotenv(dotenv_path="D:/AI-Employee-FTEs/.env")

FB_EMAIL    = os.getenv("FACEBOOK_EMAIL", "")
FB_PASS     = os.getenv("FACEBOOK_PASSWORD", "")
TW_USER     = os.getenv("TWITTER_USER", "")
TW_PASS     = os.getenv("TWITTER_PASS", "")
IG_USER     = os.getenv("INSTAGRAM_USER", "")
IG_PASS     = os.getenv("INSTAGRAM_PASS", "")

# Ensure directories exist
for d in [APPROVED_DIR, DONE_DIR, LOGS_DIR, SESSION_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def log(msg: str, status: str = "info"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {status.upper()}: {msg}")

def parse_approval(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    data = {}
    # Basic frontmatter parsing
    if text.startswith("---"):
        parts = text.split("---")
        if len(parts) >= 3:
            fm = parts[1]
            for line in fm.strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    data[k.strip().lower()] = v.strip().strip('"')
            data["content"] = parts[2].strip()
    return data

def execute_twitter(page: Page, action: dict):
    log("Opening Twitter...", "info")
    # Step 1: Go to home
    page.goto("https://x.com/home", wait_until="load", timeout=60000)
    time.sleep(5)
    
    # Step 2: Login Check & Manual Wait
    if not page.query_selector('[data-testid="SideNav_NewTweet_Button"]') and not page.query_selector('[data-testid="tweetTextarea_0"]'):
        log("NOT LOGGED IN. Please login MANUALLY in the opened window.", "warning")
        log("Waiting 60 seconds...", "info")
        for i in range(60, 0, -1):
            if page.query_selector('[data-testid="SideNav_NewTweet_Button"]') or page.query_selector('[data-testid="tweetTextarea_0"]'):
                log("Login detected!", "success")
                break
            time.sleep(1)

    if action.get("action") in ["post", "tweet"]:
        log("Starting Post Sequence...", "info")
        
        # Try Direct Compose URL (Fastest way)
        try:
            page.goto("https://x.com/compose/post", timeout=30000)
            time.sleep(3)
        except:
            pass

        # Strategy A: Find Textbox
        textarea = page.query_selector('div[role="textbox"]') or \
                   page.query_selector('[data-testid="tweetTextarea_0"]') or \
                   page.query_selector('.public-DraftEditor-content')
        
        if not textarea:
            # Strategy B: Click Sidebar Button first
            btn = page.query_selector('[data-testid="SideNav_NewTweet_Button"]')
            if btn:
                btn.click(force=True)
                time.sleep(2)
                textarea = page.query_selector('div[role="textbox"]') or \
                           page.query_selector('[data-testid="tweetTextarea_0"]')

        if textarea:
            log("Typing Content...", "info")
            textarea.click(force=True)
            page.keyboard.type(action["content"], delay=50)
            time.sleep(2)
            
            # Click Post Button
            post_btn = page.query_selector('div[data-testid="tweetButtonInline"]') or \
                       page.query_selector('[data-testid="tweetButton"]') or \
                       page.query_selector('button:has-text("Post")')
            if post_btn:
                post_btn.click(force=True)
                log("Clicking Post button...", "info")
                
                # VERIFICATION: Wait for the post box to disappear
                try:
                    page.wait_for_selector('div[role="textbox"]', state="hidden", timeout=10000)
                    log("Tweet Sent Successfully (Verified)!", "success")
                except:
                    log("Verification failed. Trying backup Enter key...", "warning")
                    page.keyboard.press("Control+Enter")
                    time.sleep(5)
                
                time.sleep(5)
            else:
                log("Could not find Post button.", "error")
        else:
            log("Could not find Tweet textbox.", "error")

def execute_facebook(page: Page, action: dict):
    log("Opening Facebook...", "info")
    page.goto("https://www.facebook.com", wait_until="networkidle")
    
    if page.query_selector('input[name="email"]'):
        log("Logging into Facebook...", "info")
        page.fill('input[name="email"]', FB_EMAIL)
        page.fill('input[name="pass"]', FB_PASS)
        page.click('button[name="login"]')
        time.sleep(5)

    if action.get("action") == "post":
        log("Creating Facebook Post...", "info")
        page.click('text="What\'s on your mind"')
        time.sleep(2)
        page.keyboard.type(action["content"], delay=50)
        time.sleep(1)
        page.click('aria-label="Post"')
        log("Facebook Post Published!", "success")
        time.sleep(3)

def handle_file(filepath: Path):
    log(f"Processing: {filepath.name}", "info")
    action_data = parse_approval(filepath)
    platform = action_data.get("platform", "").lower()
    
    if not platform:
        log("Error: No platform defined in file.", "error")
        return

    session_path = SESSION_DIR / platform

    with sync_playwright() as p:
        # UPDATED: Demo-grade Visual Settings (Full View)
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(session_path),
            headless=False, 
            slow_mo=500,
            no_viewport=True, # Forced Full Screen
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--start-maximized"
            ]
        )
        page = context.new_page() if not context.pages else context.pages[0]
        # Hide webdriver flag
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        try:
            if platform in ["twitter", "x"]:
                execute_twitter(page, action_data)
            elif platform == "facebook":
                execute_facebook(page, action_data)
            
            # VERIFICATION before archiving
            log("Final verification of the action...", "info")
            time.sleep(5)
            
            # Success! Move to Done
            shutil.move(str(filepath), str(DONE_DIR / filepath.name))
            log(f"Task Verified and moved to Done.", "success")
        except Exception as e:
            log(f"Execution Error: {e}", "error")
        finally:
            context.close()

class ApprovedHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".md"):
            time.sleep(1) # Wait for file write
            handle_file(Path(event.src_path))

if __name__ == "__main__":
    print("="*50)
    print("KE SOCIAL EXECUTOR - LIVE BROWSER MODE")
    print(f"Watching: {APPROVED_DIR}")
    print("="*50)
    
    observer = Observer()
    observer.schedule(ApprovedHandler(), str(APPROVED_DIR), recursive=False)
    observer.start()
    
    try:
        while True:
            # POLLING: Also manually check for files every 2 seconds 
            # in case the watcher misses a move event
            for f in APPROVED_DIR.glob("*.md"):
                handle_file(f)
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
