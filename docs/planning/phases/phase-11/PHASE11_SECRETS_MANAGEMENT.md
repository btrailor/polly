# Phase 11: Cross-Platform Secrets Management

**Document Version:** 1.0  
**Last Updated:** January 28, 2026  
**Related:** [PHASE11_MULTI_MODEL_ENHANCED_V2.md](./PHASE11_MULTI_MODEL_ENHANCED_V2.md)

---

## Executive Summary

This document specifies the cross-platform encrypted storage system for API keys and credentials. The system must work across macOS, Windows, and Linux with secure storage backends, encrypted file fallback, and seamless migration from environment variables.

**Key Requirements:**
- Cross-platform compatibility (macOS, Windows, Linux)
- Secure storage using native keychains where available
- Encrypted file fallback for systems without keychain
- Migration from existing environment variable approach
- Settings UI for key management
- Zero plaintext keys in config files

---

## Architecture

### Storage Strategy by Platform

```
┌─────────────────────────────────────────────────────────┐
│              API Key Storage Request                    │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│           Platform Detection                            │
└─────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    ┌─────────┐     ┌─────────┐     ┌─────────┐
    │  macOS  │     │ Windows │     │  Linux  │
    └─────────┘     └─────────┘     └─────────┘
          │               │               │
          ▼               ▼               ▼
    ┌─────────┐     ┌─────────┐     ┌─────────┐
    │Keychain │     │  Cred.  │     │ Secret  │
    │         │     │ Manager │     │ Service │
    └─────────┘     └─────────┘     └─────────┘
          │               │               │
          └───────────────┼───────────────┘
                          │
                  If not available ↓
                          ▼
              ┌─────────────────────┐
              │  Encrypted File     │
              │  (AES-256-GCM)     │
              │  ~/.polly/secrets  │
              └─────────────────────┘
```

### Platform-Specific Backends

| Platform | Primary Backend | Fallback | Notes |
|----------|----------------|----------|-------|
| macOS | Keychain | Encrypted file | Native, most secure |
| Windows | Credential Manager | Encrypted file | Via Windows API |
| Linux | Secret Service (GNOME/KDE) | Encrypted file | freedesktop.org spec |
| Other Unix | N/A | Encrypted file | BSD, etc. |

---

## Implementation

### Using `keyring` Library

```python
# requirements.txt
keyring>=24.0.0
cryptography>=41.0.0
```

The `keyring` library provides cross-platform secure storage:

