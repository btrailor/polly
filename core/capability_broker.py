"""
Capability Broker
Phase 23.5: Security Hardening

Central security boundary where all high-risk operations must request capabilities.
Implements the Capability Broker Pattern: LLM has no inherent power, must request explicitly.

Architecture:
    User/LLM Request
          ↓
    Capability Broker
      - Validates request
      - Checks policy
      - Logs to audit.db
      - Requires approval if needed
          ↓
    Approved Operation
"""

from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, timedelta
from pathlib import Path

from core.capabilities.types import (
    CapabilityType,
    CapabilityRequest,
    CapabilityGrant,
    CapabilityResponse
)
from core.security_policy import get_security_policy, SecurityPolicy

logger = logging.getLogger(__name__)


class CapabilityBroker:
    """
    Central broker for all capability requests.
    
    All high-risk operations (package install, shell exec, API calls) must
    route through this broker for approval.
    
    Features:
    - Policy validation (checks security_policy.yaml)
    - Grant management (temporary/permanent grants)
    - Audit logging (all requests logged)
    - Approval workflow (user approval for high-risk ops)
    """
    
    def __init__(self, security_policy: Optional[SecurityPolicy] = None):
        """
        Initialize capability broker.
        
        Args:
            security_policy: SecurityPolicy instance (defaults to global instance)
        """
        self.security_policy = security_policy or get_security_policy()
        
        # Grant storage (in-memory for now, will add file persistence)
        self.grants: Dict[str, CapabilityGrant] = {}
        
        # Pending approvals (waiting for user decision)
        self.pending_approvals: Dict[str, CapabilityRequest] = {}
        
        logger.info("CapabilityBroker initialized")
    
    def request_capability(
        self,
        capability_type: CapabilityType,
        requestor: str,
        resource: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CapabilityResponse:
        """
        Request a capability.
        
        This is the main entry point for all capability requests.
        The broker will:
        1. Validate the request against policy
        2. Check for existing grants
        3. Determine if approval is needed
        4. Return response (granted, denied, or pending approval)
        
        Args:
            capability_type: Type of capability requested
            requestor: Who is requesting (e.g., "professor-persona")
            resource: What resource (e.g., package name, command)
            metadata: Additional context
            
        Returns:
            CapabilityResponse with granted/denied/pending status
        """
        # Create request
        request = CapabilityRequest(
            capability_type=capability_type,
            requestor=requestor,
            resource=resource,
            metadata=metadata or {}
        )
        
        logger.info(f"Capability request: {capability_type.value} for {resource} by {requestor}")
        
        # Check if capability is enabled in policy
        if not self._is_capability_enabled(capability_type):
            logger.warning(f"Capability {capability_type.value} is disabled in policy")
            return CapabilityResponse(
                request=request,
                granted=False,
                reason=f"Capability {capability_type.value} is disabled in security policy"
            )
        
        # Check for existing grant
        existing_grant = self._find_grant(request)
        if existing_grant and not existing_grant.is_expired():
            logger.info(f"Using existing grant for {resource}")
            return CapabilityResponse(
                request=request,
                granted=True,
                grant=existing_grant,
                reason="Existing grant found"
            )
        
        # Check if approval is required
        requires_approval = self._requires_approval(capability_type, resource)
        
        if requires_approval:
            # Create pending approval
            approval_id = f"approval_{datetime.now().timestamp()}"
            self.pending_approvals[approval_id] = request
            
            logger.info(f"Approval required for {resource}, approval_id: {approval_id}")
            
            return CapabilityResponse(
                request=request,
                granted=False,
                requires_approval=True,
                approval_id=approval_id,
                reason="User approval required"
            )
        else:
            # Auto-grant based on policy
            grant = self._create_grant(request, granted_by="policy", permanent=False)
            self.grants[grant.grant_id] = grant
            
            logger.info(f"Auto-granted {resource} based on policy")
            
            return CapabilityResponse(
                request=request,
                granted=True,
                grant=grant,
                reason="Auto-granted by policy"
            )
    
    def grant_capability(
        self,
        approval_id: str,
        permanent: bool = False,
        expires_in_minutes: Optional[int] = None
    ) -> CapabilityGrant:
        """
        Grant a pending capability request.
        
        Called when user approves a capability request.
        
        Args:
            approval_id: ID of pending approval
            permanent: If True, add to allowlist (for package_install)
            expires_in_minutes: Expiration time (None = no expiration)
            
        Returns:
            CapabilityGrant object
            
        Raises:
            ValueError: If approval_id not found
        """
        if approval_id not in self.pending_approvals:
            raise ValueError(f"Approval ID not found: {approval_id}")
        
        request = self.pending_approvals.pop(approval_id)
        
        # Calculate expiration
        expires_at = None
        if expires_in_minutes:
            expires_at = datetime.now() + timedelta(minutes=expires_in_minutes)
        
        # Create grant
        grant = self._create_grant(
            request,
            granted_by="user",
            permanent=permanent,
            expires_at=expires_at
        )
        
        self.grants[grant.grant_id] = grant
        
        logger.info(f"Granted capability: {request.resource} (permanent: {permanent})")
        
        return grant
    
    def deny_capability(self, approval_id: str, reason: Optional[str] = None) -> None:
        """
        Deny a pending capability request.
        
        Called when user denies a capability request.
        
        Args:
            approval_id: ID of pending approval
            reason: Optional reason for denial
        """
        if approval_id not in self.pending_approvals:
            raise ValueError(f"Approval ID not found: {approval_id}")
        
        request = self.pending_approvals.pop(approval_id)
        
        logger.info(f"Denied capability: {request.resource} (reason: {reason})")
    
    def revoke_grant(self, grant_id: str) -> None:
        """
        Revoke an existing grant.
        
        Args:
            grant_id: ID of grant to revoke
        """
        if grant_id in self.grants:
            del self.grants[grant_id]
            logger.info(f"Revoked grant: {grant_id}")
        else:
            logger.warning(f"Grant not found: {grant_id}")
    
    def check_grant(
        self,
        capability_type: CapabilityType,
        resource: str
    ) -> Optional[CapabilityGrant]:
        """
        Check if a capability is granted.
        
        Args:
            capability_type: Type of capability
            resource: Resource name
            
        Returns:
            CapabilityGrant if found and not expired, None otherwise
        """
        for grant in self.grants.values():
            if (grant.request.capability_type == capability_type and
                grant.request.resource == resource and
                not grant.is_expired()):
                return grant
        return None
    
    # ===== Internal Methods =====
    
    def _is_capability_enabled(self, capability_type: CapabilityType) -> bool:
        """Check if capability is enabled in security policy."""
        try:
            if capability_type == CapabilityType.PACKAGE_INSTALL:
                return self.security_policy.get_package_install_config().get("enabled", True)
            elif capability_type == CapabilityType.SHELL_EXEC:
                return self.security_policy.get_shell_exec_config().get("enabled", False)
            elif capability_type == CapabilityType.API_CALL:
                return self.security_policy.get_api_call_config().get("enabled", True)
            return False
        except Exception as e:
            logger.error(f"Error checking capability enabled: {e}")
            return False
    
    def _requires_approval(self, capability_type: CapabilityType, resource: str) -> bool:
        """Check if capability requires user approval."""
        try:
            if capability_type == CapabilityType.PACKAGE_INSTALL:
                config = self.security_policy.get_package_install_config()
                return config.get("require_approval", True)
            elif capability_type == CapabilityType.SHELL_EXEC:
                config = self.security_policy.get_shell_exec_config()
                return config.get("require_approval", True)
            elif capability_type == CapabilityType.API_CALL:
                # API calls don't require approval, just rate limiting
                return False
            return True  # Default to requiring approval
        except Exception as e:
            logger.error(f"Error checking approval requirement: {e}")
            return True  # Default to requiring approval
    
    def _find_grant(self, request: CapabilityRequest) -> Optional[CapabilityGrant]:
        """Find existing grant for request."""
        for grant in self.grants.values():
            if (grant.request.capability_type == request.capability_type and
                grant.request.resource == request.resource and
                not grant.is_expired()):
                return grant
        return None
    
    def _create_grant(
        self,
        request: CapabilityRequest,
        granted_by: str = "user",
        permanent: bool = False,
        expires_at: Optional[datetime] = None
    ) -> CapabilityGrant:
        """Create a new grant."""
        return CapabilityGrant(
            request=request,
            granted_by=granted_by,
            permanent=permanent,
            expires_at=expires_at
        )
    
    def get_pending_approvals(self) -> List[CapabilityRequest]:
        """Get all pending approval requests."""
        return list(self.pending_approvals.values())
    
    def get_approval(self, approval_id: str) -> Optional[CapabilityRequest]:
        """Get a specific pending approval."""
        return self.pending_approvals.get(approval_id)


# Global capability broker instance
_capability_broker: Optional[CapabilityBroker] = None


def get_capability_broker() -> CapabilityBroker:
    """Get global capability broker instance."""
    global _capability_broker
    if _capability_broker is None:
        _capability_broker = CapabilityBroker()
    return _capability_broker
