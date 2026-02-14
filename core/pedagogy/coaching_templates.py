"""
Persona Introduction Messages and Coaching Templates (Wave 1, Task 2)

One-time introduction messages delivered when a user first activates each persona.
These messages provide a brief, natural orientation without overwhelming the user.

Design Principle: Banking model → Problem-posing education
- Introductions are invitations to dialogue, not instructions to follow
- Each persona introduces themselves through their lens and approach
- Messages are concise (2-3 sentences) and action-oriented

⚠️ IMPORTANT FOR DEVELOPERS:
When you create a NEW PERSONA, you MUST add an introduction message here!
This is a required part of the persona system. See:
- docs/PERSONA_SYSTEM_ARCHITECTURE.md → "Developer Guide: Adding New Personas"
- core/personas/NEW_PERSONA_CHECKLIST.md
- openspec/changes/learning-and-administrator-profiles/tasks.md (Task 2)

Introduction Format:
1. Greeting + persona name + primary function (1 sentence)
2. Approach or distinguishing characteristic (1 sentence)  
3. Open-ended question to invite dialogue (1 sentence)

Example:
"Hello! I'm Professor, and I'm here to help you learn through Socratic dialogue. 
Instead of just explaining things, I'll ask questions that help you discover 
insights yourself. What would you like to explore today?"
"""

from typing import Dict

# Persona Introduction Messages
# Delivered once per persona on first activation
# NOTE: Only include personas that are actually implemented in PERSONA_REGISTRY
PERSONA_INTRODUCTIONS: Dict[str, str] = {
    "professor": (
        "Hello! I'm Professor, and I'm here to help you learn through Socratic dialogue. "
        "Instead of just explaining things, I'll ask questions that help you discover "
        "insights yourself. What would you like to explore today?"
    ),
    "architect": (
        "Greetings! I'm Architect, and I help you design systems and plan technical solutions. "
        "I think in terms of structure, patterns, and tradeoffs. "
        "What are you designing or planning?"
    ),
    "scribe": (
        "Hello! I'm Scribe, and I help you capture and organize knowledge from our conversations. "
        "I create structured notes, learning records, and documentation. "
        "What would you like me to record?"
    ),
    
    # Future personas (add when implemented):
    # "programmer": "Hey there! I'm Programmer...",
    # "librarian": "Welcome! I'm Librarian...",
    # "administrator": "Hello! I'm Administrator...",
}


def get_persona_introduction(persona_name: str) -> str:
    """
    Get the introduction message for a given persona.
    
    Args:
        persona_name: Name of the persona (e.g., "professor", "programmer")
    
    Returns:
        Introduction message string, or empty string if persona not found
    """
    return PERSONA_INTRODUCTIONS.get(persona_name.lower(), "")


def should_deliver_introduction(persona_name: str, user_journey: dict) -> bool:
    """
    Check if persona introduction should be delivered.
    
    Args:
        persona_name: Name of the persona
        user_journey: User journey state dict with 'features_revealed' list
    
    Returns:
        True if introduction should be delivered, False otherwise
    """
    feature_key = f"persona_intro_{persona_name.lower()}"
    features_revealed = user_journey.get("features_revealed", [])
    return feature_key not in features_revealed


def mark_introduction_delivered(persona_name: str, user_journey: dict) -> dict:
    """
    Mark persona introduction as delivered in user journey.
    
    Args:
        persona_name: Name of the persona
        user_journey: User journey state dict
    
    Returns:
        Updated user journey dict
    """
    feature_key = f"persona_intro_{persona_name.lower()}"
    
    if "features_revealed" not in user_journey:
        user_journey["features_revealed"] = []
    
    if feature_key not in user_journey["features_revealed"]:
        user_journey["features_revealed"].append(feature_key)
    
    return user_journey


# Future: Wave 2 Coaching Templates
# These will be used by the Prompt Injector System to provide adaptive coaching
# based on user competency level and prompting patterns

COACHING_TEMPLATES = {
    # Placeholder for Wave 2
    # Will contain templates for:
    # - vague_request_coaching
    # - missing_context_coaching
    # - depth_unspecified_coaching
    # - wrong_persona_coaching
}
