"""
Telemetry, Token Efficiency, and Audit Analytics Router for NeuroRead.
Exposes token usage reductions, latency benchmarks, and query logs.
"""

from typing import Optional
from fastapi import APIRouter, Depends

from src.web.dependencies import get_pipeline_service
from src.web.services.pipeline_service import PipelineService

router = APIRouter(tags=["Telemetry"])


@router.get("/api/analytics")
async def get_analytics(service: PipelineService = Depends(get_pipeline_service)):
    analytics_data = service.telemetry.compute_analytics()
    analytics_data["document_count"] = service.store.document_count
    analytics_data["passage_count"] = len(service.store.get_all_passages())
    return analytics_data


@router.get("/api/token-efficiency")
async def get_token_efficiency(service: PipelineService = Depends(get_pipeline_service)):
    analytics = service.telemetry.compute_analytics()
    experiments = service.telemetry.get_experiments(limit=50)
    return {
        "reductions": analytics["reductions"],
        "tradeoffs": analytics["tradeoffs"],
        "recent_experiments": experiments,
    }


@router.get("/api/history")
async def get_query_history(
    limit: int = 50,
    search: Optional[str] = None,
    method: Optional[str] = None,
    service: PipelineService = Depends(get_pipeline_service),
):
    return service.telemetry.get_history(limit=limit, search=search, method=method)
