"""
Skill registry for backend core.
Maps skill identifiers to concrete skill classes.
"""

# Import skill implementations
from backend.skills.email_skill import EmailSkill
from backend.skills.social_skill import SocialSkill
from backend.skills.accounting_skill import AccountingSkill
from backend.skills.browser_skill import BrowserSkill

# Mapping used by the executor/router or other dispatchers
SKILL_MAP = {
    "email": EmailSkill,
    "social_post": SocialSkill,
    "create_invoice": AccountingSkill,
    "browser": BrowserSkill,
}

def get_skill(name: str):
    """Return the skill class for *name* or raise ``KeyError``."""
    return SKILL_MAP[name]
