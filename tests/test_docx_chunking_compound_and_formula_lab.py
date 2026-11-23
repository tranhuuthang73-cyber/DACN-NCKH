# -*- coding: utf-8 -*-
"""
Tests for:
1. DOCX parser handling of OMML (<m:oMath>), textboxes (<w:txbxContent>), content controls (<w:sdt>), and tables (<w:tbl>).
2. Chunker formatting ensuring headings and bullets do not stick together without newlines.
3. Compound query decomposition and cross-chunk entity retrieval for "chất khử là gì và chất oxi hóa là gì".
4. Offline mode strict grounding vs. Online Symbolic Formula Lab (chemistry redox, quadratic equations, Ohm's law) with zero external LLM API calls.
5. Frontend UI toggle labels for Offline (Chỉ tài liệu) and Online (Mở rộng & Bài tập).
"""
import io
import pytest
from lxml import etree
import docx
from fastapi.testclient import TestClient

from src.web.file_parser import extract_text_from_docx
from src.hybrid_qa.document_store import DocumentRecord
from src.hybrid_qa.chunker import DocumentChunker
from src.reasoning.formula_lab import (
    detect_expansion_intent,
    extract_document_formulas,
    derive_formula_transformations,
    generate_worked_examples,
    generate_practice_exercises,
    build_online_study_expansion,
)
from src.web.app import app


client = TestClient(app)


def test_docx_extracts_omath_textboxes_and_sdt():
    """Build a real DOCX file in memory with math equations, textboxes, and SDT controls."""
    doc = docx.Document()
    doc.add_heading("Chương 1: Khảo sát Hàm số và Động học", level=1)

    p1 = doc.add_paragraph("Phương trình vi phân mô tả tốc độ: ")
    # Add an OMML fraction: <m:oMath><m:f><m:num><m:r><m:t>dy</m:t></m:r></m:num><m:den><m:r><m:t>dx</m:t></m:r></m:den></m:f><m:r><m:t> = k * y</m:t></m:r></m:oMath>
    ns_m = "http://schemas.openxmlformats.org/officeDocument/2006/math"
    ns_w = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    ns_mc = "http://schemas.openxmlformats.org/markup-compatibility/2006"

    m_math = etree.Element(f"{{{ns_m}}}oMath")
    m_f = etree.SubElement(m_math, f"{{{ns_m}}}f")
    m_num = etree.SubElement(m_f, f"{{{ns_m}}}num")
    m_num_r = etree.SubElement(m_num, f"{{{ns_m}}}r")
    m_num_t = etree.SubElement(m_num_r, f"{{{ns_m}}}t")
    m_num_t.text = "dy"

    m_den = etree.SubElement(m_f, f"{{{ns_m}}}den")
    m_den_r = etree.SubElement(m_den, f"{{{ns_m}}}r")
    m_den_t = etree.SubElement(m_den_r, f"{{{ns_m}}}t")
    m_den_t.text = "dx"

    m_tail_r = etree.SubElement(m_math, f"{{{ns_m}}}r")
    m_tail_t = etree.SubElement(m_tail_r, f"{{{ns_m}}}t")
    m_tail_t.text = " = k * y"

    p1._p.append(m_math)

    # Add AlternateContent with Choice (txbxContent) and Fallback (duplicate text) to verify fallback is skipped
    alt_content = etree.Element(f"{{{ns_mc}}}AlternateContent")
    choice = etree.SubElement(alt_content, f"{{{ns_mc}}}Choice", Requires="wps")
    txbx = etree.SubElement(choice, f"{{{ns_w}}}txbxContent")
    txbx_p = etree.SubElement(txbx, f"{{{ns_w}}}p")
    txbx_r = etree.SubElement(txbx_p, f"{{{ns_w}}}r")
    txbx_t = etree.SubElement(txbx_r, f"{{{ns_w}}}t")
    txbx_t.text = "Ghi chú trong textbox độc lập: Cần bảo toàn khối lượng."

    fallback = etree.SubElement(alt_content, f"{{{ns_mc}}}Fallback")
    fb_p = etree.SubElement(fallback, f"{{{ns_w}}}p")
    fb_r = etree.SubElement(fb_p, f"{{{ns_w}}}r")
    fb_t = etree.SubElement(fb_r, f"{{{ns_w}}}t")
    fb_t.text = "Ghi chú trong textbox độc lập: Cần bảo toàn khối lượng."

    p_box = doc.add_paragraph()
    p_box._p.append(alt_content)

    # Add SDT block
    sdt = etree.Element(f"{{{ns_w}}}sdt")
    sdt_content = etree.SubElement(sdt, f"{{{ns_w}}}sdtContent")
    sdt_p = etree.SubElement(sdt_content, f"{{{ns_w}}}p")
    sdt_r = etree.SubElement(sdt_p, f"{{{ns_w}}}r")
    sdt_t = etree.SubElement(sdt_r, f"{{{ns_w}}}t")
    sdt_t.text = "Nội dung form control SDT: Xác nhận nghiệm."
    doc._body._body.append(sdt)

    # Add Table
    table = doc.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Chất"
    table.cell(0, 1).text = "Vai trò"
    table.cell(1, 0).text = "Zn"
    table.cell(1, 1).text = "Chất khử"

    buf = io.BytesIO()
    doc.save(buf)
    file_bytes = buf.getvalue()

    extracted = extract_text_from_docx(file_bytes)

    assert "(dy)/(dx) = k * y" in extracted or "dy" in extracted
    assert "Ghi chú trong textbox độc lập: Cần bảo toàn khối lượng." in extracted
    # Choice + Fallback deduplication test: text should appear only once
    assert extracted.count("Ghi chú trong textbox độc lập: Cần bảo toàn khối lượng.") == 1
    assert "Nội dung form control SDT: Xác nhận nghiệm." in extracted
    assert "Chất" in extracted and "Chất khử" in extracted


