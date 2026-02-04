"""
Base classes for Polly integrations
Defines the interface for all external service integrations
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class IntegrationStatus(Enum):
    """Status of an integration."""
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    ERROR = "error"
    SYNCING = "syncing"


class IntegrationError(Exception):
    """Base exception for integration errors."""
    pass


class Integration(ABC):
    """
    Base class for all integrations.
    
    Each integration must implement:
    - Authentication/connection logic
    - Data fetching
    - Data formatting for RAG indexing
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.status = IntegrationStatus.DISCONNECTED
        self.last_sync: Optional[datetime] = None
        self.error_message: Optional[str] = None
        
    @abstractmethod
    async def connect(self, credentials: Dict[str, str]) -> bool:
        """
        Connect to the integration service.
        
        Args:
            credentials: Dict with service-specific auth credentials
                        e.g., {"token": "..."} or {"api_key": "..."}
        
        Returns:
            True if connection successful
        
        Raises:
            IntegrationError: If connection fails
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Disconnect from the integration service.
        
        Returns:
            True if disconnection successful
        """
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """
        Test if the connection is still valid.
        
        Returns:
            True if connection is valid
        """
        pass
    
    @abstractmethod
    async def fetch_data(self, **kwargs) -> Dict[str, Any]:
        """
        Fetch data from the integration.
        
        Returns:
            Dict with fetched data, format:
            {
                "items": [...],
                "metadata": {...}
            }
        """
        pass
    
    @abstractmethod
    def format_for_rag(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format fetched data for RAG indexing.
        
        Args:
            data: Raw data from fetch_data()
        
        Returns:
            List of documents with format:
            [
                {
                    "content": "text to index",
                    "metadata": {
                        "source": "integration_name",
                        "type": "document_type",
                        "id": "unique_id",
                        "url": "source_url",
                        "created_at": "timestamp",
                        ...
                    }
                },
                ...
            ]
        """
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get current integration status."""
        return {
            "name": self.name,
            "status": self.status.value,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "error": self.error_message
        }
    
    def _set_status(self, status: IntegrationStatus, error: Optional[str] = None):
        """Update integration status."""
        self.status = status
        self.error_message = error
        logger.info(f"{self.name} status: {status.value}")


class IntegrationManager:
    """
    Manages all integrations and coordinates data syncing.
    """
    
    def __init__(self):
        self.integrations: Dict[str, Integration] = {}
        self._credentials: Dict[str, Dict[str, str]] = {}
        
        # Initialize state manager
        from .state import get_state_manager
        self.state_manager = get_state_manager()
        
        # Will restore connections after integrations are registered
        self._pending_restore = True
        
    def register_integration(self, integration: Integration):
        """Register a new integration."""
        self.integrations[integration.name] = integration
        logger.info(f"Registered integration: {integration.name}")
    
    async def restore_connections(self):
        """Restore previously connected integrations from saved state."""
        if not self._pending_restore:
            return
        
        self._pending_restore = False
        
        for name, integration in self.integrations.items():
            if self.state_manager.is_connected(name):
                try:
                    logger.info(f"Restoring connection for {name}")
                    # Try to reconnect with empty credentials (for integrations that don't need them)
                    await integration.connect({})
                    
                    # Restore last sync time
                    last_sync = self.state_manager.get_last_sync(name)
                    if last_sync:
                        integration.last_sync = last_sync
                    
                    logger.info(f"Restored connection for {name}")
                except Exception as e:
                    logger.warning(f"Failed to restore connection for {name}: {e}")
                    self.state_manager.save_connection(name, False)
    
    def get_integration(self, name: str) -> Optional[Integration]:
        """Get integration by name."""
        return self.integrations.get(name)
    
    async def connect_integration(
        self,
        name: str,
        credentials: Dict[str, str]
    ) -> bool:
        """
        Connect an integration.
        
        Args:
            name: Integration name
            credentials: Auth credentials for the integration
        
        Returns:
            True if connection successful
        """
        integration = self.get_integration(name)
        if not integration:
            raise IntegrationError(f"Integration not found: {name}")
        
        try:
            success = await integration.connect(credentials)
            if success:
                self._credentials[name] = credentials
                # Save connection state
                self.state_manager.save_connection(name, True, integration.config)
            return success
        except Exception as e:
            logger.error(f"Failed to connect {name}: {e}")
            integration._set_status(IntegrationStatus.ERROR, str(e))
            raise IntegrationError(f"Connection failed: {e}")
    
    async def disconnect_integration(self, name: str) -> bool:
        """Disconnect an integration."""
        integration = self.get_integration(name)
        if not integration:
            raise IntegrationError(f"Integration not found: {name}")
        
        success = await integration.disconnect()
        if success:
            if name in self._credentials:
                del self._credentials[name]
            # Save disconnected state
            self.state_manager.save_connection(name, False)
        return success
    
    async def sync_integration(self, name: str, **fetch_kwargs) -> Dict[str, Any]:
        """
        Sync data from an integration.
        
        Args:
            name: Integration name
            **fetch_kwargs: Arguments to pass to fetch_data()
        
        Returns:
            Dict with sync results:
            {
                "success": True,
                "documents": [...],
                "count": 123,
                "metadata": {...}
            }
        """
        integration = self.get_integration(name)
        if not integration:
            raise IntegrationError(f"Integration not found: {name}")
        
        if integration.status != IntegrationStatus.CONNECTED:
            raise IntegrationError(f"Integration not connected: {name}")
        
        try:
            integration._set_status(IntegrationStatus.SYNCING)
            
            # Fetch data
            data = await integration.fetch_data(**fetch_kwargs)
            
            # Format for RAG
            documents = integration.format_for_rag(data)
            
            # Update status
            integration.last_sync = datetime.now()
            integration._set_status(IntegrationStatus.CONNECTED)
            
            # Save last sync time
            self.state_manager.save_last_sync(name, integration.last_sync)
            
            return {
                "success": True,
                "documents": documents,
                "count": len(documents),
                "metadata": data.get("metadata", {})
            }
            
        except Exception as e:
            logger.error(f"Sync failed for {name}: {e}")
            integration._set_status(IntegrationStatus.ERROR, str(e))
            raise IntegrationError(f"Sync failed: {e}")
    
    def get_all_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all integrations."""
        return {
            name: integration.get_status()
            for name, integration in self.integrations.items()
        }
    
    def get_connected_integrations(self) -> List[str]:
        """Get list of connected integration names."""
        return [
            name
            for name, integration in self.integrations.items()
            if integration.status == IntegrationStatus.CONNECTED
        ]
