#!/usr/bin/env python3
"""
Demo: Professor Persona Using Skill Packages

This demonstrates how Professor can:
1. List available skills
2. Load a skill package (recursion)
3. Create teaching actions from skill content
4. Present diagrams, code examples, and exercises

Run this to see Professor's capabilities with the recursion skill package.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.personas.implementations.professor import ProfessorPersona
from core.personas.base import PersonaContext


def demo_skill_loading():
    """Demo 1: Loading and exploring skill packages."""
    print("=" * 80)
    print("DEMO 1: Loading Skill Packages")
    print("=" * 80)
    
    professor = ProfessorPersona()
    
    # List available skills
    print("\n📚 Available Skills:")
    skills = professor.list_available_skills()
    for skill in skills:
        print(f"  - {skill}")
    
    if not skills:
        print("  (No skills found - make sure recursion package exists)")
        return None
    
    # Load recursion skill
    print("\n📖 Loading 'recursion' skill package...")
    skill_data = professor.load_skill("recursion")
    
    if not skill_data:
        print("  ❌ Failed to load skill")
        return None
    
    print(f"  ✅ Loaded successfully!")
    print(f"  - Diagrams: {len(skill_data['diagrams'])}")
    print(f"  - Exercises: {len(skill_data['exercises'])}")
    print(f"  - Examples: {len(skill_data['examples'])}")
    
    # Show what's available
    print("\n  Diagrams:")
    for diagram in skill_data['diagrams']:
        print(f"    - {diagram['name']}")
    
    print("\n  Exercises:")
    for exercise in skill_data['exercises']:
        print(f"    - {exercise.get('title')} ({exercise.get('difficulty')})")
    
    return skill_data


def demo_teaching_with_diagrams(skill_data):
    """Demo 2: Professor creates diagram actions from skill package."""
    print("\n" + "=" * 80)
    print("DEMO 2: Teaching with Diagrams")
    print("=" * 80)
    
    professor = ProfessorPersona()
    
    # Create actions for each diagram
    actions = []
    for diagram in skill_data['diagrams']:
        print(f"\n📊 Creating diagram action: {diagram['name']}")
        
        action = professor.create_diagram_action(
            diagram_type="mermaid",
            source=diagram['source'],
            caption=f"Recursion: {diagram['name'].replace('-', ' ').title()}",
            interactive=True
        )
        actions.append(action)
        
        print(f"  ✅ Action created: {action.type}")
        print(f"  - Interactive: {action.data['interactive']}")
        print(f"  - Caption: {action.data['caption']}")
    
    print(f"\n📦 Total actions created: {len(actions)}")
    return actions


def demo_teaching_with_exercises(skill_data):
    """Demo 3: Professor creates exercise actions from skill package."""
    print("\n" + "=" * 80)
    print("DEMO 3: Teaching with Exercises")
    print("=" * 80)
    
    professor = ProfessorPersona()
    
    # Create actions for each exercise
    actions = []
    for exercise in skill_data['exercises']:
        print(f"\n📝 Creating exercise action: {exercise['title']}")
        
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
        actions.append(action)
        
        print(f"  ✅ Action created: {action.type}")
        print(f"  - Difficulty: {action.data['difficulty']}")
        print(f"  - Test cases: {len(action.data['test_cases'])}")
        print(f"  - Hints available: {len(action.data['hints'])}")
    
    print(f"\n📦 Total actions created: {len(actions)}")
    return actions


def demo_complete_lesson(skill_data):
    """Demo 4: Complete lesson flow combining diagrams and exercises."""
    print("\n" + "=" * 80)
    print("DEMO 4: Complete Lesson Flow")
    print("=" * 80)
    
    professor = ProfessorPersona()
    
    print("\n🎓 Professor's Lesson Plan: Introduction to Recursion")
    print("-" * 80)
    
    lesson_actions = []
    
    # 1. Start with call stack diagram
    print("\n1️⃣ Step 1: Show how call stack works")
    call_stack_diagram = next(
        (d for d in skill_data['diagrams'] if 'stack' in d['name']), 
        skill_data['diagrams'][0]
    )
    action = professor.create_diagram_action(
        diagram_type="mermaid",
        source=call_stack_diagram['source'],
        caption="Understanding the Call Stack in Recursion",
        interactive=True
    )
    lesson_actions.append(action)
    print(f"   ✅ Diagram action created: {call_stack_diagram['name']}")
    
    # 2. Show factorial flow diagram
    print("\n2️⃣ Step 2: Demonstrate with factorial example")
    factorial_diagram = next(
        (d for d in skill_data['diagrams'] if 'factorial' in d['name']), 
        skill_data['diagrams'][0]
    )
    action = professor.create_diagram_action(
        diagram_type="mermaid",
        source=factorial_diagram['source'],
        caption="Factorial Function Call Flow",
        interactive=True
    )
    lesson_actions.append(action)
    print(f"   ✅ Diagram action created: {factorial_diagram['name']}")
    
    # 3. Code execution example
    print("\n3️⃣ Step 3: Interactive code example")
    factorial_code = """function factorial(n) {
    if (n <= 1) {
        return 1;  // Base case
    }
    return n * factorial(n - 1);  // Recursive case
}

