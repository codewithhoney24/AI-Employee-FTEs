"""
HealthCheckSkill – verifies the AI system's health by checking:
1. The latest tweet on the configured Twitter account contains the demo marker.
2. The Odoo accounting account balance can be retrieved.
Both checks are performed using environment variables for credentials.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any

# Odoo MCP client (already uses environment vars for connection)
from backend.mcp.odoo_server import odoo_server

DEMO_CONTENT_MARKER = "KE AI Employee Demo: Automated pipeline test SUCCESSFUL!"

class HealthCheckSkill:
    """Run health‑check for social‑media posting and accounting integration.

    No input ``context`` is required, but you may optionally pass:
        {
            "twitter": {"bearer": "...", "user_id": "..."},
            "odoo_account_id": "1"
        }
    The environment variables ``TWITTER_BEARER`` and ``TWITTER_USER_ID`` are used as defaults.
    """

    def _fetch_latest_tweet(self) -> Dict[str, Any]:
        bearer = os.getenv("TWITTER_BEARER")
        user_id = os.getenv("TWITTER_USER_ID")
        if not bearer or not user_id:
            raise RuntimeError("TWITTER_BEARER and TWITTER_USER_ID must be set.")
        url = f"https://api.twitter.com/2/users/{user_id}/tweets?max_results=5&tweet.fields=created_at,text"
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {bearer}")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.load(resp)
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Twitter API error {e.code}: {e.read().decode()}")
        tweets = data.get("data", [])
        if not tweets:
            raise RuntimeError("No tweets returned for the user.")
        return tweets[0]  # most recent tweet

    def _verify_demo_tweet(self, tweet: Dict[str, Any]) -> bool:
        text = tweet.get("text", "")
        return DEMO_CONTENT_MARKER in text

    def _fetch_odoo_balance(self) -> Dict[str, Any]:
        account_id = os.getenv("ODOO_ACCOUNT_ID", "1")
        domain = [("id", "=", int(account_id))]
        records = odoo_server.fetch_report("account.account", domain)
        if not records:
            raise RuntimeError(f"No Odoo account found for id {account_id}")
        account = records[0]
        balance = account.get("balance") or (account.get("debit", 0) - account.get("credit", 0))
        return {"id": account_id, "name": account.get("name"), "balance": balance}

    def run(self, context: dict = None) -> dict:
        # Allow overrides via context (optional)
        if context is None:
            context = {}
        # ---- Twitter check ----
        try:
            tweet = self._fetch_latest_tweet()
            tweet_ok = self._verify_demo_tweet(tweet)
            tweet_result = {
                "ok": tweet_ok,
                "tweet_id": tweet.get("id"),
                "created_at": tweet.get("created_at"),
                "text": tweet.get("text"),
            }
        except Exception as e:
            tweet_result = {"error": str(e)}

        # ---- Odoo balance check ----
        try:
            balance_info = self._fetch_odoo_balance()
        except Exception as e:
            balance_info = {"error": str(e)}

        return {
            "twitter_check": tweet_result,
            "odoo_balance": balance_info,
        }

__all__ = ["HealthCheckSkill"]
