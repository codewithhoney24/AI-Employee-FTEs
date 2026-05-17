"""
Executor module for Claude Code skill execution.
It loads skill classes from the `skills` package, registers them in the
SkillRegistry, and routes incoming requests to the appropriate skill.
"""

from .skill_registry import SkillRegistry
from .router import Router

# Global singleton instances (simple for now)
registry = SkillRegistry()
router = Router(registry)

__all__ = ["registry", "router", "SkillRegistry", "Router"]
