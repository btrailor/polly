"""
Apollo Unified RAG System
Multi-source semantic search across your entire knowledge base
"""

from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import re
import logging

logger = logging.getLogger(__name__)

# Import token counter for accurate budget tracking
from core.context.token_counter import TokenCounter

# Import hybrid search components
try:
    from core.hybrid_search import HybridSearcher
    HYBRID_SEARCH_AVAILABLE = True
except ImportError:
    logger.warning("Hybrid search not available, falling back to semantic-only search")
    HYBRID_SEARCH_AVAILABLE = False


@dataclass
class Chunk:
    """A chunk of indexed content."""
    id: str
    content: str
    filepath: str
    source_type: str  # "notes", "codebase", "document"
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


@dataclass
class SearchResult:
    """A search result with relevance info."""
    chunk: Chunk
    score: float
    domain: Optional[str] = None


class MarkdownChunker:
    """Smart chunking for markdown files, preserving semantic structure."""

    def __init__(self, chunk_size: int = 800, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_file(self, content: str, filepath: str) -> List[Tuple[str, Dict]]:
        """Chunk a markdown file into semantically meaningful pieces."""
        chunks = []
        sections = self._split_by_headers(content)

        for section in sections:
            if len(section['content']) < self.chunk_size:
                chunks.append((
                    section['content'],
                    {
                        'filepath': filepath,
                        'header': section['header'],
                        'level': section['level']
                    }
                ))
            else:
                sub_chunks = self._split_large_section(section)
                for sub in sub_chunks:
                    chunks.append((
                        sub,
                        {
                            'filepath': filepath,
                            'header': section['header'],
                            'level': section['level']
                        }
                    ))

        return chunks

    def _split_by_headers(self, content: str) -> List[Dict]:
        """
        Split content by markdown headers, keeping subsections with their parent.
        Only creates new sections for headers at the same or higher level (fewer #).
        """
        sections = []
        current = {'content': '', 'header': '', 'level': 999}  # Start with high level so first header always creates section

        for line in content.split('\n'):
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)

            if header_match:
                level = len(header_match.group(1))
                header = header_match.group(2)
                
                # Only create new section if this header is same or higher level (fewer #) than current
                if level <= current['level']:
                    if current['content'].strip():
                        sections.append(current)
                    
                    current = {
                        'content': line + '\n',
                        'header': header,
                        'level': level
                    }
                else:
                    # Lower-level header (more #) - keep with current section
                    current['content'] += line + '\n'
            else:
                current['content'] += line + '\n'

        if current['content'].strip():
            sections.append(current)

        return sections

    def _split_large_section(self, section: Dict) -> List[str]:
        """Split a large section by paragraphs."""
        content = section['content']
        chunks = []
        current = ''

        paragraphs = re.split(r'\n\n+', content)

        for para in paragraphs:
            if len(current) + len(para) < self.chunk_size:
                current += para + '\n\n'
            else:
                if current.strip():
                    chunks.append(current.strip())
                current = para + '\n\n'

        if current.strip():
            chunks.append(current.strip())

        return chunks


class CodeChunker:
    """Smart chunking for code files, preserving function/class boundaries."""

    def __init__(self, chunk_size: int = 1200):
        self.chunk_size = chunk_size

    def chunk_file(self, content: str, filepath: str, language: str) -> List[Tuple[str, Dict]]:
        """Chunk a code file by semantic units."""
        chunks = []

        # Try to find function/class definitions
        patterns = self._get_patterns_for_language(language)

        if patterns:
            chunks = self._chunk_by_patterns(content, filepath, patterns, language)

        # Fallback to simple chunking if no patterns found
        if not chunks:
            chunks = self._simple_chunk(content, filepath, language)

        return chunks

    def _get_patterns_for_language(self, language: str) -> Dict[str, str]:
        """Get regex patterns for semantic chunking by language."""
        patterns = {
            'python': {
                'function': r'^(async\s+)?def\s+(\w+)',
                'class': r'^class\s+(\w+)'
            },
            'lua': {
                'function': r'^(local\s+)?function\s+(\w+)',
                'assignment': r'^(\w+)\s*='
            },
            'javascript': {
                'function': r'^(async\s+)?function\s+(\w+)',
                'const_function': r'^(const|let|var)\s+(\w+)\s*=\s*(async\s+)?\(',
                'class': r'^class\s+(\w+)'
            },
            'rust': {
                'function': r'^(pub\s+)?(async\s+)?fn\s+(\w+)',
                'struct': r'^(pub\s+)?struct\s+(\w+)',
                'impl': r'^impl\s+(\w+)'
            }
        }
        return patterns.get(language, {})

    def _chunk_by_patterns(
        self,
        content: str,
        filepath: str,
        patterns: Dict[str, str],
        language: str
    ) -> List[Tuple[str, Dict]]:
        """Chunk code by language-specific patterns."""
        chunks = []
        lines = content.split('\n')
        current_chunk = []
        current_name = None
        current_type = None

        for i, line in enumerate(lines):
            # Check for new semantic unit
            for unit_type, pattern in patterns.items():
                match = re.match(pattern, line)
                if match:
                    # Save previous chunk
                    if current_chunk:
                        chunk_text = '\n'.join(current_chunk)
                        if chunk_text.strip():
                            chunks.append((
                                chunk_text,
                                {
                                    'filepath': filepath,
                                    'name': current_name or 'module',
                                    'type': current_type or 'code',
                                    'language': language,
                                    'line': i - len(current_chunk)
                                }
                            ))

                    current_chunk = [line]
                    current_name = match.group(match.lastindex) if match.lastindex else 'unknown'
                    current_type = unit_type
                    break
            else:
                current_chunk.append(line)

        # Save final chunk
        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            if chunk_text.strip():
                chunks.append((
                    chunk_text,
                    {
                        'filepath': filepath,
                        'name': current_name or 'module',
                        'type': current_type or 'code',
                        'language': language,
                        'line': len(lines) - len(current_chunk)
                    }
                ))

        return chunks

    def _simple_chunk(
        self,
        content: str,
        filepath: str,
        language: str
    ) -> List[Tuple[str, Dict]]:
        """Simple chunking by size."""
        chunks = []
        lines = content.split('\n')
        current = []
        current_size = 0

        for i, line in enumerate(lines):
            if current_size + len(line) > self.chunk_size and current:
                chunks.append((
                    '\n'.join(current),
                    {
                        'filepath': filepath,
                        'type': 'code',
                        'language': language,
                        'line': i - len(current)
                    }
                ))
                current = []
                current_size = 0

            current.append(line)
            current_size += len(line)

        if current:
            chunks.append((
                '\n'.join(current),
                {
                    'filepath': filepath,
                    'type': 'code',
                    'language': language,
                    'line': len(lines) - len(current)
                }
            ))

        return chunks


