"""
Tests for Compare Service & REST API (Ticket 3.2).
Verifies pairwise document diffing, similarity scoring, unique passage extraction, and cross-document QA.
"""

import pytest
from fastapi.testclient import TestClient

from src.web.app import app
from src.web.services.compare_service import CompareService
from src.web.services.pipeline_service import PipelineService
from src.web.demo_data import seed_demo_documents


@pytest.fixture(autouse=True)
def ensure_seed_documents():
    service = PipelineService.get_instance()
    if service.store.document_count < 2:
        seed_demo_documents()
        service._initialize_retriever()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_compare_documents_pairwise():
    """Verify pairwise document comparison yields structural summary, similar pairs, and unique items."""
    service = CompareService()
    res = service.compare_documents("DEMO_DOC_001", "DEMO_DOC_002", similarity_threshold=0.15)

    assert "document_a" in res and res["document_a"]["id"] == "DEMO_DOC_001"
    assert "document_b" in res and res["document_b"]["id"] == "DEMO_DOC_002"
    assert "similarity_index" in res
    assert 0.0 <= res["similarity_index"] <= 1.0
    assert "summary" in res
    assert "similar_passages" in res
    assert "unique_to_a" in res
    assert "unique_to_b" in res


def test_cross_qa():
    """Verify comparative question answering synthesizes responses from both documents with citations."""
    service = CompareService()
    res = service.cross_qa(
        query="Kiến trúc bộ nhớ và hạ tầng giao thông kết nối thế nào?",
        doc_id_a="DEMO_DOC_001",
        doc_id_b="DEMO_DOC_002",
        top_k=3
    )

    assert res["query"] == "Kiến trúc bộ nhớ và hạ tầng giao thông kết nối thế nào?"
    assert res["doc_id_a"] == "DEMO_DOC_001"
    assert res["doc_id_b"] == "DEMO_DOC_002"
    assert "answer" in res and len(res["answer"]) > 20
    assert "citations" in res


def test_compare_api_endpoints(client):
    """Verify /api/v2/compare endpoints return HTTP 200 with valid structure."""
    # 1. POST /api/v2/compare
    res_cmp = client.post("/api/v2/compare", json={
        "doc_id_a": "DEMO_DOC_001",
        "doc_id_b": "DEMO_DOC_002",
        "similarity_threshold": 0.2
    })
    assert res_cmp.status_code == 200
    data_cmp = res_cmp.json()
    assert "similarity_index" in data_cmp
    assert "summary" in data_cmp

    # 2. POST /api/v2/compare/qa
    res_qa = client.post("/api/v2/compare/qa", json={
        "query": "So sánh nội dung giữa 2 tài liệu",
        "doc_id_a": "DEMO_DOC_001",
        "doc_id_b": "DEMO_DOC_002",
        "top_k": 3
    })
    assert res_qa.status_code == 200
    data_qa = res_qa.json()
    assert "answer" in data_qa
    assert "citations" in data_qa
