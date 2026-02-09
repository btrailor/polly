"""
Demo: Professor Persona with Learning Visualization Tools

This demonstrates how Professor can use the new visualization actions:
- render_diagram: Show Mermaid diagrams
- execute_code: Run code with interactive sandbox
- present_exercise: Interactive coding challenges

Run this to test the learning tools integration.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.personas.base import PersonaContext
from core.personas.implementations.professor import ProfessorPersona
from core.router_v2 import IntelligentRouterV2
from learners.learning_tracker import LearningTracker
from pathlib import Path


async def demo_diagram_visualization():
    """Demo: Professor explains recursion with a diagram"""
    print("\n" + "="*60)
    print("DEMO 1: Diagram Visualization")
    print("="*60)
    
    # Create Professor instance (mock router for demo)
    professor = ProfessorPersona(
        name="professor",
        router=None,  # Mock
        learning_tracker=None
    )
    
    # Create a diagram action
    diagram_action = professor.create_diagram_action(
        diagram_type="mermaid",
        source="""graph TD
    A[factorial 3] -->|3 * factorial 2| B[factorial 2]
    B -->|2 * factorial 1| C[factorial 1]
    C -->|returns 1| D[Base Case!]
    
    D -->|1| C
    C -->|2 * 1 = 2| B
    B -->|3 * 2 = 6| A
    A -->|Result: 6| E[Done]
    
    style D fill:#00ff88
    style E fill:#00d9ff""",
        caption="How factorial(3) executes recursively",
        interactive=True
    )
    
    print("\n📊 Action created:")
    print(f"  Type: {diagram_action.type}")
    print(f"  Caption: {diagram_action.data['caption']}")
    print(f"  Interactive: {diagram_action.data['interactive']}")
    print("\n✓ This diagram will be rendered in the Learning page session view")
    print("✓ Users can zoom/pan with interactive controls")


async def demo_code_execution():
    """Demo: Professor presents executable code example"""
    print("\n" + "="*60)
    print("DEMO 2: Code Execution Sandbox")
    print("="*60)
    
    professor = ProfessorPersona(name="professor", router=None, learning_tracker=None)
    
    # Create code execution action
    code_action = professor.create_code_execution_action(
        language="javascript",
        code="""function factorial(n) {
  if (n <= 1) {
    return 1;
  }
  return n * factorial(n - 1);
}

console.log("factorial(5) =", factorial(5));
console.log("factorial(10) =", factorial(10));""",
        editable=True,
        test_cases=[
            {"input": "factorial(5)", "expected": "120"},
            {"input": "factorial(10)", "expected": "3628800"}
        ]
    )
    
    print("\n💻 Code execution action created:")
    print(f"  Language: {code_action.data['language']}")
    print(f"  Editable: {code_action.data['editable']}")
    print(f"  Test cases: {len(code_action.data['test_cases'])}")
    print("\n✓ Code will run in JavaScript sandbox")
    print("✓ Users can edit and re-run")
    print("✓ Automatic test validation")


async def demo_interactive_exercise():
    """Demo: Professor presents a coding challenge"""
    print("\n" + "="*60)
    print("DEMO 3: Interactive Exercise")
    print("="*60)
    
    professor = ProfessorPersona(name="professor", router=None, learning_tracker=None)
    
    # Create exercise action
    exercise_action = professor.create_exercise_action(
        exercise_id="fibonacci_challenge_1",
        exercise_type="code_challenge",
        title="Implement Fibonacci",
        description="Write a recursive function that returns the nth Fibonacci number. Remember: fibonacci(0) = 0, fibonacci(1) = 1, fibonacci(n) = fibonacci(n-1) + fibonacci(n-2)",
        starter_code="""function fibonacci(n) {
  // Your code here
  
}""",
        solution="""function fibonacci(n) {
  if (n <= 0) return 0;
  if (n === 1) return 1;
  return fibonacci(n - 1) + fibonacci(n - 2);
}""",
        test_cases=[
            {"input": "fibonacci(0)", "output": "0"},
            {"input": "fibonacci(1)", "output": "1"},
            {"input": "fibonacci(5)", "output": "5"},
            {"input": "fibonacci(10)", "output": "55"}
        ],
        hints=[
            "You need TWO base cases",
            "One base case for n=0, one for n=1",
            "For other values, add the previous two Fibonacci numbers"
        ],
        difficulty="easy"
    )
    
    print("\n🎯 Exercise created:")
    print(f"  Title: {exercise_action.data['title']}")
    print(f"  Type: {exercise_action.data['type']}")
    print(f"  Difficulty: {exercise_action.data['difficulty']}")
    print(f"  Test cases: {len(exercise_action.data['test_cases'])}")
    print(f"  Hints available: {len(exercise_action.data['hints'])}")
    print(f"  Estimated time: {exercise_action.data['estimated_time']}")
    print("\n✓ Users get immediate feedback")
    print("✓ Progressive hints available")
    print("✓ Mastery tracked automatically")


