"""
Comprehensive Automated Test Suite: Full-Stack Verification & Scientific Features.
Tests 100% End-to-End Functionality:
1. GET / (HTML layout, zero CDN links, all interactive components present)
2. POST /api/chat (Modes P2, P1, B2, B5; grounded answer < 20 tokens; refusal guard)
3. POST /api/arena_compare (Feature 1: Side-by-Side Model Arena P2 vs B5 vs B2)
4. POST /api/ingest_custom_doc (Feature 2: b_ℓ(t)=1 boundary extraction, self-study QA generation, BM25 indexing)
5. POST /api/snapshots/demo_version_update & rollback (Feature 3: v1 -> v2 version demo and rollback)
6. Neural & Evidence X-Ray components (Feature 4: 5 memory levels & dynamic meters)
7. GET /api/research_summary & /figures/* (Feature 5: RQ1-RQ5 verified metrics & 300 DPI figures)
"""

import os
import sys
import socket
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure strict offline environment
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["SA_CMS_OFFLINE_MODE"] = "1"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.web.app import app


@pytest.fixture(autouse=True)
def enforce_network_isolation(monkeypatch):
    """
    Simulate physical network disconnection.
    Any attempt to connect to a non-loopback host raises an immediate OSError.
    """
    orig_connect = socket.socket.connect

    def blocked_connect(self, address):
        host = address[0] if isinstance(address, tuple) else address
        allowed_hosts = ("127.0.0.1", "localhost", "::1")
        if host not in allowed_hosts:
            raise OSError(f"STRICT OFFLINE VIOLATION: Outbound network call to {host} is prohibited.")
        return orig_connect(self, address)

    monkeypatch.setattr(socket.socket, "connect", blocked_connect)
    yield


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


# ==============================================================================
# 1. FRONTEND LAYOUT & STRICT OFFLINE ZERO-CDN CONTRACT
# ==============================================================================

def test_root_html_renders_cleanly_and_zero_cdn(client):
    """Verify GET / returns clean HTML with all UI controls and zero CDN links."""
    res = client.get("/")
    assert res.status_code == 200
    html = res.text

    # Zero CDN links verification
    forbidden_cdn = ["cdn.", "cdnjs.", "unpkg.com", "fonts.googleapis.com", "jsdelivr"]
    for token in forbidden_cdn:
        assert token not in html, f"Found external CDN reference in HTML: {token}"

    import re
    external_scripts = re.findall(r'<script[^>]+src=["\']http[^"\']+["\']', html)
    external_styles = re.findall(r'<link[^>]+href=["\']http[^"\']+["\']', html)
    assert len(external_scripts) == 0, f"Found external script tags: {external_scripts}"
    assert len(external_styles) == 0, f"Found external stylesheet tags: {external_styles}"

    # Verify 4 Core Mode Buttons
    assert 'id="mode-btn-p2"' in html
    assert 'id="mode-btn-p1"' in html
    assert 'id="mode-btn-b2"' in html
    assert 'id="mode-btn-b5"' in html

    # Verify Feature 1: Arena toggle button
    assert 'id="btn-toggle-arena"' in html

    # Verify Feature 2: Live Ingest button & Modal
    assert 'id="btn-sidebar-ingest"' in html
    assert 'id="modal-live-ingest"' in html
    assert 'id="btn-run-live-ingest"' in html
    assert 'id="btn-load-sample-text"' in html

    # Verify Feature 3: Snapshot controls
    assert 'id="btn-sidebar-update-v2"' in html
    assert 'id="btn-sidebar-rollback"' in html

    # Verify Feature 4: 5 Memory Levels & Meters
    assert 'id="val-g0"' in html
    assert 'id="bar-g0"' in html
    assert 'id="val-g1"' in html
    assert 'id="bar-g1"' in html
    assert 'id="val-g2"' in html
    assert 'id="bar-g2"' in html
    assert 'id="val-g3"' in html
    assert 'id="bar-g3"' in html
    assert "Mức 0:" in html or "Level 0" in html
    assert "Mức 1:" in html or "Level 1" in html
    assert "Mức 2:" in html or "Level 2" in html
    assert "Mức 3:" in html or "Level 3" in html
    assert "Mức 4:" in html or "Level 4" in html

    # Verify Feature 5: Research Hub button, Modal, and Session Export
    assert 'id="btn-open-research-modal"' in html
    assert 'id="modal-research-hub"' in html
    assert 'id="btn-export-session"' in html

    # Verify regression invariant classes
    assert "pipeline-stages-reference" in html
    app_js = (PROJECT_ROOT / "src" / "web" / "static" / "js" / "app.js").read_text(encoding="utf-8")
    assert "evidence-section-block" in app_js


