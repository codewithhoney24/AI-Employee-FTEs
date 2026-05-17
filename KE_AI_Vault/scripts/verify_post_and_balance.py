"""
Verification script: confirm the latest tweet matches the demo output and fetch the current account balance from Odoo.
Run it after the demo (or on a schedule) to get automatic confirmation.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Twitter verification – uses bearer token & user ID from env vars
TWITTER_BEARER = os.getenv("TWITTER_BEARER")
TWITTER_USER_ID = os.getenv("TWITTER_USER_ID")
DEMO_CONTENT_MARKER = "KE AI Employee Demo: Automated pipeline test SUCCESSFUL!"

# Odoo balance fetch – expects ODOO env vars (already used by odoo_server)
from backend.mcp.odoo_server import odoo_server

# Helper: simple GET via the generic HTTP client (used for Twitter)
from backend.core.http_client import post_json
import urllib.request
import urllib.error

def fetch_latest_tweet():
    if not TWITTER_BEARER or not TWITTER_USER_ID:
        raise RuntimeError("TWITTER_BEARER and TWITTER_USER_ID must be set in the environment.")
    url = f"https://api.twitter.com/2/users/{TWITTER_USER_ID}/tweets?max_results=5&tweet.fields=created_at,text"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {TWITTER_BEARER}")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Twitter API error {e.code}: {e.read().decode()}")
    except Exception as e:
        raise RuntimeError(f"Failed to fetch tweets: {e}")
    tweets = data.get("data", [])
    if not tweets:
        raise RuntimeError("No tweets returned for the user.")
    return tweets[0]  # most recent tweet


def verify_demo_tweet(tweet):
    text = tweet.get("text", "")
    if DEMO_CONTENT_MARKER in text:
        print("✅ Tweet verification passed – demo tweet is present.")
        print(f"   Tweet ID: {tweet.get('id')}  Time: {tweet.get('created_at')}")
    else:
        print("⚠️ Tweet verification failed – expected demo content not found.")
        print(f"   Latest tweet text: {text}")


def fetch_account_balance():
    # Simple example: read the balance of a top‑level cash/account (id=1)
    # In a real setup you would fetch the appropriate account ID from config.
    account_id = os.getenv("ODOO_ACCOUNT_ID", "1")
    domain = [("id", "=", int(account_id))]
    try:
        records = odoo_server.fetch_report("account.account", domain)
    except Exception as e:
        raise RuntimeError(f"Failed to fetch Odoo balance: {e}")
    if not records:
        raise RuntimeError(f"No account record found for id {account_id}")
    account = records[0]
    balance = account.get("balance") or account.get("debit") - account.get("credit")
    print("💰 Odoo account balance fetched:")
    print(f"   Account ID: {account_id}")
    print(f"   Name: {account.get('name')}")
    print(f"   Balance: {balance}")


def main():
    try:
        tweet = fetch_latest_ttweet()
    except Exception as e:
        print(f"❌ Error fetching tweet: {e}")
        sys.exit(1)
    verify_demo_tweet(tweet)
    try:
        fetch_account_balance()
    except Exception as e:
        print(f"❌ Error fetching Odoo balance: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
