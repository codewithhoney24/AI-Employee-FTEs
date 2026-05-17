import requests
import os
from dotenv import load_dotenv

load_dotenv(".env")
FB_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
FB_ID = os.getenv("FB_PAGE_ID")

print(f"--- Facebook Comment Test ---")
print(f"Page ID: {FB_ID}")

try:
    # 1. Get posts
    posts_url = f"https://graph.facebook.com/v19.0/{FB_ID}/feed?limit=5&access_token={FB_TOKEN}"
    posts_res = requests.get(posts_url).json()
    posts = posts_res.get("data", [])
    
    if not posts:
        print("No posts found on this page.")
    
    for post in posts:
        post_id = post.get("id")
        print(f"\nChecking Post: {post_id}")
        
        # 2. Get comments
        comments_url = f"https://graph.facebook.com/v19.0/{post_id}/comments?access_token={FB_TOKEN}"
        comments_res = requests.get(comments_url).json()
        comments = comments_res.get("data", [])
        
        if not comments:
            print("  - No comments found.")
        else:
            for comment in comments:
                print(f"  - Comment by {comment.get('from', {}).get('name', 'Unknown')}: {comment.get('message')}")

except Exception as e:
    print(f"Error: {e}")
