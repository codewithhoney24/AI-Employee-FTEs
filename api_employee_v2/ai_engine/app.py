import os
import sys
import requests
import threading
import time
import re
import json
import io
from flask import Flask, request
from google import genai
from dotenv import load_dotenv

# =========================
# UNICODE & BUFFER FIX
# =========================
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Fix Module Path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

def log_msg(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

# =========================
# CONFIG & ENV
# =========================

load_dotenv("../../.env", override=True)

WHATSAPP_API = "http://localhost:3001/send"
ADMIN_NUMBER = os.getenv("WHATSAPP_ADMIN_NUMBER", "923491379839").replace("+", "")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VAULT_PATH = os.path.abspath(os.path.join(BASE_DIR, "../../KE_AI_Vault"))
STATE_FILE = os.path.join(VAULT_PATH, "Logs", "social_state.json")

# Facebook/IG Credentials
FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
IG_BUSINESS_ID = os.getenv("IG_BUSINESS_ID") or os.getenv("IG_USER_ID")

# LinkedIn Credentials
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_PERSON_URN = os.getenv("LINKEDIN_PERSON_URN")

# AI Engine Client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

app = Flask(__name__)

# SCAN MODE: BOTH, POSTING, INTERACTION, or ODOO_ONLY
SCAN_MODE = os.getenv("SCAN_MODE", "BOTH").upper()
log_msg(f"🚀 ENGINE MODE: {SCAN_MODE}")

# AUTONOMOUS MODE - Auto-reply to comments WITHOUT approval
# But NEW DRAFTS always require approval (YES/NO/EDIT)
AUTONOMOUS_MODE = os.getenv("AUTONOMOUS_MODE", "true").lower() == "true"

# State management
pending_task = {
    "type": None,
    "content": None,
    "tasks": [],
    "status": "idle",
    "source_file": None,
    "raw_post": None,
    "last_notified": 0,
    "draft_key": None
}

post_cooldown_until = 0
comment_scan_active = False
NO_COOLDOWN_SECS = 300

# Session caches
processed_message_ids = set()
replied_comment_ids = set()
last_quota_error = 0
last_auto_gen = 0
last_linkedin_scan = 0
last_briefing_gen = time.time() # Initialize with current time
last_dashboard_sync = time.time() # Initialize with current time
posted_drafts_cache = set()
has_posted_at_least_once = False

# Locks
browser_lock = threading.Lock()

# Event to force immediate loop wake-up
scan_event = threading.Event()

# =========================
# STATE PERSISTENCE
# =========================

def load_state():
    global replied_comment_ids, posted_drafts_cache, has_posted_at_least_once
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
                replied_comment_ids = set(data.get("replied_ids", []))
                posted_drafts_cache = set(data.get("posted_drafts", []))
                has_posted_at_least_once = data.get("has_posted", False)
                log_msg(f"Loaded {len(replied_comment_ids)} replied IDs, {len(posted_drafts_cache)} posted drafts, posted: {has_posted_at_least_once}")
    except:
        pass

def save_state():
    global has_posted_at_least_once
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, "w") as f:
            json.dump({
                "replied_ids": list(replied_comment_ids),
                "posted_drafts": list(posted_drafts_cache),
                "has_posted": has_posted_at_least_once
            }, f)
    except:
        pass

load_state()

# =========================
# HELPERS
# =========================

def send_whatsapp(msg):
    log_msg(f"[WA] Sending: {msg[:50]}...")
    try:
        r = requests.post(WHATSAPP_API, json={"number": ADMIN_NUMBER, "message": msg}, timeout=20)
        log_msg(f"[WA] Response: {r.status_code}")
        time.sleep(1)
        return True
    except Exception as e:
        log_msg(f"[WA] Error: {e}")
        return False

# =========================
# AI BRAIN
# =========================

def generate_ai_content(prompt):
    global last_quota_error
    if not client: return None
    try:
        # Use Flash model for interactions (much higher quota)
        model_name = "gemini-2.0-flash" 
        response = client.models.generate_content(model=model_name, contents=prompt)
        return response.text.strip()
    except Exception as e:
        log_msg(f"⚠️ [AI] Error: {e}")
        return None

def draft_comment_reply(text, user, platform):
    prompt = f"User {user} commented on K-Electric {platform}: '{text}'. Short helpful reply (under 20 words). Use emojis."
    return generate_ai_content(prompt)

