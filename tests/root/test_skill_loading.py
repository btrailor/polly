#!/usr/bin/env python3
"""
Simple test of skill package loading without full Professor initialization.
Tests just the skill loading methods.
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_skill_loading():
    """Test loading skill packages directly."""
    print("=" * 80)
    print("TESTING SKILL PACKAGE LOADING")
    print("=" * 80)
    
    vault_path = Path.home() / "polly" / "vault" / ".polly" / "skills"
    print(f"\nVault path: {vault_path}")
    print(f"Exists: {vault_path.exists()}")
    
    if not vault_path.exists():
        print("❌ Vault path doesn't exist!")
        return False
    
    # List all skill directories
    print("\n📚 Available Skills:")
    skills = []
    for skill_dir in vault_path.iterdir():
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
            skills.append(skill_dir.name)
            print(f"  ✅ {skill_dir.name}")
    
    if not skills:
        print("  (No skills found)")
        return False
    
    # Test loading recursion skill
    print("\n" + "=" * 80)
    print("LOADING RECURSION SKILL")
    print("=" * 80)
    
    recursion_dir = vault_path / "recursion"
    if not recursion_dir.exists():
        print("❌ Recursion skill not found!")
        return False
    
    print(f"\n📖 Loading from: {recursion_dir}")
    
    # Load SKILL.md
    skill_md = recursion_dir / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text()
        print(f"  ✅ SKILL.md loaded ({len(content)} chars)")
        print(f"     First 100 chars: {content[:100]}...")
    else:
        print("  ❌ SKILL.md not found")
    
    # Load diagrams
    diagrams_dir = recursion_dir / "diagrams"
    if diagrams_dir.exists():
        diagrams = list(diagrams_dir.glob("*.mmd"))
        print(f"\n  📊 Found {len(diagrams)} diagrams:")
        for diagram in diagrams:
            print(f"     - {diagram.stem}")
    else:
        print("  ⚠️  No diagrams directory")
    
    # Load exercises
    exercises_dir = recursion_dir / "exercises"
    if exercises_dir.exists():
        exercises = list(exercises_dir.glob("*.json"))
        print(f"\n  📝 Found {len(exercises)} exercises:")
        for exercise_file in exercises:
            try:
                with open(exercise_file) as f:
                    exercise = json.load(f)
                print(f"     - {exercise.get('title')} ({exercise.get('difficulty')})")
            except Exception as e:
                print(f"     - {exercise_file.name} (ERROR: {e})")
    else:
        print("  ⚠️  No exercises directory")
    
    print("\n" + "=" * 80)
    print("✅ SKILL LOADING TEST COMPLETE")
    print("=" * 80)
    return True


def test_professor_skill_methods():
    """Test Professor skill methods with minimal initialization."""
    print("\n" + "=" * 80)
    print("TESTING PROFESSOR SKILL METHODS")
    print("=" * 80)
    
    try:
        # Import here to avoid initialization issues
        from core.personas.implementations.professor import ProfessorPersona
        from core.router_v2 import IntelligentRouterV2
        
        # Create minimal router (won't be used for this test)
        router = IntelligentRouterV2()
        
        # Create Professor
        professor = ProfessorPersona(name="Professor", router=router)
        
        print("\n✅ Professor initialized")
        
        # Test list_available_skills
        print("\n📚 Testing list_available_skills()...")
        skills = professor.list_available_skills()
        print(f"  Found {len(skills)} skills: {skills}")
        
        # Test load_skill
        if "recursion" in skills:
            print("\n📖 Testing load_skill('recursion')...")
            skill_data = professor.load_skill("recursion")
            
            if skill_data:
                print(f"  ✅ Loaded successfully!")
                print(f"     - Diagrams: {len(skill_data['diagrams'])}")
                print(f"     - Exercises: {len(skill_data['exercises'])}")
                print(f"     - Examples: {len(skill_data['examples'])}")
                
                # Test creating actions from skill data
                print("\n🎬 Testing action creation...")
                
                if skill_data['diagrams']:
                    diagram = skill_data['diagrams'][0]
                    action = professor.create_diagram_action(
                        diagram_type="mermaid",
                        source=diagram['source'],
                        caption="Test diagram",
                        interactive=True
                    )
                    print(f"  ✅ Created diagram action: {action.type}")
                
                if skill_data['exercises']:
                    exercise = skill_data['exercises'][0]
                    action = professor.create_exercise_action(
                        exercise_id=exercise['exercise_id'],
                        exercise_type=exercise['type'],
                        title=exercise['title'],
                        description=exercise['description'],
                        starter_code=exercise.get('starter_code', ''),
                        solution=exercise.get('solution', ''),
                        test_cases=exercise.get('test_cases', []),
                        hints=exercise.get('hints', []),
                        difficulty=exercise['difficulty']
                    )
                    print(f"  ✅ Created exercise action: {action.type}")
            else:
                print("  ❌ Failed to load skill")
        
        print("\n" + "=" * 80)
        print("✅ PROFESSOR METHODS TEST COMPLETE")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 25 + "SKILL PACKAGE TEST" + " " * 35 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Test 1: Direct file loading
    success1 = test_skill_loading()
    
    # Test 2: Professor methods
    success2 = test_professor_skill_methods()
    
    if success1 and success2:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n⚠️  SOME TESTS FAILED")
    
    print()
