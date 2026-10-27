"""
Central Configuration for NeuroRead / SA-CMS Web Platform.
Manages file system paths, runtime parameters, and offline-first flags.
"""

import os
from pathlib import Path

# Paths
WEB_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = WEB_DIR.parent.parent
STATIC_DIR = WEB_DIR / "static"
DATA_DIR = PROJECT_ROOT / "data"
DOCUMENT_STORE_DIR = DATA_DIR / "document_store"
CHAT_SESSIONS_DIR = DATA_DIR / "chat_sessions"
DB_PATH = DATA_DIR / "neuroread.db"
LOCAL_RUNTIME_DIR = PROJECT_ROOT / "local_runtime"
FIGURES_DIR = PROJECT_ROOT / "results" / "figures"

# Server configuration
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))

# Safety & Offline Protocols
STRICT_OFFLINE = True
TRAINING_FREEZE = True
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
