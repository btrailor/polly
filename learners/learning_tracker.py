"""
Learning Path Tracker (Phase 22 - Teaching Mode)

Tracks what the user has learned and suggests next topics.
Implements spaced repetition for review scheduling.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class LearningTopic:
    """A topic the user is learning."""
    id: str
    title: str
    domain: str
    concepts: List[str]  # Sub-concepts covered
    mastery_level: int  # 1-5 (1=introduced, 3=understood, 5=mastered)
    first_learned: datetime
    last_reviewed: datetime
    notes_created: List[str] = field(default_factory=list)  # File paths
    related_topics: List[str] = field(default_factory=list)  # Topic IDs


class LearningTracker:
    """Tracks learning progress and suggests next topics."""
    
    def __init__(self, storage_path: Path):
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.topics: Dict[str, LearningTopic] = {}
        self._load_topics()
    
    def record_learning(
        self,
        title: str,
        domain: str,
        concepts: List[str],
        mastery_level: int = 1,
        note_path: Optional[str] = None
    ):
        """
        Record that user learned a topic.
        
        Args:
            title: Topic title (e.g., "Async/Await in Python")
            domain: Domain ID (sigils, signals, etc.)
            concepts: List of concepts covered
            mastery_level: 1-5 scale (1=introduced, 5=mastered)
            note_path: Path to learning note (if created)
        """
        topic_id = self._make_id(title)
        
        now = datetime.now()
        
        if topic_id in self.topics:
            # Update existing
            topic = self.topics[topic_id]
            topic.concepts.extend(c for c in concepts if c not in topic.concepts)
            topic.mastery_level = max(topic.mastery_level, mastery_level)
            topic.last_reviewed = now
            if note_path and note_path not in topic.notes_created:
                topic.notes_created.append(note_path)
        else:
            # Create new
            topic = LearningTopic(
                id=topic_id,
                title=title,
                domain=domain,
                concepts=concepts,
                mastery_level=mastery_level,
                first_learned=now,
                last_reviewed=now,
                notes_created=[note_path] if note_path else []
            )
            self.topics[topic_id] = topic
        
        self._save_topics()
        logger.info(f"Recorded learning: {title} (mastery: {mastery_level}/5)")
    
    def get_topic(self, title: str) -> Optional[LearningTopic]:
        """Get topic by title."""
        topic_id = self._make_id(title)
        return self.topics.get(topic_id)
    
    def get_next_topics(self, current_topic: str, count: int = 3) -> List[str]:
        """
        Suggest next topics to learn based on current topic.
        
        Args:
            current_topic: Current topic title
            count: Number of suggestions
        
        Returns:
            List of suggested topic titles
        """
        current = self.topics.get(self._make_id(current_topic))
        if not current:
            return []
        
        suggestions = []
        
        # Strategy 1: Related topics with lower mastery
        for related_id in current.related_topics:
            if related_id in self.topics:
                related = self.topics[related_id]
                if related.mastery_level < current.mastery_level:
                    suggestions.append(related.title)
        
        # Strategy 2: Same domain, higher difficulty
        for topic in self.topics.values():
            if (topic.domain == current.domain and 
                topic.mastery_level <= current.mastery_level + 1 and
                topic.id != current.id):
                if topic.title not in suggestions:
                    suggestions.append(topic.title)
        
        return suggestions[:count]
    
    def get_topics_for_review(self, days_since_last_review: int = 7) -> List[LearningTopic]:
        """
        Get topics that should be reviewed (spaced repetition).
        
        Args:
            days_since_last_review: Number of days since last review
        
        Returns:
            List of topics needing review, sorted by last review date
        """
        now = datetime.now()
        review_topics = []
        
        for topic in self.topics.values():
            days_since = (now - topic.last_reviewed).days
            
            # Spaced repetition intervals based on mastery
            review_interval = {
                1: 1,   # Introduced: review after 1 day
                2: 3,   # Learning: review after 3 days
                3: 7,   # Understood: review after 1 week
                4: 14,  # Proficient: review after 2 weeks
                5: 30   # Mastered: review after 1 month
            }.get(topic.mastery_level, 7)
            
            if days_since >= review_interval:
                review_topics.append(topic)
        
        # Sort by last reviewed (oldest first)
        return sorted(review_topics, key=lambda t: t.last_reviewed)
    
    def get_learning_stats(self) -> Dict:
        """Get overall learning statistics."""
        total_topics = len(self.topics)
        by_domain = {}
        by_mastery = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        for topic in self.topics.values():
            # Count by domain
            by_domain[topic.domain] = by_domain.get(topic.domain, 0) + 1
            
            # Count by mastery level
            by_mastery[topic.mastery_level] += 1
        
        return {
            "total_topics": total_topics,
            "by_domain": by_domain,
            "by_mastery": by_mastery,
            "topics_needing_review": len(self.get_topics_for_review())
        }
    
    def _make_id(self, title: str) -> str:
        """Create ID from title."""
        return title.lower().replace(' ', '_').replace('/', '_')
    
    def _load_topics(self):
        """Load learning topics from storage."""
        if not self.storage_path.exists():
            logger.info("No existing learning data, starting fresh")
            return
        
        try:
            data = json.loads(self.storage_path.read_text())
            for topic_data in data.get('topics', []):
                topic = LearningTopic(
                    id=topic_data['id'],
                    title=topic_data['title'],
                    domain=topic_data['domain'],
                    concepts=topic_data['concepts'],
                    mastery_level=topic_data['mastery_level'],
                    first_learned=datetime.fromisoformat(topic_data['first_learned']),
                    last_reviewed=datetime.fromisoformat(topic_data['last_reviewed']),
                    notes_created=topic_data.get('notes_created', []),
                    related_topics=topic_data.get('related_topics', [])
                )
                self.topics[topic.id] = topic
            
            logger.info(f"Loaded {len(self.topics)} learning topics")
        except Exception as e:
            logger.error(f"Failed to load learning topics: {e}")
            self.topics = {}
    
    def _save_topics(self):
        """Save learning topics to storage."""
        data = {
            'topics': [
                {
                    'id': t.id,
                    'title': t.title,
                    'domain': t.domain,
                    'concepts': t.concepts,
                    'mastery_level': t.mastery_level,
                    'first_learned': t.first_learned.isoformat(),
                    'last_reviewed': t.last_reviewed.isoformat(),
                    'notes_created': t.notes_created,
                    'related_topics': t.related_topics
                }
                for t in self.topics.values()
            ],
            'version': '1.0',
            'last_updated': datetime.now().isoformat()
        }
        
        self.storage_path.write_text(json.dumps(data, indent=2))
        logger.info(f"Saved {len(self.topics)} learning topics")
