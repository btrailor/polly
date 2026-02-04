# Phase 11: Compression System Specification

**Document Version:** 1.0  
**Last Updated:** January 28, 2026  
**Status:** Basic implementation in Phase 11c, Full in Phase 23  
**Related:** [PHASE11_MULTI_MODEL_ENHANCED_V2.md](./PHASE11_MULTI_MODEL_ENHANCED_V2.md)

---

## Executive Summary

This document specifies Polly's internal compression language for extending conversation context retention. The compression system reduces token usage by 50-100x while preserving semantic meaning, allowing Polly to maintain context across much longer conversations.

**Critical Requirement:** This compression format is **ONLY for Polly's internal use**. Humans never see or edit compressed conversations.

**Goals:**
- 50x+ compression ratio initially (Phase 11c)
- 100x+ compression ratio eventually (Phase 23)
- 95%+ semantic accuracy preservation
- Fast compression/decompression (< 1s)
- Backward compatible format versioning

---

## Why Compression?

### The Context Window Problem

**Current State:**
- Average conversation: 10,000-50,000 tokens
- Model context limits: 128K-200K tokens
- After ~10-20 exchanges, context is lost
- Cost increases linearly with conversation length

**With Compression:**
- Compress old messages: 50,000 tokens → 500 tokens
- Keep recent messages uncompressed
- Extend effective conversation memory 10-50x
- Dramatically reduce API costs

### Compression Strategy

```
┌────────────────────────────────────────────────────┐
│         Conversation Timeline                      │
├────────────────────────────────────────────────────┤
│                                                     │
│  Old Messages (>100 turns ago)                    │
│  ████████████████████                             │
│  → Highly compressed (100x)                       │
│  → Summary format only                            │
│                                                     │
│  ─────────────────────────────────────────────────│
│                                                     │
│  Medium Messages (10-100 turns ago)               │
│  ████████████████████████████████                 │
│  → Moderately compressed (50x)                    │
│  → Structured metadata + key points               │
│                                                     │
│  ─────────────────────────────────────────────────│
│                                                     │
│  Recent Messages (< 10 turns)                     │
│  ████████████████████████████████████████         │
│  → Uncompressed                                    │
│  → Full message history                           │
│                                                     │
└────────────────────────────────────────────────────┘
```

---

## Compression Format (v1)

### JSON Structure

```json
{
  "version": 1,
  "user": "Brett",
  "mode": "notes",
  "task_type": "note-creation",
  "depth": 12,
  "start_time": "2026-01-28T10:00:00Z",
  "end_time": "2026-01-28T11:30:00Z",
  
  "decisions": [
    {"topic": "storage", "decision": "external folders", "confidence": 0.95},
    {"topic": "providers", "decision": "8 providers", "confidence": 1.0},
    {"topic": "timeline", "decision": "5 weeks", "confidence": 0.9}
  ],
  
  "focus_topics": ["multi-model-routing", "note-creation", "grok-safety"],
  
  "key_concepts": [
    {"term": "Architect persona", "definition": "Plan/Build modes for structured tasks"},
    {"term": "Grok safety", "definition": "Content filtering for conspiracy/extremism"}
  ],
  
  "context_critical": {
    "providers_count": 8,
    "timeline_weeks": 5,
    "safety_filters": "mandatory for Grok",
    "storage_location": "external",
    "mode_switching": "manual"
  },
  
  "artifacts_created": [
    {"type": "note", "title": "Phase 11 Planning", "file": "phase-11-planning.md"},
    {"type": "spec", "title": "Provider Specifications", "file": "PHASE11_PROVIDERS.md"}
  ],
  
  "embedding_summary": [0.234, -0.123, 0.456, ...],  // 768d vector
  
  "token_stats": {
    "original": 50000,
    "compressed": 500,
    "ratio": 100
  }
}
```

### Abbreviation System

For ultra-compression, use abbreviations:

```json
{
  "v": 1,                    // version
  "u": "Brett",              // user
  "m": "notes",              // mode
  "t": "note-creation",      // task
  "d": 12,                   // depth (turns)
  "dc": [                    // decisions
    {"t": "storage", "d": "external", "c": 0.95},
    {"t": "providers", "d": "8", "c": 1.0}
  ],
  "f": ["routing", "notes"], // focus
  "kc": [                    // key concepts
    "Architect:plan-build",
    "Grok:safety-filters"
  ],
  "ctx": {                   // critical context
    "p": 8,                  // providers
    "w": 5,                  // weeks
    "s": "grok-filter"       // safety
  },
  "emb": [0.234, -0.123, ...] // embedding
}
```

