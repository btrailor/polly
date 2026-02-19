"""
Conversation compressor for extended context retention.

Compresses conversations into structured format with 50x+ compression ratio
while preserving semantic meaning.

Also provides strategy selection for different compression types:
- LLM-based compression (existing): Best for conversation summaries
- LLMLingua compression (new): Fast algorithmic compression for RAG context
"""

import json
import re
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Any, Optional, Literal
from collections import Counter
import logging

from core.context.token_counter import TokenCounter

logger = logging.getLogger(__name__)


@dataclass
class CompressedConversation:
    """Compressed conversation format"""
    version: int
    user: str
    mode: str
    task_type: str
    depth: int
    decisions: list[dict]
    focus_topics: list[str]
    key_concepts: list[dict]
    context_critical: dict
    artifacts_created: list[dict]
    token_stats: dict
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    embedding_summary: Optional[list[float]] = None


CompressionStrategy = Literal["auto", "llmlingua", "llm_summary"]


class ConversationCompressor:
    """
    Compress conversations for extended context retention
    
    Phase 11c: Basic compression (50x)
    Phase 23: Advanced compression (100x) with embeddings
    
    Now supports multiple compression strategies:
    - "llm_summary": LLM-based conversation summarization (existing)
    - "llmlingua": Fast algorithmic compression for RAG context
    - "auto": Automatically choose strategy based on content type
    
    Usage:
        compressor = ConversationCompressor()
        compressed = compressor.compress(conversation)
        summary = compressor.decompress(compressed)
        
        # Or use strategy-based compression
        result = compressor.compress_with_strategy(text, strategy="llmlingua", ratio=0.5)
    """
    
    def __init__(self, config: Optional[dict] = None):
        self.version = 1
        self.config = config or {}
        
        # Lazy-load LLMLingua compressor
        self._llmlingua_compressor = None
        
        # Stop words for topic extraction (expand as needed)
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'under', 'again',
            'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
            'how', 'all', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
            'such', 'only', 'own', 'same', 'than', 'too', 'very', 'can', 'will',
            'just', 'should', 'now', 'this', 'that', 'these', 'those'
        }
    
    def compress(self, data: Any, type: str = "conversation", metadata: dict = None) -> dict:
        """
        Compress data into structured format.
        
        Supports:
        - type="conversation": Compress conversation history (existing behavior)
        - type="mental_model": Compress mental model to Compact Format (Phase 14)
        
        Args:
            data: Data to compress (conversation list or mental model dict)
            type: Type of compression ("conversation" or "mental_model")
            metadata: Additional context (optional)
        
        Returns:
            Compressed representation as dict (or str for mental_model)
        """
        if type == "mental_model":
            return self._compress_mental_model(data)
        elif type == "conversation":
            return self._compress_conversation(data, metadata)
        else:
            raise ValueError(f"Unknown compression type: {type}")
    
    def _compress_conversation(self, conversation: list[dict], metadata: dict = None) -> dict:
        """
        Compress conversation into structured format (original compress logic).
        
        Args:
            conversation: List of message dicts with 'role' and 'content'
            metadata: Additional context (optional)
        
        Returns:
            Compressed representation as dict
        """
        if not conversation:
            return self._empty_compression()
        
        # Extract key information
        user = self._extract_user(conversation)
        mode = self._detect_mode(conversation, metadata)
        task_type = self._classify_task(conversation)
        decisions = self._extract_decisions(conversation)
        focus_topics = self._extract_focus(conversation)
        key_concepts = self._extract_concepts(conversation)
        context = self._extract_critical_context(conversation, metadata)
        artifacts = self._extract_artifacts(conversation, metadata)
        
        # Calculate stats
        original_tokens = self._count_tokens(conversation)
        
        compressed = CompressedConversation(
            version=self.version,
            user=user,
            mode=mode,
            task_type=task_type,
            depth=len(conversation) // 2,  # Number of exchanges
            decisions=decisions,
            focus_topics=focus_topics,
            key_concepts=key_concepts,
            context_critical=context,
            artifacts_created=artifacts,
            token_stats={
                "original": original_tokens,
                "compressed": 0,  # Calculate after serialization
                "ratio": 0
            },
            start_time=conversation[0].get("timestamp") if conversation else None,
            end_time=conversation[-1].get("timestamp") if conversation else None
        )
        
        # Convert to dict
        compressed_dict = asdict(compressed)
        
        # Convert to ultra-compressed format (abbreviated keys)
        ultra_compressed = self._to_ultra_format(compressed_dict)
        
        # Calculate compressed size using ultra format
        compressed_json = json.dumps(ultra_compressed, separators=(',', ':'))
        compressed_tokens = TokenCounter.count(compressed_json)  # Accurate token count
        
        compressed_dict["token_stats"]["compressed"] = compressed_tokens
        compressed_dict["token_stats"]["ratio"] = (
            original_tokens / compressed_tokens if compressed_tokens > 0 else 0
        )
        
        # Store both formats in result
        compressed_dict["_ultra"] = ultra_compressed
        
        return compressed_dict
    
    def decompress(self, compressed: dict) -> str:
        """
        Convert compressed format to natural language summary
        
        This is what Polly uses when loading old conversations.
        Humans never see this format.
        
        Args:
            compressed: Compressed conversation dict
        
        Returns:
            Natural language summary for LLM context
        """
        template = """Previous conversation with {user} in {mode} mode.

Task: {task_type}
Duration: {depth} exchanges
Time: {start_time} to {end_time}

Key Decisions:
{decisions}

Focus Topics: {focus_topics}

Important Context:
{context}

Concepts Discussed:
{concepts}

Artifacts Created:
{artifacts}
"""
        
        return template.format(
            user=compressed.get("user", "User"),
            mode=compressed.get("mode", "chat"),
            task_type=compressed.get("task_type", "general"),
            depth=compressed.get("depth", 0),
            start_time=compressed.get("start_time", "unknown"),
            end_time=compressed.get("end_time", "unknown"),
            decisions=self._format_decisions(compressed.get("decisions", [])),
            focus_topics=", ".join(compressed.get("focus_topics", [])),
            context=self._format_context(compressed.get("context_critical", {})),
            concepts=self._format_concepts(compressed.get("key_concepts", [])),
            artifacts=self._format_artifacts(compressed.get("artifacts_created", []))
        )
    
    # ========== Extraction Methods ==========
    
    def _extract_user(self, conversation: list[dict]) -> str:
        """Extract primary user from conversation"""
        user_messages = [m for m in conversation if m.get("role") == "user"]
        if user_messages and user_messages[0].get("name"):
            return user_messages[0]["name"]
        return "User"
    
    def _detect_mode(self, conversation: list[dict], metadata: dict) -> str:
        """Detect conversation mode (chat, notes, code, etc.)"""
        if metadata and metadata.get("mode"):
            return metadata["mode"]
        
        # Analyze conversation content
        text = " ".join(m.get("content", "") for m in conversation).lower()
        
        mode_keywords = {
            "notes": ["note", "document", "write down", "record"],
            "code": ["code", "function", "class", "implement", "debug"],
            "search": ["search", "find", "look for", "locate"],
            "research": ["research", "learn", "explain", "understand"],
            "plan": ["plan", "design", "architecture", "strategy"]
        }
        
        for mode, keywords in mode_keywords.items():
            if any(kw in text for kw in keywords):
                return mode
        
        return "chat"
    
    def _classify_task(self, conversation: list[dict]) -> str:
        """Classify primary task type"""
        text = " ".join(m.get("content", "") for m in conversation).lower()
        
        task_keywords = {
            "note-creation": ["create note", "make note", "document", "write down"],
            "planning": ["plan", "design", "architecture", "strategy", "roadmap"],
            "coding": ["write code", "implement", "function", "class", "method"],
            "debugging": ["bug", "error", "fix", "issue", "problem"],
            "research": ["research", "learn", "explain", "understand", "how does"],
            "refactoring": ["refactor", "improve", "optimize", "restructure", "clean up"],
            "testing": ["test", "verify", "check", "validate"],
            "deployment": ["deploy", "release", "publish", "launch"]
        }
        
        # Count matches for each task type
        task_scores = {}
        for task, keywords in task_keywords.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                task_scores[task] = score
        
        # Return highest scoring task
        if task_scores:
            return max(task_scores, key=task_scores.get)
        
        return "general"
    
    def _extract_decisions(self, conversation: list[dict]) -> list[dict]:
        """Extract key decisions made during conversation"""
        decisions = []
        
        # Look for decision markers and number patterns
        decision_markers = [
            "decided", "chosen", "selected", "agreed",
            "will use", "going with", "final decision",
            "settled on", "confirmed", "approved"
        ]
        
        # Also look for explicit statements with numbers (e.g., "8 providers", "5 weeks")
        number_patterns = [
            (r'(\d+)\s+(provider|model|week|day|month|file|note)', 'quantity'),
            (r'we\s+(?:will|ll|should|need)\s+(.{5,40})', 'plan'),
            (r'(?:decided|chosen|selected)\s+(?:on\s+)?(.{5,40})', 'decision')
        ]
        
        for msg in conversation:
            content = msg.get("content", "")
            content_lower = content.lower()
            
            # Extract number-based decisions
            for pattern, decision_type in number_patterns:
                matches = re.findall(pattern, content_lower, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        decision_text = " ".join(str(m) for m in match)
                    else:
                        decision_text = match
                    
                    decisions.append({
                        "topic": decision_type,
                        "decision": decision_text.strip()[:50],
                        "confidence": 0.8
                    })
            
            # Extract marker-based decisions
            if msg.get("role") == "assistant":
                for marker in decision_markers:
                    if marker in content_lower:
                        # Extract context around marker
                        topic = self._extract_decision_topic(content, marker)
                        decision = self._extract_decision_value(content, marker)
                        
                        if topic and decision and decision != "unspecified":
                            decisions.append({
                                "topic": topic,
                                "decision": decision,
                                "confidence": 0.8
                            })
        
        # Deduplicate and limit
        unique_decisions = []
        seen = set()
        for d in decisions:
            key = f"{d['topic']}:{d['decision'][:20]}"
            if key not in seen:
                unique_decisions.append(d)
                seen.add(key)
        
        return unique_decisions[:10]  # Limit to top 10 decisions
    
    def _extract_decision_topic(self, content: str, marker: str) -> str:
        """Extract topic from decision context"""
        # Find sentence containing marker
        sentences = re.split(r'[.!?]', content)
        for sentence in sentences:
            if marker in sentence.lower():
                # Extract noun phrases (simplified)
                words = sentence.split()
                # Get words before marker
                marker_words = marker.split()
                try:
                    marker_idx = -1
                    for i, word in enumerate(words):
                        if word.lower().startswith(marker_words[0]):
                            marker_idx = i
                            break
                    
                    if marker_idx > 0:
                        # Get 2-3 words before marker as topic
                        topic_words = words[max(0, marker_idx - 3):marker_idx]
                        return " ".join(topic_words).strip()
                except:
                    pass
        
        return "unspecified"
    
    def _extract_decision_value(self, content: str, marker: str) -> str:
        """Extract decision value from context"""
        # Find sentence containing marker
        sentences = re.split(r'[.!?]', content)
        for sentence in sentences:
            if marker in sentence.lower():
                # Extract phrase after marker
                parts = sentence.lower().split(marker, 1)
                if len(parts) == 2:
                    # Get first few words after marker
                    after = parts[1].strip().split()[:5]
                    return " ".join(after).strip()
        
        return "unspecified"
    
    def _extract_focus(self, conversation: list[dict]) -> list[str]:
        """Extract main focus topics using frequency analysis"""
        text = " ".join(m.get("content", "") for m in conversation)
        
        # Tokenize and clean
        words = re.findall(r'\b[a-z]+\b', text.lower())
        
        # Filter stop words and short words
        meaningful_words = [
            w for w in words 
            if len(w) > 4 and w not in self.stop_words
        ]
        
        # Count frequencies
        word_freq = Counter(meaningful_words)
        
        # Get top 5 most frequent meaningful words
        top_words = word_freq.most_common(5)
        
        return [word for word, count in top_words]
    
    def _extract_concepts(self, conversation: list[dict]) -> list[dict]:
        """Extract key concepts with definitions"""
        concepts = []
        
        # Look for definition patterns
        definition_patterns = [
            (r'(.+?)\s+is\s+(.+?)[\.\n]', ' is '),
            (r'(.+?)\s+means\s+(.+?)[\.\n]', ' means '),
            (r'(.+?)\s+refers to\s+(.+?)[\.\n]', ' refers to '),
            (r'(.+?)\s+defined as\s+(.+?)[\.\n]', ' defined as ')
        ]
        
        for msg in conversation:
            content = msg.get("content", "")
            
            for pattern, marker in definition_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                
                for match in matches:
                    term = match.group(1).strip()
                    definition = match.group(2).strip()
                    
                    # Clean up term (get last few words)
                    term_words = term.split()[-3:]
                    clean_term = " ".join(term_words)
                    
                    # Truncate definition
                    clean_def = definition[:100]
                    
                    if clean_term and clean_def:
                        concepts.append({
                            "term": clean_term,
                            "definition": clean_def
                        })
        
        # Deduplicate
        unique_concepts = []
        seen_terms = set()
        for c in concepts:
            if c["term"] not in seen_terms:
                unique_concepts.append(c)
                seen_terms.add(c["term"])
        
        return unique_concepts[:10]  # Limit to top 10 concepts
    
    def _extract_critical_context(self, conversation: list[dict], metadata: dict) -> dict:
        """Extract context that must be preserved"""
        context = {}
        
        # Extract from metadata if available
        if metadata:
            for key, value in metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    context[key] = value
                elif isinstance(value, dict):
                    # Flatten nested dicts
                    for nested_key, nested_value in value.items():
                        if isinstance(nested_value, (str, int, float, bool)):
                            context[f"{key}_{nested_key}"] = nested_value
        
        # Extract numbers and quantities from conversation
        text = " ".join(m.get("content", "") for m in conversation)
        
        # Find numbers with context
        number_patterns = [
            (r'(\d+)\s+(?:providers?|models?|sources?)', 'count'),
            (r'(\d+)\s+(?:weeks?|days?|hours?)', 'timeline'),
            (r'(\d+)\s+(?:files?|notes?|documents?)', 'files'),
            (r'(\d+)%', 'percentage')
        ]
        
        for pattern, context_type in number_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches and context_type not in context:
                context[context_type] = matches[0]
        
        return context
    
    def _extract_artifacts(self, conversation: list[dict], metadata: dict) -> list[dict]:
        """Extract created artifacts (notes, code files, etc.)"""
        artifacts = []
        
        # Check metadata first
        if metadata and metadata.get("artifacts"):
            return metadata["artifacts"]
        
        # Look for file creation mentions with more flexible patterns
        file_patterns = [
            r'created?\s+(?:file|note|document)?\s*:?\s*([^\s\n]+\.(?:md|py|js|txt|json|html|css|java|cpp|h|c|rs|go|rb|php))',
            r'wrote\s+(?:to\s+)?([^\s\n]+\.(?:md|py|js|txt|json|html|css))',
            r'saved\s+(?:as|to|the\s+documentation\s+to)?\s*([^\s\n]+\.(?:md|py|js|txt|json))',
            r'(?:file|note)\s+called\s+([^\s\n]+\.(?:md|py|js|txt|json))',
            r'(?:created|made|wrote)\s+[a\s]*(?:file|note)\s+(?:called\s+|named\s+)?([^\s\n]+\.(?:md|py|js|txt|json))',
            r'(?:in|to)\s+([^\s\n]+\.(?:md|py|js|txt|json))',
            r'recommend\s+[\'"]?([^\s\'"]+\.(?:md|py|js|txt|json))',
            r'I\'ve\s+created\s+(?:file\s+)?([^\s\n]+\.(?:md|py|js|txt|json))'
        ]
        
        for msg in conversation:
            content = msg.get("content", "")
            
            for pattern in file_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    filename = match.strip().strip('"\'.,;')
                    
                    # Skip if looks invalid
                    if not filename or len(filename) < 3:
                        continue
                    
                    # Determine artifact type from extension
                    if filename.endswith('.md'):
                        artifact_type = 'note'
                    elif filename.endswith(('.py', '.js', '.java', '.cpp', '.c', '.h', '.rs', '.go', '.rb', '.php')):
                        artifact_type = 'code'
                    elif filename.endswith('.json'):
                        artifact_type = 'config'
                    elif filename.endswith(('.html', '.css')):
                        artifact_type = 'web'
                    else:
                        artifact_type = 'file'
                    
                    artifacts.append({
                        "type": artifact_type,
                        "title": filename,
                        "file": filename
                    })
        
        # Deduplicate
        unique_artifacts = []
        seen_files = set()
        for a in artifacts:
            if a["file"] not in seen_files:
                unique_artifacts.append(a)
                seen_files.add(a["file"])
        
        return unique_artifacts[:20]  # Limit to 20 artifacts
    
    def _count_tokens(self, conversation: list[dict]) -> int:
        """Estimate token count for conversation"""
        text = " ".join(m.get("content", "") for m in conversation)
        return TokenCounter.count(text)
    
    # ========== Formatting Methods ==========
    
    def _format_decisions(self, decisions: list[dict]) -> str:
        """Format decisions for decompressed output"""
        if not decisions:
            return "None recorded"
        
        lines = []
        for d in decisions:
            confidence = d.get('confidence', 0.8)
            lines.append(
                f"- {d['topic']}: {d['decision']} "
                f"(confidence: {confidence:.0%})"
            )
        return "\n".join(lines)
    
    def _format_context(self, context: dict) -> str:
        """Format critical context"""
        if not context:
            return "None recorded"
        
        lines = []
        for key, value in context.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)
    
    def _format_concepts(self, concepts: list[dict]) -> str:
        """Format key concepts"""
        if not concepts:
            return "None recorded"
        
        lines = []
        for c in concepts:
            lines.append(f"- {c['term']}: {c['definition']}")
        return "\n".join(lines)
    
    def _format_artifacts(self, artifacts: list[dict]) -> str:
        """Format created artifacts"""
        if not artifacts:
            return "None"
        
        lines = []
        for a in artifacts:
            file_info = a.get('file', 'no file')
            lines.append(f"- {a['type']}: {a['title']} ({file_info})")
        return "\n".join(lines)
    
    # ========== Ultra-Compression Methods ==========
    
    def _to_ultra_format(self, compressed: dict) -> dict:
        """
        Convert to ultra-compressed format with abbreviated keys
        
        This is the format actually stored in database for maximum compression.
        Uses single-letter keys and compact representations.
        
        Abbreviation key:
        - v: version
        - u: user
        - m: mode
        - t: task_type
        - d: depth
        - dc: decisions
        - f: focus_topics
        - kc: key_concepts (compact string format)
        - ctx: context_critical
        - a: artifacts_created (compact format)
        - st: start_time (shortened)
        - et: end_time (shortened)
        """
        ultra = {
            "v": compressed["version"],
            "u": compressed["user"],
            "m": compressed["mode"],
            "t": compressed["task_type"],
            "d": compressed["depth"]
        }
        
        # Compress decisions (abbreviated keys)
        if compressed["decisions"]:
            ultra["dc"] = [
                {
                    "t": d["topic"][:20],  # Truncate topic
                    "d": d["decision"][:30],  # Truncate decision
                    "c": round(d["confidence"], 2)  # 2 decimal places
                }
                for d in compressed["decisions"][:5]  # Limit to 5
            ]
        
        # Compress focus topics (just array of strings)
        if compressed["focus_topics"]:
            ultra["f"] = compressed["focus_topics"][:5]
        
        # Compress concepts (compact string format)
        if compressed["key_concepts"]:
            ultra["kc"] = [
                f"{c['term'][:15]}:{c['definition'][:40]}"  # Compact format
                for c in compressed["key_concepts"][:5]
            ]
        
        # Compress context (keep critical only, short keys)
        if compressed["context_critical"]:
            ultra["ctx"] = {
                k[:10]: str(v)[:20]  # Truncate keys and values
                for k, v in list(compressed["context_critical"].items())[:10]
            }
        
        # Compress artifacts (compact format)
        if compressed["artifacts_created"]:
            ultra["a"] = [
                f"{a['type'][0]}:{a['title'][:30]}"  # Format: "n:filename.md"
                for a in compressed["artifacts_created"][:10]
            ]
        
        # Compress timestamps (remove date, keep time only)
        if compressed.get("start_time"):
            ultra["st"] = self._compress_timestamp(compressed["start_time"])
        
        if compressed.get("end_time"):
            ultra["et"] = self._compress_timestamp(compressed["end_time"])
        
        return ultra
    
    def _compress_timestamp(self, timestamp: Optional[str]) -> Optional[str]:
        """Compress timestamp to minimal format"""
        if not timestamp:
            return None
        
        # Extract just the time portion (HH:MM)
        try:
            if 'T' in timestamp:
                time_part = timestamp.split('T')[1][:5]  # HH:MM
                return time_part
            return timestamp[:5]
        except:
            return None
    
    def _empty_compression(self) -> dict:
        """Return empty compression for empty conversation"""
        return {
            "version": self.version,
            "user": "User",
            "mode": "chat",
            "task_type": "general",
            "depth": 0,
            "decisions": [],
            "focus_topics": [],
            "key_concepts": [],
            "context_critical": {},
            "artifacts_created": [],
            "token_stats": {
                "original": 0,
                "compressed": 0,
                "ratio": 0
            },
            "start_time": None,
            "end_time": None
        }
    
    # ========== Mental Model Compact Format Compression (Phase 14) ==========
    
    def _compress_mental_model(self, model: dict) -> str:
        """
        Compress mental model to Compact Format (formerly PIL).
        
        Compact Format:
        MM:id|m:mode|p:[principles]|pi:prompt|d:[domains]|pg:[pages]|ps:[personas]|pm:[modes]|k:[keywords]
        
        Symbol system:
        > = over/instead of
        ↻ = evolving/iterative
        ↑ = increase/grow
        → = leads to/causes
        ⇄ = bidirectional/mutual
        + = addition/combination
        & = and/with
        ? = question/explore
        ! = important/emphasis
        
        Args:
            model: Mental model dict with standard fields
            
        Returns:
            Compact-format string achieving 2.5-3x compression
        """
        parts = []
        
        # ID (required)
        parts.append(f"MM:{model['id']}")
        
        # Extract mode from name or description
        mode = self._extract_mode(model)
        if mode:
            parts.append(f"m:{mode}")
        
        # Compress principles (top 5, symbol-ized)
        if model.get('principles'):
            compressed_principles = self._compress_principles(model['principles'][:5])
            parts.append(f"p:[{compressed_principles}]")
        
        # Compress prompt injection
        if model.get('prompt_injection'):
            compressed_prompt = self._compress_prompt(model['prompt_injection'])
            parts.append(f"pi:{compressed_prompt}")
        
        # Domains (abbreviated)
        if model.get('applies_to'):
            domains = ','.join(model['applies_to'][:5])
            parts.append(f"d:[{domains}]")
        
        # Pages (abbreviated)
        if model.get('active_on_pages'):
            pages = ','.join(self._abbreviate_pages(model['active_on_pages'][:5]))
            parts.append(f"pg:[{pages}]")
        
        # Personas
        if model.get('active_for_personas'):
            personas = ','.join(model['active_for_personas'][:3])
            parts.append(f"ps:[{personas}]")
        
        # Modes
        if model.get('active_for_modes'):
            modes = ','.join(model['active_for_modes'][:3])
            parts.append(f"pm:[{modes}]")
        
        # Keywords (top 3-5)
        if model.get('keywords'):
            keywords = ','.join(model['keywords'][:5])
            parts.append(f"k:[{keywords}]")
        
        # Join all parts
        compressed = '|'.join(parts)
        
        return compressed
    
    def _extract_mode(self, model: dict) -> str:
        """
        Extract mode/essence from model name and description.
        
        Returns:
            Short mode descriptor (e.g., "dialogue", "systems", "pedagogy")
        """
        name = model.get('name', '').lower()
        desc = model.get('description', '').lower()
        
        # Mode keywords mapping
        mode_keywords = {
            'dialogue': ['dialogue', 'conversation', 'exchange', 'socratic'],
            'pedagogy': ['education', 'teaching', 'learning', 'pedagogy', 'freire'],
            'systems': ['system', 'interconnection', 'feedback', 'emergence'],
            'design': ['design', 'prototype', 'empathize', 'iterate'],
            'analysis': ['analyze', 'break down', 'deconstruct', 'reverse'],
            'principles': ['principle', 'fundamental', 'truth', 'assumption'],
            'generative': ['generative', 'instrument', 'tool', 'create'],
            'game': ['game', 'infinite', 'finite', 'continuation'],
            'constraint': ['constraint', 'boundary', 'limitation', 'form'],
            'productivity': ['productivity', 'inbox', 'schedule', 'time'],
            'communication': ['communication', 'async', 'message', 'written']
        }
        
        # Check name and description for mode keywords
        text = name + ' ' + desc
        for mode, keywords in mode_keywords.items():
            if any(kw in text for kw in keywords):
                return mode
        
        return 'general'
    
    def _compress_principles(self, principles: list[str]) -> str:
        """
        Compress principles using compact symbol system.
        
        Symbols:
        > = over/instead of
        ↻ = evolving/iterative
        ↑ = increase/grow
        → = leads to/causes
        ⇄ = bidirectional/mutual
        + = addition/combination
        & = and/with
        ? = question/explore
        ! = important/emphasis
        
        Args:
            principles: List of principle strings
            
        Returns:
            Compressed principles string with symbols
        """
        compressed = []
        
        for principle in principles:
            p = principle.lower()
            
            # Apply symbol replacements
            # "X over Y" → "X>Y"
            p = re.sub(r'(\w+)\s+over\s+(\w+)', r'\1>\2', p)
            p = re.sub(r'(\w+)\s+rather than\s+(\w+)', r'\1>\2', p)
            p = re.sub(r'(\w+)\s+instead of\s+(\w+)', r'\1>\2', p)
            
            # "evolving X" → "X↻"
            p = re.sub(r'evolving\s+(\w+)', r'\1↻', p)
            p = re.sub(r'iterative\s+(\w+)', r'\1↻', p)
            
            # "increase X" → "↑X"
            p = re.sub(r'increase\s+(\w+)', r'↑\1', p)
            p = re.sub(r'growing\s+(\w+)', r'↑\1', p)
            
            # "X leads to Y" → "X→Y"
            p = re.sub(r'(\w+)\s+leads to\s+(\w+)', r'\1→\2', p)
            p = re.sub(r'(\w+)\s+causes\s+(\w+)', r'\1→\2', p)
            
            # "X and Y together" → "X⇄Y"
            p = re.sub(r'(\w+)\s+and\s+(\w+)\s+together', r'\1⇄\2', p)
            p = re.sub(r'mutual\s+(\w+)', r'\1⇄', p)
            
            # "X plus Y" → "X+Y"
            p = re.sub(r'(\w+)\s+plus\s+(\w+)', r'\1+\2', p)
            p = re.sub(r'(\w+)\s+and\s+(\w+)', r'\1&\2', p)
            
            # "question X" → "?X"
            if 'question' in p or 'explore' in p:
                p = '?' + p.replace('question', '').replace('explore', '').strip()
            
            # Important markers
            if 'critical' in p or 'essential' in p or 'key' in p or 'important' in p:
                p = '!' + p.replace('critical', '').replace('essential', '').replace('key', '').replace('important', '').strip()
            
            # Remove common words
            p = re.sub(r'\b(the|a|an|of|from|to|for|with|by|in|on|at)\b', '', p)
            
            # Collapse whitespace
            p = re.sub(r'\s+', ' ', p).strip()
            
            # Truncate if too long
            if len(p) > 40:
                p = p[:40]
            
            compressed.append(p)
        
        return ','.join(compressed)
    
    def _compress_prompt(self, prompt: str) -> str:
        """
        Compress prompt injection to essential keywords.
        
        Extracts key action words and concepts from prompt.
        
        Args:
            prompt: Full prompt injection string
            
        Returns:
            Compressed prompt (max 5-7 keywords)
        """
        # Extract key action words
        action_words = [
            'question', 'ask', 'explore', 'analyze', 'build', 'create',
            'design', 'implement', 'consider', 'focus', 'emphasize',
            'reveal', 'guide', 'teach', 'learn', 'dialogue', 'discuss',
            'break down', 'deconstruct', 'prototype', 'iterate', 'test',
            'document', 'process', 'schedule', 'batch', 'minimize'
        ]
        
        # Find action words in prompt
        prompt_lower = prompt.lower()
        found_actions = [word for word in action_words if word in prompt_lower]
        
        # Extract important nouns/concepts using simple heuristics
        # Look for capitalized words or quoted concepts
        concepts = re.findall(r'"([^"]+)"', prompt)
        concepts.extend(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', prompt))
        
        # Combine actions + concepts
        keywords = found_actions[:3] + [c.lower() for c in concepts[:3]]
        
        # Apply symbols to keywords
        result = []
        for kw in keywords:
            if kw in ['question', 'ask', 'explore']:
                result.append('?')
            elif kw in ['emphasize', 'important', 'critical']:
                result.append('!')
            else:
                result.append(kw)
        
        return ','.join(result[:7])
    
    def _abbreviate_pages(self, pages: list[str]) -> list[str]:
        """
        Abbreviate page names for compression.
        
        Args:
            pages: List of page names
            
        Returns:
            List of abbreviated page names
        """
        abbreviations = {
            'dashboard': 'dash',
            'calendar': 'cal',
            'learning': 'learn',
            'projects': 'proj',
            'knowledge': 'know',
            'patterns': 'patt',
            'settings': 'set'
        }
        
        return [abbreviations.get(page, page) for page in pages]
    
    # ========== Strategy-Based Compression (New) ==========
    
    def compress_with_strategy(
        self,
        text: str,
        strategy: CompressionStrategy = "auto",
        target_ratio: float = 0.5,
        context_type: str = "rag_context"
    ) -> dict:
        """
        Compress text using specified strategy.
        
        Args:
            text: Text to compress
            strategy: Compression strategy ("auto", "llmlingua", "llm_summary")
            target_ratio: Target compression ratio (0.1-1.0) for LLMLingua
            context_type: Type of content ("rag_context", "conversation", "prompt")
        
        Returns:
            Dict with compressed text and metrics
        """
        # Auto strategy: choose based on context type
        if strategy == "auto":
            if context_type == "conversation":
                strategy = "llm_summary"
            else:
                strategy = "llmlingua"
        
        # Route to appropriate compressor
        if strategy == "llmlingua":
            return self._compress_with_llmlingua(text, target_ratio, context_type)
        elif strategy == "llm_summary":
            # For now, LLM summary only works on conversation format
            # For raw text, we'd need to implement a text summarization method
            logger.warning(
                f"LLM summary compression not yet implemented for raw text. "
                f"Falling back to LLMLingua."
            )
            return self._compress_with_llmlingua(text, target_ratio, context_type)
        else:
            raise ValueError(f"Unknown compression strategy: {strategy}")
    
    def _compress_with_llmlingua(
        self,
        text: str,
        target_ratio: float,
        context_type: str
    ) -> dict:
        """
        Compress text using LLMLingua.
        
        Args:
            text: Text to compress
            target_ratio: Target compression ratio
            context_type: Type of content
        
        Returns:
            Dict with compressed text and metrics
        """
        # Lazy-load LLMLingua compressor
        if self._llmlingua_compressor is None:
            try:
                from .llmlingua_strategy import LLMLinguaCompressor
                
                # Get config for LLMLingua
                llmlingua_config = self.config.get("llmlingua", {})
                
                self._llmlingua_compressor = LLMLinguaCompressor(
                    target_ratio=target_ratio,
                    model_name=llmlingua_config.get(
                        "model",
                        "microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank"
                    ),
                    device=llmlingua_config.get("device", "cpu")
                )
                logger.info("LLMLingua compressor initialized")
            except ImportError as e:
                logger.error(f"Failed to import LLMLingua: {e}")
                # Return uncompressed as fallback
                return {
                    "compressed_text": text,
                    "original_tokens": TokenCounter.count(text),
                    "compressed_tokens": TokenCounter.count(text),
                    "compression_ratio": 1.0,
                    "strategy": "none",
                    "error": "llmlingua_not_available"
                }
        
        # Compress
        result = self._llmlingua_compressor.compress(
            text,
            target_ratio=target_ratio,
            context_type=context_type
        )
        
        return {
            "compressed_text": result.compressed_text,
            "original_tokens": result.original_tokens,
            "compressed_tokens": result.compressed_tokens,
            "compression_ratio": result.compression_ratio,
            "strategy": "llmlingua",
            "metadata": result.metadata
        }
    
    def get_strategy_for_context(self, context_type: str) -> CompressionStrategy:
        """
        Get recommended compression strategy for context type.
        
        Args:
            context_type: Type of content
        
        Returns:
            Recommended compression strategy
        """
        strategy_map = {
            "conversation": "llm_summary",
            "rag_context": "llmlingua",
            "prompt": "llmlingua",
            "mental_model": "llm_summary"
        }
        
        return strategy_map.get(context_type, "llmlingua")