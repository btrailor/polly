"""
Template manager for loading and managing note templates.
"""

from pathlib import Path
from typing import Dict, List, Optional
import yaml
import re
import logging

from .template import Template

logger = logging.getLogger(__name__)


class TemplateManager:
    """
    Manages loading and accessing note templates from the vault.
    
    Templates are markdown files with YAML frontmatter stored in
    the .polly/templates/ directory within the vault.
    """
    
    def __init__(self, templates_dir: Path):
        """
        Initialize template manager.
        
        Args:
            templates_dir: Path to templates directory (e.g., vault/.polly/templates/)
        """
        self.templates_dir = Path(templates_dir)
        self.templates: Dict[str, Template] = {}
        
        # Load all templates on initialization
        self._load_all_templates()
    
    def _load_all_templates(self) -> None:
        """
        Scan templates directory for .md files and load them.
        """
        if not self.templates_dir.exists():
            logger.warning(f"Templates directory does not exist: {self.templates_dir}")
            logger.info(f"Creating templates directory: {self.templates_dir}")
            self.templates_dir.mkdir(parents=True, exist_ok=True)
            return
        
        # Find all .md files in templates directory
        template_files = list(self.templates_dir.glob('*.md'))
        
        logger.info(f"Found {len(template_files)} template files in {self.templates_dir}")
        
        for template_file in template_files:
            try:
                template = self._load_template_file(template_file)
                if template:
                    self.templates[template.filename] = template
                    logger.info(f"Loaded template: {template.name} ({template.filename})")
            except Exception as e:
                logger.error(f"Error loading template {template_file.name}: {e}")
    
    def _load_template_file(self, filepath: Path) -> Optional[Template]:
        """
        Load a single template file.
        
        Args:
            filepath: Path to template markdown file
            
        Returns:
            Template object or None if invalid
        """
        try:
            content = filepath.read_text(encoding='utf-8')
            
            # Split frontmatter and markdown content
            frontmatter, markdown = self._parse_markdown_with_frontmatter(content)
            
            if not frontmatter:
                logger.warning(f"Template {filepath.name} missing frontmatter")
                return None
            
            # Validate required fields
            required_fields = ['template_name', 'template_icon', 'template_description']
            for field in required_fields:
                if field not in frontmatter:
                    logger.error(f"Template {filepath.name} missing required field: {field}")
                    return None
            
            # Create Template object
            template = Template(
                filename=filepath.name,
                name=frontmatter['template_name'],
                icon=frontmatter['template_icon'],
                description=frontmatter['template_description'],
                category=frontmatter.get('template_category', 'general'),
                tags=frontmatter.get('template_tags', []),
                markdown_content=markdown,
                frontmatter=frontmatter,
            )
            
            return template
            
        except Exception as e:
            logger.error(f"Error parsing template file {filepath.name}: {e}")
            return None
    
    def _parse_markdown_with_frontmatter(self, content: str) -> tuple[Dict, str]:
        """
        Parse markdown file with YAML frontmatter.
        
        Args:
            content: Raw file content
            
        Returns:
            Tuple of (frontmatter_dict, markdown_content)
        """
        # Match YAML frontmatter between --- delimiters
        pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
        match = re.match(pattern, content, re.DOTALL)
        
        if not match:
            # No frontmatter found
            return {}, content
        
        yaml_content = match.group(1)
        markdown_content = match.group(2).strip()
        
        try:
            frontmatter = yaml.safe_load(yaml_content)
            return frontmatter or {}, markdown_content
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML frontmatter: {e}")
            return {}, markdown_content
    
    def load_template(self, filename: str) -> Optional[Template]:
        """
        Load a specific template by filename.
        
        Args:
            filename: Template filename (e.g., 'meeting-notes.md')
            
        Returns:
            Template object or None if not found
        """
        if filename in self.templates:
            return self.templates[filename]
        
        # Try loading from file if not in cache
        template_path = self.templates_dir / filename
        if template_path.exists():
            template = self._load_template_file(template_path)
            if template:
                self.templates[filename] = template
            return template
        
        logger.warning(f"Template not found: {filename}")
        return None
    
    def get_all_templates(self) -> List[Template]:
        """
        Get all loaded templates.
        
        Returns:
            List of Template objects
        """
        return list(self.templates.values())
    
    def get_gallery_metadata(self) -> List[Dict]:
        """
        Get template metadata for gallery UI.
        
        Returns:
            List of dicts with template metadata (no full content)
        """
        return [template.to_dict() for template in self.templates.values()]
    
    def validate_template(self, template: Template) -> bool:
        """
        Validate template structure and required fields.
        
        Args:
            template: Template to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        if not template.name or not template.icon or not template.description:
            logger.error(f"Template {template.filename} missing required metadata")
            return False
        
        # Check markdown content exists
        if not template.markdown_content:
            logger.error(f"Template {template.filename} has no content")
            return False
        
        # Check variables can be extracted
        if not template.variables:
            logger.warning(f"Template {template.filename} has no variables")
        
        return True
    
    def reload_templates(self) -> None:
        """
        Reload all templates from disk.
        """
        logger.info("Reloading templates...")
        self.templates.clear()
        self._load_all_templates()
        logger.info(f"Reloaded {len(self.templates)} templates")