---

## Implementation (Phase 11c - Basic)

### Compressor Class

```python
# core/compression/compressor.py
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any

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
    start_time: str = None
    end_time: str = None
    embedding_summary: list[float] = None

class ConversationCompressor:
    """
    Compress conversations for extended context retention
    
    Phase 11c: Basic compression (50x)
    Phase 23: Advanced compression (100x) with embeddings
    """
    
    def __init__(self):
        self.version = 1
    
    def compress(self, conversation: list[dict], metadata: dict = None) -> dict:
        """
        Compress conversation into structured format
        
        Args:
            conversation: List of message dicts
            metadata: Additional context
        
        Returns:
            Compressed representation as dict
        """
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
        
        # Calculate compressed size
        compressed_json = json.dumps(compressed_dict)
        compressed_tokens = len(compressed_json) // 4  # Rough estimate
        
        compressed_dict["token_stats"]["compressed"] = compressed_tokens
        compressed_dict["token_stats"]["ratio"] = original_tokens / compressed_tokens if compressed_tokens > 0 else 0
        
        return compressed_dict
    
    def decompress(self, compressed: dict) -> str:
        """
        Convert compressed format to natural language summary
        
        This is what Polly uses when loading old conversations.
        Humans never see this format.
        
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
            user=compressed["user"],
            mode=compressed["mode"],
            task_type=compressed["task_type"],
            depth=compressed["depth"],
            start_time=compressed.get("start_time", "unknown"),
            end_time=compressed.get("end_time", "unknown"),
            decisions=self._format_decisions(compressed["decisions"]),
            focus_topics=", ".join(compressed["focus_topics"]),
            context=self._format_context(compressed["context_critical"]),
            concepts=self._format_concepts(compressed["key_concepts"]),
            artifacts=self._format_artifacts(compressed["artifacts_created"])
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
        
        if "note" in text or "document" in text:
            return "notes"
        elif "code" in text or "function" in text:
            return "code"
        elif "search" in text or "find" in text:
            return "search"
        else:
            return "chat"
    
    def _classify_task(self, conversation: list[dict]) -> str:
        """Classify primary task type"""
        text = " ".join(m.get("content", "") for m in conversation).lower()
        
        task_keywords = {
            "note-creation": ["create note", "make note", "document"],
            "planning": ["plan", "design", "architecture", "strategy"],
            "coding": ["write code", "implement", "function", "class"],
            "debugging": ["bug", "error", "fix", "issue"],
            "research": ["research", "learn", "explain", "understand"],
            "refactoring": ["refactor", "improve", "optimize", "restructure"]
        }
        
        for task, keywords in task_keywords.items():
            if any(kw in text for kw in keywords):
                return task
        
        return "general"
    
    def _extract_decisions(self, conversation: list[dict]) -> list[dict]:
        """Extract key decisions made during conversation"""
        decisions = []
        
        # Look for decision markers
        decision_markers = [
            "decided", "chosen", "selected", "agreed",
            "will use", "going with", "final decision"
        ]
        
        for msg in conversation:
            if msg.get("role") != "assistant":
                continue
            
            content = msg.get("content", "").lower()
            for marker in decision_markers:
                if marker in content:
                    # Extract context around marker
                    decisions.append({
                        "topic": self._extract_decision_topic(content, marker),
                        "decision": self._extract_decision_value(content, marker),
                        "confidence": 0.8  # Placeholder
                    })
        
        return decisions[:10]  # Limit to top 10 decisions
    
    def _extract_focus(self, conversation: list[dict]) -> list[str]:
        """Extract main focus topics"""
        # Use TF-IDF or similar to identify key topics
        # For basic implementation, use keyword extraction
        
        text = " ".join(m.get("content", "") for m in conversation)
        
        # Simple keyword extraction (improve in Phase 23)
        words = text.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 4:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top 5 most frequent meaningful words
        topics = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        return [topic[0] for topic in topics]
    
    def _extract_concepts(self, conversation: list[dict]) -> list[dict]:
        """Extract key concepts with definitions"""
        concepts = []
        
        # Look for definition patterns
        definition_markers = [
            " is ", " means ", " refers to ", "defined as"
        ]
        
        for msg in conversation:
            content = msg.get("content", "")
            for marker in definition_markers:
                if marker in content:
                    # Extract term and definition
                    parts = content.split(marker, 1)
                    if len(parts) == 2:
                        term = parts[0].split()[-3:]  # Last few words before marker
                        definition = parts[1].split(".")[0]  # First sentence
                        
                        concepts.append({
                            "term": " ".join(term),
                            "definition": definition[:100]  # Truncate
                        })
        
        return concepts[:10]  # Limit to top 10 concepts
    
    def _extract_critical_context(self, conversation: list[dict], metadata: dict) -> dict:
        """Extract context that must be preserved"""
        context = {}
        
        # Extract from metadata if available
        if metadata:
            for key, value in metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    context[key] = value
        
        # Add conversation-specific context
        # (Implementation depends on conversation analysis)
        
        return context
    
    def _extract_artifacts(self, conversation: list[dict], metadata: dict) -> list[dict]:
        """Extract created artifacts (notes, code, etc.)"""
        artifacts = []
        
        if metadata and metadata.get("artifacts"):
            artifacts = metadata["artifacts"]
        
        return artifacts
    
    def _count_tokens(self, conversation: list[dict]) -> int:
        """Estimate token count for conversation"""
        text = " ".join(m.get("content", "") for m in conversation)
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4
    
    # ========== Formatting Methods ==========
    
    def _format_decisions(self, decisions: list[dict]) -> str:
        """Format decisions for decompressed output"""
        if not decisions:
            return "None recorded"
        
        lines = []
        for d in decisions:
            lines.append(f"- {d['topic']}: {d['decision']} (confidence: {d['confidence']:.0%})")
        return "\n".join(lines)
    
    def _format_context(self, context: dict) -> str:
        """Format critical context"""
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
            lines.append(f"- {a['type']}: {a['title']} ({a.get('file', 'no file')})")
        return "\n".join(lines)
```