def generate_new_draft():
    """Generate a new AI draft and save to file"""
    social_folder = os.path.join(VAULT_PATH, "Social_Media")
    os.makedirs(social_folder, exist_ok=True)

    # Generate content using AI
    prompt = """Generate a social media post about K-Electric business achievements, growth, or energy sector news in Pakistan. Make it professional, positive, and engaging with relevant hashtags. Keep it under 300 words. Include emojis."""
    content = generate_ai_content(prompt)

    if not content:
        # Fallback content if AI fails
        content = "⚡ K-Electric continues to power Karachi's growth! We're committed to providing reliable electricity and supporting Pakistan's energy sector. Stay tuned for more updates! 💡🇵🇰 #KElectric #PoweringPakistan #Energy"

    # Create new draft file
    timestamp = time.strftime("%Y-%m-%d %H:%M")
    filename = os.path.join(social_folder, f"Auto_Draft_{timestamp.replace(':', '-')}.md")

    draft_content = f"""---
[DRAFT]
"{content}"
---

*Generated: {timestamp}*
"""

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(draft_content)
        log_msg(f"Created new draft: {filename}")
        return filename
    except Exception as e:
        log_msg(f"Error creating draft: {e}")
        return None

# =========================
# PLATFORM APIs (NO TWITTER)
# =========================

def reply_li(comment_context, text, target_post=None):
    try:
        from skills.linkedin_skill import LinkedInSkill
        skill = LinkedInSkill()
        with browser_lock:
            res = skill.post_reply(comment_context, text, target_post)
            skill._close_browser()
        return res
    except Exception as e:
        log_msg(f"LinkedIn Reply Error: {e}")
        return False

def reply_fb(comment_id, text):
    try: return "id" in requests.post(f"https://graph.facebook.com/v19.0/{comment_id}/comments", data={"message": text, "access_token": FB_PAGE_ACCESS_TOKEN}).json()
    except: return False

def reply_ig(comment_id, text):
    try: return "id" in requests.post(f"https://graph.facebook.com/v19.0/{comment_id}/replies", data={"message": text, "access_token": FB_PAGE_ACCESS_TOKEN}).json()
    except: return False

def post_to_facebook(content):
    try:
        url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/feed"
        r = requests.post(url, data={"message": content, "access_token": FB_PAGE_ACCESS_TOKEN}, timeout=15)
        result = r.json()
        log_msg(f"[FB] Result: {result}")
        return "SUCCESS" if "id" in result else f"Error: {result.get('error', 'Unknown')}"
    except Exception as e:
        log_msg(f"[FB] Exception: {e}")
        return f"Exception: {e}"

def post_to_instagram(content):
    try:
        image_url = "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?auto=format&fit=crop&w=1000"
        url = f"https://graph.facebook.com/v19.0/{IG_BUSINESS_ID}/media"
        r = requests.post(url, data={"caption": content, "image_url": image_url, "access_token": FB_PAGE_ACCESS_TOKEN}, timeout=15)
        res = r.json()
        log_msg(f"[IG] Container: {res}")
        if "id" in res:
            time.sleep(5)
            pub = requests.post(f"https://graph.facebook.com/v19.0/{IG_BUSINESS_ID}/media_publish", data={"creation_id": res["id"], "access_token": FB_PAGE_ACCESS_TOKEN})
            return "SUCCESS" if "id" in pub.json() else f"Error: {pub.json()}"
        return f"Error: {res}"
    except Exception as e:
        log_msg(f"[IG] Exception: {e}")
        return f"Exception: {e}"

