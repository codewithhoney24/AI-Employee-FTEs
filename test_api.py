import requests
import os
from dotenv import load_dotenv

load_dotenv(".env")

FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")

print(f"Checking FB Page: {FB_PAGE_ID}")
posts = requests.get(f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/feed?limit=10&access_token={FB_PAGE_ACCESS_TOKEN}").json().get("data", [])

for p in posts:
    print(f"\nPost: {p.get('message', 'No message')[:50]}... (ID: {p['id']})")
    coms = requests.get(f"https://graph.facebook.com/v19.0/{p['id']}/comments?access_token={FB_PAGE_ACCESS_TOKEN}").json().get("data", [])
    for c in coms:
        print(f"  - Comment: {c.get('message', 'No message')} (ID: {c['id']})")
