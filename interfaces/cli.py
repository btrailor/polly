#!/usr/bin/env python3
"""
Polly CLI Interface
Query Polly from your terminal

Usage:
    polly "What patterns do I use for MIDI handling?"
    polly --mode local "Quick question"
    polly --mode cloud "Complex analysis"
    polly index                    # Index knowledge base
    polly stats                    # Show statistics
    polly chat                     # Interactive chat mode
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog='polly',
        description='Polly - Your Personal AI Assistant',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  polly "What are my audio patterns?"     Query with context
  polly --mode local "Quick help"         Force local model
  polly --mode cloud "Deep analysis"      Force cloud model
  polly index                             Index knowledge base
  polly index --force                     Force re-index all
  polly stats                             Show statistics
  polly chat                              Interactive mode
        """
    )

    parser.add_argument(
        'query',
        nargs='?',
        help='Query to send to Polly'
    )

    parser.add_argument(
        '--mode', '-m',
        choices=['local', 'cloud', 'auto'],
        default='auto',
        help='Model routing mode (default: auto)'
    )

    parser.add_argument(
        '--tier', '-t',
        choices=['fast', 'balanced', 'quality'],
        default='balanced',
        help='Model quality tier (default: balanced)'
    )

    parser.add_argument(
        '--no-stream',
        action='store_true',
        help='Disable streaming output'
    )

    parser.add_argument(
        '--config', '-c',
        type=Path,
        help='Path to config file'
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest='command')

    # Index command
    index_parser = subparsers.add_parser('index', help='Index knowledge base')
    index_parser.add_argument('--force', '-f', action='store_true', help='Force re-index all files')
    index_parser.add_argument('--obsidian-only', action='store_true', help='Only index Obsidian vault')
    index_parser.add_argument('--code-only', action='store_true', help='Only index codebases')

    # Stats command
    subparsers.add_parser('stats', help='Show Polly statistics')

    # Chat command
    chat_parser = subparsers.add_parser('chat', help='Interactive chat mode')
    chat_parser.add_argument('--mode', '-m', choices=['local', 'cloud', 'auto'], default='auto')

    # Serve command
    serve_parser = subparsers.add_parser('serve', help='Start Polly server')
    serve_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    serve_parser.add_argument('--port', '-p', type=int, default=11436, help='Port to listen on')

    # Keys command - API key management
    keys_parser = subparsers.add_parser('keys', help='Manage API keys')
    keys_subparsers = keys_parser.add_subparsers(dest='keys_command')
    
    # keys list
    keys_subparsers.add_parser('list', help='List all API keys (masked)')
    
    # keys set
    keys_set_parser = keys_subparsers.add_parser('set', help='Set an API key')
    keys_set_parser.add_argument('provider', choices=['anthropic', 'openai', 'github'], help='Provider name')
    keys_set_parser.add_argument('--key', '-k', help='API key (if not provided, will prompt securely)')
    
    # keys delete
    keys_delete_parser = keys_subparsers.add_parser('delete', help='Delete an API key')
    keys_delete_parser.add_argument('provider', choices=['anthropic', 'openai', 'github'], help='Provider name')
    
    # keys test
    keys_test_parser = keys_subparsers.add_parser('test', help='Test API key connectivity')
    keys_test_parser.add_argument('provider', nargs='?', choices=['anthropic', 'openai', 'github'], help='Provider to test (tests all if not specified)')

    return parser


async def handle_query(args, polly):
    """Handle a single query."""
    from core.router import RoutingMode, ModelTier

    mode_map = {
        'local': RoutingMode.LOCAL,
        'cloud': RoutingMode.CLOUD,
        'auto': RoutingMode.AUTO
    }

    tier_map = {
        'fast': ModelTier.FAST,
        'balanced': ModelTier.BALANCED,
        'quality': ModelTier.QUALITY
    }

    response = ""
    async for chunk in polly.query(
        args.query,
        mode=mode_map[args.mode],
        tier=tier_map[args.tier],
        stream=not args.no_stream
    ):
        response += chunk
        if not args.no_stream:
            print(chunk, end='', flush=True)

    if not args.no_stream:
        print()  # Final newline
    else:
        print(response)


