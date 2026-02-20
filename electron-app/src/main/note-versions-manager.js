'use strict';

const crypto = require('crypto');

/**
 * NoteVersionsManager — per-note version history stored in SQLite.
 *
 * Schema is created/migrated inside the shared ConversationManager
 * database. This class is given the already-open `better-sqlite3`
 * database instance at construction time so it doesn't open a second
 * connection.
 *
 * Storage policy
 * ─────────────────────────────────────────
 * • Max 10 versions per note path.
 * • Duplicate content (same SHA-256 hash as the latest version) is skipped.
 * • Versions older than 30 days are pruned on startup.
 */
class NoteVersionsManager {
  /**
   * @param {import('better-sqlite3').Database} db - already-open SQLite connection
   */
  constructor(db) {
    this.db = db;
    this._initSchema();
    this._cleanup();
  }

  // ── Schema ──────────────────────────────────────────────────────────────────

  _initSchema() {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS note_versions (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        note_path   TEXT    NOT NULL,
        content     TEXT    NOT NULL,
        saved_at    TEXT    NOT NULL DEFAULT (datetime('now')),
        source      TEXT    NOT NULL DEFAULT 'auto-save',
        content_hash TEXT   NOT NULL
      );

      CREATE INDEX IF NOT EXISTS idx_note_versions_path
        ON note_versions (note_path, saved_at DESC);
    `);
  }

  // ── Public API ───────────────────────────────────────────────────────────────

  /**
   * Save a new version, skipping if content hash matches the latest.
   * Prunes to the most-recent 10 versions after inserting.
   *
   * @param {string} notePath  - absolute or vault-relative path used as the key
   * @param {string} content   - full note text
   * @param {string} [source]  - 'auto-save' | 'manual-save' | 'revert'
   * @returns {{ saved: boolean, id: number|null }}
   */
  save(notePath, content, source = 'auto-save') {
    const hash = this._hash(content);

    // Skip duplicate saves
    const latest = this.db
      .prepare(`SELECT content_hash FROM note_versions
                WHERE note_path = ? ORDER BY saved_at DESC LIMIT 1`)
      .get(notePath);

    if (latest && latest.content_hash === hash) {
      return { saved: false, id: null };
    }

    const info = this.db
      .prepare(`INSERT INTO note_versions (note_path, content, source, content_hash)
                VALUES (?, ?, ?, ?)`)
      .run(notePath, content, source, hash);

    // Prune: keep only the 10 most-recent
    this.db.prepare(`
      DELETE FROM note_versions
      WHERE note_path = ?
        AND id NOT IN (
          SELECT id FROM note_versions
          WHERE note_path = ?
          ORDER BY saved_at DESC
          LIMIT 10
        )
    `).run(notePath, notePath);

    return { saved: true, id: info.lastInsertRowid };
  }

  /**
   * List the last 10 versions for a note (metadata only, no content).
   *
   * @param {string} notePath
   * @returns {Array<{id, note_path, saved_at, source, preview}>}
   */
  list(notePath) {
    const rows = this.db
      .prepare(`SELECT id, note_path, saved_at, source, content
                FROM note_versions
                WHERE note_path = ?
                ORDER BY saved_at DESC
                LIMIT 10`)
      .all(notePath);

    return rows.map(({ content, ...meta }) => ({
      ...meta,
      preview: content ? content.slice(0, 100) : '',
    }));
  }

  /**
   * Get full content for a specific version.
   *
   * @param {number} versionId
   * @returns {{ id, note_path, content, saved_at, source } | null}
   */
  get(versionId) {
    return this.db
      .prepare(`SELECT id, note_path, content, saved_at, source
                FROM note_versions WHERE id = ?`)
      .get(versionId) ?? null;
  }

  /**
   * Revert a note to a previous version.
   * Records the revert as a new version entry so it can itself be undone.
   *
   * @param {string} notePath   - must match the stored note_path
   * @param {number} versionId
   * @returns {{ content: string } | { error: string }}
   */
  revert(notePath, versionId) {
    const version = this.get(versionId);

    if (!version) {
      return { error: `Version ${versionId} not found` };
    }
    if (version.note_path !== notePath) {
      return { error: 'Version path mismatch' };
    }

    // Save a "revert" entry so history is linear
    this.save(notePath, version.content, 'revert');

    return { content: version.content };
  }

  // ── Private helpers ──────────────────────────────────────────────────────────

  /** SHA-256 hex digest of content string */
  _hash(content) {
    return crypto.createHash('sha256').update(content ?? '').digest('hex');
  }

  /** Delete versions older than 30 days (called once on startup) */
  _cleanup() {
    this.db
      .prepare(`DELETE FROM note_versions
                WHERE saved_at < datetime('now', '-30 days')`)
      .run();
  }
}

module.exports = NoteVersionsManager;
