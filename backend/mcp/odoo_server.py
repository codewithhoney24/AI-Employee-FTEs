"""
Odoo MCP Server – thin wrapper around Odoo JSON‑RPC API for accounting tasks.
Only a stub implementation is provided; real calls would use the Odoo JSON‑RPC endpoint
and appropriate authentication (API key / OAuth token).
"""

import os
import json
import logging
from typing import Dict, Any

import requests

logger = logging.getLogger(__name__)

class OdooMCPServer:
    """Simple client for Odoo accounting operations.

    Expected environment variables:
        ODOO_URL      – Base URL of the Odoo instance, e.g. ``https://my‑odoo.com``
        ODOO_DB       – Database name
        ODOO_USER     – Login username
        ODOO_PASSWORD – Password or API token
    """

    def __init__(self):
        self.base_url = os.getenv("ODOO_URL", "http://localhost:8069")
        self.db = os.getenv("ODOO_DB", "dev")
        self.username = os.getenv("ODOO_USER", "admin")
        self.password = os.getenv("ODOO_PASSWORD", "admin")
        self.session_id = None
        self._authenticate()

    def _json_rpc(self, method: str, params: Dict[str, Any]) -> Any:
        """Perform a generic JSON‑RPC call to Odoo.
        Returns the ``result`` field or raises ``RuntimeError`` on error.
        """
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1,
        }
        headers = {"Content-Type": "application/json"}
        url = f"{self.base_url}/jsonrpc"
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        if response.status_code != 200:
            raise RuntimeError(f"Odoo RPC HTTP {response.status_code}: {response.text}")
        data = response.json()
        if "error" in data:
            raise RuntimeError(f"Odoo RPC error: {data['error']}")
        return data.get("result")

    def _authenticate(self):
        """Login to Odoo and store the session ID for later calls (if needed)."""
        try:
            result = self._json_rpc(
                "call",
                {
                    "service": "common",
                    "method": "login",
                    "args": [self.db, self.username, self.password],
                },
            )
            self.session_id = result
            logger.info("Authenticated to Odoo, session %s", self.session_id)
        except Exception as exc:
            logger.error("Failed to authenticate to Odoo: %s", exc)
            raise

    # ------- Public accounting helpers -----------------------------------

    def create_invoice(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an invoice.
        ``data`` should follow Odoo's ``account.move`` creation schema.
        Returns the created record ID or full record dict.
        """
        params = {
            "service": "object",
            "method": "execute_kw",
            "args": [
                self.db,
                self.session_id,
                self.password,
                "account.move",
                "create",
                [data],
            ],
        }
        result = self._json_rpc("call", params)
        logger.info("Invoice created with ID %s", result)
        return {"invoice_id": result}

    def track_payment(self, invoice_id: int, amount: float) -> Dict[str, Any]:
        """Register a payment against an invoice.
        Returns a dict with the payment record details.
        """
        payment_vals = {
            "payment_type": "inbound",
            "partner_type": "customer",
            "amount": amount,
            "payment_method_id": 1,  # placeholder – actual method ID from Odoo
            "partner_id": 1,         # placeholder – customer partner ID
            "invoice_ids": [(4, invoice_id)],
        }
        params = {
            "service": "object",
            "method": "execute_kw",
            "args": [
                self.db,
                self.session_id,
                self.password,
                "account.payment",
                "create",
                [payment_vals],
            ],
        }
        result = self._json_rpc("call", params)
        logger.info("Payment registered, ID %s", result)
        return {"payment_id": result}

    def fetch_report(self, model: str, domain: list) -> Any:
        """Generic read of records matching *domain* for a given *model*.
        Useful for dashboards, e.g. ``model='account.move', domain=[('state','!=','draft')]``.
        """
        params = {
            "service": "object",
            "method": "execute_kw",
            "args": [
                self.db,
                self.session_id,
                self.password,
                model,
                "search_read",
                [domain],
                {"fields": ["*"]},
            ],
        }
        result = self._json_rpc("call", params)
        logger.info("Fetched %d records from %s", len(result), model)
        return result

# Export a singleton for easy import elsewhere
odoo_server = OdooMCPServer()

__all__ = ["odoo_server", "OdooMCPServer"]
