"""
Context7 Integration
Fetches and indexes library documentation from Context7
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import aiohttp
import logging

from .base import Integration, IntegrationStatus, IntegrationError

logger = logging.getLogger(__name__)


class Context7Integration(Integration):
    """
    Context7 integration for Polly.
    
    Fetches and indexes:
    - Library documentation
    - Code examples
    - API references
    """
    
    CONTEXT7_API_BASE = "https://context7.com/api/v2"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("context7", config)
        self.api_key: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.cached_libraries: Dict[str, Dict] = {}  # Cache library search results
        
    async def connect(self, credentials: Dict[str, str]) -> bool:
        """
        Connect to Context7 using API key.
        
        Args:
            credentials: {"api_key": "ctx7sk-..."}
        """
        self.api_key = credentials.get("api_key")
        if not self.api_key:
            raise IntegrationError("No API key provided")
        
        # Validate API key format
        if not self.api_key.startswith("ctx7sk-"):
            raise IntegrationError("Invalid API key format. Must start with 'ctx7sk-'")
        
        # Create HTTP session
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "Polly-AI"
            }
        )
        
        # Test connection
        try:
            success = await self.test_connection()
            if success:
                self._set_status(IntegrationStatus.CONNECTED)
                logger.info("Context7 connected successfully")
            return success
        except Exception as e:
            await self.disconnect()
            raise IntegrationError(f"Connection failed: {e}")
    
    async def disconnect(self) -> bool:
        """Disconnect from Context7."""
        if self.session:
            await self.session.close()
            self.session = None
        
        self.api_key = None
        self.cached_libraries.clear()
        self._set_status(IntegrationStatus.DISCONNECTED)
        return True
    
    async def test_connection(self) -> bool:
        """Test Context7 connection by searching for a common library."""
        if not self.session:
            return False
        
        try:
            # Try to search for React as a test
            async with self.session.get(
                f"{self.CONTEXT7_API_BASE}/libs/search",
                params={"libraryName": "react", "query": "test connection"}
            ) as resp:
                if resp.status == 200:
                    results = await resp.json()
                    return len(results) > 0
                elif resp.status == 401:
                    logger.error("Context7 auth failed: Invalid API key")
                    return False
                else:
                    error_text = await resp.text()
                    logger.error(f"Context7 test failed: {resp.status} - {error_text}")
                    return False
        except Exception as e:
            logger.error(f"Context7 connection test failed: {e}")
            return False
    
    async def fetch_data(
        self,
        libraries: List[str] = None,
        query: str = "documentation and examples"
    ) -> Dict[str, Any]:
        """
        Fetch documentation for specified libraries.
        
        Args:
            libraries: List of library names to fetch (e.g., ["react", "nextjs", "python"])
            query: Query to use when fetching context (helps relevance ranking)
            
        Returns:
            Dict with documentation data and metadata
        """
        if not self.session:
            raise IntegrationError("Not connected to Context7")
        
        if not libraries:
            libraries = ["react", "nextjs", "typescript"]  # Default libraries
        
        self._set_status(IntegrationStatus.SYNCING)
        all_docs = []
        fetched_libraries = {}
        
        try:
            for library_name in libraries:
                logger.info(f"Fetching documentation for {library_name}")
                
                # Step 1: Search for the library
                library_info = await self._search_library(library_name, query)
                if not library_info:
                    logger.warning(f"Library '{library_name}' not found")
                    continue
                
                # Step 2: Get documentation context
                docs = await self._get_context(library_info["id"], query)
                
                # Step 3: Format for RAG
                for doc in docs:
                    all_docs.append({
                        "title": f"{library_info.get('title', library_name)}: {doc.get('title', 'Documentation')}",
                        "content": doc.get("content", ""),
                        "source": doc.get("source", library_info.get("title", library_name)),
                        "library_id": library_info["id"],
                        "library_name": library_info.get("title", library_name),
                        "trust_score": library_info.get("trustScore", 0),
                        "fetched_at": datetime.utcnow().isoformat()
                    })
                
                fetched_libraries[library_name] = {
                    "id": library_info["id"],
                    "title": library_info.get("title"),
                    "doc_count": len(docs)
                }
                
                logger.info(f"Fetched {len(docs)} docs for {library_name}")
            
            self._set_status(IntegrationStatus.CONNECTED)
            
            return {
                "documentation": all_docs,
                "metadata": {
                    "fetched_at": datetime.utcnow().isoformat(),
                    "libraries": fetched_libraries,
                    "total_docs": len(all_docs)
                }
            }
            
        except Exception as e:
            self._set_status(IntegrationStatus.ERROR, str(e))
            raise IntegrationError(f"Failed to fetch Context7 data: {e}")
    
    async def _search_library(self, library_name: str, query: str) -> Optional[Dict]:
        """
        Search for a library by name.
        
        Returns the best matching library info or None if not found.
        """
        # Check cache first
        cache_key = library_name.lower()
        if cache_key in self.cached_libraries:
            return self.cached_libraries[cache_key]
        
        try:
            async with self.session.get(
                f"{self.CONTEXT7_API_BASE}/libs/search",
                params={"libraryName": library_name, "query": query}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = data.get("results", [])
                    if results and len(results) > 0:
                        # Take the first (best) result
                        best_match = results[0]
                        self.cached_libraries[cache_key] = best_match
                        return best_match
                    else:
                        logger.warning(f"No results for library: {library_name}")
                        return None
                elif resp.status == 429:
                    logger.error("Context7 rate limit exceeded")
                    raise IntegrationError("Rate limit exceeded. Try again later.")
                else:
                    error_text = await resp.text()
                    logger.error(f"Library search failed: {resp.status} - {error_text}")
                    return None
        except aiohttp.ClientError as e:
            logger.error(f"Library search request failed: {e}")
            return None
    
    async def _get_context(self, library_id: str, query: str) -> List[Dict]:
        """
        Get documentation context for a library.
        
        Returns list of documentation snippets.
        """
        try:
            async with self.session.get(
                f"{self.CONTEXT7_API_BASE}/context",
                params={
                    "libraryId": library_id,
                    "query": query,
                    "type": "json"  # Request JSON format
                }
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # API returns {codeSnippets: [...]} format
                    snippets = data.get("codeSnippets", [])
                    
                    # Transform snippets to simpler format
                    docs = []
                    for snippet in snippets:
                        # Combine code examples if present
                        code_content = ""
                        if snippet.get("codeList"):
                            code_content = "\n\n".join([
                                f"```{item.get('language', '')}\n{item.get('code', '')}\n```"
                                for item in snippet.get("codeList", [])
                            ])
                        
                        docs.append({
                            "title": snippet.get("codeTitle", "Documentation"),
                            "content": f"{snippet.get('codeDescription', '')}\n\n{code_content}",
                            "source": snippet.get("codeId", ""),
                            "page_title": snippet.get("pageTitle", ""),
                            "language": snippet.get("codeLanguage", "")
                        })
                    
                    return docs
                elif resp.status == 429:
                    logger.error("Context7 rate limit exceeded")
                    raise IntegrationError("Rate limit exceeded. Try again later.")
                elif resp.status == 404:
                    logger.warning(f"Library not found: {library_id}")
                    return []
                else:
                    error_text = await resp.text()
                    logger.error(f"Context fetch failed: {resp.status} - {error_text}")
                    return []
        except aiohttp.ClientError as e:
            logger.error(f"Context request failed: {e}")
            return []
    
    def format_for_rag(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format Context7 documentation for RAG indexing.
        
        Args:
            data: Raw data dict from fetch_data() with 'documentation' and 'metadata'
            
        Returns:
            List of formatted chunks for RAG
        """
        formatted = []
        docs = data.get("documentation", [])
        
        for doc in docs:
            # Create a comprehensive text representation
            text_parts = []
            
            # Add library context
            text_parts.append(f"Library: {doc['library_name']}")
            text_parts.append(f"Documentation: {doc['title']}")
            
            # Add main content
            if doc.get("content"):
                text_parts.append(doc["content"])
            
            # Add source reference
            if doc.get("source"):
                text_parts.append(f"\nSource: {doc['source']}")
            
            formatted_text = "\n\n".join(text_parts)
            
            formatted.append({
                "content": formatted_text,
                "title": doc["title"],
                "filepath": f"context7://{doc['library_id']}",
                "source_type": "integration_context7",
                "metadata": {
                    "library_id": doc["library_id"],
                    "library_name": doc["library_name"],
                    "trust_score": doc.get("trust_score", 0),
                    "source_url": doc.get("source", ""),
                    "fetched_at": doc.get("fetched_at")
                }
            })
        
        return formatted
    
    def get_sync_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of synced data."""
        docs = data.get("documentation", [])
        metadata = data.get("metadata", {})
        
        libraries = {}
        for doc in docs:
            lib_name = doc.get("library_name", "Unknown")
            if lib_name not in libraries:
                libraries[lib_name] = 0
            libraries[lib_name] += 1
        
        return {
            "total_docs": len(docs),
            "libraries": libraries,
            "library_count": len(libraries),
            "fetched_at": metadata.get("fetched_at")
        }
