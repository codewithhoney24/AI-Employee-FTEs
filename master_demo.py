import sys
import os
import time

# Mock the environment
os.environ["WHATSAPP_ADMIN_NUMBER"] = "923491379839"
sys.path.append(os.path.abspath("api_employee_v2/ai_engine"))

import app

def demo_master_agent():
    print("============================================================")
    print("🚀 MASTER AGENT DEMO: AI DRAFT -> WHATSAPP -> MULTI-POST")
    print("============================================================")
    
    # 1. Simulate finding a draft
    print("\n[STEP 1] AI Engine scans the vault...")
    mock_draft = {
        "content": "KE is committed to a greener Karachi. Our solar initiatives are expanding! ☀️🌱 #GreenerKarachi #KE",
        "platform": "twitter",
        "file": "Social_Media/Twitter_Posts.md"
    }
    print(f"✅ Draft found for {mock_draft['platform'].upper()}")

    # 2. Simulate sending WhatsApp
    print("\n[STEP 2] Sending notification to Admin via WhatsApp...")
    full_msg = (
        f"🚀 *MASTER AGENT: NEW AI DRAFT READY*\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 *FULL DRAFT:*\n\n"
        f"{mock_draft['content']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 *COMMANDS:*\n"
        f"✅ *YES* - Post to ALL (TW, FB, IG, LI)\n"
        f"❌ *NO* - Cancel Post"
    )
    print("--- WHATSAPP MESSAGE SENT ---")
    print(full_msg)
    print("------------------------------")

    # 3. Simulate Admin Approval
    print("\n[STEP 3] Admin replies 'YES' via WhatsApp...")
    print("⏳ Processing Master Post to ALL platforms...")
    
    # Mocking the posting results
    print("✅ TWITTER: Posted successfully (ID: 18273645)")
    print("✅ FACEBOOK: Posted successfully (ID: fb_99283)")
    print("✅ INSTAGRAM: Posted successfully (ID: ig_88273)")
    print("✅ LINKEDIN: Posted successfully (ID: li_77263)")

    print("\n🔥 MASTER POST COMPLETE: ALL PLATFORMS UPDATED.")
    print("============================================================")

if __name__ == "__main__":
    demo_master_agent()