// Test it
console.log(factorial(5));  // Should print 120"""
    
    action = professor.create_code_execution_action(
        language="javascript",
        code=factorial_code,
        editable=True,
        visualize=None,
        test_cases=[
            {"input": "factorial(5)", "expected": "120"},
            {"input": "factorial(0)", "expected": "1"},
            {"input": "factorial(3)", "expected": "6"}
        ]
    )
    lesson_actions.append(action)
    print(f"   ✅ Code execution action created with 3 test cases")
    
    # 4. Practice exercises (progressive difficulty)
    print("\n4️⃣ Step 4: Practice exercises")
    for i, exercise in enumerate(skill_data['exercises'][:2], 1):  # First 2 exercises
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
        lesson_actions.append(action)
        print(f"   ✅ Exercise {i}: {exercise['title']} ({exercise['difficulty']})")
    
    print(f"\n📚 Lesson complete! Created {len(lesson_actions)} actions:")
    print(f"   - 2 diagrams (visual explanation)")
    print(f"   - 1 code example (interactive)")
    print(f"   - 2 exercises (hands-on practice)")
    
    return lesson_actions


def demo_exercise_lookup():
    """Demo 5: Looking up exercises by ID."""
    print("\n" + "=" * 80)
    print("DEMO 5: Exercise Lookup by ID")
    print("=" * 80)
    
    professor = ProfessorPersona()
    
    # Try to find a specific exercise
    exercise_id = "recursion-countdown"
    print(f"\n🔍 Looking up exercise: {exercise_id}")
    
    exercise = professor.get_exercise_by_id(exercise_id)
    
    if exercise:
        print(f"  ✅ Found exercise!")
        print(f"  - Title: {exercise['title']}")
        print(f"  - Difficulty: {exercise['difficulty']}")
        print(f"  - Description: {exercise['description'][:80]}...")
        print(f"  - Test cases: {len(exercise['test_cases'])}")
    else:
        print(f"  ❌ Exercise not found")


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "PROFESSOR SKILL PACKAGE DEMO" + " " * 30 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Demo 1: Load skill
    skill_data = demo_skill_loading()
    
    if not skill_data:
        print("\n❌ Cannot continue without skill data")
        return
    
    # Demo 2: Diagrams
    demo_teaching_with_diagrams(skill_data)
    
    # Demo 3: Exercises
    demo_teaching_with_exercises(skill_data)
    
    # Demo 4: Complete lesson
    demo_complete_lesson(skill_data)
    
    # Demo 5: Exercise lookup
    demo_exercise_lookup()
    
    print("\n" + "=" * 80)
    print("🎉 Demo Complete!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Start Polly server: python -m interfaces.server")
    print("2. Open Electron app")
    print("3. Go to Learning page")
    print("4. Ask Professor: 'Teach me about recursion'")
    print("5. Professor will use these skill packages to teach!")
    print()


if __name__ == "__main__":
    main()
