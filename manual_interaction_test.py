import json
import os

STATE_FILE = "KE_AI_Vault/Logs/social_state.json"

if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        data = json.load(f)
    
    # Completely clear replied_ids for a full re-scan test
    data["replied_ids"] = []
    
    with open(STATE_FILE, "w") as f:
        json.dump(data, f)
    
    print("✅ TEST: Cleared ALL replied IDs. Ready for full re-scan.")
else:
    print("❌ State file not found.")
