"""
Data models for Persona System (Phase 16c)

Defines metadata and data structures for the persona system,
including lazy-loading support and Architect persona models.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


# ========== Lazy-Loading Models (Phase 16c) ==========

@dataclass
class PersonaMetadata:
    """
    Lightweight metadata for personas.
    
    Loaded at startup to provide persona discovery without loading
    full prompts. This enables lazy-loading architecture where prompts
    are only loaded when a persona is activated.
    
    Attributes:
        slug: Unique identifier for persona (e.g., "scribe", "librarian")
        name: Human-readable name (e.g., "Scribe", "Librarian")
        description: Brief description of persona's purpose
        icon: Emoji icon for UI display
        modes: List of available mode names (e.g., ["capture", "organize", "enrich", "edit"])
        primary_domain: Primary domain this persona works with (optional)
        skills: List of skill names this persona uses
        collaboration_partners: List of persona slugs this persona collaborates with
    """
    slug: str
    name: str
    description: str
    icon: str
    modes: List[str]
    primary_domain: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    collaboration_partners: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "slug": self.slug,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "modes": self.modes,
            "primary_domain": self.primary_domain,
            "skills": self.skills,
            "collaboration_partners": self.collaboration_partners
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PersonaMetadata':
        """Create from dictionary"""
        return cls(
            slug=data["slug"],
            name=data["name"],
            description=data["description"],
            icon=data["icon"],
            modes=data["modes"],
            primary_domain=data.get("primary_domain"),
            skills=data.get("skills", []),
            collaboration_partners=data.get("collaboration_partners", [])
        )


@dataclass
class ModeMetadata:
    """
    Metadata for a specific persona mode.
    
    Attributes:
        name: Mode name (e.g., "Capture", "Organize")
        slug: Mode slug (e.g., "capture", "organize")
        description: Brief description of mode's purpose
    """
    name: str
    slug: str
    description: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "slug": self.slug,
            "description": self.description
        }


@dataclass
class PersonaPromptCache:
    """
    Cache entry for a loaded persona prompt.
    
    Attributes:
        slug: Persona slug
        mode: Mode slug
        prompt: Full prompt text
        loaded_at: When prompt was loaded
    """
    slug: str
    mode: str
    prompt: str
    loaded_at: datetime = field(default_factory=datetime.now)
    
    @property
    def cache_key(self) -> str:
        """Get cache key for this prompt"""
        return f"{self.slug}:{self.mode}"


# ========== Architect Persona Models (Phase 11c) ==========

@dataclass
class OutlineNode:
    """
    Represents a node in a hierarchical outline.
    
    Attributes:
        level: Heading level (1-6)
        title: Section title
        content: Optional content/description for this section
        children: Child nodes
    """
    level: int
    title: str
    content: Optional[str] = None
    children: List['OutlineNode'] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "level": self.level,
            "title": self.title,
            "content": self.content,
            "children": [child.to_dict() for child in self.children]
        }


@dataclass
class Plan:
    """
    Represents a plan created by Architect persona.
    
    Attributes:
        understanding: What Architect understands about the request
        questions: List of clarifying questions (if any)
        outline: Hierarchical outline structure
        approach: Suggested approach for execution (optional, defaults to empty string)
        template: Template suggestion (optional)
        needs_clarification: Whether clarification is needed
        user_answers: Dictionary of user answers to questions
        created_at: When plan was created
    """
    understanding: str
    questions: List[str]
    outline: List[OutlineNode]
    approach: str = ""
    template: Optional[str] = None
    needs_clarification: bool = False
    user_answers: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "understanding": self.understanding,
            "questions": self.questions,
            "outline": [node.to_dict() for node in self.outline],
            "approach": self.approach,
            "template": self.template,
            "needs_clarification": self.needs_clarification,
            "user_answers": self.user_answers,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Plan':
        """Create Plan from dictionary"""
        outline = [OutlineNode(**node) if isinstance(node, dict) else node 
                   for node in data.get("outline", [])]
        return cls(
            understanding=data.get("understanding", ""),
            questions=data.get("questions", []),
            outline=outline,
            approach=data.get("approach", ""),
            template=data.get("template"),
            needs_clarification=data.get("needs_clarification", False),
            user_answers=data.get("user_answers", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now()
        )
    
    def get_unanswered_questions(self) -> List[str]:
        """Get list of questions that haven't been answered yet"""
        return [q for q in self.questions if q not in self.user_answers]
    
    def add_answer(self, question: str, answer: str):
        """Add user's answer to a question"""
        self.user_answers[question] = answer


@dataclass
class GeneratedContent:
    """
    Content generated by Architect persona in Build mode.
    
    Attributes:
        content: The generated markdown content
        format: Format of the content (default: "markdown")
        title: Title of the generated content
        tags: Tags to apply to the content
        metadata: Additional metadata about the generation
        generated_at: When content was generated
    """
    content: str
    format: str = "markdown"
    title: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "content": self.content,
            "format": self.format,
            "title": self.title,
            "tags": self.tags,
            "metadata": self.metadata,
            "generated_at": self.generated_at.isoformat()
        }


@dataclass
class Template:
    """
    Template for note generation.
    
    Attributes:
        name: Template name
        structure: Template structure (markdown)
        variables: Variables that can be substituted
    """
    name: str
    structure: str
    variables: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "structure": self.structure,
            "variables": self.variables
        }

