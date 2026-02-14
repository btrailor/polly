"""
User Journey Tracker (Wave 1, Task 2)

Tracks user progression through Polly's features to enable adaptive onboarding
and feature revelation. This supports the progressive disclosure principle.
"""

from pathlib import Path
from typing import Dict, List, Optional
import json
import logging

logger = logging.getLogger(__name__)


class UserJourneyTracker:
    """Tracks user journey and feature revelation state."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize user journey tracker.
        
        Args:
            storage_path: Path to store user journey data.
                         Defaults to ~/.local/share/polly/user-journey.json
        """
        if storage_path is None:
            storage_path = Path.home() / ".local" / "share" / "polly" / "user-journey.json"
        
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.journey_data: Dict = self._load()
    
    def _load(self) -> Dict:
        """Load journey data from disk."""
        if not self.storage_path.exists():
            return {
                "features_revealed": [],
                "first_seen": {},
                "interaction_counts": {},
            }
        
        try:
            with open(self.storage_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load user journey data: {e}")
            return {
                "features_revealed": [],
                "first_seen": {},
                "interaction_counts": {},
            }
    
    def _save(self):
        """Save journey data to disk."""
        try:
            with open(self.storage_path, "w") as f:
                json.dump(self.journey_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save user journey data: {e}")
    
    def is_feature_revealed(self, feature_key: str) -> bool:
        """
        Check if a feature has been revealed to the user.
        
        Args:
            feature_key: Unique feature identifier (e.g., "persona_intro_professor")
        
        Returns:
            True if feature has been revealed, False otherwise
        """
        return feature_key in self.journey_data.get("features_revealed", [])
    
    def mark_feature_revealed(self, feature_key: str):
        """
        Mark a feature as revealed.
        
        Args:
            feature_key: Unique feature identifier
        """
        if "features_revealed" not in self.journey_data:
            self.journey_data["features_revealed"] = []
        
        if feature_key not in self.journey_data["features_revealed"]:
            self.journey_data["features_revealed"].append(feature_key)
            
            # Track first seen time
            if "first_seen" not in self.journey_data:
                self.journey_data["first_seen"] = {}
            
            from datetime import datetime
            self.journey_data["first_seen"][feature_key] = datetime.now().isoformat()
            
            self._save()
            logger.info(f"Feature revealed: {feature_key}")
    
    def increment_interaction(self, interaction_key: str):
        """
        Increment interaction count for a feature/action.
        
        Args:
            interaction_key: Unique interaction identifier (e.g., "persona_professor_activated")
        """
        if "interaction_counts" not in self.journey_data:
            self.journey_data["interaction_counts"] = {}
        
        current = self.journey_data["interaction_counts"].get(interaction_key, 0)
        self.journey_data["interaction_counts"][interaction_key] = current + 1
        
        self._save()
    
    def get_interaction_count(self, interaction_key: str) -> int:
        """
        Get interaction count for a feature/action.
        
        Args:
            interaction_key: Unique interaction identifier
        
        Returns:
            Number of times interaction has occurred
        """
        return self.journey_data.get("interaction_counts", {}).get(interaction_key, 0)
    
    def get_all_revealed_features(self) -> List[str]:
        """Get list of all revealed features."""
        return self.journey_data.get("features_revealed", [])
    
    def reset(self):
        """Reset journey tracking (for testing/development)."""
        self.journey_data = {
            "features_revealed": [],
            "first_seen": {},
            "interaction_counts": {},
        }
        self._save()
        logger.info("User journey data reset")


# Global singleton instance
_tracker_instance: Optional[UserJourneyTracker] = None


def get_journey_tracker() -> UserJourneyTracker:
    """Get or create the global user journey tracker instance."""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = UserJourneyTracker()
    return _tracker_instance
