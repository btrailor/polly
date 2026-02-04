"""
Professor Persona (Phase 20 + Phase 22 Combined)

The Professor persona is designed for teaching, learning, and knowledge transfer
through Socratic dialogue, structured explanations, curriculum design, and assessment.

Modes:
- Explain: Clear explanations with examples and analogies
- Socratic: Guided discovery through questioning (Socratic method + Freire's pedagogy)
- Curriculum: Design structured learning paths
- Quiz: Test understanding and provide feedback

Model Routing:
- Explain mode: Balanced tier (Sonnet 4 preferred)
- Socratic mode: Balanced tier (Sonnet 4 preferred) - needs reasoning
- Curriculum mode: Balanced tier (Sonnet 4 preferred)
- Quiz mode: Balanced tier (Sonnet 4 preferred)
"""

from typing import Dict, List, Optional, Any
import json
import logging
from datetime import datetime
from pathlib import Path

from ..base import AgentPersona, PersonaContext, PersonaResponse, PersonaAction
from core.router_v2 import TaskType, ConfidenceLevel

logger = logging.getLogger(__name__)


class ProfessorPersona(AgentPersona):
    """
    Professor persona for teaching, learning, and knowledge transfer.
    
    Primary use cases:
    - Explain concepts clearly (Explain mode)
    - Guide discovery through questions (Socratic mode) - Phase 22 Teaching Mode
    - Design learning paths (Curriculum mode)
    - Test understanding (Quiz mode)
    
    Workflow Examples:
    
    1. Socratic Teaching (Phase 22):
       User: "Teach me about async/await"
       Professor activates in Socratic mode
       Professor asks about prior knowledge
       Professor guides discovery through questions
       Professor checks understanding
       Professor offers to create learning note
    
    2. Explanation:
       User: "Explain how recursion works"
       Professor activates in Explain mode
       Professor provides structured explanation
       Professor uses examples and analogies
       Professor checks understanding
    
    3. Curriculum Design:
       User: "Create a learning path for Python"
       Professor activates in Curriculum mode
       Professor assesses current knowledge
       Professor designs progressive learning path
       Professor suggests milestones and resources
    """
    
    def __init__(self, name: str, router: Any, skill_manager: Any = None, rag: Any = None, learning_tracker: Any = None, curriculum_manager: Any = None, template_manager: Any = None):
        """
        Initialize Professor persona.
        
        Args:
            name: Persona name ("professor")
            router: IntelligentRouterV2 instance for LLM calls
            skill_manager: SkillManager instance for loading skills
            rag: UnifiedRAG instance for KB search
            learning_tracker: LearningTracker instance for progress tracking (Phase 22)
            curriculum_manager: CurriculumManager instance for curriculum CRUD (Phase 23)
            template_manager: CurriculumTemplateManager instance for templates (Phase 23)
        """
        super().__init__(name, router)
        self.skill_manager = skill_manager
        self.rag = rag
        self.learning_tracker = learning_tracker
        self.curriculum_manager = curriculum_manager
        self.template_manager = template_manager
        
        logger.info(f"Initialized Professor persona (skills: {skill_manager is not None}, "
                   f"rag: {rag is not None}, tracker: {learning_tracker is not None}, "
                   f"curriculum: {curriculum_manager is not None}, templates: {template_manager is not None})")
    
    @property
    def default_mode(self) -> str:
        return "socratic"  # Default to Socratic mode for teaching
    
    @property
    def available_modes(self) -> List[str]:
        return ["explain", "socratic", "curriculum", "quiz"]
    
    async def process(self, context: PersonaContext) -> PersonaResponse:
        """
        Route to appropriate mode handler.
        
        Args:
            context: PersonaContext with user message and conversation
        
        Returns:
            PersonaResponse from mode-specific handler
        """
        mode = self.state.current_mode
        
        logger.info(f"Professor processing in {mode} mode")
        
        if mode == "explain":
            return await self.explain(context)
        elif mode == "socratic":
            return await self.socratic(context)
        elif mode == "curriculum":
            return await self.curriculum(context)
        elif mode == "quiz":
            return await self.quiz(context)
        else:
            raise ValueError(f"Unknown mode: {mode}")
    
    def get_mode_prompts(self) -> Dict[str, str]:
        """
        Return mode-specific system prompts.
        
        Prompts are loaded from professor.yaml definition file by PersonaManager.
        This is a fallback if YAML loading fails.
        """
        return {
            "explain": "You are Professor in Explain mode. Explain concepts clearly with examples.",
            "socratic": "You are Professor in Socratic mode. Guide discovery through questions.",
            "curriculum": "You are Professor in Curriculum mode. Design structured learning paths.",
            "quiz": "You are Professor in Quiz mode. Test understanding with constructive feedback."
        }
    
    # ========== Explain Mode ==========
    
    async def explain(self, context: PersonaContext) -> PersonaResponse:
        """
        Explain mode: Provide clear explanations with examples and analogies.
        
        Process:
        1. Identify the concept to explain
        2. Check if skill package exists for this topic
        3. If skill package exists, use diagrams and exercises
        4. Otherwise, generate explanation with LLM
        5. Check understanding
        6. Suggest related concepts
        
        Args:
            context: PersonaContext with user request
        
        Returns:
            PersonaResponse with structured explanation (potentially with actions)
        """
        logger.info("Professor Explain mode: providing explanation")
        
        # Extract topic and check for skill package
        topic = self._extract_topic_from_context(context)
        skill_data = None
        actions = []
        
        if topic:
            # Try to load skill package
            skill_name = topic.lower().replace(" ", "-")
            skill_data = self.load_skill(skill_name)
            
            if skill_data:
                logger.info(f"Found skill package for topic: {topic}")
                
                # Add first diagram if available
                if skill_data['diagrams']:
                    first_diagram = skill_data['diagrams'][0]
                    actions.append(self.create_diagram_action(
                        diagram_type="mermaid",
                        source=first_diagram['source'],
                        caption=f"{topic}: {first_diagram['name'].replace('-', ' ').title()}",
                        interactive=True
                    ))
                
                # Enhance LLM prompt with skill content
                skill_context = f"\n\nSKILL PACKAGE AVAILABLE:\n{skill_data['skill_md'][:1000]}..."
                context.message += skill_context
        
        # Build messages for LLM
        messages = self._build_messages(context, include_history=True)
        
        # Add instruction about available visualizations
        if skill_data:
            messages[-1]['content'] += (
                f"\n\nYou have access to {len(skill_data['diagrams'])} diagrams "
                f"and {len(skill_data['exercises'])} exercises for this topic. "
                "Mention that visual aids are being shown."
            )
        
        # Use balanced tier for explanations
        try:
            response = await self.router.complete_with_fallback(
                messages=messages,
                task_type=TaskType.CREATIVE,
                confidence=ConfidenceLevel.BALANCED,
                max_tokens=3000,
                temperature=0.7
            )
        except Exception as e:
            logger.error(f"Router failed in explain mode: {e}")
            return PersonaResponse(
                content=f"Sorry, I encountered an error while preparing the explanation: {str(e)}",
                mode="explain",
                actions=[],
                metadata={"error": str(e)}
            )
        
        # Record learning
        if topic and self.learning_tracker:
            self.learning_tracker.record_learning(
                title=topic,
                domain="glyphs",
                concepts=[topic],
                mastery_level=1
            )
        
        return PersonaResponse(
            content=response.content,
            mode="explain",
            actions=actions,
            metadata={
                "topic": topic,
                "has_skill_package": skill_data is not None,
                "model_used": response.model,
                "tokens": response.usage.get("total_tokens", 0) if response.usage else 0
            }
        )
    
    # ========== Socratic Mode (Phase 22 Teaching Mode) ==========
    
    async def socratic(self, context: PersonaContext) -> PersonaResponse:
        """
        Socratic mode: Guide discovery through questions.
        
        This is the core of Phase 22 Teaching Mode. Uses:
        - Socratic method (questioning over telling)
        - Freire's problem-posing pedagogy
        - Progressive difficulty
        - Understanding checks
        - Learning note creation offers
        
        Process:
        1. Assess prior knowledge through questions
        2. Probe current understanding
        3. Guide discovery with leading questions
        4. Adapt difficulty based on responses
        5. Check understanding before proceeding
        6. Offer to create learning note when concept grasped
        
        Args:
            context: PersonaContext with user responses
        
        Returns:
            PersonaResponse with guiding questions or learning note offer
        """
        logger.info("Professor Socratic mode: guiding discovery")
        
        # Check if user wants to create a learning note
        if self._detect_note_creation_request(context):
            return await self._offer_learning_note_creation(context)
        
        # Build messages for LLM
        messages = self._build_messages(context, include_history=True)
        
        # Add Socratic guidance emphasis
        messages.append({
            "role": "system",
            "content": ("Remember: Ask questions to guide discovery. Don't provide direct answers. "
                       "Build on their responses. Check understanding. Be patient and encouraging.")
        })
        
        # Use balanced tier for reasoning-heavy Socratic dialogue
        try:
            response = await self.router.complete_with_fallback(
                messages=messages,
                task_type=TaskType.CREATIVE,  # Socratic teaching requires creative questioning
                confidence=ConfidenceLevel.BALANCED,
                max_tokens=2000,
                temperature=0.7
            )
        except Exception as e:
            logger.error(f"Router failed in socratic mode: {e}")
            return PersonaResponse(
                content=f"Sorry, I encountered an error during our dialogue: {str(e)}",
                mode="socratic",
                actions=[],
                metadata={"error": str(e)}
            )
        
        # Track learning progress
        topic = self._extract_topic_from_context(context)
        mastery_level = self._estimate_mastery_from_dialogue(context)
        
        if topic and self.learning_tracker and mastery_level:
            self.learning_tracker.record_learning(
                title=topic,
                domain="glyphs",
                concepts=[topic],
                mastery_level=mastery_level
            )
        
        return PersonaResponse(
            content=response.content,
            mode="socratic",
            actions=[],
            metadata={
                "topic": topic,
                "estimated_mastery": mastery_level,
                "model_used": response.model,
                "tokens": response.usage.get("total_tokens", 0) if response.usage else 0
            }
        )
    
    # ========== Curriculum Mode ==========
    
    async def curriculum(self, context: PersonaContext) -> PersonaResponse:
        """
        Curriculum mode: Design structured learning paths.
        
        Phase 23 Enhancement: Detects if user wants a structured curriculum
        and generates a reviewable outline using templates.
        
        Process:
        1. Detect if structured curriculum request
        2. If yes: Use template system to generate structured curriculum
           - Detect appropriate template
           - Generate curriculum outline with LLM
           - Parse outline into sections
           - Return review_curriculum action
        3. If no: Generate simple learning path (legacy behavior)
        
        Args:
            context: PersonaContext with learning goal
        
        Returns:
            PersonaResponse with structured learning path or curriculum review action
        """
        logger.info("Professor Curriculum mode: designing learning path")
        
        # Extract goal/topic
        goal = self._extract_topic_from_context(context) or context.user_message
        
        # Check if structured curriculum request (Phase 23)
        is_structured_request = self._detect_structured_curriculum_request(context)
        
        if is_structured_request:
            logger.info("Detected structured curriculum request - using Phase 23 flow")
            return await self._generate_structured_curriculum(context, goal)
        
        # Legacy flow: Simple learning path
        logger.info("Generating simple learning path (legacy mode)")
        
        # Search KB for related materials (if RAG available)
        related_notes = []
        if self.rag:
            try:
                if goal:
                    results = await self.rag.search(
                        query=goal,
                        top_k=5,
                        filters={"domain": "glyphs"}  # Learning materials
                    )
                    related_notes = [r.get("title", r.get("file_path", "")) for r in results]
            except Exception as e:
                logger.warning(f"KB search failed in curriculum mode: {e}")
        
        # Build messages for LLM
        messages = self._build_messages(context, include_history=True)
        
        # Add related notes context
        if related_notes:
            messages.append({
                "role": "system",
                "content": f"User's existing notes on related topics: {', '.join(related_notes)}"
            })
        
        # Use balanced tier for curriculum design
        try:
            response = await self.router.complete_with_fallback(
                messages=messages,
                task_type=TaskType.CREATIVE,
                confidence=ConfidenceLevel.BALANCED,
                max_tokens=4000,
                temperature=0.7
            )
        except Exception as e:
            logger.error(f"Router failed in curriculum mode: {e}")
            return PersonaResponse(
                content=f"Sorry, I encountered an error while designing the curriculum: {str(e)}",
                mode="curriculum",
                actions=[],
                metadata={"error": str(e)}
            )
        
        # Offer to save as note
        actions = [PersonaAction(
            type="offer_save_as_note",
            data={
                "note_type": "learning_path",
                "domain": "glyphs",
                "suggested_title": f"Learning Path - {goal}"
            }
        )]
        
        return PersonaResponse(
            content=response.content,
            mode="curriculum",
            actions=actions,
            metadata={
                "related_notes_found": len(related_notes),
                "model_used": response.model,
                "tokens": response.usage.get("total_tokens", 0) if response.usage else 0
            }
        )
    
    # ========== Quiz Mode ==========
    
    async def quiz(self, context: PersonaContext) -> PersonaResponse:
        """
        Quiz mode: Test understanding and provide feedback.
        
        Process:
        1. Generate questions based on topic and difficulty
        2. Present questions one-by-one or all at once
        3. Evaluate answers
        4. Provide constructive feedback
        5. Identify knowledge gaps
        6. Suggest review materials
        
        Args:
            context: PersonaContext with quiz request or answers
        
        Returns:
            PersonaResponse with questions or feedback
        """
        logger.info("Professor Quiz mode: testing understanding")
        
        # Build messages for LLM
        messages = self._build_messages(context, include_history=True)
        
        # Use balanced tier for quiz generation/evaluation
        try:
            response = await self.router.complete_with_fallback(
                messages=messages,
                task_type=TaskType.CREATIVE,  # Quiz mode requires creative question generation
                confidence=ConfidenceLevel.BALANCED,
                max_tokens=2500,
                temperature=0.7
            )
        except Exception as e:
            logger.error(f"Router failed in quiz mode: {e}")
            return PersonaResponse(
                content=f"Sorry, I encountered an error during the quiz: {str(e)}",
                mode="quiz",
                actions=[],
                metadata={"error": str(e)}
            )
        
        return PersonaResponse(
            content=response.content,
            mode="quiz",
            actions=[],
            metadata={
                "model_used": response.model,
                "tokens": response.usage.get("total_tokens", 0) if response.usage else 0
            }
        )
    
    # ========== Helper Methods ==========
    
    def _extract_topic_from_context(self, context: PersonaContext) -> Optional[str]:
        """Extract the learning topic from context."""
        # Simple extraction - look for "teach me about X", "explain Y", etc.
        message = context.user_message.lower()
        
        patterns = [
            r"teach me (?:about )?(.+)",
            r"explain (.+)",
            r"how (?:do|does) (.+) work",
            r"what is (.+)",
            r"learn(?:ing)? (?:about )?(.+)",
            r"understand(?:ing)? (.+)"
        ]
        
        for pattern in patterns:
            import re
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                topic = match.group(1).strip().rstrip("?")
                return topic.title()
        
        return None
    
    def _extract_template_from_message(self, message: str) -> Optional[str]:
        """
        Extract template ID from user message.
        
        Looks for phrases like:
        - "using the Programming Language template"
        - "with the Framework template"
        - "use Technical Skill template"
        
        Args:
            message: User's message
            
        Returns:
            Template ID if found, None otherwise
        """
        if not message or 'template' not in message.lower():
            return None
        
        message_lower = message.lower()
        
        # Map of keywords to template IDs
        template_mapping = {
            'programming language': 'programming-language',
            'framework': 'framework-library',
            'library': 'framework-library',
            'technical skill': 'skill-acquisition',
            'skill acquisition': 'skill-acquisition',
            'problem-solving': 'problem-solving',
            'problem solving': 'problem-solving',
            'domain exploration': 'domain-exploration',
            'exploration': 'domain-exploration'
        }
        
        # Look for template name keywords
        for keyword, template_id in template_mapping.items():
            if keyword in message_lower:
                return template_id
        
        return None
    
    def _detect_structured_curriculum_request(self, context: PersonaContext) -> bool:
        """
        Detect if user wants a structured curriculum (Phase 23).
        
        Returns True if user wants a full curriculum system with progress tracking,
        False if they just want a simple learning path or advice.
        
        Keywords that indicate structured curriculum:
        - "curriculum", "course", "structured", "program"
        - "learn [language/framework]" (without "about")
        - "master", "become proficient"
        
        Args:
            context: PersonaContext
        
        Returns:
            True if structured curriculum request detected
        """
        import re
        message = context.user_message.lower()
        
        # Strong indicators for structured curriculum
        structured_keywords = [
            r'\bcurriculum\b',
            r'\bcourse\b',
            r'\bprogram\b',
            r'\bstructured.*path\b',
            r'\blearning plan\b',
            r'\bstudy.*plan\b',
            r'\bmaster\b',
            r'\bbecome proficient\b',
            r'\blearn\s+(python|javascript|rust|go|java|typescript|react|django|vue|angular)',  # Specific tech
            r'\bi want to learn\s+\w+',  # "I want to learn X"
            r'\bcreate.*curriculum\b',
            r'\bdesign.*curriculum\b'
        ]
        
        for pattern in structured_keywords:
            if re.search(pattern, message, re.IGNORECASE):
                logger.info(f"Detected structured curriculum request: '{pattern}'")
                return True
        
        # Weak indicators (need context)
        # If conversation is short and user says "learn X", likely want structured path
        if len(context.conversation_history) <= 2:
            if re.search(r'\blearn\s+\w+', message):
                logger.info("Short conversation + 'learn X' - treating as structured request")
                return True
        
        return False
    
    async def _generate_structured_curriculum(self, context: PersonaContext, goal: str) -> PersonaResponse:
        """
        Generate a structured curriculum using template system (Phase 23).
        
        Process:
        1. Detect appropriate template
        2. Ask customization questions (if not already answered)
        3. Generate curriculum outline with LLM using template + answers
        4. Parse outline into structured sections
        5. Return review_curriculum action
        
        Args:
            context: PersonaContext
            goal: Learning goal/topic
        
        Returns:
            PersonaResponse with show_questions or review_curriculum action
        """
        import re
        
        # Step 1: Detect template
        template_detection = None
        detected_template = None
        
        if self.template_manager:
            try:
                template_detection = self.template_manager.detect_template(goal)
                
                if template_detection and template_detection.get('confidence', 0) >= 0.5:
                    template_id = template_detection['template_id']
                    detected_template = self.template_manager.get_template(template_id)
                    logger.info(f"Detected template: {template_id} (confidence: {template_detection['confidence']})")
            except Exception as e:
                logger.warning(f"Template detection failed: {e}")
        else:
            logger.warning("template_manager not available")
        
        # Step 2: Check for user-specified template override
        template_override = self._extract_template_from_message(context.user_message)
        if template_override and self.template_manager:
            override_template = self.template_manager.get_template(template_override)
            if override_template:
                detected_template = override_template
                template_detection = {
                    'template_id': template_override,
                    'confidence': 1.0,
                    'reasoning': 'User explicitly requested this template'
                }
                logger.info(f"Using user-specified template: {template_override}")
        
        # Step 3: Generate outline with LLM
        messages = self._build_messages(context, include_history=True)
        
        # Add instruction to generate structured curriculum outline
        curriculum_prompt = f"""Generate a comprehensive structured curriculum for learning: {goal}

Please create a detailed curriculum outline in the following format:

# [Curriculum Title]

**Goal:** [Clear learning objective]

**Duration:** [Estimated total time, e.g., "8 weeks"]

"""
        
        if detected_template:
            # Convert template object to dict
            template_dict = detected_template.to_dict() if hasattr(detected_template, 'to_dict') else detected_template
            curriculum_prompt += f"""**Template:** {template_dict['name']}

Use this template structure as a guide:
{json.dumps(template_dict, indent=2)[:500]}...

"""
        
        curriculum_prompt += """Format your response EXACTLY as follows. Do NOT include any conversational text before or after the structured outline. Start immediately with the # heading:

# [Curriculum Title]

**Goal:** [Clear learning objective]

**Duration:** [Estimated total time, e.g., "8 weeks"]

## Week 1: [Week Title]

### 1.1 [Section Title]
[Brief description of what will be learned]
**Concepts:** concept1, concept2, concept3
**Time:** X hours

### 1.2 [Section Title]
[Brief description]
**Concepts:** concept1, concept2
**Time:** X hours

## Week 2: [Week Title]

### 2.1 [Section Title]
...

Make it comprehensive, progressive, and practical. Include 15-25 total sections across multiple weeks."""
        
        messages.append({
            "role": "user",
            "content": curriculum_prompt
        })
        
        try:
            response = await self.router.complete_with_fallback(
                messages=messages,
                task_type=TaskType.CREATIVE,
                confidence=ConfidenceLevel.BALANCED,
                max_tokens=6000,
                temperature=0.7
            )
            
            outline_text = response.content
            logger.info(f"[Curriculum Generation] LLM response length: {len(outline_text)} chars")
            logger.debug(f"[Curriculum Generation] LLM response preview: {outline_text[:500]}")
            
            # Strip any conversational preamble (text before first # heading)
            try:
                first_heading = outline_text.find('\n#')
                if first_heading > 0:
                    logger.info(f"[Curriculum Generation] Stripping {first_heading} chars of preamble")
                    outline_text = outline_text[first_heading+1:]
                elif outline_text.startswith('#'):
                    # Already starts with heading, good
                    pass
                else:
                    # Try to find ## Week pattern
                    first_week = outline_text.find('\n## Week')
                    if first_week > 0:
                        logger.info(f"[Curriculum Generation] Stripping {first_week} chars of preamble (no # title found)")
                        outline_text = outline_text[first_week+1:]
            except Exception as strip_error:
                logger.warning(f"[Curriculum Generation] Failed to strip preamble: {strip_error}")
                # Continue with original text
            
        except Exception as e:
            logger.error(f"Failed to generate curriculum outline: {e}")
            return PersonaResponse(
                content=f"Sorry, I encountered an error while generating the curriculum: {str(e)}",
                mode="curriculum",
                actions=[],
                metadata={"error": str(e)}
            )
        
        # Step 5: Parse outline into structured sections
        try:
            curriculum_data = self._parse_curriculum_outline(outline_text, goal, detected_template)
        except Exception as e:
            logger.error(f"Failed to parse curriculum outline: {e}", exc_info=True)
            return PersonaResponse(
                content=f"I generated a curriculum but had trouble parsing it. Here it is:\n\n{outline_text[:1000]}",
                mode="curriculum",
                actions=[],
                metadata={"error": str(e), "outline": outline_text}
            )
        
        # Step 4: Return review_curriculum action
        action = PersonaAction(
            type="review_curriculum",
            data={
                "curriculum_outline": outline_text,
                "curriculum_data": curriculum_data
            }
        )
        
        return PersonaResponse(
            content=f"I've created a comprehensive curriculum for learning **{goal}**. Please review the outline below and make any adjustments you'd like before saving.\n\n{outline_text[:500]}...\n\n*(Full curriculum shown in review dialog)*",
            mode="curriculum",
            actions=[action],
            metadata={
                "template_used": detected_template.id if detected_template else None,
                "template_confidence": template_detection.get('confidence') if template_detection else None,
                "total_sections": len(curriculum_data.get('sections', [])),
                "model_used": response.model if response else None
            }
        )
    
    def _parse_curriculum_outline(self, outline_text: str, goal: str, template: Optional[Any] = None) -> Dict[str, Any]:
        """
        Parse curriculum outline markdown into structured sections.
        
        Expected format:
        # Curriculum Title
        ## Week 1: Title
        ### 1.1 Section Title
        Description
        **Concepts:** concept1, concept2
        **Time:** 3 hours
        
        Args:
            outline_text: Markdown outline from LLM
            goal: Learning goal
            template: Optional template dict
        
        Returns:
            Dict with title, goal, template_id, sections list
        """
        import re
        
        # Extract title (first # heading)
        title_match = re.search(r'^#\s+(.+)$', outline_text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else f"Learn {goal}"
        
        # Extract goal if present
        goal_match = re.search(r'\*\*Goal:\*\*\s*(.+?)(?:\n|$)', outline_text, re.IGNORECASE)
        extracted_goal = goal_match.group(1).strip() if goal_match else goal
        
        # Parse sections
        sections = []
        
        # Find all week sections (## Week X: Title)
        week_pattern = re.compile(r'^##\s+Week\s+(\d+):\s*(.+)$', re.MULTILINE | re.IGNORECASE)
        weeks = list(week_pattern.finditer(outline_text))
        
        logger.info(f"[Parse Curriculum] Found {len(weeks)} week sections")
        
        if len(weeks) == 0:
            logger.warning(f"[Parse Curriculum] No week sections found in outline. First 500 chars:\n{outline_text[:500]}")
        
        for i, week_match in enumerate(weeks):
            week_num = week_match.group(1)
            week_title = week_match.group(2).strip()
            week_id = f"week-{week_num}"
            
            # Week section
            sections.append({
                "id": week_id,
                "title": week_title,
                "type": "week",
                "order": i,
                "parent_id": None,
                "description": "",
                "concepts": [],
                "estimated_time": ""
            })
            
            # Find content between this week and next week
            start_pos = week_match.end()
            end_pos = weeks[i + 1].start() if i + 1 < len(weeks) else len(outline_text)
            week_content = outline_text[start_pos:end_pos]
            
            # Find all subsections (### X.Y Title)
            subsection_pattern = re.compile(
                r'^###\s+(\d+)\.(\d+)\s+(.+?)$\n(.*?)(?=^###|^##|\Z)',
                re.MULTILINE | re.DOTALL
            )
            subsections = list(subsection_pattern.finditer(week_content))
            
            logger.debug(f"[Parse Curriculum] Week {week_num} has {len(subsections)} subsections")
            
            for j, sub_match in enumerate(subsections):
                section_num = sub_match.group(2)
                section_title = sub_match.group(3).strip()
                section_content = sub_match.group(4).strip()
                section_id = f"week-{week_num}.{section_num}"
                
                # Extract description (first paragraph)
                desc_lines = []
                for line in section_content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('**'):
                        desc_lines.append(line)
                    elif desc_lines:
                        break
                description = ' '.join(desc_lines)
                
                # Extract concepts
                concepts = []
                concepts_match = re.search(r'\*\*Concepts:\*\*\s*(.+?)(?:\n|$)', section_content, re.IGNORECASE)
                if concepts_match:
                    concepts_str = concepts_match.group(1).strip()
                    concepts = [c.strip() for c in concepts_str.split(',')]
                
                # Extract time
                time_str = ""
                time_match = re.search(r'\*\*Time:\*\*\s*(.+?)(?:\n|$)', section_content, re.IGNORECASE)
                if time_match:
                    time_str = time_match.group(1).strip()
                
                sections.append({
                    "id": section_id,
                    "title": section_title,
                    "type": "subheading",
                    "order": j,
                    "parent_id": week_id,
                    "description": description,
                    "concepts": concepts,
                    "estimated_time": time_str
                })
        
        result = {
            "title": title,
            "goal": extracted_goal,
            "template_id": template.id if template and hasattr(template, 'id') else (template['id'] if template else None),
            "sections": sections
        }
        
        logger.info(f"Parsed curriculum: {len([s for s in sections if s['type'] == 'week'])} weeks, "
                   f"{len([s for s in sections if s['type'] == 'subheading'])} subsections")
        
        return result
    
    def _estimate_mastery_from_dialogue(self, context: PersonaContext) -> Optional[int]:
        """
        Estimate mastery level (1-5) from dialogue.
        
        Heuristic based on conversation length and user responses:
        - 1 exchange: Level 1 (introduced)
        - 2-3 exchanges with good responses: Level 2 (learning)
        - 4-6 exchanges with understanding: Level 3 (understood)
        - 7+ exchanges with synthesis: Level 4-5 (proficient/mastered)
        """
        history_length = len(context.conversation_history)
        
        if history_length <= 2:
            return 1  # Just introduced
        elif history_length <= 4:
            return 2  # Learning
        elif history_length <= 8:
            return 3  # Understood
        elif history_length <= 12:
            return 4  # Proficient
        else:
            return 5  # Mastered (extensive dialogue)
    
    def _detect_note_creation_request(self, context: PersonaContext) -> bool:
        """Detect if user wants to create a learning note."""
        message = context.user_message.lower()
        keywords = ["create note", "save note", "learning note", "yes", "save this", "capture this"]
        return any(keyword in message for keyword in keywords)
    
    async def _offer_learning_note_creation(self, context: PersonaContext) -> PersonaResponse:
        """Offer to create a learning note from the dialogue."""
        topic = self._extract_topic_from_context(context)
        
        if not topic:
            topic = "Learning Session"
        
        content = f"""I can create a learning note for "{topic}" that includes:

- 📝 Concept definition and core principles
- 💡 Key insights and 'aha' moments from our dialogue
- 🔗 Related concepts to explore next
- ✍️ Practice exercises

Would you like me to create this note?"""
        
        actions = [PersonaAction(
            type="offer_learning_note",
            data={
                "topic": topic,
                "domain": "glyphs",
                "concepts": [topic]
            }
        )]
        
        return PersonaResponse(
            content=content,
            mode="socratic",
            actions=actions,
            metadata={"topic": topic}
        )
    
    # ========== Learning Tool Actions (Phase 23) ==========
    
    def create_diagram_action(
        self, 
        diagram_type: str, 
        source: str, 
        caption: str = None, 
        interactive: bool = True
    ) -> PersonaAction:
        """
        Create action to render a Mermaid diagram.
        
        Args:
            diagram_type: Type of diagram (mermaid, graphviz, etc.)
            source: Diagram source code
            caption: Optional caption
            interactive: Enable zoom/pan controls
        
        Returns:
            PersonaAction for render_diagram
        
        Example:
            ```python
            action = professor.create_diagram_action(
                diagram_type="mermaid",
                source="graph TD\nA --> B",
                caption="Simple flow"
            )
            ```
        """
        return PersonaAction(
            type="render_diagram",
            data={
                "diagram_type": diagram_type,
                "source": source,
                "caption": caption,
                "interactive": interactive
            }
        )
    
    def create_code_execution_action(
        self,
        language: str,
        code: str,
        editable: bool = True,
        visualize: str = None,
        test_cases: List[Dict] = None
    ) -> PersonaAction:
        """
        Create action to execute code in sandbox.
        
        Args:
            language: Programming language (python, javascript)
            code: Code to execute
            editable: Allow user to edit and re-run
            visualize: Visualization type (recursion_tree, call_stack, etc.)
            test_cases: List of test cases with input/expected output
        
        Returns:
            PersonaAction for execute_code
        
        Example:
            ```python
            action = professor.create_code_execution_action(
                language="python",
                code="def hello():\n    print('Hello!')",
                test_cases=[{"input": "hello()", "expected": "Hello!"}]
            )
            ```
        """
        return PersonaAction(
            type="execute_code",
            data={
                "language": language,
                "code": code,
                "editable": editable,
                "visualize": visualize,
                "test_cases": test_cases or []
            }
        )
    
    def create_exercise_action(
        self,
        exercise_id: str,
        exercise_type: str,
        title: str,
        description: str,
        starter_code: str = None,
        solution: str = None,
        test_cases: List[Dict] = None,
        hints: List[str] = None,
        difficulty: str = "medium"
    ) -> PersonaAction:
        """
        Create action to present interactive exercise.
        
        Args:
            exercise_id: Unique exercise identifier
            exercise_type: Type (code_challenge, multiple_choice, etc.)
            title: Exercise title
            description: Problem description
            starter_code: Initial code for user
            solution: Reference solution (hidden from user)
            test_cases: Test cases to validate solution
            hints: Progressive hints
            difficulty: Difficulty level
        
        Returns:
            PersonaAction for present_exercise
        
        Example:
            ```python
            action = professor.create_exercise_action(
                exercise_id="fibonacci_1",
                exercise_type="code_challenge",
                title="Implement Fibonacci",
                description="Write a function that returns nth Fibonacci number",
                test_cases=[
                    {"input": "fibonacci(5)", "output": "5"},
                    {"input": "fibonacci(10)", "output": "55"}
                ],
                hints=["Try recursion first", "What's the base case?"]
            )
            ```
        """
        return PersonaAction(
            type="present_exercise",
            data={
                "exercise_id": exercise_id,
                "type": exercise_type,
                "title": title,
                "description": description,
                "starter_code": starter_code,
                "solution": solution,
                "test_cases": test_cases or [],
                "hints": hints or [],
                "difficulty": difficulty,
                "estimated_time": self._estimate_exercise_time(difficulty)
            }
        )
    
    def _estimate_exercise_time(self, difficulty: str) -> str:
        """Estimate time to complete exercise based on difficulty."""
        times = {
            "beginner": "5-10 minutes",
            "easy": "10-15 minutes",
            "medium": "15-30 minutes",
            "hard": "30-60 minutes",
            "expert": "1-2 hours"
        }
        return times.get(difficulty, "15-30 minutes")
    
    # ============================================================================
    # SECTION ENRICHMENT (Phase 23 - Phase 4)
    # ============================================================================
    
    async def enrich_section(self, curriculum_id: str, section_id: str, section_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate heavy enrichment for a curriculum section.
        
        This method creates comprehensive learning materials for a section including:
        - Detailed explanations
        - Visual diagrams (Mermaid)
        - Code examples with explanations
        - Interactive exercises
        - External resources
        - Assessment criteria
        
        Args:
            curriculum_id: Curriculum identifier
            section_id: Section identifier (e.g., "week-1.1")
            section_data: Section dict with title, description, concepts, etc.
        
        Returns:
            Dict containing:
            {
                "status": "success",
                "enrichment": {
                    "explanation": "detailed markdown text",
                    "diagrams": [{"type": "mermaid", "source": "...", "caption": "..."}],
                    "examples": [{"title": "...", "code": "...", "explanation": "..."}],
                    "exercises": [{"id": "...", "title": "...", "description": "...", "starter_code": "...", "solution": "..."}],
                    "resources": [{"type": "...", "url": "...", "title": "..."}],
                    "assessment_criteria": ["You can explain X", "You can build Y"]
                }
            }
        
        Example:
            ```python
            enrichment = await professor.enrich_section(
                "python-learning",
                "week-1.1",
                {
                    "title": "Introduction to Python",
                    "description": "Learn Python basics",
                    "concepts": ["variables", "data types", "syntax"]
                }
            )
            ```
        """
        try:
            logger.info(f"[Enrich Section] Starting enrichment for {curriculum_id}/{section_id}")
            
            # Extract section info
            title = section_data.get("title", "")
            description = section_data.get("description", "")
            concepts = section_data.get("concepts", [])
            estimated_time = section_data.get("estimated_time", "")
            
            # Get curriculum template to determine content type
            curriculum_template_id = None
            if self.curriculum_manager:
                curriculum = self.curriculum_manager.get_curriculum(curriculum_id)
                if curriculum:
                    curriculum_template_id = curriculum.curriculum_template_id
                    logger.info(f"[Enrich Section] Using template: {curriculum_template_id}")
            
            # Check for related skill packages
            skill_data = None
            skill_name = self._detect_skill_package(title, description, concepts)
            if skill_name:
                logger.info(f"[Enrich Section] Found related skill package: {skill_name}")
                skill_data = self.load_skill(skill_name)
            
            # Build enrichment prompt
            prompt = self._build_enrichment_prompt(
                title=title,
                description=description,
                concepts=concepts,
                estimated_time=estimated_time,
                skill_data=skill_data,
                template_id=curriculum_template_id
            )
            
            # Generate enrichment using THOROUGH confidence (best model)
            logger.info(f"[Enrich Section] Generating enrichment using best model")
            
            context = PersonaContext(
                user_message=prompt,
                current_mode=self.default_mode,
                metadata={
                    "curriculum_id": curriculum_id,
                    "section_id": section_id,
                    "task": "section_enrichment",
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Call LLM with THOROUGH confidence
            # Call router_v2 to generate enrichment content
            response = await self.router.complete_with_fallback(
                messages=[{"role": "user", "content": prompt}],
                task_type=TaskType.CREATIVE,
                confidence=ConfidenceLevel.THOROUGH,
                max_tokens=4000,
                temperature=0.7
            )
            
            llm_content = response.content
            
            # Parse LLM response into structured data
            enrichment = self._parse_enrichment_response(llm_content, skill_data)
            
            logger.info(f"[Enrich Section] Enrichment complete - "
                       f"{len(enrichment.get('diagrams', []))} diagrams, "
                       f"{len(enrichment.get('examples', []))} examples, "
                       f"{len(enrichment.get('exercises', []))} exercises")
            
            return {
                "status": "success",
                "enrichment": enrichment
            }
            
        except Exception as e:
            logger.error(f"[Enrich Section] Error enriching section: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "enrichment": {
                    "explanation": f"**Error generating enrichment:** {str(e)}",
                    "diagrams": [],
                    "examples": [],
                    "exercises": [],
                    "resources": [],
                    "assessment_criteria": []
                }
            }
    
    def _detect_skill_package(self, title: str, description: str, concepts: List[str]) -> Optional[str]:
        """
        Detect if there's a related skill package for this section.
        
        Args:
            title: Section title
            description: Section description
            concepts: List of concepts covered
        
        Returns:
            Skill package name or None
        """
        # List available skills
        available_skills = self.list_available_skills()
        if not available_skills:
            return None
        
        # Simple keyword matching
        text = f"{title} {description} {' '.join(concepts)}".lower()
        
        for skill in available_skills:
            skill_keywords = skill.replace("-", " ").replace("_", " ").split()
            for keyword in skill_keywords:
                if keyword.lower() in text:
                    return skill
        
        return None
    
    def _build_enrichment_prompt(self, title: str, description: str, concepts: List[str], 
                                  estimated_time: str, skill_data: Optional[Dict[str, Any]], 
                                  template_id: Optional[str] = None) -> str:
        """
        Build prompt for section enrichment.
        
        Args:
            title: Section title
            description: Section description
            concepts: List of concepts to cover
            estimated_time: Estimated time to complete
            skill_data: Optional skill package data
            template_id: Curriculum template ID to determine content type
        
        Returns:
            Enrichment prompt string
        """
        # Determine content type based on template
        is_programming = template_id in ['programming-language', 'framework-library']
        content_type = "code examples" if is_programming else "real-world case studies and examples (NO CODE)"
        
        prompt = f"""# Section Enrichment Request

You are enriching a curriculum section with comprehensive learning materials.

**Section:** {title}
**Description:** {description}
**Key Concepts:** {', '.join(concepts) if concepts else 'Not specified'}
**Estimated Time:** {estimated_time or 'Not specified'}
**Content Type:** {content_type}

{'IMPORTANT: This is a NON-PROGRAMMING curriculum. Do NOT include any code examples or code blocks. Use real-world examples, case studies, and applications instead.' if not is_programming else ''}

Please create enriched learning materials for this section. Provide your response in the following structured format:

## EXPLANATION
[Write a detailed, clear explanation of the concepts in this section. Use markdown formatting. Include:
- Overview of what will be learned
- Why it matters
- How it connects to other concepts
- Step-by-step breakdown of key ideas
- Common misconceptions to avoid]

## DIAGRAMS
[For each diagram, provide:
DIAGRAM_START
TYPE: mermaid
CAPTION: Brief description of diagram
SOURCE:
```mermaid
[mermaid diagram code]
```
DIAGRAM_END

IMPORTANT MERMAID GUIDELINES:
- Avoid parentheses in node labels (use "Integer Type" not "int()")
- Use simple alphanumeric labels and underscores/hyphens only
- Escape special characters or use quotes for complex text
- Test that your Mermaid syntax is valid before including it
]
"""
        
        # Adapt examples section based on curriculum template
        if template_id in ['programming-language', 'framework-library']:
            # Programming templates: Include code examples
            prompt += """
## CODE EXAMPLES
[For each code example, provide:
EXAMPLE_START
TITLE: Example title
CODE:
```
[working code example here]
```
EXPLANATION: What this example demonstrates, why it's important, and how it works
EXAMPLE_END

Include 2-3 practical code examples that learners can run and modify.
]
"""
        elif template_id == 'skill-acquisition':
            # Skill template: Include practical examples (code if technical, otherwise hands-on demos)
            prompt += """
## PRACTICAL EXAMPLES
[For each practical example, provide:
EXAMPLE_START
TITLE: Example title
CODE:
```
[code, commands, or step-by-step demonstration here]
```
EXPLANATION: What this example demonstrates and how to apply it in practice
EXAMPLE_END

Include 2-3 hands-on examples that demonstrate the skill in action.
]
"""
        elif template_id == 'problem-solving':
            # Problem-solving template: Include problem examples with solutions
            prompt += """
## PROBLEM EXAMPLES
[For each problem example, provide:
EXAMPLE_START
TITLE: Problem title
CODE:
```
[problem statement and solution approach]
```
EXPLANATION: The problem-solving strategy used and why it works
EXAMPLE_END

Include 2-3 example problems with clear solution approaches.
]
"""
        else:
            # Domain exploration or unknown template: Use case studies instead of code
            prompt += """
## REAL-WORLD EXAMPLES

CRITICAL INSTRUCTION: This is a NON-PROGRAMMING topic (e.g., design, philosophy, arts, business).
- Do NOT use "Code Examples" as a heading
- Do NOT include any code blocks or programming examples
- Do NOT use CODE: field
- Use DESCRIPTION: field instead

For each real-world example or case study:
EXAMPLE_START
TITLE: Example title (e.g., "The Coca-Cola Brand Identity", "Bauhaus Design Movement")
DESCRIPTION: Detailed description of the real-world example, case study, historical application, or demonstration of the concepts in practice (2-4 sentences)
EXPLANATION: What this example demonstrates and why it's significant to understanding the topic (1-2 sentences)
EXAMPLE_END

Include 2-3 concrete real-world examples, applications, or case studies that illustrate the concepts in practice.]
]
"""
        
        # Adapt exercises section based on curriculum template
        if template_id in ['programming-language', 'framework-library', 'skill-acquisition']:
            # Programming/technical templates: Include coding exercises
            prompt += """
