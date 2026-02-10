"""
Apollo Domain Engine
Understands your five domains and routes context appropriately

Now supports user-configurable domains via Phase 1.5 domain_config system
and integration-contracts dynamic domain configuration (YAML + custom domains).
Falls back to hardcoded domains for backward compatibility.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Set, Tuple, Any
import re

# Import domain config system
try:
    from core.domain_config import load_domains, DomainsConfig
    DOMAIN_CONFIG_AVAILABLE = True
except ImportError:
    DOMAIN_CONFIG_AVAILABLE = False

# YAML config
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


def load_domains_from_yaml(config_path: Optional[Path] = None, config_dict: Optional[Dict[str, Any]] = None) -> Optional[List["DomainConfig"]]:
    """
    Load domain definitions from YAML config (integration-contracts Task 12).
    Either pass config_path to a YAML file, or config_dict with a top-level 'domains' key.
    Returns None if no config or empty; callers fall back to domain_config JSON or hardcoded.
    """
    if config_dict is not None:
        raw = config_dict.get("domains")
    elif config_path and config_path.exists() and YAML_AVAILABLE:
        try:
            with open(config_path, "r") as f:
                data = yaml.safe_load(f) or {}
            raw = data.get("domains")
        except Exception:
            return None
    else:
        return None
    if not raw or not isinstance(raw, dict):
        return None
    result: List[DomainConfig] = []
    for domain_id, opts in raw.items():
        if not isinstance(opts, dict):
            continue
        name = opts.get("name") or domain_id.replace("_", " ").title()
        result.append(
            DomainConfig(
                id=domain_id.lower().strip(),
                name=str(name),
                description=str(opts.get("description", "")),
                color=str(opts.get("color", "#4A90D9")),
                icon=str(opts.get("icon", "📁")),
                keywords=list(opts.get("keywords", [])) if isinstance(opts.get("keywords"), list) else [],
                rag_collections=list(opts.get("rag_collections", [])) if isinstance(opts.get("rag_collections"), list) else [],
                folder_path=opts.get("folder_path"),
            )
        )
    return result if result else None


@dataclass
class DomainConfig:
    """
    Domain configuration from YAML (integration-contracts Task 12).
    Used when loading from config YAML; supports custom domains beyond the five.
    """
    id: str
    name: str
    description: str
    color: str = "#4A90D9"
    icon: str = "📁"
    keywords: List[str] = field(default_factory=list)
    rag_collections: List[str] = field(default_factory=list)
    folder_path: Optional[str] = None


class DomainType(Enum):
    """The five polymathic domains."""
    SIGILS = "sigils"      # Code, infrastructure, automation
    SIGNALS = "signals"    # Audio programming, synthesis
    SCROLLS = "scrolls"    # Writing, pedagogy, documentation
    GLYPHS = "glyphs"      # Visual work, design
    GRIDS = "grids"        # Systems thinking, frameworks
    UNKNOWN = "unknown"


@dataclass
class Domain:
    """A single domain configuration."""
    type: DomainType
    name: str
    description: str
    paths: List[Path] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    custom_id: Optional[str] = None  # Set for custom domains (id not in DomainType)

    def matches_path(self, path: Path) -> bool:
        """Check if a path belongs to this domain."""
        path_str = str(path.resolve())
        for domain_path in self.paths:
            if path_str.startswith(str(domain_path.resolve())):
                return True
        return False

    def matches_filename(self, filename: str) -> bool:
        """Check if a filename matches domain patterns."""
        from fnmatch import fnmatch
        for pattern in self.patterns:
            if fnmatch(filename, pattern):
                return True
        return False

    def matches_content(self, content: str) -> float:
        """Score how well content matches this domain (0-1)."""
        content_lower = content.lower()
        matches = sum(1 for kw in self.keywords if kw.lower() in content_lower)
        return min(matches / max(len(self.keywords), 1), 1.0)


class DomainEngine:
    """
    Manages domain detection and routing.

    The engine understands context and can:
    - Detect which domain(s) a query relates to
    - Filter search results by domain
    - Generate domain-appropriate system prompts
    - Track cross-domain connections
    """

    # Default domain definitions
    DEFAULT_DOMAINS = {
        DomainType.SIGILS: Domain(
            type=DomainType.SIGILS,
            name="Sigils",
            description="Code, infrastructure, automation, DevOps",
            patterns=["*.py", "*.rs", "*.go", "*.ts", "*.js", "*.lua",
                     "docker-compose*.yaml", "Dockerfile*", "*.tf"],
            keywords=["code", "docker", "kubernetes", "api", "server", "database",
                     "python", "rust", "javascript", "automation", "infrastructure",
                     "deploy", "ci/cd", "git"]
        ),
        DomainType.SIGNALS: Domain(
            type=DomainType.SIGNALS,
            name="Signals",
            description="Audio programming, synthesis, DSP, music technology",
            patterns=["*.scd", "*.maxpat", "*.pd", "*.faust", "*.lua"],
            keywords=["audio", "midi", "synthesis", "dsp", "norns", "supercollider",
                     "sound", "music", "oscillator", "filter", "envelope", "sampler",
                     "sequencer", "modular", "voltage", "cv", "gate", "trigger",
                     "monome", "eurorack", "instrument", "composition", "generative"]
        ),
        DomainType.SCROLLS: Domain(
            type=DomainType.SCROLLS,
            name="Scrolls",
            description="Writing, pedagogy, documentation, essays",
            patterns=["*.md", "*.txt", "*.org"],
            keywords=["essay", "pedagogy", "education", "writing", "notes", "journal",
                     "freire", "popular education", "teaching", "learning", "curriculum",
                     "documentation", "guide", "tutorial"]
        ),
        DomainType.GLYPHS: Domain(
            type=DomainType.GLYPHS,
            name="Glyphs",
            description="Visual work, design, UI/UX",
            patterns=["*.fig", "*.sketch", "*.ai", "*.psd", "*.svg"],
            keywords=["design", "visual", "ui", "ux", "color", "typography", "layout",
                     "interface", "wireframe", "mockup", "prototype", "figma"]
        ),
        DomainType.GRIDS: Domain(
            type=DomainType.GRIDS,
            name="Grids",
            description="Systems thinking, mental models, frameworks",
            patterns=[],  # Content-based, not file-type based
            keywords=["framework", "mental model", "systems thinking", "infinite game",
                     "finite game", "constraint", "emergence", "complexity", "feedback",
                     "polymathic", "cross-domain", "synthesis", "pattern", "archetype",
                     "meta", "metalearning", "paradigm", "worldview", "philosophy"]
        )
    }

    def __init__(
        self,
        config_domains: Optional[Dict] = None,
        use_domain_config: bool = True,
        config_dict: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize with optional custom domain configuration.
        
        Args:
            config_domains: Legacy config dict (for backward compatibility)
            use_domain_config: If True, load from ~/.polly/domains.json (Phase 1.5)
            config_dict: Full config dict (e.g. from PollyConfig._config) for YAML domains (Task 12)
        """
        self.domain_config: Optional[DomainsConfig] = None
        self._custom_domains: List[Domain] = []  # Custom domain ids beyond the five

        # Integration-contracts Task 12: Try YAML domains first (from config_dict)
        if config_dict is not None:
            yaml_domains = load_domains_from_yaml(config_dict=config_dict)
            if yaml_domains:
                self.domains, self._custom_domains = self._load_from_domain_config_list(yaml_domains)
                # Pattern learner integration (Use Case 2)
                self._pattern_learner = None
                return

        # Phase 1.5: Try to load from domains.json (includes custom domains from Settings UI)
        if use_domain_config and DOMAIN_CONFIG_AVAILABLE:
            try:
                self.domain_config = load_domains()
                self.domains, self._custom_domains = self._load_from_domain_config(self.domain_config)
                return
            except Exception as e:
                print(f"Warning: Failed to load domains.json: {e}")
                print("Falling back to hardcoded domains")
        
        # Fallback: use hardcoded or legacy config
        self.domains = self._load_domains(config_domains)
        
        # Pattern learner integration (Use Case 2)
        self._pattern_learner = None

    def set_pattern_learner(self, pattern_learner):
        """
        Attach pattern engine for domain detection enhancement (Use Case 2).
        
        Args:
            pattern_learner: PatternEngine instance (or legacy PatternLearner)
        """
        self._pattern_learner = pattern_learner
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Pattern engine attached to DomainEngine for enhanced detection")

    def _load_from_domain_config_list(
        self, config_list: List[DomainConfig]
    ) -> Tuple[Dict[DomainType, Domain], List[Domain]]:
        """
        Load domains from YAML-style DomainConfig list (integration-contracts Task 12).
        Returns (enum_keyed_domains, custom_domains).
        """
        domains: Dict[DomainType, Domain] = {}
        custom: List[Domain] = []
        for dc in config_list:
            try:
                domain_type = DomainType(dc.id)
            except ValueError:
                domain_type = DomainType.UNKNOWN
            default_domain = self.DEFAULT_DOMAINS.get(domain_type) if domain_type != DomainType.UNKNOWN else None
            patterns = list(default_domain.patterns) if default_domain else []
            d = Domain(
                type=domain_type,
                name=dc.name,
                description=dc.description,
                paths=[Path(dc.folder_path)] if dc.folder_path else [],
                patterns=patterns,
                keywords=list(dc.keywords),
                custom_id=dc.id if domain_type == DomainType.UNKNOWN else None,
            )
            if domain_type != DomainType.UNKNOWN:
                domains[domain_type] = d
            else:
                custom.append(d)
        # Ensure the five enum domains exist; fill from defaults if missing
        for dt in DomainType:
            if dt == DomainType.UNKNOWN:
                continue
            if dt not in domains:
                default = self.DEFAULT_DOMAINS.get(dt)
                if default:
                    domains[dt] = default
        return domains, custom

    def _load_from_domain_config(self, config: DomainsConfig) -> Tuple[Dict[DomainType, Domain], List[Domain]]:
        """
        Load domains from Phase 1.5 domain config system (domains.json).
        Enum ids go into self.domains; other ids are custom domains in _custom_domains (custom-domains feature).
        """
        domains: Dict[DomainType, Domain] = {}
        custom: List[Domain] = []

        for domain_cfg in config.domains:
            try:
                domain_type = DomainType(domain_cfg.id)
            except ValueError:
                # Custom domain: id not in enum (e.g. work, my-domain from Settings UI)
                domain_type = DomainType.UNKNOWN
            default_domain = self.DEFAULT_DOMAINS.get(domain_type) if domain_type != DomainType.UNKNOWN else None
            patterns = list(default_domain.patterns) if default_domain else []
            d = Domain(
                type=domain_type,
                name=domain_cfg.name,
                description=domain_cfg.description,
                paths=[Path(domain_cfg.folder_path)] if domain_cfg.folder_path else [],
                patterns=patterns,
                keywords=list(domain_cfg.auto_tag_rules),
                custom_id=domain_cfg.id if domain_type == DomainType.UNKNOWN else None,
            )
            if domain_type != DomainType.UNKNOWN:
                domains[domain_type] = d
            else:
                custom.append(d)

        return domains, custom
    
    def _load_domains(self, config_domains: Optional[Dict]) -> Dict[DomainType, Domain]:
        """Load domains from config, falling back to defaults."""
        domains = {}

        for domain_type in DomainType:
            if domain_type == DomainType.UNKNOWN:
                continue

            default = self.DEFAULT_DOMAINS.get(domain_type)

            if config_domains and domain_type.value in config_domains:
                cfg = config_domains[domain_type.value]
                domains[domain_type] = Domain(
                    type=domain_type,
                    name=cfg.get("name", default.name if default else domain_type.value),
                    description=cfg.get("description", default.description if default else ""),
                    paths=[Path(p) for p in cfg.get("paths", [])],
                    patterns=cfg.get("patterns", default.patterns if default else []),
                    keywords=cfg.get("keywords", default.keywords if default else [])
                )
            elif default:
                domains[domain_type] = default

        return domains
    
    def _get_pattern_domain_boosts(self, query: str) -> Dict[DomainType, float]:
        """
        Calculate domain confidence boosts based on learned patterns (Use Case 2).
        
        Uses domain→collection patterns to determine which domains are most likely
        based on historical query patterns.
        
        Args:
            query: User query
            
        Returns:
            Dict mapping DomainType → boost amount (0-0.25)
        """
        boosts: Dict[DomainType, float] = {}
        
        if not self._pattern_learner:
            return boosts
        
        # Extract query concepts for matching
        query_concepts = set(query.lower().split())
        
        # Check domain→collection patterns
        for pattern_id, domain_pattern in self._pattern_learner.domain_priority_patterns.items():
            domain_name = domain_pattern.domain
            
            # Map domain name to DomainType enum
            domain_type = None
            for dt in DomainType:
                if dt.value == domain_name.lower():
                    domain_type = dt
                    break
            
            if not domain_type:
                continue
            
            # Calculate boost based on collection weights
            # Higher weights = this domain frequently uses these collections for queries
            if domain_pattern.collection_weights:
                avg_weight = sum(domain_pattern.collection_weights.values()) / len(domain_pattern.collection_weights)
                
                # Normalize to 0-0.25 range (max 25% boost)
                # Weights are typically 0-2, so divide by 8 to get 0-0.25
                boost = min(avg_weight / 8.0, 0.25)
                
                # Only apply boost if significant (>5% = 0.05)
                if boost > 0.05:
                    boosts[domain_type] = boost
        
        # Also check conceptual patterns for concept expansion
        expanded_boosts = self._get_conceptual_pattern_boosts(query, query_concepts)
        
        # Merge conceptual boosts (take max of domain or conceptual boost)
        for domain_type, concept_boost in expanded_boosts.items():
            if domain_type in boosts:
                boosts[domain_type] = max(boosts[domain_type], concept_boost)
            else:
                boosts[domain_type] = concept_boost
        
        return boosts
    
    def _get_conceptual_pattern_boosts(self, query: str, query_concepts: Set[str]) -> Dict[DomainType, float]:
        """
        Calculate domain boosts based on conceptual pattern expansion (Use Case 2).
        
        Expands query terms using learned conceptual patterns, then re-analyzes
        for domain matches.
        
        Args:
            query: Original query
            query_concepts: Set of concepts from query
            
        Returns:
            Dict mapping DomainType → boost amount (0-0.25)
        """
        boosts: Dict[DomainType, float] = {}
        
        if not self._pattern_learner:
            return boosts
        
        # Find related concepts from patterns
        expanded_terms = []
        for concept in query_concepts:
            # Get conceptual patterns for this concept
            related_patterns = self._pattern_learner.get_conceptual_patterns(concept)
            
            # Add top 2 related concepts per query concept
            for pattern in related_patterns[:2]:
                concept1 = pattern.metadata.get('concept1', '')
                concept2 = pattern.metadata.get('concept2', '')
                
                # Get the related concept (not the query concept)
                related = concept2 if concept1 == concept else concept1
                if related and related not in query_concepts:
                    expanded_terms.append(related)
        
        # Limit to top 3 expanded terms
        expanded_terms = expanded_terms[:3]
        
        if not expanded_terms:
            return boosts
        
        # Re-analyze domain keywords with expanded terms
        expanded_query = f"{query} {' '.join(expanded_terms)}"
        
        # Calculate boost for each domain based on keyword matches in expanded query
        for domain_type, domain in self.domains.items():
            if domain_type == DomainType.UNKNOWN:
                continue
            
            # Count keyword matches in expanded terms only
            expanded_lower = ' '.join(expanded_terms).lower()
            matches = sum(1 for keyword in domain.keywords if keyword.lower() in expanded_lower)
            
            if matches > 0:
                # Boost by 0.05 per match, max 0.15
                boost = min(matches * 0.05, 0.15)
                boosts[domain_type] = boost
        
        return boosts

    def detect_domains(self, query: str, context: Optional[Dict] = None) -> List[DomainType]:
        """
        Detect which domain(s) a query relates to.

        Returns list of domains sorted by relevance.
        """
        scores = self._score_domains(query, context)
        
        # Return domains with non-zero scores, sorted by score
        relevant = [(d, s) for d, s in scores.items() if s > 0]
        relevant.sort(key=lambda x: x[1], reverse=True)

        if not relevant:
            return [DomainType.UNKNOWN]

        return [d for d, _ in relevant]
    
    def detect_domains_with_scores(self, query: str, context: Optional[Dict] = None) -> List[tuple[DomainType, float]]:
        """
        Detect which domain(s) a query relates to, returning scores.

        Returns list of (domain, score) tuples sorted by relevance.
        Useful for understanding primary vs secondary domains.
        """
        scores = self._score_domains(query, context)
        
        # Return domains with non-zero scores, sorted by score
        relevant = [(d, s) for d, s in scores.items() if s > 0]
        relevant.sort(key=lambda x: x[1], reverse=True)

        if not relevant:
            return [(DomainType.UNKNOWN, 0.0)]

        return relevant
    
    def record_successful_detection(self, query: str, detected_domains: List[DomainType], user_accepted: bool = True):
        """
        Record successful (or unsuccessful) domain detection for pattern learning (Use Case 2).
        
        Args:
            query: User query that triggered detection
            detected_domains: Domains detected by system
            user_accepted: True if user accepted, False if user corrected domain
        """
        if not self._pattern_learner:
            return
        
        # Convert DomainType enums to strings
        domain_names = [d.value for d in detected_domains if d != DomainType.UNKNOWN]
        
        if not domain_names:
            return
        
        # Record in pattern learner
        for domain_name in domain_names:
            # Find pattern by matching domain name
            for pattern_id, pattern in self._pattern_learner.domain_priority_patterns.items():
                if pattern.domain == domain_name:
                    if user_accepted:
                        # Positive reinforcement
                        pattern.total_queries += 1
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.debug(f"Domain detection success recorded: {domain_name} (total_queries: {pattern.total_queries})")
                    else:
                        # Negative feedback (could implement weight reduction here if needed)
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.info(f"Domain detection correction recorded: {query} → {domain_name} (rejected by user)")
                    break
    
    def _extract_technologies_from_query(self, query: str) -> List[str]:
        """
        Extract technology/language mentions from query.
        
        Universal: Looks for common patterns like file extensions, language names, etc.
        Returns lowercase technology identifiers.
        """
        technologies = []
        query_lower = query.lower()
        
        # Common programming languages and their variations
        tech_patterns = {
            'python': ['python', 'py'],
            'javascript': ['javascript', 'js', 'node'],
            'typescript': ['typescript', 'ts'],
            'rust': ['rust', 'rs'],
            'go': ['golang', 'go'],
            'lua': ['lua'],
            'ruby': ['ruby', 'rb'],
            'java': ['java'],
            'cpp': ['c\\+\\+', 'cpp'],  # Escape + for regex
            'c': [r'\bc language\b', r'\bc programming\b'],  # Only match if explicitly "c language" or "c programming"
            'shell': ['bash', 'zsh', 'shell', 'sh'],
            'supercollider': ['supercollider', 'sclang', 'scd'],
            'max': ['max/msp', 'maxmsp'],  # Remove plain 'max' to avoid false positives
            'puredata': ['puredata', 'pure data', 'pd'],
            'react': ['react', 'reactjs'],
            'vue': ['vue', 'vuejs'],
            'docker': ['docker', 'dockerfile'],
            'kubernetes': ['kubernetes', 'k8s'],
        }
        
        for tech, patterns in tech_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    technologies.append(tech)
                    break
        
        return technologies
    
    def _boost_domains_by_technology(self, technologies: List[str]) -> Dict[DomainType, float]:
        """
        Boost domains whose patterns match mentioned technologies.
        
        Universal: Works for ANY domain configuration and ANY technology.
        Checks if domain's file patterns match the mentioned technology.
        
        Args:
            technologies: List of technology identifiers (e.g., ['python', 'lua'])
            
        Returns:
            Dict mapping DomainType to boost amount (0-0.3)
        """
        boosts: Dict[DomainType, float] = {}
        
        if not technologies:
            return boosts
        
        import logging
        logger = logging.getLogger(__name__)
        
        # Map technologies to file extensions
        tech_to_extensions = {
            'python': ['.py'],
            'javascript': ['.js', '.mjs', '.cjs'],
            'typescript': ['.ts', '.tsx'],
            'rust': ['.rs'],
            'go': ['.go'],
            'lua': ['.lua'],
            'ruby': ['.rb'],
            'java': ['.java'],
            'cpp': ['.cpp', '.cc', '.cxx', '.hpp'],
            'c': ['.c', '.h'],
            'shell': ['.sh', '.bash', '.zsh'],
            'supercollider': ['.scd'],
            'max': ['.maxpat'],
            'puredata': ['.pd'],
            'react': ['.jsx', '.tsx'],
            'vue': ['.vue'],
            'docker': ['dockerfile', 'docker-compose'],
        }
        
        for domain_type, domain in self.domains.items():
            if domain_type == DomainType.UNKNOWN:
                continue
            
            domain_boost = 0.0
            matched_techs = []
            
            for tech in technologies:
                extensions = tech_to_extensions.get(tech, [])
                
                # Check if any of domain's patterns match this technology
                for pattern in domain.patterns:
                    pattern_lower = pattern.lower()
                    
                    # Check extensions
                    for ext in extensions:
                        if ext in pattern_lower or pattern_lower.replace('*', '') == ext:
                            domain_boost += 0.2  # Boost per matched technology
                            matched_techs.append(tech)
                            break
            
            if domain_boost > 0:
                # Cap boost at 0.3 total
                boosts[domain_type] = min(domain_boost, 0.3)
                logger.info(f"🔧 Technology boost for {domain_type.value}: +{boosts[domain_type]:.2f} (matched: {', '.join(matched_techs)})")
        
        return boosts
    
    def _detect_query_intent(self, query: str) -> List[str]:
        """
        Detect user intent from query text.
        
        Universal: Works for any type of activity/intent.
        Returns list of detected intents (can be multiple).
        
        Intent types:
        - programming: coding, development, implementation
        - analysis: data processing, calculations, research
        - design: visual work, UI/UX, mockups
        - writing: documentation, essays, notes
        - learning: understanding concepts, mental models
        - audio: sound synthesis, music creation
        """
        intents = []
        query_lower = query.lower()
        
        # Programming intent patterns
        programming_patterns = [
            r'\b(program|code|develop|build|implement|create|write)\b.*\b(app|application|script|function|api|service|tool|engine|system)\b',
            r'\b(debug|fix|refactor|optimize|test)\b',
            r'\bhow (do|can) i (program|code|write|build|create|implement)\b',
            r'\b(development|implementation|coding)\b',
            r'\bmake (a|an|the) (app|application|script|tool|api)\b',
            r'\bimplement (a|an|the)\b',
        ]
        
        for pattern in programming_patterns:
            if re.search(pattern, query_lower):
                intents.append('programming')
                break
        
        # Analysis intent patterns
        analysis_patterns = [
            r'\b(analyze|process|calculate|compute|measure|evaluate)\b',
            r'\bhow (do|can) i (analyze|process|calculate)\b',
            r'\b(data|dataset|statistics|metrics|analytics)\b.*\b(analyze|process)\b',
            r'\b(analysis|processing|computation)\b',
        ]
        
        for pattern in analysis_patterns:
            if re.search(pattern, query_lower):
                intents.append('analysis')
                break
        
        # Design intent patterns
        design_patterns = [
            r'\b(design|layout|mockup|prototype|wireframe)\b',
            r'\bhow (do|can) i (design|create|make)\b.*\b(ui|interface|layout|design)\b',
            r'\b(visual|aesthetic|style|theme)\b.*\b(design|create)\b',
            r'\b(ui|ux|interface|frontend)\b',
        ]
        
        for pattern in design_patterns:
            if re.search(pattern, query_lower):
                intents.append('design')
                break
        
        # Writing intent patterns
        writing_patterns = [
            r'\b(write|document|essay|article|note|journal)\b',
            r'\bhow (do|can) i (write|document|explain)\b',
            r'\b(documentation|tutorial|guide|explanation)\b',
            r'\b(teach|learn|understand|explain)\b.*\b(concept|idea|topic)\b',
        ]
        
        for pattern in writing_patterns:
            if re.search(pattern, query_lower):
                intents.append('writing')
                break
        
        # Learning/Systems thinking intent patterns
        learning_patterns = [
            r'\b(framework|mental model|pattern|paradigm|worldview)\b',
            r'\bwhat is (the )?(concept|idea|principle|pattern)\b',
            r'\b(understand|learn about|explain|clarify)\b.*\b(system|framework|model)\b',
            r'\b(systems thinking|complexity|emergence)\b',
            r'\bhow does.*work\b',
        ]
        
        for pattern in learning_patterns:
            if re.search(pattern, query_lower):
                intents.append('learning')
                break
        
        # Audio/Music creation intent patterns
        audio_patterns = [
            r'\b(synthesis|synthesize|sound|audio|music)\b.*\b(create|make|generate|play)\b',
            r'\bhow (do|can) i (make|create|synthesize|generate)\b.*\b(sound|audio|music)\b',
            r'\b(synthesize|generate)\b.*\b(sound|audio|music|tone|bass|lead)\b',
            r'\b(sequencer|sampler|instrument|effect)\b',
            r'\b(midi|osc|cv|gate)\b',
        ]
        
        for pattern in audio_patterns:
            if re.search(pattern, query_lower):
                intents.append('audio')
                break
        
        return intents
    
    def _boost_domains_by_intent(self, intents: List[str]) -> Dict[DomainType, float]:
        """
        Boost domains based on detected user intent.
        
        Universal: Maps intent types to domain characteristics.
        Works for ANY domain configuration by checking domain keywords and descriptions.
        
        Args:
            intents: List of detected intent types
            
        Returns:
            Dict mapping DomainType to boost amount (0-0.25)
        """
        boosts: Dict[DomainType, float] = {}
        
        if not intents:
            return boosts
        
        import logging
        logger = logging.getLogger(__name__)
        
        # Map intents to domain characteristic indicators
        intent_domain_indicators = {
            'programming': ['code', 'api', 'function', 'script', 'development', 'infrastructure'],
            'analysis': ['data', 'process', 'calculate', 'statistics', 'analysis'],
            'design': ['design', 'visual', 'ui', 'ux', 'interface', 'layout'],
            'writing': ['writing', 'documentation', 'essay', 'notes', 'teaching'],
            'learning': ['framework', 'mental model', 'systems thinking', 'pattern', 'complexity'],
            'audio': ['audio', 'synthesis', 'sound', 'music', 'midi'],
        }
        
        for domain_type, domain in self.domains.items():
            if domain_type == DomainType.UNKNOWN:
                continue
            
            domain_boost = 0.0
            matched_intents = []
            
            # Check if domain's keywords match any detected intent
            domain_keywords_lower = [kw.lower() for kw in domain.keywords]
            domain_desc_lower = domain.description.lower()
            
            for intent in intents:
                indicators = intent_domain_indicators.get(intent, [])
                
                # Check if domain has keywords matching this intent
                for indicator in indicators:
                    if (any(indicator in kw for kw in domain_keywords_lower) or 
                        indicator in domain_desc_lower):
                        domain_boost += 0.15  # Boost per matched intent
                        matched_intents.append(intent)
                        break
            
            if domain_boost > 0:
                # Cap boost at 0.25 total
                boosts[domain_type] = min(domain_boost, 0.25)
                logger.info(f"💡 Intent boost for {domain_type.value}: +{boosts[domain_type]:.2f} (matched: {', '.join(matched_intents)})")
        
        return boosts
    
    def _score_domains(self, query: str, context: Optional[Dict] = None) -> Dict[DomainType, float]:
        """
        Internal method to score all domains for a query.
        
        Enhanced with:
        - Pattern-based confidence boosting (Use Case 2)
        - Technology pattern matching (Universal cross-domain fix)
        - Intent-based detection (Universal cross-domain fix)
        """
        scores: Dict[DomainType, float] = {}

        for domain_type, domain in self.domains.items():
            score = domain.matches_content(query)

            # Boost score if context matches
            if context:
                if "file_path" in context:
                    path = Path(context["file_path"])
                    if domain.matches_path(path) or domain.matches_filename(path.name):
                        score += 0.5

                if "file_content" in context:
                    score += domain.matches_content(context["file_content"]) * 0.3

            scores[domain_type] = score

        # Universal cross-domain fix: Technology pattern matching
        # Detect technologies mentioned in query and boost domains with matching patterns
        technologies = self._extract_technologies_from_query(query)
        if technologies:
            tech_boosts = self._boost_domains_by_technology(technologies)
            for domain_type, boost in tech_boosts.items():
                if domain_type in scores:
                    scores[domain_type] += boost

        # Universal cross-domain fix: Intent-based detection
        # Detect user intent and boost domains that match that intent
        intents = self._detect_query_intent(query)
        if intents:
            intent_boosts = self._boost_domains_by_intent(intents)
            for domain_type, boost in intent_boosts.items():
                if domain_type in scores:
                    scores[domain_type] += boost

        # Use Case 2: Pattern-based confidence boosting
        # If pattern learner is available, boost scores based on learned patterns
        if hasattr(self, '_pattern_learner') and self._pattern_learner:
            pattern_boosts = self._get_pattern_domain_boosts(query)
            for domain_type, boost in pattern_boosts.items():
                if domain_type in scores:
                    original_score = scores[domain_type]
                    scores[domain_type] += boost
                    if boost > 0.05:  # Only log significant boosts
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.info(f"Pattern boosted {domain_type.value}: {original_score:.2f} → {scores[domain_type]:.2f} (+{boost:.2f})")

        return scores

    def get_domain_prompt(self, domains: List[DomainType], include_cross_domain: bool = False) -> str:
        """
        Generate a system prompt section for the detected domains.
        
        Args:
            domains: List of detected domains in priority order
            include_cross_domain: Whether to include cross-domain connection suggestions
        """
        if not domains or domains == [DomainType.UNKNOWN]:
            return ""

        domain_descriptions = []
        for domain_type in domains[:3]:  # Top 3 domains
            # Ensure domain_type is a DomainType enum
            if isinstance(domain_type, str):
                try:
                    domain_type = DomainType(domain_type)
                except ValueError:
                    continue
            elif not isinstance(domain_type, DomainType):
                continue
                
            domain = self.domains.get(domain_type)
            if domain:
                domain_descriptions.append(f"**{domain.name}**: {domain.description}")

        if not domain_descriptions:
            return ""

        prompt = f"""
The user's query relates to these domains:
{chr(10).join(domain_descriptions)}

Draw on knowledge and patterns specific to these areas when responding."""

        # Add cross-domain connections if requested and multiple domains detected
        if include_cross_domain and len(domains) >= 2:
            cross_domain = self.get_cross_domain_connections(domains)
            if cross_domain:
                prompt += f"\n{cross_domain}"

        return prompt

    def filter_sources_by_domain(
        self,
        sources: List[Dict],
        domains: List[DomainType],
        preserve_secondary: bool = True
    ) -> List[Dict]:
        """
        Filter search results to prefer domain-relevant sources.
        
        Args:
            sources: List of source dicts with filepath and content
            domains: Detected domains in priority order
            preserve_secondary: If True, keep results from secondary domains (less aggressive filtering)
        """
        if not domains or domains == [DomainType.UNKNOWN]:
            return sources
        
        # Validate and convert domains to DomainType enums
        validated_domains = []
        for d in domains:
            if isinstance(d, DomainType):
                validated_domains.append(d)
            elif isinstance(d, str):
                try:
                    validated_domains.append(DomainType(d))
                except ValueError:
                    continue
        
        if not validated_domains:
            return sources

        scored = []
        for source in sources:
            score = 0
            path = Path(source.get("filepath", ""))
            content = source.get("content", "")

            # Weight domains by their position (primary domain gets more weight)
            for idx, domain_type in enumerate(validated_domains):
                domain = self.domains.get(domain_type)
                if domain:
                    # Diminishing weight for secondary domains
                    weight = 1.0 / (idx + 1) if preserve_secondary else (1.0 if idx == 0 else 0.3)
                    
                    domain_score = 0
                    if domain.matches_path(path):
                        domain_score += 2
                    if domain.matches_filename(path.name):
                        domain_score += 1
                    domain_score += domain.matches_content(content)
                    
                    score += domain_score * weight

            scored.append((source, score))

        # Sort by score, but preserve some original ordering for semantic relevance
        # Only re-order significantly different scores
        scored.sort(key=lambda x: x[1], reverse=True)
        return [s for s, _ in scored]

    def get_cross_domain_connections(self, domains: List[DomainType]) -> str:
        """Suggest potential cross-domain connections."""
        # Ensure all domains are DomainType enums, not strings
        validated_domains = []
        for d in domains:
            if isinstance(d, DomainType):
                validated_domains.append(d)
            elif isinstance(d, str):
                # Try to convert string to DomainType
                try:
                    validated_domains.append(DomainType(d))
                except ValueError:
                    # Skip invalid domain strings
                    continue
            else:
                # Skip invalid types
                continue
        
        # Comprehensive cross-domain connection mappings
        connections = {
            (DomainType.SIGILS, DomainType.SIGNALS):
                "Code patterns that could enhance audio work, or audio concepts that inform system design",
            (DomainType.SIGILS, DomainType.SCROLLS):
                "Documentation patterns, writing about technical concepts, or teaching code through narrative",
            (DomainType.SIGILS, DomainType.GLYPHS):
                "UI/UX implementation, design systems in code, or visual debugging tools",
            (DomainType.SIGILS, DomainType.GRIDS):
                "Architectural patterns, systems design, or infrastructure as frameworks",
            (DomainType.SIGNALS, DomainType.SCROLLS):
                "Writing about sound, audio pedagogy, or documenting musical processes",
            (DomainType.SIGNALS, DomainType.GLYPHS):
                "Visual representations of audio, audio-visual synthesis, or interface design for instruments",
            (DomainType.SIGNALS, DomainType.GRIDS):
                "Audio as a lens for understanding systems, systems thinking applied to sound design, or compositional frameworks",
            (DomainType.SCROLLS, DomainType.GLYPHS):
                "Visual essays, information design for writing, or designed learning experiences",
            (DomainType.SCROLLS, DomainType.GRIDS):
                "Writing that explores systems thinking, frameworks for pedagogy, or meta-cognitive documentation",
            (DomainType.GLYPHS, DomainType.GRIDS):
                "Design frameworks, visual systems thinking, or interface patterns for complex systems",
        }

        if len(validated_domains) < 2:
            return ""

        suggestions = []
        for i, d1 in enumerate(validated_domains):
            for d2 in validated_domains[i+1:]:
                key = (d1, d2) if (d1, d2) in connections else (d2, d1)
                if key in connections:
                    suggestions.append(connections[key])

        if suggestions:
            return f"\n\n**Cross-Domain Connections**: {'; '.join(suggestions)}\n\nConsider how insights from one domain might illuminate or enhance work in the other."
        return ""
    
    def get_domain_colors(self) -> Dict[str, str]:
        """
        Get domain colors for UI rendering.
        
        Returns dict mapping domain ID to hex color.
        Used by dashboard and other UI components.
        """
        colors = {}
        
        # If we have domain config, use those colors
        if self.domain_config:
            for domain_cfg in self.domain_config.domains:
                colors[domain_cfg.id] = domain_cfg.color
        else:
            # Fallback to hardcoded colors
            colors = {
                'sigils': '#61afef',
                'signals': '#c678dd',
                'scrolls': '#98c379',
                'glyphs': '#e5c07b',
                'grids': '#e06c75'
            }
        
        return colors
    
    def get_domain_icons(self) -> Dict[str, str]:
        """
        Get domain icons for UI rendering.
        
        Returns dict mapping domain ID to emoji icon.
        """
        icons = {}
        
        # If we have domain config, use those icons
        if self.domain_config:
            for domain_cfg in self.domain_config.domains:
                icons[domain_cfg.id] = domain_cfg.icon
        else:
            # Fallback to hardcoded icons
            icons = {
                'sigils': '⚡',
                'signals': '📡',
                'scrolls': '📜',
                'glyphs': '✨',
                'grids': '🗂️'
            }
        
        return icons


# Domain-specific system prompt templates
DOMAIN_PROMPTS = {
    DomainType.SIGILS: """
When discussing code and infrastructure:
- Emphasize clean architecture and maintainability
- Consider Docker/container patterns when relevant
- Reference existing code patterns in the knowledge base
- Suggest automation where appropriate
""",

    DomainType.SIGNALS: """
When discussing audio programming:
- Emphasize instruments over tracks (generative over fixed)
- Consider real-time constraints and performance
- Reference norns/SuperCollider patterns when relevant
- Think in terms of constraint-based composition
""",

    DomainType.SCROLLS: """
When discussing writing and pedagogy:
- Use problem-posing over answer-giving approaches
- Reference Freire and popular education principles
- Consider the reader's learning journey
- Connect ideas across domains when relevant
""",

    DomainType.GLYPHS: """
When discussing visual work:
- Consider both aesthetic and functional aspects
- Think about the user's visual journey
- Reference design principles in the knowledge base
""",

    DomainType.GRIDS: """
When discussing systems and frameworks:
- Think in terms of infinite vs finite games
- Consider emergence and feedback loops
- Look for patterns that apply across domains
- Emphasize continuation over completion
"""
}
