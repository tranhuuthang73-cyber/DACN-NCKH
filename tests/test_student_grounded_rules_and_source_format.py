# -*- coding: utf-8 -*-
"""
Tests verifying the 8 student-friendly Grounded QA Rules & Hybrid Source Format:
1-2 & 7: Natural Vietnamese paraphrasing & no verbatim copying of overly long paragraphs,
         while preserving technical terms, symbols, and numbers.
3-5: Strict grounding + polite student refusal ("Xin lỗi, tài liệu hiện tại chưa cung cấp đủ thông tin...")
     while remaining compatible with legacy refusal substring checks.
6: Multi-part queries answered point-by-point (**Ý 1:**, **Ý 2:**).
8 & Source format: Inline [1] clickable citations + [Nguồn: tên_file, trang X, ID: DOC::P001] tags.
"""

from fastapi.testclient import TestClient

from src.brain.grounded_explainer import (
    compress_clause,
    format_student_source_tag,
    paraphrase_academic_vietnamese,
)
from src.hybrid_qa.chunker import DocumentChunker
from src.hybrid_qa.document_store import DocumentRecord
from src.web.app import app


client = TestClient(app)


def test_paraphrase_and_anti_long_copy_preserve_terms():
    """Rules 1, 2, 7: Rewrites stiff phrasing & trims verbose secondary clauses while keeping domain terms."""
    raw = (
        "Cụ thể hơn, thuật toán SA-CMS được sử dụng với mục đích nhằm tối ưu hóa bộ nhớ dài hạn "
        "với độ phức tạp O(log N) và đạt độ chính xác 96,4%; qua đó hệ thống còn được thảo luận rộng rãi "
        "trong nhiều hội thảo nghiên cứu học thuật tổng quan khác nhau trên thế giới."
    )
    comp = compress_clause(raw, preserve_examples=False)
    assert "dùng để" in comp
    assert "SA-CMS" in comp
    assert "O(log N)" in comp
    assert "96,4%" in comp
    # Must NOT copy the long trailing secondary filler clause after ';'
    assert "hội thảo nghiên cứu học thuật" not in comp
    assert len(comp.split()) <= 38


def test_chunker_extracts_page_number_and_source_tag_format():
    """Source Format Rule: Chunker records page_number from === Page 12 === and formats [Nguồn: file, trang 12, ID: ...]."""
    pdf_like_text = (
        "=== Page 1 ===\n"
        "Giới thiệu tổng quan về môn học Mạng máy tính.\n\n"
        "=== Page 12 ===\n"
        "## Giao thức TCP\n"
        "Giao thức TCP đảm bảo truyền dữ liệu tin cậy theo cơ chế bắt tay 3 bước (Three-way handshake)."
    )
    doc = DocumentRecord(
        document_id="DOC_NET_PDF",
        version=1,
        title="bai_giang_mang.pdf",
        raw_text=pdf_like_text,
        metadata={"filename": "bai_giang_mang.pdf"},
    )
    passages = DocumentChunker().chunk_document(doc)
    tcp_passages = [p for p in passages if "Three-way handshake" in p.text]
    assert len(tcp_passages) == 1
    p_tcp = tcp_passages[0]
    assert p_tcp.metadata.get("page_number") == 12

    tag = format_student_source_tag(
        {
            "filename": p_tcp.metadata.get("filename"),
            "document_title": doc.title,
            "page_number": p_tcp.metadata.get("page_number"),
            "passage_id": p_tcp.passage_id,
        }
    )
    assert tag == f"[Nguồn: bai_giang_mang.pdf, trang 12, ID: {p_tcp.passage_id}]"


def test_chat_e2e_source_tag_multi_part_points_and_polite_refusal():
    """Verifies E2E chat output includes [1] + [Nguồn: ..., trang 12, ID: ...], **Ý 1/2**, and polite refusal."""
    doc_text = (
        "=== Page 12 ===\n"
        "## 1. Giao thức TCP\n"
        "Giao thức TCP được sử dụng với mục đích nhằm đảm bảo truyền gói tin tin cậy và đúng thứ tự.\n\n"
        "=== Page 15 ===\n"
        "## 2. Giao thức UDP\n"
        "Giao thức UDP truyền dữ liệu không kết nối giúp giảm độ trễ cho truyền phát thời gian thực."
    )
    c_doc = client.post("/api/documents/raw", json={"title": "mang_may_tinh.pdf", "text": doc_text})
    assert c_doc.status_code == 200
    doc_id = c_doc.json()["document_id"]

    try:
        c_sess = client.post("/api/chat/sessions", json={"title": "Student QA Rules", "document_ids": [doc_id]})
        assert c_sess.status_code == 200
        sid = c_sess.json()["session_id"]
        try:
            # 1) Multi-part question -> structured **Ý 1:** / **Ý 2:** + [1] + [Nguồn: mang_may_tinh.pdf, trang 12, ID: ...]
            r_multi = client.post(
                f"/api/chat/sessions/{sid}/messages",
                json={
                    "query": "Giao thức TCP là gì và giao thức UDP là gì?",
                    "answer_mode": "balanced",
                    "allow_online_api": False,
                },
            )
            assert r_multi.status_code == 200
            d_multi = r_multi.json()
            ans_multi = d_multi.get("answer", "")
            assert not d_multi.get("refused", False)
            assert "**Ý 1:**" in ans_multi and "**Ý 2:**" in ans_multi
            assert "[1]" in ans_multi
            assert "[Nguồn: mang_may_tinh.pdf, trang 12, ID:" in ans_multi
            assert "trang 15" in ans_multi

            # 2) Unanswerable question -> polite student refusal + legacy compatible substring
            r_ref = client.post(
                f"/api/chat/sessions/{sid}/messages",
                json={
                    "query": "Công thức nấu phở bò gia truyền Hà Nội gồm những gia vị nào?",
                    "answer_mode": "concise",
                    "allow_online_api": False,
                },
            )
            assert r_ref.status_code == 200
            d_ref = r_ref.json()
            ans_ref = d_ref.get("answer", "")
            assert d_ref.get("refused") is True
            assert "Xin lỗi, tài liệu hiện tại chưa cung cấp đủ thông tin để trả lời chính xác câu hỏi này." in ans_ref
            assert "Không tìm thấy đủ thông tin trong tài liệu để trả lời chắc chắn" in ans_ref
        finally:
            client.delete(f"/api/chat/sessions/{sid}")
    finally:
        client.delete(f"/api/documents/{doc_id}")
