#!/usr/bin/env python3
"""
End-to-end test for File System integration with LLM parsing.
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.filesystem import FileSystemIntegration
from integrations.filesystem_llm import FileSystemLLMParser, parse_filesystem_request


class MockLLM:
    """Mock LLM for testing."""
    
    def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Return a mock response."""
        # Simple pattern matching for test cases
        if "organize" in prompt.lower() and "downloads" in prompt.lower():
            return """{
  "understood": "Create folders for different file types in Downloads and move files accordingly",
  "operations": [
    {"type": "create_folder", "params": {"path": "~/Desktop/polly_test/organized/PDFs", "parents": true}},
    {"type": "create_folder", "params": {"path": "~/Desktop/polly_test/organized/Images", "parents": true}},
    {"type": "batch_organize", "params": {
      "source_dir": "~/Desktop/polly_test",
      "rules": [
        {"pattern": "*.pdf", "action": "tag", "tags": ["documents", "blue"]},
        {"pattern": "*.{jpg,png}", "action": "tag", "tags": ["images", "green"]}
      ]
    }}
  ],
  "dry_run": true,
  "requires_confirmation": true,
  "warnings": []
}"""
        
        elif "tag" in prompt.lower() and "pdf" in prompt.lower():
            return """{
  "understood": "Add 'work' and blue tags to all PDF files",
  "operations": [
    {"type": "batch_organize", "params": {
      "source_dir": "~/Desktop/polly_test",
      "rules": [
        {"pattern": "*.pdf", "action": "tag", "tags": ["work", "blue"]}
      ]
    }}
  ],
  "dry_run": true,
  "requires_confirmation": false,
  "warnings": []
}"""
        
        else:
            return """{
  "understood": "Create a test folder",
  "operations": [
    {"type": "create_folder", "params": {"path": "~/Desktop/polly_test/llm_test", "parents": true}}
  ],
  "dry_run": true,
  "requires_confirmation": false,
  "warnings": []
}"""


async def test_filesystem_llm():
    """Test file system integration with LLM parsing."""
    
    print("=== File System LLM Integration Test ===\n")
    
    # Initialize
    mock_llm = MockLLM()
    fs = FileSystemIntegration(config={"dry_run": False})
    await fs.connect()
    
    print("✅ Initialized filesystem and mock LLM\n")
    
    # Test 1: Simple folder creation
    print("TEST 1: Parse simple folder creation request")
    print("-" * 50)
    request = "Create a test folder on my desktop"
    plan = parse_filesystem_request(mock_llm, request)
    
    print(f"Request: {request}")
    print(f"Understood: {plan.get('understood')}")
    print(f"Operations: {len(plan.get('operations', []))}")
    for op in plan.get('operations', []):
        print(f"  - {op['type']}: {op['params']}")
    print()
    
    # Test 2: Complex organization
    print("TEST 2: Parse complex organization request")
    print("-" * 50)
    request = "Organize my downloads folder by file type"
    plan = parse_filesystem_request(mock_llm, request, context={"current_dir": "~/Desktop/polly_test"})
    
    print(f"Request: {request}")
    print(f"Understood: {plan.get('understood')}")
    print(f"Operations: {len(plan.get('operations', []))}")
    
    parser = FileSystemLLMParser(mock_llm)
    explanation = parser.explain_operations(plan.get('operations', []))
    print(f"\nExplanation:\n{explanation}\n")
    
    # Test 3: Validation
    print("TEST 3: Validate operations")
    print("-" * 50)
    validation = parser.validate_operations(plan.get('operations', []))
    print(f"Valid: {validation['valid']}")
    print(f"Errors: {validation['errors']}")
    print(f"Warnings: {validation['warnings']}")
    print()
    
    # Test 4: Execute operations (dry-run)
    print("TEST 4: Execute operations in dry-run mode")
    print("-" * 50)
    
    # Create test directory and files
    test_dir = Path.home() / "Desktop" / "polly_test"
    test_dir.mkdir(exist_ok=True)
    
    # Create test PDF
    test_pdf = test_dir / "test_document.pdf"
    test_pdf.write_text("Mock PDF content")
    
    # Create test image
    test_img = test_dir / "test_image.png"
    test_img.write_text("Mock image content")
    
    print(f"Created test files in {test_dir}")
    
    fs.dry_run = True  # Enable dry-run mode
    
    for i, op in enumerate(plan.get('operations', []), 1):
        op_type = op.get('type')
        params = op.get('params', {})
        
        print(f"\nOperation {i}: {op_type}")
        
        try:
            if op_type == "create_folder":
                result = fs.create_folder(**params)
            elif op_type == "batch_organize":
                result = fs.batch_organize(**params)
            else:
                result = {"success": False, "error": f"Unknown type: {op_type}"}
            
            print(f"  Result: {result.get('success')}")
            if result.get('dry_run'):
                print(f"  [DRY RUN] {result.get('message', 'N/A')}")
            if result.get('actions'):
                print(f"  Actions planned: {len(result['actions'])}")
                for action in result['actions'][:3]:  # Show first 3
                    print(f"    - {action}")
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\n✅ All tests completed!")
    print(f"\nTest directory: {test_dir}")
    print("Note: Operations were run in dry-run mode (no actual changes)")


if __name__ == "__main__":
    asyncio.run(test_filesystem_llm())
