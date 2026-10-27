"""
Pydantic Request and Response Schemas for NeuroRead / SA-CMS Studio.
100% Offline, Strict Validation.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ==============================================================================
# CHAT & RETRIEVAL SCHEMAS
# ==============================================================================

class ChatRequest(BaseModel):
    query: str
    document_id: Optional[str] = None
    mode: str = "hybrid"  # context, memory, hybrid
    answer_mode: str = "balanced"  # balanced, concise, minimal
    top_k: int = 5
    language: Optional[str] = None


class CompareRequest(BaseModel):
    query: str
    document_id: Optional[str] = None
    methods: List[str] = Field(default=["B1", "B2", "P1", "P2"])
    answer_mode: str = "balanced"
    top_k: int = 5
    language: Optional[str] = None


class RetrieveRequest(BaseModel):
    query: str
    top_k: int = 5
    document_ids: Optional[List[str]] = None


class UnifiedChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    document_id: Optional[str] = None
    document_ids: Optional[List[str]] = None
    answer_mode: str = "balanced"  # concise, balanced, detailed
    mode: str = "hybrid"  # context, memory, hybrid
    top_k: int = 5
    language: Optional[str] = "vi"


class ArenaCompareRequest(BaseModel):
    query: str
    document_id: Optional[str] = None
    top_k: int = 5
    language: Optional[str] = "vi"


# ==============================================================================
# DOCUMENT INGESTION SCHEMAS
# ==============================================================================

class RawDocumentRequest(BaseModel):
    title: str
    text: str
    document_id: Optional[str] = None
    category: Optional[str] = "General"


class IngestCustomDocRequest(BaseModel):
    text: str
    title: Optional[str] = "Tài liệu Nghiên cứu Mới"
    document_id: Optional[str] = None
    category: Optional[str] = "General"


# ==============================================================================
# SESSION SCHEMAS
# ==============================================================================

class CreateSessionRequest(BaseModel):
    title: Optional[str] = None
    document_ids: Optional[List[str]] = None


class RenameSessionRequest(BaseModel):
    title: str


class AttachDocumentRequest(BaseModel):
    document_id: str


class SessionMessageRequest(BaseModel):
    query: str
    answer_mode: str = "balanced"  # concise, balanced, detailed
    mode: str = "hybrid"  # context, memory, hybrid
    top_k: int = 5
    language: Optional[str] = "vi"


# ==============================================================================
# MEMORY SNAPSHOT SCHEMAS
# ==============================================================================

class SnapshotCreateRequest(BaseModel):
    document_id: Optional[str] = None
    name: Optional[str] = None
    notes: Optional[str] = None


class SnapshotRollbackRequest(BaseModel):
    snapshot_id: Optional[str] = None
    document_id: Optional[str] = None


# ==============================================================================
# MULTI-DOCUMENT & COLLECTION SCHEMAS (Ticket 1.7)
# ==============================================================================

class BatchIngestRequest(BaseModel):
    documents: List[RawDocumentRequest]


class CreateCollectionRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    document_ids: Optional[List[str]] = None

