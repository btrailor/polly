"""
Migration from old pattern formats to unified PatternEngine format.

Handles:
- learners/patterns.py v2.0 JSON format → unified Pattern model
- core/pattern_learning.py patterns (if any in JSON) → unified Pattern model
- Backup of old files before migration
"""

from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .models import (
    DomainPriorityPattern,
    Pattern,
    PatternType,
    QueryChunkPattern,
    generate_pattern_id,
)
from .engine import PatternEngine

logger = logging.getLogger(__name__)


# Mapping from old pattern_type strings to PatternType enum
_TYPE_MAP = {
    "code": PatternType.CODE,
    "concept": PatternType.CONCEPTUAL,
    "conceptual": PatternType.CONCEPTUAL,
    "workflow": PatternType.WORKFLOW,
    "cross_domain": PatternType.CONCEPTUAL,
    "query": PatternType.QUERY,
    "routing": PatternType.ROUTING,
    "user_preference": PatternType.USER_PREFERENCE,
    "task_type": PatternType.TASK_TYPE,
    "domain": PatternType.DOMAIN,
    "persona": PatternType.PERSONA,
}


def migrate_from_v2(old_json_path: Path, engine: PatternEngine) -> Dict[str, int]:
    """
    Migrate patterns from learners/patterns.py v2.0 JSON format.

    Args:
        old_json_path: Path to old patterns.json (v2.0 format from learners/patterns.py)
        engine: Initialized PatternEngine to receive migrated patterns

    Returns:
        Dict with migration stats
    """
    stats = {
        "patterns_migrated": 0,
        "query_chunk_migrated": 0,
        "domain_priority_migrated": 0,
        "skipped": 0,
        "errors": 0,
    }

    old_path = Path(old_json_path).expanduser()
    if not old_path.exists():
        logger.info(f"No old patterns file at {old_path} — nothing to migrate")
        return stats

    # Create backup
    backup_path = old_path.with_suffix(".json.v2_backup")
    if not backup_path.exists():
        shutil.copy2(old_path, backup_path)
        logger.info(f"Created backup at {backup_path}")

    try:
        raw = json.loads(old_path.read_text())
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Failed to read old patterns file: {e}")
        stats["errors"] += 1
        return stats

    # Check if already in v3 format (already migrated)
    version = raw.get("metadata", {}).get("version", "1.0")
    if version == "3.0":
        logger.info("Patterns file is already in v3.0 format — no migration needed")
        return stats

    # Migrate legacy patterns
    for p_data in raw.get("patterns", []):
        try:
            pt_str = p_data.get("pattern_type", "query")
            pattern_type = _TYPE_MAP.get(pt_str, PatternType.QUERY)

            # Parse datetimes
            first_seen = datetime.now()
            last_seen = datetime.now()
            try:
                first_seen = datetime.fromisoformat(p_data["first_seen"])
            except (KeyError, ValueError):
                pass
            try:
                last_seen = datetime.fromisoformat(p_data["last_seen"])
            except (KeyError, ValueError):
                pass

            pattern = Pattern(
                id=p_data.get("id", generate_pattern_id(pt_str, p_data.get("name", ""))),
                pattern_type=pattern_type,
                name=p_data.get("name", ""),
                description=p_data.get("description", ""),
                confidence=p_data.get("confidence", 0.5),
                occurrences=p_data.get("occurrences", 1),
                first_seen=first_seen,
                last_seen=last_seen,
                domains=p_data.get("domains", []),
                keywords=[],
                examples=p_data.get("examples", []),
                metadata=p_data.get("metadata", {}),
                times_used=p_data.get("times_used", 0),
                times_helpful=p_data.get("times_helpful", 0),
                source="migration",
            )
            engine.json_backend.save(pattern)
            stats["patterns_migrated"] += 1

        except Exception as e:
            logger.warning(f"Failed to migrate pattern: {e}")
            stats["errors"] += 1

    # Migrate query_chunk_patterns
    for qcp_data in raw.get("query_chunk_patterns", []):
        try:
            qcp = QueryChunkPattern.from_dict(qcp_data)
            engine.json_backend.save_query_chunk_pattern(qcp)
            stats["query_chunk_migrated"] += 1
        except Exception as e:
            logger.warning(f"Failed to migrate query_chunk_pattern: {e}")
            stats["errors"] += 1

    # Migrate domain_priority_patterns
    for dpp_data in raw.get("domain_priority_patterns", []):
        try:
            dpp = DomainPriorityPattern.from_dict(dpp_data)
            engine.json_backend.save_domain_priority_pattern(dpp)
            stats["domain_priority_migrated"] += 1
        except Exception as e:
            logger.warning(f"Failed to migrate domain_priority_pattern: {e}")
            stats["errors"] += 1

    # Migrate query history
    for entry in raw.get("query_history", []):
        engine.json_backend.append_query_history(entry)

    # Save migrated data
    engine.json_backend.flush()

    logger.info(
        f"Migration complete: {stats['patterns_migrated']} patterns, "
        f"{stats['query_chunk_migrated']} query→chunk, "
        f"{stats['domain_priority_migrated']} domain priority, "
        f"{stats['errors']} errors"
    )

    return stats
