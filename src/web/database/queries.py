"""
Reusable Database Queries & Data Access Layer for NeuroRead.
Encapsulates all SQL statements for sessions, messages, documents, and collections.
"""

import json
import time
from typing import List, Dict, Any, Optional
from pathlib import Path

from src.web.database.connection import get_db


# ==============================================================================
# SESSIONS
# ==============================================================================

def upsert_session(
    session_id: str,
    title: str,
    created_at: Optional[float] = None,
    updated_at: Optional[float] = None,
    message_count: int = 0,
    db_path: Optional[Path] = None,
) -> None:
    now = time.time()
    c_time = created_at or now
    u_time = updated_at or now
    with get_db(db_path) as conn:
        conn.execute(
            """
            INSERT INTO chat_sessions (id, title, created_at, updated_at, message_count)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title = excluded.title,
                updated_at = excluded.updated_at,
                message_count = excluded.message_count
            """,
            (session_id, title, c_time, u_time, message_count),
        )


def get_session_by_id(session_id: str, db_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    with get_db(db_path) as conn:
        cur = conn.execute("SELECT * FROM chat_sessions WHERE id = ?", (session_id,))
        row = cur.fetchone()
        if not row:
            return None

        # Fetch attached document IDs
        doc_cur = conn.execute(
            "SELECT document_id FROM session_documents WHERE session_id = ? ORDER BY attached_at ASC",
            (session_id,),
        )
        doc_ids = [d["document_id"] for d in doc_cur.fetchall()]

        # Fetch messages
        msg_cur = conn.execute(
            "SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC",
            (session_id,),
        )
        messages = []
        for m in msg_cur.fetchall():
            citations = []
            if m["citations"]:
                try:
                    citations = json.loads(m["citations"])
                except Exception:
                    citations = []
            messages.append({
                "id": m["id"],
                "role": m["role"],
                "content": m["content"],
                "timestamp": m["created_at"],
                "citations": citations,
                "routing": m["routing"],
                "refused": bool(m["is_refusal"]),
            })

        return {
            "session_id": row["id"],
            "title": row["title"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "message_count": row["message_count"],
            "document_ids": doc_ids,
            "messages": messages,
        }


def list_sessions_db(db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    with get_db(db_path) as conn:
        cur = conn.execute(
            "SELECT * FROM chat_sessions WHERE is_archived = 0 ORDER BY updated_at DESC"
        )
        sessions = []
        for row in cur.fetchall():
            doc_cur = conn.execute(
                "SELECT document_id FROM session_documents WHERE session_id = ?",
                (row["id"],),
            )
            doc_ids = [d["document_id"] for d in doc_cur.fetchall()]
            sessions.append({
                "session_id": row["id"],
                "title": row["title"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "message_count": row["message_count"],
                "document_ids": doc_ids,
            })
        return sessions


def rename_session_db(session_id: str, new_title: str, db_path: Optional[Path] = None) -> bool:
    with get_db(db_path) as conn:
        cur = conn.execute(
            "UPDATE chat_sessions SET title = ?, updated_at = ? WHERE id = ?",
            (new_title.strip(), time.time(), session_id),
        )
        return cur.rowcount > 0


def delete_session_db(session_id: str, db_path: Optional[Path] = None) -> bool:
    with get_db(db_path) as conn:
        cur = conn.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
        return cur.rowcount > 0


# ==============================================================================
# MESSAGES
# ==============================================================================

def insert_message_db(
    msg_id: str,
    session_id: str,
    role: str,
    content: str,
    citations: Optional[List[Any]] = None,
    gate_values: Optional[Dict[str, float]] = None,
    input_tokens: Optional[int] = None,
    output_tokens: Optional[int] = None,
    latency_ms: Optional[float] = None,
    mode: str = "hybrid",
    is_refusal: bool = False,
    routing: str = "DIRECT_LOOKUP",
    created_at: Optional[float] = None,
    db_path: Optional[Path] = None,
) -> None:
    now = created_at or time.time()
    citations_json = json.dumps(citations or [], ensure_ascii=False)
    gates_json = json.dumps(gate_values or {}) if gate_values else None

    with get_db(db_path) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO messages (
                id, session_id, role, content, citations, gate_values,
                input_tokens, output_tokens, latency_ms, mode, is_refusal, routing, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                msg_id, session_id, role, content, citations_json, gates_json,
                input_tokens, output_tokens, latency_ms, mode, 1 if is_refusal else 0,
                routing, now
            ),
        )
        # Update session message count & timestamp
        conn.execute(
            """
            UPDATE chat_sessions
            SET message_count = (SELECT COUNT(*) FROM messages WHERE session_id = ?),
                updated_at = ?
            WHERE id = ?
            """,
            (session_id, now, session_id),
        )


# ==============================================================================
# ATTACHMENTS
# ==============================================================================

def attach_document_db(session_id: str, doc_id: str, db_path: Optional[Path] = None) -> bool:
    now = time.time()
    with get_db(db_path) as conn:
        try:
            conn.execute(
                """
                INSERT OR IGNORE INTO documents (id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (doc_id, doc_id, now, now),
            )
            conn.execute(
                """
                INSERT OR IGNORE INTO session_documents (session_id, document_id, attached_at)
                VALUES (?, ?, ?)
                """,
                (session_id, doc_id, now),
            )
            conn.execute(
                "UPDATE chat_sessions SET updated_at = ? WHERE id = ?",
                (now, session_id),
            )
            return True
        except Exception:
            return False


def detach_document_db(session_id: str, doc_id: str, db_path: Optional[Path] = None) -> bool:
    with get_db(db_path) as conn:
        cur = conn.execute(
            "DELETE FROM session_documents WHERE session_id = ? AND document_id = ?",
            (session_id, doc_id),
        )
        if cur.rowcount > 0:
            conn.execute(
                "UPDATE chat_sessions SET updated_at = ? WHERE id = ?",
                (time.time(), session_id),
            )
            return True
        return False


# ==============================================================================
# COLLECTIONS (Ticket 1.7 preparation)
# ==============================================================================

def create_collection_db(name: str, description: str = "", db_path: Optional[Path] = None) -> str:
    import uuid
    coll_id = f"coll_{uuid.uuid4().hex[:8]}"
    now = time.time()
    with get_db(db_path) as conn:
        conn.execute(
            "INSERT INTO collections (id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (coll_id, name, description, now, now),
        )
    return coll_id


def list_collections_db(db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    with get_db(db_path) as conn:
        cur = conn.execute("SELECT * FROM collections ORDER BY created_at DESC")
        return [dict(row) for row in cur.fetchall()]


def delete_collection_db(collection_id: str, db_path: Optional[Path] = None) -> bool:
    with get_db(db_path) as conn:
        cur = conn.execute("DELETE FROM collections WHERE id = ?", (collection_id,))
        return cur.rowcount > 0
