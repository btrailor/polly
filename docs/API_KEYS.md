# API Key Management for Polly

## Overview

Polly now includes a **secure secrets management system** for storing API keys. Keys are stored using your operating system's native keyring (macOS Keychain, Windows Credential Vault, Linux Secret Service), with an encrypted file fallback if keyring is unavailable.

## Quick Start

### Option 1: Interactive Setup (Recommended)

Run the setup script which will guide you through adding keys:

```bash
python3 setup_keys.py
```

This will:
1. Prompt you for each provider (Anthropic, OpenAI, GitHub)
2. Validate the key format
3. Test the connection
4. Store the key securely

### Option 2: Using CLI Commands

```bash
# Add a key (will prompt securely)
python3 -m interfaces.cli keys set anthropic

# Or provide directly (less secure - visible in shell history)
python3 -m interfaces.cli keys set anthropic --key sk-ant-api03-...

# List all keys
python3 -m interfaces.cli keys list

# Test keys
python3 -m interfaces.cli keys test

# Delete a key
python3 -m interfaces.cli keys delete anthropic
```

### Option 3: Programmatic Access

```python
from core.secrets_manager import get_secrets_manager

# Get the global instance
secrets = get_secrets_manager()

# Set a key
secrets.set_secret('anthropic', 'sk-ant-api03-...')

# Get a key (with fallback to environment)
key = secrets.get_secret('anthropic', fallback_to_env=True)

# List all keys
keys_list = secrets.list_secrets()

# Delete a key
secrets.delete_secret('anthropic')
```

---

## Supported Providers

### Anthropic (Claude)

**Get Your Key**: https://console.anthropic.com/

**Key Format**: `sk-ant-api03-...`

**Models Available**:
- `claude-3-haiku-20240307` (Fast, $0.25/$1.25 per 1M tokens)
- `claude-sonnet-4-20250514` (Balanced, $3/$15 per 1M tokens)
- `claude-opus-4-20250514` (Thorough, $15/$75 per 1M tokens)

### OpenAI (GPT)

**Get Your Key**: https://platform.openai.com/api-keys

**Key Format**: `sk-...`

**Models Available**:
- `gpt-3.5-turbo` (Fast, $0.50/$1.50 per 1M tokens)
- `gpt-4-turbo` (Balanced, $10/$30 per 1M tokens)
- `gpt-4o` (Thorough, $5/$15 per 1M tokens)
- `o1-preview` (Advanced reasoning, $15/$60 per 1M tokens)

### GitHub Copilot (Coming Soon)

**Status**: Not yet implemented (Phase 11b)

**Get Your Token**: https://github.com/settings/tokens

**Key Format**: `ghp_...` or `github_pat_...`

---

## CLI Commands Reference

### `polly keys list`

List all configured API keys (values are masked for security).

```bash
$ python3 -m interfaces.cli keys list

=== API Keys ===

✓ Anthropic    [🔐 Keyring]
   Anthropic Claude API Key
   Last used: 2026-01-28T10:30:15

✓ Openai       [📁 Encrypted File]
   OpenAI GPT API Key
   Last used: 2026-01-28T09:15:42

✗ Github       [Not Set]
   GitHub Personal Access Token
```

### `polly keys set <provider>`

Add or update an API key for a provider.

```bash
# Interactive (recommended - doesn't store in shell history)
$ python3 -m interfaces.cli keys set anthropic
Enter Anthropic API key: [hidden input]
✓ Anthropic API key saved securely
Testing key...
✓ Anthropic API key is valid and working!

# Direct (visible in shell history - use with caution)
$ python3 -m interfaces.cli keys set anthropic --key sk-ant-api03-...
```

### `polly keys delete <provider>`

Remove an API key.

```bash
$ python3 -m interfaces.cli keys delete anthropic
Delete Anthropic API key? (yes/no): yes
✓ Anthropic API key deleted
```

### `polly keys test [provider]`

Test API key connectivity.

```bash
# Test all providers
$ python3 -m interfaces.cli keys test
✓ Anthropic    - Working!
✓ Openai       - Working!
✗ Github       - Not configured

# Test specific provider
$ python3 -m interfaces.cli keys test anthropic
✓ Anthropic    - Working!
```

---

## Storage Mechanisms

### 1. System Keyring (Preferred)

When available, Polly uses your OS's native keyring:

- **macOS**: Keychain Access
- **Windows**: Credential Vault
- **Linux**: Secret Service (GNOME Keyring, KWallet, etc.)

**Advantages**:
- Integrates with OS security
- Protected by system authentication
- Encrypted at rest
- Synchronized across devices (on macOS with iCloud Keychain)

**Location**: Managed by OS (e.g., `/Users/username/Library/Keychains` on macOS)

### 2. Encrypted File (Fallback)

If keyring is unavailable, Polly uses encrypted file storage:

**Location**: `~/.polly/secrets/secrets.enc`

**Encryption**: AES-256 via Fernet (from cryptography library)

**Key Storage**: `~/.polly/secrets/.key` (restrictive permissions: 600)

