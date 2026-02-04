"""
Curriculum Template Management System
Provides domain-based templates for creating structured learning curricula.
"""

import os
import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class TemplateSection:
    """Template section structure"""
    id: str
    title: str
    type: str  # "week", "subheading"
    order: int
    parent_id: Optional[str] = None
    description: str = ""
    concepts: List[str] = field(default_factory=list)
    estimated_time: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CurriculumTemplate:
    """Curriculum template definition"""
    id: str
    name: str
    category: str  # programming, framework, skill, problem-solving, exploration
    description: str
    customization_questions: List[str] = field(default_factory=list)
    structure: List[TemplateSection] = field(default_factory=list)
    estimated_duration: str = ""
    difficulty_levels: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['structure'] = [s.to_dict() if hasattr(s, 'to_dict') else s for s in self.structure]
        return data


class CurriculumTemplateManager:
    """
    Manages curriculum templates for different learning domains.
    Provides 5 built-in templates that adapt to any topic within their domain.
    """
    
    def __init__(self, vault_path: str = None):
        """
        Initialize template manager.
        
        Args:
            vault_path: Path to vault directory (optional, used for custom templates in future)
        """
        self.vault_path = vault_path
        self.templates_dir = os.path.join(vault_path, '.polly', 'curriculum-templates') if vault_path else None
        self._templates = self._initialize_builtin_templates()
        
        # Load custom templates from vault if available (Phase 23b)
        if self.templates_dir and os.path.exists(self.templates_dir):
            self._load_custom_templates()
    
    def _initialize_builtin_templates(self) -> Dict[str, CurriculumTemplate]:
        """Initialize the 5 built-in domain templates"""
        templates = {}
        
        # Template 1: Programming Language
        templates['programming-language'] = CurriculumTemplate(
            id='programming-language',
            name='Programming Language',
            category='programming',
            description='Learn any programming language systematically, from syntax to real projects',
            estimated_duration='8 weeks',
            difficulty_levels=['beginner', 'intermediate', 'advanced'],
            customization_questions=[
                'Which language are you learning?',
                "What's your programming experience level? (beginner/intermediate/advanced)",
                'What do you want to build with this language?',
                'Any specific areas of focus? (web, data, automation, systems, etc.)'
            ],
            structure=[
                TemplateSection(
                    id='week-1',
                    title='Week 1: Syntax & Fundamentals',
                    type='week',
                    order=0,
                    description='Master the basic syntax and core language features',
                    concepts=['syntax', 'data types', 'variables', 'operators'],
                    estimated_time='8-10 hours'
                ),
                TemplateSection(
                    id='week-1.1',
                    title='Basic Syntax and Data Types',
                    type='subheading',
                    order=0,
                    parent_id='week-1',
                    description='Learn core syntax, variables, and primitive types',
                    concepts=['syntax rules', 'naming conventions', 'data types', 'type conversion'],
                    estimated_time='3 hours'
                ),
                TemplateSection(
                    id='week-1.2',
                    title='Control Flow',
                    type='subheading',
                    order=1,
                    parent_id='week-1',
                    description='Master conditionals, loops, and program flow',
                    concepts=['if/else', 'loops', 'break/continue', 'match/switch'],
                    estimated_time='3 hours'
                ),
                TemplateSection(
                    id='week-1.3',
                    title='Functions and Scope',
                    type='subheading',
                    order=2,
                    parent_id='week-1',
                    description='Define and use functions, understand scope',
                    concepts=['function definition', 'parameters', 'return values', 'scope rules'],
                    estimated_time='2-4 hours'
                ),
                TemplateSection(
                    id='week-2',
                    title='Week 2: Core Concepts',
                    type='week',
                    order=1,
                    description='Essential language concepts and patterns',
                    concepts=['data structures', 'error handling', 'modules'],
                    estimated_time='8-10 hours'
                ),
                TemplateSection(
                    id='week-2.1',
                    title='Data Structures',
                    type='subheading',
                    order=0,
                    parent_id='week-2',
                    description='Built-in data structures and when to use them',
                    concepts=['arrays/lists', 'dictionaries/maps', 'sets', 'tuples'],
                    estimated_time='3-4 hours'
                ),
                TemplateSection(
                    id='week-2.2',
                    title='Error Handling',
                    type='subheading',
                    order=1,
                    parent_id='week-2',
                    description='Handle errors gracefully and debug effectively',
                    concepts=['exceptions', 'try/catch', 'error types', 'debugging'],
                    estimated_time='2-3 hours'
                ),
                TemplateSection(
                    id='week-2.3',
                    title='Modules and Imports',
                    type='subheading',
                    order=2,
                    parent_id='week-2',
                    description='Organize code and use external libraries',
                    concepts=['imports', 'packages', 'namespaces', 'package managers'],
                    estimated_time='3 hours'
                ),
                TemplateSection(
                    id='week-3',
                    title='Week 3: Paradigms & Patterns',
                    type='week',
                    order=2,
                    description='Programming paradigms and design patterns',
                    concepts=['OOP', 'functional programming', 'best practices'],
                    estimated_time='8-10 hours'
                ),
                TemplateSection(
                    id='week-3.1',
                    title='Object-Oriented Features',
                    type='subheading',
                    order=0,
                    parent_id='week-3',
                    description='Classes, inheritance, and OOP principles',
                    concepts=['classes', 'inheritance', 'polymorphism', 'encapsulation'],
                    estimated_time='3-4 hours'
                ),
                TemplateSection(
                    id='week-3.2',
                    title='Functional Features',
                    type='subheading',
                    order=1,
                    parent_id='week-3',
                    description='Functional programming concepts in this language',
                    concepts=['first-class functions', 'closures', 'higher-order functions', 'immutability'],
                    estimated_time='3 hours'
                ),
                TemplateSection(
                    id='week-3.3',
                    title='Best Practices & Idioms',
                    type='subheading',
                    order=2,
                    parent_id='week-3',
                    description='Write idiomatic, clean code',
                    concepts=['style guides', 'idioms', 'code organization', 'documentation'],
                    estimated_time='2-3 hours'
                ),
                TemplateSection(
                    id='week-4',
                    title='Week 4: Standard Library',
                    type='week',
                    order=3,
                    description='Master the standard library and common utilities',
                    concepts=['file I/O', 'string manipulation', 'common modules'],
                    estimated_time='8-10 hours'
                ),
                TemplateSection(
                    id='week-4.1',
                    title='File I/O and System Interaction',
                    type='subheading',
                    order=0,
                    parent_id='week-4',
                    description='Read/write files and interact with the system',
                    concepts=['file operations', 'paths', 'environment variables', 'CLI arguments'],
                    estimated_time='3 hours'
                ),
                TemplateSection(
                    id='week-4.2',
                    title='String and Data Manipulation',
                    type='subheading',
                    order=1,
                    parent_id='week-4',
                    description='Process and transform strings and data',
                    concepts=['string methods', 'regex', 'parsing', 'formatting'],
                    estimated_time='3-4 hours'
                ),
                TemplateSection(
                    id='week-4.3',
                    title='Common Utilities',
                    type='subheading',
                    order=2,
                    parent_id='week-4',
                    description='Essential standard library modules',
                    concepts=['date/time', 'math', 'collections', 'itertools'],
                    estimated_time='2-3 hours'
                ),
                TemplateSection(
                    id='week-5',
                    title='Week 5-6: Practical Applications',
                    type='week',
                    order=4,
                    description='Build real applications and use ecosystem tools',
                    concepts=['CLI tools', 'libraries', 'testing', 'debugging'],
                    estimated_time='12-16 hours'
                ),
                TemplateSection(
                    id='week-5.1',
                    title='Build a CLI Tool',
                    type='subheading',
                    order=0,
                    parent_id='week-5',
                    description='Create a command-line application',
                    concepts=['CLI design', 'argument parsing', 'user input', 'output formatting'],
                    estimated_time='4-6 hours'
                ),
                TemplateSection(
                    id='week-5.2',
                    title='Work with External Libraries',
                    type='subheading',
                    order=1,
                    parent_id='week-5',
                    description='Use popular third-party libraries',
                    concepts=['package installation', 'virtual environments', 'dependency management'],
                    estimated_time='3-4 hours'
                ),
                TemplateSection(
                    id='week-5.3',
                    title='Testing and Debugging',
                    type='subheading',
                    order=2,
                    parent_id='week-5',
                    description='Write tests and debug effectively',
                    concepts=['unit testing', 'debugging tools', 'test frameworks', 'TDD basics'],
                    estimated_time='5-6 hours'
                ),
                TemplateSection(
                    id='week-7',
                    title='Week 7-8: Real Project',
                    type='week',
                    order=5,
                    description='Build a complete project from scratch',
                    concepts=['project planning', 'implementation', 'refinement'],
                    estimated_time='12-16 hours'
                ),
                TemplateSection(
                    id='week-7.1',
                    title='Domain-Specific Project',
                    type='subheading',
                    order=0,
                    parent_id='week-7',
                    description='Build a project in your chosen domain',
                    concepts=['requirements gathering', 'architecture', 'implementation', 'iteration'],
                    estimated_time='8-12 hours'
                ),
                TemplateSection(
                    id='week-7.2',
                    title='Code Review and Refinement',
                    type='subheading',
                    order=1,
                    parent_id='week-7',
                    description='Polish code and learn from review',
                    concepts=['code review', 'refactoring', 'optimization', 'documentation'],
                    estimated_time='4 hours'
                ),
            ]
        )
        
        # Template 2: Framework/Library
        templates['framework-library'] = CurriculumTemplate(
            id='framework-library',
            name='Framework/Library',
            category='framework',
            description='Master any framework or library through progressive examples',
            estimated_duration='6-8 weeks',
            difficulty_levels=['beginner', 'intermediate', 'advanced'],
            customization_questions=[
                'Which framework/library are you learning?',
                'What language/ecosystem is it part of?',
                "What's your experience with similar tools?",
                'What do you want to build with it?'
            ],
            structure=[
                TemplateSection(
                    id='week-1',
                    title='Week 1: Setup & Core Concepts',
                    type='week',
                    order=0,
                    description='Environment setup and fundamental concepts',
                    concepts=['installation', 'configuration', 'core concepts', 'hello world'],
                    estimated_time='6-8 hours'
                ),
                TemplateSection(
                    id='week-1.1',
                    title='Installation and Setup',
                    type='subheading',
                    order=0,
                    parent_id='week-1',
                    description='Get the framework running locally',
                    concepts=['installation', 'dependencies', 'project structure', 'dev tools'],
                    estimated_time='2 hours'
                ),
                TemplateSection(
                    id='week-1.2',
                    title='Core Philosophy and Concepts',
                    type='subheading',
                    order=1,
                    parent_id='week-1',
                    description='Understand the framework\'s mental model',
                    concepts=['design philosophy', 'key concepts', 'terminology', 'architecture'],
                    estimated_time='2-3 hours'
                ),
                TemplateSection(
                    id='week-1.3',
                    title='First Example',
                    type='subheading',
                    order=2,
                    parent_id='week-1',
                    description='Build your first working example',
                    concepts=['basic example', 'file structure', 'build/run process'],
                    estimated_time='2-3 hours'
                ),
                TemplateSection(
                    id='week-2',
                    title='Week 2: Essential Features',
                    type='week',
                    order=1,
                    description='Master the core features you\'ll use daily',
                    concepts=['components', 'data flow', 'lifecycle', 'APIs'],
                    estimated_time='8-10 hours'
                ),
                TemplateSection(
                    id='week-2.1',
                    title='Component/Module System',
                    type='subheading',
                    order=0,
                    parent_id='week-2',
                    description='Build and compose components/modules',
                    concepts=['component structure', 'composition', 'props/inputs', 'reusability'],
                    estimated_time='3-4 hours'
                ),
                TemplateSection(
                    id='week-2.2',
                    title='Data Management',
                    type='subheading',
                    order=1,
                    parent_id='week-2',
                    description='Handle state and data flow',
                    concepts=['state management', 'data flow', 'updates', 'reactivity'],
                    estimated_time='3-4 hours'
                ),
                TemplateSection(
                    id='week-2.3',
                    title='Lifecycle and Events',
                    type='subheading',
                    order=2,
                    parent_id='week-2',
                    description='React to changes and user interactions',
                    concepts=['lifecycle hooks', 'event handling', 'side effects'],
                    estimated_time='2-3 hours'
                ),
                TemplateSection(
                    id='week-3',
                    title='Week 3: Advanced Patterns',
                    type='week',
                    order=2,
                    description='Learn advanced patterns and best practices',
                    concepts=['routing', 'forms', 'validation', 'optimization'],
                    estimated_time='8-10 hours'
                ),
                TemplateSection(
                    id='week-3.1',
                    title='Routing and Navigation',
                    type='subheading',
                    order=0,
                    parent_id='week-3',
                    description='Handle multiple pages/views',
                    concepts=['routing', 'navigation', 'params', 'guards'],
                    estimated_time='3 hours'
                ),
                TemplateSection(
                    id='week-3.2',
                    title='Forms and Validation',
                    type='subheading',
                    order=1,
                    parent_id='week-3',
                    description='Handle user input and validation',
                    concepts=['form handling', 'validation', 'error states', 'submission'],
                    estimated_time='3-4 hours'
                ),
                TemplateSection(
                    id='week-3.3',
                    title='Performance Optimization',
                    type='subheading',
                    order=2,
                    parent_id='week-3',
                    description='Optimize for performance',
                    concepts=['lazy loading', 'memoization', 'bundle size', 'profiling'],
                    estimated_time='2-3 hours'
                ),
                TemplateSection(
                    id='week-4',
                    title='Week 4: Integration & Tools',
                    type='week',
                    order=3,
                    description='Connect to external services and use ecosystem tools',
                    concepts=['API calls', 'authentication', 'testing', 'deployment'],
                    estimated_time='8-10 hours'
                ),
                TemplateSection(
                    id='week-4.1',
                    title='API Integration',
                    type='subheading',
                    order=0,
                    parent_id='week-4',
                    description='Fetch and manage external data',
                    concepts=['HTTP requests', 'async operations', 'error handling', 'caching'],
                    estimated_time='3-4 hours'
                ),
                TemplateSection(
                    id='week-4.2',
                    title='Authentication and Authorization',
                    type='subheading',
                    order=1,
                    parent_id='week-4',
                    description='Implement auth flows',
                    concepts=['authentication', 'tokens', 'sessions', 'protected routes'],
                    estimated_time='3 hours'
                ),
                TemplateSection(
                    id='week-4.3',
                    title='Testing',
                    type='subheading',
                    order=2,
                    parent_id='week-4',
                    description='Test your application',
                    concepts=['unit tests', 'integration tests', 'test frameworks', 'mocking'],
                    estimated_time='2-3 hours'
                ),
                TemplateSection(
                    id='week-5',
                    title='Week 5-6: Real Application',
                    type='week',
                    order=4,
                    description='Build a complete application',
                    concepts=['planning', 'implementation', 'deployment', 'iteration'],
                    estimated_time='12-16 hours'
                ),
                TemplateSection(
                    id='week-5.1',
                    title='Application Architecture',
                    type='subheading',
                    order=0,
                    parent_id='week-5',
                    description='Plan and structure your app',
                    concepts=['architecture', 'folder structure', 'patterns', 'scalability'],
                    estimated_time='2-3 hours'
                ),
                TemplateSection(
                    id='week-5.2',
                    title='Implementation',
                    type='subheading',
                    order=1,
                    parent_id='week-5',
                    description='Build the complete application',
                    concepts=['feature implementation', 'integration', 'debugging', 'refinement'],
                    estimated_time='8-10 hours'
                ),
                TemplateSection(
                    id='week-5.3',
                    title='Deployment and Polish',
                    type='subheading',
                    order=2,
                    parent_id='week-5',
                    description='Deploy and refine',
                    concepts=['deployment', 'CI/CD', 'monitoring', 'optimization'],
                    estimated_time='2-3 hours'
                ),
            ]
        )
        
        # Template 3: Technical Skill (continued in next message due to length)
        templates['skill-acquisition'] = CurriculumTemplate(
            id='skill-acquisition',
            name='Technical Skill',
            category='skill',
            description='Master any technical skill through deliberate practice',
            estimated_duration='4-6 weeks',
            difficulty_levels=['beginner', 'intermediate', 'advanced'],
            customization_questions=[
                'What skill do you want to learn?',
                "What's your starting point with this skill?",
                'What would mastery look like for you?',
                'How will you apply this skill?'
            ],
            structure=[
                TemplateSection(
                    id='week-1',
                    title='Week 1: Foundations',
                    type='week',
                    order=0,
                    description='Build fundamental understanding',
                    concepts=['core concepts', 'mental models', 'basics'],
                    estimated_time='6-8 hours'
                ),
                TemplateSection(
                    id='week-1.1',
                    title='Core Concepts',
                    type='subheading',
                    order=0,
                    parent_id='week-1',
                    description='Understand the fundamental concepts',
                    concepts=['key concepts', 'terminology', 'principles'],
                    estimated_time='2-3 hours'
                ),
                TemplateSection(
                    id='week-1.2',
                    title='Mental Models',
                    type='subheading',
                    order=1,
                    parent_id='week-1',
                    description='Develop mental models for the skill',
                    concepts=['how it works', 'why it matters', 'when to use'],
                    estimated_time='2 hours'
                ),
                TemplateSection(
                    id='week-1.3',
                    title='Basic Practice',
                    type='subheading',
                    order=2,
                    parent_id='week-1',
                    description='Start practicing the basics',
                    concepts=['simple exercises', 'feedback loops', 'basic techniques'],
                    estimated_time='2-3 hours'
                ),
                TemplateSection(
                    id='week-2',
                    title='Week 2: Techniques & Tools',
                    type='week',
                    order=1,
                    description='Learn the essential techniques',
                    concepts=['techniques', 'tools', 'workflows'],
                    estimated_time='6-8 hours'
                ),
                TemplateSection(
                    id='week-2.1',
                    title='Core Techniques',
                    type='subheading',
                    order=0,
                    parent_id='week-2',
                    description='Master the essential techniques',
                    concepts=['fundamental techniques', 'application', 'variations'],
                    estimated_time='3-4 hours'
                ),
                TemplateSection(
                    id='week-2.2',
                    title='Tools and Workflow',
                    type='subheading',
                    order=1,
                    parent_id='week-2',
                    description='Learn the tools of the trade',
                    concepts=['tools', 'workflows', 'efficiency', 'shortcuts'],
                    estimated_time='2-3 hours'
                ),
                TemplateSection(
                    id='week-2.3',
                    title='Deliberate Practice',
                    type='subheading',
                    order=2,
                    parent_id='week-2',
                    description='Practice with focus and feedback',
                    concepts=['focused practice', 'feedback', 'improvement'],
                    estimated_time='1-2 hours'
                ),
                TemplateSection(
                    id='week-3',
                    title='Week 3: Advanced Application',
                    type='week',
                    order=2,
                    description='Apply the skill in complex scenarios',
                    concepts=['advanced techniques', 'problem solving', 'integration'],
                    estimated_time='6-8 hours'
                ),
                TemplateSection(
                    id='week-3.1',
                    title='Advanced Techniques',
                    type='subheading',
                    order=0,
                    parent_id='week-3',
                    description='Learn advanced approaches',
                    concepts=['advanced methods', 'edge cases', 'optimization'],
                    estimated_time='3 hours'
                ),
                TemplateSection(
                    id='week-3.2',
                    title='Problem Solving',
                    type='subheading',
                    order=1,
                    parent_id='week-3',
                    description='Apply skill to real problems',
                    concepts=['real-world problems', 'debugging', 'troubleshooting'],
                    estimated_time='2-3 hours'
                ),
                TemplateSection(
                    id='week-3.3',
                    title='Integration',
                    type='subheading',
                    order=2,
                    parent_id='week-3',
                    description='Integrate with other skills',
                    concepts=['workflows', 'combination', 'efficiency'],
                    estimated_time='1-2 hours'
                ),
                TemplateSection(
                    id='week-4',
                    title='Week 4: Mastery Project',
                    type='week',
                    order=3,
                    description='Demonstrate mastery through project',
                    concepts=['project work', 'refinement', 'mastery'],
                    estimated_time='8-12 hours'
                ),
                TemplateSection(
                    id='week-4.1',
                    title='Capstone Project',
                    type='subheading',
                    order=0,
                    parent_id='week-4',
                    description='Complete a project demonstrating the skill',
                    concepts=['project execution', 'application', 'documentation'],
                    estimated_time='6-8 hours'
                ),
                TemplateSection(
                    id='week-4.2',
                    title='Review and Reflection',
                    type='subheading',
                    order=1,
                    parent_id='week-4',
                    description='Reflect on progress and next steps',
                    concepts=['self-assessment', 'future learning', 'continued practice'],
                    estimated_time='2-4 hours'
                ),
            ]
        )
        
        # Template 4: Problem-Solving Domain
        templates['problem-solving'] = CurriculumTemplate(
            id='problem-solving',
            name='Problem-Solving Domain',
            category='problem-solving',
            description='Master systematic problem-solving in a specific domain',
            estimated_duration='6-8 weeks',
            difficulty_levels=['beginner', 'intermediate', 'advanced'],
            customization_questions=[
                'What domain do you want to master? (algorithms, system design, debugging, etc.)',
                "What's your current level in this area?",
                'What types of problems do you want to solve?',
                'What resources do you have access to?'
            ],
            structure=[
                TemplateSection(
                    id='week-1',
                    title='Week 1: Problem-Solving Framework',
                    type='week',
                    order=0,
                    description='Learn systematic approach to problems',
                    concepts=['frameworks', 'patterns', 'strategies'],
                    estimated_time='6-8 hours'
                ),
                TemplateSection(
                    id='week-1.1',
                    title='Problem Analysis',
                    type='subheading',
                    order=0,
                    parent_id='week-1',
                    description='How to break down and understand problems',
                    concepts=['problem decomposition', 'constraints', 'requirements'],
                    estimated_time='2-3 hours'
                ),
                TemplateSection(
                    id='week-1.2',
                    title='Solution Strategies',
                    type='subheading',
                    order=1,
                    parent_id='week-1',
                    description='Common strategies and when to use them',
                    concepts=['strategies', 'trade-offs', 'selection criteria'],
                    estimated_time='2-3 hours'
                ),
                TemplateSection(
                    id='week-1.3',
                    title='Basic Patterns',
                    type='subheading',
                    order=2,
                    parent_id='week-1',
                    description='Fundamental problem patterns',
                    concepts=['common patterns', 'recognition', 'application'],
                    estimated_time='2 hours'
                ),
                TemplateSection(
                    id='week-2',
                    title='Week 2-3: Easy Problems',
                    type='week',
                    order=1,
                    description='Build confidence with straightforward problems',
                    concepts=['fundamentals', 'basic patterns', 'fluency'],
                    estimated_time='12-16 hours'
                ),
                TemplateSection(
                    id='week-2.1',
                    title='Easy Pattern 1',
                    type='subheading',
                    order=0,
                    parent_id='week-2',
                    description='First major pattern category',
                    concepts=['pattern details', 'variations', 'practice'],
                    estimated_time='4-6 hours'
                ),
                TemplateSection(
                    id='week-2.2',
                    title='Easy Pattern 2',
                    type='subheading',
                    order=1,
                    parent_id='week-2',
                    description='Second major pattern category',
                    concepts=['pattern details', 'variations', 'practice'],
                    estimated_time='4-6 hours'
                ),
                TemplateSection(
                    id='week-2.3',
                    title='Easy Pattern 3',
                    type='subheading',
                    order=2,
                    parent_id='week-2',
                    description='Third major pattern category',
                    concepts=['pattern details', 'variations', 'practice'],
                    estimated_time='4 hours'
                ),
                TemplateSection(
                    id='week-4',
                    title='Week 4-5: Medium Problems',
                    type='week',
                    order=2,
                    description='Tackle multi-step problems',
                    concepts=['combinations', 'complexity', 'optimization'],
                    estimated_time='12-16 hours'
                ),
                TemplateSection(
                    id='week-4.1',
                    title='Combined Patterns',
                    type='subheading',
                    order=0,
                    parent_id='week-4',
                    description='Problems requiring multiple patterns',
                    concepts=['pattern combination', 'strategy', 'practice'],
                    estimated_time='4-6 hours'
                ),
                TemplateSection(
                    id='week-4.2',
                    title='Optimization',
                    type='subheading',
                    order=1,
                    parent_id='week-4',
                    description='Improve time and space complexity',
                    concepts=['optimization techniques', 'trade-offs', 'analysis'],
                    estimated_time='4-6 hours'
                ),
                TemplateSection(
                    id='week-4.3',
                    title='Edge Cases',
                    type='subheading',
                    order=2,
                    parent_id='week-4',
                    description='Handle edge cases and constraints',
                    concepts=['edge cases', 'validation', 'robustness'],
                    estimated_time='4 hours'
                ),
                TemplateSection(
                    id='week-6',
                    title='Week 6-8: Hard Problems',
                    type='week',
                    order=3,
                    description='Master challenging problems',
                    concepts=['complex patterns', 'advanced techniques', 'creativity'],
                    estimated_time='16-20 hours'
                ),
                TemplateSection(
                    id='week-6.1',
                    title='Advanced Patterns',
                    type='subheading',
                    order=0,
                    parent_id='week-6',
                    description='Complex problem patterns',
                    concepts=['advanced patterns', 'techniques', 'practice'],
                    estimated_time='6-8 hours'
                ),
                TemplateSection(
                    id='week-6.2',
                    title='Creative Solutions',
                    type='subheading',
                    order=1,
                    parent_id='week-6',
                    description='Develop novel approaches',
                    concepts=['creativity', 'insight', 'breakthrough'],
                    estimated_time='6-8 hours'
                ),
                TemplateSection(
                    id='week-6.3',
                    title='Mock Practice',
                    type='subheading',
                    order=2,
                    parent_id='week-6',
                    description='Simulate real conditions',
                    concepts=['timed practice', 'pressure', 'performance'],
                    estimated_time='4 hours'
                ),
            ]
        )
        
        # Template 5: Domain Exploration
        templates['domain-exploration'] = CurriculumTemplate(
            id='domain-exploration',
            name='Domain Exploration',
            category='exploration',
            description='Explore and understand a new domain systematically',
            estimated_duration='4-6 weeks',
            difficulty_levels=['beginner', 'intermediate'],
            customization_questions=[
                'What domain do you want to explore?',
                'Why are you interested in this domain?',
                'What level of depth are you aiming for?',
                'What will you do with this knowledge?'
            ],
            structure=[
                TemplateSection(
                    id='week-1',
                    title='Week 1: Landscape Survey',
                    type='week',
                    order=0,
                    description='Map out the domain and key concepts',
                    concepts=['overview', 'key concepts', 'terminology'],
                    estimated_time='6-8 hours'
                ),
                TemplateSection(
                    id='week-1.1',
                    title='Domain Overview',
                    type='subheading',
                    order=0,
                    parent_id='week-1',
                    description='Understand the big picture',
                    concepts=['history', 'purpose', 'scope', 'applications'],
                    estimated_time='2-3 hours'
                ),
                TemplateSection(
                    id='week-1.2',
                    title='Key Concepts',
                    type='subheading',
                    order=1,
                    parent_id='week-1',
                    description='Learn fundamental concepts',
                    concepts=['core concepts', 'terminology', 'relationships'],
                    estimated_time='2-3 hours'
                ),
                TemplateSection(
                    id='week-1.3',
                    title='Domain Map',
                    type='subheading',
                    order=2,
                    parent_id='week-1',
                    description='Create mental map of the domain',
                    concepts=['structure', 'connections', 'sub-domains'],
                    estimated_time='2 hours'
                ),
                TemplateSection(
                    id='week-2',
                    title='Week 2: Deep Dive into Fundamentals',
                    type='week',
                    order=1,
                    description='Understand core principles and theories',
                    concepts=['principles', 'theories', 'models'],
                    estimated_time='8-10 hours'
                ),
                TemplateSection(
                    id='week-2.1',
                    title='Core Principles',
                    type='subheading',
                    order=0,
                    parent_id='week-2',
                    description='Master fundamental principles',
                    concepts=['first principles', 'axioms', 'laws'],
                    estimated_time='3-4 hours'
                ),
                TemplateSection(
                    id='week-2.2',
                    title='Theories and Models',
                    type='subheading',
                    order=1,
                    parent_id='week-2',
                    description='Understand key theories',
                    concepts=['major theories', 'models', 'frameworks'],
                    estimated_time='3-4 hours'
                ),
                TemplateSection(
                    id='week-2.3',
                    title='Case Studies',
                    type='subheading',
                    order=2,
                    parent_id='week-2',
                    description='Learn through examples',
                    concepts=['real examples', 'applications', 'lessons'],
                    estimated_time='2 hours'
                ),
                TemplateSection(
                    id='week-3',
                    title='Week 3: Practical Applications',
                    type='week',
                    order=2,
                    description='See how the domain is applied',
                    concepts=['applications', 'tools', 'practices'],
                    estimated_time='8-10 hours'
                ),
                TemplateSection(
                    id='week-3.1',
                    title='Common Applications',
                    type='subheading',
                    order=0,
                    parent_id='week-3',
                    description='Where and how it\'s used',
                    concepts=['use cases', 'industries', 'examples'],
                    estimated_time='3 hours'
                ),
                TemplateSection(
                    id='week-3.2',
                    title='Tools and Techniques',
                    type='subheading',
                    order=1,
                    parent_id='week-3',
                    description='Learn the tools practitioners use',
                    concepts=['tools', 'techniques', 'methodologies'],
                    estimated_time='3-4 hours'
                ),
                TemplateSection(
                    id='week-3.3',
                    title='Hands-On Exploration',
                    type='subheading',
                    order=2,
                    parent_id='week-3',
                    description='Try it yourself',
                    concepts=['experiments', 'practice', 'exploration'],
                    estimated_time='2-3 hours'
                ),
                TemplateSection(
                    id='week-4',
                    title='Week 4: Connections & Next Steps',
                    type='week',
                    order=3,
                    description='Connect to other domains and plan future learning',
                    concepts=['connections', 'integration', 'future paths'],
                    estimated_time='4-6 hours'
                ),
                TemplateSection(
                    id='week-4.1',
                    title='Cross-Domain Connections',
                    type='subheading',
                    order=0,
                    parent_id='week-4',
                    description='How this connects to what you know',
                    concepts=['connections', 'analogies', 'integration'],
                    estimated_time='2 hours'
                ),
                TemplateSection(
                    id='week-4.2',
                    title='Synthesis and Reflection',
                    type='subheading',
                    order=1,
                    parent_id='week-4',
                    description='Synthesize your understanding',
                    concepts=['synthesis', 'reflection', 'insights'],
                    estimated_time='1-2 hours'
                ),
                TemplateSection(
                    id='week-4.3',
                    title='Future Learning Paths',
                    type='subheading',
                    order=2,
                    parent_id='week-4',
                    description='Plan next steps in this domain',
                    concepts=['next steps', 'resources', 'specialization'],
                    estimated_time='1-2 hours'
                ),
            ]
        )
        
        return templates
    
    def _load_custom_templates(self):
        """Load custom templates from vault (Phase 23b)"""
        # Placeholder for future feature
        pass
    
    def list_templates(self, category: Optional[str] = None) -> List[CurriculumTemplate]:
        """
        List available templates, optionally filtered by category.
        
        Args:
            category: Filter by category (programming, framework, skill, problem-solving, exploration)
            
        Returns:
            List of templates
        """
        templates = list(self._templates.values())
        
        if category:
            templates = [t for t in templates if t.category == category]
        
        return templates
    
    def get_template(self, template_id: str) -> Optional[CurriculumTemplate]:
        """
        Get specific template by ID.
        
        Args:
            template_id: Template identifier
            
        Returns:
            Template or None if not found
        """
        return self._templates.get(template_id)
    
    def detect_template(self, goal: str) -> Optional[Dict[str, Any]]:
        """
        Detect appropriate template based on learning goal.
        Uses keyword matching to recommend template.
        
        Args:
            goal: User's learning goal
            
        Returns:
            Dict with template_id, confidence, and reasoning
        """
        goal_lower = goal.lower()
        
        # Programming language keywords
        prog_langs = ['python', 'javascript', 'java', 'rust', 'go', 'c++', 'c#', 'ruby', 
                      'swift', 'kotlin', 'typescript', 'php', 'scala', 'elixir', 'clojure']
        prog_keywords = ['language', 'syntax', 'programming']
        
        # Framework/library keywords
        framework_names = ['react', 'vue', 'angular', 'django', 'flask', 'rails', 'spring',
                          'express', 'nextjs', 'svelte', 'tensorflow', 'pytorch', 'pandas']
        framework_keywords = ['framework', 'library', 'package']
        
        # Skill keywords
        skill_keywords = ['debugging', 'refactoring', 'testing', 'profiling', 'git',
                         'docker', 'kubernetes', 'sql', 'regex', 'api design']
        
        # Problem-solving keywords
        problem_keywords = ['algorithms', 'data structures', 'leetcode', 'system design',
                           'competitive programming', 'problem solving', 'interviews']
        
        # Exploration keywords
        explore_keywords = ['understand', 'learn about', 'explore', 'overview', 
                           'introduction to', 'what is', 'get into']
        
        # Check for programming language
        if any(lang in goal_lower for lang in prog_langs) or \
           any(kw in goal_lower for kw in prog_keywords):
            return {
                'template_id': 'programming-language',
                'confidence': 0.9,
                'reasoning': 'Goal mentions a programming language or language learning'
            }
        
        # Check for framework/library
        if any(fw in goal_lower for fw in framework_names) or \
           any(kw in goal_lower for kw in framework_keywords):
            return {
                'template_id': 'framework-library',
                'confidence': 0.9,
                'reasoning': 'Goal mentions a framework or library'
            }
        
        # Check for problem-solving domain
        if any(kw in goal_lower for kw in problem_keywords):
            return {
                'template_id': 'problem-solving',
                'confidence': 0.85,
                'reasoning': 'Goal is about problem-solving or algorithms'
            }
        
        # Check for skill acquisition
        if any(kw in goal_lower for kw in skill_keywords):
            return {
                'template_id': 'skill-acquisition',
                'confidence': 0.85,
                'reasoning': 'Goal is about learning a specific technical skill'
            }
        
        # Check for domain exploration
        if any(kw in goal_lower for kw in explore_keywords):
            return {
                'template_id': 'domain-exploration',
                'confidence': 0.7,
                'reasoning': 'Goal indicates exploratory learning'
            }
        
        # Default to domain exploration with lower confidence
        return {
            'template_id': 'domain-exploration',
            'confidence': 0.5,
            'reasoning': 'Could not confidently detect template, defaulting to domain exploration'
        }
    
    def create_from_template(
        self, 
        template_id: str, 
        customizations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create curriculum structure from template with customizations.
        
        Args:
            template_id: Template to use
            customizations: Dict with user's answers to customization questions
            
        Returns:
            Dict with curriculum data ready for CurriculumManager.create_curriculum()
        """
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        # Create base curriculum structure
        curriculum_data = {
            'title': customizations.get('title', f"Learning: {customizations.get('topic', 'Unknown')}"),
            'goal': customizations.get('goal', ''),
            'current_level': customizations.get('level', 'beginner'),
            'estimated_duration': template.estimated_duration,
            'template_id': template_id,
            'sections': []
        }
        
        # Convert template sections to curriculum sections
        for section in template.structure:
            curriculum_data['sections'].append({
                'id': section.id,
                'title': section.title,
                'type': section.type,
                'order': section.order,
                'parent_id': section.parent_id,
                'description': section.description,
                'concepts': section.concepts,
                'estimated_time': section.estimated_time
            })
        
        return curriculum_data
