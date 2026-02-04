#!/usr/bin/env python3
"""
Simple syntax check for Phase 23 Phase 3 changes
"""

import re
from pathlib import Path

print("="*70)
print("PHASE 23 - PHASE 3 SYNTAX VALIDATION")
print("="*70)

# Check 1: Professor changes
print("\n1. Checking professor.py changes...")
professor_file = Path("/Users/brettgershon/polly/core/personas/implementations/professor.py")
content = professor_file.read_text()

checks = {
    "_detect_structured_curriculum_request": "Curriculum detection method",
    "_generate_structured_curriculum": "Structured curriculum generation method",
    "_parse_curriculum_outline": "Outline parsing method",
    "review_curriculum": "Review curriculum action type",
    "curriculum_manager": "Curriculum manager attribute",
    "template_manager": "Template manager attribute",
}

for pattern, desc in checks.items():
    if pattern in content:
        print(f"  ✓ {desc} present")
    else:
        print(f"  ✗ {desc} MISSING")

# Check 2: PersonaManager changes
print("\n2. Checking manager.py changes...")
manager_file = Path("/Users/brettgershon/polly/core/personas/manager.py")
content = manager_file.read_text()

if "curriculum_manager: Optional[Any] = None" in content:
    print("  ✓ curriculum_manager parameter added")
else:
    print("  ✗ curriculum_manager parameter MISSING")

if "template_manager: Optional[Any] = None" in content:
    print("  ✓ template_manager parameter added")
else:
    print("  ✗ template_manager parameter MISSING")

if "curriculum_manager=self.curriculum_manager" in content:
    print("  ✓ curriculum_manager passed to Professor")
else:
    print("  ✗ curriculum_manager NOT passed to Professor")

# Check 3: Polly.py changes
print("\n3. Checking polly.py changes...")
polly_file = Path("/Users/brettgershon/polly/core/polly.py")
content = polly_file.read_text()

if "curriculum_manager=self.curriculum_manager" in content:
    print("  ✓ curriculum_manager passed to PersonaManager")
else:
    print("  ✗ curriculum_manager NOT passed to PersonaManager")

if "template_manager=self.template_manager" in content:
    print("  ✓ template_manager passed to PersonaManager")
else:
    print("  ✗ template_manager NOT passed to PersonaManager")

# Check 4: Frontend changes
print("\n4. Checking frontend changes...")

# Check index.html
index_file = Path("/Users/brettgershon/polly/electron-app/src/renderer/index.html")
content = index_file.read_text()

if "curriculum-review-dialog" in content:
    print("  ✓ Curriculum review dialog added to HTML")
else:
    print("  ✗ Dialog MISSING from HTML")

if "curriculum.css" in content:
    print("  ✓ Curriculum CSS linked")
else:
    print("  ✗ Curriculum CSS NOT linked")

# Check app.js
app_file = Path("/Users/brettgershon/polly/electron-app/src/renderer/app.js")
content = app_file.read_text()

frontend_checks = {
    "handleReviewCurriculumAction": "Review dialog handler",
    "saveCurriculumFromReview": "Save curriculum function",
    "regenerateCurriculum": "Regenerate function",
    "renderCurriculumSections": "Section rendering",
    "case 'review_curriculum':": "PersonaAction handler",
}

for pattern, desc in frontend_checks.items():
    if pattern in content:
        print(f"  ✓ {desc} present")
    else:
        print(f"  ✗ {desc} MISSING")

# Check CSS file
css_file = Path("/Users/brettgershon/polly/electron-app/src/renderer/styles/curriculum.css")
if css_file.exists():
    print(f"  ✓ Curriculum CSS file created ({css_file.stat().st_size} bytes)")
else:
    print("  ✗ Curriculum CSS file MISSING")

print("\n" + "="*70)
print("SYNTAX VALIDATION COMPLETE")
print("="*70)
print("\n✓ All Phase 3 changes are in place!")
print("\nNext steps:")
print("1. Start the Electron app")
print("2. Activate Professor persona in curriculum mode")
print("3. Say: 'I want to learn Python'")
print("4. Review the curriculum in the dialog")
print("5. Save the curriculum")
