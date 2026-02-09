# Polly Compression Guide

**Last Updated:** February 9, 2026  
**Status:** Implemented (Wave 1, Task 13)

## Overview

Polly uses two compression strategies to reduce token usage and extend context retention:

1. **LLM-based compression** (existing) — For conversation history summarization
2. **LLMLingua compression** (new) — For fast RAG context compression

## Quick Start

### Installation

```bash
# Install LLMLingua
pip install llmlingua

# Or install all requirements
pip install -r requirements.txt
```

### Configuration

Edit `config/config.yaml`:

```yaml
compression:
  strategy: "auto"  # Recommended
  
  rag_context:
    enabled: true   # Enable RAG compression
    ratio: 0.5      # 2x compression (adjust 0.1-1.0)
  
  llmlingua:
    device: "cpu"   # or "cuda" for GPU
```

### Test

```bash
python scripts/test_compression.py
```

## Compression Strategies

### Auto (Recommended)

Automatically selects the best strategy based on content type:

- **RAG context** → LLMLingua (fast, no LLM call)
- **Conversation** → LLM summary (better narrative quality)
- **Prompts** → LLMLingua

### LLMLingua

**Best for:** RAG context, prompts, any text needing fast compression

**Pros:**
- Fast (100-500ms per chunk on CPU)
- No LLM call needed
- 2x-10x token reduction
- Preserves semantic meaning

**Cons:**
- Requires ~500MB model download
- Less readable than LLM summaries
- Best for machine consumption

**Use when:** You need to reduce tokens before sending to LLM

### LLM Summary

**Best for:** Conversation history, human-readable summaries

**Pros:**
- High quality narrative summaries
- 50x-100x compression
- Human-readable output

**Cons:**
- Requires LLM call
- Slower than LLMLingua
- API cost for compression

**Use when:** You need human-readable summaries of conversations

## Configuration Options

### Compression Ratio

Controls how aggressively to compress (LLMLingua only):

```yaml
compression:
  rag_context:
    ratio: 0.5  # Values: 0.1 (10x) to 1.0 (no compression)
```

**Recommended ratios:**
- `0.5` (2x) — Balanced, minimal quality loss
- `0.3` (3.3x) — Aggressive, slight quality loss
- `0.1` (10x) — Maximum compression, noticeable quality loss

### Device Selection

```yaml
compression:
  llmlingua:
    device: "cpu"   # CPU (slower, ~500ms per chunk)
    # device: "cuda"  # GPU (faster, ~100ms per chunk)
```

**GPU requirements:** CUDA-compatible GPU with 2GB+ VRAM

### Enable/Disable

```yaml
compression:
  rag_context:
    enabled: true   # Enable compression
    # enabled: false  # Disable compression (no token reduction)
```

## Integration with RAG

Compression is automatically applied in the RAG pipeline when enabled:

```
Query → RAG Search → Retrieved Chunks
                          ↓
                    [Compression]
                    if enabled:
                        compress with LLMLingua
                          ↓
                    Compressed Chunks → LLM Call
```

### Token Savings

Compression metadata is added to search results:

```python
result.chunk.metadata['_compression'] = {
    'original_tokens': 1200,
    'compressed_tokens': 600,
    'ratio': 0.5,
    'strategy': 'llmlingua'
}
```

### Logging

```
INFO: Applying compression to RAG context chunks
INFO: RAG context compressed: 4800 → 2400 tokens (0.50x ratio, saved 2400 tokens)
```

## API Usage

### CompressionManager

```python
from core.compression import CompressionManager

# Initialize with config
manager = CompressionManager(config=config)

# Compress text
result = manager.compress_text(
    text="Your RAG context here...",
    strategy="llmlingua",  # or None for auto
    target_ratio=0.5,
    context_type="rag_context"
)

print(f"Saved {result['original_tokens'] - result['compressed_tokens']} tokens")
```

### Direct LLMLingua Usage

```python
from core.compression.llmlingua_strategy import LLMLinguaCompressor

# Initialize compressor
compressor = LLMLinguaCompressor(
    target_ratio=0.5,
    device="cpu"
)

# Compress
result = compressor.compress(text)
print(f"Compressed: {result.original_tokens} → {result.compressed_tokens} tokens")
print(f"Ratio: {result.compression_ratio:.2f}x")
```