async def demo_complete_learning_session():
    """Demo: Complete learning session with all tools"""
    print("\n" + "="*60)
    print("DEMO 4: Complete Learning Session")
    print("="*60)
    print("\nImagine a user asks: 'Teach me about recursion'\n")
    print("Professor could respond with this sequence:\n")
    
    professor = ProfessorPersona(name="professor", router=None, learning_tracker=None)
    
    # Step 1: Explain with diagram
    print("1️⃣  TEXT EXPLANATION")
    print("    Professor explains recursion concept...")
    
    diagram = professor.create_diagram_action(
        diagram_type="mermaid",
        source=open("/Users/brettgershon/polly/vault/.polly/skills/recursion/diagrams/factorial-flow.mmd").read(),
        caption="Visualizing how factorial(5) executes",
        interactive=True
    )
    print("\n2️⃣  DIAGRAM VISUALIZATION")
    print(f"    ✓ Shows {diagram.data['caption']}")
    
    # Step 2: Show runnable code
    code = professor.create_code_execution_action(
        language="javascript",
        code="""function factorial(n) {
  if (n <= 1) return 1;
  return n * factorial(n - 1);
}

// Try it yourself!
console.log(factorial(5));""",
        editable=True
    )
    print("\n3️⃣  INTERACTIVE CODE EXAMPLE")
    print("    ✓ User can run and modify code")
    
    # Step 3: Give exercise
    exercise = professor.create_exercise_action(
        exercise_id="countdown_1",
        exercise_type="code_challenge",
        title="Your Turn: Countdown Function",
        description="Write a recursive countdown function",
        starter_code="function countdown(n) {\n  // Your code\n}",
        test_cases=[
            {"input": "countdown(3)", "output": "3\n2\n1\n"}
        ],
        hints=["What's the base case?", "Print n, then call countdown(n-1)"],
        difficulty="beginner"
    )
    print("\n4️⃣  PRACTICE EXERCISE")
    print(f"    ✓ Challenge: {exercise.data['title']}")
    print(f"    ✓ Difficulty: {exercise.data['difficulty']}")
    print(f"    ✓ Hints: {len(exercise.data['hints'])} available")
    
    print("\n" + "="*60)
    print("This creates a complete learning experience:")
    print("  📖 Conceptual explanation")
    print("  📊 Visual understanding")
    print("  💻 Hands-on practice")
    print("  ✅ Immediate feedback")
    print("  📈 Progress tracking")
    print("="*60)


async def main():
    """Run all demos"""
    print("\n")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║  PROFESSOR PERSONA - LEARNING VISUALIZATION DEMO         ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    
    await demo_diagram_visualization()
    await demo_code_execution()
    await demo_interactive_exercise()
    await demo_complete_learning_session()
    
    print("\n\n" + "="*60)
    print("✓ ALL DEMOS COMPLETE")
    print("="*60)
    print("\nThese actions are now available in Professor persona:")
    print("  • create_diagram_action()")
    print("  • create_code_execution_action()")
    print("  • create_exercise_action()")
    print("\nFrontend handlers are ready in app.js:")
    print("  • renderDiagram()")
    print("  • executeCodeInSandbox()")
    print("  • presentExercise()")
    print("\nCSS styling complete in main.css")
    print("\nReady to test in the Electron app!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
