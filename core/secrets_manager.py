"""
Secrets Manager - Secure Storage for API Keys and Credentials

Provides encrypted storage for sensitive credentials using the system keyring.
Falls back to encrypted file storage if keyring is unavailable.

Features:
- Secure storage using system keyring (macOS Keychain, Windows Credential Vault, etc.)
- Encrypted fallback for systems without keyring
- Support for multiple providers
- Safe key retrieval with fallback to environment variables
- CLI-friendly key management
"""

import os
import json
import base64
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False
    logger.warning("keyring library not available, using encrypted file storage")


@dataclass
class SecretMetadata:
    """Metadata for a stored secret."""
    key_name: str
    provider: str
    created_at: datetime
    last_accessed: Optional[datetime] = None
    storage_type: str = "keyring"  # "keyring" or "file"


class SecretsManager:
    """
    Manages secure storage and retrieval of API keys and credentials.
    
    Uses system keyring when available, falls back to encrypted file storage.
    """
    
    SERVICE_NAME = "polly-ai"
    ENCRYPTION_KEY_NAME = "polly-encryption-key"
    
    # Known provider configurations
    PROVIDER_CONFIGS = {
        'anthropic': {
            'key_name': 'ANTHROPIC_API_KEY',
            'env_var': 'ANTHROPIC_API_KEY',
            'description': 'Anthropic Claude API Key',
            'format': 'sk-ant-api03-...',
            'validate_prefix': 'sk-ant-'
        },
        'openai': {
            'key_name': 'OPENAI_API_KEY',
            'env_var': 'OPENAI_API_KEY',
            'description': 'OpenAI GPT API Key',
            'format': 'sk-...',
            'validate_prefix': 'sk-'
        },
        'github': {
            'key_name': 'GITHUB_TOKEN',
            'env_var': 'GITHUB_TOKEN',
            'description': 'GitHub Personal Access Token (for Models API)',
            'format': 'ghp_... or github_pat_...',
            'validate_prefix': ['ghp_', 'github_pat_', 'gho_']
        },
        'grok': {
            'key_name': 'GROK_API_KEY',
            'env_var': 'XAI_API_KEY',
            'description': 'xAI Grok API Key',
            'format': 'xai-...',
            'validate_prefix': 'xai-'
        },
        'perplexity': {
            'key_name': 'PERPLEXITY_API_KEY',
            'env_var': 'PERPLEXITY_API_KEY',
            'description': 'Perplexity AI API Key',
            'format': 'pplx-...',
            'validate_prefix': 'pplx-'
        },
        'gemini': {
            'key_name': 'GEMINI_API_KEY',
            'env_var': 'GOOGLE_API_KEY',
            'description': 'Google Gemini API Key',
            'format': 'AI...',
            'validate_prefix': 'AI'
        },
        'mistral': {
            'key_name': 'MISTRAL_API_KEY',
            'env_var': 'MISTRAL_API_KEY',
            'description': 'Mistral AI API Key',
            'format': '...',
            'validate_prefix': None  # Mistral keys don't have a consistent prefix
        },
        'openrouter': {
            'key_name': 'OPENROUTER_API_KEY',
            'env_var': 'OPENROUTER_API_KEY',
            'description': 'OpenRouter API Key (100+ models via single API)',
            'format': 'sk-or-...',
            'validate_prefix': 'sk-or-'
        }
    }
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize the secrets manager.
        
        Args:
            storage_path: Path for encrypted file storage (default: ~/.polly/secrets)
        """
        self.storage_path = storage_path or Path.home() / '.polly' / 'secrets'
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.metadata_file = self.storage_path / 'metadata.json'
        self.secrets_file = self.storage_path / 'secrets.enc'
        
        # Load or create encryption key
        self._encryption_key = self._get_or_create_encryption_key()
        self._cipher = Fernet(self._encryption_key)
        
        # Load metadata
        self._metadata: Dict[str, SecretMetadata] = self._load_metadata()
        
        logger.info(f"Secrets manager initialized (keyring={'available' if KEYRING_AVAILABLE else 'unavailable'})")
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for file storage."""
        key_file = self.storage_path / '.key'
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        
        # Generate new key
        key = Fernet.generate_key()
        
        # Save key (with restrictive permissions)
        key_file.touch(mode=0o600)
        with open(key_file, 'wb') as f:
            f.write(key)
        
        logger.info("Generated new encryption key for secrets")
        return key
    
    def _load_metadata(self) -> Dict[str, SecretMetadata]:
        """Load metadata about stored secrets."""
        if not self.metadata_file.exists():
            return {}
        
        try:
            with open(self.metadata_file) as f:
                data = json.load(f)
            
            metadata = {}
            for key, value in data.items():
                metadata[key] = SecretMetadata(
                    key_name=value['key_name'],
                    provider=value['provider'],
                    created_at=datetime.fromisoformat(value['created_at']),
                    last_accessed=datetime.fromisoformat(value['last_accessed']) if value.get('last_accessed') else None,
                    storage_type=value.get('storage_type', 'keyring')
                )
            
            return metadata
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
            return {}
    
    def _save_metadata(self):
        """Save metadata about stored secrets."""
        data = {}
        for key, meta in self._metadata.items():
            data[key] = {
                'key_name': meta.key_name,
                'provider': meta.provider,
                'created_at': meta.created_at.isoformat(),
                'last_accessed': meta.last_accessed.isoformat() if meta.last_accessed else None,
                'storage_type': meta.storage_type
            }
        
        with open(self.metadata_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_file_secrets(self) -> Dict[str, str]:
        """Load secrets from encrypted file."""
        if not self.secrets_file.exists():
            return {}
        
        try:
            with open(self.secrets_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self._cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            logger.error(f"Error loading encrypted secrets: {e}")
            return {}
    
    def _save_file_secrets(self, secrets: Dict[str, str]):
        """Save secrets to encrypted file."""
        try:
            json_data = json.dumps(secrets).encode()
            encrypted_data = self._cipher.encrypt(json_data)
            
            # Write with restrictive permissions
            self.secrets_file.touch(mode=0o600)
            with open(self.secrets_file, 'wb') as f:
                f.write(encrypted_data)
        except Exception as e:
            logger.error(f"Error saving encrypted secrets: {e}")
            raise
    
    def set_secret(self, provider: str, value: str) -> bool:
        """
        Store a secret for a provider.
        
        Args:
            provider: Provider name (e.g., "anthropic", "openai")
            value: The API key or token
        
        Returns:
            True if successful
        
        Raises:
            ValueError: If provider is unknown or value format is invalid
        """
        # Validate provider
        if provider not in self.PROVIDER_CONFIGS:
            raise ValueError(f"Unknown provider: {provider}")
        
        config = self.PROVIDER_CONFIGS[provider]
        
        # Validate format
        if not self._validate_key_format(provider, value):
            logger.warning(f"Key format validation failed for {provider}")
            # Continue anyway - might be a valid key with unexpected format
        
        key_name = config['key_name']
        
        # Try to store in keyring first
        if KEYRING_AVAILABLE:
            try:
                keyring.set_password(self.SERVICE_NAME, key_name, value)
                storage_type = "keyring"
                logger.info(f"Stored {provider} key in system keyring")
            except Exception as e:
                logger.warning(f"Failed to store in keyring: {e}, falling back to file storage")
                storage_type = "file"
                self._store_in_file(key_name, value)
        else:
            # Use encrypted file storage
            storage_type = "file"
            self._store_in_file(key_name, value)
            logger.info(f"Stored {provider} key in encrypted file")
        
        # Update metadata
        self._metadata[key_name] = SecretMetadata(
            key_name=key_name,
            provider=provider,
            created_at=datetime.now(),
            storage_type=storage_type
        )
        self._save_metadata()
        
        return True
    
    def _store_in_file(self, key_name: str, value: str):
        """Store secret in encrypted file."""
        secrets = self._load_file_secrets()
        secrets[key_name] = value
        self._save_file_secrets(secrets)
    
    def _validate_key_format(self, provider: str, value: str) -> bool:
        """Validate key format for a provider."""
        config = self.PROVIDER_CONFIGS.get(provider)
        if not config:
            return True  # Unknown provider, skip validation
        
        prefix = config.get('validate_prefix')
        if not prefix:
            return True  # No validation configured
        
        if isinstance(prefix, list):
            return any(value.startswith(p) for p in prefix)
        else:
            return value.startswith(prefix)
    
    def get_secret(
        self,
        provider: str,
        fallback_to_env: bool = True
    ) -> Optional[str]:
        """
        Retrieve a secret for a provider.
        
        Args:
            provider: Provider name
            fallback_to_env: If True, check environment variables if not in storage
        
        Returns:
            The secret value or None if not found
        """
        if provider not in self.PROVIDER_CONFIGS:
            logger.warning(f"Unknown provider: {provider}")
            return None
        
        config = self.PROVIDER_CONFIGS[provider]
        key_name = config['key_name']
        
        # Check if we have metadata
        if key_name in self._metadata:
            meta = self._metadata[key_name]
            
            # Try keyring first if that's where it's stored
            if meta.storage_type == "keyring" and KEYRING_AVAILABLE:
                try:
                    value = keyring.get_password(self.SERVICE_NAME, key_name)
                    if value:
                        # Update last accessed
                        meta.last_accessed = datetime.now()
                        self._save_metadata()
                        return value
                except Exception as e:
                    logger.warning(f"Failed to retrieve from keyring: {e}")
            
            # Try file storage
            secrets = self._load_file_secrets()
            if key_name in secrets:
                # Update last accessed
                meta.last_accessed = datetime.now()
                self._save_metadata()
                return secrets[key_name]
        
        # Fallback to environment variable
        if fallback_to_env:
            env_var = config['env_var']
            value = os.getenv(env_var)
            if value:
                logger.info(f"Using {provider} key from environment variable")
                return value
        
        return None
    
    def delete_secret(self, provider: str) -> bool:
        """
        Delete a secret for a provider.
        
        Args:
            provider: Provider name
        
        Returns:
            True if deleted, False if not found
        """
        if provider not in self.PROVIDER_CONFIGS:
            logger.warning(f"Unknown provider: {provider}")
            return False
        
        config = self.PROVIDER_CONFIGS[provider]
        key_name = config['key_name']
        
        found = False
        
        # Try to delete from keyring
        if KEYRING_AVAILABLE:
            try:
                keyring.delete_password(self.SERVICE_NAME, key_name)
                found = True
                logger.info(f"Deleted {provider} key from keyring")
            except Exception:
                pass  # Key might not be in keyring
        
        # Try to delete from file storage
        secrets = self._load_file_secrets()
        if key_name in secrets:
            del secrets[key_name]
            self._save_file_secrets(secrets)
            found = True
            logger.info(f"Deleted {provider} key from file storage")
        
        # Remove metadata
        if key_name in self._metadata:
            del self._metadata[key_name]
            self._save_metadata()
            found = True
        
        return found
    
    def list_secrets(self) -> List[Dict[str, any]]:
        """
        List all stored secrets (without revealing values).
        
        Returns:
            List of dicts with secret metadata
        """
        secrets = []
        
        for key_name, meta in self._metadata.items():
            secrets.append({
                'provider': meta.provider,
                'key_name': key_name,
                'description': self.PROVIDER_CONFIGS[meta.provider]['description'],
                'created_at': meta.created_at.isoformat(),
                'last_accessed': meta.last_accessed.isoformat() if meta.last_accessed else None,
                'storage_type': meta.storage_type,
                'is_set': True
            })
        
        # Add unset providers
        for provider, config in self.PROVIDER_CONFIGS.items():
            key_name = config['key_name']
            if key_name not in self._metadata:
                # Check if in environment
                has_env = bool(os.getenv(config['env_var']))
                secrets.append({
                    'provider': provider,
                    'key_name': key_name,
                    'description': config['description'],
                    'created_at': None,
                    'last_accessed': None,
                    'storage_type': 'environment' if has_env else None,
                    'is_set': has_env
                })
        
        return sorted(secrets, key=lambda x: x['provider'])
    
    def get_all_provider_keys(self) -> Dict[str, Optional[str]]:
        """
        Get all provider API keys at once.
        
        Returns:
            Dict mapping provider name to API key (or None if not set)
        """
        keys = {}
        for provider in self.PROVIDER_CONFIGS:
            keys[provider] = self.get_secret(provider, fallback_to_env=True)
        return keys
    
    def test_secret(self, provider: str) -> bool:
        """
        Test if a secret can be retrieved.
        
        Args:
            provider: Provider name
        
        Returns:
            True if secret is accessible
        """
        value = self.get_secret(provider, fallback_to_env=True)
        return value is not None and len(value) > 0
    
    def get_provider_config(self, provider: str) -> Optional[Dict]:
        """Get configuration for a provider."""
        return self.PROVIDER_CONFIGS.get(provider)


# Global instance
_secrets_manager: Optional[SecretsManager] = None


def get_secrets_manager() -> SecretsManager:
    """Get global secrets manager instance."""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager
