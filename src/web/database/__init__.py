"""
NeuroRead SQLite Database Module.
"""

from src.web.database.connection import get_connection, get_db
from src.web.database.migrations import init_db, migrate_legacy_json_to_sqlite
from src.web.database.queries import (
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
)

__all__ = [
    "get_connection",
    "get_db",
    "init_db",
    "migrate_legacy_json_to_sqlite",
    "upsert_session",
    "get_session_by_id",
    "list_sessions_db",
    "rename_session_db",
    "delete_session_db",
    "insert_message_db",
    "attach_document_db",
    "detach_document_db",
    "create_collection_db",
    "list_collections_db",
    "delete_collection_db",
]
