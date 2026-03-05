"""
Apollo Pattern Learner
Discovers and tracks recurring patterns in your work over time

This module learns from:
- Your queries and how you phrase things
- Patterns in your code across projects
- Recurring themes in your notes
- Cross-domain connections you make
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple, Union
from collections import Counter, defaultdict
import json
import re
import logging

logger = logging.getLogger(__name__)


# ==================== Phase 13A: Technical Terms & Stopwords ====================
# These lists are used for spaCy concept extraction (Days 3-4)

# Technical terms whitelist (500+ terms) - preserve these during concept extraction
TECHNICAL_TERMS = {
    # Programming Languages
    'python', 'javascript', 'typescript', 'java', 'cpp', 'csharp', 'go', 'rust', 
    'ruby', 'php', 'swift', 'kotlin', 'scala', 'perl', 'bash', 'shell', 'sql',
    'html', 'css', 'jsx', 'tsx', 'graphql', 'yaml', 'json', 'xml', 'markdown',
    
    # Frameworks & Libraries
    'react', 'vue', 'angular', 'svelte', 'nextjs', 'nuxt', 'gatsby', 'remix',
    'django', 'flask', 'fastapi', 'express', 'nestjs', 'spring', 'rails',
    'laravel', 'symfony', 'aspnet', 'dotnet', 'jquery', 'bootstrap', 'tailwind',
    'pytorch', 'tensorflow', 'keras', 'scikit', 'pandas', 'numpy', 'matplotlib',
    
    # Tools & Platforms
    'docker', 'kubernetes', 'k8s', 'terraform', 'ansible', 'jenkins', 'github',
    'gitlab', 'bitbucket', 'vscode', 'vim', 'emacs', 'intellij', 'pycharm',
    'webpack', 'vite', 'rollup', 'babel', 'eslint', 'prettier', 'jest', 'pytest',
    'npm', 'yarn', 'pnpm', 'pip', 'conda', 'poetry', 'cargo', 'gradle', 'maven',
    
    # Databases
    'postgres', 'postgresql', 'mysql', 'mariadb', 'sqlite', 'mongodb', 'redis',
    'elasticsearch', 'cassandra', 'dynamodb', 'firestore', 'supabase', 'prisma',
    
    # Cloud & Infrastructure
    'aws', 'azure', 'gcp', 'heroku', 'vercel', 'netlify', 'cloudflare', 'lambda',
    's3', 'ec2', 'rds', 'cloudfront', 'route53', 'vpc', 'iam', 'cognito',
    
    # Concepts - Architecture
    'api', 'rest', 'restful', 'graphql', 'grpc', 'websocket', 'microservice',
    'monolith', 'serverless', 'backend', 'frontend', 'fullstack', 'middleware',
    'authentication', 'authorization', 'oauth', 'jwt', 'session', 'cookie',
    'cors', 'csrf', 'xss', 'sql-injection', 'encryption', 'hashing', 'ssl', 'tls',
    
    # Concepts - Programming
    'class', 'function', 'method', 'variable', 'constant', 'array', 'list',
    'dictionary', 'hashmap', 'set', 'tuple', 'struct', 'enum', 'interface',
    'inheritance', 'polymorphism', 'encapsulation', 'abstraction', 'callback',
    'promise', 'async', 'await', 'coroutine', 'thread', 'process', 'concurrency',
    'parallelism', 'mutex', 'semaphore', 'deadlock', 'race-condition',
    
    # Concepts - Data Structures & Algorithms
    'linkedlist', 'tree', 'binary-tree', 'bst', 'heap', 'graph', 'stack', 'queue',
    'hashtable', 'trie', 'sorting', 'searching', 'recursion', 'iteration',
    'dynamic-programming', 'greedy', 'backtracking', 'bfs', 'dfs', 'dijkstra',
    
    # Concepts - Design Patterns
    'singleton', 'factory', 'observer', 'decorator', 'adapter', 'facade',
    'strategy', 'command', 'state', 'proxy', 'mvc', 'mvvm', 'redux', 'flux',
    
    # Concepts - Testing
    'unittest', 'integration-test', 'e2e', 'tdd', 'bdd', 'mock', 'stub', 'spy',
    'fixture', 'assertion', 'coverage', 'ci', 'cd', 'pipeline', 'deployment',
    
    # Concepts - DevOps
    'container', 'orchestration', 'scaling', 'load-balancer', 'reverse-proxy',
    'caching', 'cdn', 'monitoring', 'logging', 'tracing', 'metrics', 'alerting',
    
    # Concepts - Web
    'http', 'https', 'url', 'uri', 'endpoint', 'route', 'middleware', 'request',
    'response', 'status-code', 'header', 'body', 'query-param', 'path-param',
    'dom', 'virtual-dom', 'ssr', 'csr', 'ssg', 'spa', 'pwa', 'seo',
    
    # Concepts - Data & ML
    'dataset', 'training', 'validation', 'testing', 'model', 'neural-network',
    'cnn', 'rnn', 'lstm', 'transformer', 'bert', 'gpt', 'embedding', 'vector',
    'classification', 'regression', 'clustering', 'supervised', 'unsupervised',
    'reinforcement-learning', 'feature-engineering', 'hyperparameter', 'epoch',
    
    # Concepts - Database
    'schema', 'table', 'column', 'row', 'index', 'foreign-key', 'primary-key',
    'constraint', 'transaction', 'acid', 'normalization', 'denormalization',
    'query', 'join', 'subquery', 'view', 'stored-procedure', 'trigger',
    
    # File Types & Formats
    'csv', 'tsv', 'parquet', 'avro', 'protobuf', 'msgpack', 'toml', 'ini',
    'dockerfile', 'makefile', 'requirements', 'package', 'manifest',
    
    # Protocols & Standards
    'tcp', 'udp', 'ip', 'dns', 'smtp', 'ftp', 'ssh', 'http2', 'http3', 'quic',
    'json-rpc', 'soap', 'wsdl', 'openapi', 'swagger', 'oauth2', 'saml',
    
    # Version Control
    'git', 'commit', 'branch', 'merge', 'rebase', 'pull-request', 'fork', 'clone',
    'push', 'pull', 'fetch', 'checkout', 'stash', 'tag', 'release',
    
    # Common Commands
    'install', 'uninstall', 'update', 'upgrade', 'build', 'compile', 'deploy',
    'migrate', 'seed', 'lint', 'format', 'test', 'run', 'start', 'stop', 'restart',
    
    # Error Types
    'exception', 'error', 'warning', 'traceback', 'stacktrace', 'bug', 'issue',
    'nullpointer', 'indexerror', 'keyerror', 'typeerror', 'valueerror', 'timeout',
    
    # Performance
    'optimize', 'performance', 'latency', 'throughput', 'bottleneck', 'profiling',
    'benchmark', 'cache-hit', 'cache-miss', 'memory-leak', 'cpu-bound', 'io-bound',
    
    # Security
    'vulnerability', 'exploit', 'malware', 'phishing', 'firewall', 'vpn',
    'penetration-test', 'audit', 'compliance', 'gdpr', 'hipaa', 'pci-dss',
    
    # Mobile
    'ios', 'android', 'react-native', 'flutter', 'xamarin', 'cordova', 'ionic',
    'mobile-first', 'responsive', 'adaptive', 'touch', 'gesture', 'notification',
    
    # AI/ML Tools
    'huggingface', 'langchain', 'openai', 'anthropic', 'cohere', 'replicate',
    'wandb', 'mlflow', 'airflow', 'dbt', 'dagster', 'prefect',
    
    # Package Managers
    'homebrew', 'apt', 'yum', 'dnf', 'pacman', 'choco', 'winget', 'scoop',
    
    # Shell/Terminal
    'bash', 'zsh', 'fish', 'powershell', 'cmd', 'terminal', 'console', 'cli',
    'stdout', 'stderr', 'stdin', 'pipe', 'redirect', 'alias', 'environment',
    
    # Additional Programming Concepts
    'lambda', 'closure', 'generator', 'iterator', 'decorator', 'annotation',
    'reflection', 'metaprogramming', 'serialization', 'deserialization',
    'immutable', 'mutable', 'stateless', 'stateful', 'idempotent', 'atomic',
}

# Extended stopwords list (700+ words) - filter these out during concept extraction
STOPWORDS = {
    # Common English stopwords
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your',
    'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she',
    'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their',
    'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that',
    'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an',
    'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of',
    'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through',
    'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
    'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then',
    'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'both',
    'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will',
    'just', 'don', 'should', 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain',
    'aren', 'couldn', 'didn', 'doesn', 'hadn', 'hasn', 'haven', 'isn', 'ma',
    'mightn', 'mustn', 'needn', 'shan', 'shouldn', 'wasn', 'weren', 'won', 'wouldn',
    
    # Question words
    'would', 'could', 'should', 'might', 'must', 'shall', 'may', 'ought',
    
    # Common verbs
    'get', 'got', 'getting', 'make', 'making', 'made', 'take', 'taking', 'took',
    'give', 'giving', 'gave', 'put', 'putting', 'go', 'going', 'went', 'gone',
    'come', 'coming', 'came', 'see', 'seeing', 'saw', 'seen', 'know', 'knowing',
    'knew', 'known', 'think', 'thinking', 'thought', 'say', 'saying', 'said',
    'tell', 'telling', 'told', 'find', 'finding', 'found', 'want', 'wanting',
    'wanted', 'need', 'needing', 'needed', 'try', 'trying', 'tried', 'use',
    'using', 'used', 'work', 'working', 'worked', 'call', 'calling', 'called',
    'ask', 'asking', 'asked', 'feel', 'feeling', 'felt', 'become', 'becoming',
    'became', 'leave', 'leaving', 'left', 'mean', 'meaning', 'meant', 'keep',
    'keeping', 'kept', 'let', 'letting', 'begin', 'beginning', 'began', 'begun',
    'seem', 'seeming', 'seemed', 'help', 'helping', 'helped', 'show', 'showing',
    'showed', 'shown', 'hear', 'hearing', 'heard', 'play', 'playing', 'played',
    'run', 'running', 'ran', 'move', 'moving', 'moved', 'live', 'living', 'lived',
    'believe', 'believing', 'believed', 'bring', 'bringing', 'brought', 'happen',
    'happening', 'happened', 'write', 'writing', 'wrote', 'written', 'provide',
    'providing', 'provided', 'sit', 'sitting', 'sat', 'stand', 'standing', 'stood',
    'lose', 'losing', 'lost', 'pay', 'paying', 'paid', 'meet', 'meeting', 'met',
    'include', 'including', 'included', 'continue', 'continuing', 'continued',
    'set', 'setting', 'learn', 'learning', 'learned', 'learnt', 'change',
    'changing', 'changed', 'lead', 'leading', 'led', 'understand', 'understanding',
    'understood', 'watch', 'watching', 'watched', 'follow', 'following', 'followed',
    'stop', 'stopping', 'stopped', 'create', 'creating', 'created', 'speak',
    'speaking', 'spoke', 'spoken', 'read', 'reading', 'allow', 'allowing',
    'allowed', 'add', 'adding', 'added', 'spend', 'spending', 'spent', 'grow',
    'growing', 'grew', 'grown', 'open', 'opening', 'opened', 'walk', 'walking',
    'walked', 'win', 'winning', 'won', 'offer', 'offering', 'offered', 'remember',
    'remembering', 'remembered', 'love', 'loving', 'loved', 'consider',
    'considering', 'considered', 'appear', 'appearing', 'appeared', 'buy',
    'buying', 'bought', 'wait', 'waiting', 'waited', 'serve', 'serving', 'served',
    'die', 'dying', 'died', 'send', 'sending', 'sent', 'expect', 'expecting',
    'expected', 'build', 'building', 'built', 'stay', 'staying', 'stayed',
    'fall', 'falling', 'fell', 'fallen', 'cut', 'cutting', 'reach', 'reaching',
    'reached', 'kill', 'killing', 'killed', 'remain', 'remaining', 'remained',
    'suggest', 'suggesting', 'suggested', 'raise', 'raising', 'raised', 'pass',
    'passing', 'passed', 'sell', 'selling', 'sold', 'require', 'requiring',
    'required', 'report', 'reporting', 'reported', 'decide', 'deciding', 'decided',
    'pull', 'pulling', 'pulled',
    
    # Common adjectives
    'good', 'better', 'best', 'new', 'old', 'first', 'last', 'long', 'great',
    'little', 'own', 'other', 'next', 'small', 'large', 'different', 'big',
    'high', 'another', 'important', 'every', 'several', 'public', 'bad', 'same',
    'few', 'right', 'social', 'only', 'national', 'young', 'possible', 'early',
    'major', 'personal', 'late', 'hard', 'simple', 'easy', 'strong', 'certain',
    'clear', 'recent', 'real', 'full', 'sure', 'low', 'main', 'particular',
    'whole', 'general', 'common', 'poor', 'financial', 'international', 'available',
    'likely', 'short', 'single', 'medical', 'current', 'wrong', 'private',
    'difficult', 'black', 'white', 'legal', 'religious', 'final', 'military',
    'similar', 'political', 'western', 'democratic', 'special', 'entire', 'red',
    'primary', 'historical', 'heavy', 'fine', 'beautiful', 'economic', 'serious',
    'necessary', 'blue', 'deep', 'specific', 'human', 'local', 'significant',
    
    # Common nouns (non-technical)
    'time', 'person', 'year', 'way', 'day', 'thing', 'man', 'world', 'life',
    'hand', 'part', 'child', 'eye', 'woman', 'place', 'work', 'week', 'case',
    'point', 'government', 'company', 'number', 'group', 'problem', 'fact',
    'lot', 'right', 'study', 'book', 'water', 'word', 'business', 'issue',
    'side', 'kind', 'head', 'house', 'service', 'friend', 'father', 'power',
    'hour', 'game', 'line', 'end', 'member', 'law', 'car', 'city', 'community',
    'name', 'president', 'team', 'minute', 'idea', 'kid', 'body', 'information',
    'back', 'parent', 'face', 'others', 'level', 'office', 'door', 'health',
    'person', 'art', 'war', 'history', 'party', 'result', 'change', 'morning',
    'reason', 'research', 'girl', 'guy', 'moment', 'air', 'teacher', 'force',
    'education', 'foot', 'boy', 'age', 'policy', 'process', 'music', 'market',
    'sense', 'nation', 'plan', 'college', 'interest', 'death', 'experience',
    'effect', 'type', 'month', 'program', 'society', 'language', 'attention',
    'lawyer', 'family', 'tonight', 'effect', 'wife', 'tonight', 'film', 'image',
    
    # Filler words and discourse markers
    'actually', 'basically', 'really', 'literally', 'honestly', 'obviously',
    'clearly', 'essentially', 'generally', 'totally', 'absolutely', 'definitely',
    'probably', 'maybe', 'perhaps', 'somehow', 'somewhat', 'anyway', 'however',
    'therefore', 'thus', 'hence', 'moreover', 'furthermore', 'nevertheless',
    'nonetheless', 'meanwhile', 'otherwise', 'instead', 'besides', 'indeed',
    'certainly', 'surely', 'truly', 'frankly', 'specifically', 'particularly',
    
    # Question starters (keep minimal)
    'please', 'thanks', 'thank', 'hello', 'hi', 'hey', 'ok', 'okay', 'yes',
    'yeah', 'yep', 'nope', 'sorry', 'excuse', 'pardon',
    
    # Code-related common words (non-specific)
    'something', 'anything', 'nothing', 'everything', 'someone', 'anyone',
    'everyone', 'somewhere', 'anywhere', 'everywhere', 'somebody', 'anybody',
    'everybody', 'nobody',
    
    # Numbers (as words)
    'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine',
    'ten', 'eleven', 'twelve', 'twenty', 'thirty', 'forty', 'fifty', 'hundred',
    'thousand', 'million', 'billion', 'first', 'second', 'third', 'fourth',
    'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth',
    
    # Additional common words
    'today', 'tomorrow', 'yesterday', 'always', 'never', 'sometimes', 'often',
    'usually', 'rarely', 'seldom', 'frequently', 'occasionally', 'constantly',
    'already', 'still', 'yet', 'soon', 'later', 'earlier', 'ago', 'currently',
    'recently', 'lately', 'previously', 'formerly', 'nowadays', 'presently',
}


def _domains_to_strings(domains) -> List[str]:
    """Convert domains to list of strings, handling both DomainType enums and strings."""
    if not domains:
        return []
    
    result = []
    for d in domains:
        if hasattr(d, 'value'):  # DomainType enum
            result.append(d.value)
        elif isinstance(d, str):
            result.append(d)
        else:
            logger.warning(f"Unknown domain type: {type(d)}")
    return result


@dataclass
class Pattern:
    """A learned pattern from your work."""
    id: str
    name: str
    description: str
    pattern_type: str  # "code", "concept", "workflow", "cross_domain"
    domains: List[str]  # Which domains this pattern appears in
    examples: List[str]  # Concrete examples
    occurrences: int
    first_seen: datetime
    last_seen: datetime
    confidence: float  # 0-1, how confident we are this is a real pattern
    metadata: Dict = field(default_factory=dict)
    # Phase 13A Days 12-13: Track pattern usefulness
    times_used: int = 0  # How many times this pattern was used (e.g., for query expansion, RAG boosting)
    times_helpful: int = 0  # How many times it led to good results (user didn't rephrase/correct)


@dataclass
class QueryPattern:
    """A pattern in how you ask questions."""
    query_template: str  # e.g., "How do I {action} with {tool}?"
    common_fills: Dict[str, List[str]]  # What typically fills each slot
    frequency: int
    domains: List[str]


# ============================================================================
# Phase 13A: New Pattern Types for RAG Efficiency
# ============================================================================

@dataclass
class QueryChunkPattern:
    """
    Phase 13A: Pattern linking queries to successful chunks.
    
    Tracks which document chunks successfully answer queries, enabling:
    - 30-50% faster RAG by directly boosting known-good chunks
    - Pattern-based chunk scoring before semantic search
    - Learning which documents are most useful per query type
    """
    pattern_id: str  # e.g., "query_chunk_docker_python"
    query_template: str  # e.g., "How do I use {tool} with {language}?"
    query_signature: str  # Normalized query for matching
    successful_chunks: List[Dict]  # [{chunk_id, collection, hit_count, avg_score}]
    total_queries: int  # How many times this query pattern was used
    confidence: float  # 0-1, based on consistency of chunk hits
    first_seen: datetime
    last_seen: datetime
    metadata: Dict = field(default_factory=dict)


@dataclass
class DomainPriorityPattern:
    """
    Phase 13A: Pattern tracking collection priorities per domain.
    
    Learns which RAG collections are relevant for each domain, enabling:
    - 20-40% faster RAG by skipping irrelevant collections
    - Dynamic collection weights (e.g., signals domain → 80% norns, 20% github)
    - Automatic pruning of low-value collections per query
    """
    pattern_id: str  # e.g., "domain_priority_signals"
    domain: str  # e.g., "signals"
    collection_weights: Dict[str, float]  # {collection_name: weight 0-1}
    collection_stats: Dict[str, Dict]  # {collection: {queries, hits, avg_score}}
    total_queries: int  # Queries in this domain
    confidence: float  # Based on number of queries
    first_seen: datetime
    last_seen: datetime
    metadata: Dict = field(default_factory=dict)


@dataclass
class ProjectWorkflowPattern:
    """
    Phase 13A: Pattern for project-specific workflows.
    
    Learns build/deploy/test workflows per project, enabling:
    - Autonomous task execution (Phase 3)
    - Remembering project-specific commands
    - Troubleshooting common failures
    """
    pattern_id: str  # e.g., "workflow_bees_build"
    project_path: str  # e.g., "/Users/brett/bees"
    domain: str  # e.g., "signals"
    workflow_type: str  # "build", "deploy", "test", "run"
    command_sequence: List[Dict]  # [{step, command, description}]
    prerequisites: List[str]  # ["colima running", "env vars set"]
    common_failures: List[Dict]  # [{error_pattern, fix, success_count}]
    learned_from: int  # Number of successful executions observed
    last_success: datetime
    confidence: float
    metadata: Dict = field(default_factory=dict)


class PatternLearner:
    """
    Learns patterns from your interactions and knowledge base.

    Discovers:
    - Code patterns you use repeatedly
    - Conceptual patterns in your thinking
    - Query patterns in how you ask questions
    - Cross-domain connections you make
    """

    def __init__(self, storage_path: Path, min_occurrences: int = 3):
        self.storage_path = Path(storage_path).expanduser()  # Fix path expansion
        self.min_occurrences = min_occurrences

        # Create storage directory if it doesn't exist
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # In-memory pattern storage (v1.0 - legacy)
        self.patterns: Dict[str, Pattern] = {}
        self.query_patterns: Dict[str, QueryPattern] = {}

        # Phase 13A: New pattern storage (v2.0)
        self.query_chunk_patterns: Dict[str, QueryChunkPattern] = {}
        self.domain_priority_patterns: Dict[str, DomainPriorityPattern] = {}
        self.project_workflow_patterns: Dict[str, ProjectWorkflowPattern] = {}

        # Tracking for pattern discovery
        self.query_history: List[Dict] = []
        self.code_snippets: List[Dict] = []
        self.concept_mentions: Counter = Counter()
        self.cross_domain_pairs: Counter = Counter()

        # Phase 13A: Initialize spaCy for concept extraction (Days 3-4)
        try:
            import spacy
            self.nlp = spacy.load('en_core_web_sm')
            logger.info("spaCy loaded successfully for concept extraction")
        except Exception as e:
            logger.warning(f"spaCy not available: {e}. Concept extraction will be limited.")
            self.nlp = None

        # Load existing patterns
        self._load_patterns()
        
        # Initialize empty storage if doesn't exist
        if not self.storage_path.exists():
            self.storage_path.write_text(json.dumps({
                'patterns': [],
                'query_patterns': [],
                'query_history': [],
                'query_chunk_patterns': [],  # Phase 13A
                'domain_priority_patterns': [],  # Phase 13A
                'project_workflow_patterns': [],  # Phase 13A
                'metadata': {
                    'created': datetime.now().isoformat(),
                    'version': '2.0'
                }
            }, indent=2))
            logger.info(f"Initialized pattern storage v2.0 at {self.storage_path}")

    def _load_patterns(self):
        """Load patterns from storage."""
        if self.storage_path.exists():
            try:
                data = json.loads(self.storage_path.read_text())

                for p in data.get('patterns', []):
                    pattern = Pattern(
                        id=p['id'],
                        name=p['name'],
                        description=p['description'],
                        pattern_type=p['pattern_type'],
                        domains=p['domains'],
                        examples=p['examples'],
                        occurrences=p['occurrences'],
                        first_seen=datetime.fromisoformat(p['first_seen']),
                        last_seen=datetime.fromisoformat(p['last_seen']),
                        confidence=p['confidence'],
                        metadata=p.get('metadata', {}),
                        # Phase 13A Days 12-13: Load usefulness tracking
                        times_used=p.get('times_used', 0),
                        times_helpful=p.get('times_helpful', 0)
                    )
                    self.patterns[pattern.id] = pattern

                for qp in data.get('query_patterns', []):
                    self.query_patterns[qp['query_template']] = QueryPattern(
                        query_template=qp['query_template'],
                        common_fills=qp['common_fills'],
                        frequency=qp['frequency'],
                        domains=qp['domains']
                    )

                self.query_history = data.get('query_history', [])[-1000:]  # Keep last 1000

                # Phase 13A: Load new pattern types
                for qcp in data.get('query_chunk_patterns', []):
                    pattern = QueryChunkPattern(
                        pattern_id=qcp['pattern_id'],
                        query_template=qcp['query_template'],
                        query_signature=qcp['query_signature'],
                        successful_chunks=qcp['successful_chunks'],
                        total_queries=qcp['total_queries'],
                        confidence=qcp['confidence'],
                        first_seen=datetime.fromisoformat(qcp['first_seen']),
                        last_seen=datetime.fromisoformat(qcp['last_seen']),
                        metadata=qcp.get('metadata', {})
                    )
                    self.query_chunk_patterns[pattern.pattern_id] = pattern

                for dpp in data.get('domain_priority_patterns', []):
                    pattern = DomainPriorityPattern(
                        pattern_id=dpp['pattern_id'],
                        domain=dpp['domain'],
                        collection_weights=dpp['collection_weights'],
                        collection_stats=dpp['collection_stats'],
                        total_queries=dpp['total_queries'],
                        confidence=dpp['confidence'],
                        first_seen=datetime.fromisoformat(dpp['first_seen']),
                        last_seen=datetime.fromisoformat(dpp['last_seen']),
                        metadata=dpp.get('metadata', {})
                    )
                    self.domain_priority_patterns[pattern.pattern_id] = pattern

                for pwp in data.get('project_workflow_patterns', []):
                    pattern = ProjectWorkflowPattern(
                        pattern_id=pwp['pattern_id'],
                        project_path=pwp['project_path'],
                        domain=pwp['domain'],
                        workflow_type=pwp['workflow_type'],
                        command_sequence=pwp['command_sequence'],
                        prerequisites=pwp['prerequisites'],
                        common_failures=pwp['common_failures'],
                        learned_from=pwp['learned_from'],
                        last_success=datetime.fromisoformat(pwp['last_success']),
                        confidence=pwp['confidence'],
                        metadata=pwp.get('metadata', {})
                    )
                    self.project_workflow_patterns[pattern.pattern_id] = pattern

                logger.info(f"Loaded {len(self.patterns)} legacy patterns, "
                           f"{len(self.query_chunk_patterns)} query→chunk patterns, "
                           f"{len(self.domain_priority_patterns)} domain priority patterns, "
                           f"{len(self.project_workflow_patterns)} workflow patterns")

            except Exception as e:
                logger.error(f"Error loading patterns: {e}")

    def save_patterns(self):
        """Save patterns to storage v2.0 with automatic pruning."""
        # Phase 13A Days 14-15: Prune before saving
        self.prune_low_quality_patterns()
        
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'patterns': [
                {
                    'id': p.id,
                    'name': p.name,
                    'description': p.description,
                    'pattern_type': p.pattern_type,
                    'domains': p.domains,
                    'examples': p.examples,
                    'occurrences': p.occurrences,
                    'first_seen': p.first_seen.isoformat(),
                    'last_seen': p.last_seen.isoformat(),
                    'confidence': p.confidence,
                    'metadata': p.metadata,
                    # Phase 13A Days 12-13: Save usefulness tracking
                    'times_used': p.times_used,
                    'times_helpful': p.times_helpful
                }
                for p in self.patterns.values()
            ],
            'query_patterns': [
                {
                    'query_template': qp.query_template,
                    'common_fills': qp.common_fills,
                    'frequency': qp.frequency,
                    'domains': qp.domains
                }
                for qp in self.query_patterns.values()
            ],
            'query_chunk_patterns': [
                {
                    'pattern_id': qcp.pattern_id,
                    'query_template': qcp.query_template,
                    'query_signature': qcp.query_signature,
                    'successful_chunks': qcp.successful_chunks,
                    'total_queries': qcp.total_queries,
                    'confidence': qcp.confidence,
                    'first_seen': qcp.first_seen.isoformat(),
                    'last_seen': qcp.last_seen.isoformat(),
                    'metadata': qcp.metadata
                }
                for qcp in self.query_chunk_patterns.values()
            ],
            'domain_priority_patterns': [
                {
                    'pattern_id': dpp.pattern_id,
                    'domain': dpp.domain,
                    'collection_weights': dpp.collection_weights,
                    'collection_stats': dpp.collection_stats,
                    'total_queries': dpp.total_queries,
                    'confidence': dpp.confidence,
                    'first_seen': dpp.first_seen.isoformat(),
                    'last_seen': dpp.last_seen.isoformat(),
                    'metadata': dpp.metadata
                }
                for dpp in self.domain_priority_patterns.values()
            ],
            'project_workflow_patterns': [
                {
                    'pattern_id': pwp.pattern_id,
                    'project_path': pwp.project_path,
                    'domain': pwp.domain,
                    'workflow_type': pwp.workflow_type,
                    'command_sequence': pwp.command_sequence,
                    'prerequisites': pwp.prerequisites,
                    'common_failures': pwp.common_failures,
                    'learned_from': pwp.learned_from,
                    'last_success': pwp.last_success.isoformat(),
                    'confidence': pwp.confidence,
                    'metadata': pwp.metadata
                }
                for pwp in self.project_workflow_patterns.values()
            ],
            'query_history': self.query_history[-1000:],
            'metadata': {
                'version': '2.0',
                'created': datetime.now().isoformat(),
                'pattern_counts': {
                    'legacy_patterns': len(self.patterns),
                    'query_chunk_patterns': len(self.query_chunk_patterns),
                    'domain_priority_patterns': len(self.domain_priority_patterns),
                    'project_workflow_patterns': len(self.project_workflow_patterns)
                }
            }
        }

        self.storage_path.write_text(json.dumps(data, indent=2))
        logger.info(f"Saved patterns v2.0: {len(self.patterns)} legacy, "
                   f"{len(self.query_chunk_patterns)} query→chunk, "
                   f"{len(self.domain_priority_patterns)} domain priority, "
                   f"{len(self.project_workflow_patterns)} workflow")
    
    def save_patterns_compressed(self, compressed_path: Optional[Path] = None):
        """
        Save patterns in compressed format using abbreviated keys.
        
        **Phase 2b: Pattern Storage Compression**
        
        Reduces pattern storage size by 3-5x using:
        - Abbreviated keys (qp, qcp, dpp, pwp)
        - Omitted zero values
        - Compact number representation
        
        Format mirrors conversation compression (Phase 11c).
        
        Args:
            compressed_path: Optional path for compressed file.
                           Defaults to patterns.json.compressed
        """
        if compressed_path is None:
            compressed_path = self.storage_path.with_suffix('.json.compressed')
        
        # Build compressed data structure with abbreviated keys
        compressed = {
            'v': '2.0',  # version
            'c': datetime.now().isoformat(),  # created
            
            # Legacy patterns (abbreviated)
            'p': [
                {
                    'id': p.id,
                    'n': p.name,  # name
                    'd': p.description[:100],  # description (truncated)
                    't': p.pattern_type,  # type
                    'dm': p.domains,  # domains
                    'o': p.occurrences,  # occurrences
                    'c': p.confidence,  # confidence
                    'fs': p.first_seen.isoformat(),  # first_seen
                    'ls': p.last_seen.isoformat(),  # last_seen
                }
                for p in self.patterns.values()
            ] if self.patterns else [],
            
            # Query patterns (abbreviated)
            'qp': [
                {
                    'qt': qp.query_template,  # query_template
                    'f': qp.frequency,  # frequency
                    'dm': qp.domains  # domains
                }
                for qp in self.query_patterns.values()
            ] if self.query_patterns else [],
            
            # Query→Chunk patterns (abbreviated, most important)
            'qcp': [
                {
                    'id': qcp.pattern_id,
                    'qt': qcp.query_template,  # query_template
                    'qs': qcp.query_signature,  # query_signature
                    'sc': [  # successful_chunks
                        {
                            'ci': c['chunk_id'],  # chunk_id (abbreviated)
                            'co': c['collection'],  # collection
                            'h': c['hit_count'],  # hit_count
                            's': round(c['avg_score'], 3)  # avg_score (rounded)
                        }
                        for c in qcp.successful_chunks[:10]  # Keep top 10
                    ],
                    'tq': qcp.total_queries,  # total_queries
                    'c': round(qcp.confidence, 3),  # confidence (rounded)
                    'fs': qcp.first_seen.isoformat(),  # first_seen
                    'ls': qcp.last_seen.isoformat()  # last_seen
                }
                for qcp in self.query_chunk_patterns.values()
            ] if self.query_chunk_patterns else [],
            
            # Domain priority patterns (abbreviated)
            'dpp': [
                {
                    'id': dpp.pattern_id,
                    'd': dpp.domain,  # domain
                    'w': {k: round(v, 3) for k, v in dpp.collection_weights.items() if v > 0.01},  # weights (omit near-zero)
                    'tq': dpp.total_queries,  # total_queries
                    'c': round(dpp.confidence, 3),  # confidence
                    'fs': dpp.first_seen.isoformat(),  # first_seen
                    'ls': dpp.last_seen.isoformat()  # last_seen
                }
                for dpp in self.domain_priority_patterns.values()
            ] if self.domain_priority_patterns else [],
            
            # Project workflow patterns (abbreviated)
            'pwp': [
                {
                    'id': pwp.pattern_id,
                    'pp': pwp.project_path,  # project_path
                    'd': pwp.domain,  # domain
                    'wt': pwp.workflow_type,  # workflow_type
                    'cs': pwp.command_sequence[:5],  # command_sequence (top 5)
                    'c': round(pwp.confidence, 3),  # confidence
                    'ls': pwp.last_success.isoformat()  # last_success
                }
                for pwp in self.project_workflow_patterns.values()
            ] if self.project_workflow_patterns else [],
            
            # Statistics
            's': {
                'p': len(self.patterns),  # patterns count
                'qp': len(self.query_patterns),  # query_patterns count
                'qcp': len(self.query_chunk_patterns),  # query_chunk_patterns count
                'dpp': len(self.domain_priority_patterns),  # domain_priority_patterns count
                'pwp': len(self.project_workflow_patterns)  # project_workflow_patterns count
            }
        }
        
        # Write compressed format (no indentation for max compression)
        compressed_path.write_text(json.dumps(compressed))
        
        # Calculate compression ratio
        original_size = len(json.dumps(self._get_full_data(), indent=2))
        compressed_size = len(json.dumps(compressed))
        ratio = original_size / compressed_size if compressed_size > 0 else 0
        
        logger.info(
            f"Saved compressed patterns: {original_size} → {compressed_size} bytes "
            f"({ratio:.1f}x compression)"
        )
        
        return {
            'original_size': original_size,
            'compressed_size': compressed_size,
            'ratio': ratio,
            'path': str(compressed_path)
        }
    
    def load_patterns_from_compressed(self, compressed_path: Optional[Path] = None):
        """
        Load patterns from compressed format.
        
        **Phase 2b: Pattern Storage Compression**
        
        Decompresses abbreviated format back to full pattern objects.
        
        Args:
            compressed_path: Optional path to compressed file.
                           Defaults to patterns.json.compressed
        """
        if compressed_path is None:
            compressed_path = self.storage_path.with_suffix('.json.compressed')
        
        if not compressed_path.exists():
            logger.warning(f"Compressed patterns file not found: {compressed_path}")
            return {
                'success': False,
                'error': 'File not found'
            }
        
        try:
            data = json.loads(compressed_path.read_text())
            
            # Clear existing patterns
            self.patterns = {}
            self.query_patterns = {}
            self.query_chunk_patterns = {}
            self.domain_priority_patterns = {}
            self.project_workflow_patterns = {}
            
            # Load legacy patterns
            for p in data.get('p', []):
                pattern = Pattern(
                    id=p['id'],
                    name=p['n'],
                    description=p['d'],
                    pattern_type=p['t'],
                    domains=p['dm'],
                    examples=[],  # Not stored in compressed format
                    occurrences=p['o'],
                    first_seen=datetime.fromisoformat(p['fs']),
                    last_seen=datetime.fromisoformat(p['ls']),
                    confidence=p['c'],
                    metadata={},
                    times_used=0,
                    times_helpful=0
                )
                self.patterns[pattern.id] = pattern
            
            # Load query patterns
            for qp in data.get('qp', []):
                self.query_patterns[qp['qt']] = QueryPattern(
                    query_template=qp['qt'],
                    common_fills={},  # Not stored in compressed format
                    frequency=qp['f'],
                    domains=qp['dm']
                )
            
            # Load query→chunk patterns (most important)
            for qcp in data.get('qcp', []):
                pattern = QueryChunkPattern(
                    pattern_id=qcp['id'],
                    query_template=qcp['qt'],
                    query_signature=qcp['qs'],
                    successful_chunks=[
                        {
                            'chunk_id': c['ci'],
                            'collection': c['co'],
                            'hit_count': c['h'],
                            'avg_score': c['s']
                        }
                        for c in qcp['sc']
                    ],
                    total_queries=qcp['tq'],
                    confidence=qcp['c'],
                    first_seen=datetime.fromisoformat(qcp['fs']),
                    last_seen=datetime.fromisoformat(qcp['ls']),
                    metadata={}
                )
                self.query_chunk_patterns[pattern.pattern_id] = pattern
            
            # Load domain priority patterns
            for dpp in data.get('dpp', []):
                pattern = DomainPriorityPattern(
                    pattern_id=dpp['id'],
                    domain=dpp['d'],
                    collection_weights=dpp['w'],
                    collection_stats={},  # Rebuild on next use
                    total_queries=dpp['tq'],
                    confidence=dpp['c'],
                    first_seen=datetime.fromisoformat(dpp['fs']),
                    last_seen=datetime.fromisoformat(dpp['ls']),
                    metadata={}
                )
                self.domain_priority_patterns[pattern.pattern_id] = pattern
            
            # Load project workflow patterns
            for pwp in data.get('pwp', []):
                pattern = ProjectWorkflowPattern(
                    pattern_id=pwp['id'],
                    project_path=pwp['pp'],
                    domain=pwp['d'],
                    workflow_type=pwp['wt'],
                    command_sequence=pwp['cs'],
                    prerequisites=[],
                    common_failures=[],
                    learned_from=[],
                    last_success=datetime.fromisoformat(pwp['ls']),
                    confidence=pwp['c'],
                    metadata={}
                )
                self.project_workflow_patterns[pattern.pattern_id] = pattern
            
            stats = data.get('s', {})
            logger.info(
                f"Loaded compressed patterns: {stats.get('p', 0)} legacy, "
                f"{stats.get('qcp', 0)} query→chunk, "
                f"{stats.get('dpp', 0)} domain priority, "
                f"{stats.get('pwp', 0)} workflow"
            )
            
            return {
                'success': True,
                'file_size': compressed_path.stat().st_size,
                'patterns_loaded': sum([
                    len(self.patterns),
                    len(self.query_patterns),
                    len(self.query_chunk_patterns),
                    len(self.domain_priority_patterns),
                    len(self.project_workflow_patterns)
                ])
            }
            
        except Exception as e:
            logger.error(f"Failed to load compressed patterns: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_full_data(self) -> dict:
        """Helper to get full uncompressed data for comparison"""
        return {
            'patterns': [asdict(p) for p in self.patterns.values()],
            'query_patterns': [asdict(qp) for qp in self.query_patterns.values()],
            'query_chunk_patterns': [
                {
                    'pattern_id': qcp.pattern_id,
                    'query_template': qcp.query_template,
                    'query_signature': qcp.query_signature,
                    'successful_chunks': qcp.successful_chunks,
                    'total_queries': qcp.total_queries,
                    'confidence': qcp.confidence,
                    'first_seen': qcp.first_seen.isoformat(),
                    'last_seen': qcp.last_seen.isoformat(),
                    'metadata': qcp.metadata
                }
                for qcp in self.query_chunk_patterns.values()
            ],
            'domain_priority_patterns': [
                {
                    'pattern_id': dpp.pattern_id,
                    'domain': dpp.domain,
                    'collection_weights': dpp.collection_weights,
                    'collection_stats': dpp.collection_stats,
                    'total_queries': dpp.total_queries,
                    'confidence': dpp.confidence,
                    'first_seen': dpp.first_seen.isoformat(),
                    'last_seen': dpp.last_seen.isoformat(),
                    'metadata': dpp.metadata
                }
                for dpp in self.domain_priority_patterns.values()
            ],
            'project_workflow_patterns': []
        }

    # ==================== Pattern Creation Helpers ====================
    # These methods will be used by the core learning algorithms (Days 3-8)
    
    def create_or_update_query_chunk_pattern(
        self, 
        query_template: str, 
        query_signature: str,
        successful_chunk: Dict,
        domain: str = None
    ) -> QueryChunkPattern:
        """
        Create or update a QueryChunkPattern.
        
        Args:
            query_template: Template like "How do I {action} {thing}?"
            query_signature: Signature like "how_do_i_action_thing"
            successful_chunk: Dict with chunk_id, collection, score
            domain: Optional domain filter
            
        Returns:
            The created or updated pattern
        """
        pattern_id = f"qcp_{query_signature}"
        now = datetime.now()
        
        if pattern_id in self.query_chunk_patterns:
            pattern = self.query_chunk_patterns[pattern_id]
            pattern.total_queries += 1
            pattern.last_seen = now
            
            # Update or add chunk
            found = False
            for chunk in pattern.successful_chunks:
                if chunk['chunk_id'] == successful_chunk['chunk_id']:
                    chunk['hit_count'] += 1
                    chunk['avg_score'] = (
                        chunk['avg_score'] * (chunk['hit_count'] - 1) + successful_chunk['score']
                    ) / chunk['hit_count']
                    found = True
                    break
            
            if not found:
                pattern.successful_chunks.append({
                    'chunk_id': successful_chunk['chunk_id'],
                    'collection': successful_chunk['collection'],
                    'hit_count': 1,
                    'avg_score': successful_chunk['score']
                })
            
            # Recalculate confidence based on hit counts
            total_hits = sum(c['hit_count'] for c in pattern.successful_chunks)
            pattern.confidence = min(0.95, 0.5 + (total_hits / 100))
        else:
            pattern = QueryChunkPattern(
                pattern_id=pattern_id,
                query_template=query_template,
                query_signature=query_signature,
                successful_chunks=[{
                    'chunk_id': successful_chunk['chunk_id'],
                    'collection': successful_chunk['collection'],
                    'hit_count': 1,
                    'avg_score': successful_chunk['score']
                }],
                total_queries=1,
                confidence=0.5,
                first_seen=now,
                last_seen=now,
                metadata={'domain': domain} if domain else {}
            )
            self.query_chunk_patterns[pattern_id] = pattern
        
        return pattern
    
    def create_or_update_domain_priority_pattern(
        self,
        domain: str,
        collection: str,
        query_success: bool,
        score: float = 0.0
    ) -> DomainPriorityPattern:
        """
        Create or update a DomainPriorityPattern.
        
        Args:
            domain: Domain like "python", "docker", "react"
            collection: Collection name
            query_success: Whether the query was successful
            score: Relevance score (0.0-1.0)
            
        Returns:
            The created or updated pattern
        """
        pattern_id = f"dpp_{domain}"
        now = datetime.now()
        
        if pattern_id in self.domain_priority_patterns:
            pattern = self.domain_priority_patterns[pattern_id]
            pattern.total_queries += 1
            pattern.last_seen = now
            
            # Update collection stats
            if collection not in pattern.collection_stats:
                pattern.collection_stats[collection] = {'queries': 0, 'successes': 0, 'avg_score': 0.0}
            
            stats = pattern.collection_stats[collection]
            stats['queries'] += 1
            if query_success:
                stats['successes'] += 1
            stats['avg_score'] = (
                stats['avg_score'] * (stats['queries'] - 1) + score
            ) / stats['queries']
            
            # Recalculate collection weights based on success rate
            for coll, coll_stats in pattern.collection_stats.items():
                if coll_stats['queries'] > 0:
                    success_rate = coll_stats['successes'] / coll_stats['queries']
                    pattern.collection_weights[coll] = 0.5 + (success_rate * 1.5)  # Range: 0.5-2.0
            
            # Update confidence
            pattern.confidence = min(0.95, 0.3 + (pattern.total_queries / 200))
        else:
            pattern = DomainPriorityPattern(
                pattern_id=pattern_id,
                domain=domain,
                collection_weights={collection: 1.0},
                collection_stats={
                    collection: {
                        'queries': 1,
                        'successes': 1 if query_success else 0,
                        'avg_score': score
                    }
                },
                total_queries=1,
                confidence=0.3,
                first_seen=now,
                last_seen=now,
                metadata={}
            )
            self.domain_priority_patterns[pattern_id] = pattern
        
        return pattern
    
    def create_or_update_workflow_pattern(
        self,
        project_path: str,
        domain: str,
        workflow_type: str,
        command: str,
        success: bool,
        error: str = None,
        solution: str = None
    ) -> ProjectWorkflowPattern:
        """
        Create or update a ProjectWorkflowPattern.
        
        Args:
            project_path: Path to the project
            domain: Domain like "python", "nodejs"
            workflow_type: Type like "build", "test", "deploy"
            command: Command that was run
            success: Whether the command succeeded
            error: Error message if failed
            solution: Solution if known
            
        Returns:
            The created or updated pattern
        """
        pattern_id = f"pwp_{Path(project_path).name}_{workflow_type}"
        now = datetime.now()
        
        if pattern_id in self.project_workflow_patterns:
            pattern = self.project_workflow_patterns[pattern_id]
            pattern.learned_from += 1
            if success:
                pattern.last_success = now
            
            # Update command sequence
            found = False
            for cmd in pattern.command_sequence:
                if cmd['command'] == command:
                    cmd['total_runs'] = cmd.get('total_runs', 1) + 1
                    if success:
                        cmd['successes'] = cmd.get('successes', 0) + 1
                    cmd['success_rate'] = cmd['successes'] / cmd['total_runs']
                    found = True
                    break
            
            if not found:
                pattern.command_sequence.append({
                    'command': command,
                    'order': len(pattern.command_sequence) + 1,
                    'total_runs': 1,
                    'successes': 1 if success else 0,
                    'success_rate': 1.0 if success else 0.0
                })
            
            # Track failures
            if error and solution:
                failure_exists = any(f['error'] == error for f in pattern.common_failures)
                if not failure_exists:
                    pattern.common_failures.append({
                        'error': error,
                        'solution': solution,
                        'occurrences': 1
                    })
            
            # Update confidence
            total_successes = sum(cmd.get('successes', 0) for cmd in pattern.command_sequence)
            total_runs = sum(cmd.get('total_runs', 1) for cmd in pattern.command_sequence)
            pattern.confidence = total_successes / total_runs if total_runs > 0 else 0.5
        else:
            pattern = ProjectWorkflowPattern(
                pattern_id=pattern_id,
                project_path=project_path,
                domain=domain,
                workflow_type=workflow_type,
                command_sequence=[{
                    'command': command,
                    'order': 1,
                    'total_runs': 1,
                    'successes': 1 if success else 0,
                    'success_rate': 1.0 if success else 0.0
                }],
                prerequisites=[],
                common_failures=[],
                learned_from=1,
                last_success=now if success else datetime.min,
                confidence=0.5,
                metadata={}
            )
            self.project_workflow_patterns[pattern_id] = pattern
        
        return pattern

    def _extract_query_template(self, query: str) -> Tuple[str, Dict[str, str]]:
        """
        Extract a template from a query.
        
        Example:
          "How do I use Docker with Python?" 
          → "How do I use {tool} with {language}?"
          → fills: {"tool": "Docker", "language": "Python"}
        """
        # Detect question patterns
        patterns = [
            (r"how (?:do|can) i (\w+) (.+) with (.+)\?", "How do I {action} {thing} with {tool}?"),
            (r"how (?:do|can) i (\w+) (.+)\?", "How do I {action} {thing}?"),
            (r"what(?:'s| is) the (?:best|right) way to (\w+) (.+)\?", "What's the best way to {action} {thing}?"),
            (r"what(?:'s| is) the (?:best|right) way to (\w+)\?", "What's the best way to {action}?"),
            (r"can you (?:help me |)(\w+) (?:this|the|my) (.+)\?", "Can you {action} this {thing}?"),
            (r"show me (?:how to |)(\w+) (.+)", "Show me how to {action} {thing}"),
            (r"explain (?:how |)(.+) works?(?: in (.+))?", "Explain how {concept} works"),
            (r"explain (.+) in (.+)", "Explain {concept} in {context}"),
            (r"explain (.+)", "Explain {concept}"),
            (r"write (?:a|an) (.+) that (.+)", "Write a {thing} that {action}"),
            (r"write (?:a|an) (.+) for (.+)", "Write a {thing} for {purpose}"),
            (r"create (?:a|an) (.+) for (.+)", "Create a {thing} for {purpose}"),
            (r"create (?:a|an) (.+) that (.+)", "Create a {thing} that {action}"),
            (r"implement (.+) using (.+)", "Implement {feature} using {tool}"),
            (r"implement (.+) for (.+)", "Implement {feature} for {purpose}"),
            (r"debug (.+) in (.+)", "Debug {issue} in {context}"),
            (r"fix (.+) in (.+)", "Fix {issue} in {context}"),
            (r"set up (.+) for (.+)", "Set up {tool} for {purpose}"),
            (r"configure (.+) to (.+)", "Configure {tool} to {action}"),
            (r"what (?:is|are) (.+)\?", "What is {concept}?"),
            (r"why (?:is|does) (.+)\?", "Why does {concept}?"),
        ]
        
        query_lower = query.lower()
        
        for regex, template in patterns:
            match = re.search(regex, query_lower)
            if match:
                fills = {}
                groups = match.groups()
                
                # Extract placeholder names from template
                placeholders = re.findall(r'\{(\w+)\}', template)
                
                # Map captured groups to placeholders
                for i, (placeholder, value) in enumerate(zip(placeholders, groups)):
                    if value:  # Only add non-None values
                        fills[placeholder] = value.strip()
                
                return template, fills
        
        # No template found, return query as-is
        return query, {}

    def record_query(self, query: str, domains, response: Optional[str] = None):
        """Record a query for pattern analysis."""
        # Convert domains to strings
        domain_strs = _domains_to_strings(domains)
        
        # Extract template
        template, fills = self._extract_query_template(query)
        
        self.query_history.append({
            'query': query,
            'template': template,
            'fills': fills,
            'domains': domain_strs,
            'timestamp': datetime.now().isoformat(),
            'response_helpful': None  # Can be updated with feedback
        })

        # Analyze query for patterns
        self._analyze_query_patterns(query, domain_strs, template, fills)

        # Track cross-domain connections
        if len(domain_strs) > 1:
            for i, d1 in enumerate(domain_strs):
                for d2 in domain_strs[i+1:]:
                    pair = tuple(sorted([d1, d2]))
                    self.cross_domain_pairs[pair] += 1

    def _analyze_query_patterns(self, query: str, domains: List[str], template: str, fills: Dict[str, str]):
        """Analyze a query for recurring patterns using extracted template."""
        # If we found a template (template != query), track it
        if template != query and fills:
            # Use template as the key
            if template not in self.query_patterns:
                self.query_patterns[template] = QueryPattern(
                    query_template=template,
                    common_fills=defaultdict(list),
                    frequency=0,
                    domains=[]
                )
            
            qp = self.query_patterns[template]
            qp.frequency += 1
            qp.domains = list(set(qp.domains + domains))
            
            # Track what fills each slot
            for placeholder, value in fills.items():
                if value not in qp.common_fills[placeholder]:
                    qp.common_fills[placeholder].append(value)
                    # Keep only top 10 most common fills per placeholder
                    if len(qp.common_fills[placeholder]) > 10:
                        qp.common_fills[placeholder] = qp.common_fills[placeholder][-10:]

    def record_code_pattern(
        self,
        code: str,
        filepath: str,
        pattern_type: str,
        domains
    ):
        """Record a code snippet for pattern analysis."""
        # Convert domains to strings
        domain_strs = _domains_to_strings(domains)
        
        self.code_snippets.append({
            'code': code,
            'filepath': filepath,
            'pattern_type': pattern_type,
            'domains': domain_strs,
            'timestamp': datetime.now().isoformat()
        })

        # Analyze for patterns (simplified - would use AST in production)
        self._analyze_code_patterns(code, domain_strs)

    def _analyze_code_patterns(self, code: str, domains: List[str]):
        """Analyze code for recurring patterns."""
        # Look for common patterns

        patterns_to_detect = [
            {
                'id': 'error_handling',
                'regex': r'try\s*:.*except|\.catch\(|if err != nil',
                'name': 'Error Handling Pattern',
                'description': 'Consistent error handling approach'
            },
            {
                'id': 'async_pattern',
                'regex': r'async\s+(?:def|function)|await\s+',
                'name': 'Async/Await Pattern',
                'description': 'Asynchronous programming pattern'
            },
            {
                'id': 'factory_pattern',
                'regex': r'def\s+create_\w+|function\s+make\w+|fn\s+new_\w+',
                'name': 'Factory Pattern',
                'description': 'Object/instance creation pattern'
            },
            {
                'id': 'callback_pattern',
                'regex': r'on_\w+\s*=|\.on\(|callback\s*[=:]',
                'name': 'Callback Pattern',
                'description': 'Event-driven callback pattern'
            },
            {
                'id': 'midi_handling',
                'regex': r'midi_?\w*|note_?on|note_?off|cc_?\d*',
                'name': 'MIDI Handling Pattern',
                'description': 'MIDI event processing'
            },
            {
                'id': 'state_machine',
                'regex': r'state\s*=|set_?state|current_?state',
                'name': 'State Machine Pattern',
                'description': 'State management pattern'
            }
        ]

        for pattern_def in patterns_to_detect:
            if re.search(pattern_def['regex'], code, re.IGNORECASE):
                self._register_pattern_occurrence(
                    pattern_id=pattern_def['id'],
                    name=pattern_def['name'],
                    description=pattern_def['description'],
                    pattern_type='code',
                    domains=domains,
                    example=code[:200]
                )

    def _register_pattern_occurrence(
        self,
        pattern_id: str,
        name: str,
        description: str,
        pattern_type: str,
        domains: List[str],
        example: str
    ):
        """Register an occurrence of a pattern with decay for stale patterns."""
        now = datetime.now()

        if pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
            
            # NEW: Apply decay if not seen recently (Days 14-15)
            days_since = (now - pattern.last_seen).days
            if days_since > 60:
                # 2% decay per day after 60 days of inactivity
                decay = 0.98 ** (days_since - 60)
                old_confidence = pattern.confidence
                pattern.confidence *= decay
                
                if pattern.confidence < old_confidence * 0.9:  # Log significant decay
                    logger.debug(f"⏳ Applied decay to {pattern.name}: "
                               f"{old_confidence:.2f} → {pattern.confidence:.2f} "
                               f"({days_since} days inactive)")
            
            # Update pattern
            pattern.occurrences += 1
            pattern.last_seen = now
            pattern.domains = list(set(pattern.domains + domains))
            if example not in pattern.examples:
                pattern.examples.append(example)
                if len(pattern.examples) > 10:
                    pattern.examples = pattern.examples[-10:]
            
            # Recalculate confidence based on occurrences (after decay)
            # This allows patterns to recover if they become active again
            new_confidence = min(pattern.occurrences / 10, 1.0)
            if new_confidence > pattern.confidence:
                pattern.confidence = new_confidence
        else:
            self.patterns[pattern_id] = Pattern(
                id=pattern_id,
                name=name,
                description=description,
                pattern_type=pattern_type,
                domains=domains,
                examples=[example],
                occurrences=1,
                first_seen=now,
                last_seen=now,
                confidence=0.1
            )

    def get_relevant_patterns(
        self,
        query: str,
        domains,
        n_results: int = 5
    ) -> List[Pattern]:
        """Get patterns relevant to a query."""
        # Convert domains to strings
        domain_strs = _domains_to_strings(domains)
        
        scored_patterns = []

        query_lower = query.lower()

        for pattern in self.patterns.values():
            score = 0

            # Domain match
            domain_overlap = len(set(pattern.domains) & set(domain_strs))
            score += domain_overlap * 2

            # Keyword match
            if pattern.name.lower() in query_lower:
                score += 3
            if any(word in query_lower for word in pattern.description.lower().split()):
                score += 1

            # Confidence boost
            score += pattern.confidence

            # Recency boost
            days_since = (datetime.now() - pattern.last_seen).days
            recency_score = max(0, 1 - days_since / 30)  # Decay over 30 days
            score += recency_score

            if score > 0:
                scored_patterns.append((pattern, score))

        scored_patterns.sort(key=lambda x: x[1], reverse=True)
        return [p for p, _ in scored_patterns[:n_results]]

    def get_cross_domain_suggestions(self, domains) -> List[str]:
        """Suggest cross-domain connections based on learned patterns."""
        # Convert domains to strings
        domain_strs = _domains_to_strings(domains)
        
        suggestions = []

        for pair, count in self.cross_domain_pairs.most_common(10):
            if any(d in pair for d in domain_strs) and count >= self.min_occurrences:
                other_domain = pair[0] if pair[1] in domain_strs else pair[1]
                suggestions.append(
                    f"You often connect {pair[0]} and {pair[1]} - "
                    f"consider patterns from {other_domain}"
                )

        return suggestions[:3]

    def get_query_suggestions(self, partial_query: str) -> List[str]:
        """Suggest query completions based on learned patterns."""
        suggestions = []

        partial_lower = partial_query.lower()

        for template, qp in self.query_patterns.items():
            if qp.frequency >= self.min_occurrences:
                # Generate concrete suggestions from template
                suggestion = template
                for placeholder, fills in qp.common_fills.items():
                    if fills:
                        suggestion = suggestion.replace(
                            f"{{{placeholder}}}",
                            fills[0]  # Most common fill
                        )

                if partial_lower in suggestion.lower():
                    suggestions.append(suggestion)

        return suggestions[:5]

    def _infer_domains_from_concepts(self, concepts: List[str]) -> List[str]:
        """
        Infer which domains concepts belong to based on keywords.
        
        Now uses Phase 1.5 domain config for keywords.
        Falls back to hardcoded keywords if config not available.
        """
        # Try to load domain keywords from config
        try:
            from core.domain_config import load_domains
            config = load_domains()
            
            # Build keyword mapping from config
            domain_keywords = {}
            for domain in config.domains:
                domain_keywords[domain.id] = domain.auto_tag_rules
                
        except Exception:
            # Fallback to hardcoded keywords
            domain_keywords = {
                'sigils': [
                    'docker', 'python', 'rust', 'javascript', 'typescript', 'react', 'vue',
                    'node', 'npm', 'cargo', 'pip', 'code', 'function', 'class', 'api',
                    'server', 'client', 'database', 'redis', 'postgres', 'mongodb',
                    'git', 'github', 'testing', 'debug', 'refactor', 'deploy'
                ],
                'signals': [
                    'audio', 'sound', 'music', 'midi', 'supercollider', 'norns', 'monome',
                    'synthesis', 'synth', 'oscillator', 'filter', 'envelope', 'sample',
                    'sequencer', 'grid', 'arc', 'crow', 'modular', 'eurorack', 'dsp'
                ],
                'scrolls': [
                    'writing', 'essay', 'article', 'note', 'document', 'text', 'prose',
                    'pedagogy', 'teaching', 'learning', 'education', 'curriculum',
                    'knowledge', 'research', 'study', 'book', 'paper', 'thesis'
                ],
                'grids': [
                    'system', 'framework', 'model', 'architecture', 'structure', 'pattern',
                    'organization', 'workflow', 'process', 'method', 'approach', 'strategy',
                    'meta', 'theory', 'principle', 'concept', 'thinking', 'mental'
                ],
                'glyphs': [
                    'design', 'visual', 'ui', 'ux', 'interface', 'layout', 'typography',
                    'color', 'aesthetic', 'style', 'graphic', 'icon', 'logo', 'brand',
                    'canvas', 'draw', 'render', 'display', 'screen', 'pixel'
                ]
            }
        
        domains_found = set()
        concepts_lower = [c.lower() for c in concepts]
        
        for domain, keywords in domain_keywords.items():
            for concept in concepts_lower:
                if any(kw in concept for kw in keywords):
                    domains_found.add(domain)
                    break
        
        return list(domains_found) if domains_found else ['grids']  # Default to grids

    def learn_conceptual_patterns(
        self,
        conversation_id: str,
        messages: List[Dict[str, str]],
        category: Optional[str] = None
    ) -> int:
        """
        Learn patterns from how concepts are connected in conversations.
        
        Phase 13A Days 12-13: Enhanced with strict quality controls
        - min_occurrences: 7 (was 3) - requires stronger evidence
        - Minimum confidence for storage: 0.5
        - Cap at 200 patterns (prunes lowest quality)
        - Uses spaCy-based concept extraction
        
        Args:
            conversation_id: Unique ID for the conversation
            messages: List of message dicts with 'role' and 'content'
            category: Optional category/domain for the conversation
        
        Returns:
            Number of new patterns detected
        """
        # Extract all text content from messages
        text_content = []
        for msg in messages:
            if msg.get('content'):
                text_content.append(msg['content'])
        
        full_text = ' '.join(text_content)
        
        # Extract key concepts using spaCy (Days 3-4 enhancement)
        concepts = self._extract_concepts(full_text)
        
        if not concepts:
            logger.info(f"No concepts extracted from conversation {conversation_id}")
            return 0
        
        # Update concept mention counts
        for concept in concepts:
            self.concept_mentions[concept] += 1
        
        # Find concept pairs (concepts mentioned together)
        concept_pairs = []
        for i, c1 in enumerate(concepts):
            for c2 in concepts[i+1:]:
                if c1 != c2:
                    pair = tuple(sorted([c1, c2]))
                    concept_pairs.append(pair)
        
        patterns_created = 0
        
        # Phase 13A Days 12-13: Stricter threshold (7 instead of 3)
        MIN_OCCURRENCES_CONCEPTUAL = 7
        MINIMUM_CONFIDENCE = 0.5
        
        # Track concept pairs
        concept_pair_counter = Counter(concept_pairs)
        for pair, count in concept_pair_counter.items():
            # Get historical count
            total_count = self.concept_mentions.get(f"pair:{pair[0]}:{pair[1]}", 0) + count
            self.concept_mentions[f"pair:{pair[0]}:{pair[1]}"] = total_count
            
            # Phase 13A: Require 7 occurrences (was min_occurrences which is 3)
            if total_count >= MIN_OCCURRENCES_CONCEPTUAL:
                pattern_id = f"concept_pair_{pair[0]}_{pair[1]}"
                
                # Infer domains from concepts
                inferred_domains = self._infer_domains_from_concepts(list(pair))
                
                pattern_name = f"Conceptual Connection: {pair[0]} ↔ {pair[1]}"
                description = f"You frequently explore {pair[0]} and {pair[1]} together"
                
                now = datetime.now()
                
                # Phase 13A Days 12-13: Calculate confidence with higher baseline
                # Formula: min(total_count / (MIN_OCCURRENCES_CONCEPTUAL * 3), 1.0)
                # This means: 7 occurrences = 0.33, 14 occurrences = 0.67, 21+ = 1.0
                confidence = min(total_count / (MIN_OCCURRENCES_CONCEPTUAL * 3), 1.0)
                
                # Phase 13A Days 12-13: Only store/update if confidence >= 0.5
                if confidence < MINIMUM_CONFIDENCE:
                    logger.debug(f"Skipping low-confidence pattern {pair[0]}↔{pair[1]} "
                               f"(confidence={confidence:.2f}, need {MINIMUM_CONFIDENCE})")
                    continue
                
                if pattern_id in self.patterns:
                    # Update existing pattern
                    pattern = self.patterns[pattern_id]
                    pattern.occurrences += count
                    pattern.last_seen = now
                    pattern.confidence = confidence
                    # Merge domains
                    pattern.domains = list(set(pattern.domains + inferred_domains))
                else:
                    # Create new pattern
                    self.patterns[pattern_id] = Pattern(
                        id=pattern_id,
                        name=pattern_name,
                        description=description,
                        pattern_type='conceptual',
                        domains=inferred_domains,
                        examples=[f"Conversation {conversation_id}"],
                        occurrences=count,
                        first_seen=now,
                        last_seen=now,
                        confidence=confidence,
                        metadata={
                            'concept1': pair[0],
                            'concept2': pair[1],
                            'conversation_ids': [conversation_id]
                        }
                    )
                    patterns_created += 1
                    logger.info(f"Created conceptual pattern: {pattern_name} (confidence={confidence:.2f})")
        
        # Phase 13A Days 12-13: Prune to top 200 conceptual patterns after learning
        self._prune_conceptual_patterns()
        
        logger.info(
            f"Learned from conversation {conversation_id}: "
            f"{len(concepts)} concepts, {len(concept_pairs)} pairs, "
            f"{patterns_created} new patterns"
        )
        
        return patterns_created

    def _prune_conceptual_patterns(self):
        """
        Keep only top 200 conceptual patterns by quality.
        
        Phase 13A Days 12-13: Cap conceptual patterns at 200 to prevent bloat.
        Quality score = confidence × occurrences (balances both factors)
        """
        conceptual = [p for p in self.patterns.values() if p.pattern_type == 'conceptual']
        
        if len(conceptual) <= 200:
            logger.debug(f"Conceptual patterns ({len(conceptual)}) under limit (200), no pruning needed")
            return  # Under limit, no pruning needed
        
        # Sort by quality score: confidence × occurrences
        conceptual.sort(key=lambda p: p.confidence * p.occurrences, reverse=True)
        
        # Remove patterns beyond top 200
        pruned_count = 0
        for pattern in conceptual[200:]:
            del self.patterns[pattern.id]
            pruned_count += 1
            logger.info(f"Pruned low-quality conceptual pattern: {pattern.name} "
                       f"(confidence={pattern.confidence:.2f}, occurrences={pattern.occurrences}, "
                       f"quality={pattern.confidence * pattern.occurrences:.2f})")
        
        logger.info(f"Pruned {pruned_count} conceptual patterns, kept top 200")

    def _extract_concepts(self, text: str) -> List[str]:
        """
        Extract key concepts from text.
        
        Phase 13A Days 3-4: Now uses spaCy-based extraction for higher quality.
        Falls back to basic extraction if spaCy unavailable.
        
        Returns 10-15 high-quality concepts instead of 50+ garbage concepts.
        """
        # Use the new spaCy-powered extraction
        return self.extract_concepts_with_spacy(text)

    def generate_pattern_summary(self) -> str:
        """Generate a summary of learned patterns for system prompt."""
        if not self.patterns:
            return ""

        summary_parts = ["## Learned Patterns from Your Work\n"]

        # Group by pattern type
        by_type = defaultdict(list)
        for pattern in self.patterns.values():
            if pattern.confidence >= 0.3:  # Only confident patterns
                by_type[pattern.pattern_type].append(pattern)

        for pattern_type, patterns in by_type.items():
            if patterns:
                summary_parts.append(f"\n### {pattern_type.title()} Patterns\n")
                for p in sorted(patterns, key=lambda x: x.occurrences, reverse=True)[:5]:
                    summary_parts.append(f"- **{p.name}**: {p.description}")

        # Add cross-domain insights
        if self.cross_domain_pairs:
            summary_parts.append("\n### Cross-Domain Connections You Make\n")
            for pair, count in self.cross_domain_pairs.most_common(3):
                if count >= self.min_occurrences:
                    summary_parts.append(f"- {pair[0]} ↔ {pair[1]} (connected {count} times)")

        return "\n".join(summary_parts)

    # ==================== Phase 13A: Core Learning Methods (Days 3-8) ====================
    # These methods will be implemented in subsequent development phases
    
    def extract_concepts_with_spacy(self, text: str) -> List[str]:
        """
        Extract technical concepts from text using spaCy NLP.
        
        Improved approach (Phase 13A Days 3-4):
        - Use spaCy for accurate POS tagging (NOUN, PROPN only)
        - Extract noun chunks for multi-word concepts
        - Use lemmatization for base forms
        - Filter with STOPWORDS (700+) and validate with TECHNICAL_TERMS (500+)
        - Return 10-15 high-quality concepts (vs 50+ garbage)
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of 10-15 high-quality technical concepts
        """
        if not self.nlp:
            logger.warning("spaCy not initialized, falling back to basic extraction")
            return self._extract_concepts_fallback(text)
        
        concepts = set()
        
        # Remove code blocks to avoid false positives
        text_no_code = re.sub(r'```[^`]*```', '', text)
        text_no_code = re.sub(r'`[^`]+`', '', text_no_code)
        
        if not text_no_code.strip():
            return []
        
        # Process with spaCy
        doc = self.nlp(text_no_code)
        
        # Extract individual nouns and proper nouns
        for token in doc:
            # Must be noun or proper noun
            if token.pos_ not in ['NOUN', 'PROPN']:
                continue
            
            # Get lemmatized form (base form: "queries" → "query")
            concept = token.lemma_.lower()
            
            # Apply quality filters
            if self._is_valid_concept(concept):
                concepts.add(concept)
        
        # Extract noun chunks (multi-word technical phrases)
        for chunk in doc.noun_chunks:
            # Get chunk text and clean it
            chunk_text = chunk.text.lower().strip()
            
            # Skip single-word chunks (already captured above)
            if ' ' not in chunk_text:
                continue
            
            # Validate multi-word concept
            if self._is_valid_concept(chunk_text):
                # Normalize: "api endpoint" stays as is, preserve spaces
                concepts.add(chunk_text)
        
        # Extract named entities (organizations, products, technologies)
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'GPE', 'NORP']:
                concept = ent.text.lower().strip()
                if self._is_valid_concept(concept):
                    concepts.add(concept)
        
        # Also extract technical terms that appear in text (word-boundary match)
        text_lower = text_no_code.lower()
        for term in TECHNICAL_TERMS:
            if re.search(r'\b' + re.escape(term) + r'\b', text_lower):
                concepts.add(term)
        
        # Convert to list
        concept_list = list(concepts)
        
        # Prioritize and sort concepts
        def concept_priority(c: str) -> tuple:
            """Return sort key: (is_technical, has_space, length)"""
            is_technical = c in TECHNICAL_TERMS
            has_space = ' ' in c  # Multi-word concepts are more specific
            return (is_technical, has_space, len(c))
        
        concept_list.sort(key=concept_priority, reverse=True)
        
        # Limit to top 15 concepts
        result = concept_list[:15]
        
        logger.debug(f"Extracted {len(result)} concepts from text: {result[:5]}...")
        
        return result
    
    def _is_valid_concept(self, concept: str) -> bool:
        """
        Validate that a concept meets quality standards.
        
        Quality criteria (Phase 13A Days 3-4):
        1. Length: 3+ characters (allows some 3-letter terms like "api", "git")
        2. Not in STOPWORDS (700+ common words)
        3. Either:
           - In TECHNICAL_TERMS whitelist (500+), OR
           - Contains numbers/special chars (e.g., "api2", "ml-ops"), OR
           - Multi-word phrase with space (e.g., "neural network"), OR
           - Properly capitalized proper noun (e.g., "Docker", "Python"), OR
           - Contains underscore/dash (e.g., "snake_case", "kebab-case")
        4. Not a common verb (even if missed by STOPWORDS)
        
        Args:
            concept: Candidate concept string
            
        Returns:
            True if concept passes quality filters
        """
        # Must be 3+ characters (allow some short technical terms)
        if len(concept) < 3:
            return False
        
        # Must not be in stopwords
        if concept.lower() in STOPWORDS:
            return False
        
        # Check if in technical terms whitelist (BEST SIGNAL)
        if concept.lower() in TECHNICAL_TERMS:
            return True
        
        # Allow multi-word phrases (usually more specific)
        if ' ' in concept:
            # But check that individual words aren't all stopwords
            words = concept.split()
            non_stopwords = [w for w in words if w.lower() not in STOPWORDS]
            if len(non_stopwords) >= 1:  # At least one meaningful word
                return True
            return False
        
        # Allow if contains numbers (likely technical: "http2", "python3", "sha256")
        if any(char.isdigit() for char in concept):
            return True
        
        # Allow if contains underscore or dash (technical naming: "snake_case", "ml-ops")
        if '_' in concept or '-' in concept:
            return True
        
        # Allow if properly capitalized (likely proper noun: "Docker", "Python", "GitHub")
        # But not all caps (often acronyms that need separate handling)
        if concept and concept[0].isupper() and not concept.isupper() and len(concept) > 3:
            return True
        
        # Reject common verbs (even if missed by stopwords)
        common_verbs = {
            'make', 'take', 'give', 'find', 'think', 'know', 'come', 'work',
            'help', 'start', 'stop', 'move', 'live', 'believe', 'bring', 'happen',
            'create', 'build', 'implement', 'handle', 'manage', 'process', 'check',
            'update', 'delete', 'insert', 'remove', 'add', 'change', 'modify',
            'issue', 'problem', 'question', 'example', 'thing', 'stuff', 'item'
        }
        if concept.lower() in common_verbs:
            return False
        
        # Reject single-letter or two-letter unless in technical terms
        if len(concept) < 3:
            return False
        
        # Default: reject (be conservative, prefer false negatives over false positives)
        return False
    
    def _extract_concepts_fallback(self, text: str) -> List[str]:
        """
        Fallback concept extraction when spaCy is unavailable.
        
        Uses basic heuristics:
        - Capitalized words (likely proper nouns)
        - Technical terms from whitelist
        - CamelCase, snake_case patterns
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of up to 15 concepts using basic extraction
        """
        concepts = set()
        
        # Remove code blocks
        text_no_code = re.sub(r'```[^`]*```', '', text)
        text_no_code = re.sub(r'`[^`]+`', '', text_no_code)
        
        if not text_no_code.strip():
            return []
        
        # Extract capitalized words (not at sentence start)
        words = text_no_code.split()
        for i, word in enumerate(words):
            # Skip first word of sentences
            if i > 0 and word and word[0].isupper():
                concept = re.sub(r'[^\w-]', '', word).lower()
                if self._is_valid_concept(concept):
                    concepts.add(concept)
        
        # Extract technical terms from whitelist (word-boundary match)
        text_lower = text_no_code.lower()
        for term in TECHNICAL_TERMS:
            if re.search(r'\b' + re.escape(term) + r'\b', text_lower):
                concepts.add(term)
        
        # Extract CamelCase patterns
        camel_case = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b', text_no_code)
        for term in camel_case:
            concept = term.lower()
            if self._is_valid_concept(concept):
                concepts.add(concept)
        
        # Extract snake_case patterns
        snake_case = re.findall(r'\b[a-z]+_[a-z_]+\b', text_lower)
        for term in snake_case:
            if len(term) > 5 and self._is_valid_concept(term):
                concepts.add(term)
        
        # Convert to list and sort by priority
        concept_list = list(concepts)
        concept_list.sort(key=lambda c: (c in TECHNICAL_TERMS, len(c)), reverse=True)
        
        result = concept_list[:15]
        logger.debug(f"Extracted {len(result)} concepts (fallback): {result[:5]}...")
        
        return result
    
    def learn_from_compressed(
        self,
        compressed_data: dict,
        conversation_id: str,
        rag_metadata: Optional[dict] = None
    ) -> Dict[str, int]:
        """
        Learn RAG optimization patterns from compressed conversation data.
        
        **Phase 2: CORRECTED Integration - RAG-Focused Learning**
        
        This method now extracts **RAG-relevant** patterns:
        - Query→Chunk patterns: Which chunks answer which query types
        - Domain→Collection patterns: Which collections are relevant per domain
        - File→Topic patterns: Which files relate to which topics
        
        IMPORTANT: This is the PRIMARY learning mechanism for RAG optimization,
        not general concept learning. The goal is to make future RAG queries faster.
        
        Args:
            compressed_data: Compressed conversation dict from CompressionManager
            conversation_id: Unique conversation identifier
            rag_metadata: Optional dict with actual RAG retrieval data:
                {
                    'queries': [{'query': str, 'chunks': [chunk_ids], 'collections': [names]}],
                    'domains': [domain_str, ...],
                    'successful_files': [filepath, ...]
                }
            
        Returns:
            Dict with counts of patterns learned:
            {
                'query_chunk_patterns': int,
                'domain_priority_patterns': int,
                'file_topic_patterns': int,
                'total': int
            }
        """
        patterns_learned = {
            'query_chunk_patterns': 0,
            'domain_priority_patterns': 0,
            'file_topic_patterns': 0,
            'conceptual_patterns': 0,  # Keep for backward compat
            'total': 0
        }
        
        try:
            # Extract compression format fields
            focus_topics = compressed_data.get('focus_topics', [])
            key_concepts = compressed_data.get('key_concepts', [])
            artifacts = compressed_data.get('artifacts_created', [])
            mode = compressed_data.get('mode', 'chat')
            task_type = compressed_data.get('task_type', 'general')
            
            # Infer domain from mode/task_type/topics
            inferred_domain = self._infer_domain_from_conversation(
                mode, task_type, focus_topics, key_concepts
            )
            
            # ==================================================================
            # PART 1: Learn from RAG metadata (if provided - HIGHEST VALUE)
            # ==================================================================
            if rag_metadata:
                # Learn query→chunk patterns from actual RAG retrievals
                for query_data in rag_metadata.get('queries', []):
                    query = query_data.get('query', '')
                    chunk_ids = query_data.get('chunks', [])
                    collections = query_data.get('collections', [])
                    
                    if query and chunk_ids:
                        # Create or update QueryChunkPattern
                        query_template, placeholders = self._extract_query_template(query)
                        query_sig = self._create_query_signature(query_template)  # FIX: use template not query
                        pattern_id = f"qcp_{query_sig}"
                        
                        if pattern_id in self.query_chunk_patterns:
                            pattern = self.query_chunk_patterns[pattern_id]
                            pattern.total_queries += 1
                            pattern.last_seen = datetime.now()
                            
                            # Add successful chunks
                            for chunk_id in chunk_ids[:5]:  # Top 5
                                # Find existing or add new
                                found = False
                                for sc in pattern.successful_chunks:
                                    if sc['chunk_id'] == chunk_id:
                                        sc['hit_count'] += 1
                                        found = True
                                        break
                                if not found:
                                    pattern.successful_chunks.append({
                                        'chunk_id': chunk_id,
                                        'collection': collections[0] if collections else 'unknown',
                                        'hit_count': 1,
                                        'avg_score': 0.8  # Assume good if retrieved
                                    })
                            
                            # Update confidence
                            pattern.confidence = min(1.0, 0.5 + (pattern.total_queries * 0.05))
                            patterns_learned['query_chunk_patterns'] += 1
                        
                        else:
                            # Create new pattern
                            self.query_chunk_patterns[pattern_id] = QueryChunkPattern(
                                pattern_id=pattern_id,
                                query_template=query_template,
                                query_signature=query_sig,
                                successful_chunks=[{
                                    'chunk_id': cid,
                                    'collection': collections[0] if collections else 'unknown',
                                    'hit_count': 1,
                                    'avg_score': 0.8
                                } for cid in chunk_ids[:5]],
                                total_queries=1,
                                confidence=0.6,
                                first_seen=datetime.now(),
                                last_seen=datetime.now(),
                                metadata={}
                            )
                            patterns_learned['query_chunk_patterns'] += 1
                
                # Learn domain→collection patterns from actual usage
                for domain in rag_metadata.get('domains', []):
                    collections_used = set()
                    num_queries_for_domain = len(rag_metadata.get('queries', []))
                    
                    for query_data in rag_metadata.get('queries', []):
                        collections_used.update(query_data.get('collections', []))
                    
                    if collections_used:
                        pattern_id = f"domain_priority_{domain}"
                        
                        if pattern_id in self.domain_priority_patterns:
                            pattern = self.domain_priority_patterns[pattern_id]
                            pattern.total_queries += num_queries_for_domain  # FIX: count all queries
                            
                            # Update weights based on usage
                            for coll in collections_used:
                                pattern.collection_weights[coll] = pattern.collection_weights.get(coll, 0) + 0.1
                            
                            # Normalize weights
                            total_weight = sum(pattern.collection_weights.values())
                            if total_weight > 0:
                                pattern.collection_weights = {
                                    k: v / total_weight 
                                    for k, v in pattern.collection_weights.items()
                                }
                            
                            pattern.confidence = min(1.0, 0.5 + (pattern.total_queries * 0.02))
                            pattern.last_seen = datetime.now()
                            patterns_learned['domain_priority_patterns'] += 1
                        else:
                            # Create new pattern
                            weights = {coll: 1.0 / len(collections_used) for coll in collections_used}
                            self.domain_priority_patterns[pattern_id] = DomainPriorityPattern(
                                pattern_id=pattern_id,
                                domain=domain,
                                collection_weights=weights,
                                collection_stats={},
                                total_queries=num_queries_for_domain,  # FIX: start with correct count
                                confidence=0.6,
                                first_seen=datetime.now(),
                                last_seen=datetime.now(),
                                metadata={}
                            )
                            patterns_learned['domain_priority_patterns'] += 1
            
            # ==================================================================
            # PART 2: Infer patterns from compression data (FALLBACK)
            # ==================================================================
            # If no RAG metadata provided, make educated guesses from compression
            
            # Infer query patterns from focus topics
            # Focus topics often represent what user was asking about
            for topic in focus_topics:
                if len(topic) > 3:
                    # Create synthetic query pattern: "What is {topic}?" or "How to {topic}?"
                    synthetic_query = f"How to {topic}" if topic in ['implement', 'create', 'build'] else f"What is {topic}"
                    synthetic_template, _ = self._extract_query_template(synthetic_query)
                    query_sig = self._create_query_signature(synthetic_template)  # FIX: use template
                    pattern_id = f"qcp_{query_sig}"
                    
                    # Only create if we have artifact hints about what was useful
                    if artifacts:
                        chunk_hints = []
                        for artifact in artifacts:
                            artifact_name = artifact.get('name', '')
                            if artifact_name and topic.lower() in artifact_name.lower():
                                # This artifact likely relates to this topic
                                chunk_hints.append({
                                    'chunk_id': f"inferred_{artifact_name}",
                                    'collection': 'codebase' if artifact.get('type') == 'code' else 'notes',
                                    'hit_count': 1,
                                    'avg_score': 0.7  # Lower confidence for inferred
                                })
                        
                        if chunk_hints:
                            if pattern_id not in self.query_chunk_patterns:
                                self.query_chunk_patterns[pattern_id] = QueryChunkPattern(
                                    pattern_id=pattern_id,
                                    query_template=synthetic_template,  # FIX: store template not query
                                    query_signature=query_sig,
                                    successful_chunks=chunk_hints[:3],  # Top 3
                                    total_queries=1,
                                    confidence=0.4,  # Lower for inferred
                                    first_seen=datetime.now(),
                                    last_seen=datetime.now(),
                                    metadata={'inferred': True}
                                )
                                patterns_learned['query_chunk_patterns'] += 1
            
            # Learn domain→collection from inferred domain and artifacts
            if inferred_domain and artifacts:
                pattern_id = f"domain_priority_{inferred_domain}"
                collections_inferred = set()
                
                for artifact in artifacts:
                    artifact_type = artifact.get('type', '')
                    if artifact_type == 'code':
                        collections_inferred.add('codebase')
                    elif artifact_type in ['document', 'note', 'markdown']:
                        collections_inferred.add('notes')
                
                if collections_inferred:
                    if pattern_id not in self.domain_priority_patterns:
                        weights = {coll: 1.0 / len(collections_inferred) for coll in collections_inferred}
                        self.domain_priority_patterns[pattern_id] = DomainPriorityPattern(
                            pattern_id=pattern_id,
                            domain=inferred_domain,
                            collection_weights=weights,
                            collection_stats={},
                            total_queries=1,
                            confidence=0.4,  # Lower for inferred
                            first_seen=datetime.now(),
                            last_seen=datetime.now(),
                            metadata={'inferred': True}
                        )
                        patterns_learned['domain_priority_patterns'] += 1
            
            # ==================================================================
            # PART 3: Keep minimal conceptual learning (backward compat)
            # ==================================================================
            # Still track concepts for query expansion, but this is secondary
            concept_names = []
            for concept in key_concepts:
                term = concept.get('term', '')
                if term:
                    self.concept_mentions[term] += 1
                    concept_names.append(term)
                    patterns_learned['conceptual_patterns'] += 1
            
            for topic in focus_topics:
                if topic and len(topic) > 3:
                    self.concept_mentions[topic] += 1
                    if topic not in concept_names:
                        concept_names.append(topic)
            
            # Create cross-domain pairs (for query expansion)
            if len(concept_names) >= 2:
                for i, c1 in enumerate(concept_names):
                    for c2 in concept_names[i+1:]:
                        if c1 != c2:
                            pair = tuple(sorted([c1, c2]))
                            self.cross_domain_pairs[pair] += 1
            
            # ==================================================================
            # Calculate totals and log
            # ==================================================================
            patterns_learned['total'] = sum([
                patterns_learned['query_chunk_patterns'],
                patterns_learned['domain_priority_patterns'],
                patterns_learned['file_topic_patterns'],
                patterns_learned['conceptual_patterns']
            ])
            
            if patterns_learned['total'] > 0:
                logger.info(
                    f"🎯 Learned RAG patterns from compressed conversation {conversation_id}: "
                    f"{patterns_learned['query_chunk_patterns']} query→chunk, "
                    f"{patterns_learned['domain_priority_patterns']} domain→collection, "
                    f"{patterns_learned['conceptual_patterns']} conceptual"
                    f"{' (with RAG metadata)' if rag_metadata else ' (inferred)'}"
                )
            
            return patterns_learned
            
        except Exception as e:
            logger.error(f"Failed to learn from compressed data: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return patterns_learned
    
    def _infer_domain_from_conversation(
        self,
        mode: str,
        task_type: str,
        focus_topics: list,
        key_concepts: list
    ) -> Optional[str]:
        """Infer domain from conversation metadata"""
        # Map mode/task to likely domain
        if mode in ['notes', 'obsidian']:
            return 'notes'
        elif mode == 'code':
            return 'code'
        
        # Check topics/concepts for domain hints
        all_terms = focus_topics + [c.get('term', '') for c in key_concepts]
        all_terms_str = ' '.join(all_terms).lower()
        
        # Domain keyword detection (extend as needed)
        if any(term in all_terms_str for term in ['norns', 'supercollider', 'lua', 'monome']):
            return 'signals'
        elif any(term in all_terms_str for term in ['sigil', 'glyph', 'symbol']):
            return 'sigils'
        elif any(term in all_terms_str for term in ['grid', 'arc', 'midi']):
            return 'grids'
        elif any(term in all_terms_str for term in ['scroll', 'timeline', 'sequencer']):
            return 'scrolls'
        elif any(term in all_terms_str for term in ['python', 'javascript', 'code', 'api']):
            return 'code'
        elif any(term in all_terms_str for term in ['note', 'document', 'writing']):
            return 'notes'
        
        return task_type if task_type != 'general' else None
    
    def learn_query_chunk_patterns(
        self, 
        query: str, 
        results: List[Dict], 
        user_feedback: Optional[str] = None
    ) -> None:
        """
        Learn which chunks successfully answer specific query patterns.
        
        Phase 13A Days 5-8 (HIGHEST PRIORITY - 30-50% speedup)
        
        Algorithm:
        1. Extract query template using _extract_query_template()
        2. Identify which chunks had high scores (>0.7)
        3. Track chunk_id + collection for successful results
        4. If user provides positive feedback, boost confidence
        5. Update or create QueryChunkPattern
        6. After N queries with same template, boost top chunks in future queries
        
        Args:
            query: The user's query text
            results: List of dicts with {chunk_id, score, filepath, source_type}
            user_feedback: Optional feedback ("helpful", "not helpful", etc.)
        """
        if not results:
            return
        
        # Extract query template (e.g., "How do I {action} {thing}?")
        template, fills = self._extract_query_template(query)
        query_sig = self._create_query_signature(template)
        
        # Find or create pattern
        pattern_id = f"qcp_{query_sig}"
        now = datetime.now()
        
        if pattern_id not in self.query_chunk_patterns:
            # Create new pattern
            self.query_chunk_patterns[pattern_id] = QueryChunkPattern(
                pattern_id=pattern_id,
                query_template=template,
                query_signature=query_sig,
                successful_chunks=[],
                total_queries=0,
                confidence=0.0,
                first_seen=now,
                last_seen=now,
                metadata={'fills_examples': [fills] if fills else []}
            )
            logger.info(f"Created query→chunk pattern: {template}")
        
        pattern = self.query_chunk_patterns[pattern_id]
        pattern.total_queries += 1
        pattern.last_seen = now
        
        # Record successful chunks (score >= 0.7)
        threshold = 0.7
        if user_feedback and user_feedback.lower() in ['helpful', 'good', 'yes']:
            threshold = 0.6  # Lower threshold if user gave positive feedback
        
        for result in results:
            score = result.get('score', 0.0)
            if score < threshold:
                continue
            
            chunk_id = result.get('chunk_id')
            if not chunk_id:
                continue
            
            # Update or add chunk stats
            chunk_found = False
            for chunk_stat in pattern.successful_chunks:
                if chunk_stat['chunk_id'] == chunk_id:
                    # Update existing chunk
                    old_count = chunk_stat['hit_count']
                    old_avg = chunk_stat['avg_score']
                    
                    chunk_stat['hit_count'] += 1
                    chunk_stat['avg_score'] = (old_avg * old_count + score) / chunk_stat['hit_count']
                    
                    chunk_found = True
                    logger.debug(f"Updated chunk {chunk_id[:8]}... stats: "
                               f"hits={chunk_stat['hit_count']}, avg_score={chunk_stat['avg_score']:.2f}")
                    break
            
            if not chunk_found:
                # Add new chunk to pattern
                pattern.successful_chunks.append({
                    'chunk_id': chunk_id,
                    'collection': result.get('source_type', 'unknown'),
                    'hit_count': 1,
                    'avg_score': score
                })
                logger.info(f"Added chunk {chunk_id[:8]}... to pattern '{template}' "
                          f"(score={score:.2f})")
        
        # Keep only top 20 chunks per pattern (by hit_count * avg_score)
        pattern.successful_chunks.sort(
            key=lambda c: c['hit_count'] * c['avg_score'],
            reverse=True
        )
        pattern.successful_chunks = pattern.successful_chunks[:20]
        
        # Update pattern confidence
        # Confidence = (query_factor) * (avg_chunk_quality)
        # query_factor: 0.0 → 1.0 as total_queries goes 0 → 10
        # avg_chunk_quality: average of (hit_count * avg_score) for top chunks
        if pattern.successful_chunks:
            query_factor = min(pattern.total_queries / 10.0, 1.0)
            avg_quality = sum(c['hit_count'] * c['avg_score'] for c in pattern.successful_chunks[:5]) / min(5, len(pattern.successful_chunks))
            pattern.confidence = query_factor * min(avg_quality / 5.0, 1.0)  # Normalize quality
        else:
            pattern.confidence = 0.0
        
        logger.debug(f"Pattern '{query_sig}': {len(pattern.successful_chunks)} chunks, "
                   f"confidence={pattern.confidence:.2f}, queries={pattern.total_queries}")
    
    def _create_query_signature(self, template: str) -> str:
        """
        Create a normalized signature for a query template.
        
        Phase 13A Days 5-8
        
        Args:
            template: Query template from _extract_query_template()
            
        Returns:
            Normalized signature (lowercase, underscores, no special chars)
            
        Example:
            "How do I {action} {thing}?" → "how_do_i_action_thing"
        """
        # Remove placeholder markers
        sig = re.sub(r'\{[^}]+\}', 'X', template)
        # Convert to lowercase
        sig = sig.lower()
        # Remove punctuation
        sig = re.sub(r'[^\w\s]', '', sig)
        # Replace spaces with underscores
        sig = sig.replace(' ', '_')
        # Remove consecutive underscores
        sig = re.sub(r'_+', '_', sig)
        # Remove leading/trailing underscores
        sig = sig.strip('_')
        
        return sig
    
    def record_collection_performance(
        self,
        domain: str,
        collection_name: str,
        had_results: bool,
        top_score: float = 0.0
    ):
        """
        Record whether a collection returned useful results for a domain query.
        
        Phase 13A Days 9-11: Low-level tracking method
        
        Args:
            domain: Domain of the query ('python', 'docker', 'react', etc.)
            collection_name: Name of collection ('obsidian', 'codebase', 'integration_github_norns', etc.)
            had_results: Whether this collection returned any results with score >= 0.6
            top_score: Highest score from this collection (0.0 if no results)
        """
        pattern_id = f"domain_priority_{domain}"
        
        now = datetime.now()
        
        if pattern_id not in self.domain_priority_patterns:
            # Create new pattern
            self.domain_priority_patterns[pattern_id] = DomainPriorityPattern(
                pattern_id=pattern_id,
                domain=domain,
                collection_weights={},
                collection_stats={},
                total_queries=0,
                confidence=0.0,
                first_seen=now,
                last_seen=now,
                metadata={}
            )
            logger.info(f"Created domain→collection pattern for domain: {domain}")
        
        pattern = self.domain_priority_patterns[pattern_id]
        pattern.last_seen = now
        
        # Initialize stats for this collection if not exists
        if collection_name not in pattern.collection_stats:
            pattern.collection_stats[collection_name] = {
                'queries': 0,
                'hits': 0,
                'total_score': 0.0,
                'hit_rate': 0.0,
                'avg_score': 0.0
            }
        
        stats = pattern.collection_stats[collection_name]
        stats['queries'] += 1
        
        if had_results and top_score >= 0.6:
            stats['hits'] += 1
            stats['total_score'] += top_score
        
        # Update hit rate and average score
        stats['hit_rate'] = stats['hits'] / stats['queries']
        stats['avg_score'] = stats['total_score'] / stats['hits'] if stats['hits'] > 0 else 0.0
        
        # Update collection weight
        # Formula: hit_rate * avg_score * (1 + log(queries + 1))
        # This gives higher weight to collections with:
        # 1. High hit rate (binary: returns results or not)
        # 2. High average score (quality of results)
        # 3. More queries (confidence factor, but logarithmic so doesn't dominate)
        import math
        confidence_factor = 1 + math.log(stats['queries'] + 1)
        quality_factor = stats['hit_rate'] * stats['avg_score']
        pattern.collection_weights[collection_name] = quality_factor * confidence_factor
        
        logger.debug(f"Domain {domain} → {collection_name}: "
                    f"hit_rate={stats['hit_rate']:.2f}, "
                    f"queries={stats['queries']}, "
                    f"weight={pattern.collection_weights[collection_name]:.2f}")
    
    def learn_domain_priorities(
        self,
        query: str,
        domain: str,
        collection_results: Dict[str, float]
    ) -> None:
        """
        Learn which collections perform best for specific domains.
        
        IMPLEMENTATION: Days 9-11 (20-40% speedup)
        
        Algorithm:
        1. Detect query domain (python, docker, react, etc.)
        2. Track which collections returned best results
        3. Calculate success rate per collection for this domain
        4. Update collection_weights: successful collections get 1.5-2.0x, poor ones get 0.5x
        5. Use these weights to prioritize collections in future queries
        
        Args:
            query: The user's query
            domain: Detected domain (e.g., "python", "docker")
            collection_results: Dict mapping collection_name -> avg_score (or max score)
        """
        pattern_id = f"domain_priority_{domain}"
        
        # Record performance for each collection (this may create the pattern)
        for collection_name, score in collection_results.items():
            had_results = score >= 0.6
            self.record_collection_performance(
                domain=domain,
                collection_name=collection_name,
                had_results=had_results,
                top_score=score
            )
        
        # Increment total_queries for this domain after recording
        if pattern_id in self.domain_priority_patterns:
            pattern = self.domain_priority_patterns[pattern_id]
            pattern.total_queries += 1
            
            # Update pattern confidence based on total queries
            # Confidence grows logarithmically: 0.0 → 1.0 as queries go 1 → 20
            import math
            pattern.confidence = min(math.log(pattern.total_queries + 1) / math.log(21), 1.0)
            
            logger.info(f"Domain pattern '{domain}': {len(pattern.collection_stats)} collections tracked, "
                       f"confidence={pattern.confidence:.2f}, queries={pattern.total_queries}")
        
        # Save patterns after learning
        self.save_patterns()
    
    def learn_project_workflow(
        self,
        project_path: str,
        command: str,
        success: bool,
        output: str = ""
    ) -> None:
        """
        Learn project-specific build/test/deploy workflows.
        
        IMPLEMENTATION: Days 12-13
        
        Algorithm:
        1. Detect workflow type (build, test, deploy, lint, etc.)
        2. Track command success/failure rates
        3. Learn command sequences (e.g., "npm install" before "npm test")
        4. Extract common errors and solutions
        5. Build confidence over time
        
        Args:
            project_path: Path to the project
            command: Command that was executed
            success: Whether command succeeded
            output: Command output (for error extraction)
        """
        # TODO: Implement project workflow learning
        # - Detect workflow type from command
        # - Parse errors from output if failed
        # - Update ProjectWorkflowPattern using create_or_update_workflow_pattern()
        # - Save patterns after update
        
        pass  # Placeholder
    
    def get_boosted_chunks_for_query(self, query: str) -> List[Dict]:
        """
        Get chunk IDs that should be boosted for this query based on learned patterns.
        
        Phase 13A Days 5-8 (used by RAG retrieval)
        
        Args:
            query: The user's query text
            
        Returns:
            List of dicts with {chunk_id, collection, boost_factor, hit_count, avg_score}
            boost_factor ranges from 1.2 to 2.0 based on confidence and hit_count
            Empty list if no pattern matches
        """
        # Extract query template to find matching pattern
        template, _ = self._extract_query_template(query)
        query_sig = self._create_query_signature(template)
        pattern_id = f"qcp_{query_sig}"
        
        if pattern_id not in self.query_chunk_patterns:
            # No learned pattern for this query type
            return []
        
        pattern = self.query_chunk_patterns[pattern_id]
        
        # Only use patterns with minimum data (at least 3 queries seen OR high confidence)
        # Lower threshold to make it useful sooner
        if pattern.total_queries < 2:
            logger.debug(f"Pattern '{query_sig}' needs more queries "
                       f"(queries={pattern.total_queries}, need 2+)")
            return []
        
        boosted_chunks = []
        
        # Get top chunks (minimum 2 hits and avg_score >= 0.65 to be reliable)
        for chunk_stat in pattern.successful_chunks[:10]:
            if chunk_stat['hit_count'] < 2:
                continue
            if chunk_stat['avg_score'] < 0.65:
                continue
            
            # Calculate boost factor based on:
            # 1. Hit count (more hits = higher boost)
            # 2. Average score (higher quality = higher boost)
            # 3. Pattern confidence
            
            # Base boost: 1.2x to 1.8x based on hit_count
            hit_boost = 1.2 + min(chunk_stat['hit_count'] / 10.0, 0.6)
            
            # Quality multiplier: 0.8x to 1.2x based on avg_score
            quality_mult = 0.6 + (chunk_stat['avg_score'] * 0.6)
            
            # Final boost capped at 2.0x
            boost_factor = min(hit_boost * quality_mult, 2.0)
            
            boosted_chunks.append({
                'chunk_id': chunk_stat['chunk_id'],
                'collection': chunk_stat['collection'],
                'boost_factor': boost_factor,
                'hit_count': chunk_stat['hit_count'],
                'avg_score': chunk_stat['avg_score']
            })
        
        if boosted_chunks:
            logger.info(f"Query pattern '{template}' (conf={pattern.confidence:.2f}, queries={pattern.total_queries}): "
                      f"boosting {len(boosted_chunks)} chunks")
        
        return boosted_chunks
    
    def get_collection_weights_for_domain(self, domain: str) -> Dict[str, float]:
        """
        Get collection priority weights for a specific domain.
        
        IMPLEMENTATION: Days 9-11 (used by RAG retrieval)
        
        Returns:
            Dict mapping collection_name -> weight (0.5 to 2.0)
            Weight is calculated from hit_rate * log(queries), ranges approx 0-3
            Returns empty dict if no pattern exists (RAG will use defaults)
            
        Example:
            weights = learner.get_collection_weights_for_domain('python')
            # {'codebase': 2.1, 'obsidian': 0.8, 'github_norns': 0.1}
        """
        pattern_id = f"domain_priority_{domain}"
        
        if pattern_id not in self.domain_priority_patterns:
            logger.debug(f"No domain priority pattern found for '{domain}'")
            return {}
        
        pattern = self.domain_priority_patterns[pattern_id]
        
        # Only use patterns with minimum confidence (at least 2 queries)
        # Lowered from 3 to make patterns useful sooner
        if pattern.total_queries < 2:
            logger.debug(f"Domain pattern '{domain}' needs more queries "
                        f"(queries={pattern.total_queries}, need 2+)")
            return {}
        
        # Return raw weights calculated by record_collection_performance()
        # Weights are: hit_rate * (1 + log(queries + 1))
        # Typical ranges:
        #   - High performers: 1.5 - 3.0 (high hit rate, many queries)
        #   - Medium: 0.5 - 1.5 (moderate hit rate)
        #   - Low: 0.0 - 0.5 (low hit rate or few queries)
        logger.debug(f"Domain '{domain}': returning {len(pattern.collection_weights)} collection weights "
                    f"(confidence={pattern.confidence:.2f})")
        
        return pattern.collection_weights.copy()
    
    def record_pattern_usage(self, pattern_id: str, was_helpful: bool = True):
        """
        Record that a pattern was used and whether it was helpful.
        
        Phase 13A Days 12-13: Track pattern usefulness
        
        Args:
            pattern_id: ID of the pattern that was used
            was_helpful: Whether the pattern led to good results
                        True = user got what they needed
                        False = user rephrased or corrected
        
        Example:
            # When query expansion uses a conceptual pattern
            learner.record_pattern_usage('concept_pair_docker_python', was_helpful=True)
            
            # When pattern is used but user rephrases (suggests it wasn't helpful)
            learner.record_pattern_usage('concept_pair_docker_python', was_helpful=False)
        """
        if pattern_id not in self.patterns:
            logger.warning(f"Attempted to record usage for unknown pattern: {pattern_id}")
            return
        
        pattern = self.patterns[pattern_id]
        pattern.times_used += 1
        
        if was_helpful:
            pattern.times_helpful += 1
        
        # Calculate usefulness ratio for logging
        usefulness_ratio = pattern.times_helpful / pattern.times_used if pattern.times_used > 0 else 0.0
        
        logger.debug(f"Pattern usage recorded: {pattern.name} "
                    f"(used={pattern.times_used}, helpful={pattern.times_helpful}, "
                    f"usefulness={usefulness_ratio:.2f})")
    
    def prune_low_quality_patterns(self) -> int:
        """
        Remove patterns with low confidence or stale data.
        
        IMPLEMENTATION: Days 14-15 (Pattern Quality Controls)
        
        Pruning rules:
        1. Conceptual patterns: keep top 200 by confidence × occurrences (already done in _prune_conceptual_patterns)
        2. Old + low confidence: remove if confidence < 0.4 AND not seen in 90 days
        3. Single occurrence + old: remove if occurrences == 1 AND not seen in 30 days
        4. Query→chunk patterns: keep top 100 by total_queries
        5. Domain priority patterns: never prune (always useful)
        
        Returns:
            Number of patterns pruned
        """
        now = datetime.now()
        cutoff_90_days = now - timedelta(days=90)
        cutoff_30_days = now - timedelta(days=30)
        pruned_count = 0
        
        # 1. Prune conceptual patterns (already implemented in Days 12-13)
        self._prune_conceptual_patterns()
        
        # 2. Remove old + low confidence patterns (legacy conceptual/code patterns)
        to_remove = []
        for pattern_id, pattern in self.patterns.items():
            if pattern.pattern_type not in ['conceptual', 'code']:
                continue
            
            if pattern.last_seen < cutoff_90_days and pattern.confidence < 0.4:
                to_remove.append(pattern_id)
                logger.info(f"🧹 Pruning stale pattern: {pattern.name} "
                           f"(last_seen={pattern.last_seen.date()}, confidence={pattern.confidence:.2f})")
        
        for pattern_id in to_remove:
            del self.patterns[pattern_id]
            pruned_count += 1
        
        # 3. Remove single occurrence + old patterns
        to_remove = []
        for pattern_id, pattern in self.patterns.items():
            if pattern.pattern_type not in ['conceptual', 'code']:
                continue
            
            if pattern.occurrences == 1 and pattern.first_seen < cutoff_30_days:
                to_remove.append(pattern_id)
                logger.info(f"🧹 Pruning one-time pattern: {pattern.name} "
                           f"(first_seen={pattern.first_seen.date()})")
        
        for pattern_id in to_remove:
            del self.patterns[pattern_id]
            pruned_count += 1
        
        # 4. Prune query→chunk patterns (keep top 100 by total_queries)
        query_chunk_list = list(self.query_chunk_patterns.values())
        if len(query_chunk_list) > 100:
            query_chunk_list.sort(key=lambda p: p.total_queries, reverse=True)
            
            for pattern in query_chunk_list[100:]:
                del self.query_chunk_patterns[pattern.pattern_id]
                logger.info(f"🧹 Pruning low-usage query→chunk pattern: {pattern.query_template} "
                           f"(total_queries={pattern.total_queries})")
                pruned_count += 1
        
        # 5. Domain priority patterns: never prune (always useful)
        # No action needed
        
        if pruned_count > 0:
            logger.info(f"🧹 Pruning complete. Removed {pruned_count} patterns. "
                       f"Patterns remaining: "
                       f"{len(self.patterns)} conceptual/code, "
                       f"{len(self.query_chunk_patterns)} query→chunk, "
                       f"{len(self.domain_priority_patterns)} domain priority")
        
        return pruned_count

    # ==================== Phase 13A Day 16: Pattern Enhancement APIs ====================
    
    def get_conceptual_patterns_for_concept(self, concept: str) -> List[Pattern]:
        """
        Get all conceptual patterns related to a concept.
        
        Phase 13A Day 16: Pattern Enhancement APIs
        
        Args:
            concept: The concept to search for (e.g., "docker", "python")
        
        Returns:
            List of Pattern objects sorted by confidence (highest first)
        
        Example:
            >>> patterns = learner.get_conceptual_patterns_for_concept("docker")
            >>> for p in patterns:
            >>>     print(f"{p.name}: {p.confidence:.2f}")
        """
        concept_lower = concept.lower()
        results = []
        
        for pattern in self.patterns.values():
            if pattern.pattern_type != 'conceptual':
                continue
            
            concept1 = pattern.metadata.get('concept1', '').lower()
            concept2 = pattern.metadata.get('concept2', '').lower()
            
            if concept_lower in [concept1, concept2]:
                results.append(pattern)
        
        results.sort(key=lambda p: p.confidence, reverse=True)
        return results
    
    def get_query_chunk_pattern(self, query: str) -> Optional[QueryChunkPattern]:
        """
        Get query→chunk pattern for a query.
        
        Phase 13A Day 16: Pattern Enhancement APIs
        
        Args:
            query: The query to find a pattern for
        
        Returns:
            QueryChunkPattern if found, None otherwise
        
        Example:
            >>> pattern = learner.get_query_chunk_pattern("How do I use Docker?")
            >>> if pattern:
            >>>     print(f"Template: {pattern.query_template}")
            >>>     print(f"Top chunks: {pattern.successful_chunks[:3]}")
        """
        template, _ = self._extract_query_template(query)  # Returns (template, fills)
        query_sig = self._create_query_signature(template)
        pattern_id = f"qcp_{query_sig}"
        
        return self.query_chunk_patterns.get(pattern_id)
        return self.query_chunk_patterns.get(pattern_id)
    
    def get_domain_priorities(self, domain: str) -> Dict[str, float]:
        """
        Get collection priorities for a domain.
        
        Phase 13A Day 16: Pattern Enhancement APIs
        
        Args:
            domain: The domain to get priorities for (e.g., "python", "docker")
        
        Returns:
            Dict mapping collection names to weight scores (0.0-3.0+)
        
        Example:
            >>> weights = learner.get_domain_priorities("python")
            >>> print(weights)  # {'codebase': 2.5, 'obsidian': 1.8, 'github': 0.0}
        """
        pattern_id = f"dpp_{domain}"
        
        if pattern_id in self.domain_priority_patterns:
            return self.domain_priority_patterns[pattern_id].collection_weights.copy()
        
        return {}
    
    def get_all_patterns_by_confidence(self, min_confidence: float = 0.5) -> List[Pattern]:
        """
        Get all patterns above a confidence threshold, sorted by confidence.
        
        Phase 13A Day 16: Pattern Enhancement APIs
        
        Args:
            min_confidence: Minimum confidence threshold (default 0.5)
        
        Returns:
            List of Pattern objects sorted by confidence (highest first)
        
        Example:
            >>> patterns = learner.get_all_patterns_by_confidence(0.8)
            >>> print(f"Found {len(patterns)} high-confidence patterns")
        """
        results = [p for p in self.patterns.values() if p.confidence >= min_confidence]
        results.sort(key=lambda p: p.confidence, reverse=True)
        return results
    
    def get_pattern_stats(self) -> Dict:
        """
        Get summary statistics about all patterns.
        
        Phase 13A Day 16: Pattern Enhancement APIs
        
        Returns:
            Dict with pattern counts and statistics
        
        Example:
            >>> stats = learner.get_pattern_stats()
            >>> print(f"Total patterns: {stats['total_patterns']}")
            >>> print(f"Avg confidence: {stats['avg_confidence']:.2f}")
        """
        conceptual_patterns = [p for p in self.patterns.values() if p.pattern_type == 'conceptual']
        
        return {
            'total_patterns': len(self.patterns) + len(self.query_chunk_patterns) + len(self.domain_priority_patterns),
            'total_conceptual': len(conceptual_patterns),
            'total_code': len([p for p in self.patterns.values() if p.pattern_type == 'code']),
            'total_query_chunk': len(self.query_chunk_patterns),
            'total_domain_priority': len(self.domain_priority_patterns),
            'avg_confidence': sum(p.confidence for p in self.patterns.values()) / len(self.patterns) if self.patterns else 0,
            'avg_conceptual_confidence': sum(p.confidence for p in conceptual_patterns) / len(conceptual_patterns) if conceptual_patterns else 0,
            'avg_query_chunk_confidence': sum(p.confidence for p in self.query_chunk_patterns.values()) / len(self.query_chunk_patterns) if self.query_chunk_patterns else 0
        }
    
    def export_patterns_for_analysis(self) -> Dict:
        """
        Export all patterns in a format suitable for analysis/visualization.
        
        Phase 13A Day 16: Pattern Enhancement APIs
        
        Returns:
            Dict with all pattern data organized by type
        
        Example:
            >>> data = learner.export_patterns_for_analysis()
            >>> print(f"Conceptual patterns: {len(data['conceptual_patterns'])}")
            >>> print(f"Query→chunk patterns: {len(data['query_chunk_patterns'])}")
        """
        return {
            'conceptual_patterns': [
                {
                    'id': p.id,
                    'concept1': p.metadata.get('concept1'),
                    'concept2': p.metadata.get('concept2'),
                    'confidence': p.confidence,
                    'occurrences': p.occurrences,
                    'times_used': p.times_used,
                    'times_helpful': p.times_helpful,
                    'usefulness_ratio': p.times_helpful / p.times_used if p.times_used > 0 else 0.0,
                    'first_seen': p.first_seen.isoformat(),
                    'last_seen': p.last_seen.isoformat(),
                    'domains': p.domains
                }
                for p in self.patterns.values() if p.pattern_type == 'conceptual'
            ],
            'query_chunk_patterns': [
                {
                    'pattern_id': p.pattern_id,
                    'query_template': p.query_template,
                    'query_signature': p.query_signature,
                    'total_queries': p.total_queries,
                    'confidence': p.confidence,
                    'top_chunks': list(p.successful_chunks.items())[:5],
                    'first_seen': p.first_seen.isoformat(),
                    'last_seen': p.last_seen.isoformat()
                }
                for p in self.query_chunk_patterns.values()
            ],
            'domain_priorities': [
                {
                    'pattern_id': p.pattern_id,
                    'domain': p.domain,
                    'collection_weights': p.collection_weights,
                    'collection_stats': p.collection_stats,
                    'total_queries': p.total_queries,
                    'confidence': p.confidence,
                    'first_seen': p.first_seen.isoformat(),
                    'last_seen': p.last_seen.isoformat()
                }
                for p in self.domain_priority_patterns.values()
            ],
            'stats': self.get_pattern_stats()
        }

