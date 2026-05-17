"""
SkillRegistry maintains a mapping of skill names to callable objects.
Skills are expected to be classes with a ``run`` method that accepts a
``context`` dict and returns a result.
"""

class SkillRegistry:
    def __init__(self):
        self._skills = {}

    def register(self, name: str, skill_cls):
        """Register a skill class under *name*.

        Overwrites an existing registration with the same name.
        """
        self._skills[name] = skill_cls

    def get(self, name: str):
        """Retrieve the skill class for *name* or raise ``KeyError``."""
        return self._skills[name]

    def list_skills(self):
        """Return a list of registered skill names."""
        return list(self._skills.keys())
