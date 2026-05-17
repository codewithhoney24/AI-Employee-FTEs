import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

# Master Configuration
AI_ENGINE_URL = "http://localhost:5000/whatsapp"
ADMIN_NUMBER = os.getenv("WHATSAPP_ADMIN_NUMBER", "923491379839").replace("+", "")

def trigger_new_draft():
    print("🤖 Master Agent: Generating new automated draft...")
    # This simulates a 'generate' command sent via WhatsApp to the engine
    try:
        response = requests.post(AI_ENGINE_URL, json={
            "text": "generate",
            "sender": ADMIN_NUMBER,
            "id": "manual_trigger_123"
        })
        if response.status_code == 200:
            print("✅ Draft generation triggered! Check your WhatsApp.")
        else:
            print(f"❌ Failed to trigger: {response.text}")
    except Exception as e:
        print(f"❌ Error connecting to AI Engine: {e}")

if __name__ == "__main__":
    trigger_new_draft()
