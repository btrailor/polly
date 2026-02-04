"""
Curriculum Manager (Phase 23 - Curriculum Learning System)

Manages structured learning curricula with sections, enrichment, and progress tracking.
Separate from LearningTracker (which tracks individual topics).
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
import json
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class CurriculumSection:
    """A section/subheading within a curriculum (e.g., week-1.1)"""
    
    # Identity
    id: str                                # "week-1.1"
    title: str                             # "Platform Overview"
    type: str                              # "lesson", "hands-on", "project", "assessment"
    order: int                             # 1, 2, 3...
    parent_id: Optional[str] = None        # "week-1"
    
    # Content
    description: str = ""                  # What this section covers
    concepts: List[str] = field(default_factory=list)  # ["norns-architecture", "supercollider"]
    estimated_time: str = "1-2 hours"      # Human-readable estimate
    
    # Enrichment (added when section starts)
    enriched: bool = False
    resources: List[Dict] = field(default_factory=list)
    exercises: List[str] = field(default_factory=list)  # Exercise IDs
    diagrams: List[str] = field(default_factory=list)   # Diagram paths
    examples: List[str] = field(default_factory=list)   # Example code paths
    explanation: str = ""                  # Detailed explanation (added during enrichment)
    assessment_criteria: List[str] = field(default_factory=list)  # "You've mastered this when..."
    
    # Progress tracking
    status: str = "not_started"            # "not_started", "in_progress", "completed", "skipped"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    time_spent_minutes: int = 0
    mastery_level: Optional[int] = None    # 1-5 (self-reported on completion)
    notes_created: List[str] = field(default_factory=list)  # Paths to notes
    struggles: List[str] = field(default_factory=list)       # What was challenging
    breakthroughs: List[str] = field(default_factory=list)   # Aha moments
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert datetime objects to ISO format
        if self.started_at:
            data['started_at'] = self.started_at.isoformat()
        if self.completed_at:
            data['completed_at'] = self.completed_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CurriculumSection':
        """Create section from dictionary."""
        # Convert ISO strings back to datetime
        if data.get('started_at'):
            data['started_at'] = datetime.fromisoformat(data['started_at'])
        if data.get('completed_at'):
            data['completed_at'] = datetime.fromisoformat(data['completed_at'])
        return cls(**data)


@dataclass
class Curriculum:
    """A complete learning curriculum"""
    
    # Identity
    id: str                                # "monome-norns"
    title: str                             # "Programming Monome Norns Scripts"
    version: str = "1.0"
    
    # Metadata
    created: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    status: str = "draft"                  # "draft", "active", "completed", "paused"
    
    # Learning context
    goal: str = ""                         # What learner wants to achieve
    current_level: str = ""                # Starting knowledge level
    estimated_duration: str = ""           # "8 weeks"
    
    # Structure
    sections: List[CurriculumSection] = field(default_factory=list)
    current_section_id: Optional[str] = None
    
    # References
    skills_referenced: List[str] = field(default_factory=list)  # Skill package IDs
    curriculum_template_id: Optional[str] = None                # Template used
    
    # Stats (calculated)
    total_sections: int = 0
    completed_sections: int = 0
    in_progress_sections: int = 0
    completion_percentage: float = 0.0
    total_time_minutes: int = 0
    mastery_average: float = 0.0
    
    def calculate_stats(self):
        """Recalculate statistics from sections."""
        self.total_sections = len(self.sections)
        self.completed_sections = sum(1 for s in self.sections if s.status == "completed")
        self.in_progress_sections = sum(1 for s in self.sections if s.status == "in_progress")
        
        # Completion percentage
        if self.total_sections > 0:
            self.completion_percentage = (self.completed_sections / self.total_sections) * 100
        else:
            self.completion_percentage = 0.0
        
        # Total time spent
        self.total_time_minutes = sum(s.time_spent_minutes for s in self.sections)
        
        # Average mastery level
        mastery_scores = [s.mastery_level for s in self.sections if s.mastery_level is not None]
        if mastery_scores:
            self.mastery_average = sum(mastery_scores) / len(mastery_scores)
        else:
            self.mastery_average = 0.0
        
        self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'version': self.version,
            'created': self.created.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'status': self.status,
            'goal': self.goal,
            'current_level': self.current_level,
            'estimated_duration': self.estimated_duration,
            'sections': [s.to_dict() for s in self.sections],
            'current_section_id': self.current_section_id,
            'skills_referenced': self.skills_referenced,
            'curriculum_template_id': self.curriculum_template_id,
            'total_sections': self.total_sections,
            'completed_sections': self.completed_sections,
            'in_progress_sections': self.in_progress_sections,
            'completion_percentage': self.completion_percentage,
            'total_time_minutes': self.total_time_minutes,
            'mastery_average': self.mastery_average
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Curriculum':
        """Create curriculum from dictionary."""
        # Convert datetime strings
        data['created'] = datetime.fromisoformat(data['created'])
        data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        
        # Convert sections
        sections_data = data.pop('sections', [])
        sections = [CurriculumSection.from_dict(s) for s in sections_data]
        
        curriculum = cls(**data, sections=sections)
        return curriculum


class CurriculumManager:
    """Manages curricula for learners."""
    
    def __init__(self, vault_path: Path):
        self.vault_path = Path(vault_path).expanduser()
        self.curricula_path = self.vault_path / ".polly" / "curricula"
        self.curricula_path.mkdir(parents=True, exist_ok=True)
        
        self.curricula: Dict[str, Curriculum] = {}
        self._load_all_curricula()
        
        logger.info(f"CurriculumManager initialized with {len(self.curricula)} curricula")
    
    # ===== CRUD Operations =====
    
    def create_curriculum(
        self, 
        title: str,
        goal: str,
        sections: List[Dict],
        current_level: str = "",
        estimated_duration: str = "",
        template_id: Optional[str] = None,
        **kwargs
    ) -> Curriculum:
        """
        Create new curriculum.
        
        Args:
            title: Curriculum title
            goal: Learning goal
            sections: List of section dictionaries with structure
            current_level: User's starting knowledge level
            estimated_duration: How long curriculum will take
            template_id: ID of template used (if any)
            **kwargs: Additional metadata
        
        Returns:
            Created Curriculum object
        """
        # Generate ID from title
        curriculum_id = self._make_id(title)
        
        # Check if already exists
        if curriculum_id in self.curricula:
            logger.warning(f"Curriculum {curriculum_id} already exists, creating with suffix")
            curriculum_id = f"{curriculum_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create sections
        section_objects = []
        for i, section_data in enumerate(sections):
            section = CurriculumSection(
                id=section_data.get('id', f'section-{i+1}'),
                title=section_data.get('title', f'Section {i+1}'),
                type=section_data.get('type', 'lesson'),
                order=section_data.get('order', i+1),
                parent_id=section_data.get('parent_id'),
                description=section_data.get('description', ''),
                concepts=section_data.get('concepts', []),
                estimated_time=section_data.get('estimated_time', '1-2 hours')
            )
            section_objects.append(section)
        
        # Create curriculum
        curriculum = Curriculum(
            id=curriculum_id,
            title=title,
            goal=goal,
            current_level=current_level,
            estimated_duration=estimated_duration,
            sections=section_objects,
            curriculum_template_id=template_id,
            status="draft"  # Start as draft
        )
        
        # Calculate initial stats
        curriculum.calculate_stats()
        
        # Store
        self.curricula[curriculum_id] = curriculum
        
        # Save to disk
        self.save_curriculum(curriculum)
        
        logger.info(f"Created curriculum: {curriculum_id} with {len(section_objects)} sections")
        return curriculum
    
    def get_curriculum(self, curriculum_id: str) -> Optional[Curriculum]:
        """Get curriculum by ID."""
        return self.curricula.get(curriculum_id)
    
    def list_curricula(self, status: Optional[str] = None) -> List[Curriculum]:
        """
        List all curricula, optionally filtered by status.
        
        Args:
            status: Filter by status ("active", "draft", "completed", "paused")
        
        Returns:
            List of Curriculum objects
        """
        curricula = list(self.curricula.values())
        
        if status:
            curricula = [c for c in curricula if c.status == status]
        
        # Sort by last_updated (most recent first)
        curricula.sort(key=lambda c: c.last_updated, reverse=True)
        
        return curricula
    
    def save_curriculum(self, curriculum: Curriculum):
        """
        Save curriculum to disk.
        
        Saves three files:
        - CURRICULUM.md (human-readable)
        - curriculum.json (machine-readable structure)
        - progress.json (progress tracking)
        """
        curriculum_dir = self.curricula_path / curriculum.id
        curriculum_dir.mkdir(parents=True, exist_ok=True)
        
        # Create resources directory
        resources_dir = curriculum_dir / "resources"
        resources_dir.mkdir(exist_ok=True)
        
        # Save curriculum.json
        curriculum_file = curriculum_dir / "curriculum.json"
        curriculum_data = curriculum.to_dict()
        curriculum_file.write_text(json.dumps(curriculum_data, indent=2))
        
        # Save progress.json (separate for easier updates)
        progress_file = curriculum_dir / "progress.json"
        progress_data = {
            'curriculum_id': curriculum.id,
            'current_section_id': curriculum.current_section_id,
            'completed_sections': curriculum.completed_sections,
            'total_sections': curriculum.total_sections,
            'completion_percentage': curriculum.completion_percentage,
            'total_time_minutes': curriculum.total_time_minutes,
            'mastery_average': curriculum.mastery_average,
            'section_progress': {
                section.id: {
                    'status': section.status,
                    'started_at': section.started_at.isoformat() if section.started_at else None,
                    'completed_at': section.completed_at.isoformat() if section.completed_at else None,
                    'time_spent_minutes': section.time_spent_minutes,
                    'mastery_level': section.mastery_level,
                    'struggles': section.struggles,
                    'breakthroughs': section.breakthroughs
                }
                for section in curriculum.sections
            },
            'last_updated': datetime.now().isoformat()
        }
        progress_file.write_text(json.dumps(progress_data, indent=2))
        
        # Save CURRICULUM.md (human-readable)
        markdown_file = curriculum_dir / "CURRICULUM.md"
        markdown_content = self._generate_markdown(curriculum)
        markdown_file.write_text(markdown_content)
        
        logger.info(f"Saved curriculum: {curriculum.id}")
    
    def delete_curriculum(self, curriculum_id: str):
        """Delete curriculum from memory and disk."""
        if curriculum_id in self.curricula:
            del self.curricula[curriculum_id]
        
        curriculum_dir = self.curricula_path / curriculum_id
        if curriculum_dir.exists():
            import shutil
            shutil.rmtree(curriculum_dir)
        
        logger.info(f"Deleted curriculum: {curriculum_id}")
    
    # ===== Lifecycle Operations =====
    
    def activate_curriculum(self, curriculum_id: str) -> Curriculum:
        """Change status from draft to active."""
        curriculum = self.get_curriculum(curriculum_id)
        if not curriculum:
            raise ValueError(f"Curriculum not found: {curriculum_id}")
        
        curriculum.status = "active"
        curriculum.last_updated = datetime.now()
        self.save_curriculum(curriculum)
        
        logger.info(f"Activated curriculum: {curriculum_id}")
        return curriculum
    
    def pause_curriculum(self, curriculum_id: str):
        """Pause active curriculum."""
        curriculum = self.get_curriculum(curriculum_id)
        if not curriculum:
            raise ValueError(f"Curriculum not found: {curriculum_id}")
        
        curriculum.status = "paused"
        curriculum.last_updated = datetime.now()
        self.save_curriculum(curriculum)
        
        logger.info(f"Paused curriculum: {curriculum_id}")
    
    def complete_curriculum(self, curriculum_id: str):
        """Mark curriculum as completed."""
        curriculum = self.get_curriculum(curriculum_id)
        if not curriculum:
            raise ValueError(f"Curriculum not found: {curriculum_id}")
        
        curriculum.status = "completed"
        curriculum.last_updated = datetime.now()
        self.save_curriculum(curriculum)
        
        logger.info(f"Completed curriculum: {curriculum_id}")
    
    # ===== Section Operations =====
    
    def get_section(self, curriculum_id: str, section_id: str) -> Optional[CurriculumSection]:
        """Get specific section."""
        curriculum = self.get_curriculum(curriculum_id)
        if not curriculum:
            return None
        
        for section in curriculum.sections:
            if section.id == section_id:
                return section
        return None
    
    def get_current_section(self, curriculum_id: str) -> Optional[CurriculumSection]:
        """Get the section currently being worked on."""
        curriculum = self.get_curriculum(curriculum_id)
        if not curriculum or not curriculum.current_section_id:
            return None
        
        return self.get_section(curriculum_id, curriculum.current_section_id)
    
    def get_next_section(self, curriculum_id: str) -> Optional[CurriculumSection]:
        """Get next section after current."""
        curriculum = self.get_curriculum(curriculum_id)
        if not curriculum:
            return None
        
        # Find first not_started or in_progress section
        for section in curriculum.sections:
            if section.status in ['not_started', 'in_progress']:
                return section
        
        return None
    
    def start_section(self, curriculum_id: str, section_id: str) -> CurriculumSection:
        """
        Mark section as started, set as current_section.
        
        Args:
            curriculum_id: Curriculum ID
            section_id: Section ID
        
        Returns:
            Updated section
        """
        curriculum = self.get_curriculum(curriculum_id)
        if not curriculum:
            raise ValueError(f"Curriculum not found: {curriculum_id}")
        
        section = self.get_section(curriculum_id, section_id)
        if not section:
            raise ValueError(f"Section not found: {section_id}")
        
        # Update section
        if section.status == "not_started":
            section.started_at = datetime.now()
        section.status = "in_progress"
        
        # Set as current section
        curriculum.current_section_id = section_id
        curriculum.last_updated = datetime.now()
        
        # Save
        self.save_curriculum(curriculum)
        
        logger.info(f"Started section: {curriculum_id}/{section_id}")
        return section
    
    def complete_section(
        self,
        curriculum_id: str,
        section_id: str,
        mastery_level: int,
        notes: Optional[List[str]] = None,
        struggles: Optional[List[str]] = None,
        breakthroughs: Optional[List[str]] = None
    ):
        """
        Mark section as completed with reflection.
        
        Args:
            curriculum_id: Curriculum ID
            section_id: Section ID
            mastery_level: 1-5 self-reported mastery
            notes: Paths to notes created
            struggles: What was challenging
            breakthroughs: Aha moments
        """
        curriculum = self.get_curriculum(curriculum_id)
        if not curriculum:
            raise ValueError(f"Curriculum not found: {curriculum_id}")
        
        section = self.get_section(curriculum_id, section_id)
        if not section:
            raise ValueError(f"Section not found: {section_id}")
        
        # Calculate time spent (if started_at exists)
        if section.started_at and section.status == "in_progress":
            time_spent = (datetime.now() - section.started_at).seconds // 60
            section.time_spent_minutes += time_spent
        
        # Update section
        section.status = "completed"
        section.completed_at = datetime.now()
        section.mastery_level = mastery_level
        
        if notes:
            section.notes_created.extend(notes)
        if struggles:
            section.struggles.extend(struggles)
        if breakthroughs:
            section.breakthroughs.extend(breakthroughs)
        
        # Recalculate curriculum stats
        curriculum.calculate_stats()
        
        # Save
        self.save_curriculum(curriculum)
        
        logger.info(f"Completed section: {curriculum_id}/{section_id} (mastery: {mastery_level}/5)")
    
    # ===== Enrichment Operations =====
    
    def enrich_section(
        self,
        curriculum_id: str,
        section_id: str,
        enrichment_data: Dict
    ):
        """
        Add detailed content to section (diagrams, exercises, resources).
        
        Args:
            curriculum_id: Curriculum ID
            section_id: Section ID
            enrichment_data: Dictionary with enrichment content
                {
                    'explanation': str,
                    'diagrams': List[Dict],
                    'examples': List[Dict],
                    'exercises': List[Dict],
                    'resources': List[Dict],
                    'assessment_criteria': List[str]
                }
        """
        curriculum = self.get_curriculum(curriculum_id)
        if not curriculum:
            raise ValueError(f"Curriculum not found: {curriculum_id}")
        
        section = self.get_section(curriculum_id, section_id)
        if not section:
            raise ValueError(f"Section not found: {section_id}")
        
        # Update section with enrichment
        section.enriched = True
        section.explanation = enrichment_data.get('explanation', '')
        section.diagrams = enrichment_data.get('diagrams', [])
        section.examples = enrichment_data.get('examples', [])
        section.exercises = enrichment_data.get('exercises', [])
        section.resources = enrichment_data.get('resources', [])
        section.assessment_criteria = enrichment_data.get('assessment_criteria', [])
        
        curriculum.last_updated = datetime.now()
        
        # Save
        self.save_curriculum(curriculum)
        
        logger.info(f"Enriched section: {curriculum_id}/{section_id}")
    
    def is_section_enriched(self, curriculum_id: str, section_id: str) -> bool:
        """Check if section has been enriched."""
        section = self.get_section(curriculum_id, section_id)
        return section.enriched if section else False
    
    # ===== Progress Queries =====
    
    def get_progress_summary(self, curriculum_id: str) -> Dict:
        """Get overall progress statistics."""
        curriculum = self.get_curriculum(curriculum_id)
        if not curriculum:
            return {}
        
        return {
            'curriculum_id': curriculum.id,
            'title': curriculum.title,
            'status': curriculum.status,
            'total_sections': curriculum.total_sections,
            'completed_sections': curriculum.completed_sections,
            'completion_percentage': curriculum.completion_percentage,
            'total_time_minutes': curriculum.total_time_minutes,
            'total_time_hours': curriculum.total_time_minutes / 60,
            'mastery_average': curriculum.mastery_average,
            'current_section_id': curriculum.current_section_id,
            'next_section': self.get_next_section(curriculum_id).id if self.get_next_section(curriculum_id) else None
        }
    
    def get_completion_percentage(self, curriculum_id: str) -> float:
        """Calculate completion percentage."""
        curriculum = self.get_curriculum(curriculum_id)
        if not curriculum:
            return 0.0
        return curriculum.completion_percentage
    
    def get_active_curricula(self) -> List[Curriculum]:
        """Get all active (in-progress) curricula."""
        return self.list_curricula(status="active")
    
    # ===== Helper Methods =====
    
    def _make_id(self, title: str) -> str:
        """Create ID from title."""
        # Convert to lowercase, replace spaces with hyphens, remove special chars
        id_str = title.lower()
        id_str = re.sub(r'[^\w\s-]', '', id_str)
        id_str = re.sub(r'[\s]+', '-', id_str)
        return id_str
    
    def _load_all_curricula(self):
        """Load all curricula from disk."""
        if not self.curricula_path.exists():
            logger.info("No curricula directory found, starting fresh")
            return
        
        for curriculum_dir in self.curricula_path.iterdir():
            if not curriculum_dir.is_dir():
                continue
            
            curriculum_file = curriculum_dir / "curriculum.json"
            if not curriculum_file.exists():
                logger.warning(f"No curriculum.json in {curriculum_dir.name}, skipping")
                continue
            
            try:
                data = json.loads(curriculum_file.read_text())
                curriculum = Curriculum.from_dict(data)
                self.curricula[curriculum.id] = curriculum
                logger.debug(f"Loaded curriculum: {curriculum.id}")
            except Exception as e:
                logger.error(f"Failed to load curriculum from {curriculum_dir.name}: {e}")
        
        logger.info(f"Loaded {len(self.curricula)} curricula")
    
    def _generate_markdown(self, curriculum: Curriculum) -> str:
        """Generate human-readable markdown for curriculum."""
        lines = []
        
        # Header
        lines.append(f"# {curriculum.title}")
        lines.append("")
        lines.append(f"**Status:** {curriculum.status.capitalize()}")
        lines.append(f"**Progress:** {curriculum.completed_sections}/{curriculum.total_sections} sections ({curriculum.completion_percentage:.1f}%)")
        lines.append(f"**Time Spent:** {curriculum.total_time_minutes // 60}h {curriculum.total_time_minutes % 60}m")
        lines.append(f"**Average Mastery:** {curriculum.mastery_average:.1f}/5")
        lines.append("")
        
        # Goal
        if curriculum.goal:
            lines.append("## Goal")
            lines.append(curriculum.goal)
            lines.append("")
        
        # Current Level
        if curriculum.current_level:
            lines.append("## Current Level")
            lines.append(curriculum.current_level)
            lines.append("")
        
        # Duration
        if curriculum.estimated_duration:
            lines.append("## Timeline")
            lines.append(curriculum.estimated_duration)
            lines.append("")
        
        # Sections grouped by parent
        lines.append("## Curriculum Structure")
        lines.append("")
        
        # Group sections by parent_id
        weeks = {}
        for section in curriculum.sections:
            parent = section.parent_id or "other"
            if parent not in weeks:
                weeks[parent] = []
            weeks[parent].append(section)
        
        # Output by week
        for week_id in sorted(weeks.keys()):
            sections = weeks[week_id]
            
            # Week header
            week_title = week_id.replace('-', ' ').title()
            lines.append(f"### {week_title}")
            lines.append("")
            
            for section in sections:
                # Status icon
                icon = {
                    'not_started': '⭕',
                    'in_progress': '⏳',
                    'completed': '✅',
                    'skipped': '⏭️'
                }.get(section.status, '⭕')
                
                # Section line
                mastery_str = f" (Mastery: {section.mastery_level}/5)" if section.mastery_level else ""
                lines.append(f"{icon} **{section.id}**: {section.title}{mastery_str}")
                lines.append(f"   - Estimated time: {section.estimated_time}")
                if section.description:
                    lines.append(f"   - {section.description}")
                if section.time_spent_minutes > 0:
                    hours = section.time_spent_minutes // 60
                    minutes = section.time_spent_minutes % 60
                    lines.append(f"   - Time spent: {hours}h {minutes}m")
                lines.append("")
        
        # Metadata
        lines.append("---")
        lines.append("")
        lines.append(f"*Created: {curriculum.created.strftime('%Y-%m-%d')}*")
        lines.append(f"*Last Updated: {curriculum.last_updated.strftime('%Y-%m-%d %H:%M')}*")
        if curriculum.curriculum_template_id:
            lines.append(f"*Template: {curriculum.curriculum_template_id}*")
        
        return "\n".join(lines)
