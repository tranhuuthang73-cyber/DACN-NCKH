"""
Web Services module for NeuroRead / SA-CMS Studio.
"""

from src.web.services.pipeline_service import PipelineService
from src.web.services.document_service import DocumentService

__all__ = ["PipelineService", "DocumentService"]
