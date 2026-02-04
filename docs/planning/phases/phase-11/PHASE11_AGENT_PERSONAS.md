# Phase 11: Agent Personas Framework

**Document Version:** 1.0  
**Last Updated:** January 28, 2026  
**Related:** [PHASE11_MULTI_MODEL_ENHANCED_V2.md](./PHASE11_MULTI_MODEL_ENHANCED_V2.md), [PHASE16C_AI_NOTE_CREATION.md](./PHASE16C_AI_NOTE_CREATION.md)

---

## Executive Summary

This document specifies the Agent Personas framework for Polly, starting with the **Architect persona** for Phase 11c and Phase 16c. Agent personas are specialized AI workflows with distinct modes of operation, allowing users to manually switch between different reasoning approaches (like OpenCode's plan/build workflow).

**Key Features:**
- Multiple specialized personas (Architect, Librarian, Critic - future)
- Manual mode switching by user
- Context-aware prompting
- Intelligent model routing per persona mode
- Persistent persona state across conversation

---

## Architecture

### Persona System Overview

```
┌─────────────────────────────────────────────────────────┐
│           User Activates Persona                        │
│           "Create a note about X"                       │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│        Persona Selection & Initialization               │
│        → Architect persona activated                    │
│        → Default mode: Plan                             │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│               Mode-Specific Workflow                    │
│                                                          │
│   Plan Mode:                    Build Mode:             │
│   • Analyze requirements        • Execute plan          │
│   • Ask clarifying questions    • Generate content      │
│   • Create outline              • Apply templates       │
│   • Validate understanding      • Finalize output       │
│                                                          │
│   [User manually switches modes via UI]                 │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│        Model Routing (per mode)                         │
│        Plan: Balanced tier (Sonnet 4)                   │
│        Build: Thorough tier (Opus 4)                    │
└─────────────────────────────────────────────────────────┘
```

---

## Phase 11c: Architect Persona

### Overview

The **Architect persona** is designed for **planning and building complex tasks**, particularly note creation. It operates in two distinct modes that the user manually controls.

**Modes:**
1. **Plan Mode:** Analyze, clarify, and create structured plans
2. **Build Mode:** Execute plans and generate final content

### Workflow

```
User Request
    │
    ▼
┌─────────────┐
│ Plan Mode   │  ← User starts here
│             │
│ • Analyze   │
│ • Question  │
│ • Outline   │
└─────────────┘
    │
    │ User reviews plan
    │ User answers questions
    │ User manually switches mode
    ▼
┌─────────────┐
│ Build Mode  │
│             │
│ • Generate  │
│ • Refine    │
│ • Deliver   │
└─────────────┘
    │
    ▼
Final Output
```

---

## Implementation

### Base Persona Class

```python
# core/personas/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

@dataclass
class PersonaContext:
    """Context passed to persona methods"""
    user_message: str
    conversation_history: list[dict]
    current_mode: str
    metadata: dict[str, Any]

@dataclass
class PersonaResponse:
    """Response from persona"""
    content: str
    mode: str
    actions: list[dict]  # UI actions (show questions, preview, etc.)
    metadata: dict[str, Any]

class AgentPersona(ABC):
    """Base class for all agent personas"""
    
    def __init__(self, name: str, router: 'IntelligentRouter'):
        self.name = name
        self.router = router
        self.current_mode = self.default_mode
        self.state = {}
    
    @property
    @abstractmethod
    def default_mode(self) -> str:
        """Default mode when persona is activated"""
        pass
    
    @property
    @abstractmethod
    def available_modes(self) -> list[str]:
        """List of available modes for this persona"""
        pass
    
    @abstractmethod
    async def process(self, context: PersonaContext) -> PersonaResponse:
        """
        Process user input in current mode
        
        Args:
            context: PersonaContext with user message and history
        
        Returns:
            PersonaResponse with content and actions
        """
        pass
    
    def switch_mode(self, mode: str):
        """User manually switches mode"""
        if mode not in self.available_modes:
            raise ValueError(f"Invalid mode '{mode}' for persona '{self.name}'")
        
        logger.info(f"{self.name} persona switching: {self.current_mode} → {mode}")
        self.current_mode = mode
        self.state["mode_switched_at"] = datetime.now()
    
    def get_system_prompt(self, mode: str) -> str:
        """Get mode-specific system prompt"""
        prompts = self.get_mode_prompts()
        return prompts.get(mode, "")
    
    @abstractmethod
    def get_mode_prompts(self) -> dict[str, str]:
        """Return dict of mode-specific system prompts"""
        pass
```

### Architect Persona Implementation

```python
# core/personas/architect.py
from core.personas.base import AgentPersona, PersonaContext, PersonaResponse
from core.router_v2 import IntelligentRouter

class ArchitectPersona(AgentPersona):
    """
    Architect persona for planning and building complex tasks
    
    Primary use case: AI note creation (Phase 16c)
    
    Modes:
    - plan: Analyze requirements, ask questions, create outline
    - build: Execute plan, generate content, finalize output
    """
    
    @property
    def default_mode(self) -> str:
        return "plan"
    
    @property
    def available_modes(self) -> list[str]:
        return ["plan", "build"]
    
    async def process(self, context: PersonaContext) -> PersonaResponse:
        """Route to appropriate mode handler"""
        if self.current_mode == "plan":
            return await self.plan(context)
        elif self.current_mode == "build":
            return await self.build(context)
        else:
            raise ValueError(f"Unknown mode: {self.current_mode}")
    
    # ========== Plan Mode ==========
    
    async def plan(self, context: PersonaContext) -> PersonaResponse:
        """
        Planning mode: Analyze and create structured plan
        
        Process:
        1. Analyze user request and conversation context
        2. Identify what is known vs. unknown
        3. Generate 2-5 clarifying questions (if needed)
        4. Create structured outline
        5. Suggest template (if applicable)
        """
        # Build planning prompt
        messages = [
            {"role": "system", "content": self.get_system_prompt("plan")},
            *context.conversation_history,
            {"role": "user", "content": context.user_message}
        ]
        
        # Add context from metadata
        if context.metadata.get("related_notes"):
            context_note = self._format_related_notes(context.metadata["related_notes"])
            messages.append({"role": "system", "content": f"Related notes:\n{context_note}"})
        
        # Use balanced tier for planning (Sonnet 4 preferred)
        response = await self.router.complete_with_fallback(
            messages,
            task_type="planning",
            confidence="balanced"
        )
        
        # Parse response into structured plan
        plan = self._parse_planning_response(response.content)
        
        # Store plan in state
        self.state["current_plan"] = plan
        self.state["planned_at"] = datetime.now()
        
        # Generate UI actions
        actions = []
        if plan.questions:
            actions.append({
                "type": "show_questions",
                "questions": plan.questions
            })
        
        return PersonaResponse(
            content=self._format_planning_output(plan),
            mode="plan",
            actions=actions,
            metadata={
                "plan": plan,
                "model_used": response.model,
                "tokens": response.tokens_in + response.tokens_out,
                "cost": response.cost
            }
        )
    
    # ========== Build Mode ==========
    
    async def build(self, context: PersonaContext) -> PersonaResponse:
        """
        Building mode: Execute plan and generate content
        
        Process:
        1. Load plan from state
        2. Incorporate user answers (if any)
        3. Generate content using thorough tier
        4. Apply template structure
        5. Return for user preview
        """
        # Retrieve plan
        plan = self.state.get("current_plan")
        if not plan:
            return PersonaResponse(
                content="No plan found. Please switch to Plan mode first.",
                mode="build",
                actions=[],
                metadata={"error": "no_plan"}
            )
        
        # Build generation prompt
        messages = [
            {"role": "system", "content": self.get_system_prompt("build")},
            {"role": "user", "content": self._construct_build_prompt(plan, context)}
        ]
        
        # Use thorough tier for building (Opus 4 or Sonnet 4)
        response = await self.router.complete_with_fallback(
            messages,
            task_type="content_creation",
            confidence="thorough"
        )
        
        # Parse generated content
        content = self._parse_build_response(response.content)
        
        # Store result in state
        self.state["generated_content"] = content
        self.state["built_at"] = datetime.now()
        
        # Generate preview action
        actions = [{
            "type": "show_preview",
            "content": content,
            "preview_type": context.metadata.get("preview_type", "note")
        }]
        
        return PersonaResponse(
            content=self._format_build_output(content),
            mode="build",
            actions=actions,
            metadata={
                "content": content,
                "model_used": response.model,
                "tokens": response.tokens_in + response.tokens_out,
                "cost": response.cost
            }
        )
    
    # ========== Helper Methods ==========
    
    def _parse_planning_response(self, content: str) -> 'Plan':
        """Parse LLM response into structured Plan object"""
        # Extract sections using regex
        understanding = self._extract_section(content, "What I understand")
        questions = self._extract_list(content, "Questions")
        outline = self._extract_outline(content, "Proposed outline")
        template = self._extract_value(content, "Suggested template")
        
        return Plan(
            understanding=understanding,
            questions=questions,
            outline=outline,
            template=template,
            needs_clarification=len(questions) > 0
        )
    
    def _construct_build_prompt(self, plan: 'Plan', context: PersonaContext) -> str:
        """Construct comprehensive prompt for building"""
        prompt = f"""Based on this plan, generate the final content.

**Plan Understanding:**
{plan.understanding}

**Outline:**
{self._format_outline(plan.outline)}
"""
        
        # Add user answers if available
        if plan.user_answers:
            prompt += f"""

**User's Answers:**
{self._format_answers(plan.user_answers)}
"""
        
        # Add template if specified
        if plan.template:
            prompt += f"""

**Template to follow:**
{plan.template.raw_content}
"""
        
        return prompt
    
    def _format_planning_output(self, plan: 'Plan') -> str:
        """Format plan for display to user"""
        output = f"""**Planning Analysis**

{plan.understanding}

**Proposed Structure:**
{self._format_outline(plan.outline)}
"""
        
        if plan.questions:
            output += f"""

**Questions for clarity:**
{self._format_questions_list(plan.questions)}

Please answer these questions, then I'll switch to Build mode to generate the content.
"""
        else:
            output += """

Ready to build! Switch to Build mode when you're ready to generate the content.
"""
        
        return output
    
    # ========== System Prompts ==========
    
    def get_mode_prompts(self) -> dict[str, str]:
        """Return mode-specific system prompts"""
        return {
            "plan": ARCHITECT_PLAN_PROMPT,
            "build": ARCHITECT_BUILD_PROMPT
        }

# System prompts
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
1. **What I understand:** [1-2 sentence summary]
2. **Questions:** [2-5 questions, if needed]
3. **Proposed outline:** [Hierarchical structure]
4. **Suggested approach:** [How you'll execute in Build mode]

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
```

### Plan Object Structure

```python
# core/personas/models.py
from dataclasses import dataclass, field
from typing import Any

@dataclass
class Plan:
    """Structured plan from Architect Planning mode"""
    understanding: str
    questions: list[str] = field(default_factory=list)
    outline: list[dict] = field(default_factory=list)
    template: Any = None  # Template object if applicable
    user_answers: dict[str, str] = field(default_factory=dict)
    needs_clarification: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_answer(self, question: str, answer: str):
        """Record user's answer to a question"""
        self.user_answers[question] = answer
    
    def is_ready_to_build(self) -> bool:
        """Check if all questions have been answered"""
        if not self.needs_clarification:
            return True
        return len(self.user_answers) == len(self.questions)
```

---

## UI Integration

### Mode Toggle Component

```javascript
// frontend/js/persona-ui.js
class PersonaUI {
    constructor() {
        this.currentPersona = null;
        this.currentMode = null;
    }
    
    renderModeToggle(persona, currentMode, availableModes) {
        const container = document.createElement('div');
        container.className = 'persona-mode-toggle';
        
        container.innerHTML = `
            <div class="persona-info">
                <span class="persona-icon">${this.getPersonaIcon(persona)}</span>
                <span class="persona-name">${persona}</span>
            </div>
            <div class="mode-selector">
                ${availableModes.map(mode => `
                    <button 
                        class="mode-btn ${mode === currentMode ? 'active' : ''}"
                        data-mode="${mode}"
                        onclick="personaUI.switchMode('${mode}')"
                    >
                        ${this.formatModeName(mode)}
                    </button>
                `).join('')}
            </div>
        `;
        
        return container;
    }
    
    async switchMode(mode) {
        // Send IPC to backend
        const result = await window.api.invoke('persona:switch-mode', {
            mode: mode
        });
        
        if (result.success) {
            this.currentMode = mode;
            this.updateModeUI(mode);
            this.showModeNotification(mode);
        }
    }
    
    showModeNotification(mode) {
        const notification = document.createElement('div');
        notification.className = 'mode-notification';
        notification.textContent = `Switched to ${this.formatModeName(mode)} mode`;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => notification.remove(), 300);
        }, 2000);
    }
    
    getPersonaIcon(persona) {
        const icons = {
            'architect': '🏗️',
            'librarian': '📚',
            'critic': '🔍'
        };
        return icons[persona.toLowerCase()] || '🤖';
    }
    
    formatModeName(mode) {
        return mode.charAt(0).toUpperCase() + mode.slice(1);
    }
}
```

### Chat Interface Integration

```
┌─────────────────────────────────────────────────────────┐
│  Polly - Conversation                                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [🏗️ Architect]  [Plan | Build]  Mode: Plan  [⚙️]      │
│   ─────────      ════   ─────                           │
│                  Active                                  │
│                                                          │
│  Brett: Create a note about today's planning session    │
│                                                          │
│  Polly (Plan Mode):                                     │
│  I'll help create a meeting note. Let me clarify:       │
│                                                          │
│  **What I understand:**                                 │
│  You want to document today's planning session          │
│                                                          │
│  **Questions:**                                         │
│  1. Who attended the session?                          │
│  2. What were the main topics discussed?               │
│  3. What decisions were made?                          │
│                                                          │
│  [Answer in chat] or [Skip and build now]              │
│                                                          │
│  ─────────────────────────────────────────────────────  │
│                                                          │
│  Brett: 1. Just me and Polly                           │
│         2. Phase 11 multi-model routing                │
│         3. Support 8 providers, 5-week timeline        │
│                                                          │
│  Polly: ✓ Answers recorded                             │
│                                                          │
│  Ready to generate! [Switch to Build mode]             │
│                                                          │
│  [User clicks "Build" mode button]                     │
│                                                          │
│  Polly (Build Mode):                                    │
│  Generating your meeting note...                        │
│  [Progress indicator]                                   │
│                                                          │
│  ✓ Note generated! [Preview]                           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Configuration

```yaml
# config.yaml
personas:
  architect:
    enabled: true
    default_mode: plan
    
    # Model routing per mode
    routing:
      plan:
        tier: balanced  # Use Sonnet 4
        fallback: ["anthropic", "openai"]
      build:
        tier: thorough  # Use Opus 4 or Sonnet 4
        fallback: ["anthropic", "openai"]
    
    # Behavior settings
    settings:
      max_questions: 5
      always_ask_questions: false  # Only ask when uncertain
      auto_switch_to_build: false  # User manual switch
```

---

## Future Personas

### Librarian Persona (Phase 17+)

```python
class LibrarianPersona(AgentPersona):
    """
    Librarian persona for knowledge base management
    
    Modes:
    - organize: Categorize and structure notes
    - link: Find and create connections between notes
    - summarize: Generate overviews and summaries
    """
    
    @property
    def available_modes(self) -> list[str]:
        return ["organize", "link", "summarize"]
```

**Use cases:**
- Reorganizing note folders
- Finding related notes
- Creating index notes
- Detecting duplicate content
- Suggesting tags

### Critic Persona (Phase 18+)

```python
class CriticPersona(AgentPersona):
    """
    Critic persona for review and improvement
    
    Modes:
    - review: Analyze code or content for issues
    - suggest: Provide improvement recommendations
    - validate: Check consistency and quality
    """
    
    @property
    def available_modes(self) -> list[str]:
        return ["review", "suggest", "validate"]
```

**Use cases:**
- Code review
- Note quality assessment
- Consistency checking
- Style suggestions
- Error detection

---

## Testing

```python
# tests/test_personas.py
import pytest
from core.personas.architect import ArchitectPersona
from core.personas.base import PersonaContext

@pytest.mark.asyncio
async def test_architect_plan_mode():
    architect = ArchitectPersona("architect", mock_router)
    
    context = PersonaContext(
        user_message="Create a note about Phase 11",
        conversation_history=[],
        current_mode="plan",
        metadata={}
    )
    
    response = await architect.plan(context)
    
    assert response.mode == "plan"
    assert response.content
    assert "What I understand" in response.content
    assert architect.state.get("current_plan") is not None

@pytest.mark.asyncio
async def test_architect_build_mode():
    architect = ArchitectPersona("architect", mock_router)
    
    # Set up plan first
    plan = Plan(
        understanding="User wants note about Phase 11",
        questions=[],
        outline=[{"heading": "Overview"}, {"heading": "Details"}]
    )
    architect.state["current_plan"] = plan
    
    context = PersonaContext(
        user_message="Build the note",
        conversation_history=[],
        current_mode="build",
        metadata={}
    )
    
    response = await architect.build(context)
    
    assert response.mode == "build"
    assert response.actions[0]["type"] == "show_preview"
    assert architect.state.get("generated_content") is not None

def test_mode_switching():
    architect = ArchitectPersona("architect", mock_router)
    
    assert architect.current_mode == "plan"  # default
    
    architect.switch_mode("build")
    assert architect.current_mode == "build"
    
    # Invalid mode should raise
    with pytest.raises(ValueError):
        architect.switch_mode("invalid")
```

---

## Performance Targets

**Plan Mode:**
- Response time: < 5s (balanced tier)
- Question quality: 2-5 relevant questions
- Outline accuracy: Matches user intent 90%+

**Build Mode:**
- Response time: < 15s (thorough tier)
- Content quality: Professional, well-structured
- User edits needed: < 20% of content

**Mode Switching:**
- UI latency: < 100ms
- State preservation: 100%

---

## Success Metrics

- [ ] Manual mode switching works reliably
- [ ] Plan mode generates useful questions 80%+ of time
- [ ] Build mode follows plans accurately 90%+ of time
- [ ] User satisfaction with generated content
- [ ] Mode-appropriate model routing working

---

## Related Documents

- [PHASE11_MULTI_MODEL_ENHANCED_V2.md](./PHASE11_MULTI_MODEL_ENHANCED_V2.md) - Overall Phase 11 spec
- [PHASE16C_AI_NOTE_CREATION.md](./PHASE16C_AI_NOTE_CREATION.md) - AI note creation using Architect
- [master_roadmap.md](./master_roadmap.md) - Project roadmap