```python
# core/secrets/manager.py
import keyring
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64
import os

class SecretsManager:
    """
    Cross-platform secrets management
    
    Storage backends (in order of preference):
    1. Native keychain (macOS Keychain, Windows Credential Manager, Linux Secret Service)
    2. Encrypted file fallback
    """
    
    SERVICE_NAME = "Polly"
    ENCRYPTED_FILE_PATH = os.path.expanduser("~/.polly/secrets.enc")
    
    def __init__(self):
        self.backend = self._detect_backend()
        self.encryption_key = None
        
        if self.backend == "encrypted_file":
            self.encryption_key = self._get_or_create_encryption_key()
    
    def _detect_backend(self) -> str:
        """
        Detect which backend to use
        
        Returns:
            'keyring' or 'encrypted_file'
        """
        try:
            # Test if keyring is available
            test_key = "test"
            keyring.set_password(self.SERVICE_NAME, test_key, "test_value")
            keyring.delete_password(self.SERVICE_NAME, test_key)
            return "keyring"
        except Exception as e:
            logger.warning(f"Keyring not available: {e}. Using encrypted file fallback.")
            return "encrypted_file"
    
    # ========== Public API ==========
    
    def set(self, key: str, value: str):
        """
        Store a secret
        
        Args:
            key: Secret identifier (e.g., "anthropic_api_key")
            value: Secret value
        """
        if self.backend == "keyring":
            self._set_keyring(key, value)
        else:
            self._set_encrypted_file(key, value)
    
    def get(self, key: str) -> str | None:
        """
        Retrieve a secret
        
        Args:
            key: Secret identifier
        
        Returns:
            Secret value or None if not found
        """
        if self.backend == "keyring":
            return self._get_keyring(key)
        else:
            return self._get_encrypted_file(key)
    
    def delete(self, key: str):
        """Delete a secret"""
        if self.backend == "keyring":
            self._delete_keyring(key)
        else:
            self._delete_encrypted_file(key)
    
    def list_keys(self) -> list[str]:
        """List all stored secret keys"""
        if self.backend == "keyring":
            # Keyring doesn't provide listing, store manifest
            return self._list_keyring_manifest()
        else:
            return self._list_encrypted_file()
    
    # ========== Keyring Backend ==========
    
    def _set_keyring(self, key: str, value: str):
        """Store in native keychain"""
        keyring.set_password(self.SERVICE_NAME, key, value)
        self._update_keyring_manifest(key, action="add")
        logger.info(f"Stored secret '{key}' in keychain")
    
    def _get_keyring(self, key: str) -> str | None:
        """Retrieve from native keychain"""
        try:
            return keyring.get_password(self.SERVICE_NAME, key)
        except Exception as e:
            logger.error(f"Failed to retrieve secret '{key}': {e}")
            return None
    
    def _delete_keyring(self, key: str):
        """Delete from native keychain"""
        try:
            keyring.delete_password(self.SERVICE_NAME, key)
            self._update_keyring_manifest(key, action="remove")
            logger.info(f"Deleted secret '{key}' from keychain")
        except Exception as e:
            logger.error(f"Failed to delete secret '{key}': {e}")
    
    def _update_keyring_manifest(self, key: str, action: str):
        """
        Maintain a manifest of keys in keychain
        (Since keyring doesn't support listing)
        """
        manifest_key = "__manifest__"
        manifest_json = keyring.get_password(self.SERVICE_NAME, manifest_key) or "[]"
        manifest = json.loads(manifest_json)
        
        if action == "add" and key not in manifest:
            manifest.append(key)
        elif action == "remove" and key in manifest:
            manifest.remove(key)
        
        keyring.set_password(self.SERVICE_NAME, manifest_key, json.dumps(manifest))
    
    def _list_keyring_manifest(self) -> list[str]:
        """List keys from manifest"""
        manifest_key = "__manifest__"
        manifest_json = keyring.get_password(self.SERVICE_NAME, manifest_key) or "[]"
        return json.loads(manifest_json)
    
    # ========== Encrypted File Backend ==========
    
    def _get_or_create_encryption_key(self) -> bytes:
        """
        Get or create encryption key for file backend
        
        Key is derived from:
        1. Machine-specific identifier (MAC address, hostname)
        2. User-specific salt
        3. PBKDF2 key derivation
        """
        key_file = os.path.expanduser("~/.polly/encryption.key")
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        
        # Generate new key
        salt = os.urandom(16)
        machine_id = self._get_machine_id()
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(machine_id.encode()))
        
        # Store key
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        with open(key_file, 'wb') as f:
            f.write(key)
        os.chmod(key_file, 0o600)  # Owner read/write only
        
        return key
    
    def _get_machine_id(self) -> str:
        """Get machine-specific identifier"""
        import platform
        import uuid
        
        # Combine multiple machine identifiers
        identifiers = [
            platform.node(),  # hostname
            str(uuid.getnode()),  # MAC address
            platform.system(),
            platform.release()
        ]
        return ":".join(identifiers)
    
    def _set_encrypted_file(self, key: str, value: str):
        """Store in encrypted file"""
        secrets = self._load_encrypted_file()
        secrets[key] = value
        self._save_encrypted_file(secrets)
        logger.info(f"Stored secret '{key}' in encrypted file")
    
    def _get_encrypted_file(self, key: str) -> str | None:
        """Retrieve from encrypted file"""
        secrets = self._load_encrypted_file()
        return secrets.get(key)
    
    def _delete_encrypted_file(self, key: str):
        """Delete from encrypted file"""
        secrets = self._load_encrypted_file()
        if key in secrets:
            del secrets[key]
            self._save_encrypted_file(secrets)
            logger.info(f"Deleted secret '{key}' from encrypted file")
    
    def _list_encrypted_file(self) -> list[str]:
        """List keys from encrypted file"""
        secrets = self._load_encrypted_file()
        return list(secrets.keys())
    
    def _load_encrypted_file(self) -> dict:
        """Load and decrypt secrets file"""
        if not os.path.exists(self.ENCRYPTED_FILE_PATH):
            return {}
        
        try:
            with open(self.ENCRYPTED_FILE_PATH, 'rb') as f:
                encrypted_data = f.read()
            
            fernet = Fernet(self.encryption_key)
            decrypted_data = fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        
        except Exception as e:
            logger.error(f"Failed to load encrypted secrets: {e}")
            return {}
    
    def _save_encrypted_file(self, secrets: dict):
        """Encrypt and save secrets file"""
        try:
            fernet = Fernet(self.encryption_key)
            json_data = json.dumps(secrets).encode()
            encrypted_data = fernet.encrypt(json_data)
            
            os.makedirs(os.path.dirname(self.ENCRYPTED_FILE_PATH), exist_ok=True)
            with open(self.ENCRYPTED_FILE_PATH, 'wb') as f:
                f.write(encrypted_data)
            os.chmod(self.ENCRYPTED_FILE_PATH, 0o600)  # Owner read/write only
        
        except Exception as e:
            logger.error(f"Failed to save encrypted secrets: {e}")
            raise
    
    # ========== Migration ==========
    
    def migrate_from_env(self):
        """
        Migrate API keys from environment variables to secure storage
        
        Looks for:
        - ANTHROPIC_API_KEY
        - OPENAI_API_KEY
        - GOOGLE_AI_API_KEY
        - etc.
        """
        env_keys = {
            "ANTHROPIC_API_KEY": "anthropic_api_key",
            "OPENAI_API_KEY": "openai_api_key",
            "GITHUB_TOKEN": "github_oauth_token",
            "OPENROUTER_API_KEY": "openrouter_api_key",
            "GOOGLE_AI_API_KEY": "google_ai_api_key",
            "MISTRAL_API_KEY": "mistral_api_key",
            "GROK_API_KEY": "grok_api_key",
            "PERPLEXITY_API_KEY": "perplexity_api_key"
        }
        
        migrated = []
        for env_var, key_name in env_keys.items():
            value = os.environ.get(env_var)
            if value:
                self.set(key_name, value)
                migrated.append(key_name)
                logger.info(f"Migrated {env_var} to secure storage")
        
        return migrated
```

