const Database = require("better-sqlite3");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

/**
 * Generate a UUID v4
 */
function uuidv4() {
  return crypto.randomUUID();
}

/**
 * ConversationManager - Manages conversations using SQLite database
 *
 * Features:
 * - Create, read, update, delete conversations
 * - Message storage with full history
 * - Category management (domains + custom)
 * - Star protection (prevents auto-deletion)
 * - Auto-cleanup (60-day retention for non-starred)
 * - Conversation limit enforcement (max 500)
 * - LLM-based auto-titling
 * - Migration from old single-conversation format
 */
class ConversationManager {
  constructor(dbPath) {
    this.dbPath = dbPath;
    this.db = null;
    this.maxConversations = 500;
    this.retentionDays = 60;
    this.autoTitleThreshold = 3; // Messages needed before auto-title

    this.initialize();
  }

  /**
   * Initialize database and load schema
   */
  initialize() {
    try {
      // Ensure directory exists
      const dir = path.dirname(this.dbPath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }

      // Open database
      this.db = new Database(this.dbPath);
      this.db.pragma("journal_mode = WAL");
      this.db.pragma("foreign_keys = ON");

      // Run migrations FIRST (for existing databases)
      this.runMigrations();

      // Load and execute schema (will skip existing tables)
      const schemaPath = path.join(__dirname, "db", "schema.sql");
      const schema = fs.readFileSync(schemaPath, "utf8");
      this.db.exec(schema);

      console.log("ConversationManager initialized successfully");
    } catch (error) {
      console.error("Failed to initialize ConversationManager:", error);
      throw error;
    }
  }

  /**
   * Run database migrations
   */
  runMigrations() {
    try {
      // Check if conversations table exists first
      const tables = this.db
        .prepare(
          "SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'",
        )
        .all();

      if (tables.length === 0) {
        console.log("New database - skipping migrations");
        return;
      }

      // Check if page_context column exists
      const tableInfo = this.db.pragma("table_info(conversations)");
      const hasPageContext = tableInfo.some(
        (col) => col.name === "page_context",
      );

      if (!hasPageContext) {
        console.log("Adding page_context column to conversations table...");

        // Add column and index in a single transaction
        this.db.exec(`
                    ALTER TABLE conversations ADD COLUMN page_context TEXT DEFAULT NULL;
                    CREATE INDEX IF NOT EXISTS idx_conversations_page_context ON conversations(page_context);
                `);

        console.log("Migration complete: page_context column and index added");
      }

      // Check if agent_id column exists (re-read table info after prior migrations)
      const tableInfoForAgent = this.db.pragma("table_info(conversations)");
      const hasAgentId = tableInfoForAgent.some(
        (col) => col.name === "agent_id",
      );

      if (!hasAgentId) {
        console.log("Adding agent_id column to conversations table...");

        this.db.exec(`
                    ALTER TABLE conversations ADD COLUMN agent_id TEXT DEFAULT 'default';
                    CREATE INDEX IF NOT EXISTS idx_conversations_agent_id ON conversations(agent_id);
                `);

        console.log("Migration complete: agent_id column and index added");
      }

      // Backfill NULL agent_id to 'default' so filtering is consistent
      const nullCount = this.db
        .prepare(
          "SELECT COUNT(*) as n FROM conversations WHERE agent_id IS NULL",
        )
        .get();
      if (nullCount && nullCount.n > 0) {
        console.log(
          "Backfilling agent_id for",
          nullCount.n,
          "existing conversations...",
        );
        this.db
          .prepare(
            "UPDATE conversations SET agent_id = 'default' WHERE agent_id IS NULL",
          )
          .run();
        console.log("Backfill complete");
      }

      // Migration: Update category icons from emoji to Lucide icon names
      const categories = this.db
        .prepare("SELECT id, icon FROM categories")
        .all();
      const hasEmojiIcons = categories.some(
        (cat) => cat.icon && cat.icon.length <= 2,
      ); // Emojis are typically 1-2 chars

      if (hasEmojiIcons) {
        console.log("Updating category icons from emoji to Lucide names...");

        // Update built-in category icons
        const iconMapping = {
          sigils: "shield",
          signals: "radio",
          scrolls: "scroll",
          glyphs: "sparkles",
          grids: "grid-3x3",
          uncategorized: "message-square",
        };

        const updateStmt = this.db.prepare(
          "UPDATE categories SET icon = ? WHERE id = ?",
        );

        for (const [id, icon] of Object.entries(iconMapping)) {
          updateStmt.run(icon, id);
        }

        console.log(
          "Migration complete: Category icons updated to Lucide names",
        );
      }
    } catch (error) {
      console.error("Migration error:", error.message);
      // Re-throw so initialization fails properly
      throw error;
    }
  }

