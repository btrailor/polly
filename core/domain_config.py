"""
Domain Configuration System for Polly
Phase 1.5: User-definable domains with migration from hardcoded structure

This module provides:
- DomainConfig: Data model for domain configuration
- load_domains(): Load domains from config with hardcoded fallback
- save_domains(): Atomic save with backups
- migrate_from_hardcoded(): One-time migration from existing structure
"""

import json
import shutil
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
import uuid
import os


@dataclass
class DomainConfig:
    """Configuration for a single domain."""
    id: str
    name: str
    description: str
    color: str
    icon: str
    folder_path: str
    rag_weight: float
    auto_tag_rules: List[str]
    created: str
    modified: str
    order: int
    
    def __post_init__(self):
        """Validate domain config after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """Validate domain configuration."""
        if not 1 <= len(self.name) <= 30:
            raise ValueError(f"Domain name must be 1-30 characters, got: {self.name}")
        
        if len(self.description) > 200:
            raise ValueError(f"Domain description must be <= 200 characters")
        
        if not self.color.startswith('#') or len(self.color) != 7:
            raise ValueError(f"Color must be hex format #RRGGBB, got: {self.color}")
        
        if not 0.0 <= self.rag_weight <= 1.0:
            raise ValueError(f"RAG weight must be 0.0-1.0, got: {self.rag_weight}")
        
        # Validate folder path (no special chars except hyphen/underscore)
        if not self.folder_path.replace('-', '').replace('_', '').replace('/', '').isalnum():
            raise ValueError(f"Invalid folder path: {self.folder_path}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with camelCase keys for JSON."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'icon': self.icon,
            'folderPath': self.folder_path,
            'ragWeight': self.rag_weight,
            'autoTagRules': self.auto_tag_rules,
            'created': self.created,
            'modified': self.modified,
            'order': self.order
        }


@dataclass
class DomainsConfig:
    """Complete domains configuration."""
    version: str
    folder_numbering: bool
    domains: List[DomainConfig]
    last_modified: str
    
    def validate(self) -> None:
        """Validate entire configuration."""
        # Check for duplicate names
        names = [d.name for d in self.domains]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate domain names found")
        
        # Check for duplicate IDs
        ids = [d.id for d in self.domains]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate domain IDs found")
        
        # Check for duplicate folder paths
        folders = [d.folder_path for d in self.domains]
        if len(folders) != len(set(folders)):
            raise ValueError("Duplicate folder paths found")
        
        # Normalize RAG weights to sum to 1.0
        total_weight = sum(d.rag_weight for d in self.domains)
        if total_weight > 0:
            for domain in self.domains:
                domain.rag_weight = domain.rag_weight / total_weight
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'version': self.version,
            'folderNumbering': self.folder_numbering,
            'domains': [d.to_dict() for d in self.domains],
            'lastModified': self.last_modified
        }


# Default path for domains configuration
DOMAINS_CONFIG_PATH = Path.home() / '.polly' / 'domains.json'


def load_domains(config_path: Optional[Path] = None) -> DomainsConfig:
    """
    Load domains from configuration file.
    
    Falls back to hardcoded domains if config doesn't exist.
    
    Args:
        config_path: Path to domains.json (defaults to ~/.polly/domains.json)
    
    Returns:
        DomainsConfig with loaded or default domains
    """
    if config_path is None:
        config_path = DOMAINS_CONFIG_PATH
    
    # If config exists, load it
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
            
            # Parse domains
            domains = []
            for d in data.get('domains', []):
                domains.append(DomainConfig(
                    id=d['id'],
                    name=d['name'],
                    description=d['description'],
                    color=d['color'],
                    icon=d['icon'],
                    folder_path=d['folderPath'],
                    rag_weight=d['ragWeight'],
                    auto_tag_rules=d['autoTagRules'],
                    created=d['created'],
                    modified=d['modified'],
                    order=d['order']
                ))
            
            config = DomainsConfig(
                version=data.get('version', '1.0'),
                folder_numbering=data.get('folderNumbering', True),
                domains=domains,
                last_modified=data.get('lastModified', datetime.now().isoformat())
            )
            
            config.validate()
            return config
            
        except Exception as e:
            print(f"Warning: Failed to load domains config: {e}")
            print("Falling back to hardcoded domains")
    
    # Fallback: create from hardcoded domains
    return _create_default_domains()


def save_domains(config: DomainsConfig, config_path: Optional[Path] = None, create_backup: bool = True) -> None:
    """
    Save domains configuration atomically with backup.
    
    Args:
        config: DomainsConfig to save
        config_path: Path to save to (defaults to ~/.polly/domains.json)
        create_backup: Whether to create backup of existing config
    """
    if config_path is None:
        config_path = DOMAINS_CONFIG_PATH
    
    # Validate before saving
    config.validate()
    
    # Update last modified timestamp
    config.last_modified = datetime.now().isoformat()
    
    # Ensure directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create backup if config exists
    if create_backup and config_path.exists():
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = config_path.parent / f"domains.backup.{timestamp}.json"
        shutil.copy2(config_path, backup_path)
        print(f"Created backup: {backup_path}")
    
    # Write to temporary file first (atomic operation)
    temp_path = config_path.parent / f"domains.json.tmp.{os.getpid()}"
    try:
        with open(temp_path, 'w') as f:
            json.dump(config.to_dict(), f, indent=2)
        
        # Atomic rename
        temp_path.replace(config_path)
        print(f"Saved domains config to {config_path}")
        
    except Exception as e:
        # Clean up temp file on error
        if temp_path.exists():
            temp_path.unlink()
        raise e


def _create_default_domains() -> DomainsConfig:
    """
    Create default domains from hardcoded structure.
    
    This is the migration path from the old hardcoded system.
    """
    now = datetime.now().isoformat()
    
    domains = [
        DomainConfig(
            id='sigils',
            name='Sigils',
            description='Code, infrastructure, automation, security',
            color='#61afef',
            icon='⚡',
            folder_path='01-Sigils',
            rag_weight=0.20,
            auto_tag_rules=[
                'code', 'docker', 'kubernetes', 'api', 'server', 'database',
                'python', 'rust', 'javascript', 'typescript', 'react', 'vue',
                'node', 'npm', 'cargo', 'pip', 'function', 'class',
                'redis', 'postgres', 'mongodb', 'git', 'github',
                'testing', 'debug', 'refactor', 'deploy', 'automation',
                'infrastructure', 'ci/cd', 'devops'
            ],
            created=now,
            modified=now,
            order=1
        ),
        DomainConfig(
            id='signals',
            name='Signals',
            description='Audio programming, synthesis, DSP, music technology',
            color='#c678dd',
            icon='📡',
            folder_path='02-Signals',
            rag_weight=0.20,
            auto_tag_rules=[
                'audio', 'sound', 'music', 'midi', 'supercollider', 'norns', 'monome',
                'synthesis', 'synth', 'oscillator', 'filter', 'envelope', 'sample',
                'sequencer', 'grid', 'arc', 'crow', 'modular', 'eurorack', 'dsp',
                'instrument', 'composition', 'generative', 'voltage', 'cv', 'gate', 'trigger'
            ],
            created=now,
            modified=now,
            order=2
        ),
        DomainConfig(
            id='scrolls',
            name='Scrolls',
            description='Writing, pedagogy, documentation, essays',
            color='#98c379',
            icon='📜',
            folder_path='03-Scrolls',
            rag_weight=0.20,
            auto_tag_rules=[
                'writing', 'essay', 'article', 'note', 'document', 'text', 'prose',
                'pedagogy', 'teaching', 'learning', 'education', 'curriculum',
                'knowledge', 'research', 'study', 'book', 'paper', 'thesis',
                'freire', 'popular education', 'documentation', 'guide', 'tutorial',
                'journal', 'notes'
            ],
            created=now,
            modified=now,
            order=3
        ),
        DomainConfig(
            id='glyphs',
            name='Glyphs',
            description='Visual work, design, UI/UX',
            color='#e5c07b',
            icon='✨',
            folder_path='04-Glyphs',
            rag_weight=0.20,
            auto_tag_rules=[
                'design', 'visual', 'ui', 'ux', 'interface', 'layout', 'typography',
                'color', 'aesthetic', 'style', 'graphic', 'icon', 'logo', 'brand',
                'canvas', 'draw', 'render', 'display', 'screen', 'pixel',
                'figma', 'sketch', 'wireframe', 'mockup', 'prototype'
            ],
            created=now,
            modified=now,
            order=4
        ),
        DomainConfig(
            id='grids',
            name='Grids',
            description='Systems thinking, mental models, frameworks',
            color='#e06c75',
            icon='🗂️',
            folder_path='05-Grids',
            rag_weight=0.20,
            auto_tag_rules=[
                'system', 'framework', 'model', 'architecture', 'structure', 'pattern',
                'organization', 'workflow', 'process', 'method', 'approach', 'strategy',
                'meta', 'theory', 'principle', 'concept', 'thinking', 'mental',
                'infinite game', 'finite game', 'constraint', 'emergence', 'complexity',
                'feedback', 'polymathic', 'cross-domain', 'synthesis', 'archetype',
                'metalearning', 'paradigm', 'worldview', 'philosophy', 'systems thinking'
            ],
            created=now,
            modified=now,
            order=5
        )
    ]
    
    return DomainsConfig(
        version='1.0',
        folder_numbering=True,
        domains=domains,
        last_modified=now
    )


def migrate_from_hardcoded(config_path: Optional[Path] = None, force: bool = False) -> DomainsConfig:
    """
    Migrate from hardcoded domains to domains.json.
    
    This is safe to run multiple times - it will only create the config
    if it doesn't already exist (unless force=True).
    
    Args:
        config_path: Path to save domains.json
        force: If True, overwrite existing config
    
    Returns:
        DomainsConfig that was created/loaded
    """
    if config_path is None:
        config_path = DOMAINS_CONFIG_PATH
    
    # Don't overwrite existing config unless forced
    if config_path.exists() and not force:
        print(f"Config already exists at {config_path}")
        return load_domains(config_path)
    
    print("Migrating from hardcoded domains to domains.json...")
    
    # Create default domains from hardcoded structure
    config = _create_default_domains()
    
    # Save to file
    save_domains(config, config_path, create_backup=False)
    
    print(f"✓ Migration complete: Created {len(config.domains)} domains")
    for domain in config.domains:
        print(f"  - {domain.icon} {domain.name}: {domain.description}")
    
    return config


def get_domain_by_id(config: DomainsConfig, domain_id: str) -> Optional[DomainConfig]:
    """Get domain by ID."""
    for domain in config.domains:
        if domain.id == domain_id:
            return domain
    return None


def get_domain_by_name(config: DomainsConfig, name: str) -> Optional[DomainConfig]:
    """Get domain by name."""
    for domain in config.domains:
        if domain.name.lower() == name.lower():
            return domain
    return None


def normalize_rag_weights(config: DomainsConfig) -> None:
    """Normalize RAG weights to sum to 1.0."""
    total = sum(d.rag_weight for d in config.domains)
    if total > 0:
        for domain in config.domains:
            domain.rag_weight = domain.rag_weight / total


def generate_folder_path(domain_name: str, order: int, use_numbering: bool) -> str:
    """
    Generate folder path from domain name.
    
    Args:
        domain_name: Name of the domain
        order: Sort order (1-indexed)
        use_numbering: Whether to add numeric prefix
    
    Returns:
        Folder path string
    """
    # Sanitize name: remove special chars, replace spaces with hyphens
    import re
    safe_name = re.sub(r'[^\w\s-]', '', domain_name)
    safe_name = re.sub(r'[\s]+', '-', safe_name)
    
    if use_numbering:
        return f"{order:02d}-{safe_name}"
    else:
        return safe_name


def is_first_run(config_path: Optional[Path] = None) -> bool:
    """
    Check if this is a first-run (no domains.json exists).
    
    Args:
        config_path: Path to domains.json (defaults to ~/.polly/domains.json)
    
    Returns:
        True if domains.json doesn't exist, False otherwise
    """
    if config_path is None:
        config_path = DOMAINS_CONFIG_PATH
    return not config_path.exists()


def create_quick_start_domains() -> DomainsConfig:
    """
    Create a minimal quick-start set of 3 domains: Work, Personal, Learning.
    
    This is intended for the first-run wizard to get users started quickly
    without overwhelming them with domain configuration.
    
    Returns:
        DomainsConfig with 3 basic domains
    """
    now = datetime.now().isoformat()
    
    domains = [
        DomainConfig(
            id='work',
            name='Work',
            description='Work projects, meetings, and professional tasks',
            color='#61afef',  # Blue
            icon='💼',
            folder_path='01-Work',
            rag_weight=0.33,
            auto_tag_rules=[
                'project', 'meeting', 'task', 'deadline', 'client',
                'email', 'calendar', 'document', 'presentation',
                'work', 'professional', 'business', 'office'
            ],
            created=now,
            modified=now,
            order=1
        ),
        DomainConfig(
            id='personal',
            name='Personal',
            description='Personal notes, hobbies, and life organization',
            color='#98c379',  # Green
            icon='🏠',
            folder_path='02-Personal',
            rag_weight=0.33,
            auto_tag_rules=[
                'personal', 'life', 'home', 'family', 'hobby',
                'health', 'finance', 'travel', 'shopping',
                'recipe', 'journal', 'diary', 'todo', 'list'
            ],
            created=now,
            modified=now,
            order=2
        ),
        DomainConfig(
            id='learning',
            name='Learning',
            description='Study notes, courses, research, and skills development',
            color='#c678dd',  # Purple
            icon='📚',
            folder_path='03-Learning',
            rag_weight=0.34,
            auto_tag_rules=[
                'learning', 'study', 'course', 'tutorial', 'research',
                'book', 'paper', 'article', 'notes', 'education',
                'skill', 'training', 'knowledge', 'academy'
            ],
            created=now,
            modified=now,
            order=3
        )
    ]
    
    config = DomainsConfig(
        version='1.0',
        folder_numbering=True,
        domains=domains,
        last_modified=now
    )
    
    config.validate()
    return config


# Convenience function for quick migration
def ensure_domains_exist() -> DomainsConfig:
    """
    Ensure domains.json exists, creating it if necessary.
    
    This is the main entry point for the migration system.
    Call this on app startup to ensure config exists.
    """
    return migrate_from_hardcoded()


if __name__ == '__main__':
    # Test migration
    print("Testing domain config system...")
    config = migrate_from_hardcoded(force=True)
    print(f"\nCreated config with {len(config.domains)} domains")
    print(f"Total RAG weight: {sum(d.rag_weight for d in config.domains):.2f}")