def post_to_linkedin(content):
    try:
        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {"Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}", "Content-Type": "application/json", "X-Restli-Protocol-Version": "2.0.0"}
        payload = {"author": LINKEDIN_PERSON_URN, "lifecycleState": "PUBLISHED", "specificContent": {"com.linkedin.ugc.ShareContent": {"shareCommentary": {"text": content}, "shareMediaCategory": "NONE"}}, "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}}
        r = requests.post(url, headers=headers, json=payload, timeout=15)
        log_msg(f"[LI] Result: {r.status_code}")
        return "SUCCESS" if r.status_code in [200, 201] else f"Error: {r.status_code}"
    except Exception as e:
        log_msg(f"[LI] Exception: {e}")
        return f"Exception: {e}"

# =========================
# DRAFT DETECTION
# =========================

def scan_for_drafts():
    """Scan all Social_Media files for [DRAFT] posts"""
    drafts = []
    social_folder = os.path.join(VAULT_PATH, "Social_Media")

    if not os.path.exists(social_folder):
        log_msg(f"Social folder not found: {social_folder}")
        return drafts

    for filename in os.listdir(social_folder):
        if not filename.endswith(".md"):
            continue

        if "twitter" in filename.lower():
            continue

        file_path = os.path.join(social_folder, filename)
        log_msg(f"Scanning: {filename}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            posts = re.split(r'---', content)

            for post in posts:
                if "[DRAFT]" in post:
                    caption = None

                    match = re.search(r'"([^"]+)"', post)
                    if match:
                        caption = match.group(1).strip()
                    else:
                        draft_start = post.find("[DRAFT]")
                        if draft_start != -1:
                            draft_content = post[draft_start + 7:].strip()
                            next_sep = draft_content.find("---")
                            if next_sep != -1:
                                caption = draft_content[:next_sep].strip()
                            else:
                                caption = draft_content.strip()

                    if caption and len(caption) > 5:
                        draft_key = f"{filename}:{caption[:50]}"

                        if draft_key in posted_drafts_cache:
                            log_msg(f"Skipping already posted: {draft_key[:30]}...")
                            continue

                        platform = filename.split("_")[0].lower()

                        drafts.append({
                            "content": caption,
                            "platform": platform,
                            "file": file_path,
                            "filename": filename,
                            "raw_post": post.strip(),
                            "draft_key": draft_key
                        })
                        log_msg(f"Found draft: {platform} - {caption[:50]}...")

        except Exception as e:
            log_msg(f"Error reading {filename}: {e}")

    return drafts

def send_draft_for_approval(draft):
    """Send draft to WhatsApp for user approval with YES/NO/EDIT options"""
    content = draft["content"]

    # Format the message with full content
    msg = f"""📝 *NEW DRAFT DETECTED*

━━━━━━━━━━━━━━━━━━━━━━
📄 *CONTENT:*
{content}
━━━━━━━━━━━━━━━━━━━━━━

🤖 *AI will post to:*
✅ Facebook
✅ Instagram
✅ LinkedIn

━━━━━━━━━━━━━━━━━━━━━━

🔘 *REPLY WITH:*
✅ *YES* - Post to ALL platforms
❌ *NO* - Cancel this post
📝 *EDIT* - Modify before posting"""

    send_whatsapp(msg)

# =========================
# COMMENT SCANNING
# =========================

def get_all_social_interactions():
    global last_linkedin_scan, replied_comment_ids
    results = []

    load_state()

    # Keywords to filter - relaxed to catch more interactions
    KEYWORDS = ["kelectric", "k-electric", "k electric", "ke", "karachi", "power", "electricity", "energy", "grid", "bill", "meter", "supply", "outage", "solar", "test", "help", "info", "query", "complaint", "thank", "good", "excellent", "well done"]

    def is_relevant(text, user):
        """Check if interaction is relevant and not from KE itself"""
        if not text: return False
        # Normalize for comparison
        text_lower = text.lower()
        user_lower = user.lower()
        
        if "k-electric" in user_lower or "kelectric" in user_lower: return False
        
        # PERMISSIVE FOR TESTING: If it contains 'test' or 'bot', it's always relevant
        if "test" in text_lower or "bot" in text_lower: return True
        
        # If it's a short comment, it's likely relevant contextually
        if len(text.split()) < 3: return True
        
        return any(kw in text_lower for kw in KEYWORDS)

    # 1. LINKEDIN - DISABLED FOR SAFETY
    # LinkedIn automation via browser is risky and has caused account restrictions.
    # log_msg("[SCAN] Checking LinkedIn...")
    # try:
    #     from skills.linkedin_skill import LinkedInSkill
    #     ... (disabled)
    # except Exception as e: log_msg(f"LI Scan Err: {e}")
    log_msg("[SCAN] LinkedIn scanning is DISABLED to protect account safety.")

    # 2. FACEBOOK
    try:
        log_msg("[SCAN] Checking Facebook...")
        posts_resp = requests.get(f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/feed?limit=10&access_token={FB_PAGE_ACCESS_TOKEN}").json()
        posts = posts_resp.get("data", [])
        log_msg(f"[SCAN] Facebook found {len(posts)} posts.")
        for p in posts:
            # Check Comments
            coms_resp = requests.get(f"https://graph.facebook.com/v19.0/{p['id']}/comments?access_token={FB_PAGE_ACCESS_TOKEN}").json()
            coms = coms_resp.get("data", [])
            for c in coms:
                if c["id"] not in replied_comment_ids:
                    user_name = c.get("from", {}).get("name", "Unknown")
                    if is_relevant(c.get("message", ""), user_name):
                        log_msg(f"🎯 Match Facebook Comment: {user_name}")
                        return [{"platform": "facebook", "id": c["id"], "text": c["message"], "user": user_name}]
                else:
                    log_msg(f"Already replied to FB: {c['id']}")
            
            # Check Reactions (Likes)
            reacts_resp = requests.get(f"https://graph.facebook.com/v19.0/{p['id']}/reactions?limit=20&access_token={FB_PAGE_ACCESS_TOKEN}").json()
            reacts = reacts_resp.get("data", [])
            for r in reacts:
                react_id = f"fb_react_{p['id']}_{r['id']}"
                if react_id not in replied_comment_ids:
                    user_name = r.get("name", "Unknown")
                    if not ("k-electric" in user_name.lower() or "kelectric" in user_name.lower()):
                        log_msg(f"🎯 Match Facebook Reaction: {user_name}")
                        return [{"platform": "facebook", "id": react_id, "text": "Liked your post", "user": user_name, "type": "reaction", "original_id": r["id"], "post_id": p["id"]}]
                else:
                    pass # Don't spam logs with likes

    except Exception as e: log_msg(f"FB Scan Err: {e}")

    # 3. INSTAGRAM
    try:
        log_msg("[SCAN] Checking Instagram...")
        media_resp = requests.get(f"https://graph.facebook.com/v19.0/{IG_BUSINESS_ID}/media?limit=10&access_token={FB_PAGE_ACCESS_TOKEN}").json()
        media = media_resp.get("data", [])
        log_msg(f"[SCAN] Instagram found {len(media)} media items.")
        for m in media:
            # Check Comments
            coms_resp = requests.get(f"https://graph.facebook.com/v19.0/{m['id']}/comments?access_token={FB_PAGE_ACCESS_TOKEN}").json()
            coms = coms_resp.get("data", [])
            for c in coms:
                if c["id"] not in replied_comment_ids:
                    user_name = c.get("username", "Unknown")
                    if is_relevant(c.get("text", ""), user_name):
                        log_msg(f"🎯 Match Instagram Comment: {user_name}")
                        return [{"platform": "instagram", "id": c["id"], "text": c["text"], "user": user_name}]
                else:
                    log_msg(f"Already replied to IG: {c['id']}")
            
    except Exception as e: log_msg(f"IG Scan Err: {e}")

    log_msg("[SCAN] No new interactions found in this cycle.")
    return []

def try_find_comments():
    coms = get_all_social_interactions()
    if coms:
        c = coms[0]
        is_reaction = c.get("type") == "reaction"
        interaction_type = "REACTION" if is_reaction else "COMMENT"
        
        log_msg(f"[AI] Drafting reply for {c['platform']} {interaction_type}...")

        if is_reaction:
            prompt = f"User {c['user']} liked a K-Electric post on {c['platform']}. Draft a very short (under 10 words) 'Thank you for the support' message with an emoji."
            reply = generate_ai_content(prompt)
        else:
            reply = draft_comment_reply(c["text"], c["user"], c["platform"])
            
        if not reply:
            reply = "Thank you for engaging with K-Electric! ⚡"

        # Update pending task
        pending_task.update({
            "type": "multi_interaction",
            "tasks": [{"platform": c["platform"], "id": c["id"], "reply": reply, "context": c["text"], "target_post": c.get("target_post"), "interaction_type": interaction_type}],
            "status": "waiting",
            "last_notified": time.time()
        })

        # Send to WhatsApp with YES/NO options
        if is_reaction:
            msg = f"""❤️ *NEW REACTION DETECTED*

━━━━━━━━━━━━━━━━━━━━━━
📝 *Platform:* {c['platform'].upper()}
👤 *From:* {c['user']}
⚡ *Action:* Liked your post
━━━━━━━━━━━━━━━━━━━━━━

🤖 *AI Suggests:*
{reply}

━━━━━━━━━━━━━━━━━━━━━━

🔘 *REPLY WITH:*
✅ *YES* - Send Thank You
❌ *NO* - Ignore"""
        else:
            msg = f"""💬 *NEW COMMENT DETECTED*

━━━━━━━━━━━━━━━━━━━━━━
📝 *Platform:* {c['platform'].upper()}
👤 *From:* {c['user']}
💬 *Comment:* {c['text'][:150]}...
━━━━━━━━━━━━━━━━━━━━━━

🤖 *AI Reply (Ready):*
{reply}

━━━━━━━━━━━━━━━━━━━━━━

🔘 *REPLY WITH:*
✅ *YES* - Post Reply
❌ *NO* - Ignore"""

        send_whatsapp(msg)
        return True
    return False

def handle_autonomous_reply(comment, reply_text):
    platform = comment["platform"]
    comment_id = comment["id"]

    log_msg(f"[AUTO-REPLY] Replying to {platform}")

    ok = False
    if platform == "facebook":
        ok = reply_fb(comment_id, reply_text)
    elif platform == "instagram":
        ok = reply_ig(comment_id, reply_text)
    elif platform == "linkedin":
        ok = reply_li(comment["context"], reply_text, comment.get("target_post"))

    if ok:
        replied_comment_ids.add(comment_id)
        save_state()
        send_whatsapp(f"✅ *AUTO-REPLIED* to {platform}:\n{reply_text}")
    else:
        send_whatsapp(f"❌ *AUTO-REPLY FAILED* on {platform}")

# =========================
# DRAFT CHECK - ALWAYS REQUIRE APPROVAL
# =========================

def try_find_single_draft():
    """Check for new draft - ALWAYS send to WhatsApp for approval"""
    if time.time() > post_cooldown_until:
        drafts = scan_for_drafts()
        if drafts:
            draft = drafts[0]
            log_msg(f"Found new draft: {draft['content'][:50]}...")

            # ALWAYS require approval for new drafts
            pending_task.update({
                "type": "post",
                "content": draft["content"],
                "platform": draft["platform"],
                "status": "waiting",
                "source_file": draft["file"],
                "raw_post": draft["raw_post"],
                "last_notified": time.time(),
                "draft_key": draft["draft_key"]
            })

            # Send to WhatsApp for approval
            send_draft_for_approval(draft)
            return True
    return False

def execute_post(content, source_file, raw_post, draft_key):
    """Execute the post after approval"""
    global has_posted_at_least_once, scanning_comments_flag

    log_msg(f"[POST] Executing: {content[:50]}...")

    f = post_to_facebook(content)
    time.sleep(1)
    i = post_to_instagram(content)
    time.sleep(1)
    l = post_to_linkedin(content)

    # Update vault
    try:
        with open(source_file, "r", encoding="utf-8") as fh:
            fc = fh.read()
        with open(source_file, "w", encoding="utf-8") as fh:
            fh.write(fc.replace(raw_post, raw_post.replace("[DRAFT]", "[POSTED]")))
        posted_drafts_cache.add(draft_key)
    except Exception as e:
        log_msg(f"Vault update error: {e}")

    f_msg = "SUCCESS" if f == "SUCCESS" else "FAILED"
    i_msg = "SUCCESS" if i == "SUCCESS" else "FAILED"
    l_msg = "SUCCESS" if l == "SUCCESS" else "FAILED"

    if f == "SUCCESS" or i == "SUCCESS" or l == "SUCCESS":
        send_whatsapp(f"🎊 *POST SUCCESSFUL*\n\n✅ Facebook: {f_msg}\n✅ Instagram: {i_msg}\n✅ LinkedIn: {l_msg}")
        # Mark that at least one post was done - now can start comment monitoring
        has_posted_at_least_once = True
        save_state()  # Save state so it persists after restart

        # AUTO-GENERATE NEXT DRAFT - Process sequentially
        log_msg("[AUTO] Generating next draft for sequential posting...")
        new_draft_file = generate_new_draft()
        if new_draft_file:
            send_whatsapp("📝 *Auto-generated next draft*\nWaiting for approval...")

        # Trigger comment scanning immediately after post
        if not scanning_comments_flag:
            scanning_comments_flag = True
            threading.Thread(target=run_comment_scan_thread, daemon=True).start()
    else:
        send_whatsapp(f"❌ *POST FAILED*\n\nFacebook: {f_msg}\nInstagram: {i_msg}\nLinkedIn: {l_msg}")

scanning_comments_flag = False

def run_comment_scan_thread():
    global scanning_comments_flag
    try:
        try_find_comments()
    finally:
        scanning_comments_flag = False

# =========================
# MAIN LOOP
# =========================

startup_sequence_done = False

def run_weekly_briefing():
    """Automated Weekly CEO Briefing on Mondays"""
    global last_briefing_gen
    from datetime import datetime
    
    now = datetime.now()
    # Check if it's Monday (weekday 0) and we haven't generated one in the last 6 days
    if now.weekday() == 0 and (time.time() - last_briefing_gen > 518400):
        log_msg("📊 Running Automated Weekly CEO Briefing...")
        try:
            import subprocess
            # Path to generate_briefing.py in root
            briefing_script = os.path.join(PROJECT_ROOT, "generate_briefing.py")
            subprocess.run(["python", briefing_script], capture_output=True)
            
            last_briefing_gen = time.time()
            send_whatsapp("📊 *Weekly CEO Briefing Generated*\nNew report available in KE_AI_Vault/Briefings")
        except Exception as e:
            log_msg(f"Briefing Error: {e}")

def fte_loop():
    global scanning_comments_flag, startup_sequence_done, post_cooldown_until, last_briefing_gen, last_dashboard_sync
    log_msg(f"🤖 RALPH ENGINE STARTED - MODE: {SCAN_MODE}")

    if SCAN_MODE == "ODOO_ONLY":
        send_whatsapp(f"📊 *ODOO MANAGER ONLINE*\nCommands: /revenue, /invoice\n(Social Scanning Disabled)")
        # In ODOO_ONLY mode, we don't check for drafts or comments automatically.
        # We only handle the periodic dashboard sync and wait for manual commands.

    # Check for briefing on startup
    if SCAN_MODE != "INTERACTION": # Briefings are business related
        run_weekly_briefing()

    if SCAN_MODE in ["BOTH", "POSTING"]:
        # FIRST: ALWAYS check for pending drafts first
        drafts = scan_for_drafts()
        if drafts:
            log_msg(f"Found {len(drafts)} pending drafts - sending to WhatsApp...")
            draft = drafts[0]
            pending_task.update({
                "type": "post",
                "content": draft["content"],
                "platform": draft["platform"],
                "status": "waiting",
                "source_file": draft["file"],
                "raw_post": draft["raw_post"],
                "last_notified": time.time(),
                "draft_key": draft["draft_key"]
            })
            send_draft_for_approval(draft)
        elif not has_posted_at_least_once:
            # No existing drafts AND never posted before - generate new AI draft
            log_msg("First run - generating new AI draft...")
            send_whatsapp("🤖 *Generating new AI draft...*")

            new_draft_file = generate_new_draft()
            if new_draft_file:
                drafts = scan_for_drafts()
                if drafts:
                    draft = drafts[0]
                    pending_task.update({
                        "type": "post",
                        "content": draft["content"],
                        "platform": draft["platform"],
                        "status": "waiting",
                        "source_file": draft["file"],
                        "raw_post": draft["raw_post"],
                        "last_notified": time.time(),
                        "draft_key": draft["draft_key"]
                    })
                    send_draft_for_approval(draft)
            else:
                send_whatsapp(f"🚀 *RALPH WIGGUM ONLINE*\nMode: POSTING\nWaiting for tasks...")
        else:
            send_whatsapp(f"🚀 *RALPH WIGGUM ONLINE*\nMode: POSTING\nMonitoring drafts...")

    if SCAN_MODE == "INTERACTION":
        mode_text = "Auto-Reply Comments" if AUTONOMOUS_MODE else "Manual Approval"
        send_whatsapp(f"🚀 *INTERACTION MANAGER ONLINE*\nMode: {mode_text}\nMonitoring comments & likes...")
        # Force immediate scan on startup
        scan_event.set()

    while True:
        try:
            log_msg(f"Loop Heartbeat (Status: {pending_task['status']}, Mode: {SCAN_MODE})")

            # Check for automated weekly briefing
            run_weekly_briefing()

            # Periodic Dashboard Sync (Every 1 hour)
            if time.time() - last_dashboard_sync > 3600:
                log_msg("🔄 Syncing Odoo Dashboard...")
                try:
                    import subprocess
                    sync_script = os.path.join(PROJECT_ROOT, "scripts", "sync_odoo_dashboard.py")
                    subprocess.run(["python", sync_script], capture_output=True)
                    last_dashboard_sync = time.time()
                except Exception as e:
                    log_msg(f"Dashboard Sync Error: {e}")

            if pending_task["status"] == "idle":
                found_task = False
                
                # SKIP automatic scans if in ODOO_ONLY mode
                if SCAN_MODE == "ODOO_ONLY":
                    pass
                else:
                    # Check for drafts ONLY if in POSTING or BOTH mode
                    if SCAN_MODE in ["BOTH", "POSTING"]:
                        found_task = try_find_single_draft()

                    # Check comments IF in INTERACTION or BOTH mode
                    if not found_task and not scanning_comments_flag:
                        if SCAN_MODE in ["BOTH", "INTERACTION"]:
                            scanning_comments_flag = True
                            threading.Thread(target=run_comment_scan_thread, daemon=True).start()

            elif pending_task["status"] == "waiting":
                # Reminder and secondary scanning
                if SCAN_MODE in ["BOTH", "INTERACTION"] and not scanning_comments_flag:
                    scanning_comments_flag = True
                    threading.Thread(target=run_comment_scan_thread, daemon=True).start()

                # Reminder for pending approval (every 10 minutes)
                if time.time() - pending_task["last_notified"] > 600:
                    if pending_task["type"] == "post":
                        send_draft_for_approval({
                            "content": pending_task["content"],
                            "platform": pending_task["platform"],
                            "file": pending_task["source_file"],
                            "raw_post": pending_task["raw_post"],
                            "draft_key": pending_task.get("draft_key", "")
                        })
                    elif pending_task["type"] == "multi_interaction":
                        task = pending_task["tasks"][0] if pending_task["tasks"] else {}
                        msg = f"""💬 *COMMENT STILL WAITING*

━━━━━━━━━━━━━━━━━━━━━━
📝 *Platform:* {task.get('platform', 'Unknown').upper()}
💬 *Comment:* {task.get('context', '')[:100]}...
🤖 *Reply:* {task.get('reply', '')}

━━━━━━━━━━━━━━━━━━━━━━

✅ *YES* - Post Reply
❌ *NO* - Ignore"""
                        send_whatsapp(msg)
                    pending_task["last_notified"] = time.time()

        except Exception as e:
            log_msg(f"LOOP ERROR: {e}")
            import traceback
            traceback.print_exc()

        scan_event.wait(5)
        scan_event.clear()

# =========================
# WHATSAPP WEBHOOK - Handle YES/NO/EDIT
# =========================

@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    global post_cooldown_until, last_linkedin_scan
    data = request.json
    raw_text = (data.get("text") or "").strip()
    clean_text = raw_text.lower()
    
    log_msg(f"DEBUG: Webhook Received - Raw: '{raw_text}', Clean: '{clean_text}' from {data.get('sender')}")
    
    if data.get("id") in processed_message_ids: return {"ok": True}
    processed_message_ids.add(data.get("id"))

    # 1. PRIORITY BUSINESS COMMANDS (Odoo)
    if clean_text == "/revenue" or "/revenue" in clean_text:
        log_msg("🎯 MATCH: /revenue command detected")
        send_whatsapp("📊 *Fetching Odoo Revenue Summary...*")
        try:
            from skills.odoo_skill import OdooSkill
            odoo = OdooSkill()
            summary = odoo.get_revenue_summary()
            
            if isinstance(summary, dict):
                msg = f"""📊 *ODOO REVENUE SUMMARY*

━━━━━━━━━━━━━━━━━━━━━━
💰 *Total Revenue:* {summary['total_revenue']:,.2f} PKR
⏳ *Pending Payments:* {summary['pending_payments']:,.2f} PKR
📝 *Total Invoices:* {summary['count']}
━━━━━━━━━━━━━━━━━━━━━━
*Status:* Odoo ERP Connected ✅"""
                send_whatsapp(msg)
                # Sync to Obsidian
                try:
                    from scripts.sync_odoo_dashboard import sync_dashboard
                    sync_dashboard()
                except Exception as e:
                    log_msg(f"Sync Error: {e}")
            else:
                send_whatsapp(f"❌ Odoo Error: {summary}")
        except Exception as e:
            log_msg(f"Odoo Revenue Error: {e}")
            send_whatsapp(f"❌ Error fetching revenue: {e}")
        return {"ok": True}

    if clean_text.startswith("/invoice"):
        log_msg("🎯 MATCH: /invoice command detected")
        import re
        # Pattern to handle: /invoice [Customer Name] 1000 Description
        # OR: /invoice Customer Name 1000 Description (if no brackets)
        
        # 1. Try to extract from brackets first: /invoice [Ali Khan] 15000 ...
        match = re.search(r'/invoice\s+\[(.*?)\]\s+([\d,.]+)(.*)', raw_text, re.IGNORECASE)
        
        if not match:
            # 2. Try simple space split but assume everything after command until a number is the name
            # Pattern: /invoice {Name} {Amount} {Description}
            match = re.search(r'/invoice\s+(.*?)\s+([\d,.]+)(.*)', raw_text, re.IGNORECASE)

        if match:
            customer = match.group(1).strip()
            amount_str = match.group(2).strip().replace(",", "")
            desc = match.group(3).strip() or "AI Service"
            
            try:
                amount = float(amount_str)
                send_whatsapp(f"⏳ *Creating Odoo Invoice for {customer}...*")
                from skills.odoo_skill import OdooSkill
                odoo = OdooSkill()
                inv_id = odoo.create_invoice(customer, amount, desc)
                
                if inv_id:
                    send_whatsapp(f"✅ *INVOICE CREATED*\n\n👤 *Customer:* {customer}\n💰 *Amount:* {amount:,.2f} PKR\n📝 *Ref:* {desc}\n🆔 *Odoo ID:* {inv_id}")
                    # Sync to Obsidian
                    try:
                        from scripts.sync_odoo_dashboard import sync_dashboard
                        sync_dashboard()
                    except Exception as e:
                        log_msg(f"Sync Error: {e}")
                else:
                    send_whatsapp("❌ Failed to create invoice in Odoo.")
            except Exception as e:
                log_msg(f"Invoice Create Error: {e}")
                send_whatsapp(f"❌ Error: {e}")
        else:
            send_whatsapp("📝 *Usage:* /invoice [Name] [Amount] [Description]")
        return {"ok": True}

    # 2. TASK APPROVALS (YES/NO/EDIT)
    if clean_text == "yes" and pending_task["status"] == "waiting":
        if pending_task["type"] == "post":
            send_whatsapp("⏳ *Posting to all platforms...*")
            execute_post(
                pending_task["content"],
                pending_task["source_file"],
                pending_task["raw_post"],
                pending_task.get("draft_key", "")
            )

        elif pending_task["type"] == "multi_interaction":
            send_whatsapp("⏳ *Processing interaction...*")
            for t in pending_task["tasks"]:
                ok = False
                # If it's a reaction, the ID might be a composite. We need the actual target.
                target_id = t["id"]
                if t.get("interaction_type") == "REACTION" and t["platform"] == "facebook":
                    # For FB reactions, we comment on the post itself
                    target_id = t.get("post_id") or t["id"].split("_")[2] # Assuming fb_react_postid_userid
                
                if t["platform"] == "facebook": ok = reply_fb(target_id, t["reply"])
                elif t["platform"] == "instagram": ok = reply_ig(target_id, t["reply"])
                elif t["platform"] == "linkedin": ok = reply_li(t["context"], t["reply"], t.get("target_post"))
                
                if ok: replied_comment_ids.add(t["id"])
            save_state()
            send_whatsapp("🎊 *INTERACTION COMPLETE*\nChecking for more...")

        # Trigger immediate next comment check
        scan_event.set()

        pending_task["status"] = "idle"

    # Handle NO - Cancel
    elif clean_text == "no" and pending_task["status"] == "waiting":
        if pending_task["type"] == "post" and pending_task["source_file"]:
            try:
                with open(pending_task["source_file"], "r", encoding="utf-8") as f: fc = f.read()
                with open(pending_task["source_file"], "w", encoding="utf-8") as f: f.write(fc.replace(pending_task["raw_post"], pending_task["raw_post"].replace("[DRAFT]", "[CANCELLED]")))
                # Mark as posted so it won't be detected again
                if pending_task.get("draft_key"):
                    posted_drafts_cache.add(pending_task["draft_key"])
                    save_state()
            except Exception as e:
                log_msg(f"Error cancelling: {e}")
            post_cooldown_until = time.time() + NO_COOLDOWN_SECS
            send_whatsapp("🛑 *POST CANCELLED*")

        elif pending_task["type"] == "multi_interaction":
            # For comments - mark as replied so we don't scan again
            for t in pending_task["tasks"]:
                replied_comment_ids.add(t["id"])
            save_state()
            send_whatsapp("🛑 *COMMENT IGNORED*\nMoving to next comment...")

        pending_task["status"] = "idle"
        scan_event.set()  # Trigger immediate next check

    # Handle EDIT - Allow user to edit then post
    elif clean_text == "edit" and pending_task["status"] == "waiting":
        # Request user to send edited version
        send_whatsapp("📝 *Send your edited version of the reply/post*\nI'll post it after you send the new content.")
        pending_task["status"] = "editing"
        pending_task["last_notified"] = time.time()

    # Handle edited content when in editing mode
    elif pending_task["status"] == "editing":
        # User sent edited content
        if raw_text and len(raw_text) > 5:
            if pending_task["type"] == "post":
                pending_task["content"] = raw_text
            elif pending_task["type"] == "multi_interaction":
                for t in pending_task["tasks"]:
                    t["reply"] = raw_text
            
            pending_task["status"] = "waiting"
            send_whatsapp(f"📝 *Content updated!*\n\n📄 {raw_text[:200]}...\n\n✅ *YES* - Post now\n❌ *NO* - Cancel")
        else:
            send_whatsapp("❌ Invalid content. Send new text to edit.")

    return {"ok": True}

if __name__ == "__main__":
    threading.Thread(target=fte_loop, daemon=True).start()
    app.run(port=5000, host="0.0.0.0")