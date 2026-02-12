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
    """A single domain configuration (pure user-defined: identified by id only)."""
    id: str
    name: str
    description: str
    paths: List[Path] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)

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
        """Score how well content matches this domain (0-1).
        
        Uses word-boundary matching for short keywords (<=3 chars) to avoid
        false positives like 'ui' matching inside 'build' or 'fruit'.
        Longer keywords use substring matching.
        """
        content_lower = content.lower()
        matches = 0
        for kw in self.keywords:
            kw_lower = kw.lower()
            if len(kw_lower) <= 3:
                # Word-boundary match for short keywords to avoid substring false positives
                if re.search(r'\b' + re.escape(kw_lower) + r'\b', content_lower):
                    matches += 1
            else:
                if kw_lower in content_lower:
                    matches += 1
        return min(matches / max(len(self.keywords), 1), 1.0)


# Optional file patterns per domain id (for template/legacy ids; pure user-defined uses config)
PATTERNS_BY_ID: Dict[str, List[str]] = {
    "sigils": ["*.py", "*.rs", "*.go", "*.ts", "*.js", "*.lua", "docker-compose*.yaml", "Dockerfile*", "*.tf"],
    "signals": ["*.scd", "*.maxpat", "*.pd", "*.faust", "*.lua"],
    "scrolls": ["*.md", "*.txt", "*.org"],
    "glyphs": ["*.fig", "*.sketch", "*.ai", "*.psd", "*.svg"],
    "grids": [],
}