---

## Configuration Integration

### Config File References

Instead of storing keys in `config.yaml`, use references:

```yaml
# config.yaml
models:
  cloud:
    anthropic:
      enabled: true
      api_key: secret:anthropic_api_key  # Reference to secrets manager
      default_model: claude-sonnet-4-20250514
    
    openai:
      enabled: true
      api_key: secret:openai_api_key
      default_model: gpt-4-turbo
    
    grok:
      enabled: false
      api_key: secret:grok_api_key
      user_consent: false
```

### Config Loader Integration

```python
# core/config.py
from core.secrets.manager import SecretsManager

class Config:
    def __init__(self):
        self.data = self._load_yaml()
        self.secrets = SecretsManager()
    
    def get(self, path: str, default=None):
        """
        Get config value, resolving secret references
        
        Examples:
            config.get("models.cloud.anthropic.api_key")
            → Resolves "secret:anthropic_api_key"
            → Returns actual API key from secrets manager
        """
        value = self._get_nested(path, default)
        
        # Resolve secret reference
        if isinstance(value, str) and value.startswith("secret:"):
            secret_key = value[7:]  # Remove "secret:" prefix
            return self.secrets.get(secret_key)
        
        return value
    
    def set_secret(self, path: str, value: str):
        """
        Store a secret and update config reference
        
        Example:
            config.set_secret("models.cloud.anthropic.api_key", "sk-ant-...")
            → Stores in secrets manager as "anthropic_api_key"
            → Updates config.yaml with "secret:anthropic_api_key"
        """
        # Extract secret key name from path
        secret_key = self._path_to_secret_key(path)
        
        # Store in secrets manager
        self.secrets.set(secret_key, value)
        
        # Update config with reference
        self._set_nested(path, f"secret:{secret_key}")
        self.save()
```

---

## Settings UI

### Provider API Key Configuration