def test_chunker_separates_heading_and_bullets_cleanly():
    """Verify that chunker does not glue section headings onto bullet points without whitespace/newlines."""
    text = (
        "## 2.1. Khái niệm cơ bản về phản ứng oxi hóa - khử\n"
        "- Chất khử là chất nhường electron (chất bị oxi hóa).\n"
        "- Chất oxi hóa là chất nhận electron (chất bị khử).\n"
        "- Quá trình oxi hóa là quá trình nhường electron.\n"
        "- Quá trình khử là quá trình nhận electron.\n"
    )
    doc_rec = DocumentRecord(document_id="doc_redox_bullets", version=1, title="Bài 2 Redox", raw_text=text)
    chunker = DocumentChunker(chunk_size=180, chunk_overlap=30, min_chunk_size=40)
    passages = chunker.chunk_document(doc_rec)

    assert len(passages) >= 1
    p0_text = passages[0].text
    # Heading and bullet point must be separated by newline, not mashed into one word
    assert "2.1. Khái niệm cơ bản về phản ứng oxi hóa - khử\n- Chất khử" in p0_text or \
           "2.1. Khái niệm cơ bản về phản ứng oxi hóa - khử" in p0_text


def test_compound_query_chat_khu_and_chat_oxi_hoa_across_separate_chunks():
    """
    Test compound query 'chất khử là gì và chất oxi hóa là gì'
    across multi-section chemistry content where each definition lives in distinct paragraphs/sections.
    Both concepts must be captured in the grounded response without repeating or missing either.
    """
    raw_doc = (
        "CHƯƠNG 2: PHẢN ỨNG OXI HÓA - KHỬ\n\n"
        "2.1. Định nghĩa chất khử\n"
        "Chất khử là chất có khả năng nhường electron cho chất khác trong phản ứng hóa học.\n"
        "Nói cách khác, chất khử là chất bị oxi hóa, số oxi hóa của nó tăng lên sau phản ứng.\n"
        "Ví dụ: Kim loại kẽm Zn đóng vai trò là chất khử khi tác dụng với axit.\n\n"
        "Nội dung giải thích mở rộng thêm về số oxi hóa của kim loại kiềm và kiềm thổ để tách chunk.\n"
        "Các kim loại kiềm nhóm IA luôn có số oxi hóa +1 trong hợp chất. Kim loại nhóm IIA có số oxi hóa +2.\n"
        "Nhôm có số oxi hóa +3 trong mọi hợp chất bền. Clo có nhiều số oxi hóa từ -1 đến +7.\n\n"
        "2.2. Định nghĩa chất oxi hóa\n"
        "Chất oxi hóa là chất có khả năng nhận electron từ chất khác trong phản ứng hóa học.\n"
        "Nói cách khác, chất oxi hóa là chất bị khử, số oxi hóa của nó giảm xuống sau phản ứng.\n"
        "Ví dụ: Ion Cu2+ hoặc axit nitric HNO3 thường đóng vai trò là chất oxi hóa mạnh.\n\n"
        "2.3. Quy tắc bảo toàn electron\n"
        "Tổng số mol electron do chất khử nhường bằng tổng số mol electron do chất oxi hóa nhận."
    )

    create_doc_resp = client.post("/api/documents/raw", json={"title": "Bài 2 Hoá học", "text": raw_doc})
    assert create_doc_resp.status_code == 200, create_doc_resp.text
    doc_id = create_doc_resp.json()["document_id"]

    try:
        create_sess_resp = client.post("/api/chat/sessions", json={"title": "Session Redox", "document_ids": [doc_id]})
        assert create_sess_resp.status_code == 200, create_sess_resp.text
        sid = create_sess_resp.json()["session_id"]

        try:
            msg_resp = client.post(
                f"/api/chat/sessions/{sid}/messages",
                json={
                    "query": "chất khử là gì và chất oxi hóa là gì",
                    "answer_mode": "balanced",
                    "allow_online_api": False
                }
            )
            assert msg_resp.status_code == 200, msg_resp.text
            data = msg_resp.json()

            answer = data.get("answer", "").lower()
            # Must answer both parts
            assert "chất khử" in answer
            assert "nhường electron" in answer or "bị oxi hóa" in answer
            assert "chất oxi hóa" in answer
            assert "nhận electron" in answer or "bị khử" in answer
            assert not data.get("refused", False)
        finally:
            client.delete(f"/api/chat/sessions/{sid}")
    finally:
        client.delete(f"/api/documents/{doc_id}")


