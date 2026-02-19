"""
Polly Configuration Loader
Handles YAML config with sensible defaults
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
import os


class PollyConfig:
    """Configuration manager for Polly."""

    DEFAULT_CONFIG = {
        "user": {"name": "User"},
        "knowledge_base": {
            "path": "~/.polly"  # Base directory for all knowledge (notes, conversations, attachments)
        },
        "models": {
            "local": {
                "host": "http://localhost:11434",
                "embedding_model": "nomic-embed-text",
                "chat_models": {
                    "fast": "llama3.2:3b",
                    "balanced": "llama3.1:7b",
                    "quality": "llama3.1:70b"
                },
                "default": "balanced"
            },
            "cloud": {
                "provider": "anthropic",
                "api_key_env": "ANTHROPIC_API_KEY",
                "models": {
                    "default": "claude-sonnet-4-20250514",
                    "quality": "claude-opus-4-20250514",
                    "fast": "claude-haiku"
                }
            }
        },
        "rag": {
            "vector_db_path": "~/.polly/chroma_db",
            "chunk_size": 800,
            "chunk_overlap": 100,
            "n_results": 5
        },
        "server": {
            "host": "0.0.0.0",
            "port": 11436
        },
        "router": {
            "default_mode": "auto",
            "allow_override": True
        },
        "compression": {
            "enabled": True,
            "message_threshold": 20,      # Compress after 20 messages (10 exchanges)
            "age_hours": 24,               # Or after 24 hours
            "keep_recent": 10,             # Keep last 10 messages uncompressed
            "show_stats": False            # Hide compression stats by default
        },
        "memory": {
            "provider": "mem0",
            "extraction": {
                "enabled": True,
                "cloud_threshold": "balanced",
                "cloud_model": "claude-haiku",
                "local_model": "llama3.2:latest",
                "max_cloud_cost": 0.02,
            },
            "tiers": {
                "stable": {"collection": "memory_stable", "decay": None},
                "episodic": {"collection": "memory_episodic", "decay_halflife_days": 90},
                "working": {"collection": "memory_working", "session_scoped": True},
            },
            "retrieval": {
                "stable_limit": 5,
                "episodic_limit": 5,
                "working_include_all": True,
                "min_similarity": 0.4,
                "dedup_threshold": 0.92,
            },
        },
        "context_budget": {
            "response_reserve": 2000,
            "model_context_windows": {
                "gpt-4": 128000,
                "gpt-4o": 128000,
                "claude-sonnet": 200000,
                "claude-haiku": 200000,
                "llama3.2": 131072,
                "default": 8192,
            },
            "sections": {
                "system_prompt": {"min": 500, "max": 2000, "target_pct": 0.10, "priority": 1},
                "conversation": {"min": 1000, "max": 8000, "target_pct": 0.25, "priority": 2},
                "memory": {"min": 500, "max": 4000, "target_pct": 0.20, "priority": 3},
                "rag": {"min": 1000, "max": 6000, "target_pct": 0.30, "priority": 4},
                "mental_models": {"min": 200, "max": 2000, "target_pct": 0.10, "priority": 5},
                "entities": {"min": 100, "max": 1000, "target_pct": 0.05, "priority": 6},
            },
            "relevance_weights": {
                "retrieval_similarity": 0.35,
                "recency": 0.25,
                "reference_frequency": 0.15,
                "domain_affinity": 0.15,
                "tier_weight": 0.10,
            },
            "rolling": {
                "decay_per_turn": 0.85,
                "eviction_turns": 5,
                "amplification_reset": True,
            },
        },
        "routing_v2": {
            "enabled": True,               # Multi-provider intelligent routing (recommended)
        }
    }

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self._find_config()
        self._config = self._load_config()

    def _find_config(self) -> Path:
        """Find config file in standard locations."""
        locations = [
            Path.cwd() / "config" / "config.yaml",
            Path.home() / ".polly" / "config.yaml",
            Path(__file__).parent.parent / "config" / "config.yaml"
        ]

        for loc in locations:
            if loc.exists():
                return loc

        # Return default location even if doesn't exist
        return Path.home() / ".polly" / "config.yaml"

    def _load_config(self) -> Dict[str, Any]:
        """Load config from file, merge with defaults."""
        config = self.DEFAULT_CONFIG.copy()

        if self.config_path and self.config_path.exists():
            with open(self.config_path) as f:
                user_config = yaml.safe_load(f) or {}
            config = self._deep_merge(config, user_config)

        # Expand paths
        config = self._expand_paths(config)

        return config

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries."""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _expand_paths(self, config: Any) -> Any:
        """Recursively expand ~ in paths."""
        if isinstance(config, dict):
            return {k: self._expand_paths(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._expand_paths(v) for v in config]
        elif isinstance(config, str) and config.startswith("~"):
            return str(Path(config).expanduser())
        return config

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by dot-notation key."""
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value
    
    def save(self) -> None:
        """Save current configuration to file."""
        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write config to YAML
        with open(self.config_path, 'w') as f:
            yaml.safe_dump(self._config, f, default_flow_style=False, sort_keys=False)

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    @property
    def user_name(self) -> str:
        return self.get("user.name", "User")

    @property
    def ollama_host(self) -> str:
        return self.get("models.local.host", "http://localhost:11434")

    @property
    def embedding_model(self) -> str:
        return self.get("models.local.embedding_model", "nomic-embed-text")

    @property
    def default_chat_model(self) -> str:
        mode = self.get("models.local.default", "balanced")
        return self.get(f"models.local.chat_models.{mode}", "llama3.1:7b")

    @property
    def cloud_api_key(self) -> Optional[str]:
        env_var = self.get("models.cloud.api_key_env", "ANTHROPIC_API_KEY")
        return os.environ.get(env_var)

    @property
    def cloud_model(self) -> str:
        return self.get("models.cloud.models.default", "claude-sonnet-4-20250514")

    @property
    def vector_db_path(self) -> Path:
        return Path(self.get("rag.vector_db_path", "~/.polly/chroma_db"))

    @property
    def domains(self) -> Dict[str, Any]:
        return self.get("domains", {})

    @property
    def obsidian_vault_path(self) -> Optional[Path]:
        path = self.get("obsidian.vault_path")
        return Path(path) if path else None

    @property
    def server_host(self) -> str:
        return self.get("server.host", "0.0.0.0")

    @property
    def server_port(self) -> int:
        return self.get("server.port", 11436)

    @property
    def compression_enabled(self) -> bool:
        return self.get("compression.enabled", True)

    @property
    def compression_threshold(self) -> int:
        return self.get("compression.message_threshold", 20)

    @property
    def compression_age_hours(self) -> int:
        return self.get("compression.age_hours", 24)

    @property
    def compression_keep_recent(self) -> int:
        return self.get("compression.keep_recent", 10)

    @property
    def compression_show_stats(self) -> bool:
        return self.get("compression.show_stats", False)

    @property
    def knowledge_base_path(self) -> Path:
        """Get the knowledge base root path."""
        # Check if new config structure exists
        kb_path = self.get("knowledge_base.path")
        if kb_path:
            return Path(kb_path)
        
        # Fallback: Check if notes.native.path exists (legacy)
        notes_path = self.get("notes.native.path")
        if notes_path:
            # Extract parent directory (e.g., ~/.polly/notes -> ~/.polly)
            return Path(notes_path).parent
        
        # Ultimate fallback
        return Path.home() / ".polly"
    
    def set_knowledge_base_path(self, new_path: str | Path) -> bool:
        """
        Set the knowledge base path and validate it.
        
        Args:
            new_path: The new path for the knowledge base
            
        Returns:
            bool: True if successful, False if validation fails
        """
        new_path = Path(new_path).expanduser().resolve()
        
        # Validate path
        if not self._validate_knowledge_base_path(new_path):
            return False
        
        # Update config
        if "knowledge_base" not in self._config:
            self._config["knowledge_base"] = {}
        
        self._config["knowledge_base"]["path"] = str(new_path)
        
        # Save to file
        self.save()
        
        return True
    
    def _validate_knowledge_base_path(self, path: Path) -> bool:
        """
        Validate that a path is suitable for the knowledge base.
        
        Args:
            path: Path to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Check if path exists or can be created
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
            except (PermissionError, OSError):
                return False
        
        # Check if path is writable
        if not os.access(path, os.W_OK):
            return False
        
        # Check if path is a directory
        if not path.is_dir():
            return False
        
        return True
    
    def detect_cloud_services(self) -> Dict[str, Optional[Path]]:
        """
        Detect common cloud storage services and their paths.
        
        Returns:
            Dict mapping service name to path (None if not found)
        """
        home = Path.home()
        services = {
            "Dropbox": home / "Dropbox",
            "iCloud Drive": home / "Library" / "Mobile Documents" / "com~apple~CloudDocs",
            "Google Drive": home / "Google Drive",
            "OneDrive": home / "OneDrive",
        }
        
        return {
            name: path if path.exists() else None
            for name, path in services.items()
        }


# Global config instance
_config: Optional[PollyConfig] = None


def get_config() -> PollyConfig:
    """Get global config instance."""
    global _config
    if _config is None:
        _config = PollyConfig()
    return _config


def load_config(config_path: Optional[Path] = None) -> PollyConfig:
    """Load config from specific path."""
    global _config
    _config = PollyConfig(config_path)
    return _config
