"""
Package Metadata Fetcher
Phase 23.5: Security Hardening

Fetches package metadata from PyPI and Context7 for package approval workflow.
"""

from typing import Dict, Any, Optional
import logging
import aiohttp
from pathlib import Path

logger = logging.getLogger(__name__)


class PackageMetadata:
    """Package metadata from PyPI and Context7."""
    
    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        version: Optional[str] = None,
        author: Optional[str] = None,
        homepage: Optional[str] = None,
        context7_trust_score: Optional[float] = None,
        context7_info: Optional[Dict[str, Any]] = None,
        pypi_info: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.description = description
        self.version = version
        self.author = author
        self.homepage = homepage
        self.context7_trust_score = context7_trust_score
        self.context7_info = context7_info or {}
        self.pypi_info = pypi_info or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "homepage": self.homepage,
            "context7_trust_score": self.context7_trust_score,
            "context7_info": self.context7_info,
            "pypi_info": self.pypi_info
        }


class PackageMetadataFetcher:
    """
    Fetches package metadata from PyPI and Context7.
    
    Used in package approval workflow to show users information about
    packages before they approve installation.
    """
    
    PYPI_API_BASE = "https://pypi.org/pypi"
    CACHE: Dict[str, PackageMetadata] = {}  # Simple in-memory cache
    
    def __init__(self, context7_integration=None):
        """
        Initialize metadata fetcher.
        
        Args:
            context7_integration: Optional Context7Integration instance for trust scores
        """
        self.context7 = context7_integration
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def fetch_metadata(self, package_name: str) -> PackageMetadata:
        """
        Fetch metadata for a package from PyPI and Context7.
        
        Args:
            package_name: Name of the package
            
        Returns:
            PackageMetadata with information from both sources
        """
        # Check cache
        cache_key = package_name.lower()
        if cache_key in self.CACHE:
            return self.CACHE[cache_key]
        
        # Fetch from PyPI
        pypi_info = await self._fetch_pypi_info(package_name)
        
        # Fetch from Context7 if available
        context7_info = None
        context7_trust_score = None
        if self.context7:
            try:
                context7_info = await self._fetch_context7_info(package_name)
                if context7_info:
                    context7_trust_score = context7_info.get("trustScore")
            except Exception as e:
                logger.warning(f"Failed to fetch Context7 info for {package_name}: {e}")
        
        # Build metadata
        metadata = PackageMetadata(
            name=package_name,
            description=pypi_info.get("info", {}).get("summary", ""),
            version=pypi_info.get("info", {}).get("version"),
            author=pypi_info.get("info", {}).get("author", ""),
            homepage=pypi_info.get("info", {}).get("home_page"),
            context7_trust_score=context7_trust_score,
            context7_info=context7_info or {},
            pypi_info=pypi_info
        )
        
        # Cache it
        self.CACHE[cache_key] = metadata
        
        return metadata
    
    async def _fetch_pypi_info(self, package_name: str) -> Dict[str, Any]:
        """Fetch package info from PyPI."""
        try:
            session = await self._get_session()
            url = f"{self.PYPI_API_BASE}/{package_name}/json"
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    return await resp.json()
                elif resp.status == 404:
                    logger.warning(f"Package not found on PyPI: {package_name}")
                    return {}
                else:
                    logger.warning(f"PyPI API error for {package_name}: {resp.status}")
                    return {}
        except Exception as e:
            logger.error(f"Error fetching PyPI info for {package_name}: {e}")
            return {}
    
    async def _fetch_context7_info(self, package_name: str) -> Optional[Dict[str, Any]]:
        """Fetch library info from Context7."""
        if not self.context7 or not hasattr(self.context7, '_search_library'):
            return None
        
        try:
            # Use Context7's search method
            library_info = await self.context7._search_library(package_name, "package metadata")
            return library_info
        except Exception as e:
            logger.warning(f"Context7 search failed for {package_name}: {e}")
            return None
    
    async def close(self):
        """Close aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None


# Global metadata fetcher instance
_metadata_fetcher: Optional[PackageMetadataFetcher] = None


async def get_package_metadata_fetcher() -> PackageMetadataFetcher:
    """Get global package metadata fetcher instance."""
    global _metadata_fetcher
    if _metadata_fetcher is None:
        # Try to get Context7 integration if available
        context7 = None
        try:
            from integrations.context7 import Context7Integration
            # Check if Context7 is connected (would need integration manager)
            # For now, we'll create without Context7 and add it later if needed
        except ImportError:
            pass
        
        _metadata_fetcher = PackageMetadataFetcher(context7_integration=context7)
    return _metadata_fetcher
