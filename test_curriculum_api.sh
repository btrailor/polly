#!/bin/bash
# Curriculum API Test Script (curl-based)
# Tests all Phase 1 curriculum endpoints

API_BASE="http://127.0.0.1:11436"

echo "===================================="
echo "CURRICULUM API TEST SUITE - Phase 1"
echo "===================================="

# Test 1: List curricula (should be empty initially)
echo -e "\n[TEST 1] List curricula..."
curl -s "${API_BASE}/polly/curricula/list" | python3 -m json.tool

# Test 2: Create a curriculum
echo -e "\n[TEST 2] Create curriculum..."
CREATE_RESPONSE=$(curl -s -X POST "${API_BASE}/polly/curricula/create" \
  -H "Content-Type: application/json" \
  -d '{
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
      }
    ]
  }')

echo "$CREATE_RESPONSE" | python3 -m json.tool
CURRICULUM_ID=$(echo "$CREATE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('curriculum', {}).get('id', ''))" 2>/dev/null)

if [ -z "$CURRICULUM_ID" ]; then
  echo "✗ FAILED: Could not create curriculum"
  exit 1
fi

echo "✓ Created curriculum: $CURRICULUM_ID"

# Test 3: Get curriculum details
echo -e "\n[TEST 3] Get curriculum details..."
curl -s "${API_BASE}/polly/curricula/${CURRICULUM_ID}" | python3 -m json.tool | head -40

# Test 4: Activate curriculum
echo -e "\n[TEST 4] Activate curriculum..."
curl -s -X POST "${API_BASE}/polly/curricula/${CURRICULUM_ID}/activate" | python3 -m json.tool

# Test 5: Start first section
echo -e "\n[TEST 5] Start section week-1.1..."
curl -s -X POST "${API_BASE}/polly/curricula/${CURRICULUM_ID}/sections/week-1.1/start" | python3 -m json.tool

# Test 6: Complete first section
echo -e "\n[TEST 6] Complete section week-1.1..."
curl -s -X POST "${API_BASE}/polly/curricula/${CURRICULUM_ID}/sections/week-1.1/complete" \
  -H "Content-Type: application/json" \
  -d '{
    "mastery_level": 4,
    "struggles": ["Understanding decorator chaining"],
    "breakthroughs": ["Finally got how closures work!"],
    "time_spent": 2.5
  }' | python3 -m json.tool

# Test 7: Get progress
echo -e "\n[TEST 7] Get progress..."
curl -s "${API_BASE}/polly/curricula/${CURRICULUM_ID}/progress" | python3 -m json.tool

# Test 8: Check file structure
echo -e "\n[TEST 8] Check file structure in vault..."
VAULT_PATH="$HOME/polly/vault/.polly/curricula/${CURRICULUM_ID}"
if [ -d "$VAULT_PATH" ]; then
  echo "✓ Curriculum directory exists: $VAULT_PATH"
  ls -lh "$VAULT_PATH"
  echo -e "\nFiles:"
  find "$VAULT_PATH" -type f -exec echo "  - {}" \;
else
  echo "✗ Curriculum directory NOT found: $VAULT_PATH"
fi

# Test 9: Pause curriculum
echo -e "\n[TEST 9] Pause curriculum..."
curl -s -X POST "${API_BASE}/polly/curricula/${CURRICULUM_ID}/pause" | python3 -m json.tool

# Test 10: List all curricula
echo -e "\n[TEST 10] List all curricula..."
curl -s "${API_BASE}/polly/curricula/list" | python3 -m json.tool

# Test 11: Delete curriculum (cleanup)
echo -e "\n[TEST 11] Delete curriculum (cleanup)..."
curl -s -X DELETE "${API_BASE}/polly/curricula/${CURRICULUM_ID}" | python3 -m json.tool

# Test 12: Verify deletion
echo -e "\n[TEST 12] Verify deletion..."
curl -s "${API_BASE}/polly/curricula/list" | python3 -m json.tool

echo -e "\n===================================="
echo "✓ ALL TESTS COMPLETED"
echo "===================================="
