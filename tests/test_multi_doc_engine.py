"""
Unit & Integration Tests for Ticket 1.7: Multi-Document Engine & Collections.
Tests batch ingestion, cross-document retrieval, collection groupings, and API endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from src.web.app import app
from src.web.services.pipeline_service import PipelineService
from src.web.services.document_service import DocumentService


@pytest.fixture(scope="module")
def client():
    service = PipelineService.get_instance()
    service._initialize_retriever()
    with TestClient(app) as c:
        yield c


def test_batch_ingest_service():
    """Verify DocumentService.batch_ingest can atomically index multiple documents."""
    doc_service = DocumentService.get_instance()
    docs_to_ingest = [
        {
            "title": "Tài liệu Y học Tập 1",
            "text": "Kháng sinh nhóm beta-lactam ức chế tổng hợp thành tế bào vi khuẩn. Penicillin là đại diện tiêu biểu.",
            "category": "Medical",
        },
        {
            "title": "Tài liệu Y học Tập 2",
            "text": "Vaccine mRNA sử dụng chuỗi RNA thông tin mã hóa kháng nguyên gai của virus để kích hoạt hệ miễn dịch.",
            "category": "Medical",
        },
        {
            "title": "Tài liệu Trí tuệ Nhân tạo",
            "text": "Mô hình Transformer sử dụng cơ chế Self-Attention để mô hình hóa mối quan hệ giữa các từ trong chuỗi.",
            "category": "AI",
        },
    ]

    res = doc_service.batch_ingest(docs_to_ingest)
    assert res["success"] is True
    assert res["total_ingested"] == 3
    assert len(res["documents"]) == 3

    # Check documents are in store and index
    doc_ids = [d["document_id"] for d in res["documents"]]
    for d_id in doc_ids:
        assert d_id in doc_service.pipeline_service.store._index


def test_cross_document_retrieval():
    """Verify BM25 cross-document retrieve restricts search to target doc_ids."""
    doc_service = DocumentService.get_instance()
    docs = [
        {
            "document_id": "DOC_CROSS_001",
            "title": "Quy định Hàng không",
            "text": "Hành khách mang theo hành lý xách tay tối đa 7kg trên các chuyến bay nội địa Việt Nam.",
        },
        {
            "document_id": "DOC_CROSS_002",
            "title": "Quy định Đường sắt",
            "text": "Hành khách đi tàu hỏa được mang theo hành lý không quá 20kg miễn phí cước vận chuyển.",
        },
    ]
    doc_service.batch_ingest(docs)

    # Search with both doc_ids
    results_both = doc_service.cross_document_retrieve(
        query="hành lý xách tay bao nhiêu kg",
        top_k=5,
        document_ids=["DOC_CROSS_001", "DOC_CROSS_002"],
    )
    assert len(results_both) > 0
    doc_ids_found = {r.document_id for r in results_both}
    assert "DOC_CROSS_001" in doc_ids_found

    # Search restricted only to DOC_CROSS_002
    results_only_rail = doc_service.cross_document_retrieve(
        query="hành lý",
        top_k=5,
        document_ids=["DOC_CROSS_002"],
    )
    for r in results_only_rail:
        assert r.document_id == "DOC_CROSS_002"


def test_collection_crud_endpoints(client):
    """Verify REST API endpoints for collection lifecycle (/api/v2/documents/collections)."""
    # 1. Create collection
    create_res = client.post("/api/v2/documents/collections", json={
        "name": "Bộ sưu tập Giao thông",
        "description": "Tập hợp các tài liệu đường sắt và hàng không",
        "document_ids": ["DOC_CROSS_001", "DOC_CROSS_002"],
    })
    assert create_res.status_code == 200
    coll_data = create_res.json()
    assert "id" in coll_data
    coll_id = coll_data["id"]

    # 2. List collections
    list_res = client.get("/api/v2/documents/collections")
    assert list_res.status_code == 200
    colls = list_res.json()["collections"]
    assert any(c["id"] == coll_id for c in colls)

    # 3. Get collection detail
    detail_res = client.get(f"/api/v2/documents/collections/{coll_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["name"] == "Bộ sưu tập Giao thông"

    # 4. Delete collection
    del_res = client.delete(f"/api/v2/documents/collections/{coll_id}")
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # 5. Verify 404 after deletion
    get_after_del = client.get(f"/api/v2/documents/collections/{coll_id}")
    assert get_after_del.status_code == 404


def test_batch_ingest_rest_endpoint(client):
    """Verify REST API POST /api/v2/documents/batch-ingest."""
    payload = {
        "documents": [
            {"title": "Doc Batch A", "text": "Hệ thống bộ nhớ tham số SA-CMS học nhanh ở Level 1.", "category": "Tech"},
            {"title": "Doc Batch B", "text": "Hệ thống bộ nhớ tham số SA-CMS củng cố chậm ở Level 3.", "category": "Tech"},
        ]
    }
    resp = client.post("/api/v2/documents/batch-ingest", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["total_ingested"] == 2
