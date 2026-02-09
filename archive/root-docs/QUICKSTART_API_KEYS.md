# Quick Start: API Key Setup for Polly

## Step 1: Install Dependencies

First, install the required packages (keyring and cryptography):

```bash
cd /Users/brettgershon/polly
pip3 install keyring cryptography
```

Or install everything from requirements.txt:

```bash
pip3 install -r requirements.txt
```

## Step 2: Run the Setup Script

The easiest way to add API keys is to use the interactive setup script:

```bash
python3 setup_keys.py
```

This will guide you through:
1. Adding your Anthropic (Claude) API key
2. Adding your OpenAI (GPT) API key  
3. Optionally adding GitHub token (not yet supported)

Each key will be:
- Validated for correct format
- Tested with a real API call
- Stored securely in your system keyring

## Step 3: Test the Router

Once keys are added, test the routing system:

```bash
python3 examples/test_routing_v2.py
```

You should see output like:

```
============================================================
Phase 11a: Multi-Provider Intelligent Routing Demo
============================================================

1. Initializing Budget Manager...
   Daily budget: $0.00 / $10.00
   Monthly budget: $0.00 / $200.00

2. Initializing Router with Providers...

3. Validating Provider Credentials...
   ✓ anthropic: available
   ✓ openai: available

4. Testing Routing Decisions...
   ...
```

## Alternative: Using CLI Commands

You can also manage keys directly with CLI commands:

```bash
# Add a key (will prompt securely)
python3 -m interfaces.cli keys set anthropic

# List all keys
python3 -m interfaces.cli keys list

# Test keys
python3 -m interfaces.cli keys test

# Delete a key
python3 -m interfaces.cli keys delete anthropic
```

## Where to Get API Keys

### Anthropic (Claude) - Recommended
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to "API Keys"
4. Click "Create Key"
5. Copy the key (starts with `sk-ant-`)

### OpenAI (GPT) - Optional
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to "API Keys"
4. Click "Create new secret key"
5. Copy the key (starts with `sk-`)

## Security

Keys are stored securely:
- **macOS**: In Keychain Access (same place as your passwords)
- **Windows**: In Credential Vault
- **Linux**: In Secret Service (GNOME Keyring, KWallet, etc.)

If keyring is unavailable, keys are stored in an encrypted file at `~/.polly/secrets/secrets.enc`.

## Troubleshooting

### "No module named 'cryptography'"

Install dependencies:
```bash
pip3 install keyring cryptography
```

### "No API keys found in environment"

This is expected! The test script checks environment variables first. Run the setup script to add keys to secure storage:
```bash
python3 setup_keys.py
```

### "Connection test failed"

Possible causes:
- Invalid API key
- Network issues
- Provider API temporarily down

Try running the test again:
```bash
python3 -m interfaces.cli keys test <provider>
```

## Need Help?

See the full documentation:
- `docs/API_KEYS.md` - Complete API key management guide
- `PHASE11A_IMPLEMENTATION.md` - Technical implementation details
- `examples/test_routing_v2.py` - Example usage

Or ask Polly! Once configured:
```bash
python3 -m interfaces.cli "How do I use the routing system?"
```