class DomainEngine:
    """
    Manages domain detection and routing (pure user-defined: all domains keyed by string id).
    """

    def _domain_id_list(self) -> List[str]:
        """Ordered list of domain ids for iteration (e.g. for backward-compat get_domain_colors)."""
        return list(self._domains_by_id.keys())

    def __init__(
        self,
        config_domains: Optional[Dict] = None,
        use_domain_config: bool = True,
        config_dict: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize with optional domain configuration (pure user-defined: store by string id).
        When no config: empty. Domains come from domains.json or config YAML only.
        """
        self.domain_config: Optional[DomainsConfig] = None
        self._domains_by_id: Dict[str, Domain] = {}
        self._pattern_learner = None

        # YAML domains first (from config_dict)
        if config_dict is not None:
            yaml_domains = load_domains_from_yaml(config_dict=config_dict)
            if yaml_domains:
                self._domains_by_id = self._load_from_domain_config_list(yaml_domains)
                return

        # domains.json (Phase 1.5)
        if use_domain_config and DOMAIN_CONFIG_AVAILABLE:
            try:
                self.domain_config = load_domains()
                self._domains_by_id = self._load_from_domain_config(self.domain_config)
                return
            except Exception as e:
                print(f"Warning: Failed to load domains.json: {e}")

        # Legacy config_domains dict (e.g. from Polly config)
        if config_domains and isinstance(config_domains, dict):
            self._domains_by_id = self._load_domains(config_domains)
        # else: leave _domains_by_id empty (no built-in fallback)

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

    def _load_from_domain_config_list(self, config_list: List[DomainConfig]) -> Dict[str, Domain]:
        """Load domains from YAML-style DomainConfig list; returns Dict[id, Domain]."""
        result: Dict[str, Domain] = {}
        for dc in config_list:
            bid = (dc.id or "").strip().lower()
            if not bid:
                continue
            result[bid] = Domain(
                id=bid,
                name=dc.name,
                description=dc.description,
                paths=[Path(dc.folder_path)] if dc.folder_path else [],
                patterns=list(PATTERNS_BY_ID.get(bid, [])),
                keywords=list(dc.keywords),
            )
        return result

    def _load_from_domain_config(self, config: DomainsConfig) -> Dict[str, Domain]:
        """Load domains from domains.json; returns Dict[id, Domain]."""
        result: Dict[str, Domain] = {}
        for domain_cfg in config.domains:
            bid = (domain_cfg.id or "").strip().lower()
            if not bid:
                continue
            result[bid] = Domain(
                id=bid,
                name=domain_cfg.name,
                description=domain_cfg.description,
                paths=[Path(domain_cfg.folder_path)] if domain_cfg.folder_path else [],
                patterns=list(PATTERNS_BY_ID.get(bid, [])),
                keywords=list(domain_cfg.auto_tag_rules),
            )
        return result
    
    def _load_domains(self, config_domains: Dict[str, Any]) -> Dict[str, Domain]:
        """Load domains from legacy config dict keyed by domain id; returns Dict[id, Domain]."""
        result: Dict[str, Domain] = {}
        for bid, cfg in (config_domains or {}).items():
            if not isinstance(cfg, dict):
                continue
            bid = (bid or "").strip().lower()
            if not bid:
                continue
            result[bid] = Domain(
                id=bid,
                name=cfg.get("name", bid),
                description=cfg.get("description", ""),
                paths=[Path(p) for p in cfg.get("paths", [])],
                patterns=list(cfg.get("patterns", PATTERNS_BY_ID.get(bid, []))),
                keywords=list(cfg.get("keywords", [])),
            )
        return result
    
    def _get_pattern_domain_boosts(self, query: str) -> Dict[str, float]:
        """Domain confidence boosts from learned patterns (Use Case 2). Returns Dict[domain_id, boost]."""
        boosts: Dict[str, float] = {}
        if not self._pattern_learner:
            return boosts
        query_concepts = set(query.lower().split())
        for pattern_id, domain_pattern in self._pattern_learner.domain_priority_patterns.items():
            domain_id = (domain_pattern.domain or "").strip().lower()
            if not domain_id or domain_id not in self._domains_by_id:
                continue
            if domain_pattern.collection_weights:
                avg_weight = sum(domain_pattern.collection_weights.values()) / len(domain_pattern.collection_weights)
                boost = min(avg_weight / 8.0, 0.25)
                if boost > 0.05:
                    boosts[domain_id] = max(boosts.get(domain_id, 0), boost)
        expanded = self._get_conceptual_pattern_boosts(query, query_concepts)
        for domain_id, concept_boost in expanded.items():
            boosts[domain_id] = max(boosts.get(domain_id, 0), concept_boost)
        return boosts
    
    def _get_conceptual_pattern_boosts(self, query: str, query_concepts: Set[str]) -> Dict[str, float]:
        """Conceptual pattern expansion boosts. Returns Dict[domain_id, boost]."""
        boosts: Dict[str, float] = {}
        if not self._pattern_learner:
            return boosts
        expanded_terms = []
        for concept in query_concepts:
            for pattern in self._pattern_learner.get_conceptual_patterns(concept)[:2]:
                concept1 = pattern.metadata.get("concept1", "")
                concept2 = pattern.metadata.get("concept2", "")
                related = concept2 if concept1 == concept else concept1
                if related and related not in query_concepts:
                    expanded_terms.append(related)
        expanded_terms = expanded_terms[:3]
        if not expanded_terms:
            return boosts
        expanded_lower = " ".join(expanded_terms).lower()
        for domain_id, domain in self._domains_by_id.items():
            matches = sum(1 for kw in domain.keywords if (kw or "").lower() in expanded_lower)
            if matches > 0:
                boosts[domain_id] = min(matches * 0.05, 0.15)
        return boosts

    def detect_domains(self, query: str, context: Optional[Dict] = None) -> List[str]:
        """Detect which domain(s) a query relates to. Returns list of domain ids sorted by relevance."""
        scores = self._score_domains(query, context)
        relevant = [(d, s) for d, s in scores.items() if s > 0]
        relevant.sort(key=lambda x: x[1], reverse=True)
        if not relevant:
            return ["unknown"]
        return [d for d, _ in relevant]

    def detect_domains_with_scores(self, query: str, context: Optional[Dict] = None) -> List[Tuple[str, float]]:
        """Detect domain(s) with scores. Returns list of (domain_id, score) sorted by relevance."""
        scores = self._score_domains(query, context)
        relevant = [(d, s) for d, s in scores.items() if s > 0]
        relevant.sort(key=lambda x: x[1], reverse=True)
        if not relevant:
            return [("unknown", 0.0)]
        return relevant

    def record_successful_detection(self, query: str, detected_domains: List[str], user_accepted: bool = True):
        """
        Record successful (or unsuccessful) domain detection for pattern learning (Use Case 2).
        
        Args:
            query: User query that triggered detection
            detected_domains: Domains detected by system
            user_accepted: True if user accepted, False if user corrected domain
        """
        if not self._pattern_learner:
            return
        
        domain_names = [d for d in detected_domains if (d or "").strip().lower() not in ("", "unknown")]
        if not domain_names:
            return
        for domain_name in domain_names:
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
    
    def _boost_domains_by_technology(self, technologies: List[str]) -> Dict[str, float]:
        """
        Boost domains whose patterns match mentioned technologies.
        Returns Dict[domain_id, boost] (0-0.3).
        """
        boosts: Dict[str, float] = {}
        
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
        
        for domain_id, domain in self._domains_by_id.items():
            domain_boost = 0.0
            matched_techs = []
            for tech in technologies:
                extensions = tech_to_extensions.get(tech, [])
                for pattern in domain.patterns:
                    pattern_lower = (pattern or "").lower()
                    for ext in extensions:
                        if ext in pattern_lower or pattern_lower.replace("*", "") == ext:
                            domain_boost += 0.2
                            matched_techs.append(tech)
                            break
            if domain_boost > 0:
                boosts[domain_id] = min(domain_boost, 0.3)
                logger.info(f"🔧 Technology boost for {domain_id}: +{boosts[domain_id]:.2f} (matched: {', '.join(matched_techs)})")
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
    
    def _boost_domains_by_intent(self, intents: List[str]) -> Dict[str, float]:
        """Boost domains by detected intent. Returns Dict[domain_id, boost] (0-0.25)."""
        boosts: Dict[str, float] = {}
        
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
        
        for domain_id, domain in self._domains_by_id.items():
            domain_boost = 0.0
            matched_intents = []
            domain_keywords_lower = [ (kw or "").lower() for kw in domain.keywords ]
            domain_desc_lower = (domain.description or "").lower()
            for intent in intents:
                indicators = intent_domain_indicators.get(intent, [])
                for indicator in indicators:
                    if any(indicator in kw for kw in domain_keywords_lower) or indicator in domain_desc_lower:
                        domain_boost += 0.15
                        matched_intents.append(intent)
                        break
            if domain_boost > 0:
                boosts[domain_id] = min(domain_boost, 0.25)
                logger.info(f"💡 Intent boost for {domain_id}: +{boosts[domain_id]:.2f} (matched: {', '.join(matched_intents)})")
        return boosts
    
    def _score_domains(self, query: str, context: Optional[Dict] = None) -> Dict[str, float]:
        """Score all domains for a query. Returns Dict[domain_id, score]."""
        scores: Dict[str, float] = {}
        for domain_id, domain in self._domains_by_id.items():
            score = domain.matches_content(query)
            if context:
                if "file_path" in context:
                    path = Path(context["file_path"])
                    if domain.matches_path(path) or domain.matches_filename(path.name):
                        score += 0.5
                if "file_content" in context:
                    score += domain.matches_content(context["file_content"]) * 0.3
            scores[domain_id] = score
        technologies = self._extract_technologies_from_query(query)
        if technologies:
            for did, boost in self._boost_domains_by_technology(technologies).items():
                if did in scores:
                    scores[did] += boost
        intents = self._detect_query_intent(query)
        if intents:
            for did, boost in self._boost_domains_by_intent(intents).items():
                if did in scores:
                    scores[did] += boost
        if getattr(self, "_pattern_learner", None):
            for did, boost in self._get_pattern_domain_boosts(query).items():
                if did in scores and boost > 0.05:
                    scores[did] += boost
        return scores

    def get_domain_prompt(self, domains: List[str], include_cross_domain: bool = False) -> str:
        """Generate a system prompt section for the detected domains (by id)."""
        if not domains or set((d or "").strip().lower() for d in domains) <= {""} | {"unknown"}:
            return ""
        domain_descriptions = []
        for domain_id in domains[:3]:
            domain_id = (domain_id or "").strip().lower()
            if not domain_id or domain_id == "unknown":
                continue
            domain = self._domains_by_id.get(domain_id)
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
        domain_ids: List[str],
        preserve_secondary: bool = True
    ) -> List[Dict]:
        """Filter search results to prefer domain-relevant sources (domain_ids in priority order)."""
        validated = [d for d in domain_ids if (d or "").strip().lower() and (d or "").strip().lower() != "unknown"]
        if not validated:
            return sources
        scored = []
        for source in sources:
            score = 0
            path = Path(source.get("filepath", ""))
            content = source.get("content", "")
            for idx, domain_id in enumerate(validated):
                domain = self._domains_by_id.get((domain_id or "").strip().lower())
                if domain:
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

    def get_cross_domain_connections(self, domain_ids: List[str]) -> str:
        """Suggest potential cross-domain connections (domain_ids as strings)."""
        validated = [(d or "").strip().lower() for d in domain_ids if (d or "").strip().lower() and (d or "").strip().lower() != "unknown"]
        if len(validated) < 2:
            return ""
        connections: Dict[Tuple[str, str], str] = {
            ("sigils", "signals"): "Code patterns that could enhance audio work, or audio concepts that inform system design",
            ("sigils", "scrolls"): "Documentation patterns, writing about technical concepts, or teaching code through narrative",
            ("sigils", "glyphs"): "UI/UX implementation, design systems in code, or visual debugging tools",
            ("sigils", "grids"): "Architectural patterns, systems design, or infrastructure as frameworks",
            ("signals", "scrolls"): "Writing about sound, audio pedagogy, or documenting musical processes",
            ("signals", "glyphs"): "Visual representations of audio, audio-visual synthesis, or interface design for instruments",
            ("signals", "grids"): "Audio as a lens for understanding systems, systems thinking applied to sound design, or compositional frameworks",
            ("scrolls", "glyphs"): "Visual essays, information design for writing, or designed learning experiences",
            ("scrolls", "grids"): "Writing that explores systems thinking, frameworks for pedagogy, or meta-cognitive documentation",
            ("glyphs", "grids"): "Design frameworks, visual systems thinking, or interface patterns for complex systems",
        }
        suggestions = []
        for i, d1 in enumerate(validated):
            for d2 in validated[i + 1 :]:
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


# Domain-specific system prompt templates (keyed by domain id)
DOMAIN_PROMPTS: Dict[str, str] = {
    "sigils": """
When discussing code and infrastructure:
- Emphasize clean architecture and maintainability
- Consider Docker/container patterns when relevant
- Reference existing code patterns in the knowledge base
- Suggest automation where appropriate
""",
    "signals": """
When discussing audio programming:
- Emphasize instruments over tracks (generative over fixed)
- Consider real-time constraints and performance
- Reference norns/SuperCollider patterns when relevant
- Think in terms of constraint-based composition
""",
    "scrolls": """
When discussing writing and pedagogy:
- Use problem-posing over answer-giving approaches
- Reference Freire and popular education principles
- Consider the reader's learning journey
- Connect ideas across domains when relevant
""",
    "glyphs": """
When discussing visual work:
- Consider both aesthetic and functional aspects
- Think about the user's visual journey
- Reference design principles in the knowledge base
""",
    "grids": """
When discussing systems and frameworks:
- Think in terms of infinite vs finite games
- Consider emergence and feedback loops
- Look for patterns that apply across domains
- Emphasize continuation over completion
""",
}
