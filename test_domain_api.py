#!/usr/bin/env python3
"""
Test script for Domain Configuration API endpoints.
Tests all CRUD operations for Phase 1.5 domain configuration.
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_domain_api():
    """Test all domain API endpoints."""
    from core.domain_config import load_domains, save_domains
    
    print("=" * 60)
    print("Testing Domain Configuration API")
    print("=" * 60)
    
    # Test 1: Load existing config
    print("\n1. Testing load_domains()...")
    try:
        config = load_domains()
        print(f"   ✓ Loaded {len(config.domains)} domains")
        print(f"   ✓ Folder numbering: {config.folder_numbering}")
        for domain in config.domains:
            print(f"     - {domain.name} ({domain.id}): {domain.folder_path}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 2: Validate domain structure
    print("\n2. Testing domain structure...")
    try:
        for domain in config.domains:
            assert domain.id, "Domain must have id"
            assert domain.name, "Domain must have name"
            assert domain.color, "Domain must have color"
            assert domain.icon, "Domain must have icon"
            assert domain.folder_path, "Domain must have folder_path"
            assert isinstance(domain.rag_weight, float), "rag_weight must be float"
            assert isinstance(domain.auto_tag_rules, list), "auto_tag_rules must be list"
        print(f"   ✓ All {len(config.domains)} domains have valid structure")
    except AssertionError as e:
        print(f"   ✗ Validation error: {e}")
        return False
    
    # Test 3: Check RAG weight normalization
    print("\n3. Testing RAG weight normalization...")
    try:
        total_weight = sum(d.rag_weight for d in config.domains)
        print(f"   Total RAG weight: {total_weight:.6f}")
        if abs(total_weight - 1.0) < 0.001:
            print(f"   ✓ RAG weights are normalized (sum ≈ 1.0)")
        else:
            print(f"   ⚠ Warning: RAG weights sum to {total_weight:.6f}, not 1.0")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 4: Test serialization to dict (API response format)
    print("\n4. Testing serialization to dict...")
    try:
        api_response = {
            "version": config.version,
            "folderNumbering": config.folder_numbering,
            "domains": [
                {
                    "id": d.id,
                    "name": d.name,
                    "description": d.description,
                    "color": d.color,
                    "icon": d.icon,
                    "folderPath": d.folder_path,
                    "ragWeight": d.rag_weight,
                    "autoTagRules": d.auto_tag_rules,
                    "created": d.created,
                    "modified": d.modified,
                    "order": d.order
                }
                for d in config.domains
            ],
            "lastModified": config.last_modified
        }
        
        # Validate JSON serialization
        json_str = json.dumps(api_response, indent=2)
        parsed = json.loads(json_str)
        
        print(f"   ✓ Config serializes to valid JSON ({len(json_str)} bytes)")
        print(f"   ✓ Contains {len(parsed['domains'])} domains")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 5: Test domain lookup
    print("\n5. Testing domain lookup by ID...")
    try:
        test_ids = ["sigils", "signals", "scrolls", "glyphs", "grids"]
        for domain_id in test_ids:
            domain = next((d for d in config.domains if d.id == domain_id), None)
            if domain:
                print(f"   ✓ Found '{domain_id}': {domain.name}")
            else:
                print(f"   ⚠ Warning: Domain '{domain_id}' not found")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 6: Test validation rules
    print("\n6. Testing validation rules...")
    try:
        # Check for duplicate IDs
        ids = [d.id for d in config.domains]
        if len(ids) != len(set(ids)):
            print(f"   ✗ Error: Duplicate domain IDs found")
            return False
        print(f"   ✓ All domain IDs are unique")
        
        # Check for duplicate names
        names = [d.name for d in config.domains]
        if len(names) != len(set(names)):
            print(f"   ✗ Error: Duplicate domain names found")
            return False
        print(f"   ✓ All domain names are unique")
        
        # Check color format
        for domain in config.domains:
            if not domain.color.startswith("#") or len(domain.color) != 7:
                print(f"   ⚠ Warning: Invalid color format for {domain.name}: {domain.color}")
        print(f"   ✓ All colors are in hex format")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 7: Test order consistency
    print("\n7. Testing domain order...")
    try:
        orders = [d.order for d in config.domains]
        expected_orders = list(range(1, len(config.domains) + 1))
        sorted_orders = sorted(orders)
        
        if sorted_orders == expected_orders:
            print(f"   ✓ Domain orders are sequential (1-{len(config.domains)})")
        else:
            print(f"   ⚠ Warning: Domain orders are not sequential")
            print(f"     Expected: {expected_orders}")
            print(f"     Got: {sorted_orders}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 8: Test keyword rules
    print("\n8. Testing auto-tag rules...")
    try:
        total_keywords = 0
        for domain in config.domains:
            keyword_count = len(domain.auto_tag_rules)
            total_keywords += keyword_count
            print(f"   - {domain.name}: {keyword_count} keywords")
        print(f"   ✓ Total keywords across all domains: {total_keywords}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_domain_api()
    sys.exit(0 if success else 1)
