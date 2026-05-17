"""
SocialSkill – placeholder for posting to social platforms (Facebook, Instagram, Twitter).
"""

class SocialSkill:
    """Unified social posting skill.
    ``context`` should contain ``platform`` (e.g., "facebook"), ``message`` and optional ``media_path``.
    The skill routes internally to the appropriate platform-specific logic.
    """

    def run(self, context: dict):
        platform = context.get("platform", "unknown")
        message = context.get("message", "[no message]")
        media = context.get("media_path")
        # Simulated result – in production replace with MCP calls per platform.
        return {
            "platform": platform,
            "status": "simulated",
            "message": message,
            "media": media,
        }
