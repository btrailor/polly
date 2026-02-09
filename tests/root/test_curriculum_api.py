#!/usr/bin/env python3
"""
Test script for Curriculum API
Tests all curriculum endpoints to verify Phase 1 implementation.
"""

import requests
import json
from datetime import datetime

API_BASE = "http://127.0.0.1:11436"

def test_list_curricula():
    """Test: List all curricula"""
    print("\n[TEST] List curricula...")
    response = requests.get(f"{API_BASE}/polly/curricula/list")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    return data

def test_create_curriculum():
    """Test: Create a new curriculum"""
    print("\n[TEST] Create curriculum...")
    
    curriculum_data = {
        "title": "Test Python Mastery",
        "goal": "Learn advanced Python concepts",
        "current_level": "intermediate",
        "estimated_duration": "6 weeks",
        "sections": [
            {
                "id": "week-1",
                "title": "Week 1: Decorators",
                "type": "week",
                "order": 0,
                "description": "Master Python decorators",
                "concepts": ["function decorators", "class decorators", "decorator patterns"],
                "estimated_time": "5 hours"
            },
            {
                "id": "week-1.1",
                "title": "Function Decorators",
                "type": "subheading",
                "order": 0,
                "parent_id": "week-1",
                "description": "Learn function decorators",
                "concepts": ["@wraps", "closures", "decorator syntax"],
                "estimated_time": "2 hours"
            },
            {
                "id": "week-1.2",
                "title": "Class Decorators",
                "type": "subheading",
                "order": 1,
                "parent_id": "week-1",
                "description": "Learn class decorators",
                "concepts": ["__call__", "class-based decorators"],
                "estimated_time": "3 hours"
            },
            {
                "id": "week-2",
                "title": "Week 2: Context Managers",
                "type": "week",
                "order": 1,
                "description": "Master context managers",
                "concepts": ["with statement", "__enter__", "__exit__"],
                "estimated_time": "5 hours"
            }
        ]
    }
    
    response = requests.post(
        f"{API_BASE}/polly/curricula/create",
        json=curriculum_data
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)[:500]}...")
    
    if data.get('success'):
        curriculum_id = data['curriculum']['id']
        print(f"✓ Created curriculum: {curriculum_id}")
        return curriculum_id
    else:
        print(f"✗ Failed to create curriculum: {data.get('error')}")
        return None

def test_get_curriculum(curriculum_id):
    """Test: Get curriculum details"""
    print(f"\n[TEST] Get curriculum {curriculum_id}...")
    response = requests.get(f"{API_BASE}/polly/curricula/{curriculum_id}")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Title: {data.get('title')}")
    print(f"Sections: {len(data.get('sections', []))}")
    print(f"Status: {data.get('status')}")
    return data

def test_activate_curriculum(curriculum_id):
    """Test: Activate curriculum"""
    print(f"\n[TEST] Activate curriculum {curriculum_id}...")
    response = requests.post(f"{API_BASE}/polly/curricula/{curriculum_id}/activate")
    print(f"Status: {response.status_code}")
    data = response.json()
    if data.get('success'):
        print(f"✓ Activated. Status: {data['curriculum']['status']}")
        return True
    else:
        print(f"✗ Failed: {data.get('error')}")
        return False

def test_start_section(curriculum_id, section_id):
    """Test: Start a section"""
    print(f"\n[TEST] Start section {section_id}...")
    response = requests.post(
        f"{API_BASE}/polly/curricula/{curriculum_id}/sections/{section_id}/start"
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    if data.get('success'):
        print(f"✓ Started section. Status: {data['section']['status']}")
        return True
    else:
        print(f"✗ Failed: {data.get('error')}")
        return False

def test_complete_section(curriculum_id, section_id):
    """Test: Complete a section"""
    print(f"\n[TEST] Complete section {section_id}...")
    
    reflection = {
        "mastery_level": 4,
        "struggles": ["Understanding decorator chaining"],
        "breakthroughs": ["Finally got how closures work!"],
        "time_spent": 2.5
    }
    
    response = requests.post(
        f"{API_BASE}/polly/curricula/{curriculum_id}/sections/{section_id}/complete",
        json=reflection
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    if data.get('success'):
        print(f"✓ Completed section. Status: {data['section']['status']}")
        return True
    else:
        print(f"✗ Failed: {data.get('error')}")
        return False

def test_get_progress(curriculum_id):
    """Test: Get progress summary"""
    print(f"\n[TEST] Get progress for {curriculum_id}...")
    response = requests.get(f"{API_BASE}/polly/curricula/{curriculum_id}/progress")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Overall completion: {data.get('overall_completion_percentage')}%")
    print(f"Sections completed: {data.get('sections_completed')}/{data.get('total_sections')}")
    print(f"Current section: {data.get('current_section', {}).get('title')}")
    return data

def test_pause_curriculum(curriculum_id):
    """Test: Pause curriculum"""
    print(f"\n[TEST] Pause curriculum {curriculum_id}...")
    response = requests.post(f"{API_BASE}/polly/curricula/{curriculum_id}/pause")
    print(f"Status: {response.status_code}")
    data = response.json()
    if data.get('success'):
        print(f"✓ Paused. Status: {data['curriculum']['status']}")
        return True
    else:
        print(f"✗ Failed: {data.get('error')}")
        return False

def test_delete_curriculum(curriculum_id):
    """Test: Delete curriculum"""
    print(f"\n[TEST] Delete curriculum {curriculum_id}...")
    response = requests.delete(f"{API_BASE}/polly/curricula/{curriculum_id}")
    print(f"Status: {response.status_code}")
    data = response.json()
    if data.get('success'):
        print(f"✓ Deleted")
        return True
    else:
        print(f"✗ Failed: {data.get('error')}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("CURRICULUM API TEST SUITE - Phase 1")
    print("=" * 60)
    
    try:
        # Test 1: List (should be empty initially)
        test_list_curricula()
        
        # Test 2: Create curriculum
        curriculum_id = test_create_curriculum()
        if not curriculum_id:
            print("\n✗ FAILED: Could not create curriculum")
            return
        
        # Test 3: Get curriculum details
        test_get_curriculum(curriculum_id)
        
        # Test 4: Activate curriculum
        test_activate_curriculum(curriculum_id)
        
        # Test 5: Start first section
        test_start_section(curriculum_id, "week-1.1")
        
        # Test 6: Complete first section
        test_complete_section(curriculum_id, "week-1.1")
        
        # Test 7: Get progress
        test_get_progress(curriculum_id)
        
        # Test 8: Pause curriculum
        test_pause_curriculum(curriculum_id)
        
        # Test 9: List again (should show our curriculum)
        curricula = test_list_curricula()
        print(f"\nTotal curricula: {len(curricula.get('curricula', []))}")
        
        # Test 10: Delete curriculum (cleanup)
        test_delete_curriculum(curriculum_id)
        
        # Test 11: List again (should be empty)
        test_list_curricula()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS COMPLETED")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
