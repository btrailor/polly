-- Conversations Table
-- Stores conversation metadata
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL DEFAULT 'New Conversation',
    category_id TEXT,
    page_context TEXT DEFAULT NULL,
    agent_id TEXT DEFAULT 'default',
    is_starred INTEGER DEFAULT 0,
    is_pinned INTEGER DEFAULT 0,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    last_message_at INTEGER,
    deleted_at INTEGER,
    message_count INTEGER DEFAULT 0,
    auto_titled INTEGER DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- Messages Table
-- Stores individual messages within conversations
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    metadata TEXT,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- Categories Table
-- Stores conversation categories (domains + custom)
CREATE TABLE IF NOT EXISTS categories (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    icon TEXT,
    color TEXT,
    is_custom INTEGER DEFAULT 0
);

-- Conversation Metadata Table
-- Stores arbitrary key-value metadata for conversations
CREATE TABLE IF NOT EXISTS conversation_metadata (
    conversation_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    PRIMARY KEY (conversation_id, key),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_conversations_category ON conversations(category_id);
CREATE INDEX IF NOT EXISTS idx_conversations_page_context ON conversations(page_context);
CREATE INDEX IF NOT EXISTS idx_conversations_agent_id ON conversations(agent_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created ON conversations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_conversations_updated ON conversations(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_conversations_deleted ON conversations(deleted_at);
CREATE INDEX IF NOT EXISTS idx_conversations_starred ON conversations(is_starred);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp DESC);

-- Pre-populate Categories
-- 5 fixed domains from DomainEngine + Uncategorized
INSERT OR IGNORE INTO categories (id, name, description, icon, color, is_custom) VALUES
    ('sigils', 'Sigils', 'Identity, authentication, security, cryptography', 'shield', '#FF6B6B', 0),
    ('signals', 'Signals', 'Communication, messaging, events, notifications', 'radio', '#4ECDC4', 0),
    ('scrolls', 'Scrolls', 'Documents, files, content, storage', 'scroll', '#95E1D3', 0),
    ('glyphs', 'Glyphs', 'UI, rendering, visual presentation', 'sparkles', '#FFE66D', 0),
    ('grids', 'Grids', 'Data structures, databases, organization', 'grid-3x3', '#A8DADC', 0),
    ('uncategorized', 'Uncategorized', 'General conversations', 'message-square', '#CCCCCC', 0);
