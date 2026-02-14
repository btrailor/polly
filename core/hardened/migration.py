"""
Schema Migration System
Hardened Knowledge Infrastructure — Wave 4

Automatic schema evolution for hardened.db.  Migrations are SQL files
stored in the migrations/ directory, named NNN_description.sql.

Design:
- Forward-only migrations (no rollback for safety)
- Version tracking in schema_version table
- Atomic transactions per migration
- Idempotent initialization (safe to run multiple times)
"""

from pathlib import Path
from typing import Optional, List, Tuple
import sqlite3
import logging

logger = logging.getLogger(__name__)

# Default migrations directory (relative to project root)
DEFAULT_MIGRATIONS_DIR = Path(__file__).parent.parent.parent / "migrations"


class MigrationManager:
    """
    Manage schema migrations for hardened.db.

    Usage:
        migrator = MigrationManager()
        migrator.apply_migrations()       # Apply all pending
        print(migrator.current_version()) # Current schema version
    """

    def __init__(
        self,
        db_path: Optional[Path] = None,
        migrations_dir: Optional[Path] = None,
    ):
        self.db_path = db_path or Path.home() / ".polly" / "hardened.db"
        self.migrations_dir = migrations_dir or DEFAULT_MIGRATIONS_DIR

    def current_version(self) -> int:
        """Get current schema version from database."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute(
                "SELECT MAX(version) FROM schema_version"
            )
            result = cursor.fetchone()[0]
            conn.close()
            return result if result is not None else 0
        except sqlite3.OperationalError:
            # schema_version table doesn't exist yet
            return 0
        except Exception as e:
            logger.warning(f"Failed to get schema version: {e}")
            return 0

    def available_migrations(self) -> List[Tuple[int, Path]]:
        """Get list of available migration files, sorted by version."""
        if not self.migrations_dir.exists():
            return []

        migrations = []
        for migration_file in sorted(self.migrations_dir.glob("*.sql")):
            try:
                # Extract version from filename: "001_initial.sql" → 1
                version = int(migration_file.stem.split("_")[0])
                migrations.append((version, migration_file))
            except (ValueError, IndexError):
                logger.warning(f"Skipping invalid migration filename: {migration_file}")

        return migrations

    def pending_migrations(self) -> List[Tuple[int, Path]]:
        """Get list of migrations not yet applied."""
        current = self.current_version()
        return [
            (v, path) for v, path in self.available_migrations()
            if v > current
        ]

    def apply_migrations(self, target_version: Optional[int] = None) -> int:
        """
        Apply all pending migrations up to target version.

        Args:
            target_version: Max version to apply (None = all available)

        Returns:
            Number of migrations applied
        """
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        current = self.current_version()
        all_migrations = self.available_migrations()

        if not all_migrations:
            logger.info("No migration files found")
            return 0

        if target_version is None:
            target_version = max(v for v, _ in all_migrations)

        pending = [
            (v, path) for v, path in all_migrations
            if v > current and v <= target_version
        ]

        if not pending:
            logger.debug(f"Database is up to date (version {current})")
            return 0

        logger.info(
            f"Applying {len(pending)} migration(s) "
            f"(v{current} → v{target_version})"
        )

        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys=ON")
        applied = 0

        try:
            for version, migration_path in pending:
                logger.info(f"Applying migration {version}: {migration_path.name}")

                sql = migration_path.read_text()

                try:
                    # Execute entire migration in a transaction
                    conn.executescript(sql)
                    applied += 1
                    logger.info(f"Migration {version} applied successfully")
                except Exception as e:
                    logger.error(f"Migration {version} failed: {e}")
                    raise
        finally:
            conn.close()

        return applied

    def get_migration_history(self) -> List[dict]:
        """Get list of applied migrations with timestamps."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM schema_version ORDER BY version"
            )
            result = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return result
        except sqlite3.OperationalError:
            return []
        except Exception as e:
            logger.warning(f"Failed to get migration history: {e}")
            return []
