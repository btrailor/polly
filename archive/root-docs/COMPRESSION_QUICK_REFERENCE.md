# Compression System - Quick Reference

## Installation

Already installed! No additional dependencies required.

## Basic Usage

### 1. Simple Compression

```python
from core.compression import ConversationCompressor

# Create compressor
compressor = ConversationCompressor()

# Your conversation history
conversation = [
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi! How can I help?"},
    # ... more messages
]

# Compress
compressed = compressor.compress(conversation)

# Check results
print(f"Original: {compressed['token_stats']['original']} tokens")
print(f"Compressed: {compressed['token_stats']['compressed']} tokens")
print(f"Ratio: {compressed['token_stats']['ratio']:.1f}x")

# Decompress to summary
summary = compressor.decompress(compressed)
print(summary)
```

### 2. With Database Storage

```python
from core.compression import CompressionManager

# Create manager (uses ~/.polly/compression.db by default)
manager = CompressionManager()

# Compress and store conversation
result = manager.compress_conversation(
    conversation_history=conversation,
    conversation_id="my-conv-123"
)

# Later, load compressed context
context = manager.load_context("my-conv-123")

# Check stats
stats = manager.get_compression_stats("my-conv-123")
print(f"Saved {stats['compression_ratio']:.1f}x")
```

### 3. Check If Should Compress

```python
manager = CompressionManager()

# Check thresholds
if manager.should_compress(conversation):
    result = manager.compress_conversation(conversation, conv_id)
```

## Configuration

### Thresholds (in CompressionManager)

```python
manager = CompressionManager()

# Customize thresholds
manager.COMPRESSION_THRESHOLD = 10      # Compress after 10 exchanges
manager.COMPRESSION_AGE_HOURS = 24      # Or after 24 hours
manager.KEEP_RECENT_COUNT = 10          # Keep last 10 messages uncompressed
```

### Custom Database Path

```python
manager = CompressionManager(db_path="/custom/path/compression.db")
```

## API Reference

### ConversationCompressor

#### `compress(conversation, metadata=None)`
Compress conversation into structured format.

**Parameters:**
- `conversation` (list[dict]): List of messages with 'role' and 'content'
- `metadata` (dict, optional): Additional context

**Returns:** dict with compressed data

#### `decompress(compressed)`
Convert compressed format to natural language summary.

**Parameters:**
- `compressed` (dict): Compressed conversation dict

**Returns:** str (natural language summary)

### CompressionManager

#### `compress_conversation(conversation_history, conversation_id, metadata=None)`
Compress and store conversation.

**Returns:** dict with 'compressed' and 'recent' keys

#### `load_context(conversation_id, recent_messages=None)`
Load conversation context with compression.

**Returns:** list[dict] of messages

#### `should_compress(conversation_history, conversation_id=None, created_at=None)`
Check if conversation should be compressed.

**Returns:** bool

#### `get_compression_stats(conversation_id)`
Get compression statistics.

**Returns:** dict with stats or None

#### `get_total_compression_savings()`
Calculate total savings across all conversations.

**Returns:** dict with totals

#### `list_all_compressed()`
List all compressed conversations.

**Returns:** list[dict]

#### `delete_compressed(conversation_id)`
Delete compressed conversation.

## Message Format

Messages should have:

```python
{
    "role": "user" | "assistant" | "system",
    "content": "message text",
    "timestamp": "2026-01-28T10:00:00Z"  # optional
}
```

## Compressed Format

```python
{
    "version": 1,
    "user": "Brett",
    "mode": "notes",
    "task_type": "note-creation",
    "depth": 12,
    "decisions": [{"topic": "...", "decision": "...", "confidence": 0.8}],
    "focus_topics": ["topic1", "topic2"],
    "key_concepts": [{"term": "...", "definition": "..."}],
    "context_critical": {"key": "value"},
    "artifacts_created": [{"type": "note", "title": "...", "file": "..."}],
    "token_stats": {
        "original": 1000,
        "compressed": 50,
        "ratio": 20.0
    }
}
```

## Database Schema

Table: `conversation_compression`

| Column             | Type     | Description                    |
|--------------------|----------|--------------------------------|
| id                 | INTEGER  | Primary key                    |
| conversation_id    | TEXT     | Unique conversation identifier |
| version            | INTEGER  | Format version                 |
| compressed_data    | TEXT     | JSON compressed data           |
| original_tokens    | INTEGER  | Original token count           |
| compressed_tokens  | INTEGER  | Compressed token count         |
| compression_ratio  | REAL     | Compression ratio              |
| created_at         | DATETIME | Compression timestamp          |

## Performance Tips

1. **Short conversations** - Don't compress < 10 messages (low benefit)
2. **Batch compression** - Compress multiple conversations at once
3. **Keep recent messages** - Always keep last 10 uncompressed
4. **Monitor ratios** - Track compression effectiveness

## Testing

Run tests:
```bash
cd /Users/brettgershon/polly
source venv/bin/activate
python -m pytest tests/test_compression.py -v
```

Run demo:
```bash
python demo_compression.py
```

## Troubleshooting

### Low compression ratio
- **Cause:** Very short conversation or unique content
- **Solution:** Only compress conversations with 20+ messages

### Missing decisions/artifacts
- **Cause:** Pattern matching didn't find them
- **Solution:** Patterns are flexible, but may need adjustment for edge cases

### Database locked
- **Cause:** Multiple processes accessing database
- **Solution:** Use separate database per process or implement locking

## Example Integration with Polly

```python
class Polly:
    def __init__(self):
        self.compression_manager = CompressionManager()
        self.conversation_history = []
        self.session_id = generate_session_id()
    
    def save_conversation(self):
        """Save conversation with compression"""
        if self.compression_manager.should_compress(self.conversation_history):
            result = self.compression_manager.compress_conversation(
                self.conversation_history,
                self.session_id
            )
            
            # Keep only recent messages in memory
            self.conversation_history = result['recent']
    
    def load_conversation(self, session_id):
        """Load conversation with compression"""
        self.session_id = session_id
        
        # Load compressed + recent messages
        context = self.compression_manager.load_context(
            session_id,
            recent_messages=self.conversation_history
        )
        
        return context
```

## Support

- Docs: `/Users/brettgershon/polly/PHASE11_COMPRESSION_SYSTEM.md`
- Implementation: `/Users/brettgershon/polly/PHASE11C_IMPLEMENTATION_SUMMARY.md`
- Tests: `/Users/brettgershon/polly/tests/test_compression.py`
- Demo: `/Users/brettgershon/polly/demo_compression.py`
