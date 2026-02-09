#!/usr/bin/env python3
"""
Index Polly codebase to extract code patterns.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.polly import Polly

def main():
    """Index the Polly codebase."""
    print("Initializing Polly...")
    polly = Polly()
    
    print("\nCurrent patterns before indexing:")
    print(f"  - Code snippets recorded: {len(polly.pattern_learner.code_snippets)}")
    print(f"  - Patterns identified: {len(polly.pattern_learner.patterns)}")
    
    # Index the current directory (Polly codebase)
    codebase_path = Path(__file__).parent
    print(f"\nIndexing codebase: {codebase_path}")
    
    # Index only Python files in core/ and learners/
    print("Indexing core/ and learners/ directories...")
    num_files = polly.rag.index_codebase(codebase_path)
    
    print(f"\n✓ Indexing complete: {num_files} files indexed")
    
    print("\nPatterns after indexing:")
    print(f"  - Code snippets recorded: {len(polly.pattern_learner.code_snippets)}")
    print(f"  - Patterns identified: {len(polly.pattern_learner.patterns)}")
    
    # Show code patterns
    code_patterns = [p for p in polly.pattern_learner.patterns.values() if p.pattern_type == 'code']
    print(f"\n✓ Found {len(code_patterns)} code patterns:")
    for p in sorted(code_patterns, key=lambda x: x.occurrences, reverse=True)[:20]:
        print(f"  - {p.name}: {p.occurrences} occurrences (confidence: {p.confidence:.2f})")
    
    # Save patterns
    polly.pattern_learner.save_patterns()
    print(f"\n✓ Patterns saved to: {polly.pattern_learner.storage_path}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
