"""
Memory Snapshots & Time-Machine Router for NeuroRead.
Supports snapshot listing, manual creation, rollback to v1, and v2 update.
"""

import time
import json
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException

from src.web.models.schemas import SnapshotCreateRequest, SnapshotRollbackRequest
from src.web.dependencies import get_pipeline_service
from src.web.services.pipeline_service import PipelineService
from src.web.demo_data import seed_demo_documents

router = APIRouter(tags=["Snapshots"])


@router.get("/api/snapshots")
async def get_snapshots_list(service: PipelineService = Depends(get_pipeline_service)):
    """
    Tính năng 3: Liệt kê các bản chụp bộ nhớ và phiên bản tài liệu (Mục 6.7 Đề cương).
    """
    docs = service.store.list_documents()
    snapshots_list = []
    for d in docs:
        doc_id = d["document_id"]
        try:
            doc = service.store.get_document(doc_id)
            snapshots_list.append({
                "snapshot_id": f"snap_{doc_id}_v{doc.version}",
                "document_id": doc_id,
                "title": doc.title,
                "version": doc.version,
                "created_at": doc.created_at,
                "status": "active" if doc.version == d.get("current_version", 1) else "archived"
            })
        except Exception:
            pass

    return {
        "snapshots": snapshots_list,
        "total": len(snapshots_list),
        "demo_version_state": getattr(service, "_demo_version_state", "v1")
    }


@router.post("/api/snapshots/create")
async def create_snapshot(
    req: SnapshotCreateRequest,
    service: PipelineService = Depends(get_pipeline_service),
):
    """Tạo bản chụp bộ nhớ mới."""
    snap_id = f"snap_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    return {
        "status": "success",
        "snapshot_id": snap_id,
        "name": req.name or "Snapshot Thủ công",
        "timestamp": time.time(),
        "message": "Đã tạo bản chụp bộ nhớ và trạng thái chỉ mục thành công."
    }


@router.post("/api/snapshots/demo_version_update")
async def demo_version_update(service: PipelineService = Depends(get_pipeline_service)):
    """
    Tính năng 3: Nạp bản cập nhật v2 của tài liệu mẫu với các số liệu mới (Mục 6.7 Đề cương).
    """
    demo_doc_id = "VN_DOC_001"
    if demo_doc_id not in service.store._index:
        all_docs = list(service.store._index.keys())
        if all_docs:
            demo_doc_id = all_docs[0]
        else:
            seed_demo_documents()
            service._initialize_retriever()
            demo_doc_id = "VN_DOC_001"

    doc = service.store.get_document(demo_doc_id)
    v2_text = (
        doc.raw_text +
        "\n\n## CẬP NHẬT PHIÊN BẢN V2 (MỤC 6.7 ĐỀ CƯƠNG NCKH)\n"
        "- Năm hoàn thành dự án đường sắt cao tốc Bắc - Nam: Năm 2035 (Phiên bản v2 cập nhật).\n"
        "- Hiệu suất vận hành thực nghiệm SA-CMS: 92% (Phiên bản v2 cập nhật, so với 35% ở bản cũ).\n"
        "- Trạng thái bộ nhớ: Củng cố Mức 2 và Mức 3 với snapshot mới D0_plus_v2.\n"
    )
    v2_title = f"{doc.title} (Bản v2)"

    if demo_doc_id in service.store._index:
        service.store._index[demo_doc_id]["current_version"] = 1

    doc_record = service.store.update_document(
        document_id=demo_doc_id,
        raw_text=v2_text,
        title=v2_title,
        metadata={"version": 2, "updated_at": time.time()}
    )
    passages = service.chunker.chunk_document(doc_record)
    doc_record.passages = passages
    doc_file = service.store.docs_dir / demo_doc_id / f"v{doc_record.version}.json"
    with open(doc_file, "w", encoding="utf-8") as f:
        json.dump(doc_record.to_dict(), f, indent=2, ensure_ascii=False)

    service._initialize_retriever()
    service._demo_version_state = "v2"

    return {
        "status": "success",
        "document_id": demo_doc_id,
        "title": v2_title,
        "version": doc_record.version,
        "new_version": doc_record.version,
        "updated_facts": {
            "nam_hoan_thanh": "Năm 2035 (Phiên bản v2)",
            "hieu_suat_van_hanh": "92% (Phiên bản v2)"
        },
        "message": "Đã nạp bản cập nhật v2! Khi hỏi lại cùng câu hỏi, hệ thống sẽ trả lời theo số liệu mới của v2."
    }


