"""
Shell Executor
Phase 23.5: Security Hardening

Wrapper for shell command execution that routes through capability broker.
Shell exec is disabled by default for personal use, but this provides
a secure path if enabled.
"""

from typing import Optional, Dict, Any
import logging
import subprocess
from pathlib import Path

from core.capability_broker import get_capability_broker
from core.capabilities.types import CapabilityType, CapabilityRequest
from core.audit_logger import get_audit_logger

logger = logging.getLogger(__name__)


class ShellExecutor:
    """
    Secure shell command executor.
    
    All shell commands must be approved through capability broker.
    Shell exec is disabled by default in security policy.
    """
    
    def __init__(self):
        self.broker = get_capability_broker()
        self.audit_logger = get_audit_logger()
    
    async def execute(
        self,
        command: str,
        requestor: str = "polly-core",
        cwd: Optional[Path] = None,
        timeout: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a shell command with capability broker approval.
        
        Args:
            command: Shell command to execute
            requestor: Who is requesting this command
            cwd: Working directory (optional)
            timeout: Command timeout in seconds (optional)
            metadata: Additional context
            
        Returns:
            Dict with:
            - status: "success" | "error" | "denied"
            - stdout: Command output
            - stderr: Error output
            - exit_code: Exit code
            
        Raises:
            PermissionError: If capability is denied
        """
        # Request capability
        response = self.broker.request_capability(
            capability_type=CapabilityType.SHELL_EXEC,
            requestor=requestor,
            resource=command,
            metadata={
                "cwd": str(cwd) if cwd else None,
                "timeout": timeout,
                **(metadata or {})
            }
        )
        
        # Log request
        self.audit_logger.log_capability_request(
            response.request,
            response
        )
        
        if not response.granted:
            if response.requires_approval:
                # Pending approval - raise error
                raise PermissionError(
                    f"Shell command execution requires approval: {command}. "
                    f"Approval ID: {response.approval_id}"
                )
            else:
                # Denied
                raise PermissionError(
                    f"Shell command execution denied: {command}. "
                    f"Reason: {response.reason}"
                )
        
        # Execute command
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                timeout=timeout,
                capture_output=True,
                text=True
            )
            
            # Log execution
            self.audit_logger.log_security_event(
                event_type="shell_exec",
                metadata={
                    "command": command,
                    "exit_code": result.returncode,
                    "requestor": requestor
                },
                requestor=requestor,
                resource=command
            )
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"Shell command timed out: {command}")
            raise TimeoutError(f"Command execution timed out: {command}")
        except Exception as e:
            logger.error(f"Shell command execution failed: {command} - {e}")
            raise


# Global shell executor instance
_shell_executor: Optional[ShellExecutor] = None


def get_shell_executor() -> ShellExecutor:
    """Get global shell executor instance."""
    global _shell_executor
    if _shell_executor is None:
        _shell_executor = ShellExecutor()
    return _shell_executor
