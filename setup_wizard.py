#!/usr/bin/env python3
"""
Polly First-Run Setup Wizard
Phase 1.5 Day 6: Interactive CLI wizard for domain configuration

This wizard helps new users set up their domains quickly:
1. Detects if this is a first run (no domains.json exists)
2. Offers quick start (3 domains) or template selection
3. Creates domains.json configuration
4. Optionally creates domain folders

Usage:
    python setup_wizard.py              # Interactive wizard
    python setup_wizard.py --quick      # Quick start (skip prompts)
    python setup_wizard.py --template software-development
"""

import sys
import os
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.domain_config import (
    is_first_run,
    create_quick_start_domains,
    save_domains,
    DOMAINS_CONFIG_PATH,
    DomainsConfig
)
from core.domain_templates import (
    list_templates,
    create_from_template,
    TEMPLATES
)


def print_header():
    """Print wizard header."""
    print("\n" + "=" * 60)
    print("   Polly Setup Wizard - Domain Configuration")
    print("=" * 60 + "\n")


def print_separator():
    """Print separator line."""
    print("\n" + "-" * 60 + "\n")


def check_existing_config() -> bool:
    """
    Check if domains.json already exists.
    
    Returns:
        True if this is a first run, False if config exists
    """
    if not is_first_run():
        print(f"⚠️  Domains configuration already exists at:")
        print(f"   {DOMAINS_CONFIG_PATH}")
        print()
        response = input("Overwrite existing configuration? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("\n✓ Setup cancelled. Existing configuration preserved.")
            return False
    return True


def show_quick_start_option():
    """Show quick start option and get user choice."""
    print("Quick Start Option:")
    print("  Get started quickly with 3 basic domains:")
    print("  💼 Work - Work projects and professional tasks")
    print("  🏠 Personal - Personal notes and life organization")
    print("  📚 Learning - Study notes and skills development")
    print()


def show_template_options():
    """Show available templates and their descriptions."""
    print("Template Options:")
    print("  Choose a pre-configured template for your use case:")
    print()
    
    templates = list_templates()
    for i, template in enumerate(templates, 1):
        print(f"  {i}. {template['name']}")
        print(f"     {template['description']}")
        print(f"     Domains: {', '.join(template['domains'])}")
        print()


def get_setup_choice() -> tuple[str, Optional[str]]:
    """
    Get user's setup choice.
    
    Returns:
        Tuple of (choice_type, template_id)
        choice_type: 'quick', 'template', or 'cancel'
        template_id: None for quick/cancel, template ID for template choice
    """
    while True:
        print("Setup Options:")
        print("  [1] Quick Start (3 domains)")
        print("  [2] Choose Template (5 domains)")
        print("  [q] Cancel")
        print()
        
        choice = input("Select an option [1/2/q]: ").strip().lower()
        
        if choice in ['q', 'quit', 'exit', 'cancel']:
            return ('cancel', None)
        
        if choice == '1':
            return ('quick', None)
        
        if choice == '2':
            # Show templates and get selection
            print_separator()
            show_template_options()
            
            templates = list_templates()
            while True:
                template_choice = input(f"Select template [1-{len(templates)}] or 'b' to go back: ").strip().lower()
                
                if template_choice in ['b', 'back']:
                    print_separator()
                    return get_setup_choice()  # Recursive call to show main menu
                
                try:
                    template_idx = int(template_choice) - 1
                    if 0 <= template_idx < len(templates):
                        return ('template', templates[template_idx]['id'])
                    else:
                        print(f"❌ Invalid choice. Please enter 1-{len(templates)}")
                except ValueError:
                    print(f"❌ Invalid input. Please enter a number 1-{len(templates)} or 'b'")
        
        print("❌ Invalid choice. Please enter 1, 2, or q\n")


def confirm_selection(config: DomainsConfig, choice_type: str) -> bool:
    """
    Show domains and confirm selection.
    
    Args:
        config: DomainsConfig to preview
        choice_type: 'quick' or 'template'
    
    Returns:
        True if user confirms, False otherwise
    """
    print_separator()
    print(f"Preview: {len(config.domains)} domains will be created")
    print()
    
    for domain in config.domains:
        print(f"  {domain.icon} {domain.name}")
        print(f"     {domain.description}")
        print(f"     Folder: {domain.folder_path}")
        print(f"     RAG Weight: {domain.rag_weight:.2f}")
        print()
    
    response = input("Create these domains? (Y/n): ").strip().lower()
    return response in ['', 'y', 'yes']


def create_domain_folders(config: DomainsConfig, base_path: Optional[Path] = None) -> bool:
    """
    Optionally create domain folders on disk.
    
    Args:
        config: DomainsConfig with domains
        base_path: Base path for folders (defaults to ~/Documents/Polly)
    
    Returns:
        True if folders were created, False if skipped
    """
    print_separator()
    print("Domain Folders:")
    print("  Would you like to create folders for your domains?")
    print()
    
    if base_path is None:
        default_base = Path.home() / "Documents" / "Polly"
        base_input = input(f"Base folder path (default: {default_base}): ").strip()
        base_path = Path(base_input) if base_input else default_base
    
    print(f"\n  Folders will be created at: {base_path}")
    print()
    for domain in config.domains:
        folder_path = base_path / domain.folder_path
        print(f"    {folder_path}")
    print()
    
    response = input("Create folders? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("\n✓ Skipping folder creation")
        return False
    
    # Create folders
    try:
        base_path.mkdir(parents=True, exist_ok=True)
        for domain in config.domains:
            folder_path = base_path / domain.folder_path
            folder_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ Created {folder_path}")
        print("\n✓ All folders created successfully")
        return True
    except Exception as e:
        print(f"\n❌ Error creating folders: {e}")
        return False


def run_wizard_interactive():
    """Run the interactive setup wizard."""
    print_header()
    
    # Check if config already exists
    if not check_existing_config():
        return
    
    print("Welcome to Polly! Let's set up your domains.")
    print()
    print("Domains organize your knowledge into categories (like folders)")
    print("and help Polly understand which information is most relevant")
    print("when answering your questions.")
    
    print_separator()
    
    # Show options
    show_quick_start_option()
    print_separator()
    show_template_options()
    print_separator()
    
    # Get user choice
    choice_type, template_id = get_setup_choice()
    
    if choice_type == 'cancel':
        print("\n✓ Setup cancelled.")
        return
    
    # Create config based on choice
    if choice_type == 'quick':
        print("\n✓ Creating Quick Start domains...")
        config = create_quick_start_domains()
    else:  # template
        template_name = TEMPLATES[template_id]['name']
        print(f"\n✓ Creating {template_name} domains...")
        config = create_from_template(template_id)
    
    # Confirm selection
    if not confirm_selection(config, choice_type):
        print("\n✓ Setup cancelled.")
        return
    
    # Save configuration
    try:
        save_domains(config, create_backup=False)
        print(f"\n✓ Configuration saved to {DOMAINS_CONFIG_PATH}")
    except Exception as e:
        print(f"\n❌ Error saving configuration: {e}")
        return
    
    # Optionally create folders
    create_domain_folders(config)
    
    # Success message
    print_separator()
    print("✓ Setup complete! Your domains are ready.")
    print()
    print("Next steps:")
    print("  1. Run Polly and start adding content to your domains")
    print("  2. Use domain-specific queries like 'search in Work: project status'")
    print("  3. Customize domains anytime in Settings")
    print()


def run_wizard_quick():
    """Run quick setup (no prompts)."""
    print_header()
    print("Quick Setup: Creating 3 basic domains...")
    
    config = create_quick_start_domains()
    
    try:
        save_domains(config, create_backup=False)
        print(f"\n✓ Configuration saved to {DOMAINS_CONFIG_PATH}")
        print(f"✓ Created {len(config.domains)} domains:")
        for domain in config.domains:
            print(f"  {domain.icon} {domain.name}")
        print("\n✓ Setup complete!")
    except Exception as e:
        print(f"\n❌ Error saving configuration: {e}")
        sys.exit(1)


def run_wizard_template(template_id: str):
    """Run setup with a specific template."""
    print_header()
    
    try:
        template_name = TEMPLATES[template_id]['name']
        print(f"Template Setup: Creating {template_name} domains...")
        
        config = create_from_template(template_id)
        
        save_domains(config, create_backup=False)
        print(f"\n✓ Configuration saved to {DOMAINS_CONFIG_PATH}")
        print(f"✓ Created {len(config.domains)} domains:")
        for domain in config.domains:
            print(f"  {domain.icon} {domain.name}")
        print("\n✓ Setup complete!")
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print(f"Available templates: {', '.join(TEMPLATES.keys())}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error saving configuration: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Polly First-Run Setup Wizard',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup_wizard.py                    # Interactive wizard
  python setup_wizard.py --quick            # Quick start (3 domains)
  python setup_wizard.py --template software-development
  python setup_wizard.py --list-templates   # List available templates
        """
    )
    
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Quick setup with 3 basic domains (no prompts)'
    )
    
    parser.add_argument(
        '--template',
        type=str,
        metavar='TEMPLATE_ID',
        help='Create domains from a template (e.g., software-development)'
    )
    
    parser.add_argument(
        '--list-templates',
        action='store_true',
        help='List available templates and exit'
    )
    
    args = parser.parse_args()
    
    # List templates
    if args.list_templates:
        print("\nAvailable Templates:")
        print("=" * 60)
        for template in list_templates():
            print(f"\n{template['id']}")
            print(f"  Name: {template['name']}")
            print(f"  Description: {template['description']}")
            print(f"  Domains ({template['domains_count']}): {', '.join(template['domains'])}")
        print("\n")
        return
    
    # Quick setup
    if args.quick:
        run_wizard_quick()
        return
    
    # Template setup
    if args.template:
        run_wizard_template(args.template)
        return
    
    # Interactive wizard (default)
    run_wizard_interactive()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✓ Setup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
