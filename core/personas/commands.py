"""
Persona mode invocation via slash commands.

Maps command strings (e.g. /learning-path, /save) to (persona, mode).
Used by frontend for parsing and autocomplete, and by backend for persona/process.
"""

from typing import Dict, List, Optional, Tuple

# Command definitions: command, persona, mode, description, optional aliases
# Aliases are separate entries that map to the same persona+mode
COMMANDS: List[Dict] = [
    {"command": "teach", "persona": "professor", "mode": "socratic", "description": "Guided learning via dialogue"},
    {"command": "learning-path", "persona": "professor", "mode": "curriculum", "description": "Design a structured curriculum"},
    {"command": "curriculum", "persona": "professor", "mode": "curriculum", "description": "Alias for learning-path"},
    {"command": "explain", "persona": "professor", "mode": "explain", "description": "Clear explanation with examples"},
    {"command": "quiz", "persona": "professor", "mode": "quiz", "description": "Test understanding"},
    {"command": "save", "persona": "scribe", "mode": "capture", "description": "Save conversation as KB note"},
    {"command": "note", "persona": "scribe", "mode": "capture", "description": "Alias for save"},
    {"command": "plan", "persona": "architect", "mode": "plan", "description": "Analyze and create plan"},
    {"command": "build", "persona": "architect", "mode": "build", "description": "Execute plan / generate content"},
]

# Lazy-built: command/alias -> (persona, mode)
_LOOKUP: Optional[Dict[str, Tuple[str, Optional[str]]]] = None


def _build_lookup() -> Dict[str, Tuple[str, Optional[str]]]:
    """Build command and alias -> (persona, mode) map."""
    lookup: Dict[str, Tuple[str, Optional[str]]] = {}
    for c in COMMANDS:
        key = (c["persona"], c.get("mode"))
        lookup[c["command"].lower()] = key
        for alias in c.get("aliases", []):
            lookup[alias.lower()] = key
    return lookup


def get_command(cmd: str) -> Optional[Tuple[str, Optional[str]]]:
    """
    Resolve command string to (persona, mode).
    Returns None if unknown.
    """
    global _LOOKUP
    if _LOOKUP is None:
        _LOOKUP = _build_lookup()
    return _LOOKUP.get(cmd.lower().strip())


def list_commands() -> List[Dict]:
    """
    Return commands for API/autocomplete.
    Includes all commands and aliases so /curriculum and /learning-path both resolve.
    """
    return [
        {
            "command": c["command"],
            "persona": c["persona"],
            "mode": c.get("mode"),
            "description": c["description"],
        }
        for c in COMMANDS
    ]
