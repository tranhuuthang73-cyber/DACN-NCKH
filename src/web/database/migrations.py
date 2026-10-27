"""
Database Schema Migrations & Data Importers for NeuroRead SQLite Database.
Initializes tables, FTS5 virtual tables, and migrates legacy JSON files.
"""

import json
import sqlite3
import time
from pathlib import Path
from typing import Optional

from src.web.config import DB_PATH, CHAT_SESSIONS_DIR, DOCUMENT_STORE_DIR
from src.web.database.connection import get_connection

SCHEMA_DDL = """
-- Documents metadata
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    file_type TEXT DEFAULT 'txt',
    file_size INTEGER DEFAULT 0,
    page_count INTEGER DEFAULT 0,
    passage_count INTEGER DEFAULT 0,
    category TEXT DEFAULT 'General',
    collection_id TEXT,
    memory_status TEXT DEFAULT 'indexed',
    raw_text_preview TEXT,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL,
    version INTEGER DEFAULT 1,
    FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE SET NULL
);

-- Document collections (grouping)
CREATE TABLE IF NOT EXISTS collections (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL
);

-- Chat sessions
CREATE TABLE IF NOT EXISTS chat_sessions (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL,
    message_count INTEGER DEFAULT 0,
    is_archived INTEGER DEFAULT 0
);

-- Session-document attachments (many-to-many)
CREATE TABLE IF NOT EXISTS session_documents (
    session_id TEXT NOT NULL,
    document_id TEXT NOT NULL,
    attached_at REAL NOT NULL,
    PRIMARY KEY (session_id, document_id),
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Chat messages
CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    citations TEXT,
    gate_values TEXT,
    input_tokens INTEGER,
    output_tokens INTEGER,
    latency_ms REAL,
    mode TEXT DEFAULT 'hybrid',
    is_refusal INTEGER DEFAULT 0,
    routing TEXT DEFAULT 'DIRECT_LOOKUP',
    created_at REAL NOT NULL,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
);

-- Flashcards (study mode)
CREATE TABLE IF NOT EXISTS flashcards (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    level TEXT,
    source_passage_id TEXT,
    status TEXT DEFAULT 'new',
    next_review_at REAL,
    review_count INTEGER DEFAULT 0,
    created_at REAL NOT NULL,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id, created_at);
CREATE INDEX IF NOT EXISTS idx_documents_collection ON documents(collection_id);
CREATE INDEX IF NOT EXISTS idx_flashcards_document ON flashcards(document_id);
"""

# FTS5 tables are created conditionally in case sqlite was compiled without FTS5
FTS5_DDL = """
CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
    content, content=messages, content_rowid=rowid
);

CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
    title, raw_text_preview, content=documents, content_rowid=rowid
);
"""


def init_db(db_path: Optional[Path] = None) -> None:
    """Creates all database tables and indexes if they do not exist."""
    conn = get_connection(db_path)
    try:
        conn.executescript(SCHEMA_DDL)
        try:
            conn.executescript(FTS5_DDL)
        except sqlite3.OperationalError:
            # FTS5 not compiled in this sqlite build; fallback gracefully
            pass
        conn.commit()
    finally:
        conn.close()


def migrate_legacy_json_to_sqlite(db_path: Optional[Path] = None) -> int:
    """
    Migrates chat sessions from `data/chat_sessions/sessions.json`
    and document index from `data/document_store/index.json` into SQLite.
    Returns the count of migrated sessions.
    """
    init_db(db_path)
    conn = get_connection(db_path)
    migrated_count = 0

    try:
        # 1. Migrate documents from document store index
        doc_index_file = DOCUMENT_STORE_DIR / "index.json"
        if doc_index_file.exists():
            try:
                with open(doc_index_file, "r", encoding="utf-8") as f:
                    doc_index = json.load(f)
                    now = time.time()
                    for doc_id, meta in doc_index.items():
                        title = meta.get("title", doc_id)
                        version = meta.get("current_version", 1)
                        created_at = meta.get("created_at", now)
                        conn.execute(
                            """
                            INSERT OR IGNORE INTO documents (
                                id, title, version, created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?)
                            """,
                            (doc_id, title, version, created_at, created_at),
                        )
            except Exception:
                pass

        # 2. Migrate sessions & messages from chat_sessions/sessions.json
        sessions_file = CHAT_SESSIONS_DIR / "sessions.json"
        if sessions_file.exists():
            try:
                with open(sessions_file, "r", encoding="utf-8") as f:
                    sessions_data = json.load(f)
                    for s in sessions_data:
                        s_id = s.get("session_id")
                        if not s_id:
                            continue

                        title = s.get("title", "Cuộc trò chuyện mới")
                        created_at = s.get("created_at", time.time())
                        updated_at = s.get("updated_at", created_at)
                        messages = s.get("messages", [])
                        doc_ids = s.get("document_ids", [])

                        # Insert session
                        conn.execute(
                            """
                            INSERT OR IGNORE INTO chat_sessions (
                                id, title, created_at, updated_at, message_count
                            ) VALUES (?, ?, ?, ?, ?)
                            """,
                            (s_id, title, created_at, updated_at, len(messages)),
                        )

                        # Insert attachments
                        for d_id in doc_ids:
                            conn.execute(
                                """
                                INSERT OR IGNORE INTO session_documents (
                                    session_id, document_id, attached_at
                                ) VALUES (?, ?, ?)
                                """,
                                (s_id, d_id, updated_at),
                            )

                        # Insert messages
                        for m in messages:
                            m_id = m.get("id") or f"msg_{s_id[:6]}_{time.time()}"
                            role = m.get("role", "user")
                            content = m.get("content", "")
                            citations = json.dumps(m.get("citations", []), ensure_ascii=False)
                            routing = m.get("routing", "DIRECT_LOOKUP")
                            refused = 1 if m.get("refused") else 0
                            m_time = m.get("timestamp", updated_at)

                            conn.execute(
                                """
                                INSERT OR IGNORE INTO messages (
                                    id, session_id, role, content, citations, routing, is_refusal, created_at
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """,
                                (m_id, s_id, role, content, citations, routing, refused, m_time),
                            )

                        migrated_count += 1
            except Exception:
                pass

        conn.commit()
    finally:
        conn.close()

    return migrated_count
