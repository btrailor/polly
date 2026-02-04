"""
Obsidian Template Engine
Templater-compatible template rendering for daily notes and more
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import re
import logging

logger = logging.getLogger(__name__)


class TemplateEngine:
    """
    Template engine compatible with Obsidian Templater plugin syntax.
    
    Supports:
    - Date/time commands: <% tp.date.now() %>
    - Conditional logic: <% if condition %>...<% endif %>
    - Loops: <% for item in items %>...<% endfor %>
    - Variables: <% variable %>
    - Custom functions
    """
    
    def __init__(self, templates_dir: Optional[Path] = None):
        """
        Initialize template engine.
        
        Args:
            templates_dir: Directory containing templates (default: vault/00-System/templates)
        """
        self.templates_dir = templates_dir
        self.functions = self._register_default_functions()
    
    def _register_default_functions(self) -> Dict[str, Any]:
        """Register default Templater-compatible functions."""
        return {
            # Date functions
            'tp.date.now': lambda fmt='YYYY-MM-DD': self._format_date(datetime.now(), fmt),
            'tp.date.today': lambda fmt='YYYY-MM-DD': self._format_date(datetime.now(), fmt),
            'tp.date.tomorrow': lambda fmt='YYYY-MM-DD': self._format_date(
                datetime.now() + timedelta(days=1), fmt
            ),
            'tp.date.yesterday': lambda fmt='YYYY-MM-DD': self._format_date(
                datetime.now() - timedelta(days=1), fmt
            ),
            'tp.date.weekday': lambda: datetime.now().strftime('%A'),
            
            # File functions (simplified for now)
            'tp.file.title': lambda ctx: ctx.get('title', 'Untitled'),
            'tp.file.folder': lambda ctx: ctx.get('folder', ''),
            
            # Custom Polly functions
            'polly.domain': lambda ctx: ctx.get('domain', 'Unknown'),
            'polly.tags': lambda ctx: ', '.join(ctx.get('tags', [])),
        }
    
    def _format_date(self, dt: datetime, fmt: str) -> str:
        """
        Format date using Templater/Moment.js format strings.
        
        Maps Moment.js tokens to Python strftime.
        """
        # Moment.js -> strftime mapping
        replacements = {
            'YYYY': '%Y',
            'YY': '%y',
            'MMMM': '%B',
            'MMM': '%b',
            'MM': '%m',
            'DD': '%d',
            'dddd': '%A',
            'ddd': '%a',
            'HH': '%H',
            'mm': '%M',
            'ss': '%S',
        }
        
        # Replace tokens
        python_fmt = fmt
        for token, strftime_code in replacements.items():
            python_fmt = python_fmt.replace(token, strftime_code)
        
        return dt.strftime(python_fmt)
    
    def load_template(self, template_name: str) -> str:
        """
        Load template from file.
        
        Args:
            template_name: Template name (without .md extension)
            
        Returns:
            Template content
        """
        if not self.templates_dir:
            raise ValueError("No templates directory configured")
        
        template_path = self.templates_dir / f"{template_name}.md"
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        return template_path.read_text(encoding='utf-8')
    
    def render(self, template: str, context: Dict[str, Any]) -> str:
        """
        Render template with context.
        
        Args:
            template: Template string
            context: Variables and data for rendering
            
        Returns:
            Rendered template
        """
        try:
            # Process template commands
            rendered = self._process_commands(template, context)
            
            # Process conditionals
            rendered = self._process_conditionals(rendered, context)
            
            # Process loops
            rendered = self._process_loops(rendered, context)
            
            # Process simple variable substitution
            rendered = self._process_variables(rendered, context)
            
            return rendered
            
        except Exception as e:
            logger.error(f"Error rendering template: {e}")
            return template  # Return original on error
    
    def _process_commands(self, template: str, context: Dict[str, Any]) -> str:
        """
        Process Templater commands like <% tp.date.now() %>.
        """
        # Pattern: <% function() %> or <% function(args) %>
        pattern = r'<%\s*([\w.]+)\s*(?:\((.*?)\))?\s*%>'
        
        def replace_command(match):
            func_name = match.group(1)
            args_str = match.group(2)
            
            # Get function
            func = self.functions.get(func_name)
            if not func:
                logger.warning(f"Unknown function: {func_name}")
                return match.group(0)  # Return original
            
            try:
                # Parse arguments if present
                if args_str:
                    # Simple arg parsing (handles strings and basic types)
                    args = self._parse_args(args_str)
                    # Some functions need context
                    if func_name.startswith('tp.file') or func_name.startswith('polly'):
                        result = func(context)
                    else:
                        result = func(*args)
                else:
                    # No args - check if function needs context
                    if func_name.startswith('tp.file') or func_name.startswith('polly'):
                        result = func(context)
                    else:
                        result = func()
                
                return str(result)
            except Exception as e:
                logger.error(f"Error executing function {func_name}: {e}")
                return match.group(0)  # Return original on error
        
        return re.sub(pattern, replace_command, template)
    
    def _parse_args(self, args_str: str) -> List[Any]:
        """
        Parse function arguments from string.
        
        Handles:
        - Strings: 'value' or "value"
        - Numbers: 42, 3.14
        - Booleans: true, false
        """
        args = []
        
        # Split by comma, respecting quotes
        parts = re.findall(r'''(?:[^,'"]|'[^']*'|"[^"]*")+''', args_str)
        
        for part in parts:
            part = part.strip()
            
            # String
            if part.startswith(("'", '"')) and part.endswith(("'", '"')):
                args.append(part[1:-1])
            # Boolean
            elif part.lower() == 'true':
                args.append(True)
            elif part.lower() == 'false':
                args.append(False)
            # Number
            elif part.replace('.', '').replace('-', '').isdigit():
                args.append(float(part) if '.' in part else int(part))
            # Keep as string
            else:
                args.append(part)
        
        return args
    
    def _process_conditionals(self, template: str, context: Dict[str, Any]) -> str:
        """
        Process conditional blocks: <% if condition %>...<% endif %>.
        """
        # Pattern: <% if var %>content<% endif %>
        pattern = r'<%\s*if\s+(\w+)\s*%>(.*?)<%\s*endif\s*%>'
        
        def replace_conditional(match):
            var_name = match.group(1)
            content = match.group(2)
            
            # Check if variable is truthy
            value = context.get(var_name)
            
            # Handle different truthy checks
            is_truthy = bool(value)
            if isinstance(value, (list, dict, str)):
                is_truthy = len(value) > 0
            
            return content if is_truthy else ''
        
        return re.sub(pattern, replace_conditional, template, flags=re.DOTALL)
    
    def _process_loops(self, template: str, context: Dict[str, Any]) -> str:
        """
        Process loop blocks: <% for item in items %>...<% endfor %>.
        """
        # Pattern: <% for item in collection %>content<% endfor %>
        pattern = r'<%\s*for\s+(\w+)\s+in\s+(\w+)\s*%>(.*?)<%\s*endfor\s*%>'
        
        def replace_loop(match):
            item_name = match.group(1)
            collection_name = match.group(2)
            content = match.group(3)
            
            collection = context.get(collection_name, [])
            if not isinstance(collection, (list, tuple)):
                return ''
            
            # Render content for each item
            results = []
            for item in collection:
                # Create item context
                item_context = context.copy()
                item_context[item_name] = item
                
                # Render item content (replace item variables)
                item_content = content
                # Simple variable substitution for item
                if isinstance(item, dict):
                    for key, value in item.items():
                        item_content = item_content.replace(
                            f'{item_name}.{key}',
                            str(value)
                        )
                else:
                    item_content = item_content.replace(item_name, str(item))
                
                results.append(item_content)
            
            return ''.join(results)
        
        return re.sub(pattern, replace_loop, template, flags=re.DOTALL)
    
    def _process_variables(self, template: str, context: Dict[str, Any]) -> str:
        """
        Process simple variable substitution: {{variable}}.
        
        Note: Using {{ }} for compatibility with Obsidian's internal templates.
        """
        # Pattern: {{variable}} or {{variable.property}}
        pattern = r'\{\{([^}]+)\}\}'
        
        def replace_variable(match):
            var_path = match.group(1).strip()
            
            # Handle nested properties (e.g., event.title)
            parts = var_path.split('.')
            value = context
            
            try:
                for part in parts:
                    if isinstance(value, dict):
                        value = value.get(part)
                    else:
                        value = getattr(value, part, None)
                    
                    if value is None:
                        return ''
                
                return str(value)
            except Exception:
                return ''
        
        return re.sub(pattern, replace_variable, template)


class DailyNoteTemplate:
    """
    Specialized template for daily notes with smart context.
    """
    
    DEFAULT_TEMPLATE = """---
date: <% tp.date.now('YYYY-MM-DD') %>
type: daily
tags: [daily, <% tp.date.now('YYYY') %>, <% tp.date.now('MMMM') %>]
---

# <% tp.date.now('YYYY-MM-DD - dddd') %>

## 📅 Schedule
<% if events %>
<% for event in events %>
- {{event.time}}: {{event.title}}<% if event.location %> ({{event.location}})<% endif %>
<% endfor %>
<% endif %>

## ✅ Tasks
<% if tasks %>
<% for task in tasks %>
- [ ] {{task.title}}<% if task.due %> (due: {{task.due}})<% endif %>
<% endfor %>
<% endif %>

## 🚀 Active Projects
<% if projects %>
<% for project in projects %>
- [[{{project.path}}|{{project.title}}]]
<% endfor %>
<% endif %>

## 📝 Recent Notes
<% if recent_notes %>
<% for note in recent_notes %>
- [[{{note.path}}|{{note.title}}]] ({{note.modified_ago}})
<% endfor %>
<% endif %>

## 💭 Thoughts



## 🔗 References

"""
    
    @classmethod
    def get_default(cls) -> str:
        """Get default daily note template."""
        return cls.DEFAULT_TEMPLATE
