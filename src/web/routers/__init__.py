"""
Central Router Registry for NeuroRead.
Aggregates all modular sub-routers into a unified APIRouter.
"""

from fastapi import APIRouter

from src.web.routers.system import router as system_router
from src.web.routers.arena import router as arena_router
from src.web.routers.ingest import router as ingest_router
from src.web.routers.snapshots import router as snapshots_router
from src.web.routers.research import router as research_router
from src.web.routers.sessions import router as sessions_router
from src.web.routers.telemetry import router as telemetry_router
from src.web.routers.chat import router as chat_router
from src.web.routers.study import router as study_router

api_router = APIRouter()

# Register all modular routers
api_router.include_router(system_router)
api_router.include_router(arena_router)
api_router.include_router(ingest_router)
api_router.include_router(snapshots_router)
api_router.include_router(research_router)
api_router.include_router(sessions_router)
api_router.include_router(telemetry_router)
api_router.include_router(chat_router)
api_router.include_router(study_router)

__all__ = [
    "api_router",
    "system_router",
    "arena_router",
    "ingest_router",
    "snapshots_router",
    "research_router",
    "sessions_router",
    "telemetry_router",
    "chat_router",
    "study_router",
]
