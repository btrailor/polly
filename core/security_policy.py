"""
Security Policy Loader
Phase 23.5: Security Hardening

Loads and validates security policy configuration from config/security_policy.yaml
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml
import logging
import re

logger = logging.getLogger(__name__)


class SecurityPolicy:
    """Security policy configuration manager."""
    
    DEFAULT_POLICY = {
        "security_mode": "personal",
        "capabilities": {
            "package_install": {
                "enabled": True,
                "allowlist_path": "config/approved_packages.yaml",
                "require_approval": True,
                "show_pypi_metadata": True,
                "show_context7_info": True,
                "min_context7_trust": 7,
                "block_on_deny": False
            },
            "shell_exec": {
                "enabled": False,
                "allowed_commands": [],
                "require_approval": True
            },
            "api_call": {
                "enabled": True,
                "rate_limit_per_minute": 60,
                "log_all_requests": True
            }
        },
        "sandbox": {
            "type": "pyodide",
            "timeout_seconds": 10,
            "memory_limit_mb": 512,
            "network_access": False,
            "filesystem_access": False
        },
        "content_security": {
            "scan_for_prompt_injection": True,
            "prompt_injection_sensitivity": "medium",
            "warn_on_suspicious_content": True,
            "block_suspicious_content": False,
            "pii_detection": {
                "enabled": True,
                "warn_only": True,
                "patterns": ["email", "phone", "ssn", "credit_card", "api_key"],
                "user_can_disable": True
            }
        },
        "api_keys": {
            "use_secure_context_manager": True,
            "auto_cleanup_memory": True,
            "rotation_reminder_days": 90
        },
        "audit": {
            "enabled": True,
            "database_path": "~/.polly/audit.db",
            "retention_days": 90,
            "log_events": [
                "capability_request",
                "capability_grant",
                "capability_deny",
                "package_install_request",
                "package_install_approved",
                "package_install_denied",
                "code_execution",
                "api_call",
                "pii_detected",
                "suspicious_content_detected"
            ]
        },
        "cors": {
            "allowed_origins": [
                "http://localhost:*",
                "http://127.0.0.1:*",
                "http://100.64.0.0/10"
            ],
            "allow_credentials": True
        }
    }
    
    def __init__(self, policy_path: Optional[Path] = None):
        """Initialize security policy from file."""
        self.policy_path = policy_path or self._find_policy_file()
        self._policy = self._load_policy()
    
    def _find_policy_file(self) -> Path:
        """Find security policy file in standard locations."""
        locations = [
            Path.cwd() / "config" / "security_policy.yaml",
            Path(__file__).parent.parent / "config" / "security_policy.yaml",
            Path.home() / ".polly" / "security_policy.yaml"
        ]
        
        for loc in locations:
            if loc.exists():
                return loc
        
        # Return default location even if doesn't exist
        return Path(__file__).parent.parent / "config" / "security_policy.yaml"
    
    def _load_policy(self) -> Dict[str, Any]:
        """Load policy from file, merge with defaults."""
        policy = self.DEFAULT_POLICY.copy()
        
        if self.policy_path and self.policy_path.exists():
            try:
                with open(self.policy_path) as f:
                    user_policy = yaml.safe_load(f) or {}
                policy = self._deep_merge(policy, user_policy)
                logger.info(f"Loaded security policy from {self.policy_path}")
            except yaml.YAMLError as e:
                logger.error(f"YAML parse error in security policy: {e}. Using defaults.")
            except Exception as e:
                logger.warning(f"Failed to load security policy: {e}. Using defaults.")
        else:
            # Policy file doesn't exist - this is OK, we'll use defaults
            logger.debug(f"Security policy file not found at {self.policy_path}. Using defaults.")
        
        # Expand paths (e.g., ~/.polly/audit.db)
        try:
            policy = self._expand_paths(policy)
        except Exception as e:
            logger.warning(f"Error expanding paths in security policy: {e}")
        
        # Validate policy
        try:
            self._validate_policy(policy)
        except Exception as e:
            logger.warning(f"Error validating security policy: {e}. Continuing with defaults.")
        
        return policy
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _expand_paths(self, policy: Any) -> Any:
        """Recursively expand ~ in paths."""
        if isinstance(policy, dict):
            return {k: self._expand_paths(v) for k, v in policy.items()}
        elif isinstance(policy, list):
            return [self._expand_paths(v) for v in policy]
        elif isinstance(policy, str) and policy.startswith("~"):
            return str(Path(policy).expanduser())
        return policy
    
    def _validate_policy(self, policy: Dict[str, Any]) -> None:
        """Validate policy structure and values."""
        # Validate security_mode
        if policy.get("security_mode") not in ["personal", "team", "public"]:
            logger.warning(f"Invalid security_mode: {policy.get('security_mode')}. Using 'personal'.")
            policy["security_mode"] = "personal"
        
        # Validate CORS origins format
        cors_origins = policy.get("cors", {}).get("allowed_origins", [])
        for origin in cors_origins:
            if not self._is_valid_origin(origin):
                logger.warning(f"Invalid CORS origin format: {origin}")
    
    def _is_valid_origin(self, origin: str) -> bool:
        """Validate CORS origin format."""
        # Allow wildcard ports: http://localhost:*
        if origin.endswith(":*"):
            base = origin[:-2]
            return base.startswith("http://") or base.startswith("https://")
        
        # Allow CIDR notation: http://100.64.0.0/10
        if "/" in origin:
            parts = origin.split("/")
            if len(parts) == 2:
                base = parts[0]
                try:
                    int(parts[1])  # CIDR prefix length
                    return base.startswith("http://") or base.startswith("https://")
                except ValueError:
                    return False
        
        # Standard origin: http://example.com:3000
        return origin.startswith("http://") or origin.startswith("https://")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get policy value by dot-notation key (e.g., 'cors.allowed_origins')."""
        keys = key.split(".")
        value = self._policy
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS allowed origins, expanding wildcards and CIDR ranges."""
        origins = self.get("cors.allowed_origins", [])
        expanded = []
        
        for origin in origins:
            # Handle wildcard ports: http://localhost:* -> http://localhost:*
            if origin.endswith(":*"):
                expanded.append(origin)
            # Handle CIDR ranges: http://100.64.0.0/10 -> keep as is (FastAPI will handle)
            elif "/" in origin:
                expanded.append(origin)
            # Standard origin
            else:
                expanded.append(origin)
        
        return expanded
    
    def get_cors_config(self) -> Dict[str, Any]:
        """Get CORS configuration for FastAPI middleware."""
        origins = self.get_cors_origins()
        
        # FastAPI CORSMiddleware doesn't support wildcard ports directly
        # We'll need to handle this in a custom middleware or expand the list
        # For now, return the origins and let the middleware handle validation
        
        return {
            "allow_origins": origins,
            "allow_credentials": self.get("cors.allow_credentials", True),
            "allow_methods": ["*"],  # Can be restricted later if needed
            "allow_headers": ["*"]   # Can be restricted later if needed
        }
    
    @property
    def policy(self) -> Dict[str, Any]:
        """Get full policy dictionary."""
        return self._policy


# Global security policy instance
_security_policy: Optional[SecurityPolicy] = None


def get_security_policy() -> SecurityPolicy:
    """Get global security policy instance."""
    global _security_policy
    if _security_policy is None:
        _security_policy = SecurityPolicy()
    return _security_policy


def load_security_policy(policy_path: Optional[Path] = None) -> SecurityPolicy:
    """Load security policy from specific path."""
    global _security_policy
    _security_policy = SecurityPolicy(policy_path)
    return _security_policy
