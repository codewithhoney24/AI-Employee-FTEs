import os
import re

VAULT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "KE_AI_Vault"))
social_folder = os.path.join(VAULT_PATH, "Social_Media")

print(f"Checking {social_folder}")
if not os.path.exists(social_folder):
    print("Folder does not exist")

found_draft = None
for fn in [f for f in os.listdir(social_folder) if f.endswith(".md")]:
    if "twitter" in fn.lower(): continue
    try:
        with open(os.path.join(social_folder, fn), "r", encoding="utf-8") as f:
            content = f.read()
        print(f"File: {fn}")
        posts = re.split(r'---', content)
        for p in posts:
            if "[DRAFT]" in p:
                print(f"Found [DRAFT] in {fn}!")
                cap = p.split('"')[1] if '"' in p else p.strip()
                found_draft = {"content": cap, "platform": fn.split("_")[0].lower(), "file": os.path.join(social_folder, fn), "raw": p.strip()}
                break
        if found_draft: break
    except Exception as e:
        print(f"Error: {e}")

if found_draft:
    print("Found draft:", found_draft)
else:
    print("No draft found.")
