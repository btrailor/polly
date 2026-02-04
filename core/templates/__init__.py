"""
Template system for Polly note generation.

This module provides template management for AI-powered note creation,
allowing users to define note structures and AI generation hints via
markdown templates with YAML frontmatter.
"""

from .template import Template
from .manager import TemplateManager

__all__ = ['Template', 'TemplateManager']