def _hit_count_to_tier_boost(hit_count: int) -> float:
    """Calibrated tier-curve boost for query→chunk positive patterns (Spec 05)."""
    if hit_count >= 15:
        return 4.0
    if hit_count >= 8:
        return 3.0
    if hit_count >= 4:
        return 2.0
    if hit_count >= 2:
        return 1.5
    return 1.2


class UnifiedRAG:
    """
    Unified RAG system that indexes and searches across:
    - Obsidian vault (notes, ideas, connections)
    - Project codebases (functions, classes, patterns)
    - Documents (PDFs, docs, references)

    Uses ChromaDB for vector storage, Ollama for embeddings.
    """

    def __init__(
        self,
        db_path: Path,
        ollama_host: str = "http://localhost:11434",
        embedding_model: str = "nomic-embed-text",
        chunk_size: int = 800,
        pattern_learner = None,  # Optional PatternLearner instance
        use_hybrid_search: bool = True,  # Enable hybrid search by default
        config: Optional[Dict] = None,  # Configuration for compression
        bm25_index_path: Optional[str] = None,  # Path for BM25 persistence (Spec 08)
    ):
        self.db_path = Path(db_path)
        self.ollama_host = ollama_host
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.pattern_learner = pattern_learner  # Store pattern learner
        self.use_hybrid_search = use_hybrid_search and HYBRID_SEARCH_AVAILABLE
        self.config = config or {}
        self._bm25_index_path = bm25_index_path  # Spec 08

        self.md_chunker = MarkdownChunker(chunk_size)
        self.code_chunker = CodeChunker(chunk_size)

        # Initialize vector DB
        self._init_db()

        # Metadata tracking
        self.metadata_cache: Dict[str, Dict] = {}

        # Initialize hybrid searcher (Spec 08: use PersistentBM25Index if path given)
        if self.use_hybrid_search:
            self.hybrid_searcher = HybridSearcher(index_path=self._bm25_index_path)
            logger.info("Hybrid search enabled (semantic + keyword)")
            # Attempt to load persisted BM25 index from disk (Spec 08)
            if self._bm25_index_path:
                self._try_load_bm25_index()
        else:
            self.hybrid_searcher = None
            logger.info("Using semantic-only search")
        
        # Initialize compression manager (lazy-loaded)
        self._compression_manager = None

    def _init_db(self):
        """Initialize ChromaDB."""
        try:
            import chromadb
            from chromadb.config import Settings

            self.db_path.mkdir(parents=True, exist_ok=True)

            self.client = chromadb.PersistentClient(
                path=str(self.db_path),
                settings=Settings(anonymized_telemetry=False)
            )

            # Collections for different source types
            self.collections = {
                'notes': self.client.get_or_create_collection(
                    name="notes",
                    metadata={"hnsw:space": "cosine"}
                ),
                'codebase': self.client.get_or_create_collection(
                    name="codebase",
                    metadata={"hnsw:space": "cosine"}
                ),
                'documents': self.client.get_or_create_collection(
                    name="documents",
                    metadata={"hnsw:space": "cosine"}
                ),
                'patterns': self.client.get_or_create_collection(
                    name="patterns",
                    metadata={"hnsw:space": "cosine"}
                )
            }
            
            # Discover and add any integration collections
            # Use threading.Timer for timeout since signal doesn't work in background threads
            try:
                import threading
                
                integration_collections = []
                timeout_occurred = [False]  # Use list to allow modification in nested function
                
                def discover_collections():
                    """Discover integration collections with timeout protection."""
                    try:
                        all_collections = self.client.list_collections()
                        for collection in all_collections:
                            if collection.name.startswith('integration_'):
                                integration_collections.append(collection)
                    except Exception as e:
                        if not timeout_occurred[0]:
                            logger.warning(f"Error discovering collections: {e}")
                
                # Run discovery in a separate thread with timeout
                discovery_thread = threading.Thread(target=discover_collections)
                discovery_thread.daemon = True
                discovery_thread.start()
                discovery_thread.join(timeout=5.0)  # 5 second timeout
                
                if discovery_thread.is_alive():
                    timeout_occurred[0] = True
                    logger.warning("ChromaDB list_collections() timed out - skipping integration discovery")
                else:
                    # Add discovered collections
                    for collection in integration_collections:
                        self.collections[collection.name] = collection
                        logger.info(f"Discovered integration collection: {collection.name}")
                    
            except Exception as e:
                logger.warning(f"Could not discover integration collections: {e}")

            logger.info(f"Initialized ChromaDB at {self.db_path} with {len(self.collections)} collections")

        except ImportError:
            logger.error("ChromaDB not installed. Run: pip install chromadb")
            raise

    def embed_text(self, text: str, max_retries: int = 3) -> List[float]:
        """Generate embedding using Ollama with retry logic."""
        import httpx
        import time

        # Truncate very long texts to avoid context length issues
        # nomic-embed-text has ~2048 token context, ~4 chars per token = ~8000 chars max
        # But to be safe, use 6000 chars
        max_chars = 6000
        if len(text) > max_chars:
            text = text[:max_chars]
            logger.debug(f"Truncated text from {len(text)} to {max_chars} chars")

        last_error = None
        for attempt in range(max_retries):
            try:
                response = httpx.post(
                    f"{self.ollama_host}/api/embeddings",
                    json={
                        "model": self.embedding_model,
                        "prompt": text
                    },
                    timeout=60.0  # Longer timeout for embedding
                )
                response.raise_for_status()
                return response.json()['embedding']

            except httpx.HTTPStatusError as e:
                last_error = e
                logger.warning(f"Embedding attempt {attempt + 1} failed with status {e.response.status_code}")
                if attempt < max_retries - 1:
                    time.sleep(1 * (attempt + 1))  # Backoff
            except Exception as e:
                last_error = e
                logger.warning(f"Embedding attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1 * (attempt + 1))

        logger.error(f"Embedding generation failed after {max_retries} attempts: {last_error}")
        raise last_error

    def index_obsidian_vault(self, vault_path: Path, force: bool = False) -> int:
        """Index all markdown files in an Obsidian vault."""
        vault_path = Path(vault_path)
        if not vault_path.exists():
            logger.error(f"Vault path does not exist: {vault_path}")
            return 0

        md_files = list(vault_path.rglob("*.md"))
        # Filter out hidden/system files (check relative path only, not absolute path)
        filtered_files = []
        for f in md_files:
            try:
                rel_parts = f.relative_to(vault_path).parts
                # Skip if relative path has hidden/system folders
                if any(part.startswith('.') or part.startswith('_') for part in rel_parts):
                    continue
                if 'templates' in rel_parts or '.trash' in str(f):
                    continue
                filtered_files.append(f)
            except ValueError:
                # File not relative to vault_path, skip it
                continue
        md_files = filtered_files

        total = len(md_files)
        logger.info(f"Found {total} markdown files to index in vault")

        indexed = 0
        errors = 0
        for i, md_file in enumerate(md_files):
            if (i + 1) % 10 == 0 or i == 0:
                logger.info(f"Indexing progress: {i + 1}/{total} files...")

            try:
                if self._index_markdown_file(md_file, vault_path, force):
                    indexed += 1
            except Exception as e:
                errors += 1
                logger.error(f"Error indexing {md_file.name}: {e}")

        logger.info(f"Indexing complete: {indexed} indexed, {errors} errors out of {total} files")
        
        # Rebuild BM25 index if hybrid search is enabled
        if self.use_hybrid_search:
            self._rebuild_bm25_index()
        
        return indexed

    def index_codebase(self, codebase_path: Path, excludes: List[str] = None, force: bool = False) -> int:
        """Index a codebase."""
        codebase_path = Path(codebase_path)
        if not codebase_path.exists():
            logger.error(f"Codebase path does not exist: {codebase_path}")
            return 0

        excludes = excludes or ['node_modules', '.git', '__pycache__', 'venv', '.venv', 'target', 'build', 'dist']

        code_extensions = {'.py', '.rs', '.go', '.ts', '.js', '.lua', '.scd'}

        # Collect all code files first
        code_files = []
        for ext in code_extensions:
            for code_file in codebase_path.rglob(f"*{ext}"):
                if not any(ex in code_file.parts for ex in excludes):
                    code_files.append(code_file)

        total = len(code_files)
        logger.info(f"Found {total} code files to index in {codebase_path.name}")

        indexed = 0
        errors = 0
        for i, code_file in enumerate(code_files):
            if (i + 1) % 10 == 0 or i == 0:
                logger.info(f"Indexing code progress: {i + 1}/{total} files...")

            try:
                if self._index_code_file(code_file, codebase_path, force):
                    indexed += 1
            except Exception as e:
                errors += 1
                logger.error(f"Error indexing {code_file.name}: {e}")

        # Save patterns after indexing
        if self.pattern_learner:
            try:
                self.pattern_learner.save()
                logger.info("Code patterns saved after indexing")
            except Exception as e:
                logger.warning(f"Could not save code patterns: {e}")

        logger.info(f"Codebase indexing complete: {indexed} indexed, {errors} errors out of {total} files")
        
        # Rebuild BM25 index if hybrid search is enabled
        if self.use_hybrid_search:
            self._rebuild_bm25_index()
        
        return indexed

    def _index_markdown_file(self, filepath: Path, base_path: Path, force: bool = False) -> bool:
        """Index a single markdown file."""
        # Check if needs re-indexing
        rel_path = str(filepath.relative_to(base_path))
        mtime = filepath.stat().st_mtime

        if not force and rel_path in self.metadata_cache:
            if self.metadata_cache[rel_path].get('mtime', 0) >= mtime:
                return False

        content = filepath.read_text(encoding='utf-8', errors='ignore')
        chunks = self.md_chunker.chunk_file(content, rel_path)

        if not chunks:
            return False

        # Remove old chunks
        try:
            self.collections['notes'].delete(where={"filepath": rel_path})
        except:
            pass

        # Add new chunks
        for chunk_text, metadata in chunks:
            chunk_id = hashlib.md5(f"{rel_path}:{chunk_text[:50]}".encode()).hexdigest()

            try:
                embedding = self.embed_text(chunk_text)

                self.collections['notes'].upsert(
                    ids=[chunk_id],
                    embeddings=[embedding],
                    documents=[chunk_text],
                    metadatas=[{
                        **metadata,
                        'indexed_at': datetime.now().isoformat()
                    }]
                )
            except Exception as e:
                logger.error(f"Error embedding chunk from {rel_path}: {e}")

        # Update metadata cache
        self.metadata_cache[rel_path] = {
            'mtime': mtime,
            'indexed_at': datetime.now().isoformat(),
            'chunk_count': len(chunks)
        }

        return True

    def index_single_document(self, filepath_str: str, source_type: str = 'notes', base_path: Optional[str] = None) -> bool:
        """
        Incrementally index a single document into RAG.
        
        Designed for the KnowledgeWriter: after saving a new note,
        index just that one file instead of rebuilding the entire collection.
        
        Args:
            filepath_str: Absolute path to the document
            source_type: 'notes', 'documents', or 'codebase'
            base_path: Root path to compute the relative path from. When provided,
                       rel_path = filepath.relative_to(base_path), which matches
                       the path key used by the bulk indexer (_index_markdown_file).
                       If omitted, falls back to filepath.name (filename only).
        
        Returns:
            True if indexing succeeded
        """
        filepath = Path(filepath_str)
        if not filepath.exists():
            logger.error(f"File does not exist for incremental index: {filepath}")
            return False
        
        if source_type not in self.collections:
            logger.error(f"Unknown source type: {source_type}")
            return False
        
        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore')
            if not content.strip():
                logger.warning(f"Empty file, skipping: {filepath}")
                return False
            
            # Derive relative path consistently with _index_markdown_file.
            # Using only filepath.name (the old behaviour) means domain sub-directory
            # info is lost, breaking domain-match scoring in the RetrievalClassifier
            # and making the chunk invisible to any path-prefix domain filters.
            if base_path:
                try:
                    rel_path = str(filepath.relative_to(Path(base_path)))
                except ValueError:
                    # filepath is not under base_path — fall back to name
                    logger.warning(f"filepath {filepath} is not under base_path {base_path}, using filename only")
                    rel_path = filepath.name
            else:
                rel_path = filepath.name
            
            # Chunk the content
            if source_type == 'notes':
                chunks = self.md_chunker.chunk_file(content, rel_path)
            else:
                chunks = self.md_chunker.chunk_file(content, rel_path)
            
            if not chunks:
                logger.warning(f"No chunks produced from: {filepath}")
                return False
            
            # Remove any existing chunks for this file
            collection = self.collections[source_type]
            try:
                collection.delete(where={"filepath": rel_path})
            except Exception:
                pass
            
            # Add new chunks with embeddings
            indexed_count = 0
            for chunk_text, metadata in chunks:
                chunk_id = hashlib.md5(f"{rel_path}:{chunk_text[:50]}".encode()).hexdigest()
                try:
                    embedding = self.embed_text(chunk_text)
                    collection.upsert(
                        ids=[chunk_id],
                        embeddings=[embedding],
                        documents=[chunk_text],
                        metadatas=[{
                            **metadata,
                            'filepath': rel_path,
                            'source_path': str(filepath),
                            'indexed_at': datetime.now().isoformat(),
                            'incremental': True,
                        }]
                    )
                    indexed_count += 1
                except Exception as e:
                    logger.error(f"Error embedding chunk from {rel_path}: {e}")
            
            # Update metadata cache
            self.metadata_cache[rel_path] = {
                'mtime': filepath.stat().st_mtime,
                'indexed_at': datetime.now().isoformat(),
                'chunk_count': indexed_count,
            }
            
            # Update BM25 index if hybrid search is enabled
            if self.use_hybrid_search and self.hybrid_searcher:
                bm25_cfg = self.config.get("rag", {}).get("bm25", {})
                if bm25_cfg.get("rebuild_on_index", False):
                    # Full rebuild + save (used when corpora are small)
                    self._rebuild_bm25_index()
                else:
                    # Mark dirty — triggers rebuild on next index run or startup (Spec 08)
                    from core.hybrid_search import PersistentBM25Index
                    if isinstance(self.hybrid_searcher.bm25_index, PersistentBM25Index):
                        self.hybrid_searcher.bm25_index.mark_dirty()
                        logger.debug("BM25 index marked dirty after single document index")
                    else:
                        self._rebuild_bm25_index()

            logger.info(f"Incrementally indexed {indexed_count} chunks from: {filepath.name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to incrementally index {filepath}: {e}", exc_info=True)
            return False

    def _index_code_file(self, filepath: Path, base_path: Path, force: bool = False) -> bool:
        """Index a single code file."""
        rel_path = str(filepath.relative_to(base_path))
        mtime = filepath.stat().st_mtime

        if not force and rel_path in self.metadata_cache:
            if self.metadata_cache[rel_path].get('mtime', 0) >= mtime:
                return False

        content = filepath.read_text(encoding='utf-8', errors='ignore')

        # Detect language
        lang_map = {
            '.py': 'python',
            '.rs': 'rust',
            '.go': 'go',
            '.ts': 'typescript',
            '.js': 'javascript',
            '.lua': 'lua',
            '.scd': 'supercollider'
        }
        language = lang_map.get(filepath.suffix, 'unknown')

        chunks = self.code_chunker.chunk_file(content, rel_path, language)

        if not chunks:
            return False

        # Extract code patterns if pattern engine is available
        if self.pattern_learner and language in ['python', 'javascript', 'typescript']:
            try:
                # Use PatternEngine.learn_code_patterns for regex-based extraction
                learned = self.pattern_learner.learn_code_patterns(
                    code=content,
                    domains=[],
                    filepath=rel_path,
                )
                if learned:
                    logger.debug(f"Extracted {len(learned)} patterns from {rel_path}")
            except Exception as e:
                logger.warning(f"Could not extract code patterns from {rel_path}: {e}")

        # Remove old chunks
        try:
            self.collections['codebase'].delete(where={"filepath": rel_path})
        except:
            pass

        # Add new chunks
        for chunk_text, metadata in chunks:
            chunk_id = hashlib.md5(f"{rel_path}:{metadata.get('name', '')}:{metadata.get('line', 0)}".encode()).hexdigest()

            try:
                embedding = self.embed_text(chunk_text)

                self.collections['codebase'].upsert(
                    ids=[chunk_id],
                    embeddings=[embedding],
                    documents=[chunk_text],
                    metadatas=[{
                        **metadata,
                        'indexed_at': datetime.now().isoformat()
                    }]
                )
            except Exception as e:
                logger.error(f"Error embedding chunk from {rel_path}: {e}")

        self.metadata_cache[rel_path] = {
            'mtime': mtime,
            'indexed_at': datetime.now().isoformat(),
            'chunk_count': len(chunks)
        }

        return True

    def _get_current_doc_ids(self) -> List[str]:
        """Fast: return all document IDs from searchable collections (IDs only — no content)."""
        doc_ids: List[str] = []
        for collection_name in ['notes', 'codebase', 'documents']:
            if collection_name not in self.collections:
                continue
            try:
                results = self.collections[collection_name].get(include=[])
                doc_ids.extend(results.get('ids', []))
            except Exception as e:
                logger.debug(f"Could not get doc IDs from {collection_name}: {e}")
        return doc_ids

    def _try_load_bm25_index(self) -> bool:
        """
        Attempt to load a persisted BM25 index from disk (Spec 08).

        Returns True if load succeeded and index is valid for current corpus.
        On failure, logs and returns False — caller handles lazy rebuild fallback.
        """
        from core.hybrid_search import PersistentBM25Index
        if not isinstance(self.hybrid_searcher.bm25_index, PersistentBM25Index):
            return False
        try:
            current_doc_ids = self._get_current_doc_ids()
            loaded = self.hybrid_searcher.bm25_index.load_if_valid(current_doc_ids)
            if loaded:
                doc_count = len(self.hybrid_searcher.bm25_index.corpus_docs)
                logger.info(f"BM25 index restored from disk: {doc_count} docs")
            else:
                logger.info("BM25 index not loaded from disk — will build on first index run")
            return loaded
        except Exception as e:
            logger.warning(f"BM25 index load attempt failed: {e}")
            return False

    def _rebuild_bm25_index(self):
        """Rebuild BM25 index from all collections for hybrid search"""
        if not self.use_hybrid_search or not self.hybrid_searcher:
            return
        
        logger.info("Rebuilding BM25 index for hybrid search...")
        
        documents = []
        
        # Gather all documents from collections we want to search
        for collection_name in ['notes', 'codebase', 'documents']:
            if collection_name not in self.collections:
                continue
            
            collection = self.collections[collection_name]
            
            try:
                # Get all documents from this collection
                results = collection.get(include=['documents', 'metadatas'])
                
                for doc, meta in zip(results['documents'], results['metadatas']):
                    # Create unique ID
                    doc_id = hashlib.md5((doc[:100] + meta.get('filepath', '')).encode()).hexdigest()
                    
                    documents.append({
                        'id': doc_id,
                        'content': doc,
                        'filepath': meta.get('filepath', ''),
                        'metadata': meta
                    })
            
            except Exception as e:
                logger.error(f"Error gathering documents from {collection_name} for BM25: {e}")
        
        # Build BM25 index
        self.hybrid_searcher.index_for_keyword_search(documents)
        logger.info(f"BM25 index built with {len(documents)} documents")

        # Persist to disk if using PersistentBM25Index (Spec 08)
        from core.hybrid_search import PersistentBM25Index
        if isinstance(self.hybrid_searcher.bm25_index, PersistentBM25Index):
            self.hybrid_searcher.bm25_index.save()

    def search(
        self,
        query: str,
        n_results: int = 5,
        source_types: Optional[List[str]] = None,
        domain_filter: Optional[str] = None,
        use_hybrid: Optional[bool] = None,
        domains: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """
        Search across all indexed sources using hybrid search (semantic + keyword).

        Args:
            query: The search query
            n_results: Number of results per source type
            source_types: Which sources to search ('notes', 'codebase', 'documents')
            domain_filter: Optional domain to filter by
            use_hybrid: Override to enable/disable hybrid search for this query
            domains: Optional list of detected domains for pattern-based collection weighting

        Returns:
            List of SearchResults sorted by relevance
        """
        # Determine if using hybrid for this search
        use_hybrid_this_search = use_hybrid if use_hybrid is not None else self.use_hybrid_search
        
        
        # Default sources plus any integration collections
        if source_types is None:
            source_types = ['notes', 'codebase', 'documents']
            # Automatically include any integration collections
            source_types.extend([name for name in self.collections.keys() 
                                if name.startswith('integration_')])
        
        logger.info(f"Searching collections: {source_types} (hybrid={'enabled' if use_hybrid_this_search else 'disabled'})")
        logger.info(f"Available collections: {list(self.collections.keys())}")

        # Phase 13A Days 9-11: Get collection priorities based on learned domain patterns
        collection_priorities = {}
        
        if self.pattern_learner and domains:
            for domain in domains:
                domain_str = domain.value if hasattr(domain, 'value') else str(domain)
                weights = self.pattern_learner.get_domain_priorities(domain_str)
                
                for coll, weight in weights.items():
                    # Use highest weight if multiple domains match same collection
                    collection_priorities[coll] = max(
                        collection_priorities.get(coll, 0),
                        weight
                    )
            
            if collection_priorities:
                logger.info(f"Collection priorities for domains {domains}: "
                          f"{dict(sorted(collection_priorities.items(), key=lambda x: x[1], reverse=True))}")

        query_embedding = self.embed_text(query)
        all_results = []
        doc_id_to_result = {}  # Map doc_id to result for hybrid search

        # Step 1: Perform semantic search across all collections
        for source_type in source_types:
            if source_type not in self.collections:
                continue

            # Phase 13A Days 9-11: Skip collections with very low priority if better options exist
            priority = collection_priorities.get(source_type, 1.0) if collection_priorities else 1.0
            
            # Universal cross-domain fix: Don't skip collections for multi-domain queries
            # When multiple domains detected, user likely needs cross-domain context
            is_multi_domain = domains and len(domains) >= 2
            
            # If this collection has very low priority AND we have high-priority alternatives, skip it
            # BUT: Never skip for multi-domain queries (prevents missing cross-domain content)
            if collection_priorities and not is_multi_domain:
                has_high_priority_alternatives = any(p > 1.5 for p in collection_priorities.values())
                # Lowered threshold: 0.5 → 0.3 (less aggressive filtering)
                if priority < 0.3 and has_high_priority_alternatives:
                    logger.info(f"⚡ Skipping {source_type} (low priority {priority:.2f}, have better alternatives)")
                    continue
            elif is_multi_domain and collection_priorities:
                # Log that we're keeping collection for cross-domain query
                if priority < 0.3:
                    logger.info(f"⚡ Keeping {source_type} despite low priority {priority:.2f} (multi-domain query: {len(domains)} domains)")
            
            # Phase 13A Days 9-11: Adjust n_results based on collection priority
            # High priority (> 2.0) → get more results (up to 2x)
            # Medium priority (1.0-2.0) → get normal results
            # Low priority (< 1.0) → get fewer results (down to 0.5x)
            if collection_priorities and source_type in collection_priorities:
                # Normalize priority to multiplier: weight 0-3 → multiplier 0.5-2.0
                # priority 0.5 → 0.6x, priority 1.0 → 0.8x, priority 2.0 → 1.2x, priority 3.0 → 1.5x
                priority_multiplier = 0.5 + (priority * 0.3)
                priority_multiplier = max(0.5, min(2.0, priority_multiplier))  # Clamp to 0.5-2.0
                adjusted_n = max(1, int(n_results * priority_multiplier))
                logger.info(f"⚡ Searching {source_type} with priority {priority:.2f} → "
                          f"{adjusted_n} results (multiplier={priority_multiplier:.2f}x)")
            else:
                adjusted_n = n_results

            collection = self.collections[source_type]

            try:
                # Get more results for hybrid search to work with
                search_n = adjusted_n * 4 if use_hybrid_this_search else adjusted_n
                
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=search_n
                )

                if results['documents'] and results['documents'][0]:
                    for doc, meta, dist in zip(
                        results['documents'][0],
                        results['metadatas'][0],
                        results['distances'][0]
                    ):
                        # Create consistent doc_id for hybrid search
                        doc_id = hashlib.md5((doc[:100] + meta.get('filepath', '')).encode()).hexdigest()
                        
                        chunk = Chunk(
                            id=doc_id,
                            content=doc,
                            filepath=meta.get('filepath', ''),
                            source_type=source_type,
                            metadata=meta
                        )

                        # Convert distance to similarity
                        score = 1 - dist
                        
                        result = SearchResult(
                            chunk=chunk,
                            score=score
                        )
                        
                        all_results.append(result)
                        doc_id_to_result[doc_id] = result

            except Exception as e:
                logger.error(f"Error searching {source_type}: {e}")

        # Step 1.5: Apply query→chunk pattern boosting (Spec 05: calibrated tier curve)
        if self.pattern_learner and all_results:
            try:
                qcp_dict = self.pattern_learner.query_chunk_patterns
                if qcp_dict:
                    query_sig = self.pattern_learner._create_query_signature(query)
                    matching_qcp = qcp_dict.get(f"qcp_{query_sig}")

                    if matching_qcp:
                        # Positive boost lookup
                        boost_lookup = {}
                        for sc in matching_qcp.successful_chunks:
                            hit_count = sc.get("hit_count", 1)
                            tier_boost = _hit_count_to_tier_boost(hit_count)
                            confidence_scale = 0.5 + 0.5 * matching_qcp.confidence
                            boost_lookup[sc["chunk_id"]] = tier_boost * confidence_scale

                        # Negative penalty lookup (decay old misses by 30-day half-life)
                        from datetime import datetime as _dt
                        penalty_lookup = {}
                        positive_override_threshold = 5  # hit_count above which positive overrides negative
                        for pc in getattr(matching_qcp, "penalised_chunks", []):
                            cid = pc["chunk_id"]
                            # Skip if strong positive evidence exists
                            if cid in boost_lookup and boost_lookup[cid] >= (
                                _hit_count_to_tier_boost(positive_override_threshold) * (0.5 + 0.5 * matching_qcp.confidence)
                            ):
                                continue
                            miss_count = pc.get("miss_count", 1)
                            # Apply 30-day decay to miss_count
                            try:
                                last_miss = _dt.fromisoformat(pc.get("last_miss", ""))
                                days_since = (_dt.now() - last_miss).days
                                if days_since > 30:
                                    miss_count *= (0.98 ** (days_since - 30))
                            except Exception:
                                pass
                            penalty_lookup[cid] = max(0.5, 1.0 - (miss_count * 0.08))

                        if boost_lookup or penalty_lookup:
                            boosted_count = penalised_count = 0
                            for result in all_results:
                                cid = result.chunk.id
                                if cid in boost_lookup:
                                    result.score *= boost_lookup[cid]
                                    boosted_count += 1
                                elif cid in penalty_lookup:
                                    result.score *= penalty_lookup[cid]
                                    penalised_count += 1
                            if boosted_count or penalised_count:
                                logger.info(
                                    f"Pattern boost applied: +{boosted_count} boosted, "
                                    f"-{penalised_count} penalised of {len(all_results)} chunks"
                                )
                                all_results.sort(key=lambda r: r.score, reverse=True)
            except Exception as e:
                logger.debug(f"Query→chunk boosting failed (non-critical): {e}")

        # Step 2: Apply hybrid search if enabled
        if use_hybrid_this_search and self.hybrid_searcher and all_results:
            logger.info(f"Applying hybrid search to {len(all_results)} semantic results")
            
            # Prepare semantic results for fusion
            semantic_results = [
                (r.chunk.id, r.score) 
                for r in all_results
            ]
            
            # Prepare metadata for title boosting
            doc_metadata = {
                r.chunk.id: {
                    'filepath': r.chunk.filepath,
                    'metadata': r.chunk.metadata
                }
                for r in all_results
            }
            
            # Perform hybrid search
            hybrid_results = self.hybrid_searcher.search(
                query=query,
                semantic_results=semantic_results,
                doc_metadata=doc_metadata,
                top_k=n_results * 3  # Get more for deduplication
            )
            
            # Update scores based on hybrid results
            for doc_id, final_score, breakdown in hybrid_results:
                if doc_id in doc_id_to_result:
                    result = doc_id_to_result[doc_id]
                    result.score = final_score
                    # Store breakdown in metadata for debugging
                    result.chunk.metadata['_hybrid_breakdown'] = breakdown
            
            # Re-sort by new hybrid scores
            all_results = [doc_id_to_result[doc_id] for doc_id, _, _ in hybrid_results if doc_id in doc_id_to_result]
        else:
            # Just use semantic scores
            all_results.sort(key=lambda r: r.score, reverse=True)
        
        # Log top results for debugging
        if all_results:
            search_type = "Hybrid" if use_hybrid_this_search else "Semantic"
            logger.info(f"Top {search_type} RAG results:")
            for i, result in enumerate(all_results[:5]):
                logger.info(f"  {i+1}. Score: {result.score:.3f} | Source: {result.chunk.source_type} | File: {result.chunk.filepath}")
                if '_hybrid_breakdown' in result.chunk.metadata:
                    bd = result.chunk.metadata['_hybrid_breakdown']
                    logger.info(f"     Breakdown: Semantic={bd['semantic_score']:.3f}, "
                              f"Keyword={bd['keyword_score']:.3f}, Boost={bd['title_boost']:.2f}x")
                logger.info(f"     Preview: {result.chunk.content[:100]}...")
        
        # Remove duplicates (prefer integration_ sources over documents)
        seen_content = {}
        unique_results = []
        for result in all_results:
            # Use first 100 chars as fingerprint
            fingerprint = result.chunk.content[:100]
            if fingerprint not in seen_content:
                seen_content[fingerprint] = result
                unique_results.append(result)
            else:
                # If this is from integration and existing is from documents, replace
                existing = seen_content[fingerprint]
                if result.chunk.source_type.startswith('integration_') and not existing.chunk.source_type.startswith('integration_'):
                    # Replace the existing one
                    idx = unique_results.index(existing)
                    unique_results[idx] = result
                    seen_content[fingerprint] = result
        
        
        # NEW: If top result has strong title match, fetch additional chunks from same document
        if unique_results and use_hybrid_this_search and self.hybrid_searcher:
            top_result = unique_results[0]
            top_filepath = top_result.chunk.filepath
            
            # Check if top result has strong title boost (indicating name match in query)
            if '_hybrid_breakdown' in top_result.chunk.metadata:
                title_boost = top_result.chunk.metadata['_hybrid_breakdown'].get('title_boost', 1.0)
                
                # If title boost is significant, get more chunks from this document
                if title_boost > 1.1:  # More than 10% boost means title matched
                    logger.info(f"Top result has strong title match ({title_boost:.2f}x boost), fetching more chunks from {top_filepath}")
                    
                    # Get additional chunks from this document from the original collections
                    additional_chunks = []
                    for source_type in ['notes', 'codebase', 'documents']:
                        if source_type not in self.collections:
                            continue
                        
                        collection = self.collections[source_type]
                        
                        try:
                            # Query for more chunks from this specific file
                            # SMART SAMPLING: Get enough chunks to cover structured documents
                            file_results = collection.get(
                                where={"filepath": top_filepath},
                                limit=100  # Get enough chunks to cover large structured documents
                            )
                            
                            if file_results['documents']:
                                # Separate chunks into categories
                                practice_headers = []  # Main PRACTICE headers
                                exercise_headers = []  # Exercise sub-headers
                                content_chunks = []  # Regular content
                                
                                for doc, meta in zip(file_results['documents'], file_results['metadatas']):
                                    doc_id = hashlib.md5((doc[:100] + meta.get('filepath', '')).encode()).hexdigest()
                                    
                                    # Skip if already in results
                                    if any(r.chunk.id == doc_id for r in unique_results):
                                        continue
                                    
                                    chunk = Chunk(
                                        id=doc_id,
                                        content=doc,
                                        filepath=meta.get('filepath', ''),
                                        source_type=source_type,
                                        metadata=meta
                                    )
                                    
                                    # Categorize chunks by importance
                                    content_stripped = doc.strip()
                                    
                                    # PRACTICE headers are most important
                                    if (content_stripped.startswith('## PRACTICE') or 
                                        content_stripped.startswith('PRACTICE ')):
                                        practice_headers.append(chunk)
                                    # Exercise headers are secondary
                                    elif (content_stripped.startswith('### Exercise') or
                                          content_stripped.startswith('## Exercise')):
                                        exercise_headers.append(chunk)
                                    # Everything else is content
                                    else:
                                        content_chunks.append(chunk)
                                
                                # STRATEGY: Prioritize PRACTICE headers, then exercises, then content
                                # This ensures we get all 10 PRACTICE headers first
                                
                                # 1. Add ALL practice headers (these are the 10 main practices)
                                for chunk in practice_headers:
                                    score = top_result.score * 0.98  # Highest priority
                                    additional_chunks.append(SearchResult(
                                        chunk=chunk,
                                        score=score
                                    ))
                                
                                # 2. Add exercise headers (sample if there are many)
                                max_exercises = 15  # Limit exercises to avoid overwhelming context
                                if len(exercise_headers) > max_exercises:
                                    # Sample evenly across exercises
                                    stride = len(exercise_headers) // max_exercises
                                    exercise_sample = exercise_headers[::stride][:max_exercises]
                                else:
                                    exercise_sample = exercise_headers
                                
                                for chunk in exercise_sample:
                                    score = top_result.score * 0.95
                                    additional_chunks.append(SearchResult(
                                        chunk=chunk,
                                        score=score
                                    ))
                                
                                # 3. Add some content chunks for context
                                max_content = 5  # Just a few content chunks
                                if len(content_chunks) > max_content:
                                    stride = len(content_chunks) // max_content
                                    content_sample = content_chunks[::stride][:max_content]
                                else:
                                    content_sample = content_chunks
                                
                                for chunk in content_sample:
                                    score = top_result.score * 0.90  # Lowest priority
                                    additional_chunks.append(SearchResult(
                                        chunk=chunk,
                                        score=score
                                    ))
                                
                                logger.info(f"Smart sampling: {len(practice_headers)} practice headers, "
                                          f"{len(exercise_sample)} exercises, {len(content_sample)} content chunks from {top_filepath}")
                        
                        except Exception as e:
                            logger.error(f"Error fetching additional chunks from {top_filepath}: {e}")
                    
                    if additional_chunks:
                        logger.info(f"Added {len(additional_chunks)} additional chunks from {top_filepath}")
                        # Insert additional chunks right after the top result
                        unique_results = [unique_results[0]] + additional_chunks + unique_results[1:]

        # Step 3: Apply optional compression to chunk content
        compression_config = self.config.get('compression', {})
        rag_compression_config = compression_config.get('rag_context', {})
        
        if rag_compression_config.get('enabled', False) and unique_results:
            logger.info("Applying compression to RAG context chunks")
            compressed_results = self._compress_search_results(
                unique_results,
                target_ratio=rag_compression_config.get('ratio', 0.5)
            )
            unique_results = compressed_results
        
        return unique_results[:n_results * 2]  # Return top results across all sources

    def get_all_github_repos(self) -> List[SearchResult]:
        """
        Get ALL GitHub repositories from the knowledge base.
        Uses metadata filtering instead of semantic search.
        """
        all_repos = []
        seen_repos = set()
        
        # Check both integration_github and documents collections
        for collection_name in ['integration_github', 'documents']:
            if collection_name not in self.collections:
                continue
                
            collection = self.collections[collection_name]
            
            try:
                # Get all items with source=github metadata
                results = collection.get(
                    where={"source": "github"},
                    include=["documents", "metadatas"]
                )
                
                if results and results['documents']:
                    for doc, meta in zip(results['documents'], results['metadatas']):
                        repo_name = meta.get('name', '')
                        if repo_name and repo_name not in seen_repos:
                            seen_repos.add(repo_name)
                            chunk = Chunk(
                                id=meta.get('id', ''),
                                content=doc,
                                filepath=meta.get('url', ''),
                                source_type=collection_name,
                                metadata=meta
                            )
                            # Give all repos same high score since we're not doing semantic search
                            all_repos.append(SearchResult(chunk=chunk, score=0.99))
            except Exception as e:
                logger.warning(f"Error fetching GitHub repos from {collection_name}: {e}")
                
        logger.info(f"Found {len(all_repos)} unique GitHub repositories")
        return all_repos

    def format_context(self, results: List[SearchResult], max_tokens: int = 3000, compact_github: bool = False) -> str:
        """
        Format search results into context string for LLM.
        
        Args:
            results: Search results to format
            max_tokens: Maximum tokens for context
            compact_github: If True, format GitHub repos as compact list (for "list all" queries)
        """
        # Special compact format for listing all GitHub repos
        if compact_github:
            github_repos = []
            for result in results:
                if (result.chunk.source_type.startswith('integration_') or 
                    result.chunk.metadata.get('source') == 'github'):
                    repo_name = result.chunk.metadata.get('name', '')
                    repo_desc = result.chunk.metadata.get('description', '')
                    repo_url = result.chunk.metadata.get('url', '')
                    language = result.chunk.metadata.get('language', '')
                    
                    if repo_name:
                        repo_info = f"- **{repo_name}**"
                        if repo_desc:
                            repo_info += f": {repo_desc}"
                        if language:
                            repo_info += f" (Language: {language})"
                        repo_info += f"\n  URL: {repo_url}"
                        github_repos.append(repo_info)
            
            if github_repos:
                return "## Your Connected GitHub Repositories\n\n" + "\n".join(github_repos)
            return ""
        
        # Normal formatting (existing code)
        context_parts = []
        total_tokens = 0

        for result in results:
            # Handle integration sources specially
            if result.chunk.source_type.startswith('integration_'):
                integration_name = result.chunk.source_type.replace('integration_', '').title()
                # Make it clear this is from the user's connected account
                if integration_name.lower() == 'github':
                    source_label = "Your Connected GitHub Account"
                else:
                    source_label = f"Your Connected {integration_name} Account"
            # Also check metadata for source type (for documents collection with source: github)
            elif result.chunk.metadata.get('source') == 'github':
                source_label = "Your Connected GitHub Account"
            else:
                source_label = {
                    'notes': 'Note',
                    'codebase': 'Code',
                    'documents': 'Document',
                    'patterns': 'Pattern'
                }.get(result.chunk.source_type, 'Source')

            header = f"**{source_label}: {result.chunk.filepath}**"
            if result.chunk.metadata.get('header'):
                header += f" (section: {result.chunk.metadata['header']})"
            elif result.chunk.metadata.get('name'):
                # For GitHub repos, show the repo name prominently
                if (result.chunk.source_type.startswith('integration_github') or 
                    result.chunk.metadata.get('source') == 'github'):
                    repo_name = result.chunk.metadata.get('name', '')
                    header = f"**{source_label} - Repository: {repo_name}**"
                else:
                    header += f" ({result.chunk.metadata.get('type', 'code')}: {result.chunk.metadata['name']})"

            # For GitHub repos, truncate long content to fit more repos
            content_text = result.chunk.content
            if (result.chunk.source_type.startswith('integration_github') or 
                result.chunk.metadata.get('source') == 'github'):
                # Limit README to first 500 chars for repo listings
                if len(content_text) > 500:
                    content_text = content_text[:500] + "...\n\n[README truncated for brevity]"
            
            content = f"{header}\n```\n{content_text}\n```"

            if total_tokens + TokenCounter.count(content) > max_tokens:
                break

            context_parts.append(content)
            total_tokens += TokenCounter.count(content)

        return "\n\n---\n\n".join(context_parts)

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about indexed content."""
        stats = {}

        for name, collection in self.collections.items():
            try:
                chunk_count = collection.count()

                # Count unique files by getting all metadata
                file_count = 0
                if chunk_count > 0:
                    try:
                        # Get all documents to count unique filepaths
                        result = collection.get(include=['metadatas'])
                        if result and result.get('metadatas'):
                            unique_files = set()
                            for meta in result['metadatas']:
                                if meta and meta.get('filepath'):
                                    unique_files.add(meta['filepath'])
                            file_count = len(unique_files)
                    except Exception as e:
                        logger.debug(f"Could not count files for {name}: {e}")

                stats[name] = {
                    'count': chunk_count,
                    'files': file_count,
                }
            except:
                stats[name] = {'count': 0, 'files': 0}

        return stats
    
    def _compress_search_results(
        self,
        results: List[SearchResult],
        target_ratio: float = 0.5
    ) -> List[SearchResult]:
        """
        Compress search result chunks using LLMLingua.
        
        Args:
            results: Search results to compress
            target_ratio: Target compression ratio
        
        Returns:
            Search results with compressed content
        """
        # Lazy-load compression manager
        if self._compression_manager is None:
            try:
                from core.compression.manager import CompressionManager
                self._compression_manager = CompressionManager(config=self.config)
                logger.info("Compression manager initialized for RAG")
            except ImportError as e:
                logger.error(f"Failed to import CompressionManager: {e}")
                return results
        
        compressed_results = []
        total_original_tokens = 0
        total_compressed_tokens = 0
        
        for result in results:
            try:
                # Compress chunk content
                compression_result = self._compression_manager.compress_text(
                    text=result.chunk.content,
                    strategy="llmlingua",  # Use LLMLingua for RAG context
                    target_ratio=target_ratio,
                    context_type="rag_context"
                )
                
                # Update chunk with compressed content
                result.chunk.content = compression_result['compressed_text']
                
                # Add compression metrics to metadata
                result.chunk.metadata['_compression'] = {
                    'original_tokens': compression_result['original_tokens'],
                    'compressed_tokens': compression_result['compressed_tokens'],
                    'ratio': compression_result['compression_ratio'],
                    'strategy': compression_result.get('strategy', 'llmlingua')
                }
                
                total_original_tokens += compression_result['original_tokens']
                total_compressed_tokens += compression_result['compressed_tokens']
                
                compressed_results.append(result)
                
            except Exception as e:
                logger.error(f"Failed to compress chunk: {e}")
                # Keep original chunk on error
                compressed_results.append(result)
        
        # Log compression stats
        if total_original_tokens > 0:
            actual_ratio = total_compressed_tokens / total_original_tokens
            tokens_saved = total_original_tokens - total_compressed_tokens
            logger.info(
                f"RAG context compressed: {total_original_tokens} → {total_compressed_tokens} tokens "
                f"({actual_ratio:.2f}x ratio, saved {tokens_saved} tokens)"
            )
        
        return compressed_results