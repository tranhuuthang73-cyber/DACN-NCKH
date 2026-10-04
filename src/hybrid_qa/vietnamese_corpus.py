"""
Vietnamese Readiness Smoke Test Corpus for Phase 3.3.

Provides:
- 5 structured Vietnamese documents (VN_DOC_001 to VN_DOC_005)
  with sections, paragraphs, passage IDs, and versions.
- 40 evaluation questions:
  - 20 Answerable (4 per document)
  - 10 Unanswerable (out-of-domain)
  - 10 Insufficient Evidence (in-domain keywords, missing target facts)
- Version 2 update for VN_DOC_001 to validate document versioning.

Note: This is a smoke test suite for readiness validation, NOT an official benchmark.
"""

from typing import List, Dict, Any


def get_vietnamese_documents() -> List[Dict[str, Any]]:
    """Returns 5 structured Vietnamese documents for Phase 3.3."""
    return [
        {
            "document_id": "VN_DOC_001",
            "title": "Nghiên cứu Hệ thống Bộ nhớ Đa quy mô SA-CMS trong Mô hình Ngôn ngữ",
            "version": 1,
            "raw_text": (
                "## 1. Giới thiệu tổng quan\n\n"
                "Đề tài nghiên cứu sinh ra nhằm giải quyết hiện tượng suy giảm ngữ cảnh của mô hình ngôn ngữ khi xử lý văn bản dài. "
                "Khung kiến trúc Continuum Memory System (CMS) phân tách các tầng bộ nhớ thành nhiều thang thời gian khác nhau để ghi nhớ thông tin một cách bền vững.\n\n"
                "Khác với cơ chế In-Context Learning thuần túy vốn bị giới hạn bởi độ dài cửa sổ context, mô hình kết hợp bộ nhớ liên tục cho phép duy trì thông tin cốt lõi ngay cả khi đoạn văn bản gốc đã trôi khỏi bộ nhớ đệm attention.\n\n"
                "## 2. Kiến trúc 3 cấp độ SA-CMS\n\n"
                "Kiến trúc SA-CMS 3 cấp độ liên kết trực tiếp với cấu trúc thứ bậc của tài liệu. Cấp độ 1 là Paragraph Memory tương ứng với thang thời gian nhanh nhất, thực hiện cập nhật cục bộ sau mỗi đoạn văn.\n\n"
                "Cấp độ 2 là Section Memory hoạt động ở thang thời gian trung bình, thực hiện tích lũy và cập nhật gradient tại ranh giới kết thúc mỗi đề mục của tài liệu.\n\n"
                "Cấp độ 3 là Document Memory hoạt động ở thang thời gian chậm nhất, ghi lại biểu diễn trừu tượng bất biến toàn cục của toàn bộ tài liệu khi hoàn thành lượt đọc.\n\n"
                "## 3. Quy trình Trả lời và Trích dẫn\n\n"
                "Hệ thống hybrid kết hợp bộ nhớ tham số SA-CMS với công cụ truy xuất BM25 để thu thập bằng chứng ngoại biên. Bộ chọn bằng chứng lọc các đoạn trích có điểm tương đồng vượt ngưỡng quy định.\n\n"
                "Bộ điều khiển từ chối (Refusal Controller) chịu trách nhiệm thẩm định độ bao phủ từ khóa và độ tin cậy của bằng chứng trước khi chuyển cho mô hình sinh câu trả lời kèm mã định danh trích dẫn."
            ),
            "metadata": {
                "field": "Trí tuệ Nhân tạo",
                "author": "Nhóm Nghiên cứu NCKH",
                "language": "vi",
                "target_levels": 3,
            },
        },
        {
            "document_id": "VN_DOC_002",
            "title": "Quy định Bảo vệ Dữ liệu Cá nhân và An toàn Thông tin Số",
            "version": 1,
            "raw_text": (
                "## 1. Nguyên tắc Xử lý Dữ liệu\n\n"
                "Nghị định 13/2023/NĐ-CP quy định dữ liệu cá nhân phải được xử lý theo nguyên tắc hợp pháp, công bằng, minh bạch và có sự đồng thuận rõ ràng của chủ thể dữ liệu trước khi thu thập.\n\n"
                "Bên kiểm soát dữ liệu có nghĩa vụ áp dụng các biện pháp an ninh mạng kỹ thuật số như mã hóa AES-256 và ẩn danh hóa để ngăn chặn truy cập trái phép hoặc rò rỉ thông tin cá nhân.\n\n"
                "## 2. Quyền của Chủ thể Dữ liệu\n\n"
                "Chủ thể dữ liệu có quyền yêu cầu xem, chỉnh sửa, hạn chế xử lý hoặc xóa bỏ toàn bộ dữ liệu cá nhân của mình trong vòng 72 giờ kể từ khi gửi văn bản hợp lệ.\n\n"
                "Trong trường hợp xảy ra sự cố vi phạm dữ liệu cá nhân, tổ chức chịu trách nhiệm phải thông báo cho Cục An ninh mạng và Phòng chống tội phạm công nghệ cao trong vòng 72 giờ làm việc.\n\n"
                "## 3. Chế tài Xử phạt\n\n"
                "Các hành vi mua bán trái phép dữ liệu cá nhân dưới 10.000 bản ghi có thể bị xử phạt vi phạm hành chính từ 50 triệu đến 100 triệu đồng tùy theo mức độ nghiêm trọng.\n\n"
                "Trường hợp tổ chức vi phạm nhiều lần hoặc chuyển giao dữ liệu trái phép ra nước ngoài có thể bị áp mức phạt tiền tối đa lên đến 5% tổng doanh thu năm tài chính liền trước."
            ),
            "metadata": {
                "field": "Pháp luật & An ninh thông tin",
                "author": "Ban Pháp chế",
                "language": "vi",
            },
        },
        {
            "document_id": "VN_DOC_003",
            "title": "Lịch sử và Kiến trúc Di sản Cố đô Huế",
            "version": 1,
            "raw_text": (
                "## 1. Quần thể Di tích Kinh thành\n\n"
                "Kinh thành Huế được khởi công xây dựng vào năm 1805 dưới triều vua Gia Long và hoàn thành vào năm 1832 dưới thời vua Minh Mạng, kết hợp giữa kiến trúc cung đình phương Đông và nguyên lý phòng thủ Vauban của Pháp.\n\n"
                "Hoàng thành Huế có cấu trúc hình vuông với bốn cổng chính gồm Ngọ Môn ở phía Nam, cửa Hiển Nhơn ở phía Đông, cửa Chương Đức ở phía Tây và cửa Hòa Bình ở phía Bắc.\n\n"
                "## 2. Nghệ thuật Nhã nhạc Cung đình\n\n"
                "Nhã nhạc Cung đình Huế đã được UNESCO chính thức vinh danh là Kiệt tác Di sản Văn hóa Phi vật thể và Truyền khẩu của Nhân loại vào năm 2003.\n\n"
                "Hệ thống dàn nhạc Cung đình bao gồm nhiều thể loại nhạc khí độc đáo như đàn tỳ bà, đàn nhị, trống bản, kèn bóp và dàn chuông đá cử hành trong các đại lễ Tế Nam Giao và lễ đăng quang.\n\n"
                "## 3. Bảo tồn và Tu bổ Di sản\n\n"
                "Dự án bảo tồn điện Kiến Trung được khởi động trùng tu phục hồi từ năm 2019 và chính thức mở cửa đón khách tham quan nhân dịp Tết Nguyên đán năm 2024.\n\n"
                "Các chuyên gia phục chế sử dụng kỹ thuật khảm sành sứ truyền thống cùng vôi vữa hàu để tái hiện chính xác hoa văn mỹ thuật triều Khải Định."
            ),
            "metadata": {
                "field": "Lịch sử & Di sản Văn hóa",
                "author": "Trung tâm Bảo tồn Di tích",
                "language": "vi",
            },
        },
        {
            "document_id": "VN_DOC_004",
            "title": "Nông nghiệp Thông minh và Ứng phó Biến đổi Khí hậu tại Đồng bằng Sông Cửu Long",
            "version": 1,
            "raw_text": (
                "## 1. Thách thức Xâm nhập Mặn\n\n"
                "Biến đổi khí hậu và việc phát triển đập thủy điện thượng nguồn sông Mê Kông đã làm giảm lưu lượng dòng chảy mùa kiệt, đẩy ranh mặn 4 gam trên lít xâm nhập sâu tới 70 km vào đất liền tại Bến Tre và Trà Vinh.\n\n"
                "Hiện tượng sụt lún đất do khai thác nước ngầm quá mức ở vùng bán đảo Cà Mau với tốc độ trung bình từ 1,5 đến 2,5 cm mỗi năm đe dọa sinh kế của hơn hai triệu nông dân.\n\n"
                "## 2. Mô hình Chuyển đổi Cơ cấu Mùa vụ\n\n"
                "Mô hình canh tác lúa - tôm thông minh thích ứng biến đổi khí hậu đã chứng minh hiệu quả kinh tế vượt trội, giảm 60% lượng phân bón hóa học và tăng thu nhập thêm 40% cho bà con vùng ngọt hóa ven biển.\n\n"
                "Giống lúa chịu mặn ST25 và OM18 được triển khai gieo cấy thành công trên diện tích 150.000 héc-ta, chịu được độ mặn tới 5 phần nghìn trong giai đoạn đẻ nhánh.\n\n"
                "## 3. Nền tảng IoT và Quản lý Nước\n\n"
                "Mạng lưới 120 trạm quan trắc tự động IoT đo độ mặn và độ pH theo thời gian thực được lắp đặt dọc các cửa sông Tiền và sông Hậu, truyền dữ liệu cảnh báo qua ứng dụng di động cho nông dân.\n\n"
                "Hệ thống đóng mở cống ngăn mặn tự động bằng năng lượng mặt trời tại cống Cái Lớn - Cái Bé giúp kiểm soát nguồn nước ngọt cho hơn 384.000 héc-ta diện tích đất sản xuất nông nghiệp."
            ),
            "metadata": {
                "field": "Nông nghiệp & Môi trường",
                "author": "Viện Nghiên cứu Biến đổi Khí hậu",
                "language": "vi",
            },
        },
        {
            "document_id": "VN_DOC_005",
            "title": "Chiến lược Phát triển Năng lượng Tái tạo và Lưới điện Quốc gia",
            "version": 1,
            "raw_text": (
                "## 1. Quy hoạch Điện VIII\n\n"
                "Quy hoạch phát triển điện lực quốc gia thời kỳ 2021 - 2030 (Quy hoạch điện VIII) đặt mục tiêu tỷ lệ năng lượng tái tạo đạt khoảng 30,9% đến 39,2% tổng sản lượng điện vào năm 2030.\n\n"
                "Công suất điện gió ngoài khơi dự kiến đạt 6.000 MW vào năm 2030, ưu tiên triển khai tại khu vực Nam Trung Bộ nhờ tiềm năng tốc độ gió trung bình trên 8 mét trên giây.\n\n"
                "## 2. Hệ thống Lưu trữ và Lưới điện Thông minh\n\n"
                "Tập đoàn Điện lực Việt Nam triển khai thí nghiệm các trạm lưu trữ pin BESS với công suất 50 MW tại Bình Thuận để cắt giảm hiện tượng quá tải đường dây truyền tải 500 kV.\n\n"
                "Công nghệ lưới điện siêu nhỏ (microgrid) kết hợp pin mặt trời áp mái và máy biến áp thông minh được áp dụng tại các khu công nghiệp công nghệ cao nhằm ổn định chất lượng điện áp.\n\n"
                "## 3. Cơ chế Mua bán Điện Trực tiếp (DPPA)\n\n"
                "Nghị định về cơ chế DPPA cho phép khách hàng sử dụng điện lớn ký hợp đồng mua bán điện trực tiếp với các đơn vị phát điện năng lượng tái tạo qua đường dây riêng hoặc lưới điện quốc gia.\n\n"
                "Mức giá trần đối với dự án điện gió trên bờ trong khung giá chuyển tiếp được quy định là 1.587,12 đồng trên một kilowatt giờ (chưa bao gồm thuế VAT)."
            ),
            "metadata": {
                "field": "Năng lượng & Công nghệ Kỹ thuật",
                "author": "Bộ Công Thương",
                "language": "vi",
            },
        },
    ]


