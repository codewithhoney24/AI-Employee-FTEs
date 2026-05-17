"""
Example skill implementation.
Each skill must provide a ``run`` method that receives a ``context``
dictionary and returns any serialisable result.
"""

class HelloSkill:
    """A simple hello world skill used for testing the executor."""

    def run(self, context: dict):
        name = context.get("name", "world")
        return {"message": f"Hello, {name}!"}
