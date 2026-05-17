import requests
import time
import os
from dotenv import load_dotenv

load_dotenv(".env")

# 1. Clear any existing session cache by sending a 'generate' command
# This forces the AI Engine to start fresh.
print("Step 1: Sending 'generate' command to AI Engine...")
try:
    r = requests.post("http://localhost:5000/whatsapp", json={
        "text": "generate",
        "sender": "923491379839",
        "id": f"test_{int(time.time())}"
    })
    print(f"Generate Response: {r.status_code}")
except Exception as e:
    print(f"❌ Error connecting to AI Engine: {e}")
    exit(1)

print("\nStep 2: Waiting for AI to generate draft (20 seconds)...")
time.sleep(20)

# 2. Simulate 'YES' approval
print("\nStep 3: Sending 'YES' to approve posting...")
try:
    r = requests.post("http://localhost:5000/whatsapp", json={
        "text": "yes",
        "sender": "923491379839",
        "id": f"yes_{int(time.time())}"
    })
    print(f"Yes Response: {r.status_code}")
except Exception as e:
    print(f"❌ Error during approval: {e}")

print("\nStep 4: Waiting for posting results (15 seconds)...")
time.sleep(15)

print("\n--- TEST COMPLETE ---")
print("Please check the 'logs/ai_engine.log' and 'logs/ai_engine_error.log' for results.")
