"""
Pattern Learning System

Extracts and stores interaction patterns from user behavior, routing decisions,
and task types. Enables adaptive learning for improved routing and personalization.

Patterns are stored in:
1. Local JSON file (~/.polly/patterns.json) - fast lookup, versioned
2. Mem0 (optional) - semantic search, entity relationships

Integration points:
- Router: Learn routing patterns (model preferences, task types)
- Personas: Learn persona-specific patterns (Scribe style, Architect decisions)
- Knowledge Writer: Learn domain/tag patterns
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class Pattern:
    """
    A learned interaction pattern.
    
    Attributes:
        type: Pattern category (routing, preference, task_type, domain, persona)
        description: Human-readable pattern description
        confidence: Pattern confidence (0.0-1.0)
        timestamp: When pattern was learned
        metadata: Additional context (model, domain, tags, etc.)
        occurrences: Number of times pattern observed
    """
    type: str  # "routing", "user_preference", "task_type", "domain", "persona"
    description: str
    confidence: float  # 0.0-1.0
    timestamp: str
    metadata: Dict[str, Any]
    occurrences: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Pattern':
        """Create Pattern from dict."""
        return cls(**data)


class PatternLearner:
    """
    Pattern learning and storage system.
    
    Learns patterns from:
    - Routing decisions (which models for which tasks)
    - User preferences (explicit and implicit)
    - Task classification patterns
    - Domain/tag associations
    - Persona behavior patterns
    
    Example:
        >>> learner = PatternLearner(config)
        >>> pattern = Pattern(
        ...     type="routing",
        ...     description="User prefers Sonnet 4 for code review tasks",
        ...     confidence=0.9,
        ...     timestamp=datetime.now().isoformat(),
        ...     metadata={"model": "claude-sonnet-4", "task": "code_review"}
        ... )
        >>> learner.learn_pattern(pattern)
        >>> results = learner.search_patterns("code review preferences")
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Pattern Learner.
        
        Args:
            config: Configuration dict with memory.provider setting
        """
        self.config = config
        self.patterns_file = Path.home() / ".polly" / "patterns.json"
        
        # Ensure patterns file exists
        self.patterns_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.patterns_file.exists():
            self._save_patterns([])
        
        # Initialize Mem0 if enabled
        self.mem0 = None
        if self._is_mem0_enabled():
            try:
                from core.memory.mem0_adapter import Mem0Adapter
                self.mem0 = Mem0Adapter(config)
                logger.info("PatternLearner: Mem0 adaptive memory enabled")
            except ImportError:
                logger.debug("Mem0 not available (mem0ai package not installed)")
            except Exception as e:
                logger.warning(f"Failed to initialize Mem0 for patterns: {e}")
    
    def _is_mem0_enabled(self) -> bool:
        """Check if Mem0 is enabled in config."""
        if self.config.get('memory', {}).get('provider') != 'mem0':
            return False
        return self.config.get('memory', {}).get('mem0', {}).get('enabled', False)
    
    def _load_patterns(self) -> List[Dict[str, Any]]:
        """Load patterns from JSON file."""
        try:
            with open(self.patterns_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load patterns: {e}")
            return []
    
    def _save_patterns(self, patterns: List[Dict[str, Any]]):
        """Save patterns to JSON file."""
        try:
            with open(self.patterns_file, 'w') as f:
                json.dump(patterns, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save patterns: {e}")
    
    def learn_pattern(self, pattern: Pattern):
        """
        Learn a new pattern or reinforce existing one.
        
        Stores pattern in both JSON (fast lookup) and Mem0 (semantic search).
        If pattern already exists, increments occurrences and updates confidence.
        
        Args:
            pattern: Pattern to learn
        """
        # Load existing patterns
        patterns = self._load_patterns()
        
        # Check for existing similar pattern
        existing_idx = None
        for i, p in enumerate(patterns):
            if (p['type'] == pattern.type and 
                p['description'].lower() == pattern.description.lower()):
                existing_idx = i
                break
        
        if existing_idx is not None:
            # Reinforce existing pattern
            existing = patterns[existing_idx]
            existing['occurrences'] = existing.get('occurrences', 1) + 1
            # Increase confidence (cap at 1.0)
            existing['confidence'] = min(
                existing.get('confidence', 0.5) + 0.1,
                1.0
            )
            existing['timestamp'] = datetime.now().isoformat()
            logger.debug(f"Reinforced pattern: {pattern.description} (occurrences: {existing['occurrences']})")
        else:
            # Add new pattern
            patterns.append(pattern.to_dict())
            logger.info(f"Learned new pattern: {pattern.type} - {pattern.description}")
        
        # Save to JSON
        self._save_patterns(patterns)
        
        # Save to Mem0 (if enabled)
        if self.mem0:
            try:
                self.mem0.add_memory(
                    content=f"Pattern: {pattern.type} - {pattern.description}",
                    user_id="patterns",
                    metadata={
                        'type': 'pattern',
                        'pattern_type': pattern.type,
                        'confidence': pattern.confidence,
                        'timestamp': pattern.timestamp,
                        'occurrences': pattern.occurrences,
                        **pattern.metadata
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to add pattern to Mem0 (non-critical): {e}")
    
    def search_patterns(
        self,
        query: str,
        pattern_type: Optional[str] = None,
        limit: int = 5
    ) -> List[Pattern]:
        """
        Search patterns using semantic search (Mem0) or fallback to JSON.
        
        Args:
            query: Search query
            pattern_type: Optional filter by pattern type
            limit: Maximum number of results
            
        Returns:
            List of matching Pattern objects, sorted by relevance/confidence
        """
        if self.mem0:
            # Use Mem0 semantic search
            try:
                results = self.mem0.search_memory(
                    query=query,
                    user_id="patterns",
                    limit=limit
                )
                
                # Convert Mem0 results to Pattern objects
                patterns = []
                for r in results:
                    metadata = r.get('metadata', {})
                    
                    # Filter by type if specified
                    if pattern_type and metadata.get('pattern_type') != pattern_type:
                        continue
                    
                    pattern = Pattern(
                        type=metadata.get('pattern_type', 'unknown'),
                        description=r.get('memory', '').replace('Pattern: ', '').split(' - ', 1)[-1],
                        confidence=metadata.get('confidence', 0.5),
                        timestamp=metadata.get('timestamp', ''),
                        metadata={k: v for k, v in metadata.items() 
                                 if k not in ['type', 'pattern_type', 'confidence', 'timestamp', 'occurrences']},
                        occurrences=metadata.get('occurrences', 1)
                    )
                    patterns.append(pattern)
                
                return patterns
                
            except Exception as e:
                logger.warning(f"Mem0 search failed, falling back to JSON: {e}")
        
        # Fallback: keyword search in JSON
        patterns = self._load_patterns()
        query_lower = query.lower()
        
        results = []
        for p_dict in patterns:
            # Filter by type if specified
            if pattern_type and p_dict.get('type') != pattern_type:
                continue
            
            # Simple keyword matching
            description_lower = p_dict.get('description', '').lower()
            if query_lower in description_lower or any(
                word in description_lower for word in query_lower.split()
            ):
                results.append(Pattern.from_dict(p_dict))
        
        # Sort by confidence and occurrences
        results.sort(
            key=lambda p: (p.confidence, p.occurrences),
            reverse=True
        )
        
        return results[:limit]
    
    def get_patterns_by_type(self, pattern_type: str) -> List[Pattern]:
        """
        Get all patterns of a specific type.
        
        Args:
            pattern_type: Pattern type to filter by
            
        Returns:
            List of Pattern objects
        """
        patterns = self._load_patterns()
        results = [
            Pattern.from_dict(p)
            for p in patterns
            if p.get('type') == pattern_type
        ]
        
        # Sort by confidence and occurrences
        results.sort(
            key=lambda p: (p.confidence, p.occurrences),
            reverse=True
        )
        
        return results
    
    def get_all_patterns(self) -> List[Pattern]:
        """Get all learned patterns."""
        patterns = self._load_patterns()
        return [Pattern.from_dict(p) for p in patterns]
    
    def get_pattern_stats(self) -> Dict[str, Any]:
        """
        Get statistics about learned patterns.
        
        Returns:
            Dict with total count, counts by type, confidence distribution
        """
        patterns = self._load_patterns()
        
        stats = {
            'total': len(patterns),
            'by_type': {},
            'avg_confidence': 0.0,
            'high_confidence': 0,  # confidence >= 0.8
            'medium_confidence': 0,  # 0.5 <= confidence < 0.8
            'low_confidence': 0,  # confidence < 0.5
        }
        
        if not patterns:
            return stats
        
        # Count by type
        for p in patterns:
            p_type = p.get('type', 'unknown')
            stats['by_type'][p_type] = stats['by_type'].get(p_type, 0) + 1
        
        # Confidence distribution
        confidences = [p.get('confidence', 0.5) for p in patterns]
        stats['avg_confidence'] = sum(confidences) / len(confidences)
        stats['high_confidence'] = sum(1 for c in confidences if c >= 0.8)
        stats['medium_confidence'] = sum(1 for c in confidences if 0.5 <= c < 0.8)
        stats['low_confidence'] = sum(1 for c in confidences if c < 0.5)
        
        return stats
    
    def delete_pattern(self, pattern_description: str) -> bool:
        """
        Delete a pattern by description.
        
        Args:
            pattern_description: Description of pattern to delete
            
        Returns:
            True if deleted, False if not found
        """
        patterns = self._load_patterns()
        original_count = len(patterns)
        
        # Filter out matching pattern
        patterns = [
            p for p in patterns
            if p.get('description', '').lower() != pattern_description.lower()
        ]
        
        if len(patterns) < original_count:
            self._save_patterns(patterns)
            logger.info(f"Deleted pattern: {pattern_description}")
            return True
        
        return False
    
    def clear_patterns(self, pattern_type: Optional[str] = None):
        """
        Clear all patterns or patterns of a specific type.
        
        Args:
            pattern_type: Optional type to filter by. If None, clears all.
        """
        if pattern_type:
            patterns = self._load_patterns()
            patterns = [p for p in patterns if p.get('type') != pattern_type]
            self._save_patterns(patterns)
            logger.info(f"Cleared patterns of type: {pattern_type}")
        else:
            self._save_patterns([])
            logger.info("Cleared all patterns")


# Singleton instance
_pattern_learner = None


def get_pattern_learner(config: Optional[Dict[str, Any]] = None) -> PatternLearner:
    """
    Get singleton PatternLearner instance.
    
    Args:
        config: Configuration dict (required on first call)
        
    Returns:
        PatternLearner instance
    """
    global _pattern_learner
    
    if _pattern_learner is None:
        if config is None:
            raise ValueError("Config required for first PatternLearner initialization")
        _pattern_learner = PatternLearner(config)
    
    return _pattern_learner
