"""
Template data model for Polly note templates.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
import re


@dataclass
class Template:
    """
    Represents a note template with metadata and structure.
    
    Templates are markdown files with YAML frontmatter that define:
    - Template metadata (name, icon, description)
    - AI generation hints (tone, focus, linking priority)
    - Smart defaults (domain, folder, tags)
    - Template structure with {{variable}} placeholders
    """
    
    filename: str
    name: str
    icon: str  # Lucide icon name
    description: str
    category: str
    tags: List[str]
    markdown_content: str  # Raw template markdown (without frontmatter)
    frontmatter: Dict[str, Any]  # Full frontmatter as dict
    variables: List[str] = field(default_factory=list)  # Extracted {{variable}} names
    
    def __post_init__(self):
        """Extract variables after initialization."""
        if not self.variables:
            self.variables = self.extract_variables()
    
    def get_ai_hints(self) -> Dict[str, Any]:
        """
        Extract AI generation hints from frontmatter.
        
        Returns:
            Dict with keys: ai_tone, ai_focus, ai_linking_priority
        """
        return {
            'tone': self.frontmatter.get('ai_tone', 'professional'),
            'focus': self.frontmatter.get('ai_focus', 'comprehensive coverage'),
            'linking_priority': self.frontmatter.get('ai_linking_priority', []),
        }
    
    def get_smart_defaults(self) -> Dict[str, Any]:
        """
        Extract smart defaults from frontmatter.
        
        Returns:
            Dict with keys: default_domain, default_folder, default_tags
        """
        return {
            'domain': self.frontmatter.get('default_domain', 'scrolls'),
            'folder': self.frontmatter.get('default_folder', ''),
            'tags': self.frontmatter.get('default_tags', []),
        }
    
    def extract_variables(self) -> List[str]:
        """
        Find all {{variable}} placeholders in markdown content.
        
        Returns:
            List of unique variable names (without braces)
        """
        pattern = r'\{\{(\w+)\}\}'
        matches = re.findall(pattern, self.markdown_content)
        return list(set(matches))  # Remove duplicates
    
    def render(self, values: Dict[str, str]) -> str:
        """
        Render template by replacing {{variables}} with provided values.
        
        Args:
            values: Dict mapping variable names to their values
            
        Returns:
            Rendered markdown with variables replaced
        """
        rendered = self.markdown_content
        
        for var_name, var_value in values.items():
            placeholder = f"{{{{{var_name}}}}}"
            rendered = rendered.replace(placeholder, str(var_value))
        
        return rendered
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert template to dictionary for API responses.
        
        Returns:
            Dict representation suitable for JSON serialization
        """
        return {
            'filename': self.filename,
            'name': self.name,
            'icon': self.icon,
            'description': self.description,
            'category': self.category,
            'tags': self.tags,
            'variables': self.variables,
            'ai_hints': self.get_ai_hints(),
            'smart_defaults': self.get_smart_defaults(),
        }
    
    def to_dict_full(self) -> Dict[str, Any]:
        """
        Convert template to full dictionary including markdown content.
        
        Returns:
            Full dict representation with markdown content
        """
        data = self.to_dict()
        data['markdown_content'] = self.markdown_content
        data['frontmatter'] = self.frontmatter
        return data
