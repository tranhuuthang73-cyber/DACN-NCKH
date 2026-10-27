"""
SQLite Connection Manager for NeuroRead Desktop & Web Studio.
Uses Python Standard Library sqlite3 with WAL mode, foreign keys, and safe connection handling.

STRICT RULE: NO TRAINING, NO GRADIENT UPDATES, FROZEN INFERENCE ONLY.
"""

import sqlite3
from pathlib import Path
from typing import Optional, Generator
from contextlib import contextmanager

from src.web.config import DB_PATH


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """
    Creates and returns an optimized SQLite connection with:
    - WAL journal mode for concurrent reads and writes
    - Synchronous = NORMAL for fast SSD performance
    - Foreign keys enforced
    - Row factory enabled for dictionary-like column access
    """
    target_path = db_path or DB_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(
        str(target_path),
        timeout=30.0,
        check_same_thread=False,
    )
    conn.row_factory = sqlite3.Row

    # Performance and integrity pragmas
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA busy_timeout = 30000;")

    return conn


@contextmanager
def get_db(db_path: Optional[Path] = None) -> Generator[sqlite3.Connection, None, None]:
    """Context manager for safe database transactions."""
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


get_db_connection = get_db
