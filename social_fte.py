#!/usr/bin/env python3
# 24/7 Social‑Media FTE
# Monitors a "drafts" folder for markdown files, asks for human‑in‑the‑loop approval
# and publishes the content to Facebook, Instagram (via Graph API), LinkedIn and Twitter.
# Requires environment variables (loaded via python‑dotenv if present):
#   FB_PAGE_ACCESS_TOKEN, FB_PAGE_ID
#   IG_USER_ACCESS_TOKEN, IG_USER_ID
#   LI_ACCESS_TOKEN or LINKEDIN_ACCESS_TOKEN, LI_AUTHOR_URN or LINKEDIN_PERSON_URN
#   TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET, TWITTER_API_KEY, TWITTER_API_SECRET

import os, sys, json, time, shutil
from pathlib import Path

# Load .env if python‑dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DRAFTS_DIR = Path('drafts')
SENT_DIR   = Path('sent')
ERROR_DIR  = Path('error')

for d in (DRAFTS_DIR, SENT_DIR, ERROR_DIR):
    d.mkdir(exist_ok=True)

def load_draft(path: Path) -> str:
    return path.read_text(encoding='utf-8').strip()

def ask_approval(content: str, filename: str) -> bool:
    print(f"\n--- Draft: {filename} ---")
    print(content)
    print("-----------------------")
    return input("Post to all platforms? [y/N]: ").lower().startswith('y')

def post_facebook(message: str):
    token = os.getenv('FB_PAGE_ACCESS_TOKEN')
    page_id = os.getenv('FB_PAGE_ID')
    if not token or not page_id:
        print('Facebook token or page ID missing – skipping')
        return False
    url = f'https://graph.facebook.com/{page_id}/feed'
    r = requests.post(url, data={'message': message, 'access_token': token})
    print('Facebook response:', r.status_code, r.text)
    return r.ok

def post_instagram(message: str):
    token = os.getenv('IG_USER_ACCESS_TOKEN') or os.getenv('INSTAGRAM_ACCESS_TOKEN')
    ig_id = os.getenv('IG_USER_ID') or os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')
    if not token or not ig_id:
        print('Instagram token or business ID missing – skipping')
        return False
    container_url = f'https://graph.facebook.com/v15.0/{ig_id}/media'
    c = requests.post(container_url, data={'caption': message, 'access_token': token})
    if c.status_code != 200:
        print('Instagram container error:', c.text)
        return False
    container_id = c.json().get('id')
    publish_url = f'https://graph.facebook.com/v15.0/{ig_id}/media_publish'
    p = requests.post(publish_url, data={'creation_id': container_id, 'access_token': token})
    print('Instagram publish response:', p.status_code, p.text)
    return p.ok

def post_linkedin(message: str):
    token = os.getenv('LI_ACCESS_TOKEN') or os.getenv('LINKEDIN_ACCESS_TOKEN')
    author = os.getenv('LI_AUTHOR_URN') or os.getenv('LINKEDIN_PERSON_URN')
    if not token or not author:
        print('LinkedIn token or author URN missing – skipping')
        return False
    url = 'https://api.linkedin.com/v2/ugcPosts'
    headers = {'Authorization': f'Bearer {token}',
               'X-Restli-Protocol-Version': '2.0.0',
               'Content-Type': 'application/json'}
    payload = {
        "author": author,
        "lifecycleState": "PUBLISHED",
        "specificContent": {"com.linkedin.ugc.ShareContent": {
            "shareCommentary": {"text": message},
            "shareMediaCategory": "NONE"
        }},
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    r = requests.post(url, headers=headers, data=json.dumps(payload))
    print('LinkedIn response:', r.status_code, r.text)
    return r.ok

def post_twitter(message: str):
    # Basic tweet via v2 API (requires bearer token style app‑only auth or user OAuth)
    token = os.getenv('TWITTER_BEARER_TOKEN')
    if not token:
        # fallback to user OAuth – we'll use the classic endpoint
        api_key = os.getenv('TWITTER_API_KEY')
        api_secret = os.getenv('TWITTER_API_SECRET')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        if not all([api_key, api_secret, access_token, access_secret]):
            print('Twitter credentials missing – skipping')
            return False
        # Use requests‑oauthlib for simplicity (if installed)
        try:
            from requests_oauthlib import OAuth1
        except ImportError:
            print('requests_oauthlib not installed – cannot tweet')
            return False
        auth = OAuth1(api_key, api_secret, access_token, access_secret)
        url = 'https://api.twitter.com/2/tweets'
        r = requests.post(url, auth=auth, json={'text': message})
    else:
        url = 'https://api.twitter.com/2/tweets'
        r = requests.post(url, headers={'Authorization': f'Bearer {token}'}, json={'text': message})
    print('Twitter response:', r.status_code, r.text)
    return r.ok

def process_file(filepath: Path):
    content = load_draft(filepath)
    if not content:
        print(f'Skipping empty draft {filepath.name}')
        return
    if not ask_approval(content, filepath.name):
        print('User denied – leaving file in drafts')
        return
    results = []
    results.append(post_facebook(content))
    results.append(post_instagram(content))
    results.append(post_linkedin(content))
    results.append(post_twitter(content))
    if all(results):
        shutil.move(str(filepath), SENT_DIR / filepath.name)
        print(f'All platforms succeeded – moved to {SENT_DIR}')
    else:
        shutil.move(str(filepath), ERROR_DIR / filepath.name)
        print(f'Some platforms failed – moved to {ERROR_DIR}')

if __name__ == '__main__':
    import requests
    print('🔁 24/7 Social FTE started – watching "drafts" folder')
    # Simple poll loop (no file system events to keep dependencies minimal)
    while True:
        pending = list(DRAFTS_DIR.glob('*.md'))
        for file in pending:
            process_file(file)
        time.sleep(30)  # check every 30 seconds