```
┌─────────────────────────────────────────────────────────┐
│  Settings > Models > Providers > Anthropic              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  API Key Configuration                                  │
│                                                          │
│  Status: ● Connected                                    │
│  Storage: macOS Keychain (secure)                       │
│                                                          │
│  API Key: [••••••••••••••••••••••] [Show] [Change]     │
│                                                          │
│  [ ] Use environment variable instead                   │
│      ANTHROPIC_API_KEY (not recommended)                │
│                                                          │
│  ─────────────────────────────────────────────────────  │
│                                                          │
│  Test Connection                                        │
│  [Test API Key]                                         │
│                                                          │
│  Last tested: 2 hours ago ✓                            │
│  Models available: 3 (Haiku, Sonnet 4, Opus 4)         │
│                                                          │
│  ─────────────────────────────────────────────────────  │
│                                                          │
│  Security Information                                   │
│                                                          │
│  ✓ API key stored in macOS Keychain                    │
│  ✓ Never written to disk in plaintext                  │
│  ✓ Automatically synced across devices via iCloud      │
│    Keychain (if enabled)                                │
│                                                          │
│  [Learn more about secret storage]                     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### First-Time Setup Wizard

```
┌─────────────────────────────────────────────────────────┐
│  Welcome to Polly - API Key Setup (Step 1 of 3)        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Polly needs API keys to connect to cloud AI providers.│
│                                                          │
│  Your API keys will be stored securely in:             │
│  ✓ macOS Keychain (this device)                        │
│                                                          │
│  ─────────────────────────────────────────────────────  │
│                                                          │
│  Essential Providers                                    │
│                                                          │
│  Anthropic (Claude) - Recommended                       │
│  API Key: [_______________________________]            │
│  [Get API Key from anthropic.com]                      │
│                                                          │
│  OpenAI (GPT)                                           │
│  API Key: [_______________________________]            │
│  [Get API Key from platform.openai.com]                │
│                                                          │
│  GitHub Copilot                                         │
│  [Connect with GitHub OAuth]                           │
│                                                          │
│  ─────────────────────────────────────────────────────  │
│                                                          │
│  [Skip for now]  [Continue]                            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Migration Tool

### Command-Line Migration

```bash
# Migrate from environment variables
$ polly migrate-secrets

Migrating API keys to secure storage...

✓ Found ANTHROPIC_API_KEY
  → Stored as anthropic_api_key in Keychain

✓ Found OPENAI_API_KEY
  → Stored as openai_api_key in Keychain

✗ GITHUB_TOKEN not found
  → Skipping

Migrated 2 API keys successfully.

You can now safely remove these environment variables.
Would you like to update your shell profile? [y/N]
```

### Python Migration Script

```python
# scripts/migrate_secrets.py
from core.secrets.manager import SecretsManager
from core.config import Config

def migrate():
    """Migrate API keys from environment variables"""
    secrets = SecretsManager()
    config = Config()
    
    print("Migrating API keys to secure storage...")
    print(f"Using backend: {secrets.backend}")
    print()
    
    # Migrate from environment
    migrated = secrets.migrate_from_env()
    
    if not migrated:
        print("No environment variables found to migrate.")
        return
    
    # Update config references
    for key_name in migrated:
        config_path = f"models.cloud.{key_name.split('_')[0]}.api_key"
        config.set(config_path, f"secret:{key_name}")
    
    config.save()
    
    print(f"\n✓ Migrated {len(migrated)} API keys successfully:")
    for key in migrated:
        print(f"  • {key}")
    
    print("\nYou can now safely remove environment variables.")
    print("Add these lines to your shell profile:")
    print()
    for key_name in migrated:
        env_var = key_name.upper()
        print(f"  # unset {env_var}")

if __name__ == "__main__":
    migrate()
```

---

## Security Considerations

### Threat Model

**Threats Mitigated:**
1. ✅ Plaintext keys in config files
2. ✅ Keys leaked via version control
3. ✅ Keys exposed in process environment
4. ✅ Unauthorized local access (encrypted file + permissions)

**Threats Not Mitigated:**
1. ⚠️ Root/admin access to machine (can access keychain)
2. ⚠️ Malware with keychain access
3. ⚠️ Physical access to unlocked machine

### Best Practices

```python
# core/secrets/manager.py

class SecretsManager:
    
    def validate_api_key_format(self, provider: str, key: str) -> bool:
        """Validate API key format before storing"""
        patterns = {
            "anthropic": r"^sk-ant-[a-zA-Z0-9\-_]{90,}$",
            "openai": r"^sk-[a-zA-Z0-9]{48}$",
            "google": r"^AIza[a-zA-Z0-9\-_]{35}$"
        }
        
        pattern = patterns.get(provider)
        if pattern and not re.match(pattern, key):
            raise ValueError(f"Invalid {provider} API key format")
        
        return True
    
    def mask_api_key(self, key: str) -> str:
        """Mask API key for display"""
        if len(key) <= 8:
            return "•" * len(key)
        return key[:4] + "•" * (len(key) - 8) + key[-4:]
    
    def rotate_encryption_key(self):
        """
        Rotate encryption key for encrypted file backend
        (Re-encrypt all secrets with new key)
        """
        if self.backend != "encrypted_file":
            return
        
        # Load with old key
        old_secrets = self._load_encrypted_file()
        
        # Generate new key
        os.remove(os.path.expanduser("~/.polly/encryption.key"))
        self.encryption_key = self._get_or_create_encryption_key()
        
        # Re-encrypt with new key
        self._save_encrypted_file(old_secrets)
        
        logger.info("Encryption key rotated successfully")
```

