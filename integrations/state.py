"""
Integration state persistence for Polly.
Saves and loads integration connection states.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class IntegrationStateManager:
    """Manages persistent state for integrations."""
    
    def __init__(self, state_file: Optional[Path] = None):
        """
        Initialize state manager.
        
        Args:
            state_file: Path to state file (default: ~/.polly/integrations_state.json)
        """
        self.state_file = state_file or Path.home() / ".polly" / "integrations_state.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self._state = self._load_state()
    
    def _load_state(self) -> Dict[str, Any]:
        """Load state from file."""
        if not self.state_file.exists():
            return {}
        
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load integration state: {e}")
            return {}
    
    def _save_state(self):
        """Save state to file."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self._state, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save integration state: {e}")
    
    def save_connection(self, integration_name: str, connected: bool, config: Optional[Dict[str, Any]] = None):
        """
        Save integration connection state.
        
        Args:
            integration_name: Name of the integration
            connected: Whether it's connected
            config: Optional configuration to save
        """
        if integration_name not in self._state:
            self._state[integration_name] = {}
        
        self._state[integration_name]['connected'] = connected
        self._state[integration_name]['last_updated'] = datetime.utcnow().isoformat()
        
        if config:
            self._state[integration_name]['config'] = config
        
        self._save_state()
        logger.info(f"Saved state for {integration_name}: connected={connected}")
    
    def is_connected(self, integration_name: str) -> bool:
        """Check if an integration should be connected on startup."""
        return self._state.get(integration_name, {}).get('connected', False)
    
    def get_config(self, integration_name: str) -> Optional[Dict[str, Any]]:
        """Get saved configuration for an integration."""
        return self._state.get(integration_name, {}).get('config')
    
    def save_last_sync(self, integration_name: str, sync_time: datetime):
        """Save last sync time for an integration."""
        if integration_name not in self._state:
            self._state[integration_name] = {}
        
        self._state[integration_name]['last_sync'] = sync_time.isoformat()
        self._save_state()
    
    def get_last_sync(self, integration_name: str) -> Optional[datetime]:
        """Get last sync time for an integration."""
        sync_str = self._state.get(integration_name, {}).get('last_sync')
        if sync_str:
            try:
                return datetime.fromisoformat(sync_str)
            except Exception:
                return None
        return None
    
    def save_metadata(self, integration_name: str, metadata: Dict[str, Any]):
        """Save arbitrary metadata for an integration."""
        if integration_name not in self._state:
            self._state[integration_name] = {}
        
        if 'metadata' not in self._state[integration_name]:
            self._state[integration_name]['metadata'] = {}
        
        self._state[integration_name]['metadata'].update(metadata)
        self._save_state()
    
    def get_metadata(self, integration_name: str, key: str, default: Any = None) -> Any:
        """Get metadata value for an integration."""
        return self._state.get(integration_name, {}).get('metadata', {}).get(key, default)
    
    def remove_integration(self, integration_name: str):
        """Remove integration state."""
        if integration_name in self._state:
            del self._state[integration_name]
            self._save_state()
            logger.info(f"Removed state for {integration_name}")


# Global state manager instance
_state_manager: Optional[IntegrationStateManager] = None


def get_state_manager() -> IntegrationStateManager:
    """Get global state manager instance."""
    global _state_manager
    if _state_manager is None:
        _state_manager = IntegrationStateManager()
    return _state_manager
