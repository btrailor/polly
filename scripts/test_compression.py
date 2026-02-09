#!/usr/bin/env python3
"""
Test script for LLMLingua compression integration.

Usage:
    python scripts/test_compression.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
from core.compression.manager import CompressionManager


def test_compression_config():
    """Test compression configuration loading"""
    print("=" * 60)
    print("TEST 1: Configuration Loading")
    print("=" * 60)
    
    # Load config
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    print(f"✓ Config loaded from {config_path}")
    print(f"  Strategy: {config.get('compression', {}).get('strategy', 'NOT SET')}")
    print(f"  RAG enabled: {config.get('compression', {}).get('rag_context', {}).get('enabled', False)}")
    print(f"  RAG ratio: {config.get('compression', {}).get('rag_context', {}).get('ratio', 'NOT SET')}")
    print()


def test_compression_manager():
    """Test compression manager initialization"""
    print("=" * 60)
    print("TEST 2: CompressionManager Initialization")
    print("=" * 60)
    
    # Load config
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Initialize manager
    manager = CompressionManager(config=config)
    print("✓ CompressionManager initialized")
    
    # Check if compression enabled
    rag_enabled = manager.is_compression_enabled("rag_context")
    print(f"  RAG compression enabled: {rag_enabled}")
    
    if rag_enabled:
        ratio = manager.get_compression_ratio("rag_context")
        print(f"  RAG compression ratio: {ratio}")
    
    print()


def test_text_compression():
    """Test text compression with LLMLingua"""
    print("=" * 60)
    print("TEST 3: Text Compression (LLMLingua)")
    print("=" * 60)
    
    # Sample text (RAG context)
    sample_text = """
    Apollo is a unified RAG system that indexes and searches across multiple sources:
    Obsidian vault (notes, ideas, connections), project codebases (functions, classes, patterns),
    and documents (PDFs, docs, references). It uses ChromaDB for vector storage and Ollama
    for embeddings. The system supports hybrid search combining semantic search with keyword
    search using BM25. Results are ranked using Reciprocal Rank Fusion (RRF) with title boosting
    for better relevance. The RAG pipeline includes query expansion using pattern learning and
    domain detection to improve search quality.
    """
    
    print(f"Sample text length: {len(sample_text)} chars")
    print(f"Sample text (first 100 chars): {sample_text[:100]}...")
    print()
    
    # Load config
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Initialize manager
    manager = CompressionManager(config=config)
    
    # Compress text
    print("Compressing text with LLMLingua...")
    try:
        result = manager.compress_text(
            text=sample_text,
            strategy="llmlingua",
            target_ratio=0.5,
            context_type="rag_context"
        )
        
        print("✓ Compression successful")
        print(f"  Original tokens: {result['original_tokens']}")
        print(f"  Compressed tokens: {result['compressed_tokens']}")
        print(f"  Compression ratio: {result['compression_ratio']:.2f}x")
        print(f"  Strategy used: {result.get('strategy', 'unknown')}")
        print(f"  Tokens saved: {result['original_tokens'] - result['compressed_tokens']}")
        print()
        print(f"Compressed text (first 100 chars):")
        print(f"  {result['compressed_text'][:100]}...")
        
    except Exception as e:
        print(f"⚠ Compression failed (expected if llmlingua not installed): {e}")
        print("  To install: pip install llmlingua")
    
    print()


def test_strategy_selection():
    """Test compression strategy selection"""
    print("=" * 60)
    print("TEST 4: Strategy Selection")
    print("=" * 60)
    
    # Load config
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Initialize manager
    manager = CompressionManager(config=config)
    
    # Test auto strategy
    print("Testing 'auto' strategy:")
    print(f"  RAG context → {manager.compressor.get_strategy_for_context('rag_context')}")
    print(f"  Conversation → {manager.compressor.get_strategy_for_context('conversation')}")
    print(f"  Prompt → {manager.compressor.get_strategy_for_context('prompt')}")
    print()


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("LLMLingua Compression Integration Test Suite")
    print("=" * 60 + "\n")
    
    try:
        test_compression_config()
        test_compression_manager()
        test_strategy_selection()
        test_text_compression()
        
        print("=" * 60)
        print("✓ All tests completed")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Install LLMLingua: pip install llmlingua")
        print("2. Enable compression in config: compression.rag_context.enabled: true")
        print("3. Test with actual RAG queries")
        print()
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