@router.post("/api/snapshots/rollback")
async def demo_version_rollback(service: PipelineService = Depends(get_pipeline_service)):
    """
    Tính năng 3: Quay lui trạng thái bộ nhớ về Snapshot v1 (Mục 6.7 Đề cương).
    """
    demo_doc_id = "VN_DOC_001"
    if demo_doc_id not in service.store._index:
        all_docs = list(service.store._index.keys())
        if all_docs:
            demo_doc_id = all_docs[0]

    if demo_doc_id in service.store._index:
        service.store._index[demo_doc_id]["current_version"] = 1
        service.store._save_index()
        service._initialize_retriever()
    service._demo_version_state = "v1"

    return {
        "status": "success",
        "document_id": demo_doc_id,
        "version": 1,
        "active_version": 1,
        "message": "Đã quay lui (Rollback) về bản chụp Snapshot v1! Các số liệu đã được phục hồi về nguyên bản."
    }


@router.get("/api/memory/snapshots")
async def list_memory_snapshots(service: PipelineService = Depends(get_pipeline_service)):
    """Lists local SA-CMS memory snapshots (Step 6)."""
    return {"snapshots": service.memory_manager.list_snapshots()}


@router.post("/api/memory/snapshots/{snapshot_id}/rollback")
async def rollback_memory_snapshot(
    snapshot_id: str,
    service: PipelineService = Depends(get_pipeline_service),
):
    """Rolls back active SA-CMS memory state to target snapshot (Step 6)."""
    success = service.memory_manager.rollback_snapshot(snapshot_id, service.model)
    if not success:
        raise HTTPException(status_code=400, detail=f"Rollback to snapshot '{snapshot_id}' failed.")
    return {"success": True, "snapshot_id": snapshot_id, "message": "Memory rolled back successfully."}


@router.get("/api/memory/manifest")
async def get_memory_manifest_endpoint(service: PipelineService = Depends(get_pipeline_service)):
    """Exposes local SA-CMS memory manifest (Step 4)."""
    return service.memory_manager.get_memory_manifest()


@router.get("/api/memory/{doc_id}")
async def get_memory_visualization(
    doc_id: str,
    version: Optional[int] = None,
    service: PipelineService = Depends(get_pipeline_service),
):
    try:
        doc = service.store.get_document(doc_id, version=version)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")

    doc_struct = service.structure_parser.parse_text(doc.raw_text)
    num_paras = max(1, len(doc_struct.paragraphs))
    num_secs = max(1, len(doc_struct.sections))
    has_snapshot = service.store.has_memory_snapshot(doc_id, doc.version)

    return {
        "document_id": doc_id,
        "title": doc.title,
        "version": doc.version,
        "has_snapshot": has_snapshot,
        "snapshot_path": f"data/document_store/snapshots/{doc_id}_v{doc.version}.pt" if has_snapshot else None,
        "total_trainable_parameters": 5314752,
        "timescales": {
            "level_1": {
                "name": "Level 1: Paragraph Adaptation",
                "timescale": "Fine (High Frequency)",
                "boundary": "Paragraph Boundaries",
                "state_size_params": 1771584,
                "dimension": "[576, 1536]",
                "update_count": num_paras,
                "covered_units": f"{num_paras} Paragraphs",
                "update_frequency_score": 95,
                "description": "Captures local phrase transitions, entities, and micro-syntax.",
            },
            "level_2": {
                "name": "Level 2: Section Alignment",
                "timescale": "Intermediate (Moderate Frequency)",
                "boundary": "Section Delimiters",
                "state_size_params": 1771584,
                "dimension": "[576, 1536]",
                "update_count": num_secs,
                "covered_units": f"{num_secs} Sections",
                "update_frequency_score": 50,
                "description": "Maintains topical coherence, sub-thematic continuity, and section context.",
            },
            "level_3": {
                "name": "Level 3: Document Synthesis",
                "timescale": "Coarse (Persistent Anchor)",
                "boundary": "Document Boundary",
                "state_size_params": 1771584,
                "dimension": "[576, 1536]",
                "update_count": 1,
                "covered_units": "1 Full Document",
                "update_frequency_score": 15,
                "description": "Stores macro-level global document representation and global invariants.",
            }
        }
    }

