"""
Skill Manager (Phase 16c Day 4-5)

Manages skill discovery, loading, and caching.
"""

from typing import Dict, List, Optional
from pathlib import Path
import logging
import yaml

from .base import Skill, SkillMetadata

logger = logging.getLogger(__name__)


class SkillManager:
    """
    Manager for skill discovery and loading.
    
    Usage:
        manager = SkillManager()
        
        # Discover all skills
        skills = manager.discover_skills()
        
        # Load specific skill
        skill = manager.load_skill("wiki-linking")
        
        # Get skills for persona
        scribe_skills = manager.get_skills_for_persona("scribe")
    """
    
    def __init__(self, skills_dir: Optional[str] = None):
        """
        Initialize skill manager.
        
        Args:
            skills_dir: Directory containing skills (defaults to vault/.polly/skills/)
        """
        if skills_dir is None:
            # Default to vault/.polly/skills/
            # Adjust path to find vault from core/skills/
            project_root = Path(__file__).parent.parent.parent
            skills_dir = project_root / "vault" / ".polly" / "skills"
        
        self.skills_dir = Path(skills_dir)
        
        # Cache for loaded skills
        self.skill_cache: Dict[str, Skill] = {}
        
        # Metadata cache (loaded on init)
        self.metadata_cache: Dict[str, SkillMetadata] = {}
        
        # Discover skills
        self._discover_skills()
        
        logger.info(
            f"SkillManager initialized with {len(self.metadata_cache)} skills from {self.skills_dir}"
        )
    
    def _discover_skills(self):
        """
        Discover all skills in skills directory.
        
        Scans for SKILL.md files and loads their metadata.
        """
        logger.info(f"Discovering skills in {self.skills_dir}")
        
        # Create skills directory if it doesn't exist
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all SKILL.md files
        skill_files = list(self.skills_dir.glob("*/SKILL.md"))
        
        if not skill_files:
            logger.warning(f"No skills found in {self.skills_dir}")
            return
        
        # Load metadata from each file
        for skill_file in skill_files:
            try:
                metadata = self._load_skill_metadata(skill_file)
                self.metadata_cache[metadata.name] = metadata
                
                logger.info(
                    f"Discovered skill: {metadata.name} "
                    f"(category: {metadata.category}, "
                    f"personas: {', '.join(metadata.personas)})"
                )
                
            except Exception as e:
                logger.warning(f"Failed to load skill metadata from {skill_file}: {e}")
        
        logger.info(f"Discovered {len(self.metadata_cache)} skills")
    
    def _load_skill_metadata(self, skill_file: Path) -> SkillMetadata:
        """
        Load metadata from a skill file's YAML frontmatter.
        
        Args:
            skill_file: Path to SKILL.md file
        
        Returns:
            SkillMetadata object
        """
        with open(skill_file, 'r') as f:
            content = f.read()
        
        # Extract YAML frontmatter
        if not content.startswith('---'):
            raise ValueError(f"Skill file {skill_file} missing YAML frontmatter")
        
        # Find end of frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            raise ValueError(f"Invalid frontmatter in {skill_file}")
        
        frontmatter_str = parts[1]
        
        # Parse YAML
        try:
            frontmatter = yaml.safe_load(frontmatter_str)
        except Exception as e:
            raise ValueError(f"Invalid YAML in {skill_file}: {e}")
        
        # Parse mental_models field — may be a string or list (#25 SKILL↔MM Bridge)
        raw_mm = frontmatter.get('mental_models', [])
        if isinstance(raw_mm, str):
            raw_mm = [raw_mm]

        # Create metadata
        metadata = SkillMetadata(
            name=frontmatter.get('name', skill_file.parent.name),
            category=frontmatter.get('category', 'general'),
            personas=frontmatter.get('personas', []),
            version=frontmatter.get('version', '1.0'),
            path=skill_file,
            mental_models=raw_mm,
        )

        return metadata
    
    def load_skill(self, name: str) -> Optional[Skill]:
        """
        Load a skill by name (with caching).
        
        Args:
            name: Skill name
        
        Returns:
            Skill object or None if not found
        """
        # Check cache first
        if name in self.skill_cache:
            logger.debug(f"Using cached skill: {name}")
            return self.skill_cache[name]
        
        # Check if skill exists
        if name not in self.metadata_cache:
            logger.warning(f"Skill not found: {name}")
            return None
        
        metadata = self.metadata_cache[name]
        
        logger.info(f"Loading skill: {name}")
        
        # Load full content
        try:
            with open(metadata.path, 'r') as f:
                content = f.read()
            
            # Remove frontmatter
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2].strip()
            
            # Create skill
            skill = Skill(metadata=metadata, content=content)
            
            # Cache it
            self.skill_cache[name] = skill
            
            logger.info(f"Loaded skill: {name} ({len(content)} chars)")
            
            return skill
            
        except Exception as e:
            logger.error(f"Failed to load skill {name}: {e}")
            return None
    
    def get_skills_for_persona(self, persona_slug: str) -> List[SkillMetadata]:
        """
        Get all skills for a specific persona (metadata only).
        
        Args:
            persona_slug: Persona slug (e.g., "scribe")
        
        Returns:
            List of SkillMetadata objects
        """
        skills = []
        
        for metadata in self.metadata_cache.values():
            if persona_slug in metadata.personas:
                skills.append(metadata)
        
        return skills
    
    def list_all_skills(self) -> List[SkillMetadata]:
        """Get all available skills (metadata only)"""
        return list(self.metadata_cache.values())
    
    def reload_skills(self):
        """Reload all skills from disk (useful for development)"""
        logger.info("Reloading skills from disk")
        self.metadata_cache.clear()
        self.skill_cache.clear()
        self._discover_skills()
    
    def clear_cache(self):
        """Clear skill cache (metadata persists)"""
        self.skill_cache.clear()
        logger.info("Cleared skill cache")
    
    def __repr__(self):
        return (
            f"<SkillManager {len(self.metadata_cache)} skills, "
            f"{len(self.skill_cache)} cached>"
        )
