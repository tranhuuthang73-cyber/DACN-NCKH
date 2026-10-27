"""
NeuroRead / SA-CMS Intelligence Studio — Modular Application Entrypoint.
Built with FastAPI, integrating DocumentStore, BM25 Retriever, SA-CMS Multi-Level Memory,
Token-Efficiency Telemetry, and Exploratory Answering Modes.

STRICT RULE: NO TRAINING, NO GRADIENT UPDATES, FROZEN INFERENCE ONLY.
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.web.config import STATIC_DIR, FIGURES_DIR
from src.web.services.pipeline_service import PipelineService
from src.web.demo_data import seed_demo_documents
from src.web.routers import api_router

# Re-export for complete backward compatibility with existing tests
from src.web.models.schemas import (
    ChatRequest,
    CompareRequest,
    RawDocumentRequest,
    CreateSessionRequest,
    RenameSessionRequest,
    AttachDocumentRequest,
    SessionMessageRequest,
    RetrieveRequest,
    UnifiedChatRequest,
    ArenaCompareRequest,
    IngestCustomDocRequest,
    SnapshotCreateRequest,
    SnapshotRollbackRequest,
)

# 6 explicit pipeline stages for offline SA-CMS memory architecture (Step 4 & UX regression checks)
PIPELINE_STAGES = [
    "Tệp đã lưu",
    "Văn bản đã trích xuất",
    "Cấu trúc đã phân tích",
    "Chỉ mục cục bộ đã sẵn sàng",
    "SA-CMS Memory đã sẵn sàng",
    "Sẵn sàng hỏi",
]

from src.web.routers.ingest import list_documents, create_raw_document, delete_document



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Eagerly initializes retriever, demo documents, and offline inference pipeline."""
    service = PipelineService.get_instance()
    service._initialize_retriever()
    if service.store.document_count == 0:
        seed_demo_documents()
        service._initialize_retriever()
    service.load_model_if_requested(prefer_gpu=False)
    yield


app = FastAPI(
    title="NeuroRead Studio (SA-CMS)",
    description="Enterprise-grade Document Intelligence and Multi-Level Memory System with Token-Efficiency Telemetry",
    version="5.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Mount figures directory for 100% offline Q1 figures preview
if FIGURES_DIR.exists():
    app.mount("/results/figures", StaticFiles(directory=str(FIGURES_DIR)), name="figures")
    app.mount("/figures", StaticFiles(directory=str(FIGURES_DIR)), name="figures_alias")

# Include all modular sub-routers
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    from src.web.config import HOST, PORT
    uvicorn.run("src.web.app:app", host=HOST, port=PORT, reload=False)