## EXERCISES
[For each exercise, provide:
EXERCISE_START
ID: unique-exercise-id
TITLE: Exercise title
DESCRIPTION: What the learner should do
STARTER_CODE:
```
[starter code if applicable]
```
SOLUTION:
```
[solution code]
```
TEST_CASES: Describe what should pass/fail
EXERCISE_END
]
"""
        else:
            # Non-programming templates: Include reflection/application exercises
            prompt += """
## EXERCISES
[For each exercise, provide:
EXERCISE_START
ID: unique-exercise-id
TITLE: Exercise title
DESCRIPTION: What the learner should do (reflection questions, analysis tasks, creative applications)
GUIDANCE: Key points or approaches to consider
EXAMPLE_RESPONSE: Brief example of a good response
EXERCISE_END

Focus on critical thinking, analysis, and application rather than coding exercises.
]
"""
        
        prompt += """
## RESOURCES
[For each resource, provide:
RESOURCE_START
TYPE: [documentation/article/video/tool]
URL: [if applicable]
TITLE: Resource title
DESCRIPTION: Why this resource is helpful
RESOURCE_END
]

## ASSESSMENT_CRITERIA
[List 3-5 clear statements of what mastery looks like:
- "You can explain X to someone else"
- "You can build Y without looking at docs"
- etc.]
"""

        # Add skill package hint if available
        if skill_data:
            prompt += f"""