  /**
   * Create a new conversation
   * @param {Object} data - Conversation data
   * @param {string} data.title - Conversation title (optional)
   * @param {string} data.category_id - Category ID (optional)
   * @param {string} data.page_context - Page context (optional, e.g., 'dashboard', 'knowledge')
   * @param {boolean} data.is_starred - Star status (optional)
   * @returns {Object} Created conversation
   */
  createConversation(data = {}) {
    const id = uuidv4();
    const now = Date.now();
    const agentId =
      data.agent_id != null && data.agent_id !== ""
        ? String(data.agent_id)
        : "default";

    const stmt = this.db.prepare(`
            INSERT INTO conversations (
                id, title, category_id, page_context, agent_id, is_starred, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        `);

    stmt.run(
      id,
      data.title || "New Conversation",
      data.category_id || "uncategorized",
      data.page_context || null,
      agentId,
      data.is_starred ? 1 : 0,
      now,
      now,
    );

    return this.getConversation(id);
  }

  /**
   * Get a conversation by ID with its messages
   * @param {string} id - Conversation ID
   * @param {Object} options - Options
   * @param {number} options.messageLimit - Max messages to return
   * @param {number} options.messageOffset - Message offset for pagination
   * @returns {Object|null} Conversation with messages
   */
  getConversation(id, options = {}) {
    const conversation = this.db
      .prepare(
        `
            SELECT c.*, cat.name as category_name, cat.color as category_color, cat.icon as category_icon
            FROM conversations c
            LEFT JOIN categories cat ON c.category_id = cat.id
            WHERE c.id = ? AND c.deleted_at IS NULL
        `,
      )
      .get(id);

    if (!conversation) {
      return null;
    }

    // Get messages
    const messages = this.getMessages(
      id,
      options.messageLimit,
      options.messageOffset,
    );

    return {
      ...conversation,
      is_starred: Boolean(conversation.is_starred),
      is_pinned: Boolean(conversation.is_pinned),
      auto_titled: Boolean(conversation.auto_titled),
      messages,
    };
  }

  /**
   * Update a conversation
   * @param {string} id - Conversation ID
   * @param {Object} updates - Fields to update
   * @returns {Object|null} Updated conversation
   */
  updateConversation(id, updates) {
    const allowedFields = [
      "title",
      "category_id",
      "page_context",
      "agent_id",
      "is_starred",
      "is_pinned",
      "auto_titled",
      "message_count",
    ];

    const fields = [];
    const values = [];

    for (const [key, value] of Object.entries(updates)) {
      if (allowedFields.includes(key)) {
        fields.push(`${key} = ?`);
        values.push(value);
      }
    }

    if (fields.length === 0) {
      return this.getConversation(id);
    }

    fields.push("updated_at = ?");
    values.push(Date.now());
    values.push(id);

    const stmt = this.db.prepare(`
            UPDATE conversations 
            SET ${fields.join(", ")}
            WHERE id = ? AND deleted_at IS NULL
        `);

    stmt.run(...values);
    return this.getConversation(id);
  }

  /**
   * Delete a conversation (soft delete by default)
   * @param {string} id - Conversation ID
   * @param {boolean} soft - Use soft delete (default: true)
   * @returns {boolean} Success status
   */
  deleteConversation(id, soft = true) {
    if (soft) {
      const stmt = this.db.prepare(`
                UPDATE conversations 
                SET deleted_at = ?, updated_at = ?
                WHERE id = ?
            `);
      const now = Date.now();
      stmt.run(now, now, id);
    } else {
      // Hard delete (cascade will delete messages too)
      const stmt = this.db.prepare("DELETE FROM conversations WHERE id = ?");
      stmt.run(id);
    }
    return true;
  }

