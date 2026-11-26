"""
Brain v9 (3-Layer Persistent Long-Term Memory + Pedagogical Tables/Steps + Auto-Thinking)
AND Teammate Tô Thế Kiệt's 4 Real-World Runtime Bug Regressions.

100% Local Offline — ZERO external LLM/AI APIs.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

import numpy as np
import pytest
from fastapi.testclient import TestClient

from src.brain.long_term_memory import LongTermMemoryStore
from src.evaluation.online_corpus_fetcher import (
    _is_fetched_doc_relevant_to_query,
    clean_online_search_query,
)
from src.web.app import app


PHILOSOPHY_DOC = """# GIÁO TRÌNH TRIẾT HỌC MÁC - LÊNIN

## Chương 1: Chủ nghĩa duy vật biện chứng và phương pháp siêu hình
Chủ nghĩa duy vật biện chứng là học thuyết triết học khẳng định vật chất có trước, ý thức có sau, và xem xét sự vật trong mối liên hệ phổ biến, vận động và phát triển không ngừng.
Phương pháp biện chứng nhận thức đối tượng trong trạng thái vận động, biến đổi và chuyển hóa lẫn nhau theo các quy luật khách quan.
Ngược lại với phương pháp biện chứng, phương pháp siêu hình xem xét sự vật trong trạng thái cô lập, tĩnh tại, tách rời khỏi các mối liên hệ với các sự vật khác.
Phương pháp siêu hình chỉ thừa nhận sự biến đổi thuần túy về lượng mà phủ nhận sự biến đổi về chất và nguồn gốc tự thân bên trong của sự phát triển.

## Chương 2: Quy luật chuyển hóa từ những sự thay đổi về lượng thành những sự thay đổi về chất
Bước 1: Sự vật tích lũy dần dần về lượng trong giới hạn của độ mà chưa làm thay đổi ngay bản chất của sự vật.
Bước 2: Khi lượng tích lũy đạt tới điểm nút thì mâu thuẫn nội tại trở nên chín muồi để chuẩn bị cho sự biến đổi về chất.
Bước 3: Thực hiện bước nhảy làm chất cũ mất đi và chất mới ra đời với độ mới và điểm nút mới.
"""

DIABETES_DOC = """# PHÁC ĐỒ CHẨN ĐOÁN VÀ ĐIỀU TRỊ ĐÁI THÁO ĐƯỜNG TÝP 2

## 1. Tiêu chuẩn chẩn đoán
Đái tháo đường týp 2 được chẩn đoán khi nồng độ đường huyết lúc đói lớn hơn hoặc bằng 7.0 mmol/L hoặc HbA1c từ 6.5% trở lên sau ít nhất 8 giờ nhịn ăn.
Nghiệm pháp dung nạp glucose đường uống xác định chẩn đoán khi đường huyết sau 2 giờ đạt từ 11.1 mmol/L trở lên.
Bệnh nhân thường đi kèm tình trạng kháng insulin tại mô ngoại vi và suy giảm tương đối tiết insulin của tế bào beta tuyến tụy.

## 2. Nguyên tắc điều trị
Metformin là thuốc lựa chọn hàng đầu trong điều trị đái tháo đường týp 2 nếu không có chống chỉ định suy thận nặng.
Người bệnh cần kiểm soát chế độ dinh dưỡng tiết chế tinh bột nhanh và duy trì vận động thể lực tối thiểu 150 phút mỗi tuần.
"""

TOPIC_SPEAK_DOC = """# IELTS SPEAKING PART 2 TOPICS

## Topic 1: Describe a time when you had to wait in a long line
You should say where you were and why you were waiting in that long queue.
Last summer I went to the central hospital for a routine health checkup early in the morning.
Hundreds of patients were already standing in front of the registration counter because the electronic ticketing system was temporarily under maintenance.
To pass the time patiently, I listened to an academic podcast on my headphones and reviewed my study flashcards.
Eventually after forty-five minutes, the staff opened two extra counters and processed everyone smoothly.

