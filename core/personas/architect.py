"""
Architect Persona (Phase 11c)

The Architect persona is designed for planning and building complex tasks,
particularly AI-powered note creation (Phase 16c).

Modes:
- Plan: Analyze requirements, ask clarifying questions, create structured outline
- Build: Execute plan, generate content using outline and user answers

Model Routing:
- Plan mode: Balanced tier (Claude Sonnet 4 preferred)
- Build mode: Thorough tier (Claude Opus 4 or Sonnet 4)
"""

from typing import Dict, List, Optional, Any
import re
import logging
from datetime import datetime

from .base import AgentPersona, PersonaContext, PersonaResponse, PersonaAction
from .models import Plan, GeneratedContent, OutlineNode
from core.router_v2 import TaskType, ConfidenceLevel

logger = logging.getLogger(__name__)


# ========== System Prompts ==========

ARCHITECT_PLAN_PROMPT = """You are Architect, Polly's planning persona.

Your job is to analyze user requests and create detailed, actionable plans.

**Process:**
1. Review conversation context carefully
2. Identify what you understand about the request
3. Identify what you need to clarify
4. Ask 2-5 targeted questions (if needed - don't over-ask)
5. Create a structured outline showing how you'll approach the task

**Guidelines:**
- Be concise but thorough
- Focus on understanding intent before planning execution
- Ask specific, actionable questions
- Create clear, hierarchical outlines
- Suggest templates or structures when applicable
- Don't generate content yet (that's Build mode)

**Output Format:**
You MUST structure your response exactly like this:

## What I Understand
[1-2 sentence summary of what you understand about the request]

## Questions
[Only if needed - 2-5 specific questions to clarify requirements]
1. [Question 1]
2. [Question 2]
...

## Proposed Outline
[Hierarchical structure using markdown headings]
# Main Section 1
## Subsection 1.1
## Subsection 1.2

# Main Section 2
## Subsection 2.1

## Suggested Approach
[Brief description of how you'll execute this in Build mode]

Be direct, clear, and helpful.
"""

ARCHITECT_BUILD_PROMPT = """You are Architect, Polly's building persona.

Your job is to execute plans and generate high-quality content.

**Process:**
1. Review the plan and user's answers carefully
2. Follow the outline structure exactly
3. Generate thorough, well-structured content
4. Apply templates if specified
5. Ensure consistency and quality throughout

**Guidelines:**
- Follow the plan and outline precisely
- Use the user's voice and terminology
- Be thorough but concise
- Maintain professional quality
- Include all user-provided information
- Add relevant cross-references when appropriate
- Use markdown formatting effectively

**Quality Standards:**
- Clear, well-structured headings
- Logical flow and organization
- Comprehensive coverage of outline points
- Professional tone
- Actionable and useful content

Generate the complete final output ready for user review.
"""


# ========== Architect Persona ==========