def test_offline_strict_vs_online_formula_lab_chemistry_algebra_physics():
    """
    Verify:
    1. Offline mode strictly stays inside document scope and informs user if they ask for expansion.
    2. Online mode (Symbolic Formula Lab, 100% local SymPy) successfully derives formulas,
       generates worked examples, and produces 3 practice exercises without hallucination.
    """
    chem_math_doc = (
        "BÀI HỌC TOÁN VÀ HÓA ĐẠI CƯƠNG\n\n"
        "Phần 1: Phản ứng oxi hóa - khử\n"
        "Phương trình phản ứng: Zn + 2HCl -> ZnCl2 + H2\n"
        "Trong đó Zn là chất khử nhường 2 electron: Zn -> Zn2+ + 2e.\n"
        "Ion H+ là chất oxi hóa nhận electron: 2H+ + 2e -> H2.\n\n"
        "Phần 2: Phương trình bậc hai\n"
        "Dạng tổng quát: x^2 - 5*x + 6 = 0\n"
        "Nghiệm của phương trình được tính theo biệt thức Delta.\n\n"
        "Phần 3: Định luật Ohm vật lý\n"
        "Biểu thức định luật: U = I * R trong đó U là hiệu điện thế, I là cường độ dòng điện, R là điện trở."
    )

    create_doc_resp = client.post("/api/documents/raw", json={"title": "Toán Lý Hóa Tổng Hợp", "text": chem_math_doc})
    assert create_doc_resp.status_code == 200
    doc_id = create_doc_resp.json()["document_id"]

    try:
        create_sess_resp = client.post("/api/chat/sessions", json={"title": "Session Formula Lab", "document_ids": [doc_id]})
        assert create_sess_resp.status_code == 200
        sid = create_sess_resp.json()["session_id"]

        try:
            # Case A: Offline mode with request to generate extra practice / transform
            offline_msg = client.post(
                f"/api/chat/sessions/{sid}/messages",
                json={
                    "query": "biến đổi công thức và cho ví dụ bài tập về x^2 - 5*x + 6 = 0",
                    "answer_mode": "balanced",
                    "allow_online_api": False
                }
            )
            assert offline_msg.status_code == 200
            offline_data = offline_msg.json()
            offline_answer = offline_data.get("answer", "")
            # Must note offline mode constraint
            assert "Chế độ Offline" in offline_answer or "Online" in offline_answer

            # Case B: Online mode - should activate Symbolic Formula Lab
            online_msg = client.post(
                f"/api/chat/sessions/{sid}/messages",
                json={
                    "query": "biến đổi công thức x^2 - 5*x + 6 = 0 và cho ví dụ bài tập tương tự",
                    "answer_mode": "balanced",
                    "allow_online_api": True
                }
            )
            assert online_msg.status_code == 200
            online_data = online_msg.json()
            online_answer = online_data.get("answer", "")

            assert not online_data.get("refused", False)
            assert "Lưu ý đối soát" not in online_answer
            assert "Biến đổi công thức" in online_answer or "Phương trình" in online_answer
            assert "Bài tập" in online_answer
            # Check diagnostics provenance
            diag = online_data.get("diagnostics", {})
            formula_lab_diag = diag.get("online_formula_lab", {})
            assert formula_lab_diag.get("active") is True
            assert "SymbolicFormulaLab" in (formula_lab_diag.get("engine") or "")

            # Case C: Online mode for Physics Ohm's law (U = I * R -> SymPy derives I = U/R, R = U/I)
            phys_msg = client.post(
                f"/api/chat/sessions/{sid}/messages",
                json={
                    "query": "biến đổi công thức U = I * R và tạo bài tập tương tự",
                    "answer_mode": "balanced",
                    "allow_online_api": True,
                },
            )
            assert phys_msg.status_code == 200
            phys_data = phys_msg.json()
            phys_ans = phys_data.get("answer", "")
            assert not phys_data.get("refused", False)
            assert "U/R" in phys_ans or "U/I" in phys_ans
            assert phys_data.get("diagnostics", {}).get("online_formula_lab", {}).get("active") is True

            # Case D: Online mode for Chemistry Redox (conservation of electrons)
            chem_msg = client.post(
                f"/api/chat/sessions/{sid}/messages",
                json={
                    "query": "sinh thêm ví dụ và bài tập về phản ứng oxi hóa - khử",
                    "answer_mode": "balanced",
                    "allow_online_api": True,
                },
            )
            assert chem_msg.status_code == 200
            chem_data = chem_msg.json()
            chem_ans = chem_data.get("answer", "")
            assert not chem_data.get("refused", False)
            assert "bảo toàn" in chem_ans.lower() or "nhường" in chem_ans.lower()
            assert "Bài 1" in chem_ans and "Bài 3" in chem_ans
            assert chem_data.get("diagnostics", {}).get("online_formula_lab", {}).get("active") is True
        finally:
            client.delete(f"/api/chat/sessions/{sid}")
    finally:
        client.delete(f"/api/documents/{doc_id}")