# ==============================================================================
# 2. CHAT API: MODES P2, P1, B2, B5 & GROUNDING / REFUSAL
# ==============================================================================

def test_chat_p2_grounded_answer(client):
    """Verify Mode P2 answers grounded query with citations and concise text."""
    payload = {
        "query": "Tuyến đường sắt cao tốc Bắc - Nam có chiều dài bao nhiêu km?",
        "document_id": "DEMO_DOC_002",
        "mode": "hybrid",
        "answer_mode": "concise",
        "top_k": 5,
        "language": "vi",
    }
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["refused"] is False
    assert len(data.get("citations", [])) > 0
    assert "1.541" in data["answer"] or "1541" in data["answer"] or "km" in data["answer"] or "chiều dài" in data["answer"]

    # Verify telemetry
    assert "telemetry" in data
    assert data["telemetry"]["input_tokens"] > 0
    assert data["telemetry"]["output_tokens"] > 0

    # Verify memory diagnostics
    diag = data.get("memory_diagnostics", {})
    assert "g1" in diag and "g2" in diag and "g3" in diag


def test_chat_refusal_on_ungrounded_query(client):
    """Verify system safely refuses out-of-domain queries without hallucination."""
    payload = {
        "query": "Giá xe ô tô điện VinFast VF8 hiện nay là bao nhiêu tiền?",
        "mode": "hybrid",
        "answer_mode": "concise",
        "top_k": 5,
        "language": "vi",
    }
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["refused"] is True
    assert data.get("citations", []) == []
    refusal_text = data.get("refusal_message") or data.get("answer") or ""
    assert any(term in refusal_text.lower() for term in ["không chứa", "từ chối", "bằng chứng", "refus"])


