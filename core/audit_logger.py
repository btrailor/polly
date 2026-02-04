"""
Audit Logger
Phase 23.5: Security Hardening

Logs all security-relevant events to SQLite database for audit trail.
All capability requests, grants, denials, and security events are logged.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import json
import logging

from core.capabilities.types import CapabilityRequest, CapabilityGrant, CapabilityResponse
from core.security_policy import get_security_policy

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Audit logger for security events.
    
    Logs all capability requests, grants, denials, and security events
    to a SQLite database for audit trail.
    
    Database schema:
    - events: All security events
      - id: INTEGER PRIMARY KEY
      - event_type: TEXT (capability_request, capability_grant, etc.)
      - timestamp: TEXT (ISO format)
      - requestor: TEXT
      - resource: TEXT
      - capability_type: TEXT
      - granted: INTEGER (0 or 1)
      - reason: TEXT
      - metadata: TEXT (JSON)
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize audit logger.
        
        Args:
            db_path: Path to audit database (defaults to ~/.polly/audit.db)
        """
        if db_path is None:
            # Get from security policy
            security_policy = get_security_policy()
            db_path_str = security_policy.get("audit.database_path", "~/.polly/audit.db")
            db_path = Path(db_path_str).expanduser()
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        logger.info(f"AuditLogger initialized: {self.db_path}")
    
    def _init_database(self) -> None:
        """Initialize audit database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    requestor TEXT,
                    resource TEXT,
                    capability_type TEXT,
                    granted INTEGER DEFAULT 0,
                    reason TEXT,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for common queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_event_type 
                ON events(event_type)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON events(timestamp)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_capability_type 
                ON events(capability_type)
            """)
            
            conn.commit()
    
    def log_capability_request(
        self,
        request: CapabilityRequest,
        response: CapabilityResponse
    ) -> None:
        """
        Log a capability request and response.
        
        Args:
            request: CapabilityRequest object
            response: CapabilityResponse object
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO events (
                        event_type, timestamp, requestor, resource,
                        capability_type, granted, reason, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    "capability_request",
                    request.timestamp.isoformat(),
                    request.requestor,
                    request.resource,
                    request.capability_type.value,
                    1 if response.granted else 0,
                    response.reason,
                    json.dumps({
                        "request": request.to_dict(),
                        "response": response.to_dict(),
                        "requires_approval": response.requires_approval,
                        "approval_id": response.approval_id
                    })
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error logging capability request: {e}", exc_info=True)
    
    def log_capability_grant(
        self,
        grant: CapabilityGrant,
        approval_id: Optional[str] = None
    ) -> None:
        """
        Log a capability grant.
        
        Args:
            grant: CapabilityGrant object
            approval_id: Optional approval ID if from pending approval
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO events (
                        event_type, timestamp, requestor, resource,
                        capability_type, granted, reason, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    "capability_grant",
                    grant.granted_at.isoformat(),
                    grant.request.requestor,
                    grant.request.resource,
                    grant.request.capability_type.value,
                    1,
                    f"Granted by {grant.granted_by}",
                    json.dumps({
                        "grant_id": grant.grant_id,
                        "permanent": grant.permanent,
                        "expires_at": grant.expires_at.isoformat() if grant.expires_at else None,
                        "approval_id": approval_id
                    })
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error logging capability grant: {e}", exc_info=True)
    
    def log_capability_denial(
        self,
        request: CapabilityRequest,
        reason: str,
        approval_id: Optional[str] = None
    ) -> None:
        """
        Log a capability denial.
        
        Args:
            request: CapabilityRequest object
            reason: Reason for denial
            approval_id: Optional approval ID if from pending approval
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO events (
                        event_type, timestamp, requestor, resource,
                        capability_type, granted, reason, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    "capability_deny",
                    datetime.now().isoformat(),
                    request.requestor,
                    request.resource,
                    request.capability_type.value,
                    0,
                    reason,
                    json.dumps({
                        "request": request.to_dict(),
                        "approval_id": approval_id
                    })
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error logging capability denial: {e}", exc_info=True)
    
    def log_security_event(
        self,
        event_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        requestor: Optional[str] = None,
        resource: Optional[str] = None
    ) -> None:
        """
        Log a general security event.
        
        Args:
            event_type: Type of event (e.g., "pii_detected", "suspicious_content")
            metadata: Additional event data
            requestor: Who triggered the event
            resource: What resource was involved
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO events (
                        event_type, timestamp, requestor, resource,
                        metadata
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    event_type,
                    datetime.now().isoformat(),
                    requestor,
                    resource,
                    json.dumps(metadata or {})
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error logging security event: {e}", exc_info=True)
    
    def get_events(
        self,
        event_type: Optional[str] = None,
        capability_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query audit events.
        
        Args:
            event_type: Filter by event type
            capability_type: Filter by capability type
            start_date: Start date for query
            end_date: End date for query
            limit: Maximum number of results
            
        Returns:
            List of event dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                query = "SELECT * FROM events WHERE 1=1"
                params = []
                
                if event_type:
                    query += " AND event_type = ?"
                    params.append(event_type)
                
                if capability_type:
                    query += " AND capability_type = ?"
                    params.append(capability_type)
                
                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date.isoformat())
                
                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date.isoformat())
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                events = []
                for row in rows:
                    event = dict(row)
                    # Parse metadata JSON
                    if event.get("metadata"):
                        try:
                            event["metadata"] = json.loads(event["metadata"])
                        except json.JSONDecodeError:
                            pass
                    events.append(event)
                
                return events
        except Exception as e:
            logger.error(f"Error querying audit events: {e}", exc_info=True)
            return []
    
    def cleanup_old_events(self, retention_days: Optional[int] = None) -> int:
        """
        Delete events older than retention period.
        
        Args:
            retention_days: Retention period in days (defaults to policy setting)
            
        Returns:
            Number of events deleted
        """
        if retention_days is None:
            security_policy = get_security_policy()
            retention_days = security_policy.get("audit.retention_days", 90)
        
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    DELETE FROM events 
                    WHERE timestamp < ?
                """, (cutoff_date.isoformat(),))
                deleted = cursor.rowcount
                conn.commit()
                logger.info(f"Cleaned up {deleted} old audit events (older than {retention_days} days)")
                return deleted
        except Exception as e:
            logger.error(f"Error cleaning up old events: {e}", exc_info=True)
            return 0


# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get global audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger
