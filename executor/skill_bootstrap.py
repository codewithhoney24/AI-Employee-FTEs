"""
Bootstrap script that discovers and registers all skill classes in the ``skills`` package.
It imports each module, finds attributes ending with ``Skill`` (e.g., ``HelloSkill``),
strips the ``Skill`` suffix, lower‑cases the name, and registers the class in the
provided ``SkillRegistry`` instance.
"""

import importlib
import pkgutil
from pathlib import Path

from .skill_registry import SkillRegistry


def discover_and_register(registry: SkillRegistry, package_name: str = "skills"):
    """Import every module under *package_name* and register any class whose name ends with ``Skill``.

    The class name without the ``Skill`` suffix (lower‑cased) becomes the skill identifier.
    """
    pkg = importlib.import_module(package_name)
    pkg_path = Path(pkg.__file__).parent
    for _, mod_name, is_pkg in pkgutil.iter_modules([str(pkg_path)]):
        if is_pkg:
            continue
        module = importlib.import_module(f"{package_name}.{mod_name}")
        for attr in dir(module):
            if attr.endswith("Skill"):
                cls = getattr(module, attr)
                skill_name = attr[:-5].lower()
                registry.register(skill_name, cls)

if __name__ == "__main__":
    # ✅ PROPER: Handle both relative and absolute imports
    try:
        from skill_registry import SkillRegistry
    except ImportError:
        from .skill_registry import SkillRegistry
    
    reg = SkillRegistry()
    discover_and_register(reg)
    print("Registered skills:", reg.list_skills())