## Topic 10: Describe a piece of technology you find hard to use
Smart home automation hubs can sometimes feel overly complicated when configuring custom wireless routines across different brands.
"""

HCM_DOC = """# TIỂU SỬ CHỦ TỊCH HỒ CHÍ MINH

## 1. Quê hương và thời niên thiếu
Chủ tịch Hồ Chí Minh sinh ngày 19 tháng 5 năm 1890 tại làng Sen, xã Kim Liên, huyện Nam Đàn, tỉnh Nghệ An.
Năm 1911, Người rời bến cảng Nhà Rồng ra đi tìm đường cứu nước, mở ra hành trình giải phóng dân tộc Việt Nam.
"""

RAILWAY_DOC = """# QUY HOẠCH TUYẾN ĐƯỜNG SẮT TỐC ĐỘ CAO BẮC - NAM

## 1. Thông số kỹ thuật chủ đạo
Tuyến đường sắt tốc độ cao trên trục Bắc - Nam là dự án hạ tầng giao thông chiến lược quốc gia đi qua 20 tỉnh và thành phố từ Hà Nội đến Thành phố Hồ Chí Minh.
Chiều dài toàn tuyến khoảng 1.541 km với khổ đường đôi 1.435 mm điện khí hóa và tốc độ thiết kế 350 km/h.
Các phương thức khai thác trên tuyến bao gồm:
- Tàu khách tốc độ cao chạy suốt giữa các trung tâm kinh tế lớn.
- Tàu khách liên vùng phục vụ kết nối các đô thị dọc hành lang Bắc - Nam.
"""


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


# ==============================================================================
# 1. KIỆT BUG #1: Philosophy & Medical Quiz Generation (Zero Wrong Physics/Chem)
# ==============================================================================

def test_kiet_bug1_philosophy_and_medical_exercises_never_hallucinate_physics_or_chem(client: TestClient):
    created_docs: List[str] = []
    created_sessions: List[str] = []
    try:
        r_phil = client.post(
            "/api/documents/raw",
            json={"title": "Triet Hoc Mac Lenin", "text": PHILOSOPHY_DOC},
        )
        assert r_phil.status_code == 200
        phil_id = r_phil.json()["document_id"]
        created_docs.append(phil_id)

        r_med = client.post(
            "/api/documents/raw",
            json={"title": "Phac Do Dai Thao Duong", "text": DIABETES_DOC},
        )
        assert r_med.status_code == 200
        med_id = r_med.json()["document_id"]
        created_docs.append(med_id)

        # Session A: Philosophy exercises (Online ON + Offline fallback)
        s_phil = client.post(
            "/api/chat/sessions",
            json={"title": "Test Philosophy Quiz", "document_ids": [phil_id]},
        ).json()["session_id"]
        created_sessions.append(s_phil)

        for q_text in ("bài tập về duy vật biện chứng", "cho tôi bài tập về siêu hình"):
            resp = client.post(
                f"/api/chat/sessions/{s_phil}/messages",
                json={"query": q_text, "allow_online_api": True},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["refused"] is False
            ans = data["answer"]
            # Must generate grounded MCQ options + collapsible answer key
            assert "Câu 1" in ans and "A." in ans and "B." in ans
            assert "Đáp án kiểm tra:" in ans
            # Must NEVER hallucinate unrelated Physics / Chemistry formulas
            assert "v = s/t" not in ans and "v = s / t" not in ans
            assert "C_M = n/V" not in ans and "C_M = n / V" not in ans
            # Practice generation answers carry no source footer
            assert "### Nguồn tham khảo" not in ans

        # Also test bare "cho tôi bài tập đi" in Offline mode -> grounded quiz instead of random "tập" match
        resp_bare_off = client.post(
            f"/api/chat/sessions/{s_phil}/messages",
            json={"query": "cho tôi bài tập đi", "allow_online_api": False},
        )
        assert resp_bare_off.status_code == 200
        d_bare = resp_bare_off.json()
        assert d_bare["refused"] is False
        assert "Câu 1" in d_bare["answer"]
        assert "Offline" in d_bare["answer"]

        # Session B: Diabetes medical doc containing "7.0 mmol/L" and "6.5%" must NOT trigger C_M = n/V or interest formula
        s_med = client.post(
            "/api/chat/sessions",
            json={"title": "Test Medical Quiz", "document_ids": [med_id]},
        ).json()["session_id"]
        created_sessions.append(s_med)

        resp_med = client.post(
            f"/api/chat/sessions/{s_med}/messages",
            json={"query": "cho tôi thêm bài tập đi", "allow_online_api": True},
        )
        assert resp_med.status_code == 200
        d_med = resp_med.json()
        assert d_med["refused"] is False
        ans_med = d_med["answer"]
        assert "Câu 1" in ans_med
        assert "C_M" not in ans_med and "v = s" not in ans_med
        assert any(k in ans_med.lower() for k in ("đái tháo đường", "mmol/l", "insulin", "metformin", "hba1c"))
    finally:
        for sid in created_sessions:
            client.delete(f"/api/chat/sessions/{sid}")
        for did in created_docs:
            client.delete(f"/api/documents/{did}")


# ==============================================================================
# 2. KIỆT BUG #2: Multilingual Section Navigation ("tóm gọn / đoạn tiếp theo / phần còn lại của topic 1")
# ==============================================================================

def test_kiet_bug2_topic_speak_section_summary_and_continuation_navigation(client: TestClient):
    created_docs: List[str] = []
    created_sessions: List[str] = []
    try:
        r_doc = client.post(
            "/api/documents/raw",
            json={"title": "Topic Speak Practice", "text": TOPIC_SPEAK_DOC},
        )
        assert r_doc.status_code == 200
        doc_id = r_doc.json()["document_id"]
        created_docs.append(doc_id)

        sid = client.post(
            "/api/chat/sessions",
            json={"title": "Topic Speak Nav", "document_ids": [doc_id]},
        ).json()["session_id"]
        created_sessions.append(sid)

        # Turn 1: "giúp tôi tóm gọn topic 1" (Vietnamese command on English section)
        r_sum = client.post(
            f"/api/chat/sessions/{sid}/messages",
            json={"query": "giúp tôi tóm gọn topic 1"},
        )
        assert r_sum.status_code == 200
        d_sum = r_sum.json()
        assert d_sum["refused"] is False
        assert "Topic 1" in d_sum["answer"] or "wait" in d_sum["answer"].lower() or "hospital" in d_sum["answer"].lower()
        assert "Topic 10" not in d_sum["answer"] and "Smart home" not in d_sum["answer"]

        # Turn 2: "cho tôi đoạn tiếp theo của topic 1"
        r_next = client.post(
            f"/api/chat/sessions/{sid}/messages",
            json={"query": "cho tôi đoạn tiếp theo của topic 1"},
        )
        assert r_next.status_code == 200
        d_next = r_next.json()
        assert d_next["refused"] is False
        assert "Topic 10" not in d_next["answer"] and "Smart home" not in d_next["answer"]
        assert any(w in d_next["answer"].lower() for w in ("hospital", "patients", "podcast", "forty-five", "counters", "queue"))

        # Turn 3: "cho tôi phần còn lại của topic 1"
        r_rest = client.post(
            f"/api/chat/sessions/{sid}/messages",
            json={"query": "cho tôi phần còn lại của topic 1"},
        )
        assert r_rest.status_code == 200
        d_rest = r_rest.json()
        assert d_rest["refused"] is False
        assert "Topic 10" not in d_rest["answer"] and "Smart home" not in d_rest["answer"]

        # Non-existent section must still refuse cleanly
        r_missing = client.post(
            f"/api/chat/sessions/{sid}/messages",
            json={"query": "cho tôi phần còn lại của topic 99"},
        )
        assert r_missing.status_code == 200
        assert r_missing.json()["refused"] is True
    finally:
        for sid in created_sessions:
            client.delete(f"/api/chat/sessions/{sid}")
        for did in created_docs:
            client.delete(f"/api/documents/{did}")


# ==============================================================================
# 3. KIỆT BUG #3: Diacritic-Strict Online Filter & Multi-Doc Citation Sync
# ==============================================================================

def test_kiet_bug3_online_diacritic_filter_and_multidoc_citation_sync(client: TestClient):
    # Part A: "triết học" must NOT match "triệt căn ung thư tuyến tiền liệt"
    q_raw = "cho tôi tài liệu về phần triết học"
    cleaned = clean_online_search_query(q_raw)
    assert "triết học" in cleaned.lower()
    assert "cho tôi" not in cleaned.lower()

    wrong_prostate_doc = {
        "title": "Tái phát sinh hóa sau điều trị triệt căn ung thư tuyến tiền liệt",
        "text": "Nghiên cứu đánh giá tỷ lệ tái phát sinh hóa sau phẫu thuật triệt căn ung thư tuyến tiền liệt.",
    }
    right_phil_doc = {
        "title": "Triết học Mác - Lênin và phép biện chứng duy vật",
        "text": "Triết học nghiên cứu những quy luật vận động và phát triển chung nhất của tự nhiên, xã hội và tư duy.",
    }
    assert _is_fetched_doc_relevant_to_query(q_raw, wrong_prostate_doc["title"], wrong_prostate_doc["text"]) is False
    assert _is_fetched_doc_relevant_to_query(q_raw, right_phil_doc["title"], right_phil_doc["text"]) is True

    # Part B: Multi-doc session (HCM + Railway) -> asking about Railway must cite Railway, NEVER HCM
    created_docs: List[str] = []
    created_sessions: List[str] = []
    try:
        d_hcm = client.post("/api/documents/raw", json={"title": "Hồ Chí Minh", "text": HCM_DOC}).json()["document_id"]
        created_docs.append(d_hcm)
        d_rail = client.post(
            "/api/documents/raw",
            json={"title": "Quy hoạch Đường sắt tốc độ cao Bắc - Nam", "text": RAILWAY_DOC},
        ).json()["document_id"]
        created_docs.append(d_rail)

        sid = client.post(
            "/api/chat/sessions",
            json={"title": "MultiDoc Citation Sync", "document_ids": [d_hcm, d_rail]},
        ).json()["session_id"]
        created_sessions.append(sid)

        # Query 1: Direct factual lookup on Railway in multi-doc session
        resp = client.post(
            f"/api/chat/sessions/{sid}/messages",
            json={"query": "Tốc độ thiết kế và chiều dài toàn tuyến đường sắt tốc độ cao Bắc - Nam là bao nhiêu?"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["refused"] is False
        assert "350 km/h" in data["answer"] or "1.541 km" in data["answer"]
        assert len(data["citations"]) >= 1
        assert all(c["document_id"] == d_rail for c in data["citations"])
        assert "Hồ Chí Minh —" not in data["answer"].split("### Nguồn tham khảo")[-1]

        # Query 2: KnowledgeBank DEFINITION_AND_TYPES synthesis on Railway in multi-doc session
        resp_kb = client.post(
            f"/api/chat/sessions/{sid}/messages",
            json={"query": "Quy hoạch đường sắt tốc độ cao Bắc - Nam có bao nhiêu loại phương thức khai thác?"},
        )
        assert resp_kb.status_code == 200
        data_kb = resp_kb.json()
        assert data_kb["refused"] is False
        assert "Tàu khách" in data_kb["answer"]
        assert len(data_kb["citations"]) >= 1
        assert all(c["document_id"] == d_rail for c in data_kb["citations"])
        assert "Hồ Chí Minh —" not in data_kb["answer"].split("### Nguồn tham khảo")[-1]
    finally:
        for sid in created_sessions:
            client.delete(f"/api/chat/sessions/{sid}")
        for did in created_docs:
            client.delete(f"/api/documents/{did}")


# ==============================================================================
# 4. BRAIN V9: 3-Layer Persistent Long-Term Memory & Certified Exact Unlearning
# ==============================================================================

def test_brain_v9_long_term_memory_persistence_antipoisoning_and_exact_unlearning(
    tmp_path: Path, client: TestClient
):
    ltm_dir = tmp_path / "ltm_test"
    store1 = LongTermMemoryStore(storage_dir=str(ltm_dir))

    # Assimilate doc_A and doc_B; verify baseline snapshot when only doc_B exists
    ltm_only_b_dir = tmp_path / "ltm_only_b"
    store_only_b = LongTermMemoryStore(storage_dir=str(ltm_only_b_dir))
    passages_b = [
        {"passage_id": "B_P1", "document_id": "DOC_B", "section_title": "Đái tháo đường", "text": DIABETES_DOC}
    ]
    store_only_b.assimilate_document("DOC_B", "Phác đồ ĐTĐ", DIABETES_DOC, passages_b)
    g_expected = store_only_b.ridge.G.data.copy()
    b_expected = store_only_b.ridge.B.data.copy()

    passages_a = [
        {"passage_id": "A_P1", "document_id": "DOC_A", "section_title": "Duy vật biện chứng", "text": PHILOSOPHY_DOC}
    ]
    res_a = store1.assimilate_document("DOC_A", "Triết học", PHILOSOPHY_DOC, passages_a)
    store1.assimilate_document("DOC_B", "Phác đồ ĐTĐ", DIABETES_DOC, passages_b)
    assert res_a["concepts_added"] >= 1

    # Anti-poisoning: refused or unfaithful or clarification turns MUST NOT enter episodic_qa
    assert store1.record_verified_interaction(
        session_id="S1",
        raw_query="Cách nấu phở bò?",
        effective_query="Cách nấu phở bò?",
        answer="Xin lỗi...",
        citations=[],
        refused=True,
    ) is False
    assert store1.record_verified_interaction(
        session_id="S1",
        raw_query="Ảo giác",
        effective_query="Ảo giác",
        answer="Không trung thực",
        citations=[{"document_id": "DOC_A", "passage_id": "A_P1", "text": "test"}],
        refused=False,
        is_faithful=False,
    ) is False
    assert len(store1.episodic_qa) == 0

    # Valid verified interaction IS recorded and teaches associative link
    assert store1.record_verified_interaction(
        session_id="S1",
        raw_query="Học thuyết xem sự vật luôn vận động liên hệ phổ biến gọi là gì?",
        effective_query="Chủ nghĩa duy vật biện chứng là gì?",
        answer="Chủ nghĩa duy vật biện chứng xem xét sự vật trong mối liên hệ phổ biến [1].",
        citations=[{"document_id": "DOC_A", "passage_id": "A_P1", "section_title": "Chương 1", "text": PHILOSOPHY_DOC}],
        refused=False,
        is_faithful=True,
    ) is True
    # Ask a second time so learner profile reaches >= 2 inquiries
    store1.record_verified_interaction(
        session_id="S2",
        raw_query="Giải thích chủ nghĩa duy vật biện chứng",
        effective_query="Chủ nghĩa duy vật biện chứng là gì?",
        answer="Chủ nghĩa duy vật biện chứng...",
        citations=[{"document_id": "DOC_A", "passage_id": "A_P1", "section_title": "Chương 1", "text": PHILOSOPHY_DOC}],
        refused=False,
        is_faithful=True,
    )
    assert len(store1.episodic_qa) == 2

    # Reload fresh instance from disk -> persistence verified
    store2 = LongTermMemoryStore(storage_dir=str(ltm_dir))
    assert len(store2.episodic_qa) == 2
    assert "DOC_A" in store2.assimilated_docs and "DOC_B" in store2.assimilated_docs
    assert store2.get_learner_hint("Chủ nghĩa duy vật biện chứng", ["DOC_A"]) is not None
    # Zero cross-doc leakage: learner hint and boosts for DOC_A must NEVER leak into DOC_B
    assert store2.get_learner_hint("Chủ nghĩa duy vật biện chứng", ["DOC_B"]) is None
    boosts_a = store2.recall_associative_boost(
        "học thuyết xem sự vật luôn vận động liên hệ phổ biến",
        passages_a + passages_b,
        allowed_document_ids=["DOC_A"],
    )
    assert boosts_a.get("A_P1", 0.0) > 1.0
    assert "B_P1" not in boosts_a

    # Certified Bit-Exact Unlearning of DOC_A -> restores exact int64 fixed-point G, B of DOC_B alone!
    unlearn_res = store2.unlearn_document("DOC_A")
    assert unlearn_res["ridge_unlearned"] is True
    assert unlearn_res["removed_episodic"] == 2
    assert "DOC_A" not in store2.concepts_by_doc
    assert len(store2.episodic_qa) == 0
    assert np.array_equal(store2.ridge.G.data, g_expected)
    assert np.array_equal(store2.ridge.B.data, b_expected)

    # Also verify HTTP endpoint GET /api/memory/long-term/status
    r_status = client.get("/api/memory/long-term/status")
    assert r_status.status_code == 200
    st = r_status.json()
    assert st["status"] == "active"
    assert "concepts_learned" in st and "episodic_qa_count" in st


# ==============================================================================
# 5. BRAIN V9: Pedagogical Markdown Tables, Step Flows & Auto-Thinking Mode
# ==============================================================================

def test_brain_v9_pedagogical_comparison_table_step_flow_and_auto_thinking(client: TestClient):
    created_docs: List[str] = []
    created_sessions: List[str] = []
    try:
        r_phil = client.post(
            "/api/documents/raw",
            json={"title": "Triet Hoc So Sanh Va Quy Trinh", "text": PHILOSOPHY_DOC},
        )
        assert r_phil.status_code == 200
        phil_id = r_phil.json()["document_id"]
        created_docs.append(phil_id)

        sid = client.post(
            "/api/chat/sessions",
            json={"title": "Pedagogical & Auto-Thinking", "document_ids": [phil_id]},
        ).json()["session_id"]
        created_sessions.append(sid)

        # 1. Comparison query with thinking_mode="auto" -> promotes to "deep" + renders Markdown table
        r_cmp = client.post(
            f"/api/chat/sessions/{sid}/messages",
            json={
                "query": "So sánh phương pháp biện chứng và phương pháp siêu hình khác nhau như thế nào?",
                "thinking_mode": "auto",
            },
        )
        assert r_cmp.status_code == 200
        d_cmp = r_cmp.json()
        assert d_cmp["refused"] is False
        assert d_cmp["thinking_mode"] == "deep"
        assert d_cmp["diagnostics"]["auto_thinking_promoted"] is True
        assert d_cmp["reasoning_trace"]["mode"] == "deep"
        assert "| Tiêu chí |" in d_cmp["answer"]

        # 2. Step-by-step process query -> renders structured Bước 1..3 flow
        r_steps = client.post(
            f"/api/chat/sessions/{sid}/messages",
            json={
                "query": "Trình bày các bước chuyển hóa từ lượng thành chất trong tài liệu?",
                "thinking_mode": "fast",
            },
        )
        assert r_steps.status_code == 200
        d_steps = r_steps.json()
        assert d_steps["refused"] is False
        assert "Bước 1" in d_steps["answer"] and "Bước 2" in d_steps["answer"]

        # 3. Omitted thinking_mode in raw API stays "fast" (0% API regression)
        r_def = client.post(
            f"/api/chat/sessions/{sid}/messages",
            json={"query": "Chủ nghĩa duy vật biện chứng là gì?"},
        )
        assert r_def.status_code == 200
        assert r_def.json()["thinking_mode"] == "fast"
    finally:
        for sid in created_sessions:
            client.delete(f"/api/chat/sessions/{sid}")
        for did in created_docs:
            client.delete(f"/api/documents/{did}")