def get_vietnamese_v2_update() -> Dict[str, Any]:
    """Returns the updated version 2 of VN_DOC_001 to test Document Versioning."""
    return {
        "document_id": "VN_DOC_001",
        "title": "Nghiên cứu Hệ thống Bộ nhớ Đa quy mô SA-CMS trong Mô hình Ngôn ngữ (Phiên bản v2)",
        "version": 2,
        "raw_text": (
            "## 1. Giới thiệu tổng quan\n\n"
            "Đề tài nghiên cứu sinh ra nhằm giải quyết hiện tượng suy giảm ngữ cảnh của mô hình ngôn ngữ khi xử lý văn bản dài. "
            "Khung kiến trúc Continuum Memory System (CMS) phân tách các tầng bộ nhớ thành nhiều thang thời gian khác nhau để ghi nhớ thông tin một cách bền vững.\n\n"
            "Khác với cơ chế In-Context Learning thuần túy vốn bị giới hạn bởi độ dài cửa sổ context, mô hình kết hợp bộ nhớ liên tục cho phép duy trì thông tin cốt lõi ngay cả khi đoạn văn bản gốc đã trôi khỏi bộ nhớ đệm attention.\n\n"
            "## 2. Kiến trúc 3 cấp độ SA-CMS\n\n"
            "Kiến trúc SA-CMS 3 cấp độ liên kết trực tiếp với cấu trúc thứ bậc của tài liệu. Cấp độ 1 là Paragraph Memory tương ứng với thang thời gian nhanh nhất, thực hiện cập nhật cục bộ sau mỗi đoạn văn.\n\n"
            "Cấp độ 2 là Section Memory trong phiên bản v2 được tối ưu hóa với thuật toán momentum tích lũy, tốc độ học nâng cấp là 0.005 thay vì 0.01 nhằm ổn định biểu diễn ngữ nghĩa giữa các đề mục.\n\n"
            "Cấp độ 3 là Document Memory hoạt động ở thang thời gian chậm nhất, ghi lại biểu diễn trừu tượng bất biến toàn cục của toàn bộ tài liệu khi hoàn thành lượt đọc.\n\n"
            "## 3. Quy trình Trả lời và Trích dẫn\n\n"
            "Hệ thống hybrid kết hợp bộ nhớ tham số SA-CMS với công cụ truy xuất BM25 để thu thập bằng chứng ngoại biên. Bộ chọn bằng chứng lọc các đoạn trích có điểm tương đồng vượt ngưỡng quy định.\n\n"
            "Bộ điều khiển từ chối (Refusal Controller) chịu trách nhiệm thẩm định độ bao phủ từ khóa và độ tin cậy của bằng chứng trước khi chuyển cho mô hình sinh câu trả lời kèm mã định danh trích dẫn."
        ),
        "metadata": {
            "field": "Trí tuệ Nhân tạo",
            "author": "Nhóm Nghiên cứu NCKH",
            "language": "vi",
            "target_levels": 3,
            "version_note": "Cập nhật tốc độ học Section Memory lên 0.005",
        },
    }


