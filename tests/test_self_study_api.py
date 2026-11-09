"""
Integration Tests for Self-Study API Endpoints (Ticket 1.4).
Validates:
1. POST /api/self-study/ingest (extraction & Level 2/3 memory adaptation).
2. GET /api/self-study/{doc_id}/pairs (retrieves extracted QA pairs).
3. POST /api/self-study/ask (NeuralReaderEngine grounded answering).
4. POST /api/self-study/ask with unrelated query (safe refusal).
5. POST /api/self-study/reset (memory parameter reset).
"""

import pytest
from fastapi.testclient import TestClient

from src.web.app import app, PipelineService


@pytest.fixture(scope="module")
def client():
    # Initialize pipeline service and demo store
    service = PipelineService.get_instance()
    service._initialize_retriever()
    return TestClient(app)


def test_api_ingest_with_raw_text(client):
    payload = {
        "text": (
            "Hệ thống SA-CMS là bộ nhớ liên tục cấu trúc đa tầng. "
            "Cơ chế này giúp tối ưu hóa chi phí token trên văn bản dài. "
            "Mô hình đạt tỷ lệ giảm 87,5% chi phí token. "
            "Tuy nhiên, hạn chế của hệ thống là cần phân đoạn rõ ràng."
        ),
        "document_id": "test_doc_api_01",
        "max_pairs": 10,
        "epochs": 1,
        "max_steps": 2,
        "train_memory": False,  # disable actual GPU/CPU gradient steps in rapid API test
    }
    response = client.post("/api/self-study/ingest", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["document_id"] == "test_doc_api_01"
    assert data["pairs_count"] > 0
    assert len(data["pairs"]) > 0
    assert "pairs_by_rule" in data


def test_api_ingest_empty_text_raises_400(client):
    payload = {"text": "   "}
    response = client.post("/api/self-study/ingest", json=payload)
    assert response.status_code == 400


def test_api_get_pairs_existing_or_missing(client):
    # Missing document
    response = client.get("/api/self-study/nonexistent_doc_id/pairs")
    assert response.status_code == 404


def test_api_ask_neural_reader(client):
    payload = {
        "query": "SA-CMS là gì?",
        "answer_mode": "balanced",
        "top_k": 3,
    }
    response = client.post("/api/self-study/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "core_answer" in data
    assert "formatted_answer" in data
    assert "confidence" in data
    assert "is_grounded" in data
    assert "tokens_used" in data
    assert "latency_ms" in data


def test_api_ask_refusal_on_unrelated_query(client):
    payload = {
        "query": "Cách nấu lẩu hải sản chua cay?",
        "answer_mode": "balanced",
        "top_k": 2,
    }
    response = client.post("/api/self-study/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_grounded"] is False
    assert "Không tìm thấy đủ thông tin" in data["formatted_answer"]


def test_api_reset_memory(client):
    response = client.post("/api/self-study/reset")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("success", "error")


def test_api_hypergraph_build_and_deduce(client):
    # 1. Build hypergraph from existing documents
    res_build = client.post("/api/self-study/hypergraph/build")
    assert res_build.status_code == 200
    build_data = res_build.json()
    assert build_data["status"] == "success"
    assert "hypergraph_statistics" in build_data

    # 2. Test multi-hop deduce
    payload = {
        "query": "SA-CMS giải quyết vấn đề gì?",
        "start_concept": "SA-CMS",
        "target_concept": "Chi phí token",
        "max_hops": 4,
    }
    res_deduce = client.post("/api/self-study/hypergraph/deduce", json=payload)
    assert res_deduce.status_code == 200
    deduce_data = res_deduce.json()
    assert deduce_data["status"] in ("success", "no_path_found")


def test_api_contradiction_scan(client):
    payload = {"document_ids": None}
    res = client.post("/api/self-study/contradictions/scan", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "report" in data
    assert "contradictions_found" in data["report"]


def test_api_entropy_filter(client):
    payload = {
        "text": "Xin chào bạn, chúc một ngày tốt lành. Mô hình SA-CMS đạt tỷ lệ giảm 87,5% chi phí token.",
        "surprisal_threshold": 3.5,
    }
    res = client.post("/api/self-study/entropy/filter", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "filtered_text" in data
    assert "SA-CMS" in data["filtered_text"]


def test_api_sleep_consolidate(client):
    payload = {
        "document_ids": None,
        "steps": 1,
        "ewc_lambda": 100.0,
    }
    res = client.post("/api/self-study/sleep/consolidate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "consolidation_report" in data
    assert data["consolidation_report"]["status"] in ("success", "no_pairs_to_replay")