  /**
   * Add a message to a conversation
   * @param {string} conversationId - Conversation ID
   * @param {string} role - Message role (user/assistant/system)
   * @param {string} content - Message content
   * @param {Object} metadata - Additional metadata (optional)
   * @returns {Object} Created message
   */
  addMessage(conversationId, role, content, metadata = null) {
    const timestamp = Date.now();

    const stmt = this.db.prepare(`
            INSERT INTO messages (conversation_id, role, content, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?)
        `);

    const info = stmt.run(
      conversationId,
      role,
      content,
      timestamp,
      metadata ? JSON.stringify(metadata) : null,
    );

    // Update conversation metadata
    this.db
      .prepare(
        `
            UPDATE conversations 
            SET last_message_at = ?, 
                updated_at = ?,
                message_count = message_count + 1
            WHERE id = ?
        `,
      )
      .run(timestamp, timestamp, conversationId);

    // Trigger pattern learning asynchronously (non-blocking)
    // Only after we have at least 3 messages to learn from
    const conversation = this.getConversation(conversationId);
    if (conversation && conversation.message_count >= 3) {
      this.triggerPatternLearning(conversationId).catch((err) => {
        console.error("Pattern learning failed (non-fatal):", err.message);
      });
    }

    return {
      id: info.lastInsertRowid,
      conversation_id: conversationId,
      role,
      content,
      timestamp,
      metadata,
    };
  }

  /**
   * Trigger pattern learning from a conversation (async, non-blocking)
   * @param {string} conversationId - Conversation ID
   */
  async triggerPatternLearning(conversationId) {
    try {
      const conversation = this.getConversation(conversationId);
      if (
        !conversation ||
        !conversation.messages ||
        conversation.messages.length < 3
      ) {
        return; // Not enough messages
      }

      // Prepare messages in the format the backend expects
      const messages = conversation.messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));