---

## Storage & Usage

### Database Storage

```sql
CREATE TABLE conversation_compression (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER NOT NULL,
    version INTEGER NOT NULL,
    compressed_data TEXT NOT NULL,  -- JSON blob
    original_tokens INTEGER,
    compressed_tokens INTEGER,
    compression_ratio REAL,
    created_at DATETIME,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

CREATE INDEX idx_compression_conversation ON conversation_compression(conversation_id);
```

### When to Compress

```python
# core/compression/manager.py
class CompressionManager:
    """Manage conversation compression lifecycle"""
    
    COMPRESSION_THRESHOLD = 10  # Compress after 10 exchanges
    COMPRESSION_AGE = 24 * 60 * 60  # Or after 24 hours
    
    async def should_compress(self, conversation_id: int) -> bool:
        """Check if conversation should be compressed"""
        conv = await self.db.get_conversation(conversation_id)
        
        # Check message count
        message_count = len(conv.messages)
        if message_count > self.COMPRESSION_THRESHOLD * 2:
            return True
        
        # Check age
        age = (datetime.now() - conv.created_at).total_seconds()
        if age > self.COMPRESSION_AGE and message_count > self.COMPRESSION_THRESHOLD:
            return True
        
        return False
    
    async def compress_conversation(self, conversation_id: int):
        """Compress old messages in conversation"""
        conv = await self.db.get_conversation(conversation_id)
        
        # Keep recent messages uncompressed
        recent_count = 10
        old_messages = conv.messages[:-recent_count]
        recent_messages = conv.messages[-recent_count:]
        
        if not old_messages:
            return  # Nothing to compress
        
        # Compress old messages
        compressor = ConversationCompressor()
        compressed = compressor.compress(old_messages, conv.metadata)
        
        # Store compressed version
        await self.db.insert("conversation_compression", {
            "conversation_id": conversation_id,
            "version": compressed["version"],
            "compressed_data": json.dumps(compressed),
            "original_tokens": compressed["token_stats"]["original"],
            "compressed_tokens": compressed["token_stats"]["compressed"],
            "compression_ratio": compressed["token_stats"]["ratio"],
            "created_at": datetime.now()
        })
        
        # Remove old messages from active conversation
        await self.db.archive_messages(conversation_id, old_messages)
        
        logger.info(f"Compressed {len(old_messages)} messages: "
                   f"{compressed['token_stats']['original']} → "
                   f"{compressed['token_stats']['compressed']} tokens "
                   f"({compressed['token_stats']['ratio']:.1f}x)")
```

### Loading Compressed Context

