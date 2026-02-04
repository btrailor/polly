"""
Dataview Query Converter
Handles conversion of Obsidian Dataview queries during migration to Polly.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import re
import logging

logger = logging.getLogger(__name__)


class DataviewConverter:
    """Converts Obsidian Dataview queries to Polly equivalents."""
    
    # Supported Dataview query types
    QUERY_TYPES = [
        'TABLE',
        'LIST',
        'TASK',
        'CALENDAR',
        'PAGES',
        'FILE',
        'GROUP'
    ]
    
    def __init__(self):
        """Initialize the Dataview converter."""
        pass
    
    def detect_queries(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract all Dataview queries from markdown content.
        
        Args:
            content: Markdown file content
        
        Returns:
            List of dicts containing query info:
            [
                {
                    'raw': '```dataview\\nTABLE...\\n```',
                    'query': 'TABLE status...',
                    'type': 'TABLE',
                    'start_pos': 123,
                    'end_pos': 456
                }
            ]
        """
        queries = []
        pattern = r'```dataview\n([\s\S]*?)\n```'
        
        for match in re.finditer(pattern, content):
            query_text = match.group(1).strip()
            query_type = self._detect_query_type(query_text)
            
            queries.append({
                'raw': match.group(0),
                'query': query_text,
                'type': query_type,
                'start_pos': match.start(),
                'end_pos': match.end()
            })
        
        return queries
    
    def _detect_query_type(self, query: str) -> str:
        """Detect the type of Dataview query."""
        first_line = query.split('\n')[0].strip().upper()
        
        for query_type in self.QUERY_TYPES:
            if first_line.startswith(query_type):
                return query_type
        
        return 'UNKNOWN'
    
    def convert_to_static(self, query: str, vault_path: Path) -> str:
        """
        Convert Dataview query to static markdown content.
        
        This executes the query once and freezes the results as markdown.
        Since we don't have the Dataview engine, we'll create a placeholder
        that documents what the query was.
        
        Args:
            query: Dataview query string
            vault_path: Path to Obsidian vault (for context)
        
        Returns:
            Markdown representation of query (static)
        """
        logger.info(f"Converting Dataview query to static: {query[:50]}...")
        
        # Extract key information from query
        query_type = self._detect_query_type(query)
        filters = self._extract_filters(query)
        
        # Build static markdown representation
        static_content = f"<!-- Dataview query converted to static content -->\n"
        static_content += f"**Original Query:** `{query_type}`\n\n"
        
        if filters.get('from'):
            static_content += f"**Source:** {filters['from']}\n"
        if filters.get('where'):
            static_content += f"**Filters:** {filters['where']}\n"
        
        static_content += "\n> ⚠️ This was a Dataview query that has been frozen during migration.\n"
        static_content += "> To update this list, use Polly's search features.\n\n"
        
        static_content += "<!-- Original query:\n"
        static_content += f"```dataview\n{query}\n```\n"
        static_content += "-->\n"
        
        return static_content
    
    def convert_to_search_link(self, query: str) -> str:
        """
        Convert Dataview query to Polly search link.
        
        Extracts filters from the query and builds a polly://search URL
        that can be clicked to open Polly search with those filters.
        
        Args:
            query: Dataview query string
        
        Returns:
            Markdown link to Polly search
        """
        logger.info(f"Converting Dataview query to search link: {query[:50]}...")
        
        filters = self._extract_filters(query)
        
        # Build search URL
        search_params = []
        
        if filters.get('from'):
            # Extract tag from FROM clause (e.g., "FROM #project" -> "tag=project")
            from_clause = filters['from']
            if '#' in from_clause:
                tags = re.findall(r'#([a-zA-Z0-9/_-]+)', from_clause)
                for tag in tags:
                    search_params.append(f"tag={tag}")
            elif '"' in from_clause:
                # Folder path
                folder = from_clause.strip('"')
                search_params.append(f"folder={folder}")
        
        if filters.get('where'):
            # Try to extract simple filters from WHERE clause
            where_clause = filters['where']
            
            # Status filter
            status_match = re.search(r'status\s*=\s*"([^"]+)"', where_clause)
            if status_match:
                search_params.append(f"status={status_match.group(1)}")
            
            # Priority filter
            priority_match = re.search(r'priority\s*=\s*"([^"]+)"', where_clause)
            if priority_match:
                search_params.append(f"priority={priority_match.group(1)}")
        
        # Build the search URL
        if search_params:
            search_url = f"polly://search?{'&'.join(search_params)}"
        else:
            search_url = "polly://search"
        
        # Create markdown content
        search_content = f"<!-- Dataview query converted to search link -->\n"
        search_content += f"[🔍 Open in Polly Search]({search_url})\n\n"
        search_content += "> This Dataview query has been converted to a Polly search link.\n"
        search_content += "> Click the link above to search for matching notes.\n\n"
        
        search_content += "<details>\n"
        search_content += "<summary>Original Dataview query</summary>\n\n"
        search_content += f"```dataview\n{query}\n```\n\n"
        search_content += "</details>\n"
        
        return search_content
    
    def remove_query(self, query: str) -> str:
        """
        Remove Dataview query entirely.
        
        Replaces the query with a comment indicating it was removed.
        
        Args:
            query: Dataview query string
        
        Returns:
            Empty string or comment
        """
        logger.info(f"Removing Dataview query: {query[:50]}...")
        
        return "<!-- Dataview query removed during migration -->\n"
    
    def _extract_filters(self, query: str) -> Dict[str, str]:
        """
        Extract filter information from Dataview query.
        
        Returns dict with keys: 'from', 'where', 'sort', 'limit'
        """
        filters = {}
        
        # Extract FROM clause
        from_match = re.search(r'FROM\s+([^\n]+)', query, re.IGNORECASE)
        if from_match:
            filters['from'] = from_match.group(1).strip()
        
        # Extract WHERE clause
        where_match = re.search(r'WHERE\s+([^\n]+)', query, re.IGNORECASE)
        if where_match:
            filters['where'] = where_match.group(1).strip()
        
        # Extract SORT clause
        sort_match = re.search(r'SORT\s+([^\n]+)', query, re.IGNORECASE)
        if sort_match:
            filters['sort'] = sort_match.group(1).strip()
        
        # Extract LIMIT clause
        limit_match = re.search(r'LIMIT\s+(\d+)', query, re.IGNORECASE)
        if limit_match:
            filters['limit'] = limit_match.group(1)
        
        return filters
    
    def convert_queries_in_file(
        self,
        file_path: Path,
        conversions: Dict[int, str],
        output_path: Optional[Path] = None
    ) -> str:
        """
        Convert all Dataview queries in a file according to specified conversions.
        
        Args:
            file_path: Path to markdown file
            conversions: Dict mapping query index to conversion type ('static', 'search_link', 'remove')
            output_path: Optional path to write converted file (defaults to overwrite original)
        
        Returns:
            Converted file content
        """
        content = file_path.read_text(encoding='utf-8')
        queries = self.detect_queries(content)
        
        # Sort queries by position (reverse order) so we can replace without affecting positions
        queries_sorted = sorted(enumerate(queries), key=lambda x: x[1]['start_pos'], reverse=True)
        
        converted_content = content
        
        for idx, query in queries_sorted:
            conversion_type = conversions.get(idx, 'static')  # Default to static
            
            # Get replacement text based on conversion type
            if conversion_type == 'static':
                replacement = self.convert_to_static(query['query'], file_path.parent)
            elif conversion_type == 'search_link':
                replacement = self.convert_to_search_link(query['query'])
            elif conversion_type == 'remove':
                replacement = self.remove_query(query['query'])
            else:
                logger.warning(f"Unknown conversion type: {conversion_type}, using static")
                replacement = self.convert_to_static(query['query'], file_path.parent)
            
            # Replace query in content
            converted_content = (
                converted_content[:query['start_pos']] +
                replacement +
                converted_content[query['end_pos']:]
            )
        
        # Write to output file if specified
        if output_path:
            output_path.write_text(converted_content, encoding='utf-8')
            logger.info(f"Wrote converted file to {output_path}")
        
        return converted_content
    
    def batch_convert_vault(
        self,
        vault_path: Path,
        conversion_type: str = 'static',
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Batch convert all Dataview queries in a vault.
        
        Args:
            vault_path: Path to Obsidian vault
            conversion_type: Default conversion type ('static', 'search_link', 'remove')
            dry_run: If True, don't modify files, just report what would be done
        
        Returns:
            Dict with conversion statistics
        """
        stats = {
            'files_scanned': 0,
            'files_with_queries': 0,
            'total_queries': 0,
            'converted_files': [],
            'errors': []
        }
        
        for md_file in vault_path.rglob("*.md"):
            stats['files_scanned'] += 1
            
            try:
                content = md_file.read_text(encoding='utf-8')
                queries = self.detect_queries(content)
                
                if queries:
                    stats['files_with_queries'] += 1
                    stats['total_queries'] += len(queries)
                    
                    if not dry_run:
                        # Convert all queries in this file
                        conversions = {i: conversion_type for i in range(len(queries))}
                        self.convert_queries_in_file(md_file, conversions, output_path=md_file)
                    
                    stats['converted_files'].append({
                        'path': str(md_file.relative_to(vault_path)),
                        'query_count': len(queries)
                    })
                    
            except Exception as e:
                logger.error(f"Error processing {md_file}: {e}")
                stats['errors'].append({
                    'file': str(md_file.relative_to(vault_path)),
                    'error': str(e)
                })
        
        return stats
