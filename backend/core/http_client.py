"""
Simple HTTP client helper for sending JSON payloads to MCP servers.
Uses the standard library ``urllib.request`` to avoid extra dependencies.
"""

import json
import logging
from urllib import request, error
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def post_json(url: str, payload: Dict[str, Any], timeout: int = 10) -> Optional[Dict[str, Any]]:
    """POST ``payload`` as JSON to ``url`` and return the decoded JSON response.

    Returns ``None`` when the request fails – callers should handle retries or
    fallback logic themselves.
    """
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            resp_data = resp.read().decode("utf-8")
            return json.loads(resp_data)
    except error.HTTPError as he:
        logger.error("HTTP error %s when POST to %s: %s", he.code, url, he.read().decode())
    except error.URLError as ue:
        logger.error("URL error when POST to %s: %s", url, ue.reason)
    except Exception as exc:
        logger.exception("Unexpected error during POST to %s", url)
    return None

__all__ = ["post_json"]
