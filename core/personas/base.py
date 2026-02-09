"""
Base classes for Agent Personas (Phase 11c)

This module defines the base persona framework that allows Polly to adopt
different specialized modes of operation, like the Architect persona for
planning and building complex tasks.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ========== Data Models ==========

@dataclass
class PersonaContext:
    """
    Context passed to persona processing methods.
    
    Contains all information needed for a persona to process user input,
    including conversation history, current state, and metadata.
    """
    user_message: str
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    current_mode: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_metadata(self, key: str, value: Any):
        """Add metadata to context"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value with default"""
        return self.metadata.get(key, default)


@dataclass
class PersonaAction:
    """
    Action that a persona wants the UI to perform.
    
    Examples:
    - Show questions form
    - Display preview modal
    - Enable mode switching
    - Update UI state
    """
    type: str
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "type": self.type,
            "data": self.data
        }


@dataclass
class PersonaResponse:
    """
    Response from a persona after processing user input.
    
    Contains:
    - Content to show the user
    - Current mode
    - Actions for the UI to perform
    - Metadata about the response
    """
    content: str
    mode: str
    actions: List[PersonaAction] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def add_action(self, action_type: str, data: Dict[str, Any] = None):
        """Add an action to the response"""
        self.actions.append(PersonaAction(type=action_type, data=data or {}))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "content": self.content,
            "mode": self.mode,
            "actions": [a.to_dict() for a in self.actions],
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class PersonaState:
    """
    Persistent state for a persona instance.
    
    Tracks:
    - Current mode
    - Mode history
    - Persona-specific data (plan, generated content, etc.)
    - Timestamps
    """
    persona_name: str
    current_mode: str
    data: Dict[str, Any] = field(default_factory=dict)
    mode_history: List[Dict[str, Any]] = field(default_factory=list)
    activated_at: datetime = field(default_factory=datetime.now)
    last_interaction: datetime = field(default_factory=datetime.now)
    
    def switch_mode(self, new_mode: str):
        """Record mode switch"""
        self.mode_history.append({
            "from": self.current_mode,
            "to": new_mode,
            "timestamp": datetime.now()
        })
        self.current_mode = new_mode
        self.last_interaction = datetime.now()
    
    def set_data(self, key: str, value: Any):
        """Set persona-specific data"""
        self.data[key] = value
        self.last_interaction = datetime.now()
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """Get persona-specific data"""
        return self.data.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "persona_name": self.persona_name,
            "current_mode": self.current_mode,
            "data": self.data,
            "mode_history": self.mode_history,
            "activated_at": self.activated_at.isoformat(),
            "last_interaction": self.last_interaction.isoformat()
        }


# ========== Base Persona Class ==========

