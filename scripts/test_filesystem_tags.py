#!/usr/bin/env python3
"""
Test script for FileSystem integration - specifically tag operations.
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.filesystem import FileSystemIntegration


async def test_tags():
    """Test tag operations with real files."""
    
    print("=== File System Tag Operations Test ===\n")
    
    # Initialize filesystem integration (NOT in dry-run mode)
    fs = FileSystemIntegration(config={"dry_run": False})
    
    # Connect
    print("1. Connecting to filesystem...")
    await fs.connect()
    print(f"   Status: {fs.status}\n")
    
    # Create a test file
    test_dir = Path.home() / "Desktop" / "polly_test"
    test_dir.mkdir(exist_ok=True)
    test_file = test_dir / "test_tags.txt"
    test_file.write_text("This is a test file for tag operations.")
    
    print(f"2. Created test file: {test_file}\n")
    
    # Add tags
    print("3. Adding tags ['work', 'blue', 'important']...")
    result = fs.add_tags(str(test_file), ["work", "blue", "important"])
    print(f"   Result: {result}\n")
    
    # Get tags
    print("4. Getting tags...")
    result = fs.get_tags(str(test_file))
    print(f"   Result: {result}\n")
    
    # Add more tags
    print("5. Adding additional tags ['python', 'red']...")
    result = fs.add_tags(str(test_file), ["python", "red"])
    print(f"   Result: {result}\n")
    
    # Get tags again
    print("6. Getting all tags...")
    result = fs.get_tags(str(test_file))
    print(f"   Result: {result}\n")
    
    # Search by tags
    print("7. Searching for files with 'work' tag on Desktop...")
    result = fs.find_by_tags(["work"], str(Path.home() / "Desktop"))
    print(f"   Found {result.get('count', 0)} files:")
    for file in result.get('files', [])[:5]:  # Show first 5
        print(f"     - {file}")
    print()
    
    # Test with folder
    test_folder = test_dir / "tagged_folder"
    test_folder.mkdir(exist_ok=True)
    
    print(f"8. Created test folder: {test_folder}")
    print("   Adding tags ['project', 'green']...")
    result = fs.add_tags(str(test_folder), ["project", "green"])
    print(f"   Result: {result}\n")
    
    print("9. Getting folder tags...")
    result = fs.get_tags(str(test_folder))
    print(f"   Result: {result}\n")
    
    # Operation history
    print("10. Operation history:")
    history = fs.get_operation_history(limit=10)
    for i, op in enumerate(history, 1):
        print(f"    {i}. {op['action']} - {op.get('path', 'N/A')} - {op['timestamp']}")
    
    print("\n✅ Tag operations test complete!")
    print(f"\nTest files created in: {test_dir}")
    print("You can check the tags in Finder to verify they're visible.")


if __name__ == "__main__":
    asyncio.run(test_tags())