async def handle_index(args, polly):
    """Handle index command."""
    print("Indexing knowledge base...")

    obsidian = not args.code_only if hasattr(args, 'code_only') else True
    codebases = not args.obsidian_only if hasattr(args, 'obsidian_only') else True
    force = args.force if hasattr(args, 'force') else False

    results = await polly.index(
        obsidian=obsidian,
        codebases=codebases,
        force=force
    )

    print("\nIndexing complete:")
    for source, count in results.items():
        print(f"  {source}: {count} files")


def handle_stats(polly):
    """Handle stats command."""
    stats = polly.get_stats()

    print(f"\n=== Polly Statistics ===")
    print(f"User: {stats['user']}")
    print(f"Session started: {stats['session_start']}")
    print(f"Conversation length: {stats['conversation_length']} messages")

    print(f"\n--- RAG Database ---")
    for source, info in stats['rag'].items():
        print(f"  {source}: {info['count']} chunks")

    if 'patterns' in stats:
        print(f"\n--- Learned Patterns ---")
        print(f"  Total patterns: {stats['patterns']}")

    if 'graph' in stats:
        print(f"\n--- Knowledge Graph ---")
        print(f"  Entities: {stats['graph']['entities']}")
        print(f"  Relationships: {stats['graph']['relationships']}")


async def handle_chat(args, polly):
    """Handle interactive chat mode."""
    from core.router import RoutingMode

    mode_map = {
        'local': RoutingMode.LOCAL,
        'cloud': RoutingMode.CLOUD,
        'auto': RoutingMode.AUTO
    }

    print(f"\n=== Polly Chat ===")
    print(f"Mode: {args.mode}")
    print("Type 'quit' to exit, 'clear' to clear history, 'stats' for statistics\n")

    while True:
        try:
            query = input("You: ").strip()

            if not query:
                continue

            if query.lower() == 'quit':
                polly.save_state()
                print("Goodbye!")
                break

            if query.lower() == 'clear':
                polly.clear_conversation()
                print("Conversation cleared.\n")
                continue

            if query.lower() == 'stats':
                handle_stats(polly)
                continue

            print("\nPolly: ", end='', flush=True)

            async for chunk in polly.query(
                query,
                mode=mode_map[args.mode],
                stream=True
            ):
                print(chunk, end='', flush=True)

            print("\n")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Saving state...")
            polly.save_state()
            break
        except EOFError:
            break


