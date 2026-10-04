"""
Test Corpus & Evaluation Question Suite for Phase 3.1.

Contains:
- Document A (Nested Learning & SmolLM2-135M)
- Document B (BM25 Retrieval & Refusal)
- Document C (Astronomy & Oceanography)
- 100 Test Questions categorized into:
    * 50 Answerable questions
    * 25 Unanswerable questions
    * 25 Insufficient-evidence questions
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Tuple

DOC_A_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "test_documents" / "doc_a.md"
DOC_B_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "test_documents" / "doc_b.md"
DOC_C_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "test_documents" / "doc_c.md"


def get_test_documents() -> List[Dict[str, Any]]:
    """Return the raw text and metadata for Document A, B, and C."""
    with open(DOC_A_PATH, "r", encoding="utf-8") as f:
        text_a = f.read()
    with open(DOC_B_PATH, "r", encoding="utf-8") as f:
        text_b = f.read()
    with open(DOC_C_PATH, "r", encoding="utf-8") as f:
        text_c = f.read()

    return [
        {
            "document_id": "DOC001",
            "title": "Hệ thống Bộ nhớ Đa thang SA-CMS và Kiến trúc Mô hình Ngôn ngữ Nhỏ SmolLM2-135M",
            "raw_text": text_a,
            "version": 1,
            "metadata": {"type": "architecture_specification", "subject": "Nested Learning & SmolLM2"},
        },
        {
            "document_id": "DOC002",
            "title": "Hệ thống Truy xuất Thông tin BM25, Quản lý Trích dẫn và Cổng Từ chối RefusalController",
            "raw_text": text_b,
            "version": 1,
            "metadata": {"type": "retrieval_specification", "subject": "BM25 & Refusal"},
        },
        {
            "document_id": "DOC003",
            "title": "Lịch sử Quan sát Thiên văn Vũ trụ và Thám hiểm Đáy biển Sâu",
            "raw_text": text_c,
            "version": 1,
            "metadata": {"type": "unrelated_domain", "subject": "Astronomy & Oceanography"},
        },
    ]


def get_100_test_questions() -> List[Dict[str, Any]]:
    """
    Returns exactly 100 test questions covering:
    - 50 Answerable questions (Doc A & Doc B)
    - 25 Unanswerable questions (out-of-corpus / unrelated)
    - 25 Insufficient evidence questions (partial mention, lacking details)
    """
    questions = []

    # =========================================================================
    # PART 1: 50 ANSWERABLE QUESTIONS (Doc A & Doc B)
    # =========================================================================
    ans_q_data = [
        # Doc A - Section 1
        ("SmolLM2-135M có chính xác bao nhiêu tham số?", "DOC001", "134.5 triệu", ["SmolLM2-135M", "tham số"]),
        ("Backbone SmolLM2-135M có bị đóng băng trong quá trình cập nhật không?", "DOC001", "đóng băng", ["SmolLM2-135M", "đóng băng"]),
        ("CMS thay thế thành phần nào của kiến trúc Transformer truyền thống?", "DOC001", "MLP", ["CMS", "MLP"]),
        ("Tên đầy đủ của hệ thống CMS trong đề cương là gì?", "DOC001", "Continuum Memory System", ["Continuum Memory System"]),
        ("Tầng nào kết nối backbone với bộ nhớ tham số?", "DOC001", "Hope-Attention", ["Hope-Attention"]),
        ("Tầng Hope-Attention chuẩn hóa trạng thái ẩn qua thành phần nào?", "DOC001", "cms_norm", ["cms_norm", "LayerNorm"]),
        ("Trạng thái ẩn kết hợp với phần dư bộ nhớ theo phương trình nào của bài báo?", "DOC001", "Phương trình 70 và 74", ["Phương trình 70"]),
        ("Mã số bài báo arXiv của Nested Learning là gì?", "DOC001", "arXiv:2512.24695v1", ["2512.24695v1"]),
        ("Backbone SmolLM2 được phát triển bởi tổ chức nào trên HuggingFace?", "DOC001", "HuggingFaceTB", ["HuggingFaceTB"]),
        ("Tỷ lệ đóng băng của backbone là bao nhiêu phần trăm?", "DOC001", "100%", ["100%"]),

        # Doc A - Section 2
        ("Card đồ họa được sử dụng trong thử nghiệm là dòng nào?", "DOC001", "NVIDIA GeForce GTX 1650 Ti", ["GTX 1650 Ti"]),
        ("Dung lượng VRAM của GPU GTX 1650 Ti là bao nhiêu GB?", "DOC001", "4GB", ["4GB", "VRAM"]),
        ("Hệ điều hành chạy trong môi trường thử nghiệm là gì?", "DOC001", "Windows 11", ["Windows 11"]),
        ("Phiên bản Python nào được sử dụng trong nghiên cứu?", "DOC001", "Python 3.9", ["Python 3.9"]),
        ("Số mức thời gian num_levels của bộ nhớ CMS được cấu hình là bao nhiêu?", "DOC001", "2 mức", ["num_levels", "2"]),
        ("Kích thước khối tối thiểu lowest_chunk_size của CMS là bao nhiêu token?", "DOC001", "64 token", ["lowest_chunk_size", "64"]),
        ("Tốc độ học cơ sở base_lr của CMS được cố định ở giá trị nào?", "DOC001", "0.01", ["base_lr", "0.01"]),
        ("Số lượng tham số bổ sung của CMS là bao nhiêu triệu tham số?", "DOC001", "3.54 triệu", ["3.54 triệu"]),
        ("Số tham số của CMS chiếm chưa đến bao nhiêu phần trăm tổng mô hình?", "DOC001", "2.6%", ["2.6%"]),
        ("Thuật toán tối ưu nào được áp dụng cho cập nhật online?", "DOC001", "Phương trình 71", ["Phương trình 71"]),

        # Doc A - Section 3
        ("Phương pháp SA-CMS đề xuất căn chỉnh ranh giới theo yếu tố nào?", "DOC001", "cấu trúc văn bản", ["cấu trúc văn bản"]),
        ("SA-CMS thay thế cơ chế cắt nào của baseline?", "DOC001", "cắt token cố định", ["cắt token cố định"]),
        ("Các ranh giới tài liệu thực tế nào được SA-CMS sử dụng?", "DOC001", "tiêu đề mục, đoạn văn và ranh giới câu", ["tiêu đề mục"]),
        ("Bộ phận nào bóc tách văn bản thành cây cấu trúc phân cấp?", "DOC001", "Document Structure Parser", ["Document Structure Parser"]),
        ("Mã định danh đoạn văn bản trong hệ thống có định dạng chuẩn nào?", "DOC001", "DOC{id}::P{idx}", ["DOC{id}::P{idx}"]),
        ("Mục tiêu của việc gán mã định danh duy nhất cho từng đoạn là gì?", "DOC001", "truy vết nguồn gốc 100%", ["truy vết nguồn gốc"]),
        ("Sự kiện cập nhật gradient online tuân theo phương trình nào?", "DOC001", "Phương trình 71", ["Phương trình 71"]),
        ("SA-CMS là từ viết tắt của cụm từ tiếng Anh nào?", "DOC001", "Structure-Aligned CMS", ["Structure-Aligned CMS"]),
        ("Cây cấu trúc của parser phân tách tài liệu thành những cấp nào?", "DOC001", "phân cấp", ["cây cấu trúc"]),
        ("Các cập nhật của CMS diễn ra ở chế độ nào?", "DOC001", "online", ["online"]),

        # Doc A - Section 4
        ("Số hạt giống ngẫu nhiên (seeds) được kiểm soát ở Phase 2.5 là bao nhiêu?", "DOC001", "3 hạt giống", ["seeds", "42, 43, 44"]),
        ("Những seed cụ thể nào đã được dùng trong thử nghiệm Phase 2.5?", "DOC001", "42, 43, 44", ["42, 43, 44"]),
        ("Ngân sách cập nhật chuẩn hóa ở Level 2 là bao nhiêu updates?", "DOC001", "1540 updates", ["1540 updates"]),
        ("Ngân sách cập nhật chuẩn hóa ở Level 3 là bao nhiêu updates?", "DOC001", "1650 updates", ["1650 updates"]),
        ("Xác suất mục tiêu MK-NIAH của SA-CMS đạt giá trị bao nhiêu?", "DOC001", "0.0296", ["0.0296"]),
        ("Xác suất mục tiêu MK-NIAH của Fixed-Token là bao nhiêu?", "DOC001", "0.0210", ["0.0210"]),
        ("Giá trị p-value giữa SA-CMS và Fixed-Token trên MK-NIAH là bao nhiêu?", "DOC001", "nhỏ hơn 1e-17", ["1e-17"]),
        ("Điểm perplexity (PPL) hiệu chuẩn trên tập QASPER là bao nhiêu?", "DOC001", "98.19", ["98.19"]),
        ("Hiện tượng nào khiến PPL tăng khi cập nhật online với hàm mất mát CLM?", "DOC001", "trôi dạt biểu diễn (representation drift)", ["representation drift"]),
        ("Bộ dữ liệu QASPER đánh giá cấp học viên gồm bao nhiêu tài liệu?", "DOC001", "10 tài liệu", ["10 tài liệu"]),

        # Doc B - Section 1
        ("Hệ thống con truy xuất sử dụng giải thuật nào?", "DOC002", "BM25 Okapi", ["BM25 Okapi"]),
        ("Giải thuật BM25 được viết bằng ngôn ngữ nào?", "DOC002", "Python thuần túy", ["Python thuần túy"]),
        ("Mục đích của việc dùng BM25 thuần Python là gì?", "DOC002", "loại bỏ phụ thuộc và đảm bảo tái lập", ["tái lập 100%"]),
        ("Tham số k1 trong thuật toán BM25 có giá trị mặc định là bao nhiêu?", "DOC002", "1.5", ["k1", "1.5"]),
        ("Tham số b trong thuật toán BM25 có giá trị mặc định là bao nhiêu?", "DOC002", "0.75", ["b", "0.75"]),
        ("Tham số k1 điều chỉnh yếu tố gì trong công thức BM25?", "DOC002", "độ bão hòa tần số từ", ["bão hòa tần số từ"]),
        ("Tham số b điều chỉnh yếu tố gì trong công thức BM25?", "DOC002", "độ dài văn bản (length normalization)", ["độ dài văn bản"]),
        ("Chỉ mục BM25 cập nhật theo phương thức nào khi có tài liệu mới?", "DOC002", "tăng dần", ["tăng dần"]),

        # Doc B - Section 2 & 3
        ("Kho lưu trữ DocumentStore lưu trữ dữ liệu dưới định dạng tệp nào?", "DOC002", "JSON", ["JSON"]),
        ("Mã băm kiểm soát toàn vẹn tài liệu sử dụng thuật toán nào?", "DOC002", "SHA-256 rút gọn 16 ký tự", ["SHA-256", "16 ký tự"]),
    ]

    for idx, (q_text, doc_target, gold_ans, keywords) in enumerate(ans_q_data, start=1):
        questions.append({
            "question_id": f"Q{idx:03d}",
            "question": q_text,
            "category": "answerable",
            "target_document_id": doc_target,
            "expected_decision": "answer",
            "expected_reason": None,
            "gold_answer": gold_ans,
            "keywords": keywords,
        })

    # =========================================================================
    # PART 2: 25 UNANSWERABLE QUESTIONS (Out of domain / completely absent)
    # =========================================================================
    unans_q_data = [
        "Thủ đô của nước Pháp là thành phố nào?",
        "Cách nấu món phở bò truyền thống của Hà Nội như thế nào?",
        "Ai là người đã vẽ nên bức tranh Mona Lisa nổi tiếng?",
        "Định lý cuối cùng của Fermat được chứng minh vào năm nào?",
        "Vận tốc ánh sáng trong chân không chính xác là bao nhiêu m/s?",
        "Dân số hiện tại của Tokyo là bao nhiêu triệu người?",
        "Giải bóng đá Ngoại Hạng Anh có bao nhiêu câu lạc bộ tham dự mỗi mùa?",
        "Đỉnh núi Everest có độ cao chính xác là bao nhiêu mét?",
        "Hành tinh nào gần Mặt Trời nhất trong Hệ Mặt Trời?",
        "Thành phố nào là thủ đô của Australia?",
        "Ai đã phát minh ra máy hơi nước mở đầu cuộc Cách mạng Công nghiệp?",
        "Nguyên tố hóa học nào có ký hiệu là Au trong bảng tuần hoàn?",
        "Tác phẩm Romeo và Juliet do ai sáng tác?",
        "Quốc gia nào có diện tích lãnh thổ lớn nhất thế giới?",
        "Đơn vị tiền tệ chính thức của Nhật Bản là gì?",
        "Đại dương nào có diện tích lớn nhất trên Trái Đất?",
        "Hệ điều hành Android ban đầu được công ty nào sáng lập trước khi Google mua lại?",
        "Cầu Cổng Vàng (Golden Gate Bridge) nằm ở thành phố nào của Mỹ?",
        "Loài động vật có vú nào bay được duy nhất trên Trái Đất?",
        "Kim tự tháp Giza nằm ở quốc gia nào?",
        "Ai là tác giả của Thuyết tương đối rộng?",
        "Cây cầu Bãi Cháy nằm ở tỉnh thành nào của Việt Nam?",
        "Đồng tiền chung của Liên minh Châu Âu có tên là gì?",
        "Trận chung kết World Cup 2022 diễn ra tại quốc gia nào?",
        "Bức họa Đêm đầy sao (The Starry Night) do danh họa nào sáng tác?",
    ]

    for idx, q_text in enumerate(unans_q_data, start=51):
        questions.append({
            "question_id": f"Q{idx:03d}",
            "question": q_text,
            "category": "unanswerable",
            "target_document_id": None,
            "expected_decision": "refusal",
            "expected_reason": "no_relevant_evidence_found",
            "gold_answer": None,
            "keywords": [],
        })

    # =========================================================================
    # PART 3: 25 INSUFFICIENT EVIDENCE QUESTIONS (Near-topic / Partial mention)
    # =========================================================================
    insuff_q_data = [
        ("Mô hình SmolLM2-135M được huấn luyện trong bao nhiêu epoch trước khi phát hành?", "DOC001"),
        ("Tổng chi phí điện năng tiêu thụ của GPU GTX 1650 Ti là bao nhiêu kWh?", "DOC001"),
        ("Tên của kỹ sư trưởng nhóm tác giả phát triển mô hình SmolLM2 là ai?", "DOC001"),
        ("Hàm mất mát CLM của SmolLM2 sử dụng trọng số chi tiết cho từng lớp là bao nhiêu?", "DOC001"),
        ("CMS có khả năng mở rộng lên 100 mức thời gian hay không và công thức là gì?", "DOC001"),
        ("Độ trễ inference của SmolLM2-135M trên vi xử lý Apple M2 là bao nhiêu mili-giây?", "DOC001"),
        ("Phiên bản driver NVIDIA GeForce nào được cài đặt trên máy trạm Windows 11?", "DOC001"),
        ("Dataset QASPER được thu thập chính xác vào ngày tháng năm nào?", "DOC001"),
        ("Giá bán lẻ hiện tại của card đồ họa GTX 1650 Ti trên thị trường là bao nhiêu USD?", "DOC001"),
        ("Thuật toán SA-CMS có được cấp bằng sáng chế độc quyền tại Việt Nam không?", "DOC001"),
        ("Thuật toán BM25 có hỗ trợ xử lý ngôn ngữ tiếng Ả Rập hay tiếng Nga không?", "DOC002"),
        ("Tốc độ xử lý của BM25 khi chỉ mục có 10 triệu văn bản là bao nhiêu giây?", "DOC002"),
        ("Ai là người đầu tiên phát minh ra hệ số độ dài b trong BM25 vào năm 1994?", "DOC002"),
        ("DocumentStore có hỗ trợ lưu trữ cơ sở dữ liệu phân tán Cassandra không?", "DOC002"),
        ("Mã băm SHA-256 của tài liệu DOC001 có thể giải mã ngược lại được không?", "DOC002"),
        ("RefusalController có thể tích hợp với mô hình GPT-4 để đánh giá không?", "DOC002"),
        ("Ngưỡng điểm tin cậy min_evidence_score có tự động học qua gradient descent không?", "DOC002"),
        ("CitationChecker có kiểm tra chữ ký số mật mã học RSA của tác giả không?", "DOC002"),
        ("Độ dài tối đa của một passage trong DocumentChunker có thể lên tới 10,000 từ không?", "DOC002"),
        ("Thư viện Python nào được khuyên dùng để tăng tốc BM25 bằng GPU CUDA?", "DOC002"),
        ("Kính viễn vọng James Webb đã tiêu tốn tổng cộng bao nhiêu tỷ đô la kinh phí?", "DOC003"),
        ("Tên của nhà khoa học đứng đầu dự án thám hiểm rãnh Mariana năm 1960 là ai?", "DOC003"),
        ("Vận tốc bay tối đa của tên lửa Ariane 5 khi đưa JWST lên quỹ đạo là bao nhiêu km/h?", "DOC003"),
        ("Loài cá ốc Mariana có tuổi thọ trung bình là bao nhiêu năm?", "DOC003"),
        ("Áp suất tại tâm Trái Đất lớn hơn áp suất Challenger Deep bao nhiêu lần?", "DOC003"),
    ]

    for idx, (q_text, target_doc) in enumerate(insuff_q_data, start=76):
        questions.append({
            "question_id": f"Q{idx:03d}",
            "question": q_text,
            "category": "insufficient_evidence",
            "target_document_id": target_doc,
            "expected_decision": "refusal",
            "expected_reason": "evidence_below_confidence_threshold",
            "gold_answer": None,
            "keywords": [],
        })

    assert len(questions) == 100, f"Expected 100 questions, got {len(questions)}"
    return questions
