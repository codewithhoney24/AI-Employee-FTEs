#!/usr/bin/env python3
# Simple social media auto‑poster with human‑in‑the‑loop approval
# Requires environment variables:
#   FB_PAGE_ACCESS_TOKEN, IG_USER_ACCESS_TOKEN, LI_ACCESS_TOKEN
#   (and corresponding page/user IDs set in .env or exported)
#
# Usage: python social_post.py path/to/draft.md
# The draft markdown file should contain the text to post.
# The script will display the content, ask for your approval, then POST
# to Facebook, Instagram (via Graph API) and LinkedIn (via v2 API).

import os, sys, json, requests
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed – assume environment variables are already set
    pass

def load_draft(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def ask_approval(content):
    print("--- Draft Content ---")
    print(content)
    print("---------------------")
    resp = input("Post to Facebook, Instagram, LinkedIn? [y/N]: ")
    return resp.lower().startswith('y')

def post_facebook(message):
    token = os.getenv('FB_PAGE_ACCESS_TOKEN')
    page_id = os.getenv('FB_PAGE_ID')
    if not token or not page_id:
        print('Facebook token or page ID not set – skipping')
        return
    url = f'https://graph.facebook.com/{page_id}/feed'
    r = requests.post(url, data={'message': message, 'access_token': token})
    print('Facebook response:', r.status_code, r.text)

def post_instagram(message):
    # Instagram posting works via the Facebook Graph API for Instagram Business accounts
    token = os.getenv('IG_USER_ACCESS_TOKEN')
    ig_user_id = os.getenv('IG_USER_ID')
    if not token or not ig_user_id:
        print('Instagram token or user ID not set – skipping')
        return
    # 1. Create the container
    container_url = f'https://graph.facebook.com/v15.0/{ig_user_id}/media'
    c = requests.post(container_url, data={'caption': message, 'access_token': token})
    if c.status_code != 200:
        print('Instagram container error:', c.text)
        return
    container_id = c.json().get('id')
    # 2. Publish the container
    publish_url = f'https://graph.facebook.com/v15.0/{ig_user_id}/media_publish'
    p = requests.post(publish_url, data={'creation_id': container_id, 'access_token': token})
    print('Instagram publish response:', p.status_code, p.text)

def post_linkedin(message):
    token = os.getenv('LI_ACCESS_TOKEN') or os.getenv('LINKEDIN_ACCESS_TOKEN')
    author_urn = os.getenv('LI_AUTHOR_URN') or os.getenv('LINKEDIN_PERSON_URN')
    if not token or not author_urn:
        print('LinkedIn token or author URN not set – skipping')
        return
    url = 'https://api.linkedin.com/v2/ugcPosts'
    headers = {'Authorization': f'Bearer {token}', 'X-Restli-Protocol-Version': '2.0.0', 'Content-Type': 'application/json'}
    payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": message},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    r = requests.post(url, headers=headers, data=json.dumps(payload))
    print('LinkedIn response:', r.status_code, r.text)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python social_post.py path/to/draft.md')
        sys.exit(1)
    draft_path = sys.argv[1]
    content = load_draft(draft_path)
    if not content:
        print('Draft is empty – aborting')
        sys.exit(1)
    if not ask_approval(content):
        print('Approval denied – aborting')
        sys.exit(0)
    post_facebook(content)
    post_instagram(content)
    post_linkedin(content)
    print('Done')