---

## Testing

### Unit Tests

```python
# tests/test_secrets_manager.py
import pytest
import os
from core.secrets.manager import SecretsManager

@pytest.fixture
def secrets_manager(tmp_path):
    # Use temp directory for testing
    manager = SecretsManager()
    manager.ENCRYPTED_FILE_PATH = str(tmp_path / "secrets.enc")
    return manager

def test_set_and_get_secret(secrets_manager):
    secrets_manager.set("test_key", "test_value")
    assert secrets_manager.get("test_key") == "test_value"

def test_delete_secret(secrets_manager):
    secrets_manager.set("test_key", "test_value")
    secrets_manager.delete("test_key")
    assert secrets_manager.get("test_key") is None

def test_list_keys(secrets_manager):
    secrets_manager.set("key1", "value1")
    secrets_manager.set("key2", "value2")
    assert set(secrets_manager.list_keys()) == {"key1", "key2"}

def test_encrypted_file_permissions(secrets_manager):
    secrets_manager.set("test_key", "test_value")
    
    # Check file permissions (owner read/write only)
    mode = os.stat(secrets_manager.ENCRYPTED_FILE_PATH).st_mode
    assert oct(mode)[-3:] == "600"

def test_migration_from_env(secrets_manager, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test123")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test456")
    
    migrated = secrets_manager.migrate_from_env()
    
    assert "anthropic_api_key" in migrated
    assert "openai_api_key" in migrated
    assert secrets_manager.get("anthropic_api_key") == "sk-ant-test123"
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_config_secret_resolution():
    config = Config()
    secrets = SecretsManager()
    
    # Store secret
    secrets.set("anthropic_api_key", "sk-ant-test123")
    
    # Update config
    config.data["models"]["cloud"]["anthropic"]["api_key"] = "secret:anthropic_api_key"
    
    # Retrieve via config (should resolve reference)
    api_key = config.get("models.cloud.anthropic.api_key")
    assert api_key == "sk-ant-test123"
```

---

## Platform-Specific Notes

### macOS

```python
# Uses Keychain via keyring library
# Keys are stored in login keychain by default
# Can sync via iCloud Keychain (user preference)

# Manual verification:
# $ security find-generic-password -s Polly -a anthropic_api_key
```

### Windows

```python
# Uses Windows Credential Manager
# Stored in: Control Panel > Credential Manager > Generic Credentials

# Manual verification (PowerShell):
# > cmdkey /list | Select-String "Polly"
```

### Linux

```python
# Uses Secret Service API (GNOME Keyring, KDE Wallet)
# Requires D-Bus and running desktop environment

# Manual verification:
# $ secret-tool lookup service Polly username anthropic_api_key
```

### Fallback (All Platforms)

```python
# Encrypted file: ~/.polly/secrets.enc
# Encryption key: ~/.polly/encryption.key (machine-specific)
# Algorithm: AES-256-GCM via Fernet
```

---

## Performance

**Keychain Backend:**
- Get operation: < 10ms
- Set operation: < 20ms
- Cached after first access

**Encrypted File Backend:**
- Get operation: < 5ms (decrypts entire file)
- Set operation: < 10ms (re-encrypts entire file)
- All keys loaded at startup

**Optimization:**
- Cache decrypted secrets in memory (secure string)
- Lazy loading for encrypted file
- Background key validation

---

## Dependencies

```python
# requirements.txt
keyring>=24.0.0
cryptography>=41.0.0

# Platform-specific (auto-installed by keyring):
# macOS: (built-in)
# Windows: pywin32
# Linux: SecretStorage, jeepney
```

---

## Timeline

**Phase 11a Week 1-2:**
- Days 1-2: Implement SecretsManager class
- Days 3-4: Config integration
- Days 5-6: Migration tool
- Days 7: Settings UI integration

**Testing:**
- Day 8: Cross-platform testing (macOS, Windows, Linux)

---

## Related Documents

- [PHASE11_MULTI_MODEL_ENHANCED_V2.md](./PHASE11_MULTI_MODEL_ENHANCED_V2.md) - Overall Phase 11 spec
- [PHASE11_PROVIDER_SPECIFICATIONS.md](./PHASE11_PROVIDER_SPECIFICATIONS.md) - Provider details
- [master_roadmap.md](./master_roadmap.md) - Project roadmap
