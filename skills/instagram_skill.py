"""
InstagramSkill – placeholder for Instagram posting integration.
The real implementation would use the Instagram Graph API via an MCP server.
"""

class InstagramSkill:
    """Skill that (in production) would post an image/video with caption to Instagram."""

    def run(self, context: dict):
        # Expected keys: ``media_path`` (image/video), ``caption``
        media = context.get("media_path", "[no media]")
        caption = context.get("caption", "[no caption]")
        return {"platform": "instagram", "status": "simulated", "media": media, "caption": caption}
