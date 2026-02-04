"""
PersonaManager (Phase 16c - Lazy-Loading Architecture)

Manages persona instances and provides a unified interface for Polly to
interact with personas.

Responsibilities:
- Create and manage persona instances
- Route requests to appropriate persona
- Track active persona and state
- Handle mode switching
- Provide persona discovery
- Lazy-load persona prompts on-demand (NEW in Phase 16c)

Architecture:
- At startup: Load only metadata (slug, name, description, modes)
- On activation: Load full prompts for specific mode
- Prompts cached in memory after first load
"""

from typing import Dict, Optional, Type, List, Any
import logging
import os
import yaml
from pathlib import Path

from .base import AgentPersona, PersonaContext, PersonaResponse, PersonaState
from .models import PersonaMetadata, PersonaPromptCache
from .architect import ArchitectPersona
from .implementations.scribe import ScribePersona
from .implementations.professor import ProfessorPersona
from core.router_v2 import IntelligentRouterV2

logger = logging.getLogger(__name__)


class PersonaManager:
    """
    Manager for agent personas with lazy-loading architecture.
    
    Usage:
        manager = PersonaManager(router)
        
        # List available personas (uses metadata only)
        personas = manager.list_personas()
        
        # Activate a persona (loads prompts on-demand)
        manager.activate_persona("scribe", mode="capture")
        
        # Process user input
        context = PersonaContext(user_message="Save this as a note")
        response = await manager.process(context)
        
        # Switch modes (loads new mode prompt if not cached)
        manager.switch_mode("organize")
    
    Architecture:
        - Startup: Load all persona metadata from YAML definitions
        - Activation: Load specific mode prompt on-demand
        - Caching: Keep loaded prompts in memory
        - System prompt: Include active persona + all metadata for routing
    """
    
    # Registry of available personas (hardcoded for now, YAML-based in Phase 23+)
    PERSONA_REGISTRY: Dict[str, Type[AgentPersona]] = {
        "architect": ArchitectPersona,
        "scribe": ScribePersona,  # Phase 16c
        "professor": ProfessorPersona,  # Phase 20+22
        # Future personas (Phase 17-22):
        # "librarian": LibrarianPersona,
        # "programmer": ProgrammerPersona,
        # "administrator": AdministratorPersona,
    }
    
    def __init__(
        self, 
        router: IntelligentRouterV2, 
        definitions_dir: Optional[str] = None,
        skill_manager: Optional[Any] = None,
        rag: Optional[Any] = None,
        learning_tracker: Optional[Any] = None,
        curriculum_manager: Optional[Any] = None,
        template_manager: Optional[Any] = None
    ):
        """
        Initialize persona manager.
        
        Args:
            router: IntelligentRouterV2 instance for LLM calls
            definitions_dir: Directory containing persona YAML definitions
                           (defaults to core/personas/definitions/)
            skill_manager: SkillManager instance for loading skills (Phase 16c)
            rag: UnifiedRAG instance for knowledge base search (Phase 16c)
            learning_tracker: LearningTracker instance for tracking learning progress (Phase 22)
            curriculum_manager: CurriculumManager instance for curriculum management (Phase 23)
            template_manager: CurriculumTemplateManager instance for templates (Phase 23)
        """
        self.router = router
        self.skill_manager = skill_manager
        self.rag = rag
        self.learning_tracker = learning_tracker
        self.curriculum_manager = curriculum_manager
        self.template_manager = template_manager
        
        # Set definitions directory
        if definitions_dir is None:
            # Default to core/personas/definitions/
            current_dir = Path(__file__).parent
            definitions_dir = current_dir / "definitions"
        self.definitions_dir = Path(definitions_dir)
        
        # Active persona instance
        self.active_persona: Optional[AgentPersona] = None
        self.active_persona_name: Optional[str] = None
        
        # Persona instances cache (reuse if reactivated)
        self._persona_cache: Dict[str, AgentPersona] = {}
        
        # Metadata cache (loaded at startup)
        self.metadata_cache: Dict[str, PersonaMetadata] = {}
        
        # Prompt cache (loaded on-demand)
        self.loaded_prompts: Dict[str, PersonaPromptCache] = {}
        
        # Load all persona metadata
        self._load_all_metadata()
        
        logger.info(
            f"PersonaManager initialized with {len(self.metadata_cache)} personas"
        )
    
    # ========== Metadata Loading (Phase 16c) ==========
    
    def _load_all_metadata(self):
        """
        Load metadata for all personas at startup.
        
        This method discovers all YAML definition files in the definitions
        directory and loads only their metadata (not full prompts). This
        enables fast startup and persona discovery without loading all prompts.
        
        Metadata includes:
        - slug, name, description, icon
        - available modes
        - skills required
        - collaboration partners
        
        Full prompts are loaded on-demand when a persona is activated.
        """
        logger.info(f"Loading persona metadata from {self.definitions_dir}")
        
        # Create definitions directory if it doesn't exist
        self.definitions_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all YAML files
        yaml_files = list(self.definitions_dir.glob("*.yaml")) + \
                     list(self.definitions_dir.glob("*.yml"))
        
        if not yaml_files:
            logger.warning(
                f"No persona definitions found in {self.definitions_dir}. "
                f"System will use hardcoded personas only."
            )
            return
        
        # Load metadata from each file
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                
                # Extract metadata (top-level fields only, not mode prompts)
                metadata = PersonaMetadata(
                    slug=data.get("slug", yaml_file.stem),
                    name=data.get("name", yaml_file.stem.capitalize()),
                    description=data.get("description", ""),
                    icon=data.get("icon", "🤖"),
                    modes=list(data.get("modes", {}).keys()),
                    primary_domain=data.get("primary_domain"),
                    skills=data.get("skills", []),
                    collaboration_partners=data.get("collaboration", {}).get("partners", [])
                )
                
                self.metadata_cache[metadata.slug] = metadata
                
                logger.info(
                    f"Loaded metadata for {metadata.name} persona "
                    f"({len(metadata.modes)} modes)"
                )
                
            except Exception as e:
                logger.error(
                    f"Failed to load persona metadata from {yaml_file}: {e}"
                )
        
        logger.info(
            f"Loaded metadata for {len(self.metadata_cache)} personas"
        )
    
    def list_personas(self) -> List[PersonaMetadata]:
        """
        Get list of all available personas (metadata only).
        
        Returns:
            List of PersonaMetadata objects
        """
        return list(self.metadata_cache.values())
    
    def get_persona_metadata(self, slug: str) -> Optional[PersonaMetadata]:
        """
        Get metadata for a specific persona.
        
        Args:
            slug: Persona slug
        
        Returns:
            PersonaMetadata or None if not found
        """
        return self.metadata_cache.get(slug)
    
    # ========== Prompt Loading (Phase 16c) ==========
    
    def _load_persona_prompt(self, slug: str, mode: str) -> str:
        """
        Load prompt for a specific persona mode on-demand.
        
        This method loads the full prompt text for a persona's mode from
        the YAML definition file. Prompts are cached after first load.
        
        Args:
            slug: Persona slug (e.g., "scribe")
            mode: Mode slug (e.g., "capture")
        
        Returns:
            Full prompt text for the mode
        
        Raises:
            ValueError: If persona or mode not found
            FileNotFoundError: If YAML file doesn't exist
        """
        # Check cache first
        cache_key = f"{slug}:{mode}"
        if cache_key in self.loaded_prompts:
            logger.debug(f"Using cached prompt for {cache_key}")
            return self.loaded_prompts[cache_key].prompt
        
        logger.info(f"Loading prompt for {slug}:{mode}")
        
        # Find YAML file
        yaml_path = self.definitions_dir / f"{slug}.yaml"
        if not yaml_path.exists():
            # Try .yml extension
            yaml_path = self.definitions_dir / f"{slug}.yml"
            if not yaml_path.exists():
                raise FileNotFoundError(
                    f"No definition file found for persona '{slug}' "
                    f"in {self.definitions_dir}"
                )
        
        # Load YAML
        try:
            with open(yaml_path, 'r') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            raise ValueError(f"Failed to parse YAML for {slug}: {e}")
        
        # Extract mode prompt
        modes = data.get("modes", {})
        if mode not in modes:
            available_modes = ", ".join(modes.keys())
            raise ValueError(
                f"Mode '{mode}' not found for persona '{slug}'. "
                f"Available modes: {available_modes}"
            )
        
        mode_data = modes[mode]
        prompt = mode_data.get("prompt", "")
        
        if not prompt:
            raise ValueError(
                f"No prompt defined for {slug}:{mode}"
            )
        
        # Cache the prompt
        self.loaded_prompts[cache_key] = PersonaPromptCache(
            slug=slug,
            mode=mode,
            prompt=prompt
        )
        
        logger.info(
            f"Loaded and cached prompt for {slug}:{mode} "
            f"({len(prompt)} chars)"
        )
        
        return prompt
    
    def get_prompt_for_mode(self, slug: str, mode: str) -> Optional[str]:
        """
        Get prompt for a persona mode (public API).
        
        Args:
            slug: Persona slug
            mode: Mode slug
        
        Returns:
            Prompt text or None if not found
        """
        try:
            return self._load_persona_prompt(slug, mode)
        except (ValueError, FileNotFoundError) as e:
            logger.error(f"Failed to load prompt for {slug}:{mode}: {e}")
            return None
    
    def clear_prompt_cache(self):
        """Clear all cached prompts (useful for development/testing)"""
        self.loaded_prompts.clear()
        logger.info("Cleared prompt cache")
    
    # ========== Persona Management ==========
    
    def activate_persona(self, persona_name: str, mode: Optional[str] = None) -> PersonaState:
        """
        Activate a persona with lazy-loaded prompts.
        
        Args:
            persona_name: Name of persona to activate ("architect", "scribe", etc.)
            mode: Optional mode to activate (uses default mode if not specified)
        
        Returns:
            PersonaState for the activated persona
        
        Raises:
            ValueError: If persona_name is not registered or mode is invalid
        """
        if persona_name not in self.PERSONA_REGISTRY:
            available = ", ".join(self.PERSONA_REGISTRY.keys())
            raise ValueError(
                f"Unknown persona '{persona_name}'. "
                f"Available personas: {available}"
            )
        
        # Deactivate current persona if any
        if self.active_persona:
            self.active_persona.deactivate()
        
        # Get or create persona instance
        if persona_name in self._persona_cache:
            persona = self._persona_cache[persona_name]
            logger.info(f"Reactivating cached {persona_name} persona")
        else:
            persona_class = self.PERSONA_REGISTRY[persona_name]
            
            # Pass dependencies to personas that need them
            if persona_name == "scribe":
                persona = persona_class(
                    name=persona_name, 
                    router=self.router,
                    skill_manager=self.skill_manager,
                    rag=self.rag
                )
            elif persona_name == "professor":
                # Professor needs skill_manager, rag, and learning_tracker (Phase 20+22)
                # Plus curriculum_manager and template_manager (Phase 23)
                persona = persona_class(
                    name=persona_name,
                    router=self.router,
                    skill_manager=self.skill_manager,
                    rag=self.rag,
                    learning_tracker=self.learning_tracker,
                    curriculum_manager=self.curriculum_manager,
                    template_manager=self.template_manager
                )
            else:
                # Other personas don't need additional dependencies yet
                persona = persona_class(name=persona_name, router=self.router)
            
            self._persona_cache[persona_name] = persona
            logger.info(f"Created new {persona_name} persona")
        
        # Determine target mode
        target_mode = mode or persona.default_mode
        
        # Load prompt for target mode (lazy-loading)
        # Note: For now, hardcoded personas (like Architect) handle prompts internally
        # YAML-based personas (Phase 16c+) will use loaded prompts
        if persona_name in self.metadata_cache:
            # This is a YAML-based persona - load prompt
            try:
                prompt = self._load_persona_prompt(persona_name, target_mode)
                # Store prompt in persona for use (will enhance persona base class in Day 3)
                logger.debug(f"Loaded prompt for {persona_name}:{target_mode}")
            except (ValueError, FileNotFoundError) as e:
                logger.warning(
                    f"Could not load prompt for {persona_name}:{target_mode}: {e}. "
                    f"Using hardcoded prompts."
                )
        
        # Activate persona
        state = persona.activate()
        
        # Switch to target mode if different from default
        if target_mode != state.current_mode:
            state = persona.switch_mode(target_mode)
        
        self.active_persona = persona
        self.active_persona_name = persona_name
        
        logger.info(
            f"Activated {persona_name} persona "
            f"(mode: {state.current_mode})"
        )
        
        return state
    
    def deactivate_persona(self):
        """Deactivate current persona"""
        if self.active_persona:
            logger.info(f"Deactivating {self.active_persona_name} persona")
            self.active_persona.deactivate()
            self.active_persona = None
            self.active_persona_name = None
    
    def get_active_persona(self) -> Optional[AgentPersona]:
        """Get currently active persona"""
        return self.active_persona
    
    def get_active_persona_name(self) -> Optional[str]:
        """Get name of currently active persona"""
        return self.active_persona_name
    
    def is_persona_active(self) -> bool:
        """Check if any persona is currently active"""
        return self.active_persona is not None
    
    # ========== Processing ==========
    
    async def process(self, context: PersonaContext) -> PersonaResponse:
        """
        Process user input with active persona.
        
        Args:
            context: PersonaContext with user message
        
        Returns:
            PersonaResponse from active persona
        
        Raises:
            RuntimeError: If no persona is active
        """
        if not self.active_persona:
            raise RuntimeError(
                "No persona is active. Call activate_persona() first."
            )
        
        logger.info(
            f"Processing with {self.active_persona_name} persona "
            f"(mode: {self.active_persona.state.current_mode})"
        )
        
        return await self.active_persona.process(context)
    
    def get_system_prompt(self, include_metadata: bool = True) -> str:
        """
        Get system prompt that includes active persona and metadata.
        
        This method constructs a system prompt that includes:
        1. Active persona's mode-specific prompt (if any)
        2. Metadata about all available personas (for routing/suggestions)
        
        Args:
            include_metadata: Whether to include metadata about available personas
        
        Returns:
            Complete system prompt string
        """
        prompt_parts = []
        
        # Add active persona prompt if available
        if self.active_persona and self.active_persona_name:
            current_mode = self.active_persona.state.current_mode
            
            # Try to get loaded prompt for YAML-based personas
            cache_key = f"{self.active_persona_name}:{current_mode}"
            if cache_key in self.loaded_prompts:
                prompt_parts.append(self.loaded_prompts[cache_key].prompt)
            else:
                # Fallback: Try to get from persona's own method (hardcoded personas)
                if hasattr(self.active_persona, 'get_mode_prompts'):
                    mode_prompts = self.active_persona.get_mode_prompts()
                    if current_mode in mode_prompts:
                        prompt_parts.append(mode_prompts[current_mode])
        
        # Add metadata section for routing (Phase 21 - Orchestrator)
        if include_metadata and self.metadata_cache:
            metadata_section = "\n\n## Available Personas\n\n"
            metadata_section += "You have access to these specialized personas:\n\n"
            
            for metadata in self.metadata_cache.values():
                metadata_section += f"- **{metadata.icon} {metadata.name}** ({metadata.slug})\n"
                metadata_section += f"  {metadata.description}\n"
                metadata_section += f"  Modes: {', '.join(metadata.modes)}\n"
                if metadata.primary_domain:
                    metadata_section += f"  Primary domain: {metadata.primary_domain}\n"
                metadata_section += "\n"
            
            metadata_section += (
                "When orchestrator mode is enabled, you can collaborate with other "
                "personas by requesting their help for tasks that match their expertise.\n"
            )
            
            prompt_parts.append(metadata_section)
        
        return "\n\n".join(prompt_parts)
    
    # ========== Mode Management ==========
    
    def switch_mode(self, mode: str) -> PersonaState:
        """
        Switch active persona to a different mode (with lazy-loading).
        
        Args:
            mode: Target mode name
        
        Returns:
            Updated PersonaState
        
        Raises:
            RuntimeError: If no persona is active
            ValueError: If mode is invalid for active persona
        """
        if not self.active_persona:
            raise RuntimeError(
                "No persona is active. Call activate_persona() first."
            )
        
        logger.info(
            f"Switching {self.active_persona_name} persona: "
            f"{self.active_persona.state.current_mode} → {mode}"
        )
        
        # Load prompt for new mode if YAML-based persona
        if self.active_persona_name in self.metadata_cache:
            try:
                prompt = self._load_persona_prompt(self.active_persona_name, mode)
                logger.debug(f"Loaded prompt for {self.active_persona_name}:{mode}")
            except (ValueError, FileNotFoundError) as e:
                logger.warning(
                    f"Could not load prompt for {self.active_persona_name}:{mode}: {e}"
                )
        
        return self.active_persona.switch_mode(mode)
    
    def get_current_mode(self) -> Optional[str]:
        """Get current mode of active persona"""
        if not self.active_persona:
            return None
        return self.active_persona.state.current_mode
    
    def get_available_modes(self) -> List[str]:
        """Get available modes for active persona"""
        if not self.active_persona:
            return []
        return self.active_persona.available_modes
    
    # ========== State Management ==========
    
    def get_state(self) -> Optional[PersonaState]:
        """Get state of active persona"""
        if not self.active_persona:
            return None
        return self.active_persona.get_state()
    
    def get_state_dict(self) -> Optional[Dict]:
        """Get state as dictionary"""
        state = self.get_state()
        if not state:
            return None
        return state.to_dict()
    
    # ========== Discovery ==========
    
    @classmethod
    def list_available_personas(cls) -> List[Dict[str, str]]:
        """
        Get list of available personas with metadata.
        
        Returns:
            List of dicts with persona info
        """
        personas = []
        
        for name, persona_class in cls.PERSONA_REGISTRY.items():
            # Create temporary instance to get metadata
            temp_instance = persona_class(name=name, router=None)
            
            personas.append({
                "name": name,
                "default_mode": temp_instance.default_mode,
                "available_modes": temp_instance.available_modes,
                "description": persona_class.__doc__ or ""
            })
        
        return personas
    
    @classmethod
    def get_persona_info(cls, persona_name: str) -> Dict[str, any]:
        """
        Get detailed info about a specific persona.
        
        Args:
            persona_name: Name of persona
        
        Returns:
            Dict with persona metadata
        
        Raises:
            ValueError: If persona_name is not registered
        """
        if persona_name not in cls.PERSONA_REGISTRY:
            raise ValueError(f"Unknown persona: {persona_name}")
        
        persona_class = cls.PERSONA_REGISTRY[persona_name]
        temp_instance = persona_class(name=persona_name, router=None)
        
        return {
            "name": persona_name,
            "class": persona_class.__name__,
            "default_mode": temp_instance.default_mode,
            "available_modes": temp_instance.available_modes,
            "mode_prompts": list(temp_instance.get_mode_prompts().keys()),
            "description": persona_class.__doc__ or ""
        }
    
    # ========== Utility ==========
    
    def __repr__(self) -> str:
        if self.active_persona:
            return (
                f"<PersonaManager active={self.active_persona_name} "
                f"mode={self.active_persona.state.current_mode}>"
            )
        else:
            return "<PersonaManager active=None>"