**Note:** A related skill package is available with existing materials. You may reference or build upon:
- Diagrams: {len(skill_data.get('diagrams', []))} available
- Exercises: {len(skill_data.get('exercises', []))} available
- Examples: {len(skill_data.get('examples', []))} available

Feel free to create new materials or adapt existing ones for this specific section.
"""
        
        return prompt
    
    def _parse_enrichment_response(self, content: str, skill_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Parse LLM enrichment response into structured data.
        
        Args:
            content: LLM response text
            skill_data: Optional skill package data to merge
        
        Returns:
            Enrichment dict with explanation, diagrams, examples, exercises, resources, assessment_criteria
        """
        enrichment = {
            "explanation": "",
            "diagrams": [],
            "examples": [],
            "exercises": [],
            "resources": [],
            "assessment_criteria": []
        }
        
        try:
            # Extract explanation (everything from EXPLANATION to next section)
            explanation_match = content.find("## EXPLANATION")
            if explanation_match != -1:
                explanation_end = content.find("## DIAGRAMS", explanation_match)
                if explanation_end == -1:
                    explanation_end = len(content)
                explanation = content[explanation_match + len("## EXPLANATION"):explanation_end].strip()
                enrichment["explanation"] = explanation
            
            # Extract diagrams
            diagram_sections = content.split("DIAGRAM_START")
            for section in diagram_sections[1:]:  # Skip first (before any DIAGRAM_START)
                if "DIAGRAM_END" not in section:
                    continue
                
                diagram_content = section.split("DIAGRAM_END")[0]
                
                # Extract diagram fields
                diagram_type = "mermaid"
                caption = ""
                source = ""
                
                for line in diagram_content.split("\n"):
                    if line.startswith("TYPE:"):
                        diagram_type = line.replace("TYPE:", "").strip()
                    elif line.startswith("CAPTION:"):
                        caption = line.replace("CAPTION:", "").strip()
                    elif "```mermaid" in line or "```" in diagram_content:
                        # Extract code block
                        code_start = diagram_content.find("```")
                        if code_start != -1:
                            code_end = diagram_content.find("```", code_start + 3)
                            if code_end != -1:
                                source = diagram_content[code_start+3:code_end].strip()
                                # Remove language identifier if present
                                if source.startswith("mermaid"):
                                    source = source[7:].strip()
                
                if source:
                    enrichment["diagrams"].append({
                        "type": diagram_type,
                        "source": source,
                        "caption": caption
                    })
            
            # Extract examples
            example_sections = content.split("EXAMPLE_START")
            for section in example_sections[1:]:
                if "EXAMPLE_END" not in section:
                    continue
                
                example_content = section.split("EXAMPLE_END")[0]
                
                title = ""
                code = ""
                description = ""
                explanation = ""
                
                for line in example_content.split("\n"):
                    if line.startswith("TITLE:"):
                        title = line.replace("TITLE:", "").strip()
                    elif line.startswith("DESCRIPTION:"):
                        description = line.replace("DESCRIPTION:", "").strip()
                    elif line.startswith("EXPLANATION:"):
                        explanation = line.replace("EXPLANATION:", "").strip()
                
                # Extract code block if present
                if "```" in example_content:
                    code_start = example_content.find("```")
                    code_end = example_content.find("```", code_start + 3)
                    if code_start != -1 and code_end != -1:
                        code = example_content[code_start+3:code_end].strip()
                        # Remove language identifier
                        if "\n" in code:
                            lines = code.split("\n")
                            if lines[0] and not " " in lines[0]:  # Likely language identifier
                                code = "\n".join(lines[1:])
                
                # Store example with either code or description
                if title:
                    example_data = {
                        "title": title,
                        "explanation": explanation
                    }
                    if code:
                        example_data["code"] = code
                    if description:
                        example_data["description"] = description
                    enrichment["examples"].append(example_data)
            
            # Extract exercises
            exercise_sections = content.split("EXERCISE_START")
            for section in exercise_sections[1:]:
                if "EXERCISE_END" not in section:
                    continue
                
                exercise_content = section.split("EXERCISE_END")[0]
                
                exercise = {
                    "id": "",
                    "title": "",
                    "description": "",
                    "starter_code": "",
                    "solution": "",
                    "test_cases": "",
                    "guidance": "",
                    "example_response": ""
                }
                
                lines = exercise_content.split("\n")
                current_field = None
                current_code = []
                
                for line in lines:
                    if line.startswith("ID:"):
                        exercise["id"] = line.replace("ID:", "").strip()
                    elif line.startswith("TITLE:"):
                        exercise["title"] = line.replace("TITLE:", "").strip()
                    elif line.startswith("DESCRIPTION:"):
                        exercise["description"] = line.replace("DESCRIPTION:", "").strip()
                    elif line.startswith("TEST_CASES:"):
                        exercise["test_cases"] = line.replace("TEST_CASES:", "").strip()
                    elif line.startswith("GUIDANCE:"):
                        exercise["guidance"] = line.replace("GUIDANCE:", "").strip()
                    elif line.startswith("EXAMPLE_RESPONSE:"):
                        exercise["example_response"] = line.replace("EXAMPLE_RESPONSE:", "").strip()
                    elif line.startswith("STARTER_CODE:"):
                        current_field = "starter_code"
                        current_code = []
                    elif line.startswith("SOLUTION:"):
                        if current_field == "starter_code" and current_code:
                            exercise["starter_code"] = "\n".join(current_code).strip()
                        current_field = "solution"
                        current_code = []
                    elif current_field and line.strip():
                        if "```" in line:
                            continue  # Skip code fence markers
                        current_code.append(line)
                
                # Save last code block
                if current_field == "solution" and current_code:
                    exercise["solution"] = "\n".join(current_code).strip()
                
                if exercise["id"] and exercise["title"]:
                    enrichment["exercises"].append(exercise)
            
            # Extract resources
            resource_sections = content.split("RESOURCE_START")
            for section in resource_sections[1:]:
                if "RESOURCE_END" not in section:
                    continue
                
                resource_content = section.split("RESOURCE_END")[0]
                
                resource = {
                    "type": "documentation",
                    "url": "",
                    "title": "",
                    "description": ""
                }
                
                for line in resource_content.split("\n"):
                    if line.startswith("TYPE:"):
                        resource["type"] = line.replace("TYPE:", "").strip()
                    elif line.startswith("URL:"):
                        resource["url"] = line.replace("URL:", "").strip()
                    elif line.startswith("TITLE:"):
                        resource["title"] = line.replace("TITLE:", "").strip()
                    elif line.startswith("DESCRIPTION:"):
                        resource["description"] = line.replace("DESCRIPTION:", "").strip()
                
                if resource["title"]:
                    enrichment["resources"].append(resource)
            
            # Extract assessment criteria
            assessment_start = content.find("## ASSESSMENT_CRITERIA")
            if assessment_start != -1:
                assessment_content = content[assessment_start + len("## ASSESSMENT_CRITERIA"):].strip()
                
                # Extract list items
                for line in assessment_content.split("\n"):
                    line = line.strip()
                    if line.startswith("-") or line.startswith("*"):
                        criterion = line[1:].strip().strip('"')
                        if criterion:
                            enrichment["assessment_criteria"].append(criterion)
            
            # Merge skill package data if available
            if skill_data:
                # Add skill package resources
                if skill_data.get("skill_md"):
                    enrichment["resources"].insert(0, {
                        "type": "skill_package",
                        "title": f"Skill Package: {skill_data['name']}",
                        "description": "Curated materials from Polly skill library",
                        "url": ""
                    })
            
            logger.info(f"[Parse Enrichment] Parsed: "
                       f"{len(enrichment['diagrams'])} diagrams, "
                       f"{len(enrichment['examples'])} examples, "
                       f"{len(enrichment['exercises'])} exercises")
            
        except Exception as e:
            logger.error(f"[Parse Enrichment] Error parsing: {e}", exc_info=True)
        
        return enrichment

    # Skill Package Management
    
    def load_skill(self, skill_name: str, vault_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Load a skill package from the vault.
        
        Args:
            skill_name: Name of skill (e.g., "recursion", "async-await")
            vault_path: Optional custom vault path
        
        Returns:
            Dict containing:
            - skill_md: Content of SKILL.md
            - diagrams: List of diagram files and their content
            - exercises: List of exercise JSON objects
            - examples: List of example files
        
        Example:
            ```python
            skill = professor.load_skill("recursion")
            if skill:
                # Use skill content to teach
                print(skill['skill_md'])
                for diagram in skill['diagrams']:
                    action = professor.create_diagram_action(...)
            ```
        """
        try:
            # Determine vault path
            if vault_path is None:
                vault_path = Path.home() / "polly" / "vault" / ".polly" / "skills"
            else:
                vault_path = Path(vault_path)
            
            skill_dir = vault_path / skill_name
            
            if not skill_dir.exists():
                logger.warning(f"Skill package not found: {skill_dir}")
                return None
            
            skill_data = {
                "name": skill_name,
                "skill_md": None,
                "diagrams": [],
                "exercises": [],
                "examples": []
            }
            
            # Load SKILL.md
            skill_md_path = skill_dir / "SKILL.md"
            if skill_md_path.exists():
                skill_data["skill_md"] = skill_md_path.read_text(encoding='utf-8')
            
            # Load diagrams
            diagrams_dir = skill_dir / "diagrams"
            if diagrams_dir.exists():
                for diagram_file in diagrams_dir.glob("*.mmd"):
                    skill_data["diagrams"].append({
                        "name": diagram_file.stem,
                        "path": str(diagram_file),
                        "source": diagram_file.read_text(encoding='utf-8')
                    })
            
            # Load exercises
            exercises_dir = skill_dir / "exercises"
            if exercises_dir.exists():
                for exercise_file in sorted(exercises_dir.glob("*.json")):
                    try:
                        exercise_data = json.loads(exercise_file.read_text(encoding='utf-8'))
                        skill_data["exercises"].append(exercise_data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse exercise {exercise_file}: {e}")
            
            # Load examples
            examples_dir = skill_dir / "examples"
            if examples_dir.exists():
                for example_file in examples_dir.glob("*"):
                    if example_file.is_file():
                        skill_data["examples"].append({
                            "name": example_file.stem,
                            "path": str(example_file),
                            "content": example_file.read_text(encoding='utf-8')
                        })
            
            logger.info(f"Loaded skill package: {skill_name} - "
                       f"{len(skill_data['diagrams'])} diagrams, "
                       f"{len(skill_data['exercises'])} exercises, "
                       f"{len(skill_data['examples'])} examples")
            
            return skill_data
            
        except Exception as e:
            logger.error(f"Error loading skill package {skill_name}: {e}")
            return None
    
    def list_available_skills(self, vault_path: Optional[str] = None) -> List[str]:
        """
        List all available skill packages in the vault.
        
        Args:
            vault_path: Optional custom vault path
        
        Returns:
            List of skill names
        """
        try:
            if vault_path is None:
                vault_path = Path.home() / "polly" / "vault" / ".polly" / "skills"
            else:
                vault_path = Path(vault_path)
            
            if not vault_path.exists():
                return []
            
            skills = []
            for skill_dir in vault_path.iterdir():
                if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                    skills.append(skill_dir.name)
            
            return sorted(skills)
            
        except Exception as e:
            logger.error(f"Error listing skills: {e}")
            return []
    
    def get_exercise_by_id(self, exercise_id: str, vault_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get a specific exercise by ID.
        
        Args:
            exercise_id: Exercise identifier (e.g., "fibonacci_1")
            vault_path: Optional custom vault path
        
        Returns:
            Exercise data dict or None if not found
        """
        # Extract skill name from exercise_id (e.g., "fibonacci_1" -> "fibonacci")
        skill_name = exercise_id.rsplit("_", 1)[0].replace("_", "-")
        
        skill_data = self.load_skill(skill_name, vault_path)
        if not skill_data:
            return None
        
        for exercise in skill_data.get("exercises", []):
            if exercise.get("exercise_id") == exercise_id:
                return exercise
        
        return None

