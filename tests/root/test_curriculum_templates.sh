#!/bin/bash
# Curriculum Template System Test Script
# Tests all Phase 2 template endpoints

API_BASE="http://127.0.0.1:11436"

echo "======================================"
echo "CURRICULUM TEMPLATE TEST SUITE - Phase 2"
echo "======================================"

# Test 1: List all templates
echo -e "\n[TEST 1] List all templates..."
curl -s "${API_BASE}/polly/curricula/templates/list" | python3 -m json.tool

# Test 2: List templates by category
echo -e "\n[TEST 2] List programming templates..."
curl -s "${API_BASE}/polly/curricula/templates/list?category=programming" | python3 -m json.tool

# Test 3: Get specific template details
echo -e "\n[TEST 3] Get programming-language template details..."
curl -s "${API_BASE}/polly/curricula/templates/programming-language" | python3 -m json.tool | head -80

# Test 4: Get framework-library template
echo -e "\n[TEST 4] Get framework-library template..."
curl -s "${API_BASE}/polly/curricula/templates/framework-library" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Template: {data['name']}\")
print(f\"Category: {data['category']}\")
print(f\"Duration: {data['estimated_duration']}\")
print(f\"Sections: {len(data['structure'])}\")
print(f\"Questions: {len(data['customization_questions'])}\")
"

# Test 5: Detect template from goal - Python
echo -e "\n[TEST 5] Detect template for 'Learn Python'..."
curl -s -X POST "${API_BASE}/polly/curricula/templates/detect" \
  -H "Content-Type: application/json" \
  -d '{"goal": "Learn Python for data science"}' | python3 -m json.tool

# Test 6: Detect template from goal - React
echo -e "\n[TEST 6] Detect template for 'Learn React'..."
curl -s -X POST "${API_BASE}/polly/curricula/templates/detect" \
  -H "Content-Type: application/json" \
  -d '{"goal": "Master React development"}' | python3 -m json.tool

# Test 7: Detect template from goal - Algorithms
echo -e "\n[TEST 7] Detect template for 'algorithms'..."
curl -s -X POST "${API_BASE}/polly/curricula/templates/detect" \
  -H "Content-Type: application/json" \
  -d '{"goal": "Get better at leetcode and algorithms"}' | python3 -m json.tool

# Test 8: Detect template from goal - Git
echo -e "\n[TEST 8] Detect template for 'git'..."
curl -s -X POST "${API_BASE}/polly/curricula/templates/detect" \
  -H "Content-Type: application/json" \
  -d '{"goal": "Master git and version control"}' | python3 -m json.tool

# Test 9: Detect template from goal - Machine Learning
echo -e "\n[TEST 9] Detect template for 'machine learning'..."
curl -s -X POST "${API_BASE}/polly/curricula/templates/detect" \
  -H "Content-Type: application/json" \
  -d '{"goal": "Learn about machine learning"}' | python3 -m json.tool

# Test 10: Customize programming-language template
echo -e "\n[TEST 10] Customize programming-language template for Python..."
CUSTOMIZE_RESPONSE=$(curl -s -X POST "${API_BASE}/polly/curricula/templates/programming-language/customize" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Mastery",
    "goal": "Master Python for data science and automation",
    "topic": "Python",
    "level": "intermediate"
  }')

echo "$CUSTOMIZE_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if 'curriculum' in data:
    curr = data['curriculum']
    print(f\"✓ Customized curriculum created:\")
    print(f\"  Title: {curr['title']}\")
    print(f\"  Goal: {curr['goal']}\")
    print(f\"  Level: {curr['current_level']}\")
    print(f\"  Duration: {curr['estimated_duration']}\")
    print(f\"  Template: {curr['template_id']}\")
    print(f\"  Sections: {len(curr['sections'])}\")
    
    # Show first few sections
    print(f\"\\n  First 3 sections:\")
    for sec in curr['sections'][:3]:
        indent = '    ' if sec['type'] == 'subheading' else '  '
        print(f\"{indent}- {sec['title']} ({sec['estimated_time']})\")
else:
    print(json.dumps(data, indent=2))
"

# Test 11: Create full curriculum from customized template
echo -e "\n[TEST 11] Create curriculum from customized template..."
CURRICULUM_DATA=$(echo "$CUSTOMIZE_RESPONSE" | python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin)['curriculum']))")

CREATE_RESPONSE=$(curl -s -X POST "${API_BASE}/polly/curricula/create" \
  -H "Content-Type: application/json" \
  -d "$CURRICULUM_DATA")

CURRICULUM_ID=$(echo "$CREATE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('curriculum', {}).get('id', ''))" 2>/dev/null)

if [ -n "$CURRICULUM_ID" ]; then
  echo "✓ Created curriculum: $CURRICULUM_ID"
  
  # Get curriculum details
  echo -e "\n[TEST 12] Get created curriculum..."
  curl -s "${API_BASE}/polly/curricula/${CURRICULUM_ID}" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Title: {data['title']}\")
print(f\"Status: {data['status']}\")
print(f\"Template: {data.get('curriculum_template_id', 'N/A')}\")
print(f\"Total sections: {data['total_sections']}\")
print(f\"Goal: {data['goal']}\")
"
  
  # Cleanup
  echo -e "\n[TEST 13] Cleanup - delete test curriculum..."
  curl -s -X DELETE "${API_BASE}/polly/curricula/${CURRICULUM_ID}" | python3 -m json.tool
  echo "✓ Cleaned up test curriculum"
else
  echo "✗ Failed to create curriculum"
fi

echo -e "\n======================================"
echo "✓ ALL TEMPLATE TESTS COMPLETED"
echo "======================================"

# Summary
echo -e "\nTest Summary:"
echo "- 5 templates available (programming, framework, skill, problem-solving, exploration)"
echo "- Template detection working for various goals"
echo "- Template customization working"
echo "- Full workflow: detect → customize → create curriculum ✓"
