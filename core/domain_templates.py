"""
Domain Templates for Polly
Phase 1.5 Day 6: First-run wizard templates

This module provides pre-configured domain templates for common use cases:
- Software Development: For developers and engineers
- Academic Research: For researchers and students
- Creative Work: For artists, writers, and designers
- Business: For entrepreneurs and business professionals

Templates help users get started quickly without having to configure domains manually.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Callable

# Add parent directory to path for imports when run as script
if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).parent.parent))

from core.domain_config import DomainConfig, DomainsConfig


def create_software_development_template() -> DomainsConfig:
    """
    Software Development template.
    
    Domains:
    - Code: Active projects and code
    - Infrastructure: DevOps, deployment, monitoring
    - Learning: Tutorials, documentation, courses
    - Archive: Completed projects and legacy code
    - Ideas: Brainstorming and future projects
    
    Returns:
        DomainsConfig with 5 software development domains
    """
    now = datetime.now().isoformat()
    
    domains = [
        DomainConfig(
            id='code',
            name='Code',
            description='Active projects, repositories, and code',
            color='#61afef',  # Blue
            icon='💻',
            folder_path='01-Code',
            rag_weight=0.30,
            auto_tag_rules=[
                'code', 'project', 'repository', 'repo', 'git', 'github',
                'python', 'rust', 'javascript', 'typescript', 'java', 'go',
                'function', 'class', 'method', 'api', 'endpoint',
                'bug', 'feature', 'refactor', 'test', 'debug',
                'algorithm', 'data structure', 'pattern', 'architecture'
            ],
            created=now,
            modified=now,
            order=1
        ),
        DomainConfig(
            id='infrastructure',
            name='Infrastructure',
            description='DevOps, deployment, CI/CD, monitoring',
            color='#e5c07b',  # Yellow
            icon='🏗️',
            folder_path='02-Infrastructure',
            rag_weight=0.20,
            auto_tag_rules=[
                'docker', 'kubernetes', 'k8s', 'deploy', 'deployment',
                'ci/cd', 'pipeline', 'jenkins', 'github actions',
                'server', 'cloud', 'aws', 'azure', 'gcp',
                'monitoring', 'logging', 'metrics', 'alerting',
                'nginx', 'apache', 'load balancer', 'cdn',
                'database', 'postgres', 'redis', 'mongodb',
                'infrastructure', 'terraform', 'ansible', 'devops'
            ],
            created=now,
            modified=now,
            order=2
        ),
        DomainConfig(
            id='learning-dev',
            name='Learning',
            description='Tutorials, documentation, courses, books',
            color='#c678dd',  # Purple
            icon='📚',
            folder_path='03-Learning',
            rag_weight=0.20,
            auto_tag_rules=[
                'tutorial', 'documentation', 'docs', 'guide', 'course',
                'learning', 'study', 'book', 'article', 'paper',
                'example', 'sample', 'demo', 'playground',
                'notes', 'reference', 'cheatsheet', 'snippet'
            ],
            created=now,
            modified=now,
            order=3
        ),
        DomainConfig(
            id='archive-dev',
            name='Archive',
            description='Completed projects and legacy code',
            color='#5c6370',  # Gray
            icon='📦',
            folder_path='04-Archive',
            rag_weight=0.10,
            auto_tag_rules=[
                'archive', 'completed', 'finished', 'legacy', 'old',
                'deprecated', 'retired', 'historical', 'past'
            ],
            created=now,
            modified=now,
            order=4
        ),
        DomainConfig(
            id='ideas-dev',
            name='Ideas',
            description='Brainstorming, future projects, experiments',
            color='#98c379',  # Green
            icon='💡',
            folder_path='05-Ideas',
            rag_weight=0.20,
            auto_tag_rules=[
                'idea', 'brainstorm', 'future', 'experiment', 'prototype',
                'concept', 'sketch', 'draft', 'proposal', 'plan',
                'todo', 'backlog', 'wishlist', 'someday'
            ],
            created=now,
            modified=now,
            order=5
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


def create_research_template() -> DomainsConfig:
    """
    Academic Research template.
    
    Domains:
    - Research: Active research projects
    - Literature: Papers, books, references
    - Data: Datasets, experiments, analysis
    - Writing: Papers, theses, presentations
    - Teaching: Courses, lectures, materials
    
    Returns:
        DomainsConfig with 5 academic research domains
    """
    now = datetime.now().isoformat()
    
    domains = [
        DomainConfig(
            id='research',
            name='Research',
            description='Active research projects and experiments',
            color='#61afef',  # Blue
            icon='🔬',
            folder_path='01-Research',
            rag_weight=0.30,
            auto_tag_rules=[
                'research', 'project', 'experiment', 'study', 'investigation',
                'hypothesis', 'method', 'methodology', 'analysis',
                'finding', 'result', 'conclusion', 'discussion',
                'lab', 'field work', 'survey', 'interview'
            ],
            created=now,
            modified=now,
            order=1
        ),
        DomainConfig(
            id='literature',
            name='Literature',
            description='Papers, books, articles, and references',
            color='#c678dd',  # Purple
            icon='📖',
            folder_path='02-Literature',
            rag_weight=0.25,
            auto_tag_rules=[
                'paper', 'article', 'book', 'journal', 'publication',
                'literature', 'review', 'reference', 'citation',
                'author', 'scholar', 'academic', 'peer review',
                'doi', 'arxiv', 'pubmed', 'bibliography'
            ],
            created=now,
            modified=now,
            order=2
        ),
        DomainConfig(
            id='data',
            name='Data',
            description='Datasets, experiments, and analysis',
            color='#e5c07b',  # Yellow
            icon='📊',
            folder_path='03-Data',
            rag_weight=0.20,
            auto_tag_rules=[
                'data', 'dataset', 'analysis', 'statistics', 'stats',
                'visualization', 'graph', 'chart', 'plot',
                'csv', 'excel', 'spreadsheet', 'table',
                'r', 'python', 'jupyter', 'notebook',
                'pandas', 'numpy', 'matplotlib', 'seaborn'
            ],
            created=now,
            modified=now,
            order=3
        ),
        DomainConfig(
            id='writing',
            name='Writing',
            description='Papers, theses, presentations, grants',
            color='#98c379',  # Green
            icon='✍️',
            folder_path='04-Writing',
            rag_weight=0.15,
            auto_tag_rules=[
                'writing', 'paper', 'thesis', 'dissertation', 'manuscript',
                'draft', 'revision', 'feedback', 'edit',
                'presentation', 'poster', 'slide', 'talk',
                'grant', 'proposal', 'abstract', 'outline',
                'latex', 'overleaf', 'word', 'markdown'
            ],
            created=now,
            modified=now,
            order=4
        ),
        DomainConfig(
            id='teaching',
            name='Teaching',
            description='Courses, lectures, and teaching materials',
            color='#e06c75',  # Red
            icon='👨‍🏫',
            folder_path='05-Teaching',
            rag_weight=0.10,
            auto_tag_rules=[
                'teaching', 'course', 'lecture', 'class', 'lesson',
                'syllabus', 'assignment', 'homework', 'exam', 'quiz',
                'student', 'grade', 'feedback', 'office hours',
                'pedagogy', 'curriculum', 'education', 'learning'
            ],
            created=now,
            modified=now,
            order=5
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


def create_creative_work_template() -> DomainsConfig:
    """
    Creative Work template.
    
    Domains:
    - Active Projects: Current creative work
    - Writing: Essays, stories, scripts
    - Visual: Design, art, graphics
    - Audio: Music, sound, podcasts
    - Archive: Completed works
    
    Returns:
        DomainsConfig with 5 creative work domains
    """
    now = datetime.now().isoformat()
    
    domains = [
        DomainConfig(
            id='active-projects',
            name='Active Projects',
            description='Current creative projects and works-in-progress',
            color='#e06c75',  # Red
            icon='🎨',
            folder_path='01-Active-Projects',
            rag_weight=0.30,
            auto_tag_rules=[
                'project', 'active', 'wip', 'work in progress',
                'current', 'draft', 'sketch', 'prototype',
                'creative', 'art', 'work', 'piece'
            ],
            created=now,
            modified=now,
            order=1
        ),
        DomainConfig(
            id='writing',
            name='Writing',
            description='Essays, stories, scripts, and prose',
            color='#98c379',  # Green
            icon='📝',
            folder_path='02-Writing',
            rag_weight=0.25,
            auto_tag_rules=[
                'writing', 'essay', 'story', 'script', 'prose', 'poetry',
                'article', 'blog', 'journal', 'diary', 'note',
                'character', 'plot', 'narrative', 'dialogue',
                'fiction', 'nonfiction', 'creative writing'
            ],
            created=now,
            modified=now,
            order=2
        ),
        DomainConfig(
            id='visual',
            name='Visual',
            description='Design, art, graphics, and visual work',
            color='#e5c07b',  # Yellow
            icon='🖼️',
            folder_path='03-Visual',
            rag_weight=0.20,
            auto_tag_rules=[
                'design', 'art', 'visual', 'graphic', 'illustration',
                'drawing', 'painting', 'sketch', 'render',
                'photography', 'photo', 'image', 'picture',
                'ui', 'ux', 'interface', 'layout', 'composition',
                'color', 'typography', 'style', 'aesthetic',
                'photoshop', 'illustrator', 'figma', 'sketch'
            ],
            created=now,
            modified=now,
            order=3
        ),
        DomainConfig(
            id='audio',
            name='Audio',
            description='Music, sound design, podcasts, audio work',
            color='#c678dd',  # Purple
            icon='🎵',
            folder_path='04-Audio',
            rag_weight=0.15,
            auto_tag_rules=[
                'audio', 'music', 'sound', 'song', 'track',
                'composition', 'arrangement', 'mix', 'master',
                'podcast', 'episode', 'recording', 'voice',
                'instrument', 'synth', 'sample', 'loop',
                'daw', 'ableton', 'logic', 'protools', 'reaper',
                'midi', 'synthesis', 'effect', 'plugin'
            ],
            created=now,
            modified=now,
            order=4
        ),
        DomainConfig(
            id='archive-creative',
            name='Archive',
            description='Completed works and portfolio pieces',
            color='#5c6370',  # Gray
            icon='📚',
            folder_path='05-Archive',
            rag_weight=0.10,
            auto_tag_rules=[
                'archive', 'completed', 'finished', 'done',
                'portfolio', 'published', 'released',
                'historical', 'past', 'old'
            ],
            created=now,
            modified=now,
            order=5
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


def create_business_template() -> DomainsConfig:
    """
    Business template.
    
    Domains:
    - Operations: Day-to-day business operations
    - Strategy: Planning, goals, vision
    - Clients: Client work and communications
    - Finance: Accounting, budgets, invoices
    - Marketing: Content, campaigns, outreach
    
    Returns:
        DomainsConfig with 5 business domains
    """
    now = datetime.now().isoformat()
    
    domains = [
        DomainConfig(
            id='operations',
            name='Operations',
            description='Day-to-day business operations and tasks',
            color='#61afef',  # Blue
            icon='⚙️',
            folder_path='01-Operations',
            rag_weight=0.30,
            auto_tag_rules=[
                'operations', 'ops', 'daily', 'task', 'workflow',
                'process', 'procedure', 'system', 'sop',
                'meeting', 'agenda', 'minutes', 'action item',
                'team', 'collaboration', 'project', 'milestone'
            ],
            created=now,
            modified=now,
            order=1
        ),
        DomainConfig(
            id='strategy',
            name='Strategy',
            description='Business planning, goals, and strategy',
            color='#c678dd',  # Purple
            icon='🎯',
            folder_path='02-Strategy',
            rag_weight=0.20,
            auto_tag_rules=[
                'strategy', 'planning', 'plan', 'goal', 'objective',
                'vision', 'mission', 'value', 'principle',
                'roadmap', 'quarter', 'okr', 'kpi', 'metric',
                'growth', 'expansion', 'market', 'competitive',
                'analysis', 'swot', 'research'
            ],
            created=now,
            modified=now,
            order=2
        ),
        DomainConfig(
            id='clients',
            name='Clients',
            description='Client projects, communications, and deliverables',
            color='#98c379',  # Green
            icon='🤝',
            folder_path='03-Clients',
            rag_weight=0.25,
            auto_tag_rules=[
                'client', 'customer', 'account', 'project',
                'contract', 'agreement', 'proposal', 'quote',
                'deliverable', 'milestone', 'invoice', 'payment',
                'meeting', 'email', 'communication', 'feedback',
                'relationship', 'satisfaction', 'crm'
            ],
            created=now,
            modified=now,
            order=3
        ),
        DomainConfig(
            id='finance',
            name='Finance',
            description='Accounting, budgets, invoices, financial planning',
            color='#e5c07b',  # Yellow
            icon='💰',
            folder_path='04-Finance',
            rag_weight=0.15,
            auto_tag_rules=[
                'finance', 'accounting', 'budget', 'expense', 'revenue',
                'invoice', 'receipt', 'payment', 'transaction',
                'tax', 'payroll', 'profit', 'loss', 'cashflow',
                'forecast', 'financial', 'bank', 'account',
                'quickbooks', 'xero', 'spreadsheet'
            ],
            created=now,
            modified=now,
            order=4
        ),
        DomainConfig(
            id='marketing',
            name='Marketing',
            description='Marketing, content, campaigns, and outreach',
            color='#e06c75',  # Red
            icon='📣',
            folder_path='05-Marketing',
            rag_weight=0.10,
            auto_tag_rules=[
                'marketing', 'content', 'campaign', 'outreach',
                'social media', 'blog', 'newsletter', 'email',
                'seo', 'analytics', 'traffic', 'conversion',
                'brand', 'messaging', 'copy', 'creative',
                'lead', 'funnel', 'acquisition', 'retention'
            ],
            created=now,
            modified=now,
            order=5
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


# Template registry
TEMPLATES: Dict[str, Dict[str, any]] = {
    'software-development': {
        'name': 'Software Development',
        'description': 'For developers and engineers working on code, infrastructure, and technical projects',
        'create_func': create_software_development_template,
        'domains_count': 5,
        'domains': ['Code', 'Infrastructure', 'Learning', 'Archive', 'Ideas']
    },
    'research': {
        'name': 'Academic Research',
        'description': 'For researchers and students working on academic projects, papers, and studies',
        'create_func': create_research_template,
        'domains_count': 5,
        'domains': ['Research', 'Literature', 'Data', 'Writing', 'Teaching']
    },
    'creative': {
        'name': 'Creative Work',
        'description': 'For artists, writers, designers, and creative professionals',
        'create_func': create_creative_work_template,
        'domains_count': 5,
        'domains': ['Active Projects', 'Writing', 'Visual', 'Audio', 'Archive']
    },
    'business': {
        'name': 'Business',
        'description': 'For entrepreneurs and business professionals managing operations, clients, and growth',
        'create_func': create_business_template,
        'domains_count': 5,
        'domains': ['Operations', 'Strategy', 'Clients', 'Finance', 'Marketing']
    }
}


def list_templates() -> List[Dict[str, any]]:
    """
    List all available domain templates.
    
    Returns:
        List of template metadata dictionaries
    """
    templates = []
    for template_id, template_data in TEMPLATES.items():
        templates.append({
            'id': template_id,
            'name': template_data['name'],
            'description': template_data['description'],
            'domains_count': template_data['domains_count'],
            'domains': template_data['domains']
        })
    return templates


def create_from_template(template_id: str) -> DomainsConfig:
    """
    Create domains from a template.
    
    Args:
        template_id: Template identifier (e.g., 'software-development')
    
    Returns:
        DomainsConfig with domains from the template
    
    Raises:
        ValueError: If template_id is not found
    """
    if template_id not in TEMPLATES:
        available = ', '.join(TEMPLATES.keys())
        raise ValueError(f"Template '{template_id}' not found. Available: {available}")
    
    template = TEMPLATES[template_id]
    create_func = template['create_func']
    
    return create_func()


def get_template_info(template_id: str) -> Dict[str, any]:
    """
    Get information about a template.
    
    Args:
        template_id: Template identifier
    
    Returns:
        Template metadata dictionary
    
    Raises:
        ValueError: If template_id is not found
    """
    if template_id not in TEMPLATES:
        available = ', '.join(TEMPLATES.keys())
        raise ValueError(f"Template '{template_id}' not found. Available: {available}")
    
    template = TEMPLATES[template_id]
    return {
        'id': template_id,
        'name': template['name'],
        'description': template['description'],
        'domains_count': template['domains_count'],
        'domains': template['domains']
    }


if __name__ == '__main__':
    # Test templates
    print("Available Templates:")
    print("=" * 60)
    
    for template in list_templates():
        print(f"\n{template['name']} ({template['id']})")
        print(f"  {template['description']}")
        print(f"  Domains ({template['domains_count']}): {', '.join(template['domains'])}")
    
    print("\n" + "=" * 60)
    print("\nTesting software-development template:")
    config = create_from_template('software-development')
    print(f"Created {len(config.domains)} domains:")
    for domain in config.domains:
        print(f"  {domain.icon} {domain.name}: {domain.description}")
