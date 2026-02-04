"""
Capability Types
Phase 23.5: Security Hardening

Defines the types of capabilities that can be requested through the Capability Broker.
All high-risk operations must request capabilities explicitly.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime


class CapabilityType(Enum):
    """
    Types of capabilities that can be requested.
    
    HIGH RISK:
    - PACKAGE_INSTALL: Installing Python packages (always require approval)
    - SHELL_EXEC: Executing shell commands (disabled by default)
    
    MEDIUM RISK:
    - API_CALL: Making external API calls (for rate limiting, not blocking)
    
    NOT INCLUDED (handled elsewhere):
    - FILE_WRITE: Permissive (trusted operation for vault/notes)
    - CODE_EXEC: Handled by Pyodide sandbox (inherently safe)
    """
    PACKAGE_INSTALL = "package_install"
    SHELL_EXEC = "shell_exec"
    API_CALL = "api_call"


@dataclass
class CapabilityRequest:
    """
    Request for a capability.
    
    All high-risk operations must create a CapabilityRequest and route it
    through the CapabilityBroker for approval.
    """
    capability_type: CapabilityType
    requestor: str  # e.g., "polly-core", "professor-persona", "curriculum-manager"
    resource: str  # e.g., package name, command, API endpoint
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional context
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "capability_type": self.capability_type.value,
            "requestor": self.requestor,
            "resource": self.resource,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CapabilityRequest':
        """Create from dictionary."""
        return cls(
            capability_type=CapabilityType(data["capability_type"]),
            requestor=data["requestor"],
            resource=data["resource"],
            metadata=data.get("metadata", {}),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat()))
        )


@dataclass
class CapabilityGrant:
    """
    Grant of a capability.
    
    Represents an approved capability request. Grants can be:
    - Temporary (expire after use or time limit)
    - Permanent (added to allowlist)
    - Revocable (can be revoked later)
    """
    request: CapabilityRequest
    granted_at: datetime = field(default_factory=datetime.now)
    granted_by: str = "user"  # "user" | "auto" | "policy"
    expires_at: Optional[datetime] = None
    permanent: bool = False  # If True, added to allowlist
    grant_id: str = field(default_factory=lambda: f"grant_{datetime.now().timestamp()}")
    
    def is_expired(self) -> bool:
        """Check if grant has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "grant_id": self.grant_id,
            "request": self.request.to_dict(),
            "granted_at": self.granted_at.isoformat(),
            "granted_by": self.granted_by,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "permanent": self.permanent
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CapabilityGrant':
        """Create from dictionary."""
        request = CapabilityRequest.from_dict(data["request"])
        return cls(
            request=request,
            granted_at=datetime.fromisoformat(data.get("granted_at", datetime.now().isoformat())),
            granted_by=data.get("granted_by", "user"),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            permanent=data.get("permanent", False),
            grant_id=data.get("grant_id", f"grant_{datetime.now().timestamp()}")
        )


@dataclass
class CapabilityResponse:
    """
    Response to a capability request.
    
    Contains the result of a capability request: granted, denied, or pending approval.
    """
    request: CapabilityRequest
    granted: bool
    grant: Optional[CapabilityGrant] = None
    reason: Optional[str] = None  # Why granted/denied
    requires_approval: bool = False  # If True, user approval needed
    approval_id: Optional[str] = None  # ID for pending approval
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "request": self.request.to_dict(),
            "granted": self.granted,
            "grant": self.grant.to_dict() if self.grant else None,
            "reason": self.reason,
            "requires_approval": self.requires_approval,
            "approval_id": self.approval_id
        }
