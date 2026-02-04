"""
Obsidian Smart Features
Intelligent note operations powered by RAG, DomainEngine, and LLM
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
import logging
import re

logger = logging.getLogger(__name__)


class ObsidianSmartFeatures:
    """
    Smart features for Obsidian integration.
    
    Provides:
    - Smart folder suggestions (DomainEngine-powered)
    - Intelligent tag suggestions (RAG + domain knowledge)
    - Related notes discovery (semantic similarity)
    - Daily note creation with context
    - Conversation to note conversion
    """
    
    def __init__(self, obsidian_integration, domain_engine, rag_engine):
        """
        Initialize smart features.
        
        Args:
            obsidian_integration: ObsidianIntegration instance
            domain_engine: DomainEngine instance
            rag_engine: RAG engine instance
        """
        self.obsidian = obsidian_integration
        self.domain_engine = domain_engine
        self.rag = rag_engine
        
        # Domain to folder mapping
        self.domain_folder_mapping = {
            "Sigils": "01-Sigils",
            "Signals": "02-Signals", 
            "Scrolls": "03-Scrolls",
            "Glyphs": "04-Glyphs",
            "Grids": "05-Grids"
        }
        
    async def suggest_folder(
        self, 
        content: str, 
        title: str,
        existing_structure: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Suggest folder based on content using DomainEngine.
        
        Args:
            content: Note content to analyze
            title: Note title
            existing_structure: Optional vault structure for subfolder suggestions
            
        Returns:
            Dict with suggested_folder, confidence, reasoning, etc.
        """
        try:
            # Combine title and content for analysis
            full_text = f"{title}\n\n{content}"
            
            # Detect domains with scores
            domain_scores = self.domain_engine.detect_domains_with_scores(
                query=full_text,
                context={"source": "obsidian_note"}
            )
            
            if not domain_scores:
                return {
                    "suggested_folder": "30-Ideas",
                    "suggested_subfolder": None,
                    "confidence": 0.5,
                    "domain": "Unknown",
                    "reasoning": "Could not determine domain, defaulting to Ideas folder",
                    "alternatives": []
                }
            
            # Get primary domain
            primary_domain, primary_score = domain_scores[0]
            
            # Extract domain name from enum
            if hasattr(primary_domain, 'value'):
                domain_key = primary_domain.value.title()  # 'signals' -> 'Signals'
            elif hasattr(primary_domain, 'name'):
                domain_key = primary_domain.name.title()  # 'SIGNALS' -> 'Signals'
            else:
                domain_key = str(primary_domain)
            
            # Store domain_name for use in reasoning and response
            domain_name = domain_key
            
            # Map domain to folder
            suggested_folder = self.domain_folder_mapping.get(
                domain_key,
                "30-Ideas"  # Default fallback
            )
            
            # Suggest subfolder based on content analysis
            suggested_subfolder = await self._suggest_subfolder(
                suggested_folder,
                full_text,
                existing_structure
            )
            
            # Build alternatives list
            alternatives = []
            for domain, score in domain_scores[1:3]:  # Next 2 domains
                if score > 0.3:  # Only meaningful alternatives
                    # Extract domain name consistently
                    if hasattr(domain, 'value'):
                        alt_domain_name = domain.value.title()
                    elif hasattr(domain, 'name'):
                        alt_domain_name = domain.name.title()
                    else:
                        alt_domain_name = str(domain)
                    
                    alternatives.append({
                        "folder": self.domain_folder_mapping.get(alt_domain_name, "30-Ideas"),
                        "domain": alt_domain_name,
                        "reason": f"If focusing on {alt_domain_name} aspects",
                        "confidence": round(score, 2)
                    })
            
            # Generate reasoning
            reasoning = self._explain_folder_choice(
                domain_name,
                primary_score,
                full_text
            )
            
            return {
                "suggested_folder": suggested_folder,
                "suggested_subfolder": suggested_subfolder,
                "confidence": round(primary_score, 2),
                "domain": domain_name,
                "reasoning": reasoning,
                "alternatives": alternatives
            }
            
        except Exception as e:
            logger.error(f"Error suggesting folder: {e}")
            return {
                "suggested_folder": "30-Ideas",
                "suggested_subfolder": None,
                "confidence": 0.0,
                "domain": "Unknown",
                "reasoning": f"Error during analysis: {str(e)}",
                "alternatives": []
            }
    
    async def _suggest_subfolder(
        self,
        parent_folder: str,
        content: str,
        existing_structure: Optional[Dict]
    ) -> Optional[str]:
        """
        Suggest a subfolder within the parent folder.
        
        Uses RAG to find similar notes and their folder structure.
        """
        try:
            # Query RAG for similar notes in this domain
            similar_notes = self.rag.search(
                query=content[:1000],  # Use beginning of content
                n_results=5,
                source_types=['obsidian']
            )
            
            if not similar_notes:
                return None
            
            # Extract subfolder patterns from similar notes
            subfolder_counts = {}
            for result in similar_notes:
                # Get path from metadata
                note_path = result.chunk.filepath
                if not note_path:
                    continue
                
                # Extract subfolder between parent and filename
                # e.g., "02-Signals/Audio-Engines/synthesis.md" -> "Audio-Engines"
                parts = Path(note_path).parts
                if len(parts) > 2:  # Has subfolder
                    subfolder = parts[1] if parent_folder in parts[0] else None
                    if subfolder:
                        subfolder_counts[subfolder] = subfolder_counts.get(subfolder, 0) + 1
            
            # Return most common subfolder if meaningful
            if subfolder_counts:
                most_common = max(subfolder_counts.items(), key=lambda x: x[1])
                if most_common[1] >= 2:  # At least 2 similar notes
                    return most_common[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error suggesting subfolder: {e}")
            return None
    
    def _explain_folder_choice(
        self,
        domain: str,
        confidence: float,
        content: str
    ) -> str:
        """Generate human-readable explanation for folder choice."""
        
        # Extract key domain indicators from content
        indicators = []
        content_lower = content.lower()
        
        # Domain-specific keywords to highlight
        domain_keywords = {
            "Sigils": ["code", "api", "infrastructure", "automation"],
            "Signals": ["audio", "synthesis", "midi", "dsp"],
            "Scrolls": ["writing", "documentation", "pedagogy"],
            "Glyphs": ["design", "visual", "ui", "ux"],
            "Grids": ["framework", "system", "pattern", "model"]
        }
        
        if domain in domain_keywords:
            for keyword in domain_keywords[domain]:
                if keyword in content_lower:
                    indicators.append(keyword)
        
        # Build explanation
        if confidence > 0.8:
            strength = "clearly"
        elif confidence > 0.6:
            strength = "primarily"
        else:
            strength = "seems to"
        
        explanation = f"Content {strength} relates to {domain}"
        
        if indicators:
            indicator_text = ", ".join(indicators[:3])
            explanation += f" (mentions: {indicator_text})"
        
        return explanation
    
    async def suggest_tags(
        self,
        content: str,
        title: str,
        existing_tags: Optional[List[str]] = None,
        max_suggestions: int = 10
    ) -> Dict[str, Any]:
        """
        Suggest tags using RAG + domain knowledge.
        
        Args:
            content: Note content
            title: Note title
            existing_tags: Tags already on the note
            max_suggestions: Maximum number of suggestions
            
        Returns:
            Dict with suggested_tags, tag_groups, reasoning
        """
        try:
            existing_tags = existing_tags or []
            full_text = f"{title}\n\n{content}"
            
            # 1. Get domain-specific tags
            domain_scores = self.domain_engine.detect_domains_with_scores(full_text)
            primary_domain = domain_scores[0][0] if domain_scores else None
            domain_tags = self._get_domain_tags(primary_domain) if primary_domain else []
            
            # 2. Extract concept tags from content
            concept_tags = self._extract_concept_tags(full_text)
            
            # 3. Query RAG for similar notes
            similar_notes = self.rag.search(
                query=content[:1000],
                n_results=10,
                source_types=['obsidian']
            )
            
            # 4. Analyze tags from similar notes
            similar_tags = self._analyze_tags_from_similar(similar_notes)
            
            # 5. Combine and rank suggestions
            all_suggestions = []
            
            # Add domain tags (high confidence)
            for tag in domain_tags:
                if tag not in existing_tags:
                    all_suggestions.append({
                        "tag": tag,
                        "confidence": 0.9,
                        "source": "domain"
                    })
            
            # Add concept tags (medium confidence)
            for tag in concept_tags:
                if tag not in existing_tags and tag not in domain_tags:
                    all_suggestions.append({
                        "tag": tag,
                        "confidence": 0.7,
                        "source": "content"
                    })
            
            # Add similar note tags (variable confidence based on frequency)
            for tag, count in similar_tags.items():
                if tag not in existing_tags and tag not in domain_tags and tag not in concept_tags:
                    confidence = min(0.5 + (count / 10), 0.85)
                    all_suggestions.append({
                        "tag": tag,
                        "confidence": confidence,
                        "source": "similar_notes"
                    })
            
            # Sort by confidence and take top N
            all_suggestions.sort(key=lambda x: x["confidence"], reverse=True)
            suggested_tags = all_suggestions[:max_suggestions]
            
            return {
                "suggested_tags": suggested_tags,
                "tag_groups": {
                    "domain": domain_tags,
                    "concepts": concept_tags,
                    "similar_notes": list(similar_tags.keys())[:5]
                },
                "reasoning": self._explain_tag_suggestions(
                    suggested_tags,
                    primary_domain
                )
            }
            
        except Exception as e:
            logger.error(f"Error suggesting tags: {e}")
            return {
                "suggested_tags": [],
                "tag_groups": {},
                "reasoning": f"Error during analysis: {str(e)}"
            }
    
    def _get_domain_tags(self, domain) -> List[str]:
        """Get standard tags for a domain."""
        domain_name = domain.name if hasattr(domain, 'name') else str(domain)
        
        domain_tag_map = {
            "Sigils": ["code", "infrastructure", "automation"],
            "Signals": ["audio", "synthesis", "music-tech"],
            "Scrolls": ["writing", "documentation"],
            "Glyphs": ["design", "visual"],
            "Grids": ["systems", "frameworks"]
        }
        
        return domain_tag_map.get(domain_name, [])
    
    def _extract_concept_tags(self, content: str) -> List[str]:
        """
        Extract conceptual tags from content.
        
        Looks for:
        - Capitalized terms (likely concepts)
        - Technical terms
        - Repeated important words
        """
        # This is a simple implementation - could be enhanced with NER
        content_lower = content.lower()
        words = re.findall(r'\b[a-z]{4,}\b', content_lower)
        
        # Count word frequency
        word_freq = {}
        for word in words:
            # Skip common words
            if word in ['that', 'this', 'with', 'from', 'have', 'been', 'were', 'what']:
                continue
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get words that appear multiple times
        concepts = [word for word, count in word_freq.items() if count >= 2]
        
        return concepts[:5]  # Top 5 concepts
    
    def _analyze_tags_from_similar(self, similar_notes: List) -> Dict[str, int]:
        """
        Analyze tags from similar notes and return frequency count.
        """
        tag_freq = {}
        
        for result in similar_notes:
            tags = result.chunk.metadata.get('tags', [])
            for tag in tags:
                if isinstance(tag, str):
                    tag_freq[tag] = tag_freq.get(tag, 0) + 1
        
        return tag_freq
    
    def _explain_tag_suggestions(
        self,
        suggestions: List[Dict],
        primary_domain
    ) -> str:
        """Generate explanation for tag suggestions."""
        if not suggestions:
            return "No tag suggestions available"
        
        domain_name = primary_domain.name if primary_domain and hasattr(primary_domain, 'name') else "Unknown"
        
        sources = set(s["source"] for s in suggestions)
        
        explanation_parts = []
        if "domain" in sources:
            explanation_parts.append(f"based on {domain_name} domain")
        if "content" in sources:
            explanation_parts.append("content analysis")
        if "similar_notes" in sources:
            explanation_parts.append("similar notes")
        
        return f"Suggestions from {', '.join(explanation_parts)}"
    
    async def find_related_notes(
        self,
        note_path: Optional[str] = None,
        content: Optional[str] = None,
        title: Optional[str] = None,
        top_k: int = 5,
        min_similarity: float = 0.01  # Lower threshold for hybrid search scores (range ~0.01-0.08)
    ) -> Dict[str, Any]:
        """
        Find semantically similar notes using RAG.
        
        Args:
            note_path: Path to note (will load content)
            content: Note content (if path not provided)
            title: Note title for context
            top_k: Number of results to return
            min_similarity: Minimum similarity threshold
            
        Returns:
            Dict with related_notes, grouped_by_domain, suggested_links
        """
        try:
            # Get content if path provided
            if note_path and not content:
                note = await self.obsidian.get_note_by_path(note_path)
                if note:
                    content = note.get("content", "")
                    title = title or note.get("title", "")
            
            if not content:
                return {
                    "related_notes": [],
                    "grouped_by_domain": {},
                    "suggested_links": [],
                    "error": "No content provided"
                }
            
            # Query RAG for similar documents
            similar_docs = self.rag.search(
                query=content,
                n_results=top_k * 2,  # Get extras for filtering
                source_types=['obsidian']
            )
            
            # Filter by similarity threshold and deduplicate by filepath
            related_notes = []
            seen_paths = set()
            
            for result in similar_docs:
                similarity = result.score
                doc_path = result.chunk.filepath
                
                # Skip self
                if note_path and doc_path == note_path:
                    continue
                
                # Skip duplicates (same file, different chunks)
                if doc_path in seen_paths:
                    continue
                
                # Check threshold
                if similarity >= min_similarity:
                    seen_paths.add(doc_path)
                    
                    # Analyze connection
                    connection = self._analyze_connection(
                        source_content=content,
                        target_content=result.chunk.content,
                        similarity_score=similarity,
                        target_path=doc_path
                    )
                    
                    related_notes.append({
                        "path": doc_path,
                        "title": result.chunk.metadata.get('title', Path(doc_path).stem),
                        "similarity": round(similarity, 2),
                        "connections": connection
                    })
                
                if len(related_notes) >= top_k:
                    break
            
            # Group by domain
            grouped = self._group_by_domain(related_notes)
            
            # Generate suggested link text
            suggested_links = self._suggest_link_text(content, title, related_notes)
            
            return {
                "related_notes": related_notes,
                "grouped_by_domain": grouped,
                "suggested_links": suggested_links,
                "total_found": len(similar_docs),
                "filtered_by_threshold": len(similar_docs) - len(related_notes)
            }
            
        except Exception as e:
            logger.error(f"Error finding related notes: {e}")
            return {
                "related_notes": [],
                "grouped_by_domain": {},
                "suggested_links": [],
                "error": str(e)
            }
    
    def _analyze_connection(
        self,
        source_content: str,
        target_content: str,
        similarity_score: float,
        target_path: str
    ) -> Dict[str, Any]:
        """
        Analyze the type of connection between two notes.
        """
        # Extract shared concepts (simple word overlap for now)
        source_words = set(re.findall(r'\b[a-z]{4,}\b', source_content.lower()))
        target_words = set(re.findall(r'\b[a-z]{4,}\b', target_content.lower()))
        
        shared_concepts = list(source_words & target_words)[:5]
        
        # Determine connection type
        connection_type = "related_topic"
        if similarity_score > 0.85:
            connection_type = "highly_related"
        elif similarity_score > 0.75:
            connection_type = "directly_related"
        
        # Generate suggested link text
        target_name = Path(target_path).stem
        link_suggestions = [
            f"See also [[{target_name}]]",
            f"Related: [[{target_name}]]",
            f"For more on this, see [[{target_name}]]"
        ]
        
        return {
            "shared_concepts": shared_concepts,
            "connection_type": connection_type,
            "suggested_link_text": link_suggestions[0]
        }
    
    def _group_by_domain(self, notes: List[Dict]) -> Dict[str, int]:
        """Group notes by their domain folder."""
        grouped = {}
        
        for note in notes:
            path = note.get('path', '')
            # Extract domain from path (e.g., "02-Signals/..." -> "02-Signals")
            parts = Path(path).parts
            if parts:
                domain = parts[0]
                grouped[domain] = grouped.get(domain, 0) + 1
        
        return grouped
    
    def _suggest_link_text(
        self,
        content: str,
        title: Optional[str],
        related_notes: List[Dict]
    ) -> List[str]:
        """
        Generate suggested link text for related notes.
        """
        suggestions = []
        
        for note in related_notes[:3]:  # Top 3
            note_title = note.get('title', '')
            connection = note.get('connections', {})
            connection_type = connection.get('connection_type', 'related_topic')
            
            if connection_type == "highly_related":
                suggestions.append(f"This closely relates to [[{note_title}]]")
            elif connection_type == "directly_related":
                suggestions.append(f"See also [[{note_title}]]")
            else:
                suggestions.append(f"Related: [[{note_title}]]")
        
        return suggestions