      // Call the pattern learning endpoint
      const response = await fetch(
        "http://localhost:11436/polly/patterns/learn-from-conversation",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            conversation_id: conversationId,
            messages: messages,
            category: conversation.category_id,
          }),
        },
      );

      if (!response.ok) {
        throw new Error(`Pattern learning API returned ${response.status}`);
      }

      const result = await response.json();
      console.log(
        `Pattern learning: ${result.patterns_learned} patterns from conversation ${conversationId}`,
      );
    } catch (error) {
      // Pattern learning failures are non-fatal, just log them
      console.warn("Pattern learning failed:", error.message);
    }
  }

  /**
   * Get messages for a conversation
   * @param {string} conversationId - Conversation ID
   * @param {number} limit - Max messages to return (optional)
   * @param {number} offset - Offset for pagination (optional)
   * @returns {Array} Messages
   */
  getMessages(conversationId, limit = null, offset = 0) {
    let query = `
            SELECT id, conversation_id, role, content, timestamp, metadata
            FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp ASC
        `;

    const params = [conversationId];

    if (limit) {
      query += " LIMIT ? OFFSET ?";
      params.push(limit, offset);
    }

    const messages = this.db.prepare(query).all(...params);

    return messages.map((msg) => ({
      ...msg,
      metadata: msg.metadata ? JSON.parse(msg.metadata) : null,
    }));
  }

  /**
   * Get all conversations with optional filtering
   * @param {Object} options - Filter options
   * @param {string} options.agent_id - Filter by agent ID
   * @param {string} options.category_id - Filter by category
   * @param {string} options.page_context - Filter by page context
   * @param {boolean} options.starred - Filter by starred status
   * @param {boolean} options.pinned - Filter by pinned status
   * @param {number} options.limit - Max conversations to return
   * @param {number} options.offset - Offset for pagination
   * @returns {Array} Conversations
   */
  getAllConversations(options = {}) {
    const opts = options || {};
    // Always filter by agent_id so each agent only sees its own conversations
    const agentId =
      opts.agent_id !== undefined && opts.agent_id !== null
        ? opts.agent_id || "default"
        : "default";

    let query = `
            SELECT c.*, cat.name as category_name, cat.color as category_color, cat.icon as category_icon
            FROM conversations c
            LEFT JOIN categories cat ON c.category_id = cat.id
            WHERE c.deleted_at IS NULL
            AND (c.agent_id = ? OR (c.agent_id IS NULL AND ? = 'default'))
        `;

    const params = [agentId, agentId];

    if (opts.category_id) {
      query += " AND c.category_id = ?";
      params.push(opts.category_id);
    }

    if (opts.page_context) {
      query += " AND c.page_context = ?";
      params.push(opts.page_context);
    }

    if (opts.starred !== undefined) {
      query += " AND c.is_starred = ?";
      params.push(opts.starred ? 1 : 0);
    }

    if (opts.pinned !== undefined) {
      query += " AND c.is_pinned = ?";
      params.push(opts.pinned ? 1 : 0);
    }

    // Order by pinned first, then updated
    query += " ORDER BY c.is_pinned DESC, c.updated_at DESC";

    if (opts.limit) {
      query += " LIMIT ? OFFSET ?";
      params.push(opts.limit, opts.offset || 0);
    }

    const conversations = this.db.prepare(query).all(...params);

    return conversations.map((conv) => ({
      ...conv,
      is_starred: Boolean(conv.is_starred),
      is_pinned: Boolean(conv.is_pinned),
      auto_titled: Boolean(conv.auto_titled),
    }));
  }

  /**
   * Search conversations by title
   * @param {string} query - Search query
   * @param {number} limit - Max results
   * @returns {Array} Matching conversations
   */
  searchConversations(query, limit = 50) {
    const conversations = this.db
      .prepare(
        `
            SELECT c.*, cat.name as category_name, cat.color as category_color, cat.icon as category_icon
            FROM conversations c
            LEFT JOIN categories cat ON c.category_id = cat.id
            WHERE c.deleted_at IS NULL 
            AND c.title LIKE ?
            ORDER BY c.updated_at DESC
            LIMIT ?
        `,
      )
      .all(`%${query}%`, limit);

    return conversations.map((conv) => ({
      ...conv,
      is_starred: Boolean(conv.is_starred),
      is_pinned: Boolean(conv.is_pinned),
      auto_titled: Boolean(conv.auto_titled),
    }));
  }

  /**
   * Toggle star status for a conversation
   * @param {string} id - Conversation ID
   * @returns {Object} Updated conversation
   */
  toggleStar(id) {
    const current = this.db
      .prepare("SELECT is_starred FROM conversations WHERE id = ?")
      .get(id);
    if (!current) return null;

    const newValue = current.is_starred ? 0 : 1;
    return this.updateConversation(id, { is_starred: newValue });
  }

  /**
   * Toggle pin status for a conversation
   * @param {string} id - Conversation ID
   * @returns {Object} Updated conversation
   */
  togglePin(id) {
    const current = this.db
      .prepare("SELECT is_pinned FROM conversations WHERE id = ?")
      .get(id);
    if (!current) return null;

    const newValue = current.is_pinned ? 0 : 1;
    return this.updateConversation(id, { is_pinned: newValue });
  }

  /**
   * Generate a title for a conversation using LLM
   * This should be called from the main process with access to the LLM
   * @param {string} id - Conversation ID
   * @param {string} generatedTitle - The LLM-generated title
   * @returns {Object} Updated conversation
   */
  setGeneratedTitle(id, generatedTitle) {
    return this.updateConversation(id, {
      title: generatedTitle,
      auto_titled: 1,
    });
  }

  /**
   * Check if a conversation needs auto-titling
   * @param {string} id - Conversation ID
   * @returns {boolean} True if needs titling
   */
  needsAutoTitle(id) {
    const conv = this.db
      .prepare(
        `
            SELECT message_count, auto_titled, title
            FROM conversations
            WHERE id = ? AND deleted_at IS NULL
        `,
      )
      .get(id);

    if (!conv) return false;

    // Needs title if:
    // - Has enough messages
    // - Not already auto-titled
    // - Still has default title (case-insensitive check)
    const title = (conv.title || "").trim().toLowerCase();
    const isDefaultTitle = !title || title === "new conversation";
    return (
      conv.message_count >= this.autoTitleThreshold &&
      !conv.auto_titled &&
      isDefaultTitle
    );
  }

  /**
   * Clean up old conversations (soft-deleted and > 60 days)
   * Respects starred status
   * @returns {number} Number of conversations cleaned up
   */
  cleanupOldConversations() {
    const cutoffTime = Date.now() - this.retentionDays * 24 * 60 * 60 * 1000;

    const stmt = this.db.prepare(`
            UPDATE conversations
            SET deleted_at = ?
            WHERE deleted_at IS NULL
            AND is_starred = 0
            AND updated_at < ?
        `);

    const info = stmt.run(Date.now(), cutoffTime);
    return info.changes;
  }

  /**
   * Hard delete old soft-deleted conversations
   * @returns {number} Number of conversations permanently deleted
   */
  permanentlyDeleteOld() {
    const cutoffTime = Date.now() - this.retentionDays * 24 * 60 * 60 * 1000;

    const stmt = this.db.prepare(`
            DELETE FROM conversations
            WHERE deleted_at IS NOT NULL
            AND deleted_at < ?
        `);

    const info = stmt.run(cutoffTime);
    return info.changes;
  }

  /**
   * Enforce conversation limit (max 500)
   * Deletes oldest non-starred, non-pinned conversations
   * @returns {number} Number of conversations removed
   */
  enforceLimit() {
    const count = this.db
      .prepare(
        `
            SELECT COUNT(*) as count 
            FROM conversations 
            WHERE deleted_at IS NULL
        `,
      )
      .get().count;

    if (count <= this.maxConversations) {
      return 0;
    }

    const toDelete = count - this.maxConversations;

    // Get IDs of oldest non-starred, non-pinned conversations
    const ids = this.db
      .prepare(
        `
            SELECT id FROM conversations
            WHERE deleted_at IS NULL
            AND is_starred = 0
            AND is_pinned = 0
            ORDER BY updated_at ASC
            LIMIT ?
        `,
      )
      .all(toDelete);

    let deleted = 0;
    for (const { id } of ids) {
      this.deleteConversation(id, true);
      deleted++;
    }

    return deleted;
  }

  /**
   * Migrate old single conversation history to database
   * @param {Array} messages - Array of message objects from old format
   * @param {string} title - Optional title for the conversation
   * @returns {Object} Created conversation
   */
  migrateOldConversation(messages, title = "Migrated Conversation") {
    if (!messages || messages.length === 0) {
      return null;
    }

    // Create conversation
    const conversation = this.createConversation({
      title,
      category_id: "uncategorized",
    });

    // Add all messages
    for (const msg of messages) {
      this.addMessage(
        conversation.id,
        msg.role,
        msg.content,
        msg.metadata || null,
      );
    }

    return this.getConversation(conversation.id);
  }

  /**
   * Get all categories
   * @returns {Array} Categories
   */
  getAllCategories() {
    const categories = this.db
      .prepare(
        `
            SELECT * FROM categories
            ORDER BY is_custom ASC, name ASC
        `,
      )
      .all();

    return categories.map((cat) => ({
      ...cat,
      is_custom: Boolean(cat.is_custom),
    }));
  }

  /**
   * Create a custom category
   * @param {Object} data - Category data
   * @returns {Object} Created category
   */
  createCategory(data) {
    const id = data.id || data.name.toLowerCase().replace(/\s+/g, "-");

    const stmt = this.db.prepare(`
            INSERT INTO categories (id, name, description, icon, color, is_custom)
            VALUES (?, ?, ?, ?, ?, 1)
        `);

    stmt.run(
      id,
      data.name,
      data.description || null,
      data.icon || "folder",
      data.color || "#888888",
    );

    return this.db.prepare("SELECT * FROM categories WHERE id = ?").get(id);
  }

  /**
   * Get conversation statistics
   * @returns {Object} Statistics
   */
  getStats() {
    const total = this.db
      .prepare(
        `
            SELECT COUNT(*) as count FROM conversations WHERE deleted_at IS NULL
        `,
      )
      .get().count;

    const starred = this.db
      .prepare(
        `
            SELECT COUNT(*) as count FROM conversations WHERE deleted_at IS NULL AND is_starred = 1
        `,
      )
      .get().count;

    const byCategory = this.db
      .prepare(
        `
            SELECT c.category_id, cat.name, COUNT(*) as count
            FROM conversations c
            LEFT JOIN categories cat ON c.category_id = cat.id
            WHERE c.deleted_at IS NULL
            GROUP BY c.category_id
        `,
      )
      .all();

    const totalMessages = this.db
      .prepare(
        `
            SELECT COUNT(*) as count FROM messages
        `,
      )
      .get().count;

    return {
      total,
      starred,
      byCategory,
      totalMessages,
      limit: this.maxConversations,
      remaining: Math.max(0, this.maxConversations - total),
    };
  }

  /**
   * Close the database connection
   */
  close() {
    if (this.db) {
      this.db.close();
      this.db = null;
    }
  }
}

module.exports = ConversationManager;
