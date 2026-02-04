"""
Pyodide Sandbox
Phase 23.5: Security Hardening

Sandboxed Python code execution using Pyodide (WebAssembly).
Code execution happens in the Electron renderer process, not on the server.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Execution result status."""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class ExecutionResult:
    """Result of code execution in Pyodide sandbox."""
    status: ExecutionStatus
    output: str = ""
    error: Optional[str] = None
    execution_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "execution_time": round(self.execution_time, 3)
        }


class PyodideSandbox:
    """
    Pyodide Sandbox for secure Python code execution.
    
    Note: Actual execution happens in the Electron renderer process.
    This class provides the interface and validation for sandboxed execution.
    
    Security Features:
    - Code runs in WebAssembly (Pyodide) in browser security model
    - No network access by default
    - No filesystem access by default
    - Timeout protection
    - Memory limits
    - Isolated from host system
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Pyodide sandbox.
        
        Args:
            config: Sandbox configuration from security policy
        """
        if config is None:
            from core.security_policy import get_security_policy
            security_policy = get_security_policy()
            config = security_policy.get("sandbox", {})
        
        self.timeout_seconds = config.get("timeout_seconds", 10)
        self.memory_limit_mb = config.get("memory_limit_mb", 512)
        self.network_access = config.get("network_access", False)
        self.filesystem_access = config.get("filesystem_access", False)
        
        logger.info(f"PyodideSandbox initialized: timeout={self.timeout_seconds}s, memory={self.memory_limit_mb}MB")
    
    def validate_code(self, code: str) -> tuple[bool, Optional[str]]:
        """
        Validate code before execution.
        
        Checks for:
        - Empty code
        - Suspicious patterns (future: injection attempts)
        - Code length limits
        
        Args:
            code: Python code to validate
            
        Returns:
            (is_valid, error_message)
        """
        if not code or not code.strip():
            return False, "Code is empty"
        
        # Check code length (prevent DoS)
        max_code_length = 100_000  # 100KB limit
        if len(code) > max_code_length:
            return False, f"Code too long (max {max_code_length} characters)"
        
        # Future: Add more validation (import restrictions, etc.)
        
        return True, None
    
    async def execute(self, code: str, timeout: Optional[int] = None) -> ExecutionResult:
        """
        Execute Python code in Pyodide sandbox.
        
        Note: This method validates and prepares the execution request.
        Actual execution happens in the Electron renderer process.
        
        Args:
            code: Python code to execute
            timeout: Execution timeout in seconds (overrides config default)
            
        Returns:
            ExecutionResult with status, output, and error
        """
        # Validate code
        is_valid, error_msg = self.validate_code(code)
        if not is_valid:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                error=error_msg or "Code validation failed"
            )
        
        # Use provided timeout or default
        timeout = timeout or self.timeout_seconds
        
        # Log execution request (for audit)
        logger.info(f"Pyodide execution request: code_length={len(code)}, timeout={timeout}s")
        
        # Note: Actual execution happens in Electron renderer
        # This method is called from the server endpoint, which then
        # communicates with the Electron renderer to execute the code.
        # The renderer returns the result, which we convert to ExecutionResult.
        
        # For now, return a placeholder that indicates execution should happen in renderer
        # The actual implementation will be in the server endpoint that communicates with Electron
        return ExecutionResult(
            status=ExecutionStatus.ERROR,
            error="Execution must be handled by Electron renderer process"
        )
    
    def get_sandbox_info(self) -> Dict[str, Any]:
        """Get information about the sandbox configuration."""
        return {
            "type": "pyodide",
            "timeout_seconds": self.timeout_seconds,
            "memory_limit_mb": self.memory_limit_mb,
            "network_access": self.network_access,
            "filesystem_access": self.filesystem_access,
            "isolation": "WebAssembly (browser security model)"
        }