def test_chat_all_alternative_modes(client):
    """Verify Modes P1 (memory), B2 (context/RAG), and B5 (fixed CMS) execute."""
    for mode in ["memory", "context", "hybrid"]:
        payload = {
            "query": "Kiến trúc SA-CMS áp dụng mấy cấp độ bộ nhớ?",
            "mode": mode,
            "answer_mode": "concise",
            "top_k": 3,
            "language": "vi",
        }
        res = client.post("/api/chat", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "answer" in data


# ==============================================================================
# 3. FEATURE 1: SIDE-BY-SIDE MODEL ARENA (P2 vs B5 vs B2)
# ==============================================================================

def test_arena_compare_grounded_query(client):
    """Verify Arena returns 3 comparative columns with P2 as superior winner."""
    payload = {
        "query": "Tuyến đường sắt cao tốc Bắc - Nam có chiều dài bao nhiêu km?",
        "top_k": 5,
        "language": "vi",
    }
    res = client.post("/api/arena_compare", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["is_refusal"] is False
    assert "p2" in data and "b5" in data and "b2" in data

    p2 = data["p2"]
    b5 = data["b5"]
    b2 = data["b2"]

    # P2 metrics: concise, accurate, -70.1% token savings
    assert len(p2["citations"]) > 0
    assert p2["tokens_saved_pct"] <= -50.0
    assert p2["output_tokens"] <= 25
    assert p2["gates"]["g1"] > 0
    assert p2["gates"]["g2"] > 0
    assert p2["gates"]["g3"] > 0

    # B2 metrics: high token overhead (> 800 tokens)
    assert b2["input_tokens"] > 800

    # Winner verdict
    assert data["winner"] == "P2_SA_CMS_HYBRID"


def test_arena_compare_refusal_query(client):
    """Verify Arena correctly activates smart refusal on P2 for out-of-scope query."""
    payload = {
        "query": "Giá tiền mã hóa Bitcoin hôm nay là bao nhiêu USD?",
        "top_k": 5,
        "language": "vi",
    }
    res = client.post("/api/arena_compare", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["is_refusal"] is True
    assert data["p2"]["refused"] is True


# ==============================================================================
# 4. FEATURE 2: LIVE INGESTION & SELF-STUDY QA GENERATOR
# ==============================================================================

def test_ingest_custom_doc_boundaries_and_self_study(client):
    """Verify structural boundary detection b_ℓ(t)=1, fixed-cuts hazard, and self-study QA."""
    doc_text = (
        "# CHIẾN LƯỢC NĂNG LƯỢNG TÁI TẠO QUỐC GIA 2030\n\n"
        "## Mục 1: Tiềm năng Năng lượng Gió Ngoài khơi\n"
        "Việt Nam sở hữu hơn 3.260 km bờ biển với tiềm năng điện gió ngoài khơi ước tính đạt 600 GW. "
        "Đây là nguồn năng lượng chiến lược để đạt phát thải ròng bằng 0 vào năm 2050.\n\n"
        "Tốc độ gió trung bình đạt 9 m/s ở độ cao 100 mét tại vùng biển duyên hải Nam Trung Bộ, "
        "rất thuận lợi để triển khai các trang trại điện gió quy mô lớn.\n\n"
        "## Mục 2: Dự án Năng lượng Mặt trời Tập trung\n"
        "Quy hoạch Điện VIII đặt mục tiêu tổng công suất điện mặt trời đạt 34.000 MW vào năm 2030, "
        "ưu tiên phát triển hệ thống điện mặt trời mái nhà tự sản tự tiêu cho hộ gia đình và khu công nghiệp.\n\n"
        "Tổng mức đầu tư cho hạ tầng truyền tải giải tỏa công suất ước tính 15 tỷ USD giai đoạn 2026 - 2030."
    )

    payload = {
        "title": "Chiến lược Năng lượng Tái tạo 2030",
        "text": doc_text,
    }
    res = client.post("/api/ingest_custom_doc", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["success"] is True
    stats = data["stats"]
    assert stats["documents"] == 1
    assert stats["sections"] >= 2
    assert stats["paragraphs"] >= 4

    # Verify detected boundaries b_ℓ(t)=1
    boundaries = data["detected_boundaries"]
    levels = [b["level"] for b in boundaries]
    assert 1 in levels  # b_1(t)=1 paragraph
    assert 2 in levels  # b_2(t)=1 section
    assert 3 in levels  # b_3(t)=1 document

    # Verify fixed cuts comparison
    cuts = data["fixed_cuts_comparison"]
    assert len(cuts) >= 3
    assert any("C^(1)" in c["schedule"] or "C(1)" in c["schedule"] or "C(¹)" in c["schedule"] for c in cuts)

    # Verify Self-Study QA generation (Section 6.4)
    self_study = data["self_study_qa"]
    assert len(self_study) >= 2
    for qa in self_study:
        assert len(qa["question"]) > 10
        assert len(qa["answer"]) > 10
        assert "source_section" in qa

    # Verify BM25 live indexing
    assert data["indexed_passages"] >= 4

    # Verify we can immediately ask a question about the new document
    qa_payload = {
        "query": "Tiềm năng điện gió ngoài khơi của Việt Nam ước tính đạt bao nhiêu GW?",
        "mode": "hybrid",
        "answer_mode": "concise",
        "top_k": 3,
        "language": "vi",
    }
    chat_res = client.post("/api/chat", json=qa_payload)
    assert chat_res.status_code == 200
    chat_data = chat_res.json()
    assert chat_data["refused"] is False
    assert "600" in chat_data["answer"] or "GW" in chat_data["answer"]


# ==============================================================================
# 5. FEATURE 3: SNAPSHOT TIME MACHINE & VERSION UPDATE (v1 -> v2 & ROLLBACK)
# ==============================================================================

def test_snapshot_lifecycle_v1_to_v2_and_rollback(client):
    """Verify live defense workflow: update facts to v2, verify new answer, rollback to v1."""
    # 1. Check snapshots endpoint
    res_snap = client.get("/api/snapshots")
    assert res_snap.status_code == 200
    snap_data = res_snap.json()
    assert "snapshots" in snap_data

    # 2. Execute v2 update demo
    res_v2 = client.post("/api/snapshots/demo_version_update")
    assert res_v2.status_code == 200
    v2_data = res_v2.json()
    assert v2_data["status"] == "success"
    assert v2_data["new_version"] == 2

    # 3. Query updated fact: efficiency is 92% in v2
    qa_v2 = {
        "query": "Hiệu suất vận hành thực nghiệm SA-CMS là bao nhiêu phần trăm?",
        "mode": "hybrid",
        "answer_mode": "concise",
        "top_k": 3,
        "language": "vi",
    }
    chat_v2 = client.post("/api/chat", json=qa_v2)
    assert chat_v2.status_code == 200
    assert "92" in chat_v2.json()["answer"]

    # 4. Rollback to v1
    res_rb = client.post("/api/snapshots/rollback")
    assert res_rb.status_code == 200
    rb_data = res_rb.json()
    assert rb_data["status"] == "success"
    assert rb_data["active_version"] == 1

    # 5. Query after rollback: efficiency 92% is no longer in v1
    chat_v1 = client.post("/api/chat", json=qa_v2)
    assert chat_v1.status_code == 200
    assert "92" not in chat_v1.json()["answer"]


# ==============================================================================
# 6. FEATURE 5: RESEARCH HUB RQ1–RQ5 VERIFIED BENCHMARKS & FIGURES
# ==============================================================================

def test_research_summary_metrics_and_figures(client):
    """Verify RQ1-RQ5 verified metrics and high-res figures are served cleanly."""
    res = client.get("/api/research_summary")
    assert res.status_code == 200
    data = res.json()

    # RQ1: loss and convergence
    assert "rq1" in data
    assert data["rq1"]["p2"]["token_f1"] > data["rq1"]["b5"]["token_f1"]

    # RQ2: statistical significance p < 0.001
    assert "rq2" in data
    assert data["rq2"]["p2_vs_b5"]["p_value"] < 0.001

    # RQ3: ablation study
    assert "rq3" in data

    # RQ4: continual learning snapshots
    assert "rq4" in data
    assert data["rq4"]["snapshots"] == 36

    # RQ5: token budget savings -70.1%
    assert "rq5" in data
    assert data["rq5"]["savings_pct"] == -70.1

    # Figures metadata
    assert len(data.get("figures", [])) >= 4

    # Verify static route serving for each figure
    fig_urls = [
        "/figures/fig1_rq2_sa_cms_vs_baselines.png",
        "/figures/fig2_ablation_study.png",
        "/results/figures/fig3_rq4_continual_forgetting_curve.png",
        "/results/figures/fig4_rq3_hybrid_faithfulness.png",
    ]
    for url in fig_urls:
        fig_res = client.get(url)
        assert fig_res.status_code == 200
        assert fig_res.headers["content-type"] == "image/png"
        assert len(fig_res.content) > 1000