class AgentPersona(ABC):
    """
    Base class for all agent personas.
    
    A persona is a specialized mode of operation for Polly that provides
    a distinct workflow and interaction pattern. Personas can have multiple
    modes that users manually switch between.
    
    Example: Architect persona
    - Plan mode: Analyze and create structured plans
    - Build mode: Execute plans and generate content
    
    Subclasses must implement:
    - default_mode: Initial mode when persona is activated
    - available_modes: List of mode names
    - process(): Handle user input in current mode
    - get_mode_prompts(): System prompts for each mode
    """
    
    def __init__(self, name: str, router: Any):
        """
        Initialize persona.
        
        Args:
            name: Persona name (e.g., "architect")
            router: IntelligentRouterV2 instance for LLM calls
        """
        self.name = name
        self.router = router
        
        # Initialize state
        self.state = PersonaState(
            persona_name=name,
            current_mode=self.default_mode
        )
        
        # Initialize Mem0 adapter if enabled
        self.mem0 = None
        self.config = getattr(router, 'config', {})
        if self._is_mem0_enabled():
            try:
                from core.memory.mem0_adapter import Mem0Adapter
                self.mem0 = Mem0Adapter(self.config)
                logger.debug(f"{name} persona: Mem0 adaptive memory enabled")
            except ImportError:
                logger.debug(f"{name} persona: Mem0 not available")
            except Exception as e:
                logger.warning(f"{name} persona: Failed to initialize Mem0: {e}")
        
        logger.info(f"Initialized {name} persona (default mode: {self.default_mode})")
    
    # ========== Abstract Properties ==========
    
    @property
    @abstractmethod
    def default_mode(self) -> str:
        """
        Default mode when persona is first activated.
        
        Returns:
            Mode name (e.g., "plan")
        """
        pass
    
    @property
    @abstractmethod
    def available_modes(self) -> List[str]:
        """
        List of available modes for this persona.
        
        Returns:
            List of mode names (e.g., ["plan", "build"])
        """
        pass
    
    # ========== Abstract Methods ==========
    
    @abstractmethod
    async def process(self, context: PersonaContext) -> PersonaResponse:
        """
        Process user input in the current mode.
        
        This is the main entry point for persona logic. Route to mode-specific
        handlers based on current_mode.
        
        Args:
            context: PersonaContext with user message and conversation history
        
        Returns:
            PersonaResponse with content, actions, and metadata
        """
        pass
    
    @abstractmethod
    def get_mode_prompts(self) -> Dict[str, str]:
        """
        Get system prompts for each mode.
        
        Returns:
            Dictionary mapping mode name to system prompt
            Example: {"plan": "You are...", "build": "You are..."}
        """
        pass
    
    # ========== Public Methods ==========
    
    def activate(self) -> PersonaState:
        """
        Activate this persona.
        
        Called when user explicitly activates this persona or when
        Polly auto-detects that this persona should be used.
        
        Returns:
            Current persona state
        """
        logger.info(f"Activating {self.name} persona")
        self.state = PersonaState(
            persona_name=self.name,
            current_mode=self.default_mode
        )
        return self.state
    
    def switch_mode(self, mode: str) -> PersonaState:
        """
        Switch to a different mode.
        
        User manually requests mode switch (e.g., Plan → Build).
        
        Args:
            mode: Target mode name
        
        Returns:
            Updated persona state
        
        Raises:
            ValueError: If mode is not in available_modes
        """
        if mode not in self.available_modes:
            raise ValueError(
                f"Invalid mode '{mode}' for persona '{self.name}'. "
                f"Available modes: {', '.join(self.available_modes)}"
            )
        
        old_mode = self.state.current_mode
        self.state.switch_mode(mode)
        
        logger.info(f"{self.name} persona: {old_mode} → {mode}")
        
        return self.state
    
    def get_system_prompt(self, mode: str = None) -> str:
        """
        Get system prompt for a specific mode.
        
        Args:
            mode: Mode name (defaults to current_mode)
        
        Returns:
            System prompt string
        """
        mode = mode or self.state.current_mode
        prompts = self.get_mode_prompts()
        
        if mode not in prompts:
            logger.warning(f"No system prompt for mode '{mode}', using default")
            return prompts.get(self.default_mode, "")
        
        return prompts[mode]
    
    def get_state(self) -> PersonaState:
        """Get current persona state"""
        return self.state
    
    def deactivate(self):
        """Deactivate this persona"""
        logger.info(f"Deactivating {self.name} persona")
        # State is preserved for potential reactivation
    
    # ========== Protected Helper Methods ==========
    
    def _build_messages(
        self,
        context: PersonaContext,
        system_prompt: str = None,
        include_history: bool = True
    ) -> List[Dict[str, str]]:
        """
        Build message array for LLM call.
        
        Args:
            context: Persona context
            system_prompt: System prompt (defaults to current mode's prompt)
            include_history: Whether to include conversation history
        
        Returns:
            List of message dicts for router
        """
        messages = []
        
        # Add system prompt
        if system_prompt is None:
            system_prompt = self.get_system_prompt()
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        if include_history and context.conversation_history:
            messages.extend(context.conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": context.user_message})
        
        return messages
    
    def _is_mem0_enabled(self) -> bool:
        """Check if Mem0 is enabled in config."""
        if self.config.get('memory', {}).get('provider') != 'mem0':
            return False
        return self.config.get('memory', {}).get('mem0', {}).get('enabled', False)
    
    def _get_memory_context(self, query: str, limit: int = 3) -> str:
        """
        Get persona-specific memory context for LLM calls.
        
        Retrieves relevant memories from this persona's namespace
        (e.g., "persona:scribe") to provide context-aware responses.
        
        Args:
            query: Query to search for relevant memories
            limit: Maximum number of memories to retrieve
        
        Returns:
            Formatted context string (empty if Mem0 disabled or no memories)
        
        Example:
            >>> context = self._get_memory_context("enrichment style preferences")
            >>> system_prompt = f"You are the Scribe...\\n\\n{context}\\n\\nTask: ..."
        """
        if not self.mem0:
            return ""
        
        try:
            user_id = f"persona:{self.name}"
            return self.mem0.get_relevant_context(query, user_id, limit)
        except Exception as e:
            logger.warning(f"{self.name} persona: Failed to get memory context: {e}")
            return ""
    
    def _add_memory(self, content: str, metadata: Dict[str, Any] = None):
        """
        Add a memory to this persona's namespace.
        
        Stores information that should inform future interactions,
        such as user preferences, patterns, or decisions.
        
        Args:
            content: Memory content
            metadata: Optional metadata (type, confidence, etc.)
        
        Example:
            >>> self._add_memory(
            ...     content="User prefers concise enrichment style with minimal commentary",
            ...     metadata={'type': 'preference', 'confidence': 0.9}
            ... )
        """
        if not self.mem0:
            return
        
        try:
            user_id = f"persona:{self.name}"
            if metadata is None:
                metadata = {}
            metadata['persona'] = self.name
            metadata['mode'] = self.state.current_mode
            
            self.mem0.add_memory(content, user_id, metadata)
            logger.debug(f"{self.name} persona: Added memory - {content[:50]}...")
        except Exception as e:
            logger.warning(f"{self.name} persona: Failed to add memory: {e}")
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name} mode={self.state.current_mode}>"
