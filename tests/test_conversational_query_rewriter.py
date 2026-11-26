# -*- coding: utf-8 -*-
"""
Tests for the 7 Conversational Query Rewriting & Clarification Rules:
1. Preserves user intent and scope.
2. Replaces pronouns/references ("nó", "cái đó", "ý 2", "phần trên", "cái đầu", "chúng") when history resolves them.
3. Carries forward active scope/condition constraints ("trong chương 2", "ở điều kiện chuẩn").
4-5. Outputs only a standalone search query (never answers or invents facts).
6. Leaves standalone queries intact; document-level "tài liệu này" / "cho biết mục 3" never falsely ask clarification.
7. Emits NEED_CLARIFICATION (and polite chat clarification response) when referent is missing, out of range, or ambiguous across 2+ prior entities.
"""

from fastapi.testclient import TestClient

from src.web.app import app
from src.web.session_manager import NEED_CLARIFICATION, rewrite_query_text


client = TestClient(app)


def test_rewrite_pronouns_positional_and_prior_constraints():
    """Rules 1, 2, 3: Resolves 'nó', 'cái đó', 'phần trên', 'ý 2' and preserves prior scope constraints."""
    history = [
        {"role": "user", "content": "Trong chương 2, chất khử là gì?"},
        {
            "role": "assistant",
            "content": (
                "- **Ý 1:** Chất khử là chất nhường electron cho chất khác [1].\n"
                "- **Ý 2:** Số oxi hóa của chất khử tăng lên sau phản ứng [1]."
            ),
        },
    ]

    # "cái đó" -> "chất khử" + preserves "Trong chương 2"
    q_cai_do = rewrite_query_text(history, "Cái đó có vai trò gì trong phản ứng?")
    assert "chất khử" in q_cai_do.lower()
    assert "trong chương 2" in q_cai_do.lower()
    assert "cái đó" not in q_cai_do.lower()

    # "phần trên" -> resolved to prior subject
    q_phan_tren = rewrite_query_text(history, "Cho ví dụ minh họa về phần trên")
    assert "chất khử" in q_phan_tren.lower()

    # "ý 2" -> resolved to bullet #2 content (preserving "Cho ví dụ về" intent!)
    q_y2 = rewrite_query_text(history, "Cho ví dụ về ý 2")
    assert "số oxi hóa của chất khử tăng lên" in q_y2.lower()
    assert "cho ví dụ về" in q_y2.lower()


def test_standalone_and_document_self_reference_not_hijacked():
    """Rule 6: Standalone queries and 'tài liệu này' / 'mục 3' stay standalone even on empty history."""
    assert rewrite_query_text([], "Tóm tắt nội dung chính của tài liệu này") == "Tóm tắt nội dung chính của tài liệu này"
    assert rewrite_query_text([], "Cho biết mục 3") == "Cho biết mục 3"
    assert rewrite_query_text([], "Thuật toán SA-CMS hoạt động như thế nào?") == "Thuật toán SA-CMS hoạt động như thế nào?"


def test_need_clarification_on_missing_out_of_range_and_ambiguous_multi_entity():
    """Rule 7: Returns NEED_CLARIFICATION instead of guessing when referent cannot be uniquely determined."""
    # 1. Empty history + dangling pronoun
    assert rewrite_query_text([], "Nó hoạt động như thế nào?") == NEED_CLARIFICATION
    assert rewrite_query_text([], "Giải thích kỹ hơn cái đó") == NEED_CLARIFICATION
    assert rewrite_query_text([], "Ý 2 nghĩa là gì?") == NEED_CLARIFICATION

    # 2. Multi-entity prior turn: singular "nó" is ambiguous, while "cái đầu", "cái sau", "chúng" resolve cleanly!
    multi_hist = [
        {"role": "user", "content": "Giao thức TCP là gì và giao thức UDP là gì?"},
        {
            "role": "assistant",
            "content": (
                "- **Ý 1:** Giao thức TCP truyền dữ liệu tin cậy có kết nối [1].\n"
                "- **Ý 2:** Giao thức UDP truyền dữ liệu không kết nối tốc độ cao [2]."
            ),
        },
    ]
    assert rewrite_query_text(multi_hist, "Nó có đảm bảo thứ tự gói tin không?") == NEED_CLARIFICATION
    assert rewrite_query_text(multi_hist, "Giải thích ý 5") == NEED_CLARIFICATION

    q_first = rewrite_query_text(multi_hist, "Cái đầu dùng trong trường hợp nào?")
    assert "tcp" in q_first.lower() and "udp" not in q_first.lower()

    q_second = rewrite_query_text(multi_hist, "Cái sau dùng trong trường hợp nào?")
    assert "udp" in q_second.lower() and "tcp" not in q_second.lower()

    q_both = rewrite_query_text(multi_hist, "Chúng khác nhau ở điểm nào?")
    assert "tcp" in q_both.lower() and "udp" in q_both.lower()


def test_chat_endpoint_clarification_flow_e2e():
    """Verifies E2E /api/chat/sessions/{sid}/messages returns CLARIFICATION_NEEDED without hallucinating."""
    doc_text = (
        "## 1. Giao thức TCP\n"
        "Giao thức TCP đảm bảo truyền dữ liệu tin cậy có kết nối.\n\n"
        "## 2. Giao thức UDP\n"
        "Giao thức UDP truyền dữ liệu không kết nối với độ trễ thấp."
    )
    c_doc = client.post("/api/documents/raw", json={"title": "net.txt", "text": doc_text})
    assert c_doc.status_code == 200
    doc_id = c_doc.json()["document_id"]

    try:
        c_sess = client.post("/api/chat/sessions", json={"title": "Clarify E2E", "document_ids": [doc_id]})
        assert c_sess.status_code == 200
        sid = c_sess.json()["session_id"]
        try:
            # Turn 1 on fresh session: dangling "Cái đó là gì?" -> CLARIFICATION_NEEDED
            r1 = client.post(
                f"/api/chat/sessions/{sid}/messages",
                json={"query": "Cái đó là gì?", "answer_mode": "balanced", "allow_online_api": False},
            )
            assert r1.status_code == 200
            d1 = r1.json()
            assert d1.get("effective_query") == NEED_CLARIFICATION
            assert d1.get("routing") == "CLARIFICATION_NEEDED"
            assert "chưa xác định được đối tượng" in d1.get("answer", "").lower()

            # Turn 2: Ask compound question about TCP and UDP
            r2 = client.post(
                f"/api/chat/sessions/{sid}/messages",
                json={"query": "Giao thức TCP là gì và giao thức UDP là gì?", "answer_mode": "balanced", "allow_online_api": False},
            )
            assert r2.status_code == 200
            assert not r2.json().get("refused", False)

            # Turn 3: Singular "Nó có kết nối không?" after TCP+UDP -> asks user whether they mean TCP or UDP!
            r3 = client.post(
                f"/api/chat/sessions/{sid}/messages",
                json={"query": "Nó có kết nối không?", "answer_mode": "balanced", "allow_online_api": False},
            )
            assert r3.status_code == 200
            d3 = r3.json()
            assert d3.get("effective_query") == NEED_CLARIFICATION
            assert d3.get("routing") == "CLARIFICATION_NEEDED"
            ans3 = d3.get("answer", "").lower()
            assert "tcp" in ans3 and "udp" in ans3
        finally:
            client.delete(f"/api/chat/sessions/{sid}")
    finally:
        client.delete(f"/api/documents/{doc_id}")