## Performance

### LLMLingua

| Operation | CPU | GPU (CUDA) |
|-----------|-----|------------|
| First call (model load) | ~2-5s | ~1-2s |
| Subsequent calls | ~100-500ms | ~50-100ms |
| Memory usage | ~500MB | ~500MB VRAM |

### LLM Summary

| Operation | Time |
|-----------|------|
| Compression | ~1-3s (LLM call) |
| Decompression | Instant (template) |

## Troubleshooting

### LLMLingua not installed

```
ERROR: LLMLingua not installed. Run: pip install llmlingua
```

**Solution:** `pip install llmlingua`

### Model download fails

```
ERROR: Failed to load LLMLingua model: ...
```

**Solutions:**
1. Check internet connection (model downloads from HuggingFace)
2. Check disk space (~500MB needed)
3. Try manual download:
   ```bash
   python -c "from transformers import AutoTokenizer, AutoModel; \
              AutoTokenizer.from_pretrained('microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank'); \
              AutoModel.from_pretrained('microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank')"
   ```

### CUDA not available

```
WARNING: CUDA device requested but not available, falling back to CPU
```

**Solution:** Either install CUDA drivers or set `device: "cpu"` in config

### Compression quality issues

If compressed text loses too much meaning:

1. **Increase compression ratio:**
   ```yaml
   compression:
     rag_context:
       ratio: 0.7  # Less aggressive (1.4x compression)
   ```

2. **Disable compression for specific queries:**
   ```python
   results = rag.search(query, n_results=5)
   # Compression is skipped if disabled in config
   ```

### Performance issues

If compression is too slow:

1. **Use GPU if available:**
   ```yaml
   compression:
     llmlingua:
       device: "cuda"
   ```

2. **Reduce compression ratio (faster):**
   ```yaml
   compression:
     rag_context:
       ratio: 0.7  # Less compression = faster
   ```

3. **Disable compression:**
   ```yaml
   compression:
     rag_context:
       enabled: false
   ```

## Metrics & Monitoring

### Token Savings

Track token savings in logs:

```
INFO: RAG context compressed: 4800 → 2400 tokens (0.50x ratio, saved 2400 tokens)
```

### Compression Ratio

Check actual compression ratio vs target:

```python
result = manager.compress_text(text, target_ratio=0.5)
print(f"Target: 0.5, Actual: {result['compression_ratio']:.2f}")
```

### Cost Savings

Estimate cost savings:

```python
tokens_saved = result['original_tokens'] - result['compressed_tokens']
cost_per_token = 0.000003  # $3 per 1M tokens (Claude Sonnet)
savings = tokens_saved * cost_per_token
print(f"Saved ${savings:.4f} on this query")
```

## Best Practices

### When to Enable Compression

✅ **Enable when:**
- RAG returns large chunks (>500 tokens each)
- Using expensive cloud providers
- Context window is limited
- Query returns many results (>10 chunks)

❌ **Disable when:**
- RAG chunks are already small (<200 tokens)
- Using local models (Ollama) — no cost savings
- Compression time > LLM inference time
- Quality is critical (legal, medical, etc.)

### Compression Ratio Guidelines

| Use Case | Recommended Ratio | Expected Quality |
|----------|-------------------|------------------|
| General RAG | 0.5 (2x) | Excellent |
| Large context | 0.3 (3.3x) | Good |
| Maximum savings | 0.1 (10x) | Fair |

### Strategy Selection

| Content Type | Recommended Strategy |
|--------------|---------------------|
| RAG context | LLMLingua |
| Conversation history | LLM Summary |
| Prompts | LLMLingua |
| Code snippets | LLMLingua |
| Human-readable summaries | LLM Summary |

## Future Enhancements

- **Adaptive compression** — Adjust ratio based on context window size
- **Compression caching** — Cache compressed chunks to avoid recompression
- **PIL v2 format** — Extend PIL to cover patterns, knowledge summaries
- **Selective compression** — Compress only low-relevance chunks

## Reference

- **Implementation:** `core/compression/`
- **Config:** `config/config.yaml` → `compression`
- **Spec:** `openspec/specs/compression/spec.md`
- **Change folder:** `openspec/changes/core-framework-refinement/`
- **LLMLingua paper:** https://arxiv.org/abs/2310.06201
