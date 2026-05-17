"""
Workflow skill that creates an Odoo invoice and then posts a social update.
It demonstrates a live end‑to‑end flow using the Odoo MCP client and the generic
social MCP endpoint.
"""

import os
from backend.mcp.odoo_server import odoo_server
from backend.core.http_client import post_json
from backend.core.retry_engine import retry


class OdooSocialWorkflowSkill:
    """Create an invoice in Odoo and announce it on a social platform.

    Expected ``context`` keys:
        - ``invoice_data``: dict compatible with Odoo ``account.move`` creation.
        - ``social``: dict with ``platform`` (facebook/instagram/twitter) and
          ``message`` (text to post).
        - ``social_endpoint`` (optional): full URL of the social MCP server;
          defaults to environment variable ``SOCIAL_MCP_URL`` or a localhost stub.
    """

    @retry(attempts=3, backoff_factor=0.5, fallback={"error": "workflow failed"})
    def run(self, context: dict):
        # 1. Create invoice in Odoo
        invoice_data = context.get("invoice_data", {})
        invoice_res = odoo_server.create_invoice(invoice_data)
        invoice_id = invoice_res.get("invoice_id")

        # 2. Prepare social payload – include a link or reference to the invoice
        social_cfg = context.get("social", {})
        platform = social_cfg.get("platform", "facebook")
        message = social_cfg.get("message", f"New invoice #{invoice_id} created.")
        social_payload = {
            "platform": platform,
            "message": message,
            "metadata": {"invoice_id": invoice_id},
        }

        # 3. Determine MCP endpoint
        endpoint = context.get(
            "social_endpoint",
            None,
        ) or os.getenv("SOCIAL_MCP_URL", "http://localhost:8003/social-mcp")

        # 4. Send to social MCP (HTTP POST)
        response = post_json(endpoint, social_payload)
        if response is None:
            # Let the retry decorator handle the failure – we raise to trigger retry
            raise RuntimeError("Social MCP call failed")

        return {
            "invoice": invoice_res,
            "social_response": response,
        }

__all__ = ["OdooSocialWorkflowSkill"]
