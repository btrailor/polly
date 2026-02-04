"""
Polly Integrations
External service integrations for enhanced capabilities
"""

from .base import Integration, IntegrationManager, IntegrationError
from .github import GitHubIntegration
from .context7 import Context7Integration
from .calendar import CalendarIntegration
from .reminders import RemindersIntegration
from .obsidian import ObsidianIntegration
from .state import IntegrationStateManager, get_state_manager

__all__ = [
    'Integration',
    'IntegrationManager',
    'IntegrationError',
    'GitHubIntegration',
    'Context7Integration',
    'CalendarIntegration',
    'RemindersIntegration',
    'ObsidianIntegration',
    'IntegrationStateManager',
    'get_state_manager'
]
