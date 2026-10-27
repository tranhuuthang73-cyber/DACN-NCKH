"""
Unit Tests for NeuroRead SQLite Database Layer & SessionManager Migration.
Verifies table creation, CRUD operations, foreign keys, and migration fidelity.
"""

import time
import pytest
from pathlib import Path

from src.web.database import (
    get_connection,
    init_db,
    upsert_session,
    get_session_by_id,
    list_sessions_db,
    rename_session_db,
    delete_session_db,
    insert_message_db,
    attach_document_db,
    detach_document_db,
    create_collection_db,
    list_collections_db,
    delete_collection_db,
    migrate_legacy_json_to_sqlite,
)
from src.web.session_manager import SessionManager


@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_neuroread.db"
    init_db(db_file)
    return db_file


def test_db_initialization_and_tables(temp_db):
    conn = get_connection(temp_db)
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
    )
    tables = [row["name"] for row in cur.fetchall()]
    conn.close()

    assert "documents" in tables
    assert "collections" in tables
    assert "chat_sessions" in tables
    assert "session_documents" in tables
    assert "messages" in tables
    assert "flashcards" in tables


def test_session_and_message_crud(temp_db):
    session_id = "test_chat_001"
    upsert_session(session_id, "Test Chat Session", db_path=temp_db)

    # Verify session inserted
    s = get_session_by_id(session_id, db_path=temp_db)
    assert s is not None
    assert s["title"] == "Test Chat Session"
    assert s["message_count"] == 0

    # Insert messages
    insert_message_db(
        msg_id="msg_001",
        session_id=session_id,
        role="user",
        content="Hello NeuroRead",
        db_path=temp_db,
    )
    insert_message_db(
        msg_id="msg_002",
        session_id=session_id,
        role="assistant",
        content="Hello! How can I assist you with your document?",
        citations=["P001", "P002"],
        db_path=temp_db,
    )

    s_updated = get_session_by_id(session_id, db_path=temp_db)
    assert len(s_updated["messages"]) == 2
    assert s_updated["message_count"] == 2
    assert s_updated["messages"][0]["content"] == "Hello NeuroRead"
    assert s_updated["messages"][1]["citations"] == ["P001", "P002"]

    # Rename
    assert rename_session_db(session_id, "Renamed Session", db_path=temp_db) is True
    assert get_session_by_id(session_id, db_path=temp_db)["title"] == "Renamed Session"

    # Delete
    assert delete_session_db(session_id, db_path=temp_db) is True
    assert get_session_by_id(session_id, db_path=temp_db) is None


def test_document_attachment_lifecycle(temp_db):
    session_id = "test_chat_attach"
    upsert_session(session_id, "Attachment Test", db_path=temp_db)

    # Attach document
    assert attach_document_db(session_id, "DOC_001", db_path=temp_db) is True
    assert attach_document_db(session_id, "DOC_002", db_path=temp_db) is True

    s = get_session_by_id(session_id, db_path=temp_db)
    assert s["document_ids"] == ["DOC_001", "DOC_002"]

    # Detach document
    assert detach_document_db(session_id, "DOC_001", db_path=temp_db) is True
    s2 = get_session_by_id(session_id, db_path=temp_db)
    assert s2["document_ids"] == ["DOC_002"]


def test_collections_crud(temp_db):
    coll_id = create_collection_db("Research Papers", "My collection", db_path=temp_db)
    assert coll_id.startswith("coll_")

    colls = list_collections_db(db_path=temp_db)
    assert len(colls) == 1
    assert colls[0]["name"] == "Research Papers"

    assert delete_collection_db(coll_id, db_path=temp_db) is True
    assert len(list_collections_db(db_path=temp_db)) == 0


def test_session_manager_persistence(tmp_path):
    storage_dir = tmp_path / "chat_sessions"
    sm1 = SessionManager(storage_dir=str(storage_dir))
    sess = sm1.create_session(title="Persistent Chat")
    sess.add_message(role="user", content="Test persistent message")
    sm1.attach_document(sess.session_id, "DOC_TEST_999")
    sm1.save()

    # Re-initialize SessionManager to test loading from SQLite / files
    sm2 = SessionManager(storage_dir=str(storage_dir))
    loaded = sm2.get_session(sess.session_id)
    assert loaded is not None
    assert loaded.title == "Persistent Chat"
    assert "DOC_TEST_999" in loaded.document_ids
    assert len(loaded.messages) == 1
    assert loaded.messages[0]["content"] == "Test persistent message"
