#!/usr/bin/env python3
"""
Quick Setup Script for Polly API Keys

This script helps you set up API keys for Polly's multi-provider routing system.
It will guide you through adding keys for Anthropic, OpenAI, and optionally GitHub.
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.secrets_manager import get_secrets_manager


def print_header():
    """Print welcome header."""
    print("=" * 60)
    print("Polly API Key Setup")
    print("=" * 60)
    print()
    print("This script will help you configure API keys for:")
    print("  • Anthropic (Claude)")
    print("  • OpenAI (GPT)")
    print("  • GitHub Copilot (optional)")
    print()
    print("Keys are stored securely using your system's keyring")
    print("(macOS Keychain, Windows Credential Vault, etc.)")
    print()


def print_provider_info(provider: str, config: dict):
    """Print information about a provider."""
    print(f"\n--- {provider.title()} ---")
    print(f"Description: {config['description']}")
    print(f"Key format: {config['format']}")
    print()


async def setup_provider(secrets, provider: str) -> bool:
    """Set up a single provider."""
    import getpass
    
    config = secrets.get_provider_config(provider)
    if not config:
        return False
    
    # Check if already set
    existing = secrets.get_secret(provider, fallback_to_env=False)
    if existing:
        print(f"✓ {provider.title()} API key is already configured")
        update = input("  Update it? (y/n): ").strip().lower()
        if update not in ['y', 'yes']:
            return True
    
    print_provider_info(provider, config)
    
    # Get the key
    key_value = getpass.getpass(f"Enter your {provider.title()} API key (or press Enter to skip): ")
    
    if not key_value:
        print(f"Skipped {provider.title()}")
        return False
    
    # Validate format
    if not secrets._validate_key_format(provider, key_value):
        print(f"⚠️  Warning: Key doesn't match expected format {config['format']}")
        proceed = input("  Continue anyway? (y/n): ").strip().lower()
        if proceed not in ['y', 'yes']:
            return False
    
    # Save the key
    try:
        secrets.set_secret(provider, key_value)
        print(f"✓ Saved {provider.title()} API key")
        
        # Test the key
        print(f"  Testing connection...", end='', flush=True)
        
        if provider == 'anthropic':
            from core.providers.anthropic_provider import AnthropicAdapter
            adapter = AnthropicAdapter(key_value)
            valid = await adapter.validate_credentials()
        elif provider == 'openai':
            from core.providers.openai_provider import OpenAIAdapter
            adapter = OpenAIAdapter(key_value)
            valid = await adapter.validate_credentials()
        else:
            valid = False
        
        if valid:
            print("\r  ✓ Connection successful!     ")
            return True
        else:
            print("\r  ✗ Connection failed          ")
            print("  The key was saved but couldn't be validated.")
            print("  Please check that the key is correct.")
            return False
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def main():
    """Main setup flow."""
    print_header()
    
    # Initialize secrets manager
    secrets = get_secrets_manager()
    
    # Setup each provider
    results = {}
    
    # Anthropic
    print("=" * 60)
    print("1. Anthropic (Claude) - Recommended")
    print("=" * 60)
    print("Get your API key from: https://console.anthropic.com/")
    results['anthropic'] = await setup_provider(secrets, 'anthropic')
    
    # OpenAI
    print("\n" + "=" * 60)
    print("2. OpenAI (GPT) - Optional but recommended")
    print("=" * 60)
    print("Get your API key from: https://platform.openai.com/api-keys")
    results['openai'] = await setup_provider(secrets, 'openai')
    
    # GitHub (optional)
    print("\n" + "=" * 60)
    print("3. GitHub Copilot - Optional (not yet implemented)")
    print("=" * 60)
    print("GitHub Copilot support coming in Phase 11b")
    skip_github = input("Skip GitHub for now? (Y/n): ").strip().lower()
    if skip_github not in ['n', 'no']:
        results['github'] = False
    else:
        print("Get a token from: https://github.com/settings/tokens")
        results['github'] = await setup_provider(secrets, 'github')
    
    # Summary
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print()
    
    configured = [name.title() for name, success in results.items() if success]
    skipped = [name.title() for name, success in results.items() if not success]
    
    if configured:
        print(f"✓ Configured: {', '.join(configured)}")
    if skipped:
        print(f"○ Skipped: {', '.join(skipped)}")
    
    print()
    print("You can manage your API keys anytime with:")
    print("  polly keys list          # View configured keys")
    print("  polly keys set <provider>  # Add/update a key")
    print("  polly keys delete <provider>  # Remove a key")
    print("  polly keys test          # Test all keys")
    print()
    
    if not any(results.values()):
        print("⚠️  No providers configured!")
        print("   Polly won't be able to use cloud models until you add keys.")
        print("   Run this script again or use 'polly keys set' to add keys.")
        print()
    else:
        print("✓ You're all set! Try testing the routing system:")
        print("  python3 examples/test_routing_v2.py")
        print()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(1)
