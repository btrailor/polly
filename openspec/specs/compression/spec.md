# Compression (OpenSpec)

Source of truth for conversation and context compression in Polly.

## Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| LLM summary (conversation compression) | ✅ Implemented | `core/compression/compressor.py` |
| LLMLingua (RAG context compression) | ✅ Implemented | `core/compression/llmlingua_strategy.py` |
| Strategy selection (auto / llmlingua / llm_summary) | ✅ Implemented | config + settings API |
| ContextContributor (priority 10) | ✅ Implemented | _gather_context in polly.py |
| Adaptive compression / caching | 💭 Vision | Spec-only; planned enhancement |

## Overview

Polly uses compression to extend context retention and reduce token usage:

1. **Conversation Compression** (Phase 11c) — LLM-based summarization of old conversation messages (50x compression)
2. **RAG Context Compression** (Wave 1, Task 13) — Algorithmic compression of retrieved chunks (2x-10x compression)

## Strategies

### LLM Summary (Existing)

- **Use case:** Conversation history compression
- **Method:** Extract decisions, topics, concepts, artifacts from conversation → structured format → natural language summary
- **Compression ratio:** 50x-100x
- **Cost:** Requires LLM call for decompression
- **Implementation:** `core/compression/compressor.py` → `ConversationCompressor`

### LLMLingua (NEW - Wave 1)

- **Use case:** RAG context, prompts, any text that needs fast compression
- **Method:** Algorithmic prompt compression using LLMLingua-2 BERT model
- **Compression ratio:** 2x-10x (configurable via `target_ratio`)
- **Cost:** No LLM call needed, CPU/GPU model inference only
- **Implementation:** `core/compression/llmlingua_strategy.py` → `LLMLinguaCompressor`
- **Model:** `microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank`
- **Reference:** https://arxiv.org/abs/2310.06201

## Configuration

```yaml
compression:
  strategy: "auto"  # "auto" | "llmlingua" | "llm_summary"
  
  rag_context:
    enabled: true
    ratio: 0.5  # 2x compression (1.0 = no compression, 0.1 = 10x)
  
  conversation:
    strategy: "llm_summary"  # Force LLM for conversation compression
  
  llmlingua:
    model: "microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank"
    device: "cpu"  # or "cuda"
```

## Strategy Selection

**Auto mode (default):**
- RAG context → LLMLingua (fast, no LLM call)
- Conversation → LLM summary (better narrative quality)
- Prompts → LLMLingua

**Manual override:**
- Set `compression.strategy` to force one strategy for all contexts

## Integration Points

### RAG Pipeline

```
Query → RAG Search → Retrieved Chunks
                          ↓
                    [Optional Compression]
                    if compression.rag_context.enabled:
                        compress chunks with LLMLingua
                          ↓
                    Compressed Chunks → LLM Call
```

**Token savings tracking:**
- Original tokens, compressed tokens, compression ratio stored in chunk metadata
- Logged for each search operation
- Aggregated in autonomy metrics

### Conversation Manager

```
Old Messages → ConversationCompressor
                    ↓
              Compressed Summary
                    ↓
              Stored in SQLite
                    ↓
              Loaded as system message in new context
```

### Entity Extraction from Compression (Integration Contracts — Feb 2026)
After conversation compression, key concepts and focus topics from the compressed output are passed to the entity extractor (`source_type="compression"`). This feeds the knowledge graph with high-signal terms from summarized conversations. Implemented in `Polly._try_compress_conversation()`: `key_concepts` and `focus_topics` from the compression result are sent to `entity_extractor.extract_and_store()`.

## API

### CompressionManager

```python
from core.compression import CompressionManager

manager = CompressionManager(config=config)

# Compress text with strategy
result = manager.compress_text(
    text="...",
    strategy="llmlingua",  # or None for auto
    target_ratio=0.5,
    context_type="rag_context"
)

# Check if compression enabled
if manager.is_compression_enabled("rag_context"):
    ratio = manager.get_compression_ratio("rag_context")
```

### LLMLinguaCompressor (Direct)

```python
from core.compression.llmlingua_strategy import LLMLinguaCompressor

compressor = LLMLinguaCompressor(target_ratio=0.5, device="cpu")
result = compressor.compress(text)

print(f"Compressed {result.original_tokens} → {result.compressed_tokens} tokens")
print(f"Ratio: {result.compression_ratio:.2f}x")
```

## Metrics

### Token Tracking

- **Before compression:** Original token count
- **After compression:** Compressed token count
- **Ratio:** `compressed_tokens / original_tokens`
- **Savings:** `original_tokens - compressed_tokens`

### Logged in RAG Search Results

```python
result.chunk.metadata['_compression'] = {
    'original_tokens': 1200,
    'compressed_tokens': 600,
    'ratio': 0.5,
    'strategy': 'llmlingua'
}
```

### Aggregated Metrics

- Total tokens saved across all RAG searches
- Average compression ratio
- Compression strategy distribution

## Performance

### LLMLingua

- **First call:** ~2-5 seconds (model loading)
- **Subsequent calls:** ~100-500ms per chunk (CPU), ~50-100ms (GPU)
- **Memory:** ~500MB for BERT model

### LLM Summary

- **Compression:** ~1-3 seconds (LLM call)
- **Decompression:** Instant (template-based)

## Troubleshooting

### LLMLingua not available

```
ERROR: LLMLingua not installed. Run: pip install llmlingua
```

**Solution:** Install llmlingua: `pip install llmlingua`

### Model loading fails

```
ERROR: Failed to load LLMLingua model: ...
```

**Solutions:**
1. Check internet connection (model downloads from HuggingFace)
2. Check disk space (~500MB needed)
3. Try CPU device if CUDA fails: `compression.llmlingua.device: "cpu"`

### Compression disabled/fallback

If compression fails, RAG pipeline falls back to uncompressed chunks. Check logs for errors.

## Future Enhancements

- **Compact Format v2** (Task 21) — Extend compact format (formerly PIL) to cover patterns, knowledge summaries, routing decisions
- **Adaptive compression** — Adjust ratio based on context window size
- **Compression caching** — Cache compressed chunks to avoid recompression

## Reference

- **Implementation:** `core/compression/`
- **Config:** `config/config.yaml` → `compression`
- **Change folder:** [openspec/changes/core-framework-refinement/](../../changes/core-framework-refinement/)
- **RAG integration:** [openspec/specs/rag/spec.md](../rag/spec.md)
