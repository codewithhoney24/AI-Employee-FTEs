"""
Router dispatches a request to the appropriate skill based on the
``skill_name`` field in the inbound payload.

The router expects a ``registry`` (instance of ``SkillRegistry``) and
calls ``skill_cls().run(context)``.
"""

from backend.core.retry_engine import retry

class Router:
    def __init__(self, registry):
        self.registry = registry
        # Configure retry parameters – can be tuned later
        self._retry_decorator = retry(attempts=3, backoff_factor=0.5, fallback={"error": "skill execution failed"})

    def route(self, payload: dict):
        """Dispatch *payload* to the matching skill.

        ``payload`` must contain:
            - ``skill_name``: name of the skill to execute
            - ``context``: dict passed to the skill's ``run`` method
        """
        skill_name = payload.get("skill_name")
        if not skill_name:
            raise ValueError("payload missing 'skill_name'")
        skill_cls = self.registry.get(skill_name)
        skill_instance = skill_cls()
        # Wrap the run call with the retry decorator for resilience
        run_with_retry = self._retry_decorator(skill_instance.run)
        return run_with_retry(payload.get("context", {}))