async def handle_serve(args, polly):
    """Handle serve command - start the API server."""
    from .server import create_app
    import uvicorn

    app = create_app(polly)

    print(f"\n=== Polly Server ===")
    print(f"Starting on http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop\n")

    config = uvicorn.Config(app, host=args.host, port=args.port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def handle_keys(args):
    """Handle API key management commands."""
    from core.secrets_manager import get_secrets_manager
    import getpass
    
    secrets = get_secrets_manager()
    
    if not args.keys_command:
        print("Usage: polly keys {list|set|delete|test}")
        return
    
    if args.keys_command == 'list':
        # List all keys
        print("\n=== API Keys ===\n")
        
        keys_list = secrets.list_secrets()
        
        for item in keys_list:
            status = "✓" if item['is_set'] else "✗"
            provider = item['provider'].title()
            
            if item['is_set']:
                storage = item['storage_type'] or 'unknown'
                if storage == 'keyring':
                    storage_label = "🔐 Keyring"
                elif storage == 'file':
                    storage_label = "📁 Encrypted File"
                elif storage == 'environment':
                    storage_label = "🌍 Environment"
                else:
                    storage_label = storage
                
                print(f"{status} {provider:12} [{storage_label}]")
                print(f"   {item['description']}")
                if item['last_accessed']:
                    print(f"   Last used: {item['last_accessed']}")
            else:
                print(f"{status} {provider:12} [Not Set]")
                print(f"   {item['description']}")
            
            print()
    
    elif args.keys_command == 'set':
        # Set a key
        provider = args.provider
        config = secrets.get_provider_config(provider)
        
        if not config:
            print(f"Error: Unknown provider '{provider}'")
            return
        
        print(f"\n=== Set {provider.title()} API Key ===\n")
        print(f"Description: {config['description']}")
        print(f"Format: {config['format']}\n")
        
        # Get key value
        if args.key:
            key_value = args.key
        else:
            # Prompt securely
            key_value = getpass.getpass(f"Enter {provider.title()} API key: ")
        
        if not key_value:
            print("Error: No key provided")
            return
        
        # Store the key
        try:
            secrets.set_secret(provider, key_value)
            print(f"✓ {provider.title()} API key saved securely")
            
            # Test the key
            print("\nTesting key...")
            if await test_provider_key(provider, key_value):
                print(f"✓ {provider.title()} API key is valid and working!")
            else:
                print(f"⚠️  Key saved but validation failed. Please check the key.")
        
        except Exception as e:
            print(f"✗ Error saving key: {e}")
    
    elif args.keys_command == 'delete':
        # Delete a key
        provider = args.provider
        
        print(f"\n=== Delete {provider.title()} API Key ===\n")
        
        # Confirm
        confirm = input(f"Delete {provider.title()} API key? (yes/no): ")
        if confirm.lower() not in ['yes', 'y']:
            print("Cancelled")
            return
        
        if secrets.delete_secret(provider):
            print(f"✓ {provider.title()} API key deleted")
        else:
            print(f"✗ {provider.title()} API key not found")
    
    elif args.keys_command == 'test':
        # Test keys
        if args.provider:
            providers = [args.provider]
        else:
            providers = ['anthropic', 'openai', 'github']
        
        print("\n=== Testing API Keys ===\n")
        
        for provider in providers:
            key = secrets.get_secret(provider, fallback_to_env=True)
            
            if not key:
                print(f"✗ {provider.title():12} - Not configured")
                continue
            
            print(f"⏳ {provider.title():12} - Testing...", end='', flush=True)
            
            if await test_provider_key(provider, key):
                print(f"\r✓ {provider.title():12} - Working!")
            else:
                print(f"\r✗ {provider.title():12} - Failed")
        
        print()


async def test_provider_key(provider: str, key: str) -> bool:
    """Test if a provider API key is valid."""
    try:
        if provider == 'anthropic':
            from core.providers.anthropic_provider import AnthropicAdapter
            adapter = AnthropicAdapter(key)
            return await adapter.validate_credentials()
        
        elif provider == 'openai':
            from core.providers.openai_provider import OpenAIAdapter
            adapter = OpenAIAdapter(key)
            return await adapter.validate_credentials()
        
        elif provider == 'github':
            # TODO: Implement GitHub validation in Phase 11b
            return False
        
        return False
    except Exception as e:
        return False


async def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Handle keys command without initializing Polly
    if args.command == 'keys':
        await handle_keys(args)
        return

    # Late import to avoid circular imports
    from core.config import load_config
    from core.polly import Polly

    # Load config
    if args.config:
        load_config(args.config)

    # Initialize Polly
    try:
        polly = Polly()
    except Exception as e:
        print(f"Error initializing Polly: {e}", file=sys.stderr)
        print("\nMake sure Ollama is running: ollama serve", file=sys.stderr)
        sys.exit(1)

    # Check router availability
    await polly.router.check_availability()

    # Handle commands
    if args.command == 'index':
        await handle_index(args, polly)
    elif args.command == 'stats':
        handle_stats(polly)
    elif args.command == 'chat':
        await handle_chat(args, polly)
    elif args.command == 'serve':
        await handle_serve(args, polly)
    elif args.query:
        await handle_query(args, polly)
    else:
        parser.print_help()


def cli_main():
    """Entry point for CLI."""
    asyncio.run(main())


if __name__ == '__main__':
    cli_main()