```python
# core/conversation.py
class Conversation:
    
    async def load_context(self) -> list[dict]:
        """
        Load conversation context with compression
        
        Returns:
            List of messages (recent + decompressed summary)
        """
        messages = []
        
        # Check if compressed version exists
        compressed = await self.db.get_compressed(self.id)
        
        if compressed:
            # Add decompressed summary as system message
            compressor = ConversationCompressor()
            summary = compressor.decompress(json.loads(compressed["compressed_data"]))
            
            messages.append({
                "role": "system",
                "content": f"Conversation history summary:\n\n{summary}"
            })
        
        # Add recent messages (uncompressed)
        recent = await self.db.get_recent_messages(self.id, limit=10)
        messages.extend(recent)
        
        return messages
```

---

## Phase 23: Advanced Compression

### Semantic Embeddings

In Phase 23, add embedding-based compression:

```python
class AdvancedCompressor(ConversationCompressor):
    """Advanced compression with embeddings"""
    
    def __init__(self, embedding_model):
        super().__init__()
        self.embedding_model = embedding_model
    
    async def compress(self, conversation: list[dict], metadata: dict = None) -> dict:
        """Compress with semantic embeddings"""
        # Basic compression
        compressed = super().compress(conversation, metadata)
        
        # Add semantic embedding
        text = " ".join(m.get("content", "") for m in conversation)
        embedding = await self.embedding_model.embed(text)
        
        compressed["embedding_summary"] = embedding.tolist()
        compressed["embedding_model"] = self.embedding_model.name
        
        return compressed
    
    async def semantic_search(self, query: str, compressed_convs: list[dict]) -> list[dict]:
        """Search compressed conversations by semantic similarity"""
        query_embedding = await self.embedding_model.embed(query)
        
        similarities = []
        for conv in compressed_convs:
            if "embedding_summary" not in conv:
                continue
            
            conv_embedding = conv["embedding_summary"]
            similarity = cosine_similarity(query_embedding, conv_embedding)
            similarities.append((similarity, conv))
        
        # Sort by similarity
        similarities.sort(reverse=True, key=lambda x: x[0])
        
        return [conv for _, conv in similarities[:10]]
```

---

## Performance Targets

**Phase 11c (Basic):**
- Compression ratio: 50x minimum
- Compression time: < 1s per conversation
- Decompression time: < 100ms
- Semantic accuracy: 90%+

**Phase 23 (Advanced):**
- Compression ratio: 100x+
- With embeddings: Semantic search enabled
- Semantic accuracy: 95%+

---

## Testing

```python
# tests/test_compression.py
import pytest
from core.compression.compressor import ConversationCompressor

@pytest.fixture
def sample_conversation():
    return [
        {"role": "user", "content": "Create a note about Phase 11 planning"},
        {"role": "assistant", "content": "I'll help create that note. A few questions..."},
        {"role": "user", "content": "We decided on 8 providers and a 5-week timeline"},
        {"role": "assistant", "content": "Great! Here's the note..."},
        # ... 20 more exchanges
    ]

def test_compression_ratio(sample_conversation):
    compressor = ConversationCompressor()
    
    compressed = compressor.compress(sample_conversation)
    
    ratio = compressed["token_stats"]["ratio"]
    assert ratio >= 50, f"Compression ratio {ratio}x below 50x target"

def test_decompression_quality(sample_conversation):
    compressor = ConversationCompressor()
    
    compressed = compressor.compress(sample_conversation)
    decompressed = compressor.decompress(compressed)
    
    # Check key information preserved
    assert "8 providers" in decompressed
    assert "5-week" in decompressed or "5 weeks" in decompressed
    assert "Phase 11" in decompressed

def test_format_versioning():
    compressor = ConversationCompressor()
    
    compressed = compressor.compress([])
    assert compressed["version"] == 1  # Current version

def test_backward_compatibility():
    # Test loading old format (when we update to v2)
    old_format = {"version": 1, "user": "Test", ...}
    
    compressor = ConversationCompressor()
    decompressed = compressor.decompress(old_format)
    
    assert decompressed  # Should handle old format gracefully
```

---

## Success Metrics

**Phase 11c:**
- [ ] 50x+ compression ratio achieved
- [ ] < 5% information loss in testing
- [ ] Compression/decompression fast enough (< 1s)
- [ ] Context loading works with compressed history
- [ ] Database storage implemented

**Phase 23:**
- [ ] 100x+ compression ratio
- [ ] Embedding-based semantic search working
- [ ] 95%+ semantic accuracy
- [ ] Compression improves conversation retention

---

## Related Documents

- [PHASE11_MULTI_MODEL_ENHANCED_V2.md](./PHASE11_MULTI_MODEL_ENHANCED_V2.md) - Overall Phase 11 spec
- [master_roadmap.md](./master_roadmap.md) - Project roadmap