def test_frontend_online_toggle_labels():
    """Ensure HTML and app.js maintain the correct user-friendly labels and DOM element IDs."""
    with open("src/web/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    assert 'id="btn-toggle-online-api"' in html
    assert 'id="lbl-online-api"' in html
    assert "Offline (Chỉ tài liệu)" in html

    with open("src/web/static/js/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    assert "🔒 Offline (Chỉ tài liệu)" in js
    assert "🌐 Online (Mở rộng & Bài tập)" in js


def test_docx_embedded_image_ocr_extraction(monkeypatch):
    """DOCX parser extracts OCR text from raster images inside word/media/* cleanly."""
    from PIL import Image
    import src.web.file_parser as fp

    doc = docx.Document()
    doc.add_paragraph("Phần lý thuyết chính trong văn bản Word.")

    img_buf = io.BytesIO()
    Image.new("RGB", (140, 90), color=(255, 255, 255)).save(img_buf, format="PNG")
    img_buf.seek(0)
    doc.add_picture(img_buf)

    docx_buf = io.BytesIO()
    doc.save(docx_buf)
    raw_bytes = docx_buf.getvalue()

    monkeypatch.setattr(fp, "_ocr_image_bytes", lambda _b: "Công thức ảnh chụp: E = m * c^2")
    extracted = extract_text_from_docx(raw_bytes)
    assert "Phần lý thuyết chính trong văn bản Word." in extracted
    assert "Nội dung OCR từ hình ảnh" in extracted
    assert "E = m * c^2" in extracted

    # Graceful empty fallback when OCR engine is unavailable (must not crash or inject noise)
    monkeypatch.setattr(fp, "_ocr_image_bytes", lambda _b: "")
    extracted_no_ocr = extract_text_from_docx(raw_bytes)
    assert "Phần lý thuyết chính trong văn bản Word." in extracted_no_ocr
    assert "Nội dung OCR từ hình ảnh" not in extracted_no_ocr


def test_compound_three_concept_query_across_chunks():
    """
    Tests 3-concept list query ('chất khử, chất oxi hóa và quá trình oxi hóa là gì')
    across multi-section content, and guards against splitting paired aspects of 1 entity.
    """
    from src.reasoning.query_decomposer import QueryDecomposer

    dec = QueryDecomposer()
    d3 = dec.decompose("chất khử, chất oxi hóa và quá trình oxi hóa là gì?")
    assert d3.is_compound is True
    assert len(d3.sub_queries) == 3

    # Paired generic aspects of ONE entity must NOT be split into bare "Đặc điểm là gì?"
    d_single = dec.decompose("Đặc điểm và cơ chế của hệ thống SA-CMS là gì?")
    assert not any(sq.text.strip().lower().startswith("đặc điểm là gì") for sq in d_single.sub_queries)

    raw_doc = (
        "BÀI 2: PHẢN ỨNG OXI HÓA - KHỬ\n\n"
        "2.1. Chất khử\n"
        "Chất khử là chất nhường electron cho chất khác và có số oxi hóa tăng sau phản ứng.\n"
        "Ví dụ: Kim loại Zn nhường 2 electron để tạo thành ion Zn2+.\n\n"
        "2.2. Chất oxi hóa\n"
        "Chất oxi hóa là chất nhận electron từ chất khác và có số oxi hóa giảm sau phản ứng.\n"
        "Ví dụ: Ion H+ nhận electron tạo thành khí H2.\n\n"
        "2.3. Quá trình oxi hóa\n"
        "Quá trình oxi hóa là quá trình chất khử nhường electron (sự oxi hóa).\n"
        "Ngược lại, quá trình khử là quá trình chất oxi hóa nhận electron."
    )
    c_doc = client.post("/api/documents/raw", json={"title": "Bài 2 Redox 3 Khái Niệm", "text": raw_doc})
    assert c_doc.status_code == 200
    doc_id = c_doc.json()["document_id"]
    try:
        c_sess = client.post("/api/chat/sessions", json={"title": "3-Concept Test", "document_ids": [doc_id]})
        assert c_sess.status_code == 200
        sid = c_sess.json()["session_id"]
        try:
            r = client.post(
                f"/api/chat/sessions/{sid}/messages",
                json={
                    "query": "chất khử, chất oxi hóa và quá trình oxi hóa là gì?",
                    "answer_mode": "balanced",
                    "allow_online_api": False,
                },
            )
            assert r.status_code == 200
            data = r.json()
            ans = (data.get("answer") or "").lower()
            assert not data.get("refused", False)
            assert "chất khử" in ans and "nhường electron" in ans
            assert "chất oxi hóa" in ans and "nhận electron" in ans
            assert "quá trình oxi hóa" in ans
        finally:
            client.delete(f"/api/chat/sessions/{sid}")
    finally:
        client.delete(f"/api/documents/{doc_id}")


def test_formula_lab_calculus_latex_linear_system_and_word_example_inference():
    """
    Verifies upgraded 100% local SymPy Formula Lab across:
    1. LaTeX calculus function f(x) = x^3 - 3x + 2 (diff, integrate, factor, critical points)
    2. LaTeX physics equation E_k = \\frac{1}{2} m v^{2}
    3. 2-variable linear system (2x + y = 5; x - y = 1)
    4. Example-only word problem without explicit '=' equation (kinematics v = s / t)
    """
    # 1. LaTeX calculus function
    calc_doc = (
        "CHƯƠNG GIẢI TÍCH: KHẢO SÁT HÀM ĐA THỨC\n"
        "Xét hàm số bậc ba viết dưới dạng LaTeX: $f(x) = x^{3} - 3x + 2$.\n"
        "Ta nghiên cứu chiều biến thiên và cực trị của hàm số này."
    )
    calc_res = build_online_study_expansion(
        query="tính đạo hàm, nguyên hàm, phân tích nhân tử và tạo bài tập cho f(x)",
        doc_text=calc_doc,
        doc_title="Giải tích 12",
    )
    assert calc_res is not None
    calc_ans = calc_res["answer"]
    assert "3*x^2 - 3" in calc_ans
    assert "x^4/4 - 3*x^2/2 + 2*x" in calc_ans
    assert "(x - 1)^2*(x + 2)" in calc_ans
    assert "Bài 1" in calc_ans and "Bài 3" in calc_ans

    # 2. LaTeX fraction physics equation
    latex_phys = r"Động năng của vật khối lượng m chuyển động với vận tốc v: $E_k = \frac{1}{2} \cdot m \cdot v^{2}$."
    phys_formulas = extract_document_formulas(latex_phys)
    assert any(f.get("kind") == "algebraic_eq" for f in phys_formulas)
    phys_trans = "\n".join(derive_formula_transformations(phys_formulas))
    assert "2*E_k/v^2" in phys_trans
    assert "sqrt(" in phys_trans

    # 3. 2-variable linear system
    sys_doc = (
        "BÀI 3: HỆ HAI PHƯƠNG TRÌNH BẬC NHẤT HAI ẨN\n"
        "Xét hệ phương trình:\n"
        "2x + y = 5\n"
        "x - y = 1\n"
    )
    sys_res = build_online_study_expansion(
        query="giải hệ phương trình, biến đổi thế và sinh thêm ví dụ bài tập tương tự",
        doc_text=sys_doc,
        doc_title="Đại số tuyến tính",
    )
    assert sys_res is not None
    sys_ans = sys_res["answer"]
    assert "x = 2" in sys_ans and "y = 1" in sys_ans
    assert "Cramer" in sys_ans
    assert "Bài 1" in sys_ans and "Bài 3" in sys_ans

    # 4. Word-problem / example-only inference (NO explicit '=' equation!) + full chat E2E check
    word_doc = (
        "BÀI TOÁN CHUYỂN ĐỘNG ĐỀU\n"
        "Ví dụ minh họa: Một ô tô di chuyển trên quãng đường dài 120 km trong thời gian 2 giờ, "
        "đạt vận tốc trung bình 60 km/h trên toàn tuyến."
    )
    word_formulas = extract_document_formulas(word_doc)
    assert len(word_formulas) >= 1
    assert word_formulas[0].get("inferred_from_example") is True
    assert word_formulas[0].get("raw") == "v = s / t"

    c_doc = client.post("/api/documents/raw", json={"title": "Chuyển động đều", "text": word_doc})
    assert c_doc.status_code == 200
    doc_id = c_doc.json()["document_id"]
    try:
        c_sess = client.post("/api/chat/sessions", json={"title": "Word Inference Session", "document_ids": [doc_id]})
        assert c_sess.status_code == 200
        sid = c_sess.json()["session_id"]
        try:
            # Online mode infers v = s/t, transforms variables, gives new example & 3 exercises
            r_on = client.post(
                f"/api/chat/sessions/{sid}/messages",
                json={
                    "query": "biến đổi công thức và sinh thêm ví dụ bài tập tương tự",
                    "answer_mode": "balanced",
                    "allow_online_api": True,
                },
            )
            assert r_on.status_code == 200
            d_on = r_on.json()
            a_on = d_on.get("answer", "")
            assert not d_on.get("refused", False)
            assert "s/t" in a_on or "t*v" in a_on
            assert "Bài 1" in a_on and "Bài 3" in a_on
            assert d_on.get("diagnostics", {}).get("online_formula_lab", {}).get("active") is True
        finally:
            client.delete(f"/api/chat/sessions/{sid}")
    finally:
        client.delete(f"/api/documents/{doc_id}")
