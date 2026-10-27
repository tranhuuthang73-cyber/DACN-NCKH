"""
System & Health Router for NeuroRead.
Serves index page, provides system health status, and verifies offline resource integrity.
"""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse

from src.web.config import STATIC_DIR
from src.web.dependencies import get_pipeline_service
from src.web.services.pipeline_service import PipelineService
from src.web.local_model_loader import LocalModelLoader

router = APIRouter(tags=["System"])


@router.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h2>Document Intelligence Web Platform (SA-CMS) Initializing...</h2>")


@router.get("/api/health")
async def get_health(service: PipelineService = Depends(get_pipeline_service)):
    return {
        "status": "healthy",
        "phase": "5.1",
        "document_count": service.store.document_count,
        "indexed_passages": len(service.store.get_all_passages()),
        "model_loaded": service.model_loaded,
        "device": service.device,
        "model_error": service.model_error,
    }


@router.get("/api/system/status")
async def get_system_status(service: PipelineService = Depends(get_pipeline_service)):
    """Returns local offline resource status for UI / demonstration (Steps 17 & 18)."""
    loader = LocalModelLoader.get_instance()
    status = loader.get_resource_status(document_count=service.store.document_count)

    mem_detail = service.memory_manager.get_detailed_offline_status()
    status.update({
        "integrity_verdict": mem_detail["integrity_verdict"],
        "memory_state": mem_detail["memory_state"],
        "document_store_status": mem_detail["document_store_status"],
        "network_status": mem_detail["network_status"],
    })
    return status


@router.get("/api/system/integrity")
async def get_system_integrity_endpoint(service: PipelineService = Depends(get_pipeline_service)):
    """Verifies SHA-256 checksum integrity of offline assets (Step 17)."""
    return service.memory_manager.verify_checksum_integrity()


@router.post("/api/checkpoints/switch")
async def switch_checkpoint_endpoint(checkpoint_name: str = Query(...)):
    """Switches active SA-CMS checkpoint (Step 14)."""
    loader = LocalModelLoader.get_instance()
    return loader.switch_checkpoint(checkpoint_name)
