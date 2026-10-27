"""
FastAPI Dependency Injection Providers for NeuroRead.
Allows routers to cleanly request services and managers without hardcoupling.
"""

from src.web.services.pipeline_service import PipelineService
from src.web.session_manager import SessionManager
from src.hybrid_qa.document_store import DocumentStore
from src.memory.offline_memory_manager import OfflineMemoryManager


def get_pipeline_service() -> PipelineService:
    """Returns the singleton PipelineService instance."""
    return PipelineService.get_instance()


def get_session_manager() -> SessionManager:
    """Returns the SessionManager instance from PipelineService."""
    return PipelineService.get_instance().session_manager


def get_document_store() -> DocumentStore:
    """Returns the DocumentStore instance from PipelineService."""
    return PipelineService.get_instance().store


def get_memory_manager() -> OfflineMemoryManager:
    """Returns the OfflineMemoryManager instance."""
    return PipelineService.get_instance().memory_manager
