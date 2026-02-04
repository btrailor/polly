"""
Skill System Package (Phase 16c)

On-demand knowledge packages for personas.
"""

from .base import Skill, SkillMetadata
from .manager import SkillManager

__all__ = ['Skill', 'SkillMetadata', 'SkillManager']