def get_vietnamese_smoke_questions() -> List[Dict[str, Any]]:
    """
    Returns 40 smoke test questions:
    - 20 Answerable
    - 10 Unanswerable
    - 10 Insufficient Evidence
    """
    return [
        # =====================================================================
        # 20 ANSWERABLE QUESTIONS (VN_DOC_001 to VN_DOC_005)
        # =====================================================================
        # VN_DOC_001
        {
            "question_id": "VN_ANS_001",
            "category": "answerable",
            "document_id": "VN_DOC_001",
            "expected_decision": "answer",
            "question": "Kiến trúc SA-CMS 3 cấp độ phân chia các tầng bộ nhớ như thế nào?",
            "target_passages": ["VN_DOC_001::P002", "VN_DOC_001::P003", "VN_DOC_001::P004"],
            "expected_keywords": ["Paragraph Memory", "Section Memory", "Document Memory"],
        },
        {
            "question_id": "VN_ANS_002",
            "category": "answerable",
            "document_id": "VN_DOC_001",
            "expected_decision": "answer",
            "question": "Cấp độ 1 Paragraph Memory trong SA-CMS thực hiện cập nhật vào thời điểm nào?",
            "target_passages": ["VN_DOC_001::P002"],
            "expected_keywords": ["sau mỗi đoạn văn", "cục bộ", "thang thời gian nhanh nhất"],
        },
        {
            "question_id": "VN_ANS_003",
            "category": "answerable",
            "document_id": "VN_DOC_001",
            "expected_decision": "answer",
            "question": "Bộ điều khiển từ chối trong hệ thống hybrid có nhiệm vụ gì?",
            "target_passages": ["VN_DOC_001::P006"],
            "expected_keywords": ["Refusal Controller", "thẩm định", "độ bao phủ", "độ tin cậy"],
        },
        {
            "question_id": "VN_ANS_004",
            "category": "answerable",
            "document_id": "VN_DOC_001",
            "expected_decision": "answer",
            "question": "Công cụ truy xuất nào được kết hợp với bộ nhớ SA-CMS để thu thập bằng chứng ngoại biên?",
            "target_passages": ["VN_DOC_001::P005"],
            "expected_keywords": ["BM25", "truy xuất"],
        },

        # VN_DOC_002
        {
            "question_id": "VN_ANS_005",
            "category": "answerable",
            "document_id": "VN_DOC_002",
            "expected_decision": "answer",
            "question": "Theo Nghị định 13/2023/NĐ-CP, việc xử lý dữ liệu cá nhân phải tuân theo những nguyên tắc nào?",
            "target_passages": ["VN_DOC_002::P000"],
            "expected_keywords": ["hợp pháp", "công bằng", "minh bạch", "đồng thuận"],
        },
        {
            "question_id": "VN_ANS_006",
            "category": "answerable",
            "document_id": "VN_DOC_002",
            "expected_decision": "answer",
            "question": "Chủ thể dữ liệu có quyền yêu cầu chỉnh sửa hoặc xóa dữ liệu cá nhân trong thời hạn bao lâu?",
            "target_passages": ["VN_DOC_002::P002"],
            "expected_keywords": ["72 giờ"],
        },
        {
            "question_id": "VN_ANS_007",
            "category": "answerable",
            "document_id": "VN_DOC_002",
            "expected_decision": "answer",
            "question": "Khi xảy ra sự cố rò rỉ dữ liệu cá nhân, tổ chức phải thông báo cho cơ quan nào?",
            "target_passages": ["VN_DOC_002::P003"],
            "expected_keywords": ["Cục An ninh mạng", "Phòng chống tội phạm công nghệ cao"],
        },
        {
            "question_id": "VN_ANS_008",
            "category": "answerable",
            "document_id": "VN_DOC_002",
            "expected_decision": "answer",
            "question": "Mức phạt tiền tối đa đối với tổ chức chuyển giao dữ liệu trái phép ra nước ngoài là bao nhiêu?",
            "target_passages": ["VN_DOC_002::P005"],
            "expected_keywords": ["5%", "tổng doanh thu"],
        },

        # VN_DOC_003
        {
            "question_id": "VN_ANS_009",
            "category": "answerable",
            "document_id": "VN_DOC_003",
            "expected_decision": "answer",
            "question": "Kinh thành Huế được khởi công xây dựng vào năm nào và hoàn thành dưới triều vua nào?",
            "target_passages": ["VN_DOC_003::P000"],
            "expected_keywords": ["1805", "Gia Long", "1832", "Minh Mạng"],
        },
        {
            "question_id": "VN_ANS_010",
            "category": "answerable",
            "document_id": "VN_DOC_003",
            "expected_decision": "answer",
            "question": "Bốn cổng chính của Hoàng thành Huế gồm những cổng nào?",
            "target_passages": ["VN_DOC_003::P001"],
            "expected_keywords": ["Ngọ Môn", "Hiển Nhơn", "Chương Đức", "Hòa Bình"],
        },
        {
            "question_id": "VN_ANS_011",
            "category": "answerable",
            "document_id": "VN_DOC_003",
            "expected_decision": "answer",
            "question": "Nhã nhạc Cung đình Huế được UNESCO công nhận là di sản văn hóa vào năm nào?",
            "target_passages": ["VN_DOC_003::P002"],
            "expected_keywords": ["2003", "UNESCO"],
        },
        {
            "question_id": "VN_ANS_012",
            "category": "answerable",
            "document_id": "VN_DOC_003",
            "expected_decision": "answer",
            "question": "Điện Kiến Trung tại Huế mở cửa đón khách tham quan vào dịp nào sau khi phục hồi?",
            "target_passages": ["VN_DOC_003::P004"],
            "expected_keywords": ["Tết Nguyên đán", "2024"],
        },

        # VN_DOC_004
        {
            "question_id": "VN_ANS_013",
            "category": "answerable",
            "document_id": "VN_DOC_004",
            "expected_decision": "answer",
            "question": "Ranh mặn 4 gam trên lít xâm nhập sâu bao nhiêu km vào đất liền tại Bến Tre và Trà Vinh?",
            "target_passages": ["VN_DOC_004::P000"],
            "expected_keywords": ["70 km", "Bến Tre", "Trà Vinh"],
        },
        {
            "question_id": "VN_ANS_014",
            "category": "answerable",
            "document_id": "VN_DOC_004",
            "expected_decision": "answer",
            "question": "Mô hình canh tác lúa - tôm thông minh giúp giảm bao nhiêu phần trăm lượng phân bón hóa học?",
            "target_passages": ["VN_DOC_004::P002"],
            "expected_keywords": ["60%", "phân bón"],
        },
        {
            "question_id": "VN_ANS_015",
            "category": "answerable",
            "document_id": "VN_DOC_004",
            "expected_decision": "answer",
            "question": "Những giống lúa chịu mặn nào được triển khai gieo cấy trên diện tích 150.000 héc-ta?",
            "target_passages": ["VN_DOC_004::P003"],
            "expected_keywords": ["ST25", "OM18"],
        },
        {
            "question_id": "VN_ANS_016",
            "category": "answerable",
            "document_id": "VN_DOC_004",
            "expected_decision": "answer",
            "question": "Hệ thống cống Cái Lớn - Cái Bé giúp kiểm soát nguồn nước ngọt cho bao nhiêu héc-ta đất nông nghiệp?",
            "target_passages": ["VN_DOC_004::P005"],
            "expected_keywords": ["384.000 héc-ta", "Cái Lớn - Cái Bé"],
        },

        # VN_DOC_005
        {
            "question_id": "VN_ANS_017",
            "category": "answerable",
            "document_id": "VN_DOC_005",
            "expected_decision": "answer",
            "question": "Quy hoạch điện VIII đặt mục tiêu tỷ lệ năng lượng tái tạo đạt bao nhiêu phần trăm vào năm 2030?",
            "target_passages": ["VN_DOC_005::P000"],
            "expected_keywords": ["30,9%", "39,2%", "2030"],
        },
        {
            "question_id": "VN_ANS_018",
            "category": "answerable",
            "document_id": "VN_DOC_005",
            "expected_decision": "answer",
            "question": "Công suất điện gió ngoài khơi theo Quy hoạch điện VIII dự kiến đạt bao nhiêu MW vào năm 2030?",
            "target_passages": ["VN_DOC_005::P001"],
            "expected_keywords": ["6.000 MW", "Nam Trung Bộ"],
        },
        {
            "question_id": "VN_ANS_019",
            "category": "answerable",
            "document_id": "VN_DOC_005",
            "expected_decision": "answer",
            "question": "Trạm lưu trữ pin BESS tại Bình Thuận có công suất là bao nhiêu?",
            "target_passages": ["VN_DOC_005::P002"],
            "expected_keywords": ["50 MW", "Bình Thuận", "BESS"],
        },
        {
            "question_id": "VN_ANS_020",
            "category": "answerable",
            "document_id": "VN_DOC_005",
            "expected_decision": "answer",
            "question": "Mức giá trần đối với dự án điện gió trên bờ trong khung giá chuyển tiếp là bao nhiêu đồng một kWh?",
            "target_passages": ["VN_DOC_005::P005"],
            "expected_keywords": ["1.587,12 đồng", "kilowatt giờ"],
        },

        # =====================================================================
        # 10 UNANSWERABLE QUESTIONS (Out-of-Domain)
        # =====================================================================
        {
            "question_id": "VN_UNANS_001",
            "category": "unanswerable",
            "document_id": None,
            "expected_decision": "refuse",
            "question": "Thủ đô của nước Úc là thành phố nào và có bao nhiêu dân số?",
            "target_passages": [],
            "expected_keywords": [],
        },
        {
            "question_id": "VN_UNANS_002",
            "category": "unanswerable",
            "document_id": None,
            "expected_decision": "refuse",
            "question": "Ai là tác giả của vở kịch kinh điển Hamlet được sáng tác vào thế kỷ 16?",
            "target_passages": [],
            "expected_keywords": [],
        },
        {
            "question_id": "VN_UNANS_003",
            "category": "unanswerable",
            "document_id": None,
            "expected_decision": "refuse",
            "question": "Tàu thám hiểm không gian Perseverance của NASA hạ cánh xuống sao Hỏa vào ngày tháng năm nào?",
            "target_passages": [],
            "expected_keywords": [],
        },
        {
            "question_id": "VN_UNANS_004",
            "category": "unanswerable",
            "document_id": None,
            "expected_decision": "refuse",
            "question": "Khoảng cách trung bình từ Trái Đất đến Mặt Trăng được đo đạc là bao nhiêu kilomet?",
            "target_passages": [],
            "expected_keywords": [],
        },
        {
            "question_id": "VN_UNANS_005",
            "category": "unanswerable",
            "document_id": None,
            "expected_decision": "refuse",
            "question": "Đội tuyển bóng đá quốc gia nào đã giành chức vô địch World Cup năm 1998 tại Pháp?",
            "target_passages": [],
            "expected_keywords": [],
        },
        {
            "question_id": "VN_UNANS_006",
            "category": "unanswerable",
            "document_id": None,
            "expected_decision": "refuse",
            "question": "Công thức hóa học và khối lượng mol phân tử của axit sulfuric đậm đặc là gì?",
            "target_passages": [],
            "expected_keywords": [],
        },
        {
            "question_id": "VN_UNANS_007",
            "category": "unanswerable",
            "document_id": None,
            "expected_decision": "refuse",
            "question": "Dãy núi Andes trải dài qua những quốc gia nào ở lục địa Nam Mỹ?",
            "target_passages": [],
            "expected_keywords": [],
        },
        {
            "question_id": "VN_UNANS_008",
            "category": "unanswerable",
            "document_id": None,
            "expected_decision": "refuse",
            "question": "Nhà phát minh Thomas Edison đã phát minh ra bóng đèn dây tóc vào năm bao nhiêu?",
            "target_passages": [],
            "expected_keywords": [],
        },
        {
            "question_id": "VN_UNANS_009",
            "category": "unanswerable",
            "document_id": None,
            "expected_decision": "refuse",
            "question": "Nhiệt độ sôi chính xác của nitơ lỏng ở áp suất khí quyển tiêu chuẩn là bao nhiêu độ C?",
            "target_passages": [],
            "expected_keywords": [],
        },
        {
            "question_id": "VN_UNANS_010",
            "category": "unanswerable",
            "document_id": None,
            "expected_decision": "refuse",
            "question": "Bức họa nổi tiếng Nàng Mona Lisa của họa sĩ Leonardo da Vinci hiện đang treo ở bảo tàng nào?",
            "target_passages": [],
            "expected_keywords": [],
        },

        # =====================================================================
        # 10 INSUFFICIENT EVIDENCE QUESTIONS (In-Domain terms, missing facts)
        # =====================================================================
        {
            "question_id": "VN_INSUFF_001",
            "category": "insufficient_evidence",
            "document_id": "VN_DOC_001",
            "expected_decision": "refuse",
            "question": "Trong tài liệu SA-CMS, tổng ngân sách tài trợ bằng tiền mặt năm 2024 của đề tài là bao nhiêu triệu đồng?",
            "target_passages": [],
            "expected_keywords": [],
        },
        {
            "question_id": "VN_INSUFF_002",
            "category": "insufficient_evidence",
            "document_id": "VN_DOC_001",
            "expected_decision": "refuse",
            "question": "Họ và tên của giảng viên hướng dẫn trực tiếp đề tài nghiên cứu SA-CMS là ai?",
            "target_passages": [],
            "expected_keywords": [],
        },
        {
            "question_id": "VN_INSUFF_003",
            "category": "insufficient_evidence",
            "document_id": "VN_DOC_002",
            "expected_decision": "refuse",
            "question": "Cá nhân nào là người đầu tiên bị khởi tố hình sự theo Nghị định 13/2023/NĐ-CP tại Việt Nam?",
            "target_passages": [],
            "expected_keywords": [],
        },
        {
            "question_id": "VN_INSUFF_004",
            "category": "insufficient_evidence",
            "document_id": "VN_DOC_002",
            "expected_decision": "refuse",
            "question": "Mã số thuế doanh nghiệp và số tài khoản ngân hàng của bên xử lý dữ liệu cá nhân theo Nghị định 13 là gì?",
            "target_passages": [],
            "expected_keywords": [],
        },
        {
            "question_id": "VN_INSUFF_005",
            "category": "insufficient_evidence",
            "document_id": "VN_DOC_003",
            "expected_decision": "refuse",
            "question": "Chi phí xây dựng chính xác bằng tiền đồng của Kinh thành Huế năm 1805 là bao nhiêu vạn quan tiền?",
            "target_passages": [],
            "expected_keywords": [],
        },
        {
            "question_id": "VN_INSUFF_006",
            "category": "insufficient_evidence",
            "document_id": "VN_DOC_003",
            "expected_decision": "refuse",
            "question": "Vua Minh Mạng đã dùng loại gỗ quý cụ thể nào để đóng cổng Hòa Bình ở phía Bắc Hoàng thành Huế?",
            "target_passages": [],
            "expected_keywords": [],
        },
        {
            "question_id": "VN_INSUFF_007",
            "category": "insufficient_evidence",
            "document_id": "VN_DOC_004",
            "expected_decision": "refuse",
            "question": "Số lượng cá heo nước ngọt còn lại ở sông Tiền sau khi xây dựng cống Cái Lớn là bao nhiêu con?",
            "target_passages": [],
            "expected_keywords": [],
        },
        {
            "question_id": "VN_INSUFF_008",
            "category": "insufficient_evidence",
            "document_id": "VN_DOC_004",
            "expected_decision": "refuse",
            "question": "Tên và quê quán của vị giáo sư nông nghiệp đã phát minh ra giống lúa ST25 là ai?",
            "target_passages": [],
            "expected_keywords": [],
        },
        {
            "question_id": "VN_INSUFF_009",
            "category": "insufficient_evidence",
            "document_id": "VN_DOC_005",
            "expected_decision": "refuse",
            "question": "Tập đoàn Điện lực Việt Nam đã mua bao nhiêu tấn lithium từ Chile để làm pin BESS tại Bình Thuận?",
            "target_passages": [],
            "expected_keywords": [],
        },
        {
            "question_id": "VN_INSUFF_010",
            "category": "insufficient_evidence",
            "document_id": "VN_DOC_005",
            "expected_decision": "refuse",
            "question": "Họ và tên của giám đốc ban quản lý dự án điện gió ngoài khơi Nam Trung Bộ là ai?",
            "target_passages": [],
            "expected_keywords": [],
        },
    ]
