"""
Database Initialization
Hardened Knowledge Infrastructure — Wave 4

Manages the hardened.db SQLite database with WAL mode and foreign keys.
Provides connection management and initialization for the hardened
infrastructure layer.

Design:
- Separate database (~/.polly/hardened.db) from existing Polly DBs
- WAL mode for safe concurrent reads
- Foreign keys enabled
- Lazy initialization — doesn't create DB until first use
- MigrationManager handles schema evolution
"""

from pathlib import Path
from typing import Optional
import sqlite3
import logging

logger = logging.getLogger(__name__)

# Default database path
DEFAULT_DB_PATH = Path.home() / ".polly" / "hardened.db"


def get_db_path() -> Path:
    """Get the hardened database path."""
    return DEFAULT_DB_PATH


def get_connection(
    db_path: Optional[Path] = None,
    wal_mode: bool = True,
) -> sqlite3.Connection:
    """
    Get a connection to hardened.db with recommended settings.

    Args:
        db_path: Override database path
        wal_mode: Enable WAL mode (recommended for concurrent access)

    Returns:
        sqlite3.Connection with WAL mode and foreign keys enabled
    """
    path = db_path or DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(path)

    if wal_mode:
        conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    return conn


def initialize_database(db_path: Optional[Path] = None) -> Path:
    """
    Initialize the hardened database with migrations.

    This is the entry point for database setup. Called during Polly
    initialization to ensure the schema is up to date.

    Args:
        db_path: Override database path

    Returns:
        Path to the initialized database
    """
    from core.hardened.migration import MigrationManager

    path = db_path or DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    # Apply migrations
    migrator = MigrationManager(db_path=path)
    migrator.apply_migrations()

    # Set recommended pragmas
    conn = get_connection(path)
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.close()
    except Exception as e:
        logger.warning(f"Failed to set database pragmas: {e}")
        conn.close()

    logger.info(f"Hardened database initialized: {path}")
    return path