class ArchitectPersona(AgentPersona):
    """
    Architect persona for planning and building complex tasks.
    
    Primary use case: AI note creation (Phase 16c)
    
    Workflow:
    1. User: "Create a note about X"
    2. Architect activates in Plan mode
    3. Architect analyzes, asks questions, creates outline
    4. User answers questions
    5. User switches to Build mode
    6. Architect generates final content
    7. Content shown in preview modal
    """
    
    @property
    def default_mode(self) -> str:
        return "plan"
    
    @property
    def available_modes(self) -> List[str]:
        return ["plan", "build"]
    
    async def process(self, context: PersonaContext) -> PersonaResponse:
        """
        Route to appropriate mode handler.
        
        Args:
            context: PersonaContext with user message and conversation
        
        Returns:
            PersonaResponse from mode-specific handler
        """
        mode = self.state.current_mode
        
        logger.info(f"Architect processing in {mode} mode")
        
        if mode == "plan":
            return await self.plan(context)
        elif mode == "build":
            return await self.build(context)
        else:
            raise ValueError(f"Unknown mode: {mode}")
    
    def get_mode_prompts(self) -> Dict[str, str]:
        """Return mode-specific system prompts"""
        return {
            "plan": ARCHITECT_PLAN_PROMPT,
            "build": ARCHITECT_BUILD_PROMPT
        }
    
    # ========== Plan Mode ==========
    
    async def plan(self, context: PersonaContext) -> PersonaResponse:
        """
        Planning mode: Analyze request and create structured plan.
        
        Process:
        1. Analyze user request and conversation context
        2. Identify what is known vs. unknown
        3. Generate 2-5 clarifying questions (if needed)
        4. Create structured outline
        5. Suggest template (if applicable)
        
        Args:
            context: PersonaContext with user input
        
        Returns:
            PersonaResponse with plan and questions
        """
        logger.info("Architect Plan mode: analyzing request")
        
        # Build messages for LLM
        messages = self._build_messages(context, include_history=True)
        
        # Add context from metadata if available
        if context.metadata.get("related_notes"):
            context_note = self._format_related_notes(context.metadata["related_notes"])
            messages.append({
                "role": "system",
                "content": f"Related notes from knowledge base:\n{context_note}"
            })
        
        # Use balanced tier for planning (Sonnet 4 preferred)
        try:
            response = await self.router.complete_with_fallback(
                messages=messages,
                task_type=TaskType.ARCHITECTURAL,
                confidence=ConfidenceLevel.BALANCED,
                max_tokens=2000,
                temperature=0.7
            )
        except Exception as e:
            logger.error(f"Router failed in plan mode: {e}")
            return PersonaResponse(
                content=f"Sorry, I encountered an error while planning: {str(e)}",
                mode="plan",
                actions=[],
                metadata={"error": str(e)}
            )
        
        # Parse response into structured plan
        plan = self._parse_planning_response(response.content)
        
        # Store plan in persona state
        self.state.set_data("current_plan", plan.to_dict())
        self.state.set_data("plan_created_at", datetime.now().isoformat())
        
        # Generate UI actions
        actions = []
        if plan.questions:
            actions.append(PersonaAction(
                type="show_questions",
                data={
                    "questions": plan.questions,
                    "can_skip": len(plan.questions) <= 2  # Can skip if only 1-2 questions
                }
            ))
        
        # Add mode switch suggestion
        if not plan.needs_clarification:
            actions.append(PersonaAction(
                type="suggest_mode_switch",
                data={"target_mode": "build", "message": "Ready to build!"}
            ))
        
        # Format output for user
        output = self._format_planning_output(plan)
        
        return PersonaResponse(
            content=output,
            mode="plan",
            actions=actions,
            metadata={
                "plan": plan.to_dict(),
                "model_used": response.model,
                "tokens_in": response.tokens_in,
                "tokens_out": response.tokens_out,
                "cost": response.cost
            }
        )
    
    # ========== Build Mode ==========
    
    async def build(self, context: PersonaContext) -> PersonaResponse:
        """
        Building mode: Execute plan and generate content.
        
        Process:
        1. Load plan from state
        2. Incorporate user answers (if any)
        3. Generate content using thorough tier
        4. Apply template structure
        5. Return for user preview
        
        Args:
            context: PersonaContext with user input (answers or confirmation)
        
        Returns:
            PersonaResponse with generated content and preview action
        """
        logger.info("Architect Build mode: generating content")
        
        # Retrieve plan from state
        plan_dict = self.state.get_data("current_plan")
        if not plan_dict:
            return PersonaResponse(
                content="No plan found. Please switch back to Plan mode first to create a plan.",
                mode="build",
                actions=[PersonaAction(
                    type="suggest_mode_switch",
                    data={"target_mode": "plan", "message": "Create a plan first"}
                )],
                metadata={"error": "no_plan"}
            )
        
        plan = Plan.from_dict(plan_dict)
        
        # Check if user wants to proceed despite unanswered questions
        user_msg_lower = context.user_message.lower() if context.user_message else ""
        proceed_keywords = ["generate", "build", "create", "proceed", "continue", "go ahead", "skip"]
        wants_to_proceed = any(keyword in user_msg_lower for keyword in proceed_keywords)
        
        # Check if user is providing answers to questions
        if context.user_message and plan.get_unanswered_questions() and not wants_to_proceed:
            # Parse answers from user message
            self._parse_and_add_answers(plan, context.user_message)
            self.state.set_data("current_plan", plan.to_dict())
            
            # If still have unanswered questions and user didn't explicitly ask to proceed, ask for them
            if plan.get_unanswered_questions():
                return PersonaResponse(
                    content=self._format_unanswered_questions(plan),
                    mode="build",
                    actions=[PersonaAction(
                        type="show_questions",
                        data={"questions": plan.get_unanswered_questions(), "can_skip": True}
                    )],
                    metadata={"awaiting_answers": True}
                )
        
        # Build generation prompt
        build_prompt = self._construct_build_prompt(plan, context)
        messages = [
            {"role": "system", "content": ARCHITECT_BUILD_PROMPT},
            {"role": "user", "content": build_prompt}
        ]
        
        # Use thorough tier for building (Opus 4 or Sonnet 4)
        try:
            response = await self.router.complete_with_fallback(
                messages=messages,
                task_type=TaskType.CREATIVE,
                confidence=ConfidenceLevel.THOROUGH,
                max_tokens=4000,
                temperature=0.8
            )
        except Exception as e:
            logger.error(f"Router failed in build mode: {e}")
            return PersonaResponse(
                content=f"Sorry, I encountered an error while building: {str(e)}",
                mode="build",
                actions=[],
                metadata={"error": str(e)}
            )
        
        # Parse generated content
        generated = GeneratedContent(
            content=response.content,
            format="markdown",
            title=self._extract_title_from_plan(plan),
            generated_at=datetime.now()
        )
        
        # Store result in state
        self.state.set_data("generated_content", generated.to_dict())
        self.state.set_data("built_at", datetime.now().isoformat())
        
        # Generate preview action
        actions = [PersonaAction(
            type="show_preview",
            data={
                "content": generated.content,
                "title": generated.title,
                "format": generated.format,
                "preview_type": "note"
            }
        )]
        
        # Format output
        output = self._format_build_output(generated)
        
        return PersonaResponse(
            content=output,
            mode="build",
            actions=actions,
            metadata={
                "generated_content": generated.to_dict(),
                "model_used": response.model,
                "tokens_in": response.tokens_in,
                "tokens_out": response.tokens_out,
                "cost": response.cost
            }
        )
    
    # ========== Helper Methods: Parsing ==========
    
    def _parse_planning_response(self, content: str) -> Plan:
        """
        Parse LLM response into structured Plan object.
        
        Extracts sections using markdown headings and patterns.
        """
        # Extract "What I Understand" section
        understanding = self._extract_section(content, r"##\s*What I Understand")
        if not understanding:
            understanding = content.split('\n')[0]  # Fallback to first line
        
        # Extract questions
        questions = self._extract_questions(content)
        
        # Extract outline
        outline = self._extract_outline(content)
        
        # Extract template suggestion
        template = self._extract_section(content, r"##\s*Template")
        
        return Plan(
            understanding=understanding.strip(),
            questions=questions,
            outline=outline,
            template=template.strip() if template else None,
            needs_clarification=len(questions) > 0
        )
    
    def _extract_section(self, content: str, heading_pattern: str) -> str:
        """Extract content under a specific heading"""
        match = re.search(heading_pattern, content, re.IGNORECASE | re.MULTILINE)
        if not match:
            return ""
        
        # Find start of section
        start = match.end()
        
        # Find end of section (next ## heading or end of content)
        next_heading = re.search(r'\n##\s+', content[start:])
        if next_heading:
            end = start + next_heading.start()
        else:
            end = len(content)
        
        return content[start:end].strip()
    
    def _extract_questions(self, content: str) -> List[str]:
        """Extract list of questions from content"""
        questions = []
        
        # Find Questions section
        questions_section = self._extract_section(content, r"##\s*Questions")
        if not questions_section:
            return questions
        
        # Extract numbered or bulleted items
        lines = questions_section.split('\n')
        for line in lines:
            line = line.strip()
            # Match "1. Question" or "- Question" or "* Question"
            match = re.match(r'^(?:\d+\.|-|\*)\s+(.+)', line)
            if match:
                questions.append(match.group(1).strip())
        
        return questions
    
    def _extract_outline(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract hierarchical outline from content.
        
        Parses markdown headings into structured outline.
        """
        outline = []
        
        # Find Proposed Outline section
        outline_section = self._extract_section(content, r"##\s*Proposed Outline")
        if not outline_section:
            return outline
        
        # Parse markdown headings
        lines = outline_section.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Match markdown headings
            match = re.match(r'^(#{1,6})\s+(.+)', line)
            if match:
                level = len(match.group(1))  # Number of # characters
                title = match.group(2).strip()
                outline.append({
                    "level": level,
                    "title": title
                })
        
        return outline
    
    def _parse_and_add_answers(self, plan: Plan, user_message: str):
        """Parse user's answers from message and add to plan"""
        # Simple heuristic: if message is short and has Q&A format, parse it
        # Otherwise, treat entire message as answer to first unanswered question
        
        unanswered = plan.get_unanswered_questions()
        if not unanswered:
            return
        
        # Try to parse "Q1: answer1, Q2: answer2" format
        for i, question in enumerate(unanswered):
            # Simple approach: assign message to first unanswered question
            if i == 0:
                plan.add_answer(question, user_message.strip())
                break
    
    # ========== Helper Methods: Construction ==========
    
    def _construct_build_prompt(self, plan: Plan, context: PersonaContext) -> str:
        """Construct comprehensive prompt for content generation"""
        prompt = f"""Based on this plan, generate the final content.

**What I Understand:**
{plan.understanding}

**Outline to Follow:**
{self._format_outline_for_prompt(plan.outline)}
"""
        
        # Add user answers if available
        if plan.user_answers:
            answers_text = "\n".join([
                f"Q: {q}\nA: {a}"
                for q, a in plan.user_answers.items()
            ])
            prompt += f"""

**User's Answers:**
{answers_text}
"""
        
        # Add template if specified
        if plan.template:
            prompt += f"""

**Template to Follow:**
{plan.template}
"""
        
        # Add any additional context
        if context.metadata.get("additional_context"):
            prompt += f"""

**Additional Context:**
{context.metadata['additional_context']}
"""
        
        return prompt
    
    def _format_outline_for_prompt(self, outline: List[Dict[str, Any]]) -> str:
        """Format outline for inclusion in prompt"""
        if not outline:
            return "[No specific outline provided]"
        
        lines = []
        for item in outline:
            level = item.get("level", 1)
            title = item.get("title", "")
            indent = "  " * (level - 1)
            lines.append(f"{indent}- {title}")
        
        return "\n".join(lines)
    
    def _format_related_notes(self, notes: List[Dict]) -> str:
        """Format related notes for context"""
        if not notes:
            return ""
        
        lines = []
        for note in notes[:5]:  # Limit to 5 notes
            title = note.get("title", "Untitled")
            content = note.get("content", "")[:200]  # First 200 chars
            lines.append(f"- {title}: {content}...")
        
        return "\n".join(lines)
    
    def _extract_title_from_plan(self, plan: Plan) -> Optional[str]:
        """Extract a title from the plan's understanding or outline"""
        # Try to get from first outline item
        if plan.outline:
            return plan.outline[0].get("title")
        
        # Fall back to first few words of understanding
        words = plan.understanding.split()[:5]
        return " ".join(words)
    
    # ========== Helper Methods: Formatting ==========
    
    def _format_planning_output(self, plan: Plan) -> str:
        """Format plan for display to user"""
        output = f"""**Planning Analysis**

{plan.understanding}

**Proposed Structure:**
{self._format_outline_display(plan.outline)}
"""
        
        if plan.questions:
            questions_list = "\n".join([f"{i+1}. {q}" for i, q in enumerate(plan.questions)])
            output += f"""

**Questions for Clarity:**
{questions_list}

Please answer these questions, then switch to Build mode to generate the content.
"""
        else:
            output += """

✓ Plan is complete! Switch to Build mode when you're ready to generate the content.
"""
        
        return output
    
    def _format_outline_display(self, outline: List[Dict[str, Any]]) -> str:
        """Format outline for display to user"""
        if not outline:
            return "[Will be structured based on your input]"
        
        lines = []
        for item in outline:
            level = item.get("level", 1)
            title = item.get("title", "")
            prefix = "#" * level
            lines.append(f"{prefix} {title}")
        
        return "\n".join(lines)
    
    def _format_unanswered_questions(self, plan: Plan) -> str:
        """Format message prompting for unanswered questions"""
        unanswered = plan.get_unanswered_questions()
        questions_list = "\n".join([f"{i+1}. {q}" for i, q in enumerate(unanswered)])
        
        return f"""I still need answers to these questions before building:

{questions_list}

Please provide your answers.
"""
    
    def _format_build_output(self, generated: GeneratedContent) -> str:
        """Format generated content for display"""
        return f"""**Generated Content**

{generated.content}

---
*Content generated and ready for preview. Review and save when ready.*
"""
