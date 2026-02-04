#!/usr/bin/env python3
"""
Migration script to compress pattern storage (Phase 2b)

This script:
1. Backs up existing patterns.json
2. Creates compressed version (patterns.json.compressed)
3. Verifies integrity
4. Optionally switches to compressed format

Usage:
    python scripts/migrate_patterns_to_compressed.py [--switch]
    
Options:
    --switch    Make compressed format the primary storage (advanced)
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from learners.patterns import PatternLearner


def backup_patterns(patterns_path: Path) -> Path:
    """Create timestamped backup of patterns file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = patterns_path.parent / f'patterns.backup.{timestamp}.json'
    
    if patterns_path.exists():
        shutil.copy2(patterns_path, backup_path)
        print(f"✓ Created backup: {backup_path}")
        return backup_path
    else:
        print(f"⚠ No patterns file found at {patterns_path}")
        return None


def verify_compression(pl: PatternLearner, patterns_path: Path) -> bool:
    """Verify compressed file can be loaded and matches original"""
    # Store original counts
    orig_patterns = len(pl.patterns)
    orig_qp = len(pl.query_patterns)
    orig_qcp = len(pl.query_chunk_patterns)
    orig_dpp = len(pl.domain_priority_patterns)
    orig_pwp = len(pl.project_workflow_patterns)
    
    print("\nOriginal pattern counts:")
    print(f"  Legacy patterns: {orig_patterns}")
    print(f"  Query patterns: {orig_qp}")
    print(f"  Query→Chunk patterns: {orig_qcp}")
    print(f"  Domain priority patterns: {orig_dpp}")
    print(f"  Project workflow patterns: {orig_pwp}")
    print(f"  Total: {orig_patterns + orig_qp + orig_qcp + orig_dpp + orig_pwp}")
    
    # Load compressed
    result = pl.load_patterns_from_compressed()
    
    if not result['success']:
        print(f"✗ Failed to load compressed patterns: {result.get('error')}")
        return False
    
    # Verify counts match
    print("\nLoaded pattern counts:")
    print(f"  Legacy patterns: {len(pl.patterns)}")
    print(f"  Query patterns: {len(pl.query_patterns)}")
    print(f"  Query→Chunk patterns: {len(pl.query_chunk_patterns)}")
    print(f"  Domain priority patterns: {len(pl.domain_priority_patterns)}")
    print(f"  Project workflow patterns: {len(pl.project_workflow_patterns)}")
    print(f"  Total: {result['patterns_loaded']}")
    
    if (len(pl.patterns) != orig_patterns or
        len(pl.query_patterns) != orig_qp or
        len(pl.query_chunk_patterns) != orig_qcp or
        len(pl.domain_priority_patterns) != orig_dpp or
        len(pl.project_workflow_patterns) != orig_pwp):
        print("\n✗ Pattern count mismatch!")
        return False
    
    print("\n✓ All patterns verified successfully")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Migrate patterns.json to compressed format'
    )
    parser.add_argument(
        '--switch',
        action='store_true',
        help='Make compressed format the primary storage (renames files)'
    )
    parser.add_argument(
        '--patterns-path',
        type=Path,
        default=Path.home() / '.polly' / 'patterns.json',
        help='Path to patterns.json file'
    )
    
    args = parser.parse_args()
    patterns_path = args.patterns_path.expanduser()
    compressed_path = patterns_path.with_suffix('.json.compressed')
    
    print("=" * 60)
    print("Pattern Storage Migration (Phase 2b)")
    print("=" * 60)
    print()
    
    # Check if patterns file exists
    if not patterns_path.exists():
        print(f"✗ Patterns file not found: {patterns_path}")
        print("  Nothing to migrate.")
        return 1
    
    # Load patterns
    print(f"Loading patterns from {patterns_path}...")
    pl = PatternLearner(patterns_path)
    
    # Check current size
    orig_size = patterns_path.stat().st_size
    print(f"Current file size: {orig_size:,} bytes ({orig_size/1024:.1f} KB)")
    print()
    
    # Create backup
    print("Step 1: Creating backup...")
    backup_path = backup_patterns(patterns_path)
    print()
    
    # Compress
    print("Step 2: Creating compressed version...")
    result = pl.save_patterns_compressed()
    
    new_size = result['compressed_size']
    ratio = result['ratio']
    savings = orig_size - new_size
    
    print(f"✓ Compressed to: {compressed_path}")
    print(f"  Original size: {orig_size:,} bytes")
    print(f"  Compressed size: {new_size:,} bytes")
    print(f"  Compression ratio: {ratio:.1f}x")
    print(f"  Space saved: {savings:,} bytes ({savings/1024:.1f} KB)")
    print()
    
    # Verify
    print("Step 3: Verifying integrity...")
    if not verify_compression(pl, patterns_path):
        print("\n✗ Verification failed!")
        print(f"  Compressed file: {compressed_path}")
        print(f"  Backup available: {backup_path}")
        return 1
    print()
    
    # Switch if requested
    if args.switch:
        print("Step 4: Switching to compressed format...")
        old_uncompressed = patterns_path.with_suffix('.json.uncompressed')
        
        # Rename original to .uncompressed
        shutil.move(patterns_path, old_uncompressed)
        print(f"  Renamed {patterns_path.name} → {old_uncompressed.name}")
        
        # Rename compressed to main file
        shutil.move(compressed_path, patterns_path)
        print(f"  Renamed {compressed_path.name} → {patterns_path.name}")
        
        print()
        print("✓ Switched to compressed format")
        print(f"  Primary file: {patterns_path}")
        print(f"  Old format: {old_uncompressed}")
        print(f"  Backup: {backup_path}")
    else:
        print("Step 4: Keeping both formats...")
        print(f"  Uncompressed (current): {patterns_path}")
        print(f"  Compressed (new): {compressed_path}")
        print()
        print("To switch to compressed format, run:")
        print(f"  python {__file__} --switch")
    
    print()
    print("=" * 60)
    print("Migration complete!")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
