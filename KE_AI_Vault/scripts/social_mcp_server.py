import os
import json
import sys
import urllib.request
import urllib.parse
from dotenv import load_dotenv

# Load social credentials from various .env files
load_dotenv("KE_AI_Vault/facebook/.env")

FB_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
FB_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
IG_BUSINESS_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

def fb_post(message):
    if not FB_ACCESS_TOKEN or not FB_PAGE_ID:
        return {"error": "Facebook credentials missing"}
    
    url = f"https://graph.facebook.com/v18.0/{FB_PAGE_ID}/feed"
    data = urllib.parse.urlencode({"message": message, "access_token": FB_ACCESS_TOKEN}).encode()
    
    try:
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode())
            return {"status": "success", "post_id": res_data.get("id")}
    except Exception as e:
        return {"error": str(e)}

def ig_post(image_url, caption):
    if not FB_ACCESS_TOKEN or not IG_BUSINESS_ID:
        return {"error": "Instagram credentials missing"}
    
    # IG posting is a 2-step process: 1. Container creation, 2. Publication
    container_url = f"https://graph.facebook.com/v18.0/{IG_BUSINESS_ID}/media"
    container_data = urllib.parse.urlencode({
        "image_url": image_url,
        "caption": caption,
        "access_token": FB_ACCESS_TOKEN
    }).encode()
    
    try:
        req = urllib.request.Request(container_url, data=container_data, method="POST")
        with urllib.request.urlopen(req) as response:
            container_id = json.loads(response.read().decode()).get("id")
        
        publish_url = f"https://graph.facebook.com/v18.0/{IG_BUSINESS_ID}/media_publish"
        publish_data = urllib.parse.urlencode({
            "creation_id": container_id,
            "access_token": FB_ACCESS_TOKEN
        }).encode()
        
        req2 = urllib.request.Request(publish_url, data=publish_data, method="POST")
        with urllib.request.urlopen(req2) as response:
            res_data = json.loads(response.read().decode())
            return {"status": "success", "media_id": res_data.get("id")}
    except Exception as e:
        return {"error": str(e)}

TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

def twitter_post(text):
    if not TWITTER_BEARER_TOKEN:
        return {"status": "simulated", "message": f"Tweet would be: {text}", "note": "TWITTER_BEARER_TOKEN missing in .env"}
    
    # Twitter v2 API URL
    url = "https://api.twitter.com/2/tweets"
    headers = {
        "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = json.dumps({"text": text}).encode('utf-8')
    
    try:
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode())
            return {"status": "success", "data": res_data}
    except Exception as e:
        return {"status": "error", "message": str(e), "tip": "Verify API v2 permissions & Bearer Token"}

def get_summaries():
    # Simulated summaries of recent activity
    return {
        "facebook": "Last post: 'Grid Modernization Milestone' - 342 likes, 18 comments.",
        "instagram": "Last post: 'Solar Energy Promo' - 512 likes, 4 comments.",
        "twitter": "Last tweet: 'Weather Alert' - 1.2k impressions, 15 retweets."
    }

def handle_mcp_request(request):
    method = request.get("method")
    params = request.get("params", {})
    
    if method == "facebook_post":
        return fb_post(params.get("message"))
    elif method == "instagram_post":
        return ig_post(params.get("image_url"), params.get("caption"))
    elif method == "twitter_post":
        return twitter_post(params.get("text"))
    elif method == "get_summaries":
        return get_summaries()
    else:
        return {"error": f"Method {method} not found"}

if __name__ == "__main__":
    for line in sys.stdin:
        try:
            request = json.loads(line)
            response = handle_mcp_request(request)
            print(json.dumps({"id": request.get("id"), "result": response}))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()
