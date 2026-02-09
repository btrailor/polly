#!/usr/bin/env python3
"""
Migrate existing patterns.json to Mem0

This script migrates patterns from the local JSON file to Mem0's
adaptive memory system, preserving all metadata and enabling
semantic pattern search.

Usage:
    python scripts/migrate_patterns_to_mem0.py [--dry-run] [--backup]

Options:
    --dry-run    Show what would be migrated without actually doing it
    --backup     Create backup of patterns.json (default: True)
    --no-backup  Skip backup creation
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.memory.mem0_adapter import Mem0Adapter
from core.pattern_learning import Pattern
import yaml

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def load_config() -> dict:
    """Load Polly configuration."""
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    
    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        sys.exit(1)
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    return config


def check_mem0_enabled(config: dict) -> bool:
    """Check if Mem0 is enabled in config."""
    if config.get('memory', {}).get('provider') != 'mem0':
        logger.error("Memory provider is not set to 'mem0' in config.yaml")
        return False
    
    if not config.get('memory', {}).get('mem0', {}).get('enabled', False):
        logger.error("Mem0 is not enabled in config.yaml (memory.mem0.enabled: false)")
        return False
    
    return True


def load_patterns(patterns_file: Path) -> list:
    """Load patterns from JSON file."""
    if not patterns_file.exists():
        logger.warning(f"Patterns file not found: {patterns_file}")
        return []
    
    try:
        with open(patterns_file) as f:
            patterns = json.load(f)
        logger.info(f"Loaded {len(patterns)} patterns from {patterns_file}")
        return patterns
    except Exception as e:
        logger.error(f"Failed to load patterns: {e}")
        sys.exit(1)


def create_backup(patterns_file: Path):
    """Create backup of patterns.json."""
    if not patterns_file.exists():
        return
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = patterns_file.with_suffix(f'.json.backup_{timestamp}')
    
    try:
        import shutil
        shutil.copy2(patterns_file, backup_file)
        logger.info(f"Created backup: {backup_file}")
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        sys.exit(1)


def migrate_patterns(patterns: list, mem0: Mem0Adapter, dry_run: bool = False):
    """Migrate patterns to Mem0."""
    logger.info(f"{'[DRY RUN] ' if dry_run else ''}Migrating {len(patterns)} patterns to Mem0...")
    
    migrated = 0
    failed = 0
    
    for i, pattern_dict in enumerate(patterns, 1):
        try:
            # Convert to Pattern object for validation
            pattern = Pattern.from_dict(pattern_dict)
            
            # Build memory content
            content = f"Pattern: {pattern.type} - {pattern.description}"
            
            # Build metadata
            metadata = {
                'type': 'pattern',
                'pattern_type': pattern.type,
                'confidence': pattern.confidence,
                'timestamp': pattern.timestamp,
                'occurrences': pattern.occurrences,
                'source': 'migration',
                'migrated_at': datetime.now().isoformat()
            }
            
            # Add additional metadata from pattern
            for key, value in pattern.metadata.items():
                if key not in metadata:
                    metadata[key] = str(value) if not isinstance(value, (str, int, float, bool)) else value
            
            if not dry_run:
                # Add to Mem0
                result = mem0.add_memory(
                    content=content,
                    user_id="patterns",
                    metadata=metadata
                )
                logger.debug(f"Migrated pattern {i}/{len(patterns)}: {pattern.description[:50]}... (id: {result.get('id', 'unknown')})")
            else:
                logger.debug(f"[DRY RUN] Would migrate: {pattern.type} - {pattern.description[:50]}...")
            
            migrated += 1
            
        except Exception as e:
            logger.error(f"Failed to migrate pattern {i}: {e}")
            logger.debug(f"Pattern data: {pattern_dict}")
            failed += 1
    
    return migrated, failed


def main():
    parser = argparse.ArgumentParser(
        description="Migrate patterns.json to Mem0 adaptive memory"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Show what would be migrated without actually doing it"
    )
    parser.add_argument(
        '--backup',
        action='store_true',
        default=True,
        help="Create backup of patterns.json (default: True)"
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help="Skip backup creation"
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Override backup if --no-backup specified
    if args.no_backup:
        args.backup = False
    
    logger.info("=" * 60)
    logger.info("Polly Pattern Migration: patterns.json → Mem0")
    logger.info("=" * 60)
    
    # Load config
    logger.info("Loading configuration...")
    config = load_config()
    
    # Check if Mem0 is enabled
    if not check_mem0_enabled(config):
        logger.error("\nTo enable Mem0, update config/config.yaml:")
        logger.error("  memory:")
        logger.error("    provider: mem0")
        logger.error("    mem0:")
        logger.error("      enabled: true")
        sys.exit(1)
    
    logger.info("✓ Mem0 is enabled")
    
    # Locate patterns file
    patterns_file = Path.home() / ".polly" / "patterns.json"
    logger.info(f"Patterns file: {patterns_file}")
    
    # Load patterns
    patterns = load_patterns(patterns_file)
    
    if not patterns:
        logger.info("No patterns to migrate. Exiting.")
        sys.exit(0)
    
    # Create backup
    if args.backup and not args.dry_run:
        create_backup(patterns_file)
    
    # Initialize Mem0
    logger.info("Initializing Mem0 adapter...")
    try:
        mem0 = Mem0Adapter(config)
        logger.info("✓ Mem0 adapter initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Mem0: {e}")
        sys.exit(1)
    
    # Migrate patterns
    migrated, failed = migrate_patterns(patterns, mem0, dry_run=args.dry_run)
    
    # Summary
    logger.info("=" * 60)
    logger.info("Migration Summary")
    logger.info("=" * 60)
    logger.info(f"Total patterns: {len(patterns)}")
    logger.info(f"{'Would migrate' if args.dry_run else 'Migrated'}: {migrated}")
    logger.info(f"Failed: {failed}")
    
    if args.dry_run:
        logger.info("\n[DRY RUN] No changes were made.")
        logger.info("Run without --dry-run to perform migration.")
    else:
        logger.info("\n✓ Migration complete!")
        logger.info(f"Original patterns.json preserved at: {patterns_file}")
        if args.backup:
            logger.info("Backup created for safety.")
    
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
