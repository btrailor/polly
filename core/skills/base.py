"""
Skill System Base Classes (Phase 16c Day 4)

Skills are on-demand knowledge packages that personas can load and use.
Examples: template-guide, wiki-linking, domain-structure, coding-standards

Skills are stored as markdown files with YAML frontmatter.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path
import re


@dataclass
class SkillMetadata:
    """
    Metadata for a skill (from YAML frontmatter).

    Attributes:
        name: Skill identifier (e.g., "wiki-linking")
        category: Skill category (e.g., "note-taking", "coding")
        personas: List of persona slugs that use this skill
        version: Skill version
        path: Full path to skill file
        mental_models: Mental model IDs this skill should activate (#25 SKILL↔MM Bridge).
            Example: ["instruments_over_tracks", "collaborative_maps"]
    """
    name: str
    category: str
    personas: List[str]
    version: str
    path: Path
    mental_models: List[str] = field(default_factory=list)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "name": self.name,
            "category": self.category,
            "personas": self.personas,
            "version": self.version,
            "path": str(self.path),
            "mental_models": self.mental_models,
        }


class Skill:
    """
    A skill with full content loaded from markdown file.
    
    Skills are structured markdown documents with YAML frontmatter:
    
    ```
    ---
    name: wiki-linking
    category: note-taking
    personas: [scribe, librarian]
    version: 1.0
    ---
    
    # Wiki-Linking Rules
    
    ## When to Create Links
    ...
    ```
    """
    
    def __init__(self, metadata: SkillMetadata, content: str):
        """
        Initialize skill.
        
        Args:
            metadata: SkillMetadata object
            content: Full markdown content (without frontmatter)
        """
        self.metadata = metadata
        self.content = content
        self._sections = None
    
    def get_section(self, section_name: str) -> Optional[str]:
        """
        Extract a specific section from skill content.
        
        Args:
            section_name: Section heading to extract (e.g., "When to Create Links")
        
        Returns:
            Section content or None if not found
        """
        if self._sections is None:
            self._parse_sections()
        
        return self._sections.get(section_name)
    
    def _parse_sections(self):
        """Parse markdown content into sections"""
        self._sections = {}
        
        # Split by markdown headings
        lines = self.content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            # Check if line is a heading
            heading_match = re.match(r'^#+\s+(.+)$', line)
            
            if heading_match:
                # Save previous section
                if current_section:
                    self._sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = heading_match.group(1).strip()
                current_content = []
            else:
                if current_section:
                    current_content.append(line)
        
        # Save last section
        if current_section:
            self._sections[current_section] = '\n'.join(current_content).strip()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "metadata": self.metadata.to_dict(),
            "content_length": len(self.content),
            "sections": list(self.get_all_sections().keys())
        }
    
    def get_all_sections(self):
        """Get all sections"""
        if self._sections is None:
            self._parse_sections()
        return self._sections
    
    def __repr__(self):
        return f"<Skill {self.metadata.name} ({len(self.content)} chars)>"
