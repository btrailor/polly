#!/usr/bin/env python3
"""Test file system integration."""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.filesystem import FileSystemIntegration


async def main():
    print("=" * 70)
    print("Testing File System Integration")
    print("=" * 70)
    print()
    
    # Create integration in dry-run mode for testing
    fs = FileSystemIntegration(config={"dry_run": True})
    
    print("1. Connecting to file system...")
    connected = await fs.connect()
    print(f"   {'✅' if connected else '❌'} Connected: {connected}\n")
    
    # Test folder creation
    print("2. Testing folder creation...")
    test_path = "~/Desktop/polly_test_folder"
    result = fs.create_folder(test_path)
    print(f"   Result: {result}\n")
    
    # Test file moving
    print("3. Testing file move...")
    result = fs.move_file(
        "~/Desktop/test.txt",
        "~/Documents/test.txt"
    )
    print(f"   Result: {result}\n")
    
    # Test file renaming
    print("4. Testing file rename...")
    result = fs.rename_file(
        "~/Desktop/oldname.txt",
        "newname.txt"
    )
    print(f"   Result: {result}\n")
    
    # Test adding tags
    print("5. Testing macOS tags...")
    result = fs.add_tags(
        "~/Desktop",
        ["blue", "work", "important"]
    )
    print(f"   Result: {result}\n")
    
    # Test getting tags
    print("6. Testing get tags from Desktop...")
    result = fs.get_tags("~/Desktop")
    print(f"   Result: {result}\n")
    
    # Test finding by tags
    print("7. Testing find by tags...")
    result = fs.find_by_tags(["blue"], search_path="~/Desktop")
    print(f"   Found {result.get('count', 0)} files")
    if result.get('files'):
        for f in result['files'][:5]:
            print(f"     - {f}")
    print()
    
    # Test batch organization
    print("8. Testing batch organization...")
    rules = [
        {
            "pattern": "*.pdf",
            "action": "move",
            "destination": "~/Documents/PDFs"
        },
        {
            "pattern": "*.jpg",
            "action": "tag",
            "tags": ["photo", "green"]
        }
    ]
    result = fs.batch_organize("~/Downloads", rules)
    print(f"   Actions taken: {result.get('actions_count', 0)}")
    print(f"   Result: {result.get('success')}\n")
    
    # Show operation history
    print("9. Operation history:")
    history = fs.get_operation_history(limit=10)
    for i, op in enumerate(history, 1):
        print(f"   {i}. {op['action']}: {op.get('path', op.get('source', 'N/A'))}")
    
    print()
    print("=" * 70)
    print("✅ File System Integration Test Complete")
    print("=" * 70)
    print()
    print("Note: All operations were in DRY RUN mode (no actual changes made)")
    print()


if __name__ == "__main__":
    asyncio.run(main())
