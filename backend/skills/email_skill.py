"""
EmailSkill – placeholder for sending email via an MCP server.
"""

class EmailSkill:
    """Skill to send an email. In production this would call an email MCP server.
    Expected ``context`` keys: ``to``, ``subject``, ``body``.
    """

    def run(self, context: dict):
        to = context.get("to", "[no recipient]")
        subject = context.get("subject", "[no subject]")
        body = context.get("body", "[no body]")
        return {
            "platform": "email",
            "status": "simulated",
            "to": to,
            "subject": subject,
            "body": body,
        }
