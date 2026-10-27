"""
Web models module.
"""

from src.web.models.schemas import (
    ChatRequest,
    CompareRequest,
    RetrieveRequest,
    UnifiedChatRequest,
    ArenaCompareRequest,
    RawDocumentRequest,
    IngestCustomDocRequest,
    CreateSessionRequest,
    RenameSessionRequest,
    AttachDocumentRequest,
    SessionMessageRequest,
    SnapshotCreateRequest,
    SnapshotRollbackRequest,
)

__all__ = [
    "ChatRequest",
    "CompareRequest",
    "RetrieveRequest",
    "UnifiedChatRequest",
    "ArenaCompareRequest",
    "RawDocumentRequest",
    "IngestCustomDocRequest",
    "CreateSessionRequest",
    "RenameSessionRequest",
    "AttachDocumentRequest",
    "SessionMessageRequest",
    "SnapshotCreateRequest",
    "SnapshotRollbackRequest",
]