**Metadata**: `~/.polly/secrets/metadata.json` (stores creation dates, last access, storage type)

### 3. Environment Variables (Read-Only Fallback)

For backwards compatibility and deployment scenarios, Polly also checks environment variables:

- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`
- `GITHUB_TOKEN`

**Note**: Environment variables are **read-only**. The `keys set` command won't write to environment variables.

---

## Security Best Practices

### ✅ Do:

1. **Use the interactive setup**: `python3 setup_keys.py` (keys never touch disk unencrypted)
2. **Use `keys set` without `--key`** flag to prompt securely
3. **Regularly rotate your keys** at the provider level
4. **Use `keys test`** to verify keys are working
5. **Keep `~/.polly/secrets/.key`** file permissions at 600

### ❌ Don't:

1. **Don't use `--key` flag** unless necessary (visible in shell history)
2. **Don't commit keys** to version control
3. **Don't share your `~/.polly/secrets/` directory**
4. **Don't store keys** in plain text config files
5. **Don't use the same key** across multiple machines in production

### Shell History Warning

If you use `polly keys set --key sk-ant-...`, the key will be in your shell history:

```bash
# Clear recent command from history (bash/zsh)
history -d $(history | tail -n 1 | awk '{print $1}')

# Or clear all history
history -c

# Better: just don't use --key flag!
```

---

## Troubleshooting

### "keyring library not available"

Install the keyring package:

```bash
pip install keyring cryptography
```

Or install from requirements:

```bash
pip install -r requirements.txt
```

### "Failed to store in keyring, falling back to file storage"

This is normal on some systems. The key will be stored in an encrypted file at `~/.polly/secrets/secrets.enc`.

### "Key format validation failed"

The key doesn't match the expected format for the provider:
- Anthropic: Must start with `sk-ant-`
- OpenAI: Must start with `sk-`
- GitHub: Must start with `ghp_` or `github_pat_`

You can proceed anyway if you're sure the key is correct.

### "Connection test failed"

Possible causes:
1. Invalid API key
2. Network connectivity issues
3. Provider API is down
4. Rate limiting

Try testing again with `polly keys test <provider>`.

### Permission denied on `~/.polly/secrets/.key`

The encryption key file has incorrect permissions:

```bash
chmod 600 ~/.polly/secrets/.key
```

---

## Migrating from Environment Variables

If you currently use environment variables, you can migrate to secure storage:

```bash
# Keys will be automatically detected from environment
$ python3 -m interfaces.cli keys list
✓ Anthropic    [🌍 Environment]

# Set explicitly to move to secure storage
$ python3 -m interfaces.cli keys set anthropic
# (paste the value from echo $ANTHROPIC_API_KEY)

# Now it's in secure storage
$ python3 -m interfaces.cli keys list
✓ Anthropic    [🔐 Keyring]

# You can now remove from environment
$ unset ANTHROPIC_API_KEY
```

---

## Integration with Router

The router automatically uses the secrets manager:

```python
from core.router_v2 import IntelligentRouterV2
from core.budget_manager import BudgetManager
from core.secrets_manager import get_secrets_manager

# Get keys from secure storage
secrets = get_secrets_manager()
keys = secrets.get_all_provider_keys()

# Initialize router
router = IntelligentRouterV2(
    anthropic_api_key=keys['anthropic'],
    openai_api_key=keys['openai'],
    github_token=keys['github'],
    budget_manager=BudgetManager()
)
```

Or let the router helper do it for you:

```python
from core.router_v2 import create_router_from_config

# Automatically loads keys from secrets manager
router = create_router_from_config()
```

---

## File Structure

```
~/.polly/secrets/
├── .key                  # Encryption key (600 permissions)
├── secrets.enc           # Encrypted secrets (600 permissions)
└── metadata.json         # Metadata (creation dates, etc.)
```

---

## API Reference

### `SecretsManager`

Main class for managing secrets.

#### Methods:

**`set_secret(provider: str, value: str) -> bool`**
- Store a secret for a provider
- Validates format
- Stores in keyring or encrypted file
- Updates metadata

**`get_secret(provider: str, fallback_to_env: bool = True) -> Optional[str]`**
- Retrieve a secret
- Falls back to environment if `fallback_to_env=True`
- Updates last accessed timestamp

**`delete_secret(provider: str) -> bool`**
- Delete a secret
- Removes from keyring and file storage
- Removes metadata

**`list_secrets() -> List[Dict]`**
- List all secrets (without values)
- Includes storage type and timestamps
- Shows environment variables

**`get_all_provider_keys() -> Dict[str, Optional[str]]`**
- Get all provider keys at once
- Returns dict: `{'anthropic': 'sk-ant-...', 'openai': 'sk-...', ...}`

**`test_secret(provider: str) -> bool`**
- Test if a secret can be retrieved
- Returns True if accessible

---

## Next Steps

1. **Run setup**: `python3 setup_keys.py`
2. **Test the demo**: `python3 examples/test_routing_v2.py`
3. **Start using Polly** with cloud providers!

For more information, see `PHASE11A_IMPLEMENTATION.md`.
