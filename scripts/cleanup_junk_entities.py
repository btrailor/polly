#!/usr/bin/env python3
"""
Clean up garbage entities from the entity store.

Removes entities that:
1. Match the expanded GARBAGE_STOPWORDS list (generic programming terms extracted via substring matching)
2. Have names that fail is_valid_entity_name() validation

Also cleans up orphaned mentions and relationships pointing to deleted entities.
"""

import sqlite3
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.entities.extractor import GARBAGE_STOPWORDS, is_valid_entity_name

DB_PATH = Path("~/.polly/entities.db").expanduser()


def cleanup(dry_run: bool = False):
    if not DB_PATH.exists():
        print(f"Database not found: {DB_PATH}")
        return

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Get all entities
    cur.execute("SELECT id, name, entity_type, mention_count FROM entities")
    all_entities = cur.fetchall()

    # Identify entities to delete
    to_delete = []
    for row in all_entities:
        name = row["name"]
        entity_type = row["entity_type"]
        mention_count = row["mention_count"]
        eid = row["id"]

        # Check against expanded stopwords
        if not is_valid_entity_name(name):
            to_delete.append((eid, name, entity_type, mention_count, "failed_validation"))
            continue

    # Sort by mention_count descending for readable output
    to_delete.sort(key=lambda x: x[3], reverse=True)

    print(f"\nTotal entities in DB: {len(all_entities)}")
    print(f"Entities to delete:  {len(to_delete)}")
    print(f"Entities remaining:  {len(all_entities) - len(to_delete)}")
    print()

    if to_delete:
        print("Entities being removed:")
        print(f"{'Name':<25} {'Type':<15} {'Mentions':<10} {'Reason'}")
        print("-" * 70)
        for eid, name, etype, count, reason in to_delete:
            print(f"{name:<25} {etype:<15} {count:<10} {reason}")

    if dry_run:
        print("\n[DRY RUN] No changes made. Run with --execute to apply.")
        conn.close()
        return

    if not to_delete:
        print("Nothing to clean up!")
        conn.close()
        return

    # Delete entities
    delete_ids = [row[0] for row in to_delete]
    placeholders = ",".join("?" * len(delete_ids))

    # Count related records before deletion
    cur.execute(f"SELECT COUNT(*) FROM entity_mentions WHERE entity_id IN ({placeholders})", delete_ids)
    mention_count = cur.fetchone()[0]

    cur.execute(
        f"SELECT COUNT(*) FROM relationships WHERE source_id IN ({placeholders}) OR target_id IN ({placeholders})",
        delete_ids + delete_ids,
    )
    rel_count = cur.fetchone()[0]

    # Delete mentions
    cur.execute(f"DELETE FROM entity_mentions WHERE entity_id IN ({placeholders})", delete_ids)
    print(f"\nDeleted {mention_count} entity mentions")

    # Delete relationships
    cur.execute(
        f"DELETE FROM relationships WHERE source_id IN ({placeholders}) OR target_id IN ({placeholders})",
        delete_ids + delete_ids,
    )
    print(f"Deleted {rel_count} relationships")

    # Delete entities
    cur.execute(f"DELETE FROM entities WHERE id IN ({placeholders})", delete_ids)
    print(f"Deleted {len(delete_ids)} entities")

    # Also clean up any orphaned relationships (both endpoints must exist)
    cur.execute("""
        DELETE FROM relationships
        WHERE source_id NOT IN (SELECT id FROM entities)
           OR target_id NOT IN (SELECT id FROM entities)
    """)
    orphaned_rels = cur.rowcount
    if orphaned_rels:
        print(f"Cleaned up {orphaned_rels} orphaned relationships")

    # Also clean up orphaned mentions
    cur.execute("""
        DELETE FROM entity_mentions
        WHERE entity_id NOT IN (SELECT id FROM entities)
    """)
    orphaned_mentions = cur.rowcount
    if orphaned_mentions:
        print(f"Cleaned up {orphaned_mentions} orphaned mentions")

    conn.commit()

    # Report final state
    cur.execute("SELECT COUNT(*) FROM entities")
    final_entities = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM relationships")
    final_rels = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM entity_mentions")
    final_mentions = cur.fetchone()[0]

    print(f"\nFinal DB state:")
    print(f"  Entities:      {final_entities}")
    print(f"  Relationships: {final_rels}")
    print(f"  Mentions:      {final_mentions}")

    # VACUUM to reclaim space
    conn.execute("VACUUM")
    conn.close()
    print("\nDatabase vacuumed. Cleanup complete!")


if __name__ == "__main__":
    dry = "--execute" not in sys.argv
    if dry:
        print("=== DRY RUN MODE (pass --execute to apply changes) ===")
    else:
        print("=== EXECUTING CLEANUP ===")
    cleanup(dry_run=dry)
