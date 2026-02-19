# Dependency Tracker

**Last audited:** 2026-02-19
**Python:** 3.13.11
**Dependency tool:** pip + requirements.txt (no lock file)
**Internal libraries:** 5 packages under `libs/` (polly-routing, polly-personas, polly-patterns, polly-entities, polly-compression)

---

## Action Items

| Package | Issue | Priority | Status |
|---------|-------|----------|--------|
| `aiohttp` | DeprecationWarning: `enable_cleanup_closed` ignored in Python 3.13+ ([cpython#118960](https://github.com/python/cpython/pull/118960)). Warning emitted from `connector.py:993` on every HTTPS connection. | Low | Open |

---

## Core Dependencies

Packages explicitly listed in `requirements.txt` with their current installed versions and constraint.

| Package | Constraint | Installed | Notes |
|---------|-----------|-----------|-------|
| `pyyaml` | >=6.0 | 6.0.3 | |
| `pydantic` | >=2.0 | 2.12.5 | |
| `chromadb` | >=0.4.0 | 1.4.1 | Major version jump from constraint; API stable |
| `fastapi` | >=0.100.0 | 0.128.0 | |
| `uvicorn[standard]` | >=0.23.0 | 0.40.0 | |
| `httpx` | >=0.24.0 | 0.28.1 | |
| `aiohttp` | >=3.9.0 | 3.13.3 | See Action Items — deprecation warning on Python 3.13 |
| `anthropic` | >=0.20.0 | 0.76.0 | |
| `openai` | >=1.10.0 | 2.16.0 | Major version jump; OpenAI SDK v2 |
| `litellm` | >=1.30.0 | 1.81.9 | Fast-moving package; updates frequently |
| `keyring` | >=24.0.0 | 25.7.0 | |
| `cryptography` | >=41.0.0 | 46.0.4 | |
| `watchdog` | >=3.0.0 | 6.0.0 | |
| `rank-bm25` | >=0.2.2 | 0.2.2 | Pinned at minimum; no newer versions |
| `spacy` | >=3.7.0 | 3.8.11 | |
| `en-core-web-sm` | ==3.8.0 | 3.8.0 | Pinned via wheel URL; must match spaCy version |
| `llmlingua` | >=0.2.0 | 0.2.2 | |
| `mem0ai` | >=1.0.0 | 1.0.3 | |
| `tiktoken` | >=0.5.0 | 0.12.0 | Lazy-imported; fallback to estimation if unavailable |

## Internal Libraries

Editable installs from `libs/`. Each has its own `pyproject.toml`.

| Library | Version | Installed As | Key Deps |
|---------|---------|-------------|----------|
| `polly-routing` | 0.1.0 | `-e libs/polly-routing` (in requirements.txt) | pyyaml, litellm (optional) |
| `polly-personas` | 0.1.0 | Not in requirements.txt | pyyaml |
| `polly-patterns` | 0.1.0 | Not in requirements.txt | pyyaml, mem0ai (optional) |
| `polly-entities` | 0.1.0 | Not in requirements.txt | spacy (optional) |
| `polly-compression` | 0.1.0 | Not in requirements.txt | pyyaml, llmlingua (optional) |

**Note:** Only `polly-routing` is referenced from the root `requirements.txt`. The other 4 libraries are imported directly via path (Python path manipulation or editable installs done outside requirements.txt).

## Transitive Dependencies (Notable)

Packages not in `requirements.txt` but installed transitively and worth tracking.

| Package | Installed | Pulled In By | Notes |
|---------|-----------|-------------|-------|
| `torch` | 2.10.0 | llmlingua, transformers | Large (~2GB); ML inference backend |
| `transformers` | 5.1.0 | llmlingua | HuggingFace model loading |
| `accelerate` | 1.12.0 | transformers | GPU/CPU dispatch |
| `SQLAlchemy` | 2.0.46 | mem0ai | Database ORM for Mem0 |
| `networkx` | 3.6.1 | (knowledge graph) | Graph data structures |
| `nltk` | 3.9.2 | (NLP utilities) | Tokenization, stopwords |
| `qdrant-client` | 1.16.2 | mem0ai | Vector DB client (Mem0 can use Qdrant or ChromaDB) |
| `pytest` | 9.0.2 | dev | Test runner |
| `pytest-asyncio` | 1.3.0 | dev | Async test support |

## Local Services

External services Polly depends on at runtime.

| Service | Purpose | Version/Model | Notes |
|---------|---------|--------------|-------|
| Ollama | Local LLM + embeddings | qwen2.5:7b, nomic-embed-text:latest | Must be running for local routing and memory search |
| ChromaDB | Vector storage | Embedded (via chromadb pip package) | Runs in-process, no separate server |
| SQLite | Entity store, compression DB | System (bundled with Python) | Files at `~/.polly/*.db` |

---

## Upgrade Policy

Current approach: all constraints use `>=` minimum bounds with no upper pins. This means `pip install` pulls the latest compatible version. There is no lock file.

### Risks
- **No reproducibility:** Two installs at different times get different versions.
- **Breaking changes:** Major version bumps (e.g., openai v1→v2, chromadb 0.x→1.x) can land silently.
- **Transitive drift:** torch, transformers, etc. update frequently and can introduce incompatibilities.

### Recommendations (future)
- Consider `pip-compile` (pip-tools) to generate a `requirements.lock` from `requirements.txt`.
- Pin major versions for fast-moving packages: `litellm>=1.30,<2`, `openai>=2.0,<3`, `chromadb>=1.0,<2`.
- Run `pip list --outdated` periodically and log results here.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-02-19 | Initial audit. Documented all 20 core deps, 5 internal libs, 9 notable transitive deps, and 1 open action item (aiohttp deprecation warning). |
