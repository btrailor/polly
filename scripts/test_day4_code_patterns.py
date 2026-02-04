#!/usr/bin/env python3
"""
Day 4 Test - Code Pattern Extraction
Tests Python and JavaScript pattern detection
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from learners.code_patterns import CodePatternExtractor


def test_python_patterns():
    """Test Python code pattern extraction."""
    print("=" * 60)
    print("Python Pattern Extraction Test")
    print("=" * 60)
    
    extractor = CodePatternExtractor()
    
    # Sample Python code with various patterns
    sample_code = """
import asyncio
import json
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class UserModel:
    name: str
    email: str
    
class DataProcessor:
    \"\"\"Process data with async operations.\"\"\"
    
    def __init__(self):
        self.data = []
    
    async def process(self, data: List[str]) -> Dict:
        try:
            results = []
            for item in data:
                result = await self.process_item(item)
                results.append(result)
            return {"results": results}
        except ValueError as e:
            print(f"Error: {e}")
            raise
        except (TypeError, KeyError) as e:
            print(f"Multiple exception: {e}")
            return {}
    
    async def process_item(self, item: str):
        with open('data.json', 'r') as f:
            data = json.load(f)
        return data
    
    def get_summary(self) -> List[str]:
        return [item for item in self.data if item.startswith('A')]

@property
def status(self):
    return "active"
"""
    
    print("\n[Test 1] Extracting patterns from Python code...")
    patterns = extractor.extract_from_python(sample_code)
    
    print(f"\nFound {len(patterns)} pattern types:")
    for i, pattern in enumerate(patterns, 1):
        print(f"\n  {i}. {pattern['pattern']} ({pattern['type']})")
        
        if 'details' in pattern:
            print(f"     Details: {pattern['details']}")
        elif 'count' in pattern:
            print(f"     Count: {pattern['count']}")
        
        if 'names' in pattern:
            print(f"     Names: {pattern['names']}")
        
        if 'try_blocks' in pattern:
            print(f"     Try blocks: {pattern['try_blocks']}")
    
    # Verify key patterns were detected
    pattern_types = [p['type'] for p in patterns]
    
    checks = {
        'imports': 'imports' in pattern_types,
        'async': 'async' in pattern_types,
        'error_handling': 'error_handling' in pattern_types,
        'decorators': 'decorators' in pattern_types,
        'context_managers': 'context_managers' in pattern_types,
        'comprehensions': 'comprehensions' in pattern_types,
    }
    
    print("\n[Verification]")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")
    
    return all(checks.values())


def test_javascript_patterns():
    """Test JavaScript code pattern extraction."""
    print("\n" + "=" * 60)
    print("JavaScript Pattern Extraction Test")
    print("=" * 60)
    
    extractor = CodePatternExtractor()
    
    # Sample React/JavaScript code
    sample_code = """
import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Button } from './components/Button';

const UserProfile = ({ userId }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    fetchUser();
  }, [userId]);
  
  const fetchUser = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`/api/users/${userId}`);
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleClick = useCallback(() => {
    console.log('Clicked!');
  }, []);
  
  if (loading) return <div>Loading...</div>;
  if (!user) return null;
  
  return (
    <div className="profile">
      <h1>{user.name}</h1>
      <Button onClick={handleClick}>Click me</Button>
    </div>
  );
};

class OldComponent extends React.Component {
  render() {
    return <div>Legacy component</div>;
  }
}

export default UserProfile;
"""
    
    print("\n[Test 2] Extracting patterns from JavaScript code...")
    patterns = extractor.extract_from_javascript(sample_code)
    
    print(f"\nFound {len(patterns)} pattern types:")
    for i, pattern in enumerate(patterns, 1):
        print(f"\n  {i}. {pattern['pattern']} ({pattern['type']})")
        
        if 'details' in pattern:
            print(f"     Details: {pattern['details']}")
        elif 'count' in pattern:
            print(f"     Count: {pattern['count']}")
        
        if 'async_functions' in pattern:
            print(f"     Async functions: {pattern['async_functions']}")
        if 'await_calls' in pattern:
            print(f"     Await calls: {pattern['await_calls']}")
    
    # Verify key patterns were detected
    pattern_types = [p['type'] for p in patterns]
    
    checks = {
        'framework': 'framework' in pattern_types,
        'react_hooks': 'react_hooks' in pattern_types,
        'jsx': 'jsx' in pattern_types,
        'async': 'async' in pattern_types,
        'style': 'style' in pattern_types,  # arrow functions
    }
    
    print("\n[Verification]")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")
    
    return all(checks.values())


def test_auto_detection():
    """Test automatic language detection."""
    print("\n" + "=" * 60)
    print("Auto Language Detection Test")
    print("=" * 60)
    
    extractor = CodePatternExtractor()
    
    python_code = "def hello():\n    import os\n    return 'world'"
    js_code = "const hello = () => { return 'world'; }"
    
    print("\n[Test 3] Auto-detecting Python...")
    py_patterns = extractor.extract_patterns(python_code)
    print(f"  Detected {len(py_patterns)} patterns")
    
    print("\n[Test 4] Auto-detecting JavaScript...")
    js_patterns = extractor.extract_patterns(js_code)
    print(f"  Detected {len(js_patterns)} patterns")
    
    return len(py_patterns) > 0 and len(js_patterns) > 0


def test_real_files():
    """Test with actual project files."""
    print("\n" + "=" * 60)
    print("Real File Pattern Extraction Test")
    print("=" * 60)
    
    extractor = CodePatternExtractor()
    
    # Test with actual polly.py
    polly_file = Path(__file__).parent.parent / "core" / "polly.py"
    
    if polly_file.exists():
        print(f"\n[Test 5] Analyzing {polly_file.name}...")
        code = polly_file.read_text()
        patterns = extractor.extract_from_python(code)
        
        print(f"  Found {len(patterns)} pattern types:")
        for pattern in patterns[:5]:  # Show first 5
            print(f"    - {pattern['pattern']}")
        
        return len(patterns) > 0
    else:
        print("  ⚠️  polly.py not found, skipping")
        return True


if __name__ == "__main__":
    print("\n🧪 Code Pattern Extractor Test Suite\n")
    
    results = {
        "Python patterns": test_python_patterns(),
        "JavaScript patterns": test_javascript_patterns(),
        "Auto detection": test_auto_detection(),
        "Real files": test_real_files(),
    }
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test}")
    
    print("\n" + "=" * 60)
    
    all_passed = all(results.values())
    if all_passed:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
    
    sys.exit(0 if all_passed else 1)
