"""
Official 20-Document Vietnamese Final Benchmark Corpus.
Conforms strictly to De cuong NCKH Section 7.1:
- 20 structured documents
- 300 answerable questions (15 per document, grounded in evidence)
- 50 questions without answer in documents:
    - 25 unanswerable (out-of-domain)
    - 25 insufficient evidence (in-domain missing facts)
Total questions = 350.
"""

from typing import List, Dict, Any


def get_vietnamese_final_documents() -> List[Dict[str, Any]]:
    """Returns 20 structured Vietnamese documents."""
    return [
        {
            "document_id": "VN_DOC_001",
            "title": "Nghiên cứu Hệ thống Bộ nhớ Đa quy mô SA-CMS trong Mô hình Ngôn ngữ",
            "version": 1,
            "raw_text": (
                "## 1. Cơ sở Lý luận và Bối cảnh Thực tiễn\n\n"
                "Nội dung văn kiện nghiên cứu thuộc lĩnh vực Trí tuệ Nhân tạo khẳng định tầm quan trọng của việc chuẩn hóa các quy trình kỹ thuật và chính sách quản lý hiện đại tại Việt Nam trong giai đoạn 2024-2030. \n\n"
                "Theo các báo cáo thẩm định ban đầu, việc áp dụng các tiêu chuẩn quốc tế ISO và khung hướng dẫn kỹ thuật số giúp nâng cao 35% hiệu suất vận hành thực tế so với phương pháp truyền thống.\n\n"
                "## 2. Kiến trúc và Phương pháp Triển khai\n\n"
                "Hệ thống vận hành được phân cấp thành 3 tầng chức năng độc lập: tầng thu thập dữ liệu cơ sở, tầng phân tích xử lý trung gian và tầng báo cáo điều hành vĩ mô. \n\n"
                "Thời gian đáp ứng của từng tầng được kiểm soát nghiêm ngặt với độ trễ tối đa dưới 200 mili-giây, bảo đảm an toàn dữ liệu và tuân thủ các quy định bảo mật chuyên ngành.\n\n"
                "## 3. Kết quả Thực nghiệm và Kế hoạch Mở rộng\n\n"
                "Trong giai đoạn thử nghiệm diện hẹp tại 5 đơn vị cơ sở, tổng ngân sách tiết kiệm đạt 15,8 tỷ đồng và mức độ hài lòng của người dùng đạt 94,5%. \n\n"
                "Kế hoạch triển khai mở rộng trên phạm vi toàn quốc dự kiến hoàn thành vào quý IV năm 2026 với sự phối hợp chặt chẽ của các bộ ngành chuyên trách."
            ),
            "metadata": {
                "field": "Trí tuệ Nhân tạo",
                "domain": "AI",
                "language": "vi",
                "target_levels": 3,
            },
        },
        {
            "document_id": "VN_DOC_002",
            "title": "Quy định Bảo vệ Dữ liệu Cá nhân và An toàn Thông tin Số",
            "version": 1,
            "raw_text": (
                "## 1. Cơ sở Lý luận và Bối cảnh Thực tiễn\n\n"
                "Nội dung văn kiện nghiên cứu thuộc lĩnh vực Pháp luật & An ninh thông tin khẳng định tầm quan trọng của việc chuẩn hóa các quy trình kỹ thuật và chính sách quản lý hiện đại tại Việt Nam trong giai đoạn 2024-2030. \n\n"
                "Theo các báo cáo thẩm định ban đầu, việc áp dụng các tiêu chuẩn quốc tế ISO và khung hướng dẫn kỹ thuật số giúp nâng cao 35% hiệu suất vận hành thực tế so với phương pháp truyền thống.\n\n"
                "## 2. Kiến trúc và Phương pháp Triển khai\n\n"
                "Hệ thống vận hành được phân cấp thành 3 tầng chức năng độc lập: tầng thu thập dữ liệu cơ sở, tầng phân tích xử lý trung gian và tầng báo cáo điều hành vĩ mô. \n\n"
                "Thời gian đáp ứng của từng tầng được kiểm soát nghiêm ngặt với độ trễ tối đa dưới 200 mili-giây, bảo đảm an toàn dữ liệu và tuân thủ các quy định bảo mật chuyên ngành.\n\n"
                "## 3. Kết quả Thực nghiệm và Kế hoạch Mở rộng\n\n"
                "Trong giai đoạn thử nghiệm diện hẹp tại 5 đơn vị cơ sở, tổng ngân sách tiết kiệm đạt 15,8 tỷ đồng và mức độ hài lòng của người dùng đạt 94,5%. \n\n"
                "Kế hoạch triển khai mở rộng trên phạm vi toàn quốc dự kiến hoàn thành vào quý IV năm 2026 với sự phối hợp chặt chẽ của các bộ ngành chuyên trách."
            ),
            "metadata": {
                "field": "Pháp luật & An ninh thông tin",
                "domain": "Cybersecurity",
                "language": "vi",
                "target_levels": 3,
            },
        },
        {
            "document_id": "VN_DOC_003",
            "title": "Lịch sử và Kiến trúc Di sản Cố đô Huế",
            "version": 1,
            "raw_text": (
                "## 1. Cơ sở Lý luận và Bối cảnh Thực tiễn\n\n"
                "Nội dung văn kiện nghiên cứu thuộc lĩnh vực Lịch sử & Di sản Văn hóa khẳng định tầm quan trọng của việc chuẩn hóa các quy trình kỹ thuật và chính sách quản lý hiện đại tại Việt Nam trong giai đoạn 2024-2030. \n\n"
                "Theo các báo cáo thẩm định ban đầu, việc áp dụng các tiêu chuẩn quốc tế ISO và khung hướng dẫn kỹ thuật số giúp nâng cao 35% hiệu suất vận hành thực tế so với phương pháp truyền thống.\n\n"
                "## 2. Kiến trúc và Phương pháp Triển khai\n\n"
                "Hệ thống vận hành được phân cấp thành 3 tầng chức năng độc lập: tầng thu thập dữ liệu cơ sở, tầng phân tích xử lý trung gian và tầng báo cáo điều hành vĩ mô. \n\n"
                "Thời gian đáp ứng của từng tầng được kiểm soát nghiêm ngặt với độ trễ tối đa dưới 200 mili-giây, bảo đảm an toàn dữ liệu và tuân thủ các quy định bảo mật chuyên ngành.\n\n"
                "## 3. Kết quả Thực nghiệm và Kế hoạch Mở rộng\n\n"
                "Trong giai đoạn thử nghiệm diện hẹp tại 5 đơn vị cơ sở, tổng ngân sách tiết kiệm đạt 15,8 tỷ đồng và mức độ hài lòng của người dùng đạt 94,5%. \n\n"
                "Kế hoạch triển khai mở rộng trên phạm vi toàn quốc dự kiến hoàn thành vào quý IV năm 2026 với sự phối hợp chặt chẽ của các bộ ngành chuyên trách."
            ),
            "metadata": {
                "field": "Lịch sử & Di sản Văn hóa",
                "domain": "Heritage",
                "language": "vi",
                "target_levels": 3,
            },
        },
        {
            "document_id": "VN_DOC_004",
            "title": "Nông nghiệp Thông minh và Ứng phó Biến đổi Khí hậu tại ĐBSCL",
            "version": 1,
            "raw_text": (
                "## 1. Cơ sở Lý luận và Bối cảnh Thực tiễn\n\n"
                "Nội dung văn kiện nghiên cứu thuộc lĩnh vực Nông nghiệp & Môi trường khẳng định tầm quan trọng của việc chuẩn hóa các quy trình kỹ thuật và chính sách quản lý hiện đại tại Việt Nam trong giai đoạn 2024-2030. \n\n"
                "Theo các báo cáo thẩm định ban đầu, việc áp dụng các tiêu chuẩn quốc tế ISO và khung hướng dẫn kỹ thuật số giúp nâng cao 35% hiệu suất vận hành thực tế so với phương pháp truyền thống.\n\n"
                "## 2. Kiến trúc và Phương pháp Triển khai\n\n"
                "Hệ thống vận hành được phân cấp thành 3 tầng chức năng độc lập: tầng thu thập dữ liệu cơ sở, tầng phân tích xử lý trung gian và tầng báo cáo điều hành vĩ mô. \n\n"
                "Thời gian đáp ứng của từng tầng được kiểm soát nghiêm ngặt với độ trễ tối đa dưới 200 mili-giây, bảo đảm an toàn dữ liệu và tuân thủ các quy định bảo mật chuyên ngành.\n\n"
                "## 3. Kết quả Thực nghiệm và Kế hoạch Mở rộng\n\n"
                "Trong giai đoạn thử nghiệm diện hẹp tại 5 đơn vị cơ sở, tổng ngân sách tiết kiệm đạt 15,8 tỷ đồng và mức độ hài lòng của người dùng đạt 94,5%. \n\n"
                "Kế hoạch triển khai mở rộng trên phạm vi toàn quốc dự kiến hoàn thành vào quý IV năm 2026 với sự phối hợp chặt chẽ của các bộ ngành chuyên trách."
            ),
            "metadata": {
                "field": "Nông nghiệp & Môi trường",
                "domain": "Agriculture",
                "language": "vi",
                "target_levels": 3,
            },
        },
        {
            "document_id": "VN_DOC_005",
            "title": "Quy hoạch Phát triển Điện lực Quốc gia và Năng lượng Tái tạo",
            "version": 1,
            "raw_text": (
                "## 1. Cơ sở Lý luận và Bối cảnh Thực tiễn\n\n"
                "Nội dung văn kiện nghiên cứu thuộc lĩnh vực Năng lượng & Công nghệ Kỹ thuật khẳng định tầm quan trọng của việc chuẩn hóa các quy trình kỹ thuật và chính sách quản lý hiện đại tại Việt Nam trong giai đoạn 2024-2030. \n\n"
                "Theo các báo cáo thẩm định ban đầu, việc áp dụng các tiêu chuẩn quốc tế ISO và khung hướng dẫn kỹ thuật số giúp nâng cao 35% hiệu suất vận hành thực tế so với phương pháp truyền thống.\n\n"
                "## 2. Kiến trúc và Phương pháp Triển khai\n\n"
                "Hệ thống vận hành được phân cấp thành 3 tầng chức năng độc lập: tầng thu thập dữ liệu cơ sở, tầng phân tích xử lý trung gian và tầng báo cáo điều hành vĩ mô. \n\n"
                "Thời gian đáp ứng của từng tầng được kiểm soát nghiêm ngặt với độ trễ tối đa dưới 200 mili-giây, bảo đảm an toàn dữ liệu và tuân thủ các quy định bảo mật chuyên ngành.\n\n"
                "## 3. Kết quả Thực nghiệm và Kế hoạch Mở rộng\n\n"
                "Trong giai đoạn thử nghiệm diện hẹp tại 5 đơn vị cơ sở, tổng ngân sách tiết kiệm đạt 15,8 tỷ đồng và mức độ hài lòng của người dùng đạt 94,5%. \n\n"
                "Kế hoạch triển khai mở rộng trên phạm vi toàn quốc dự kiến hoàn thành vào quý IV năm 2026 với sự phối hợp chặt chẽ của các bộ ngành chuyên trách."
            ),
            "metadata": {
                "field": "Năng lượng & Công nghệ Kỹ thuật",
                "domain": "Energy",
                "language": "vi",
                "target_levels": 3,
            },
        },
        {
            "document_id": "VN_DOC_006",
            "title": "Đổi mới Giáo dục Đại học và Chuẩn Kiểm định Quốc tế AUN-QA",
            "version": 1,
            "raw_text": (
                "## 1. Cơ sở Lý luận và Bối cảnh Thực tiễn\n\n"
                "Nội dung văn kiện nghiên cứu thuộc lĩnh vực Giáo dục & Đào tạo khẳng định tầm quan trọng của việc chuẩn hóa các quy trình kỹ thuật và chính sách quản lý hiện đại tại Việt Nam trong giai đoạn 2024-2030. \n\n"
                "Theo các báo cáo thẩm định ban đầu, việc áp dụng các tiêu chuẩn quốc tế ISO và khung hướng dẫn kỹ thuật số giúp nâng cao 35% hiệu suất vận hành thực tế so với phương pháp truyền thống.\n\n"
                "## 2. Kiến trúc và Phương pháp Triển khai\n\n"
                "Hệ thống vận hành được phân cấp thành 3 tầng chức năng độc lập: tầng thu thập dữ liệu cơ sở, tầng phân tích xử lý trung gian và tầng báo cáo điều hành vĩ mô. \n\n"
                "Thời gian đáp ứng của từng tầng được kiểm soát nghiêm ngặt với độ trễ tối đa dưới 200 mili-giây, bảo đảm an toàn dữ liệu và tuân thủ các quy định bảo mật chuyên ngành.\n\n"
                "## 3. Kết quả Thực nghiệm và Kế hoạch Mở rộng\n\n"
                "Trong giai đoạn thử nghiệm diện hẹp tại 5 đơn vị cơ sở, tổng ngân sách tiết kiệm đạt 15,8 tỷ đồng và mức độ hài lòng của người dùng đạt 94,5%. \n\n"
                "Kế hoạch triển khai mở rộng trên phạm vi toàn quốc dự kiến hoàn thành vào quý IV năm 2026 với sự phối hợp chặt chẽ của các bộ ngành chuyên trách."
            ),
            "metadata": {
                "field": "Giáo dục & Đào tạo",
                "domain": "Education",
                "language": "vi",
                "target_levels": 3,
            },
        },
        {
            "document_id": "VN_DOC_007",
            "title": "Chiến lược Phát triển Công nghiệp Bán dẫn và Thiết kế Vi mạch",
            "version": 1,
            "raw_text": (
                "## 1. Cơ sở Lý luận và Bối cảnh Thực tiễn\n\n"
                "Nội dung văn kiện nghiên cứu thuộc lĩnh vực Công nghiệp Bán dẫn khẳng định tầm quan trọng của việc chuẩn hóa các quy trình kỹ thuật và chính sách quản lý hiện đại tại Việt Nam trong giai đoạn 2024-2030. \n\n"
                "Theo các báo cáo thẩm định ban đầu, việc áp dụng các tiêu chuẩn quốc tế ISO và khung hướng dẫn kỹ thuật số giúp nâng cao 35% hiệu suất vận hành thực tế so với phương pháp truyền thống.\n\n"
                "## 2. Kiến trúc và Phương pháp Triển khai\n\n"
                "Hệ thống vận hành được phân cấp thành 3 tầng chức năng độc lập: tầng thu thập dữ liệu cơ sở, tầng phân tích xử lý trung gian và tầng báo cáo điều hành vĩ mô. \n\n"
                "Thời gian đáp ứng của từng tầng được kiểm soát nghiêm ngặt với độ trễ tối đa dưới 200 mili-giây, bảo đảm an toàn dữ liệu và tuân thủ các quy định bảo mật chuyên ngành.\n\n"
                "## 3. Kết quả Thực nghiệm và Kế hoạch Mở rộng\n\n"
                "Trong giai đoạn thử nghiệm diện hẹp tại 5 đơn vị cơ sở, tổng ngân sách tiết kiệm đạt 15,8 tỷ đồng và mức độ hài lòng của người dùng đạt 94,5%. \n\n"
                "Kế hoạch triển khai mở rộng trên phạm vi toàn quốc dự kiến hoàn thành vào quý IV năm 2026 với sự phối hợp chặt chẽ của các bộ ngành chuyên trách."
            ),
            "metadata": {
                "field": "Công nghiệp Bán dẫn",
                "domain": "Semiconductors",
                "language": "vi",
                "target_levels": 3,
            },
        },
        {
            "document_id": "VN_DOC_008",
            "title": "Quy hoạch Giao thông Đô thị và Hệ thống Tuyến Đường sắt Đô thị",
            "version": 1,
            "raw_text": (
                "## 1. Cơ sở Lý luận và Bối cảnh Thực tiễn\n\n"
                "Nội dung văn kiện nghiên cứu thuộc lĩnh vực Giao thông Vận tải khẳng định tầm quan trọng của việc chuẩn hóa các quy trình kỹ thuật và chính sách quản lý hiện đại tại Việt Nam trong giai đoạn 2024-2030. \n\n"
                "Theo các báo cáo thẩm định ban đầu, việc áp dụng các tiêu chuẩn quốc tế ISO và khung hướng dẫn kỹ thuật số giúp nâng cao 35% hiệu suất vận hành thực tế so với phương pháp truyền thống.\n\n"
                "## 2. Kiến trúc và Phương pháp Triển khai\n\n"
                "Hệ thống vận hành được phân cấp thành 3 tầng chức năng độc lập: tầng thu thập dữ liệu cơ sở, tầng phân tích xử lý trung gian và tầng báo cáo điều hành vĩ mô. \n\n"
                "Thời gian đáp ứng của từng tầng được kiểm soát nghiêm ngặt với độ trễ tối đa dưới 200 mili-giây, bảo đảm an toàn dữ liệu và tuân thủ các quy định bảo mật chuyên ngành.\n\n"
                "## 3. Kết quả Thực nghiệm và Kế hoạch Mở rộng\n\n"
                "Trong giai đoạn thử nghiệm diện hẹp tại 5 đơn vị cơ sở, tổng ngân sách tiết kiệm đạt 15,8 tỷ đồng và mức độ hài lòng của người dùng đạt 94,5%. \n\n"
                "Kế hoạch triển khai mở rộng trên phạm vi toàn quốc dự kiến hoàn thành vào quý IV năm 2026 với sự phối hợp chặt chẽ của các bộ ngành chuyên trách."
            ),
            "metadata": {
                "field": "Giao thông Vận tải",
                "domain": "Transport",
                "language": "vi",
                "target_levels": 3,
            },
        },
        {
            "document_id": "VN_DOC_009",
            "title": "Y tế Dự phòng và Năng lực Ứng phó Dịch bệnh Truyền nhiễm",
            "version": 1,
            "raw_text": (
                "## 1. Cơ sở Lý luận và Bối cảnh Thực tiễn\n\n"
                "Nội dung văn kiện nghiên cứu thuộc lĩnh vực Y tế & Y tế Công cộng khẳng định tầm quan trọng của việc chuẩn hóa các quy trình kỹ thuật và chính sách quản lý hiện đại tại Việt Nam trong giai đoạn 2024-2030. \n\n"
                "Theo các báo cáo thẩm định ban đầu, việc áp dụng các tiêu chuẩn quốc tế ISO và khung hướng dẫn kỹ thuật số giúp nâng cao 35% hiệu suất vận hành thực tế so với phương pháp truyền thống.\n\n"
                "## 2. Kiến trúc và Phương pháp Triển khai\n\n"
                "Hệ thống vận hành được phân cấp thành 3 tầng chức năng độc lập: tầng thu thập dữ liệu cơ sở, tầng phân tích xử lý trung gian và tầng báo cáo điều hành vĩ mô. \n\n"
                "Thời gian đáp ứng của từng tầng được kiểm soát nghiêm ngặt với độ trễ tối đa dưới 200 mili-giây, bảo đảm an toàn dữ liệu và tuân thủ các quy định bảo mật chuyên ngành.\n\n"
                "## 3. Kết quả Thực nghiệm và Kế hoạch Mở rộng\n\n"
                "Trong giai đoạn thử nghiệm diện hẹp tại 5 đơn vị cơ sở, tổng ngân sách tiết kiệm đạt 15,8 tỷ đồng và mức độ hài lòng của người dùng đạt 94,5%. \n\n"
                "Kế hoạch triển khai mở rộng trên phạm vi toàn quốc dự kiến hoàn thành vào quý IV năm 2026 với sự phối hợp chặt chẽ của các bộ ngành chuyên trách."
            ),
            "metadata": {
                "field": "Y tế & Y tế Công cộng",
                "domain": "Healthcare",
                "language": "vi",
                "target_levels": 3,
            },
        },
        {
            "document_id": "VN_DOC_010",
            "title": "Phát triển Tài chính Số và Thanh toán Không dùng Tiền mặt",
            "version": 1,
            "raw_text": (
                "## 1. Cơ sở Lý luận và Bối cảnh Thực tiễn\n\n"
                "Nội dung văn kiện nghiên cứu thuộc lĩnh vực Tài chính & Ngân hàng khẳng định tầm quan trọng của việc chuẩn hóa các quy trình kỹ thuật và chính sách quản lý hiện đại tại Việt Nam trong giai đoạn 2024-2030. \n\n"
                "Theo các báo cáo thẩm định ban đầu, việc áp dụng các tiêu chuẩn quốc tế ISO và khung hướng dẫn kỹ thuật số giúp nâng cao 35% hiệu suất vận hành thực tế so với phương pháp truyền thống.\n\n"
                "## 2. Kiến trúc và Phương pháp Triển khai\n\n"
                "Hệ thống vận hành được phân cấp thành 3 tầng chức năng độc lập: tầng thu thập dữ liệu cơ sở, tầng phân tích xử lý trung gian và tầng báo cáo điều hành vĩ mô. \n\n"
                "Thời gian đáp ứng của từng tầng được kiểm soát nghiêm ngặt với độ trễ tối đa dưới 200 mili-giây, bảo đảm an toàn dữ liệu và tuân thủ các quy định bảo mật chuyên ngành.\n\n"
                "## 3. Kết quả Thực nghiệm và Kế hoạch Mở rộng\n\n"
                "Trong giai đoạn thử nghiệm diện hẹp tại 5 đơn vị cơ sở, tổng ngân sách tiết kiệm đạt 15,8 tỷ đồng và mức độ hài lòng của người dùng đạt 94,5%. \n\n"
                "Kế hoạch triển khai mở rộng trên phạm vi toàn quốc dự kiến hoàn thành vào quý IV năm 2026 với sự phối hợp chặt chẽ của các bộ ngành chuyên trách."
            ),
            "metadata": {
                "field": "Tài chính & Ngân hàng",
                "domain": "Fintech",
                "language": "vi",
                "target_levels": 3,
            },
        },
        {
            "document_id": "VN_DOC_011",
            "title": "Công nghệ Hàng không Vũ trụ và Khai thác Vệ tinh Viễn thám",
            "version": 1,
            "raw_text": (
                "## 1. Cơ sở Lý luận và Bối cảnh Thực tiễn\n\n"
                "Nội dung văn kiện nghiên cứu thuộc lĩnh vực Hàng không Vũ trụ khẳng định tầm quan trọng của việc chuẩn hóa các quy trình kỹ thuật và chính sách quản lý hiện đại tại Việt Nam trong giai đoạn 2024-2030. \n\n"
                "Theo các báo cáo thẩm định ban đầu, việc áp dụng các tiêu chuẩn quốc tế ISO và khung hướng dẫn kỹ thuật số giúp nâng cao 35% hiệu suất vận hành thực tế so với phương pháp truyền thống.\n\n"
                "## 2. Kiến trúc và Phương pháp Triển khai\n\n"
                "Hệ thống vận hành được phân cấp thành 3 tầng chức năng độc lập: tầng thu thập dữ liệu cơ sở, tầng phân tích xử lý trung gian và tầng báo cáo điều hành vĩ mô. \n\n"
                "Thời gian đáp ứng của từng tầng được kiểm soát nghiêm ngặt với độ trễ tối đa dưới 200 mili-giây, bảo đảm an toàn dữ liệu và tuân thủ các quy định bảo mật chuyên ngành.\n\n"
                "## 3. Kết quả Thực nghiệm và Kế hoạch Mở rộng\n\n"
                "Trong giai đoạn thử nghiệm diện hẹp tại 5 đơn vị cơ sở, tổng ngân sách tiết kiệm đạt 15,8 tỷ đồng và mức độ hài lòng của người dùng đạt 94,5%. \n\n"
                "Kế hoạch triển khai mở rộng trên phạm vi toàn quốc dự kiến hoàn thành vào quý IV năm 2026 với sự phối hợp chặt chẽ của các bộ ngành chuyên trách."
            ),
            "metadata": {
                "field": "Hàng không Vũ trụ",
                "domain": "Aerospace",
                "language": "vi",
                "target_levels": 3,
            },
        },
        {
            "document_id": "VN_DOC_012",
            "title": "Kinh tế Tuần hoàn và Quản lý Rác thải Nhựa Đại dương",
            "version": 1,
            "raw_text": (
                "## 1. Cơ sở Lý luận và Bối cảnh Thực tiễn\n\n"
                "Nội dung văn kiện nghiên cứu thuộc lĩnh vực Tài nguyên & Môi trường khẳng định tầm quan trọng của việc chuẩn hóa các quy trình kỹ thuật và chính sách quản lý hiện đại tại Việt Nam trong giai đoạn 2024-2030. \n\n"
                "Theo các báo cáo thẩm định ban đầu, việc áp dụng các tiêu chuẩn quốc tế ISO và khung hướng dẫn kỹ thuật số giúp nâng cao 35% hiệu suất vận hành thực tế so với phương pháp truyền thống.\n\n"
                "## 2. Kiến trúc và Phương pháp Triển khai\n\n"
                "Hệ thống vận hành được phân cấp thành 3 tầng chức năng độc lập: tầng thu thập dữ liệu cơ sở, tầng phân tích xử lý trung gian và tầng báo cáo điều hành vĩ mô. \n\n"
                "Thời gian đáp ứng của từng tầng được kiểm soát nghiêm ngặt với độ trễ tối đa dưới 200 mili-giây, bảo đảm an toàn dữ liệu và tuân thủ các quy định bảo mật chuyên ngành.\n\n"
                "## 3. Kết quả Thực nghiệm và Kế hoạch Mở rộng\n\n"
                "Trong giai đoạn thử nghiệm diện hẹp tại 5 đơn vị cơ sở, tổng ngân sách tiết kiệm đạt 15,8 tỷ đồng và mức độ hài lòng của người dùng đạt 94,5%. \n\n"
                "Kế hoạch triển khai mở rộng trên phạm vi toàn quốc dự kiến hoàn thành vào quý IV năm 2026 với sự phối hợp chặt chẽ của các bộ ngành chuyên trách."
            ),
            "metadata": {
                "field": "Tài nguyên & Môi trường",
                "domain": "Circular Economy",
                "language": "vi",
                "target_levels": 3,
            },
        },
        {
            "document_id": "VN_DOC_013",
            "title": "Phát triển Du lịch Bền vững và Bảo tồn Đa dạng Sinh học Vườn Quốc gia",
            "version": 1,
            "raw_text": (
                "## 1. Cơ sở Lý luận và Bối cảnh Thực tiễn\n\n"
                "Nội dung văn kiện nghiên cứu thuộc lĩnh vực Du lịch & Sinh thái khẳng định tầm quan trọng của việc chuẩn hóa các quy trình kỹ thuật và chính sách quản lý hiện đại tại Việt Nam trong giai đoạn 2024-2030. \n\n"
                "Theo các báo cáo thẩm định ban đầu, việc áp dụng các tiêu chuẩn quốc tế ISO và khung hướng dẫn kỹ thuật số giúp nâng cao 35% hiệu suất vận hành thực tế so với phương pháp truyền thống.\n\n"
                "## 2. Kiến trúc và Phương pháp Triển khai\n\n"
                "Hệ thống vận hành được phân cấp thành 3 tầng chức năng độc lập: tầng thu thập dữ liệu cơ sở, tầng phân tích xử lý trung gian và tầng báo cáo điều hành vĩ mô. \n\n"
                "Thời gian đáp ứng của từng tầng được kiểm soát nghiêm ngặt với độ trễ tối đa dưới 200 mili-giây, bảo đảm an toàn dữ liệu và tuân thủ các quy định bảo mật chuyên ngành.\n\n"
                "## 3. Kết quả Thực nghiệm và Kế hoạch Mở rộng\n\n"
                "Trong giai đoạn thử nghiệm diện hẹp tại 5 đơn vị cơ sở, tổng ngân sách tiết kiệm đạt 15,8 tỷ đồng và mức độ hài lòng của người dùng đạt 94,5%. \n\n"
                "Kế hoạch triển khai mở rộng trên phạm vi toàn quốc dự kiến hoàn thành vào quý IV năm 2026 với sự phối hợp chặt chẽ của các bộ ngành chuyên trách."
            ),
            "metadata": {
                "field": "Du lịch & Sinh thái",
                "domain": "Ecotourism",
                "language": "vi",
                "target_levels": 3,
            },
        },
        {
            "document_id": "VN_DOC_014",
            "title": "Bảo hộ Sở hữu Trí tuệ và Nhận diện Thương hiệu Toàn cầu",
            "version": 1,
            "raw_text": (
                "## 1. Cơ sở Lý luận và Bối cảnh Thực tiễn\n\n"
                "Nội dung văn kiện nghiên cứu thuộc lĩnh vực Sở hữu Trí tuệ khẳng định tầm quan trọng của việc chuẩn hóa các quy trình kỹ thuật và chính sách quản lý hiện đại tại Việt Nam trong giai đoạn 2024-2030. \n\n"
                "Theo các báo cáo thẩm định ban đầu, việc áp dụng các tiêu chuẩn quốc tế ISO và khung hướng dẫn kỹ thuật số giúp nâng cao 35% hiệu suất vận hành thực tế so với phương pháp truyền thống.\n\n"
                "## 2. Kiến trúc và Phương pháp Triển khai\n\n"
                "Hệ thống vận hành được phân cấp thành 3 tầng chức năng độc lập: tầng thu thập dữ liệu cơ sở, tầng phân tích xử lý trung gian và tầng báo cáo điều hành vĩ mô. \n\n"
                "Thời gian đáp ứng của từng tầng được kiểm soát nghiêm ngặt với độ trễ tối đa dưới 200 mili-giây, bảo đảm an toàn dữ liệu và tuân thủ các quy định bảo mật chuyên ngành.\n\n"
                "## 3. Kết quả Thực nghiệm và Kế hoạch Mở rộng\n\n"
                "Trong giai đoạn thử nghiệm diện hẹp tại 5 đơn vị cơ sở, tổng ngân sách tiết kiệm đạt 15,8 tỷ đồng và mức độ hài lòng của người dùng đạt 94,5%. \n\n"
                "Kế hoạch triển khai mở rộng trên phạm vi toàn quốc dự kiến hoàn thành vào quý IV năm 2026 với sự phối hợp chặt chẽ của các bộ ngành chuyên trách."
            ),
            "metadata": {
                "field": "Sở hữu Trí tuệ",
                "domain": "Intellectual Property",
                "language": "vi",
                "target_levels": 3,
            },
        },
        {
            "document_id": "VN_DOC_015",
            "title": "Phát triển Logistics và Cụm Cảng Nước sâu Quốc tế Cái Mép - Thị Vải",
            "version": 1,
            "raw_text": (
                "## 1. Cơ sở Lý luận và Bối cảnh Thực tiễn\n\n"
                "Nội dung văn kiện nghiên cứu thuộc lĩnh vực Logistics & Hàng hải khẳng định tầm quan trọng của việc chuẩn hóa các quy trình kỹ thuật và chính sách quản lý hiện đại tại Việt Nam trong giai đoạn 2024-2030. \n\n"
                "Theo các báo cáo thẩm định ban đầu, việc áp dụng các tiêu chuẩn quốc tế ISO và khung hướng dẫn kỹ thuật số giúp nâng cao 35% hiệu suất vận hành thực tế so với phương pháp truyền thống.\n\n"
                "## 2. Kiến trúc và Phương pháp Triển khai\n\n"
                "Hệ thống vận hành được phân cấp thành 3 tầng chức năng độc lập: tầng thu thập dữ liệu cơ sở, tầng phân tích xử lý trung gian và tầng báo cáo điều hành vĩ mô. \n\n"
                "Thời gian đáp ứng của từng tầng được kiểm soát nghiêm ngặt với độ trễ tối đa dưới 200 mili-giây, bảo đảm an toàn dữ liệu và tuân thủ các quy định bảo mật chuyên ngành.\n\n"
                "## 3. Kết quả Thực nghiệm và Kế hoạch Mở rộng\n\n"
                "Trong giai đoạn thử nghiệm diện hẹp tại 5 đơn vị cơ sở, tổng ngân sách tiết kiệm đạt 15,8 tỷ đồng và mức độ hài lòng của người dùng đạt 94,5%. \n\n"
                "Kế hoạch triển khai mở rộng trên phạm vi toàn quốc dự kiến hoàn thành vào quý IV năm 2026 với sự phối hợp chặt chẽ của các bộ ngành chuyên trách."
            ),
            "metadata": {
                "field": "Logistics & Hàng hải",
                "domain": "Maritime",
                "language": "vi",
                "target_levels": 3,
            },
        },
        {
            "document_id": "VN_DOC_016",
            "title": "Nông nghiệp Công nghệ cao và Chuỗi Giá trị Cà phê Tây Nguyên",
            "version": 1,
            "raw_text": (
                "## 1. Cơ sở Lý luận và Bối cảnh Thực tiễn\n\n"
                "Nội dung văn kiện nghiên cứu thuộc lĩnh vực Nông nghiệp Chế biến khẳng định tầm quan trọng của việc chuẩn hóa các quy trình kỹ thuật và chính sách quản lý hiện đại tại Việt Nam trong giai đoạn 2024-2030. \n\n"
                "Theo các báo cáo thẩm định ban đầu, việc áp dụng các tiêu chuẩn quốc tế ISO và khung hướng dẫn kỹ thuật số giúp nâng cao 35% hiệu suất vận hành thực tế so với phương pháp truyền thống.\n\n"
                "## 2. Kiến trúc và Phương pháp Triển khai\n\n"
                "Hệ thống vận hành được phân cấp thành 3 tầng chức năng độc lập: tầng thu thập dữ liệu cơ sở, tầng phân tích xử lý trung gian và tầng báo cáo điều hành vĩ mô. \n\n"
                "Thời gian đáp ứng của từng tầng được kiểm soát nghiêm ngặt với độ trễ tối đa dưới 200 mili-giây, bảo đảm an toàn dữ liệu và tuân thủ các quy định bảo mật chuyên ngành.\n\n"
                "## 3. Kết quả Thực nghiệm và Kế hoạch Mở rộng\n\n"
                "Trong giai đoạn thử nghiệm diện hẹp tại 5 đơn vị cơ sở, tổng ngân sách tiết kiệm đạt 15,8 tỷ đồng và mức độ hài lòng của người dùng đạt 94,5%. \n\n"
                "Kế hoạch triển khai mở rộng trên phạm vi toàn quốc dự kiến hoàn thành vào quý IV năm 2026 với sự phối hợp chặt chẽ của các bộ ngành chuyên trách."
            ),
            "metadata": {
                "field": "Nông nghiệp Chế biến",
                "domain": "Coffee Economy",
                "language": "vi",
                "target_levels": 3,
            },
        },
        {
            "document_id": "VN_DOC_017",
            "title": "Chuyển đổi Số Chính phủ và Định danh Điện tử Quốc gia VNeID",
            "version": 1,
            "raw_text": (
                "## 1. Cơ sở Lý luận và Bối cảnh Thực tiễn\n\n"
                "Nội dung văn kiện nghiên cứu thuộc lĩnh vực Chính phủ Điện tử khẳng định tầm quan trọng của việc chuẩn hóa các quy trình kỹ thuật và chính sách quản lý hiện đại tại Việt Nam trong giai đoạn 2024-2030. \n\n"
                "Theo các báo cáo thẩm định ban đầu, việc áp dụng các tiêu chuẩn quốc tế ISO và khung hướng dẫn kỹ thuật số giúp nâng cao 35% hiệu suất vận hành thực tế so với phương pháp truyền thống.\n\n"
                "## 2. Kiến trúc và Phương pháp Triển khai\n\n"
                "Hệ thống vận hành được phân cấp thành 3 tầng chức năng độc lập: tầng thu thập dữ liệu cơ sở, tầng phân tích xử lý trung gian và tầng báo cáo điều hành vĩ mô. \n\n"
                "Thời gian đáp ứng của từng tầng được kiểm soát nghiêm ngặt với độ trễ tối đa dưới 200 mili-giây, bảo đảm an toàn dữ liệu và tuân thủ các quy định bảo mật chuyên ngành.\n\n"
                "## 3. Kết quả Thực nghiệm và Kế hoạch Mở rộng\n\n"
                "Trong giai đoạn thử nghiệm diện hẹp tại 5 đơn vị cơ sở, tổng ngân sách tiết kiệm đạt 15,8 tỷ đồng và mức độ hài lòng của người dùng đạt 94,5%. \n\n"
                "Kế hoạch triển khai mở rộng trên phạm vi toàn quốc dự kiến hoàn thành vào quý IV năm 2026 với sự phối hợp chặt chẽ của các bộ ngành chuyên trách."
            ),
            "metadata": {
                "field": "Chính phủ Điện tử",
                "domain": "Digital Gov",
                "language": "vi",
                "target_levels": 3,
            },
        },
        {
            "document_id": "VN_DOC_018",
            "title": "Phòng chống Rửa tiền và Quản lý Tài sản Ảo trong Hệ thống Tín dụng",
            "version": 1,
            "raw_text": (
                "## 1. Cơ sở Lý luận và Bối cảnh Thực tiễn\n\n"
                "Nội dung văn kiện nghiên cứu thuộc lĩnh vực Ngân hàng & Giám sát khẳng định tầm quan trọng của việc chuẩn hóa các quy trình kỹ thuật và chính sách quản lý hiện đại tại Việt Nam trong giai đoạn 2024-2030. \n\n"
                "Theo các báo cáo thẩm định ban đầu, việc áp dụng các tiêu chuẩn quốc tế ISO và khung hướng dẫn kỹ thuật số giúp nâng cao 35% hiệu suất vận hành thực tế so với phương pháp truyền thống.\n\n"
                "## 2. Kiến trúc và Phương pháp Triển khai\n\n"
                "Hệ thống vận hành được phân cấp thành 3 tầng chức năng độc lập: tầng thu thập dữ liệu cơ sở, tầng phân tích xử lý trung gian và tầng báo cáo điều hành vĩ mô. \n\n"
                "Thời gian đáp ứng của từng tầng được kiểm soát nghiêm ngặt với độ trễ tối đa dưới 200 mili-giây, bảo đảm an toàn dữ liệu và tuân thủ các quy định bảo mật chuyên ngành.\n\n"
                "## 3. Kết quả Thực nghiệm và Kế hoạch Mở rộng\n\n"
                "Trong giai đoạn thử nghiệm diện hẹp tại 5 đơn vị cơ sở, tổng ngân sách tiết kiệm đạt 15,8 tỷ đồng và mức độ hài lòng của người dùng đạt 94,5%. \n\n"
                "Kế hoạch triển khai mở rộng trên phạm vi toàn quốc dự kiến hoàn thành vào quý IV năm 2026 với sự phối hợp chặt chẽ của các bộ ngành chuyên trách."
            ),
            "metadata": {
                "field": "Ngân hàng & Giám sát",
                "domain": "AML & Compliance",
                "language": "vi",
                "target_levels": 3,
            },
        },
        {
            "document_id": "VN_DOC_019",
            "title": "Công nghệ Sinh học Ứng dụng trong Chọn tạo Giống Tôm Nước lợ",
            "version": 1,
            "raw_text": (
                "## 1. Cơ sở Lý luận và Bối cảnh Thực tiễn\n\n"
                "Nội dung văn kiện nghiên cứu thuộc lĩnh vực Thủy sản & Công nghệ Sinh học khẳng định tầm quan trọng của việc chuẩn hóa các quy trình kỹ thuật và chính sách quản lý hiện đại tại Việt Nam trong giai đoạn 2024-2030. \n\n"
                "Theo các báo cáo thẩm định ban đầu, việc áp dụng các tiêu chuẩn quốc tế ISO và khung hướng dẫn kỹ thuật số giúp nâng cao 35% hiệu suất vận hành thực tế so với phương pháp truyền thống.\n\n"
                "## 2. Kiến trúc và Phương pháp Triển khai\n\n"
                "Hệ thống vận hành được phân cấp thành 3 tầng chức năng độc lập: tầng thu thập dữ liệu cơ sở, tầng phân tích xử lý trung gian và tầng báo cáo điều hành vĩ mô. \n\n"
                "Thời gian đáp ứng của từng tầng được kiểm soát nghiêm ngặt với độ trễ tối đa dưới 200 mili-giây, bảo đảm an toàn dữ liệu và tuân thủ các quy định bảo mật chuyên ngành.\n\n"
                "## 3. Kết quả Thực nghiệm và Kế hoạch Mở rộng\n\n"
                "Trong giai đoạn thử nghiệm diện hẹp tại 5 đơn vị cơ sở, tổng ngân sách tiết kiệm đạt 15,8 tỷ đồng và mức độ hài lòng của người dùng đạt 94,5%. \n\n"
                "Kế hoạch triển khai mở rộng trên phạm vi toàn quốc dự kiến hoàn thành vào quý IV năm 2026 với sự phối hợp chặt chẽ của các bộ ngành chuyên trách."
            ),
            "metadata": {
                "field": "Thủy sản & Công nghệ Sinh học",
                "domain": "Aquaculture",
                "language": "vi",
                "target_levels": 3,
            },
        },
        {
            "document_id": "VN_DOC_020",
            "title": "Quy hoạch Đô thị Giảm Phát thải và Mục tiêu Phát thải Ròng bằng Không (Net-Zero)",
            "version": 1,
            "raw_text": (
                "## 1. Cơ sở Lý luận và Bối cảnh Thực tiễn\n\n"
                "Nội dung văn kiện nghiên cứu thuộc lĩnh vực Đô thị & Biến đổi Khí hậu khẳng định tầm quan trọng của việc chuẩn hóa các quy trình kỹ thuật và chính sách quản lý hiện đại tại Việt Nam trong giai đoạn 2024-2030. \n\n"
                "Theo các báo cáo thẩm định ban đầu, việc áp dụng các tiêu chuẩn quốc tế ISO và khung hướng dẫn kỹ thuật số giúp nâng cao 35% hiệu suất vận hành thực tế so với phương pháp truyền thống.\n\n"
                "## 2. Kiến trúc và Phương pháp Triển khai\n\n"
                "Hệ thống vận hành được phân cấp thành 3 tầng chức năng độc lập: tầng thu thập dữ liệu cơ sở, tầng phân tích xử lý trung gian và tầng báo cáo điều hành vĩ mô. \n\n"
                "Thời gian đáp ứng của từng tầng được kiểm soát nghiêm ngặt với độ trễ tối đa dưới 200 mili-giây, bảo đảm an toàn dữ liệu và tuân thủ các quy định bảo mật chuyên ngành.\n\n"
                "## 3. Kết quả Thực nghiệm và Kế hoạch Mở rộng\n\n"
                "Trong giai đoạn thử nghiệm diện hẹp tại 5 đơn vị cơ sở, tổng ngân sách tiết kiệm đạt 15,8 tỷ đồng và mức độ hài lòng của người dùng đạt 94,5%. \n\n"
                "Kế hoạch triển khai mở rộng trên phạm vi toàn quốc dự kiến hoàn thành vào quý IV năm 2026 với sự phối hợp chặt chẽ của các bộ ngành chuyên trách."
            ),
            "metadata": {
                "field": "Đô thị & Biến đổi Khí hậu",
                "domain": "Net-Zero Urban",
                "language": "vi",
                "target_levels": 3,
            },
        },
    ]


def get_vietnamese_final_questions() -> List[Dict[str, Any]]:
    """Returns 350 questions: 300 answerable, 50 without answer."""
    questions = []
    # -------------------------------------------------------------------------
    # 1. 300 ANSWERABLE QUESTIONS (15 per document)
    # -------------------------------------------------------------------------
    questions.append({
        "question_id": "VN_FINAL_ANS_001",
        "category": "answerable",
        "document_id": "VN_DOC_001",
        "expected_decision": "answer",
        "question": "Lĩnh vực nghiên cứu chính của tài liệu là gì?",
        "ground_truth_answer": "Trí tuệ Nhân tạo",
        "target_passages": ["VN_DOC_001::P000", "VN_DOC_001::P001", "VN_DOC_001::P002"],
        "expected_keywords": ["Trí tuệ Nhân tạo"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_002",
        "category": "answerable",
        "document_id": "VN_DOC_001",
        "expected_decision": "answer",
        "question": "Giai đoạn áp dụng chính sách quản lý được đề cập kéo dài từ năm nào đến năm nào?",
        "ground_truth_answer": "giai đoạn 2024-2030",
        "target_passages": ["VN_DOC_001::P000", "VN_DOC_001::P001", "VN_DOC_001::P002"],
        "expected_keywords": ["2024", "2030"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_003",
        "category": "answerable",
        "document_id": "VN_DOC_001",
        "expected_decision": "answer",
        "question": "Việc áp dụng tiêu chuẩn quốc tế giúp nâng cao hiệu suất vận hành bao nhiêu phần trăm?",
        "ground_truth_answer": "35% hiệu suất vận hành",
        "target_passages": ["VN_DOC_001::P000", "VN_DOC_001::P001", "VN_DOC_001::P002"],
        "expected_keywords": ["35%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_004",
        "category": "answerable",
        "document_id": "VN_DOC_001",
        "expected_decision": "answer",
        "question": "Hệ thống vận hành được phân cấp thành bao nhiêu tầng chức năng độc lập?",
        "ground_truth_answer": "3 tầng chức năng độc lập",
        "target_passages": ["VN_DOC_001::P000", "VN_DOC_001::P001", "VN_DOC_001::P002"],
        "expected_keywords": ["3 tầng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_005",
        "category": "answerable",
        "document_id": "VN_DOC_001",
        "expected_decision": "answer",
        "question": "Tầng đầu tiên trong kiến trúc phân cấp của hệ thống đảm nhiệm vai trò gì?",
        "ground_truth_answer": "thu thập dữ liệu cơ sở",
        "target_passages": ["VN_DOC_001::P000", "VN_DOC_001::P001", "VN_DOC_001::P002"],
        "expected_keywords": ["thu thập dữ liệu"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_006",
        "category": "answerable",
        "document_id": "VN_DOC_001",
        "expected_decision": "answer",
        "question": "Tầng chức năng trung gian của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "phân tích xử lý trung gian",
        "target_passages": ["VN_DOC_001::P000", "VN_DOC_001::P001", "VN_DOC_001::P002"],
        "expected_keywords": ["phân tích", "xử lý"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_007",
        "category": "answerable",
        "document_id": "VN_DOC_001",
        "expected_decision": "answer",
        "question": "Tầng cao nhất của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "báo cáo điều hành vĩ mô",
        "target_passages": ["VN_DOC_001::P000", "VN_DOC_001::P001", "VN_DOC_001::P002"],
        "expected_keywords": ["điều hành vĩ mô", "báo cáo"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_008",
        "category": "answerable",
        "document_id": "VN_DOC_001",
        "expected_decision": "answer",
        "question": "Thời gian đáp ứng tối đa của từng tầng được quy định là bao nhiêu?",
        "ground_truth_answer": "dưới 200 mili-giây",
        "target_passages": ["VN_DOC_001::P000", "VN_DOC_001::P001", "VN_DOC_001::P002"],
        "expected_keywords": ["200", "mili-giây"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_009",
        "category": "answerable",
        "document_id": "VN_DOC_001",
        "expected_decision": "answer",
        "question": "Giai đoạn thử nghiệm diện hẹp đã được tiến hành tại bao nhiêu đơn vị cơ sở?",
        "ground_truth_answer": "5 đơn vị cơ sở",
        "target_passages": ["VN_DOC_001::P000", "VN_DOC_001::P001", "VN_DOC_001::P002"],
        "expected_keywords": ["5 đơn vị"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_010",
        "category": "answerable",
        "document_id": "VN_DOC_001",
        "expected_decision": "answer",
        "question": "Tổng ngân sách tiết kiệm được trong giai đoạn thử nghiệm diện hẹp là bao nhiêu?",
        "ground_truth_answer": "15,8 tỷ đồng",
        "target_passages": ["VN_DOC_001::P000", "VN_DOC_001::P001", "VN_DOC_001::P002"],
        "expected_keywords": ["15,8 tỷ", "đồng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_011",
        "category": "answerable",
        "document_id": "VN_DOC_001",
        "expected_decision": "answer",
        "question": "Mức độ hài lòng của người dùng đạt được trong giai đoạn thử nghiệm là bao nhiêu phần trăm?",
        "ground_truth_answer": "94,5%",
        "target_passages": ["VN_DOC_001::P000", "VN_DOC_001::P001", "VN_DOC_001::P002"],
        "expected_keywords": ["94,5%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_012",
        "category": "answerable",
        "document_id": "VN_DOC_001",
        "expected_decision": "answer",
        "question": "Kế hoạch triển khai mở rộng toàn quốc dự kiến hoàn thành vào thời gian nào?",
        "ground_truth_answer": "quý IV năm 2026",
        "target_passages": ["VN_DOC_001::P000", "VN_DOC_001::P001", "VN_DOC_001::P002"],
        "expected_keywords": ["quý IV", "2026"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_013",
        "category": "answerable",
        "document_id": "VN_DOC_001",
        "expected_decision": "answer",
        "question": "Phương pháp nào được so sánh với tiêu chuẩn quốc tế ISO trong việc nâng cao hiệu suất?",
        "ground_truth_answer": "phương pháp truyền thống",
        "target_passages": ["VN_DOC_001::P000", "VN_DOC_001::P001", "VN_DOC_001::P002"],
        "expected_keywords": ["phương pháp truyền thống"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_014",
        "category": "answerable",
        "document_id": "VN_DOC_001",
        "expected_decision": "answer",
        "question": "Yếu tố an toàn nào được kiểm soát nghiêm ngặt cùng với độ trễ dưới 200 mili-giây?",
        "ground_truth_answer": "an toàn dữ liệu và bảo mật chuyên ngành",
        "target_passages": ["VN_DOC_001::P000", "VN_DOC_001::P001", "VN_DOC_001::P002"],
        "expected_keywords": ["an toàn dữ liệu", "bảo mật"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_015",
        "category": "answerable",
        "document_id": "VN_DOC_001",
        "expected_decision": "answer",
        "question": "Sự phối hợp của các cơ quan nào là cần thiết cho kế hoạch mở rộng toàn quốc?",
        "ground_truth_answer": "sự phối hợp của các bộ ngành chuyên trách",
        "target_passages": ["VN_DOC_001::P000", "VN_DOC_001::P001", "VN_DOC_001::P002"],
        "expected_keywords": ["bộ ngành chuyên trách"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_016",
        "category": "answerable",
        "document_id": "VN_DOC_002",
        "expected_decision": "answer",
        "question": "Lĩnh vực nghiên cứu chính của tài liệu là gì?",
        "ground_truth_answer": "Pháp luật & An ninh thông tin",
        "target_passages": ["VN_DOC_002::P000", "VN_DOC_002::P001", "VN_DOC_002::P002"],
        "expected_keywords": ["Pháp luật & An ninh thông tin"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_017",
        "category": "answerable",
        "document_id": "VN_DOC_002",
        "expected_decision": "answer",
        "question": "Giai đoạn áp dụng chính sách quản lý được đề cập kéo dài từ năm nào đến năm nào?",
        "ground_truth_answer": "giai đoạn 2024-2030",
        "target_passages": ["VN_DOC_002::P000", "VN_DOC_002::P001", "VN_DOC_002::P002"],
        "expected_keywords": ["2024", "2030"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_018",
        "category": "answerable",
        "document_id": "VN_DOC_002",
        "expected_decision": "answer",
        "question": "Việc áp dụng tiêu chuẩn quốc tế giúp nâng cao hiệu suất vận hành bao nhiêu phần trăm?",
        "ground_truth_answer": "35% hiệu suất vận hành",
        "target_passages": ["VN_DOC_002::P000", "VN_DOC_002::P001", "VN_DOC_002::P002"],
        "expected_keywords": ["35%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_019",
        "category": "answerable",
        "document_id": "VN_DOC_002",
        "expected_decision": "answer",
        "question": "Hệ thống vận hành được phân cấp thành bao nhiêu tầng chức năng độc lập?",
        "ground_truth_answer": "3 tầng chức năng độc lập",
        "target_passages": ["VN_DOC_002::P000", "VN_DOC_002::P001", "VN_DOC_002::P002"],
        "expected_keywords": ["3 tầng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_020",
        "category": "answerable",
        "document_id": "VN_DOC_002",
        "expected_decision": "answer",
        "question": "Tầng đầu tiên trong kiến trúc phân cấp của hệ thống đảm nhiệm vai trò gì?",
        "ground_truth_answer": "thu thập dữ liệu cơ sở",
        "target_passages": ["VN_DOC_002::P000", "VN_DOC_002::P001", "VN_DOC_002::P002"],
        "expected_keywords": ["thu thập dữ liệu"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_021",
        "category": "answerable",
        "document_id": "VN_DOC_002",
        "expected_decision": "answer",
        "question": "Tầng chức năng trung gian của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "phân tích xử lý trung gian",
        "target_passages": ["VN_DOC_002::P000", "VN_DOC_002::P001", "VN_DOC_002::P002"],
        "expected_keywords": ["phân tích", "xử lý"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_022",
        "category": "answerable",
        "document_id": "VN_DOC_002",
        "expected_decision": "answer",
        "question": "Tầng cao nhất của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "báo cáo điều hành vĩ mô",
        "target_passages": ["VN_DOC_002::P000", "VN_DOC_002::P001", "VN_DOC_002::P002"],
        "expected_keywords": ["điều hành vĩ mô", "báo cáo"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_023",
        "category": "answerable",
        "document_id": "VN_DOC_002",
        "expected_decision": "answer",
        "question": "Thời gian đáp ứng tối đa của từng tầng được quy định là bao nhiêu?",
        "ground_truth_answer": "dưới 200 mili-giây",
        "target_passages": ["VN_DOC_002::P000", "VN_DOC_002::P001", "VN_DOC_002::P002"],
        "expected_keywords": ["200", "mili-giây"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_024",
        "category": "answerable",
        "document_id": "VN_DOC_002",
        "expected_decision": "answer",
        "question": "Giai đoạn thử nghiệm diện hẹp đã được tiến hành tại bao nhiêu đơn vị cơ sở?",
        "ground_truth_answer": "5 đơn vị cơ sở",
        "target_passages": ["VN_DOC_002::P000", "VN_DOC_002::P001", "VN_DOC_002::P002"],
        "expected_keywords": ["5 đơn vị"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_025",
        "category": "answerable",
        "document_id": "VN_DOC_002",
        "expected_decision": "answer",
        "question": "Tổng ngân sách tiết kiệm được trong giai đoạn thử nghiệm diện hẹp là bao nhiêu?",
        "ground_truth_answer": "15,8 tỷ đồng",
        "target_passages": ["VN_DOC_002::P000", "VN_DOC_002::P001", "VN_DOC_002::P002"],
        "expected_keywords": ["15,8 tỷ", "đồng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_026",
        "category": "answerable",
        "document_id": "VN_DOC_002",
        "expected_decision": "answer",
        "question": "Mức độ hài lòng của người dùng đạt được trong giai đoạn thử nghiệm là bao nhiêu phần trăm?",
        "ground_truth_answer": "94,5%",
        "target_passages": ["VN_DOC_002::P000", "VN_DOC_002::P001", "VN_DOC_002::P002"],
        "expected_keywords": ["94,5%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_027",
        "category": "answerable",
        "document_id": "VN_DOC_002",
        "expected_decision": "answer",
        "question": "Kế hoạch triển khai mở rộng toàn quốc dự kiến hoàn thành vào thời gian nào?",
        "ground_truth_answer": "quý IV năm 2026",
        "target_passages": ["VN_DOC_002::P000", "VN_DOC_002::P001", "VN_DOC_002::P002"],
        "expected_keywords": ["quý IV", "2026"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_028",
        "category": "answerable",
        "document_id": "VN_DOC_002",
        "expected_decision": "answer",
        "question": "Phương pháp nào được so sánh với tiêu chuẩn quốc tế ISO trong việc nâng cao hiệu suất?",
        "ground_truth_answer": "phương pháp truyền thống",
        "target_passages": ["VN_DOC_002::P000", "VN_DOC_002::P001", "VN_DOC_002::P002"],
        "expected_keywords": ["phương pháp truyền thống"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_029",
        "category": "answerable",
        "document_id": "VN_DOC_002",
        "expected_decision": "answer",
        "question": "Yếu tố an toàn nào được kiểm soát nghiêm ngặt cùng với độ trễ dưới 200 mili-giây?",
        "ground_truth_answer": "an toàn dữ liệu và bảo mật chuyên ngành",
        "target_passages": ["VN_DOC_002::P000", "VN_DOC_002::P001", "VN_DOC_002::P002"],
        "expected_keywords": ["an toàn dữ liệu", "bảo mật"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_030",
        "category": "answerable",
        "document_id": "VN_DOC_002",
        "expected_decision": "answer",
        "question": "Sự phối hợp của các cơ quan nào là cần thiết cho kế hoạch mở rộng toàn quốc?",
        "ground_truth_answer": "sự phối hợp của các bộ ngành chuyên trách",
        "target_passages": ["VN_DOC_002::P000", "VN_DOC_002::P001", "VN_DOC_002::P002"],
        "expected_keywords": ["bộ ngành chuyên trách"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_031",
        "category": "answerable",
        "document_id": "VN_DOC_003",
        "expected_decision": "answer",
        "question": "Lĩnh vực nghiên cứu chính của tài liệu là gì?",
        "ground_truth_answer": "Lịch sử & Di sản Văn hóa",
        "target_passages": ["VN_DOC_003::P000", "VN_DOC_003::P001", "VN_DOC_003::P002"],
        "expected_keywords": ["Lịch sử & Di sản Văn hóa"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_032",
        "category": "answerable",
        "document_id": "VN_DOC_003",
        "expected_decision": "answer",
        "question": "Giai đoạn áp dụng chính sách quản lý được đề cập kéo dài từ năm nào đến năm nào?",
        "ground_truth_answer": "giai đoạn 2024-2030",
        "target_passages": ["VN_DOC_003::P000", "VN_DOC_003::P001", "VN_DOC_003::P002"],
        "expected_keywords": ["2024", "2030"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_033",
        "category": "answerable",
        "document_id": "VN_DOC_003",
        "expected_decision": "answer",
        "question": "Việc áp dụng tiêu chuẩn quốc tế giúp nâng cao hiệu suất vận hành bao nhiêu phần trăm?",
        "ground_truth_answer": "35% hiệu suất vận hành",
        "target_passages": ["VN_DOC_003::P000", "VN_DOC_003::P001", "VN_DOC_003::P002"],
        "expected_keywords": ["35%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_034",
        "category": "answerable",
        "document_id": "VN_DOC_003",
        "expected_decision": "answer",
        "question": "Hệ thống vận hành được phân cấp thành bao nhiêu tầng chức năng độc lập?",
        "ground_truth_answer": "3 tầng chức năng độc lập",
        "target_passages": ["VN_DOC_003::P000", "VN_DOC_003::P001", "VN_DOC_003::P002"],
        "expected_keywords": ["3 tầng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_035",
        "category": "answerable",
        "document_id": "VN_DOC_003",
        "expected_decision": "answer",
        "question": "Tầng đầu tiên trong kiến trúc phân cấp của hệ thống đảm nhiệm vai trò gì?",
        "ground_truth_answer": "thu thập dữ liệu cơ sở",
        "target_passages": ["VN_DOC_003::P000", "VN_DOC_003::P001", "VN_DOC_003::P002"],
        "expected_keywords": ["thu thập dữ liệu"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_036",
        "category": "answerable",
        "document_id": "VN_DOC_003",
        "expected_decision": "answer",
        "question": "Tầng chức năng trung gian của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "phân tích xử lý trung gian",
        "target_passages": ["VN_DOC_003::P000", "VN_DOC_003::P001", "VN_DOC_003::P002"],
        "expected_keywords": ["phân tích", "xử lý"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_037",
        "category": "answerable",
        "document_id": "VN_DOC_003",
        "expected_decision": "answer",
        "question": "Tầng cao nhất của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "báo cáo điều hành vĩ mô",
        "target_passages": ["VN_DOC_003::P000", "VN_DOC_003::P001", "VN_DOC_003::P002"],
        "expected_keywords": ["điều hành vĩ mô", "báo cáo"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_038",
        "category": "answerable",
        "document_id": "VN_DOC_003",
        "expected_decision": "answer",
        "question": "Thời gian đáp ứng tối đa của từng tầng được quy định là bao nhiêu?",
        "ground_truth_answer": "dưới 200 mili-giây",
        "target_passages": ["VN_DOC_003::P000", "VN_DOC_003::P001", "VN_DOC_003::P002"],
        "expected_keywords": ["200", "mili-giây"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_039",
        "category": "answerable",
        "document_id": "VN_DOC_003",
        "expected_decision": "answer",
        "question": "Giai đoạn thử nghiệm diện hẹp đã được tiến hành tại bao nhiêu đơn vị cơ sở?",
        "ground_truth_answer": "5 đơn vị cơ sở",
        "target_passages": ["VN_DOC_003::P000", "VN_DOC_003::P001", "VN_DOC_003::P002"],
        "expected_keywords": ["5 đơn vị"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_040",
        "category": "answerable",
        "document_id": "VN_DOC_003",
        "expected_decision": "answer",
        "question": "Tổng ngân sách tiết kiệm được trong giai đoạn thử nghiệm diện hẹp là bao nhiêu?",
        "ground_truth_answer": "15,8 tỷ đồng",
        "target_passages": ["VN_DOC_003::P000", "VN_DOC_003::P001", "VN_DOC_003::P002"],
        "expected_keywords": ["15,8 tỷ", "đồng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_041",
        "category": "answerable",
        "document_id": "VN_DOC_003",
        "expected_decision": "answer",
        "question": "Mức độ hài lòng của người dùng đạt được trong giai đoạn thử nghiệm là bao nhiêu phần trăm?",
        "ground_truth_answer": "94,5%",
        "target_passages": ["VN_DOC_003::P000", "VN_DOC_003::P001", "VN_DOC_003::P002"],
        "expected_keywords": ["94,5%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_042",
        "category": "answerable",
        "document_id": "VN_DOC_003",
        "expected_decision": "answer",
        "question": "Kế hoạch triển khai mở rộng toàn quốc dự kiến hoàn thành vào thời gian nào?",
        "ground_truth_answer": "quý IV năm 2026",
        "target_passages": ["VN_DOC_003::P000", "VN_DOC_003::P001", "VN_DOC_003::P002"],
        "expected_keywords": ["quý IV", "2026"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_043",
        "category": "answerable",
        "document_id": "VN_DOC_003",
        "expected_decision": "answer",
        "question": "Phương pháp nào được so sánh với tiêu chuẩn quốc tế ISO trong việc nâng cao hiệu suất?",
        "ground_truth_answer": "phương pháp truyền thống",
        "target_passages": ["VN_DOC_003::P000", "VN_DOC_003::P001", "VN_DOC_003::P002"],
        "expected_keywords": ["phương pháp truyền thống"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_044",
        "category": "answerable",
        "document_id": "VN_DOC_003",
        "expected_decision": "answer",
        "question": "Yếu tố an toàn nào được kiểm soát nghiêm ngặt cùng với độ trễ dưới 200 mili-giây?",
        "ground_truth_answer": "an toàn dữ liệu và bảo mật chuyên ngành",
        "target_passages": ["VN_DOC_003::P000", "VN_DOC_003::P001", "VN_DOC_003::P002"],
        "expected_keywords": ["an toàn dữ liệu", "bảo mật"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_045",
        "category": "answerable",
        "document_id": "VN_DOC_003",
        "expected_decision": "answer",
        "question": "Sự phối hợp của các cơ quan nào là cần thiết cho kế hoạch mở rộng toàn quốc?",
        "ground_truth_answer": "sự phối hợp của các bộ ngành chuyên trách",
        "target_passages": ["VN_DOC_003::P000", "VN_DOC_003::P001", "VN_DOC_003::P002"],
        "expected_keywords": ["bộ ngành chuyên trách"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_046",
        "category": "answerable",
        "document_id": "VN_DOC_004",
        "expected_decision": "answer",
        "question": "Lĩnh vực nghiên cứu chính của tài liệu là gì?",
        "ground_truth_answer": "Nông nghiệp & Môi trường",
        "target_passages": ["VN_DOC_004::P000", "VN_DOC_004::P001", "VN_DOC_004::P002"],
        "expected_keywords": ["Nông nghiệp & Môi trường"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_047",
        "category": "answerable",
        "document_id": "VN_DOC_004",
        "expected_decision": "answer",
        "question": "Giai đoạn áp dụng chính sách quản lý được đề cập kéo dài từ năm nào đến năm nào?",
        "ground_truth_answer": "giai đoạn 2024-2030",
        "target_passages": ["VN_DOC_004::P000", "VN_DOC_004::P001", "VN_DOC_004::P002"],
        "expected_keywords": ["2024", "2030"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_048",
        "category": "answerable",
        "document_id": "VN_DOC_004",
        "expected_decision": "answer",
        "question": "Việc áp dụng tiêu chuẩn quốc tế giúp nâng cao hiệu suất vận hành bao nhiêu phần trăm?",
        "ground_truth_answer": "35% hiệu suất vận hành",
        "target_passages": ["VN_DOC_004::P000", "VN_DOC_004::P001", "VN_DOC_004::P002"],
        "expected_keywords": ["35%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_049",
        "category": "answerable",
        "document_id": "VN_DOC_004",
        "expected_decision": "answer",
        "question": "Hệ thống vận hành được phân cấp thành bao nhiêu tầng chức năng độc lập?",
        "ground_truth_answer": "3 tầng chức năng độc lập",
        "target_passages": ["VN_DOC_004::P000", "VN_DOC_004::P001", "VN_DOC_004::P002"],
        "expected_keywords": ["3 tầng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_050",
        "category": "answerable",
        "document_id": "VN_DOC_004",
        "expected_decision": "answer",
        "question": "Tầng đầu tiên trong kiến trúc phân cấp của hệ thống đảm nhiệm vai trò gì?",
        "ground_truth_answer": "thu thập dữ liệu cơ sở",
        "target_passages": ["VN_DOC_004::P000", "VN_DOC_004::P001", "VN_DOC_004::P002"],
        "expected_keywords": ["thu thập dữ liệu"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_051",
        "category": "answerable",
        "document_id": "VN_DOC_004",
        "expected_decision": "answer",
        "question": "Tầng chức năng trung gian của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "phân tích xử lý trung gian",
        "target_passages": ["VN_DOC_004::P000", "VN_DOC_004::P001", "VN_DOC_004::P002"],
        "expected_keywords": ["phân tích", "xử lý"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_052",
        "category": "answerable",
        "document_id": "VN_DOC_004",
        "expected_decision": "answer",
        "question": "Tầng cao nhất của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "báo cáo điều hành vĩ mô",
        "target_passages": ["VN_DOC_004::P000", "VN_DOC_004::P001", "VN_DOC_004::P002"],
        "expected_keywords": ["điều hành vĩ mô", "báo cáo"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_053",
        "category": "answerable",
        "document_id": "VN_DOC_004",
        "expected_decision": "answer",
        "question": "Thời gian đáp ứng tối đa của từng tầng được quy định là bao nhiêu?",
        "ground_truth_answer": "dưới 200 mili-giây",
        "target_passages": ["VN_DOC_004::P000", "VN_DOC_004::P001", "VN_DOC_004::P002"],
        "expected_keywords": ["200", "mili-giây"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_054",
        "category": "answerable",
        "document_id": "VN_DOC_004",
        "expected_decision": "answer",
        "question": "Giai đoạn thử nghiệm diện hẹp đã được tiến hành tại bao nhiêu đơn vị cơ sở?",
        "ground_truth_answer": "5 đơn vị cơ sở",
        "target_passages": ["VN_DOC_004::P000", "VN_DOC_004::P001", "VN_DOC_004::P002"],
        "expected_keywords": ["5 đơn vị"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_055",
        "category": "answerable",
        "document_id": "VN_DOC_004",
        "expected_decision": "answer",
        "question": "Tổng ngân sách tiết kiệm được trong giai đoạn thử nghiệm diện hẹp là bao nhiêu?",
        "ground_truth_answer": "15,8 tỷ đồng",
        "target_passages": ["VN_DOC_004::P000", "VN_DOC_004::P001", "VN_DOC_004::P002"],
        "expected_keywords": ["15,8 tỷ", "đồng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_056",
        "category": "answerable",
        "document_id": "VN_DOC_004",
        "expected_decision": "answer",
        "question": "Mức độ hài lòng của người dùng đạt được trong giai đoạn thử nghiệm là bao nhiêu phần trăm?",
        "ground_truth_answer": "94,5%",
        "target_passages": ["VN_DOC_004::P000", "VN_DOC_004::P001", "VN_DOC_004::P002"],
        "expected_keywords": ["94,5%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_057",
        "category": "answerable",
        "document_id": "VN_DOC_004",
        "expected_decision": "answer",
        "question": "Kế hoạch triển khai mở rộng toàn quốc dự kiến hoàn thành vào thời gian nào?",
        "ground_truth_answer": "quý IV năm 2026",
        "target_passages": ["VN_DOC_004::P000", "VN_DOC_004::P001", "VN_DOC_004::P002"],
        "expected_keywords": ["quý IV", "2026"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_058",
        "category": "answerable",
        "document_id": "VN_DOC_004",
        "expected_decision": "answer",
        "question": "Phương pháp nào được so sánh với tiêu chuẩn quốc tế ISO trong việc nâng cao hiệu suất?",
        "ground_truth_answer": "phương pháp truyền thống",
        "target_passages": ["VN_DOC_004::P000", "VN_DOC_004::P001", "VN_DOC_004::P002"],
        "expected_keywords": ["phương pháp truyền thống"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_059",
        "category": "answerable",
        "document_id": "VN_DOC_004",
        "expected_decision": "answer",
        "question": "Yếu tố an toàn nào được kiểm soát nghiêm ngặt cùng với độ trễ dưới 200 mili-giây?",
        "ground_truth_answer": "an toàn dữ liệu và bảo mật chuyên ngành",
        "target_passages": ["VN_DOC_004::P000", "VN_DOC_004::P001", "VN_DOC_004::P002"],
        "expected_keywords": ["an toàn dữ liệu", "bảo mật"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_060",
        "category": "answerable",
        "document_id": "VN_DOC_004",
        "expected_decision": "answer",
        "question": "Sự phối hợp của các cơ quan nào là cần thiết cho kế hoạch mở rộng toàn quốc?",
        "ground_truth_answer": "sự phối hợp của các bộ ngành chuyên trách",
        "target_passages": ["VN_DOC_004::P000", "VN_DOC_004::P001", "VN_DOC_004::P002"],
        "expected_keywords": ["bộ ngành chuyên trách"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_061",
        "category": "answerable",
        "document_id": "VN_DOC_005",
        "expected_decision": "answer",
        "question": "Lĩnh vực nghiên cứu chính của tài liệu là gì?",
        "ground_truth_answer": "Năng lượng & Công nghệ Kỹ thuật",
        "target_passages": ["VN_DOC_005::P000", "VN_DOC_005::P001", "VN_DOC_005::P002"],
        "expected_keywords": ["Năng lượng & Công nghệ Kỹ thuật"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_062",
        "category": "answerable",
        "document_id": "VN_DOC_005",
        "expected_decision": "answer",
        "question": "Giai đoạn áp dụng chính sách quản lý được đề cập kéo dài từ năm nào đến năm nào?",
        "ground_truth_answer": "giai đoạn 2024-2030",
        "target_passages": ["VN_DOC_005::P000", "VN_DOC_005::P001", "VN_DOC_005::P002"],
        "expected_keywords": ["2024", "2030"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_063",
        "category": "answerable",
        "document_id": "VN_DOC_005",
        "expected_decision": "answer",
        "question": "Việc áp dụng tiêu chuẩn quốc tế giúp nâng cao hiệu suất vận hành bao nhiêu phần trăm?",
        "ground_truth_answer": "35% hiệu suất vận hành",
        "target_passages": ["VN_DOC_005::P000", "VN_DOC_005::P001", "VN_DOC_005::P002"],
        "expected_keywords": ["35%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_064",
        "category": "answerable",
        "document_id": "VN_DOC_005",
        "expected_decision": "answer",
        "question": "Hệ thống vận hành được phân cấp thành bao nhiêu tầng chức năng độc lập?",
        "ground_truth_answer": "3 tầng chức năng độc lập",
        "target_passages": ["VN_DOC_005::P000", "VN_DOC_005::P001", "VN_DOC_005::P002"],
        "expected_keywords": ["3 tầng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_065",
        "category": "answerable",
        "document_id": "VN_DOC_005",
        "expected_decision": "answer",
        "question": "Tầng đầu tiên trong kiến trúc phân cấp của hệ thống đảm nhiệm vai trò gì?",
        "ground_truth_answer": "thu thập dữ liệu cơ sở",
        "target_passages": ["VN_DOC_005::P000", "VN_DOC_005::P001", "VN_DOC_005::P002"],
        "expected_keywords": ["thu thập dữ liệu"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_066",
        "category": "answerable",
        "document_id": "VN_DOC_005",
        "expected_decision": "answer",
        "question": "Tầng chức năng trung gian của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "phân tích xử lý trung gian",
        "target_passages": ["VN_DOC_005::P000", "VN_DOC_005::P001", "VN_DOC_005::P002"],
        "expected_keywords": ["phân tích", "xử lý"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_067",
        "category": "answerable",
        "document_id": "VN_DOC_005",
        "expected_decision": "answer",
        "question": "Tầng cao nhất của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "báo cáo điều hành vĩ mô",
        "target_passages": ["VN_DOC_005::P000", "VN_DOC_005::P001", "VN_DOC_005::P002"],
        "expected_keywords": ["điều hành vĩ mô", "báo cáo"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_068",
        "category": "answerable",
        "document_id": "VN_DOC_005",
        "expected_decision": "answer",
        "question": "Thời gian đáp ứng tối đa của từng tầng được quy định là bao nhiêu?",
        "ground_truth_answer": "dưới 200 mili-giây",
        "target_passages": ["VN_DOC_005::P000", "VN_DOC_005::P001", "VN_DOC_005::P002"],
        "expected_keywords": ["200", "mili-giây"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_069",
        "category": "answerable",
        "document_id": "VN_DOC_005",
        "expected_decision": "answer",
        "question": "Giai đoạn thử nghiệm diện hẹp đã được tiến hành tại bao nhiêu đơn vị cơ sở?",
        "ground_truth_answer": "5 đơn vị cơ sở",
        "target_passages": ["VN_DOC_005::P000", "VN_DOC_005::P001", "VN_DOC_005::P002"],
        "expected_keywords": ["5 đơn vị"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_070",
        "category": "answerable",
        "document_id": "VN_DOC_005",
        "expected_decision": "answer",
        "question": "Tổng ngân sách tiết kiệm được trong giai đoạn thử nghiệm diện hẹp là bao nhiêu?",
        "ground_truth_answer": "15,8 tỷ đồng",
        "target_passages": ["VN_DOC_005::P000", "VN_DOC_005::P001", "VN_DOC_005::P002"],
        "expected_keywords": ["15,8 tỷ", "đồng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_071",
        "category": "answerable",
        "document_id": "VN_DOC_005",
        "expected_decision": "answer",
        "question": "Mức độ hài lòng của người dùng đạt được trong giai đoạn thử nghiệm là bao nhiêu phần trăm?",
        "ground_truth_answer": "94,5%",
        "target_passages": ["VN_DOC_005::P000", "VN_DOC_005::P001", "VN_DOC_005::P002"],
        "expected_keywords": ["94,5%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_072",
        "category": "answerable",
        "document_id": "VN_DOC_005",
        "expected_decision": "answer",
        "question": "Kế hoạch triển khai mở rộng toàn quốc dự kiến hoàn thành vào thời gian nào?",
        "ground_truth_answer": "quý IV năm 2026",
        "target_passages": ["VN_DOC_005::P000", "VN_DOC_005::P001", "VN_DOC_005::P002"],
        "expected_keywords": ["quý IV", "2026"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_073",
        "category": "answerable",
        "document_id": "VN_DOC_005",
        "expected_decision": "answer",
        "question": "Phương pháp nào được so sánh với tiêu chuẩn quốc tế ISO trong việc nâng cao hiệu suất?",
        "ground_truth_answer": "phương pháp truyền thống",
        "target_passages": ["VN_DOC_005::P000", "VN_DOC_005::P001", "VN_DOC_005::P002"],
        "expected_keywords": ["phương pháp truyền thống"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_074",
        "category": "answerable",
        "document_id": "VN_DOC_005",
        "expected_decision": "answer",
        "question": "Yếu tố an toàn nào được kiểm soát nghiêm ngặt cùng với độ trễ dưới 200 mili-giây?",
        "ground_truth_answer": "an toàn dữ liệu và bảo mật chuyên ngành",
        "target_passages": ["VN_DOC_005::P000", "VN_DOC_005::P001", "VN_DOC_005::P002"],
        "expected_keywords": ["an toàn dữ liệu", "bảo mật"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_075",
        "category": "answerable",
        "document_id": "VN_DOC_005",
        "expected_decision": "answer",
        "question": "Sự phối hợp của các cơ quan nào là cần thiết cho kế hoạch mở rộng toàn quốc?",
        "ground_truth_answer": "sự phối hợp của các bộ ngành chuyên trách",
        "target_passages": ["VN_DOC_005::P000", "VN_DOC_005::P001", "VN_DOC_005::P002"],
        "expected_keywords": ["bộ ngành chuyên trách"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_076",
        "category": "answerable",
        "document_id": "VN_DOC_006",
        "expected_decision": "answer",
        "question": "Lĩnh vực nghiên cứu chính của tài liệu là gì?",
        "ground_truth_answer": "Giáo dục & Đào tạo",
        "target_passages": ["VN_DOC_006::P000", "VN_DOC_006::P001", "VN_DOC_006::P002"],
        "expected_keywords": ["Giáo dục & Đào tạo"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_077",
        "category": "answerable",
        "document_id": "VN_DOC_006",
        "expected_decision": "answer",
        "question": "Giai đoạn áp dụng chính sách quản lý được đề cập kéo dài từ năm nào đến năm nào?",
        "ground_truth_answer": "giai đoạn 2024-2030",
        "target_passages": ["VN_DOC_006::P000", "VN_DOC_006::P001", "VN_DOC_006::P002"],
        "expected_keywords": ["2024", "2030"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_078",
        "category": "answerable",
        "document_id": "VN_DOC_006",
        "expected_decision": "answer",
        "question": "Việc áp dụng tiêu chuẩn quốc tế giúp nâng cao hiệu suất vận hành bao nhiêu phần trăm?",
        "ground_truth_answer": "35% hiệu suất vận hành",
        "target_passages": ["VN_DOC_006::P000", "VN_DOC_006::P001", "VN_DOC_006::P002"],
        "expected_keywords": ["35%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_079",
        "category": "answerable",
        "document_id": "VN_DOC_006",
        "expected_decision": "answer",
        "question": "Hệ thống vận hành được phân cấp thành bao nhiêu tầng chức năng độc lập?",
        "ground_truth_answer": "3 tầng chức năng độc lập",
        "target_passages": ["VN_DOC_006::P000", "VN_DOC_006::P001", "VN_DOC_006::P002"],
        "expected_keywords": ["3 tầng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_080",
        "category": "answerable",
        "document_id": "VN_DOC_006",
        "expected_decision": "answer",
        "question": "Tầng đầu tiên trong kiến trúc phân cấp của hệ thống đảm nhiệm vai trò gì?",
        "ground_truth_answer": "thu thập dữ liệu cơ sở",
        "target_passages": ["VN_DOC_006::P000", "VN_DOC_006::P001", "VN_DOC_006::P002"],
        "expected_keywords": ["thu thập dữ liệu"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_081",
        "category": "answerable",
        "document_id": "VN_DOC_006",
        "expected_decision": "answer",
        "question": "Tầng chức năng trung gian của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "phân tích xử lý trung gian",
        "target_passages": ["VN_DOC_006::P000", "VN_DOC_006::P001", "VN_DOC_006::P002"],
        "expected_keywords": ["phân tích", "xử lý"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_082",
        "category": "answerable",
        "document_id": "VN_DOC_006",
        "expected_decision": "answer",
        "question": "Tầng cao nhất của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "báo cáo điều hành vĩ mô",
        "target_passages": ["VN_DOC_006::P000", "VN_DOC_006::P001", "VN_DOC_006::P002"],
        "expected_keywords": ["điều hành vĩ mô", "báo cáo"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_083",
        "category": "answerable",
        "document_id": "VN_DOC_006",
        "expected_decision": "answer",
        "question": "Thời gian đáp ứng tối đa của từng tầng được quy định là bao nhiêu?",
        "ground_truth_answer": "dưới 200 mili-giây",
        "target_passages": ["VN_DOC_006::P000", "VN_DOC_006::P001", "VN_DOC_006::P002"],
        "expected_keywords": ["200", "mili-giây"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_084",
        "category": "answerable",
        "document_id": "VN_DOC_006",
        "expected_decision": "answer",
        "question": "Giai đoạn thử nghiệm diện hẹp đã được tiến hành tại bao nhiêu đơn vị cơ sở?",
        "ground_truth_answer": "5 đơn vị cơ sở",
        "target_passages": ["VN_DOC_006::P000", "VN_DOC_006::P001", "VN_DOC_006::P002"],
        "expected_keywords": ["5 đơn vị"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_085",
        "category": "answerable",
        "document_id": "VN_DOC_006",
        "expected_decision": "answer",
        "question": "Tổng ngân sách tiết kiệm được trong giai đoạn thử nghiệm diện hẹp là bao nhiêu?",
        "ground_truth_answer": "15,8 tỷ đồng",
        "target_passages": ["VN_DOC_006::P000", "VN_DOC_006::P001", "VN_DOC_006::P002"],
        "expected_keywords": ["15,8 tỷ", "đồng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_086",
        "category": "answerable",
        "document_id": "VN_DOC_006",
        "expected_decision": "answer",
        "question": "Mức độ hài lòng của người dùng đạt được trong giai đoạn thử nghiệm là bao nhiêu phần trăm?",
        "ground_truth_answer": "94,5%",
        "target_passages": ["VN_DOC_006::P000", "VN_DOC_006::P001", "VN_DOC_006::P002"],
        "expected_keywords": ["94,5%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_087",
        "category": "answerable",
        "document_id": "VN_DOC_006",
        "expected_decision": "answer",
        "question": "Kế hoạch triển khai mở rộng toàn quốc dự kiến hoàn thành vào thời gian nào?",
        "ground_truth_answer": "quý IV năm 2026",
        "target_passages": ["VN_DOC_006::P000", "VN_DOC_006::P001", "VN_DOC_006::P002"],
        "expected_keywords": ["quý IV", "2026"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_088",
        "category": "answerable",
        "document_id": "VN_DOC_006",
        "expected_decision": "answer",
        "question": "Phương pháp nào được so sánh với tiêu chuẩn quốc tế ISO trong việc nâng cao hiệu suất?",
        "ground_truth_answer": "phương pháp truyền thống",
        "target_passages": ["VN_DOC_006::P000", "VN_DOC_006::P001", "VN_DOC_006::P002"],
        "expected_keywords": ["phương pháp truyền thống"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_089",
        "category": "answerable",
        "document_id": "VN_DOC_006",
        "expected_decision": "answer",
        "question": "Yếu tố an toàn nào được kiểm soát nghiêm ngặt cùng với độ trễ dưới 200 mili-giây?",
        "ground_truth_answer": "an toàn dữ liệu và bảo mật chuyên ngành",
        "target_passages": ["VN_DOC_006::P000", "VN_DOC_006::P001", "VN_DOC_006::P002"],
        "expected_keywords": ["an toàn dữ liệu", "bảo mật"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_090",
        "category": "answerable",
        "document_id": "VN_DOC_006",
        "expected_decision": "answer",
        "question": "Sự phối hợp của các cơ quan nào là cần thiết cho kế hoạch mở rộng toàn quốc?",
        "ground_truth_answer": "sự phối hợp của các bộ ngành chuyên trách",
        "target_passages": ["VN_DOC_006::P000", "VN_DOC_006::P001", "VN_DOC_006::P002"],
        "expected_keywords": ["bộ ngành chuyên trách"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_091",
        "category": "answerable",
        "document_id": "VN_DOC_007",
        "expected_decision": "answer",
        "question": "Lĩnh vực nghiên cứu chính của tài liệu là gì?",
        "ground_truth_answer": "Công nghiệp Bán dẫn",
        "target_passages": ["VN_DOC_007::P000", "VN_DOC_007::P001", "VN_DOC_007::P002"],
        "expected_keywords": ["Công nghiệp Bán dẫn"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_092",
        "category": "answerable",
        "document_id": "VN_DOC_007",
        "expected_decision": "answer",
        "question": "Giai đoạn áp dụng chính sách quản lý được đề cập kéo dài từ năm nào đến năm nào?",
        "ground_truth_answer": "giai đoạn 2024-2030",
        "target_passages": ["VN_DOC_007::P000", "VN_DOC_007::P001", "VN_DOC_007::P002"],
        "expected_keywords": ["2024", "2030"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_093",
        "category": "answerable",
        "document_id": "VN_DOC_007",
        "expected_decision": "answer",
        "question": "Việc áp dụng tiêu chuẩn quốc tế giúp nâng cao hiệu suất vận hành bao nhiêu phần trăm?",
        "ground_truth_answer": "35% hiệu suất vận hành",
        "target_passages": ["VN_DOC_007::P000", "VN_DOC_007::P001", "VN_DOC_007::P002"],
        "expected_keywords": ["35%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_094",
        "category": "answerable",
        "document_id": "VN_DOC_007",
        "expected_decision": "answer",
        "question": "Hệ thống vận hành được phân cấp thành bao nhiêu tầng chức năng độc lập?",
        "ground_truth_answer": "3 tầng chức năng độc lập",
        "target_passages": ["VN_DOC_007::P000", "VN_DOC_007::P001", "VN_DOC_007::P002"],
        "expected_keywords": ["3 tầng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_095",
        "category": "answerable",
        "document_id": "VN_DOC_007",
        "expected_decision": "answer",
        "question": "Tầng đầu tiên trong kiến trúc phân cấp của hệ thống đảm nhiệm vai trò gì?",
        "ground_truth_answer": "thu thập dữ liệu cơ sở",
        "target_passages": ["VN_DOC_007::P000", "VN_DOC_007::P001", "VN_DOC_007::P002"],
        "expected_keywords": ["thu thập dữ liệu"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_096",
        "category": "answerable",
        "document_id": "VN_DOC_007",
        "expected_decision": "answer",
        "question": "Tầng chức năng trung gian của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "phân tích xử lý trung gian",
        "target_passages": ["VN_DOC_007::P000", "VN_DOC_007::P001", "VN_DOC_007::P002"],
        "expected_keywords": ["phân tích", "xử lý"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_097",
        "category": "answerable",
        "document_id": "VN_DOC_007",
        "expected_decision": "answer",
        "question": "Tầng cao nhất của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "báo cáo điều hành vĩ mô",
        "target_passages": ["VN_DOC_007::P000", "VN_DOC_007::P001", "VN_DOC_007::P002"],
        "expected_keywords": ["điều hành vĩ mô", "báo cáo"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_098",
        "category": "answerable",
        "document_id": "VN_DOC_007",
        "expected_decision": "answer",
        "question": "Thời gian đáp ứng tối đa của từng tầng được quy định là bao nhiêu?",
        "ground_truth_answer": "dưới 200 mili-giây",
        "target_passages": ["VN_DOC_007::P000", "VN_DOC_007::P001", "VN_DOC_007::P002"],
        "expected_keywords": ["200", "mili-giây"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_099",
        "category": "answerable",
        "document_id": "VN_DOC_007",
        "expected_decision": "answer",
        "question": "Giai đoạn thử nghiệm diện hẹp đã được tiến hành tại bao nhiêu đơn vị cơ sở?",
        "ground_truth_answer": "5 đơn vị cơ sở",
        "target_passages": ["VN_DOC_007::P000", "VN_DOC_007::P001", "VN_DOC_007::P002"],
        "expected_keywords": ["5 đơn vị"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_100",
        "category": "answerable",
        "document_id": "VN_DOC_007",
        "expected_decision": "answer",
        "question": "Tổng ngân sách tiết kiệm được trong giai đoạn thử nghiệm diện hẹp là bao nhiêu?",
        "ground_truth_answer": "15,8 tỷ đồng",
        "target_passages": ["VN_DOC_007::P000", "VN_DOC_007::P001", "VN_DOC_007::P002"],
        "expected_keywords": ["15,8 tỷ", "đồng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_101",
        "category": "answerable",
        "document_id": "VN_DOC_007",
        "expected_decision": "answer",
        "question": "Mức độ hài lòng của người dùng đạt được trong giai đoạn thử nghiệm là bao nhiêu phần trăm?",
        "ground_truth_answer": "94,5%",
        "target_passages": ["VN_DOC_007::P000", "VN_DOC_007::P001", "VN_DOC_007::P002"],
        "expected_keywords": ["94,5%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_102",
        "category": "answerable",
        "document_id": "VN_DOC_007",
        "expected_decision": "answer",
        "question": "Kế hoạch triển khai mở rộng toàn quốc dự kiến hoàn thành vào thời gian nào?",
        "ground_truth_answer": "quý IV năm 2026",
        "target_passages": ["VN_DOC_007::P000", "VN_DOC_007::P001", "VN_DOC_007::P002"],
        "expected_keywords": ["quý IV", "2026"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_103",
        "category": "answerable",
        "document_id": "VN_DOC_007",
        "expected_decision": "answer",
        "question": "Phương pháp nào được so sánh với tiêu chuẩn quốc tế ISO trong việc nâng cao hiệu suất?",
        "ground_truth_answer": "phương pháp truyền thống",
        "target_passages": ["VN_DOC_007::P000", "VN_DOC_007::P001", "VN_DOC_007::P002"],
        "expected_keywords": ["phương pháp truyền thống"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_104",
        "category": "answerable",
        "document_id": "VN_DOC_007",
        "expected_decision": "answer",
        "question": "Yếu tố an toàn nào được kiểm soát nghiêm ngặt cùng với độ trễ dưới 200 mili-giây?",
        "ground_truth_answer": "an toàn dữ liệu và bảo mật chuyên ngành",
        "target_passages": ["VN_DOC_007::P000", "VN_DOC_007::P001", "VN_DOC_007::P002"],
        "expected_keywords": ["an toàn dữ liệu", "bảo mật"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_105",
        "category": "answerable",
        "document_id": "VN_DOC_007",
        "expected_decision": "answer",
        "question": "Sự phối hợp của các cơ quan nào là cần thiết cho kế hoạch mở rộng toàn quốc?",
        "ground_truth_answer": "sự phối hợp của các bộ ngành chuyên trách",
        "target_passages": ["VN_DOC_007::P000", "VN_DOC_007::P001", "VN_DOC_007::P002"],
        "expected_keywords": ["bộ ngành chuyên trách"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_106",
        "category": "answerable",
        "document_id": "VN_DOC_008",
        "expected_decision": "answer",
        "question": "Lĩnh vực nghiên cứu chính của tài liệu là gì?",
        "ground_truth_answer": "Giao thông Vận tải",
        "target_passages": ["VN_DOC_008::P000", "VN_DOC_008::P001", "VN_DOC_008::P002"],
        "expected_keywords": ["Giao thông Vận tải"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_107",
        "category": "answerable",
        "document_id": "VN_DOC_008",
        "expected_decision": "answer",
        "question": "Giai đoạn áp dụng chính sách quản lý được đề cập kéo dài từ năm nào đến năm nào?",
        "ground_truth_answer": "giai đoạn 2024-2030",
        "target_passages": ["VN_DOC_008::P000", "VN_DOC_008::P001", "VN_DOC_008::P002"],
        "expected_keywords": ["2024", "2030"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_108",
        "category": "answerable",
        "document_id": "VN_DOC_008",
        "expected_decision": "answer",
        "question": "Việc áp dụng tiêu chuẩn quốc tế giúp nâng cao hiệu suất vận hành bao nhiêu phần trăm?",
        "ground_truth_answer": "35% hiệu suất vận hành",
        "target_passages": ["VN_DOC_008::P000", "VN_DOC_008::P001", "VN_DOC_008::P002"],
        "expected_keywords": ["35%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_109",
        "category": "answerable",
        "document_id": "VN_DOC_008",
        "expected_decision": "answer",
        "question": "Hệ thống vận hành được phân cấp thành bao nhiêu tầng chức năng độc lập?",
        "ground_truth_answer": "3 tầng chức năng độc lập",
        "target_passages": ["VN_DOC_008::P000", "VN_DOC_008::P001", "VN_DOC_008::P002"],
        "expected_keywords": ["3 tầng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_110",
        "category": "answerable",
        "document_id": "VN_DOC_008",
        "expected_decision": "answer",
        "question": "Tầng đầu tiên trong kiến trúc phân cấp của hệ thống đảm nhiệm vai trò gì?",
        "ground_truth_answer": "thu thập dữ liệu cơ sở",
        "target_passages": ["VN_DOC_008::P000", "VN_DOC_008::P001", "VN_DOC_008::P002"],
        "expected_keywords": ["thu thập dữ liệu"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_111",
        "category": "answerable",
        "document_id": "VN_DOC_008",
        "expected_decision": "answer",
        "question": "Tầng chức năng trung gian của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "phân tích xử lý trung gian",
        "target_passages": ["VN_DOC_008::P000", "VN_DOC_008::P001", "VN_DOC_008::P002"],
        "expected_keywords": ["phân tích", "xử lý"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_112",
        "category": "answerable",
        "document_id": "VN_DOC_008",
        "expected_decision": "answer",
        "question": "Tầng cao nhất của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "báo cáo điều hành vĩ mô",
        "target_passages": ["VN_DOC_008::P000", "VN_DOC_008::P001", "VN_DOC_008::P002"],
        "expected_keywords": ["điều hành vĩ mô", "báo cáo"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_113",
        "category": "answerable",
        "document_id": "VN_DOC_008",
        "expected_decision": "answer",
        "question": "Thời gian đáp ứng tối đa của từng tầng được quy định là bao nhiêu?",
        "ground_truth_answer": "dưới 200 mili-giây",
        "target_passages": ["VN_DOC_008::P000", "VN_DOC_008::P001", "VN_DOC_008::P002"],
        "expected_keywords": ["200", "mili-giây"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_114",
        "category": "answerable",
        "document_id": "VN_DOC_008",
        "expected_decision": "answer",
        "question": "Giai đoạn thử nghiệm diện hẹp đã được tiến hành tại bao nhiêu đơn vị cơ sở?",
        "ground_truth_answer": "5 đơn vị cơ sở",
        "target_passages": ["VN_DOC_008::P000", "VN_DOC_008::P001", "VN_DOC_008::P002"],
        "expected_keywords": ["5 đơn vị"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_115",
        "category": "answerable",
        "document_id": "VN_DOC_008",
        "expected_decision": "answer",
        "question": "Tổng ngân sách tiết kiệm được trong giai đoạn thử nghiệm diện hẹp là bao nhiêu?",
        "ground_truth_answer": "15,8 tỷ đồng",
        "target_passages": ["VN_DOC_008::P000", "VN_DOC_008::P001", "VN_DOC_008::P002"],
        "expected_keywords": ["15,8 tỷ", "đồng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_116",
        "category": "answerable",
        "document_id": "VN_DOC_008",
        "expected_decision": "answer",
        "question": "Mức độ hài lòng của người dùng đạt được trong giai đoạn thử nghiệm là bao nhiêu phần trăm?",
        "ground_truth_answer": "94,5%",
        "target_passages": ["VN_DOC_008::P000", "VN_DOC_008::P001", "VN_DOC_008::P002"],
        "expected_keywords": ["94,5%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_117",
        "category": "answerable",
        "document_id": "VN_DOC_008",
        "expected_decision": "answer",
        "question": "Kế hoạch triển khai mở rộng toàn quốc dự kiến hoàn thành vào thời gian nào?",
        "ground_truth_answer": "quý IV năm 2026",
        "target_passages": ["VN_DOC_008::P000", "VN_DOC_008::P001", "VN_DOC_008::P002"],
        "expected_keywords": ["quý IV", "2026"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_118",
        "category": "answerable",
        "document_id": "VN_DOC_008",
        "expected_decision": "answer",
        "question": "Phương pháp nào được so sánh với tiêu chuẩn quốc tế ISO trong việc nâng cao hiệu suất?",
        "ground_truth_answer": "phương pháp truyền thống",
        "target_passages": ["VN_DOC_008::P000", "VN_DOC_008::P001", "VN_DOC_008::P002"],
        "expected_keywords": ["phương pháp truyền thống"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_119",
        "category": "answerable",
        "document_id": "VN_DOC_008",
        "expected_decision": "answer",
        "question": "Yếu tố an toàn nào được kiểm soát nghiêm ngặt cùng với độ trễ dưới 200 mili-giây?",
        "ground_truth_answer": "an toàn dữ liệu và bảo mật chuyên ngành",
        "target_passages": ["VN_DOC_008::P000", "VN_DOC_008::P001", "VN_DOC_008::P002"],
        "expected_keywords": ["an toàn dữ liệu", "bảo mật"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_120",
        "category": "answerable",
        "document_id": "VN_DOC_008",
        "expected_decision": "answer",
        "question": "Sự phối hợp của các cơ quan nào là cần thiết cho kế hoạch mở rộng toàn quốc?",
        "ground_truth_answer": "sự phối hợp của các bộ ngành chuyên trách",
        "target_passages": ["VN_DOC_008::P000", "VN_DOC_008::P001", "VN_DOC_008::P002"],
        "expected_keywords": ["bộ ngành chuyên trách"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_121",
        "category": "answerable",
        "document_id": "VN_DOC_009",
        "expected_decision": "answer",
        "question": "Lĩnh vực nghiên cứu chính của tài liệu là gì?",
        "ground_truth_answer": "Y tế & Y tế Công cộng",
        "target_passages": ["VN_DOC_009::P000", "VN_DOC_009::P001", "VN_DOC_009::P002"],
        "expected_keywords": ["Y tế & Y tế Công cộng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_122",
        "category": "answerable",
        "document_id": "VN_DOC_009",
        "expected_decision": "answer",
        "question": "Giai đoạn áp dụng chính sách quản lý được đề cập kéo dài từ năm nào đến năm nào?",
        "ground_truth_answer": "giai đoạn 2024-2030",
        "target_passages": ["VN_DOC_009::P000", "VN_DOC_009::P001", "VN_DOC_009::P002"],
        "expected_keywords": ["2024", "2030"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_123",
        "category": "answerable",
        "document_id": "VN_DOC_009",
        "expected_decision": "answer",
        "question": "Việc áp dụng tiêu chuẩn quốc tế giúp nâng cao hiệu suất vận hành bao nhiêu phần trăm?",
        "ground_truth_answer": "35% hiệu suất vận hành",
        "target_passages": ["VN_DOC_009::P000", "VN_DOC_009::P001", "VN_DOC_009::P002"],
        "expected_keywords": ["35%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_124",
        "category": "answerable",
        "document_id": "VN_DOC_009",
        "expected_decision": "answer",
        "question": "Hệ thống vận hành được phân cấp thành bao nhiêu tầng chức năng độc lập?",
        "ground_truth_answer": "3 tầng chức năng độc lập",
        "target_passages": ["VN_DOC_009::P000", "VN_DOC_009::P001", "VN_DOC_009::P002"],
        "expected_keywords": ["3 tầng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_125",
        "category": "answerable",
        "document_id": "VN_DOC_009",
        "expected_decision": "answer",
        "question": "Tầng đầu tiên trong kiến trúc phân cấp của hệ thống đảm nhiệm vai trò gì?",
        "ground_truth_answer": "thu thập dữ liệu cơ sở",
        "target_passages": ["VN_DOC_009::P000", "VN_DOC_009::P001", "VN_DOC_009::P002"],
        "expected_keywords": ["thu thập dữ liệu"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_126",
        "category": "answerable",
        "document_id": "VN_DOC_009",
        "expected_decision": "answer",
        "question": "Tầng chức năng trung gian của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "phân tích xử lý trung gian",
        "target_passages": ["VN_DOC_009::P000", "VN_DOC_009::P001", "VN_DOC_009::P002"],
        "expected_keywords": ["phân tích", "xử lý"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_127",
        "category": "answerable",
        "document_id": "VN_DOC_009",
        "expected_decision": "answer",
        "question": "Tầng cao nhất của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "báo cáo điều hành vĩ mô",
        "target_passages": ["VN_DOC_009::P000", "VN_DOC_009::P001", "VN_DOC_009::P002"],
        "expected_keywords": ["điều hành vĩ mô", "báo cáo"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_128",
        "category": "answerable",
        "document_id": "VN_DOC_009",
        "expected_decision": "answer",
        "question": "Thời gian đáp ứng tối đa của từng tầng được quy định là bao nhiêu?",
        "ground_truth_answer": "dưới 200 mili-giây",
        "target_passages": ["VN_DOC_009::P000", "VN_DOC_009::P001", "VN_DOC_009::P002"],
        "expected_keywords": ["200", "mili-giây"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_129",
        "category": "answerable",
        "document_id": "VN_DOC_009",
        "expected_decision": "answer",
        "question": "Giai đoạn thử nghiệm diện hẹp đã được tiến hành tại bao nhiêu đơn vị cơ sở?",
        "ground_truth_answer": "5 đơn vị cơ sở",
        "target_passages": ["VN_DOC_009::P000", "VN_DOC_009::P001", "VN_DOC_009::P002"],
        "expected_keywords": ["5 đơn vị"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_130",
        "category": "answerable",
        "document_id": "VN_DOC_009",
        "expected_decision": "answer",
        "question": "Tổng ngân sách tiết kiệm được trong giai đoạn thử nghiệm diện hẹp là bao nhiêu?",
        "ground_truth_answer": "15,8 tỷ đồng",
        "target_passages": ["VN_DOC_009::P000", "VN_DOC_009::P001", "VN_DOC_009::P002"],
        "expected_keywords": ["15,8 tỷ", "đồng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_131",
        "category": "answerable",
        "document_id": "VN_DOC_009",
        "expected_decision": "answer",
        "question": "Mức độ hài lòng của người dùng đạt được trong giai đoạn thử nghiệm là bao nhiêu phần trăm?",
        "ground_truth_answer": "94,5%",
        "target_passages": ["VN_DOC_009::P000", "VN_DOC_009::P001", "VN_DOC_009::P002"],
        "expected_keywords": ["94,5%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_132",
        "category": "answerable",
        "document_id": "VN_DOC_009",
        "expected_decision": "answer",
        "question": "Kế hoạch triển khai mở rộng toàn quốc dự kiến hoàn thành vào thời gian nào?",
        "ground_truth_answer": "quý IV năm 2026",
        "target_passages": ["VN_DOC_009::P000", "VN_DOC_009::P001", "VN_DOC_009::P002"],
        "expected_keywords": ["quý IV", "2026"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_133",
        "category": "answerable",
        "document_id": "VN_DOC_009",
        "expected_decision": "answer",
        "question": "Phương pháp nào được so sánh với tiêu chuẩn quốc tế ISO trong việc nâng cao hiệu suất?",
        "ground_truth_answer": "phương pháp truyền thống",
        "target_passages": ["VN_DOC_009::P000", "VN_DOC_009::P001", "VN_DOC_009::P002"],
        "expected_keywords": ["phương pháp truyền thống"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_134",
        "category": "answerable",
        "document_id": "VN_DOC_009",
        "expected_decision": "answer",
        "question": "Yếu tố an toàn nào được kiểm soát nghiêm ngặt cùng với độ trễ dưới 200 mili-giây?",
        "ground_truth_answer": "an toàn dữ liệu và bảo mật chuyên ngành",
        "target_passages": ["VN_DOC_009::P000", "VN_DOC_009::P001", "VN_DOC_009::P002"],
        "expected_keywords": ["an toàn dữ liệu", "bảo mật"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_135",
        "category": "answerable",
        "document_id": "VN_DOC_009",
        "expected_decision": "answer",
        "question": "Sự phối hợp của các cơ quan nào là cần thiết cho kế hoạch mở rộng toàn quốc?",
        "ground_truth_answer": "sự phối hợp của các bộ ngành chuyên trách",
        "target_passages": ["VN_DOC_009::P000", "VN_DOC_009::P001", "VN_DOC_009::P002"],
        "expected_keywords": ["bộ ngành chuyên trách"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_136",
        "category": "answerable",
        "document_id": "VN_DOC_010",
        "expected_decision": "answer",
        "question": "Lĩnh vực nghiên cứu chính của tài liệu là gì?",
        "ground_truth_answer": "Tài chính & Ngân hàng",
        "target_passages": ["VN_DOC_010::P000", "VN_DOC_010::P001", "VN_DOC_010::P002"],
        "expected_keywords": ["Tài chính & Ngân hàng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_137",
        "category": "answerable",
        "document_id": "VN_DOC_010",
        "expected_decision": "answer",
        "question": "Giai đoạn áp dụng chính sách quản lý được đề cập kéo dài từ năm nào đến năm nào?",
        "ground_truth_answer": "giai đoạn 2024-2030",
        "target_passages": ["VN_DOC_010::P000", "VN_DOC_010::P001", "VN_DOC_010::P002"],
        "expected_keywords": ["2024", "2030"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_138",
        "category": "answerable",
        "document_id": "VN_DOC_010",
        "expected_decision": "answer",
        "question": "Việc áp dụng tiêu chuẩn quốc tế giúp nâng cao hiệu suất vận hành bao nhiêu phần trăm?",
        "ground_truth_answer": "35% hiệu suất vận hành",
        "target_passages": ["VN_DOC_010::P000", "VN_DOC_010::P001", "VN_DOC_010::P002"],
        "expected_keywords": ["35%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_139",
        "category": "answerable",
        "document_id": "VN_DOC_010",
        "expected_decision": "answer",
        "question": "Hệ thống vận hành được phân cấp thành bao nhiêu tầng chức năng độc lập?",
        "ground_truth_answer": "3 tầng chức năng độc lập",
        "target_passages": ["VN_DOC_010::P000", "VN_DOC_010::P001", "VN_DOC_010::P002"],
        "expected_keywords": ["3 tầng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_140",
        "category": "answerable",
        "document_id": "VN_DOC_010",
        "expected_decision": "answer",
        "question": "Tầng đầu tiên trong kiến trúc phân cấp của hệ thống đảm nhiệm vai trò gì?",
        "ground_truth_answer": "thu thập dữ liệu cơ sở",
        "target_passages": ["VN_DOC_010::P000", "VN_DOC_010::P001", "VN_DOC_010::P002"],
        "expected_keywords": ["thu thập dữ liệu"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_141",
        "category": "answerable",
        "document_id": "VN_DOC_010",
        "expected_decision": "answer",
        "question": "Tầng chức năng trung gian của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "phân tích xử lý trung gian",
        "target_passages": ["VN_DOC_010::P000", "VN_DOC_010::P001", "VN_DOC_010::P002"],
        "expected_keywords": ["phân tích", "xử lý"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_142",
        "category": "answerable",
        "document_id": "VN_DOC_010",
        "expected_decision": "answer",
        "question": "Tầng cao nhất của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "báo cáo điều hành vĩ mô",
        "target_passages": ["VN_DOC_010::P000", "VN_DOC_010::P001", "VN_DOC_010::P002"],
        "expected_keywords": ["điều hành vĩ mô", "báo cáo"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_143",
        "category": "answerable",
        "document_id": "VN_DOC_010",
        "expected_decision": "answer",
        "question": "Thời gian đáp ứng tối đa của từng tầng được quy định là bao nhiêu?",
        "ground_truth_answer": "dưới 200 mili-giây",
        "target_passages": ["VN_DOC_010::P000", "VN_DOC_010::P001", "VN_DOC_010::P002"],
        "expected_keywords": ["200", "mili-giây"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_144",
        "category": "answerable",
        "document_id": "VN_DOC_010",
        "expected_decision": "answer",
        "question": "Giai đoạn thử nghiệm diện hẹp đã được tiến hành tại bao nhiêu đơn vị cơ sở?",
        "ground_truth_answer": "5 đơn vị cơ sở",
        "target_passages": ["VN_DOC_010::P000", "VN_DOC_010::P001", "VN_DOC_010::P002"],
        "expected_keywords": ["5 đơn vị"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_145",
        "category": "answerable",
        "document_id": "VN_DOC_010",
        "expected_decision": "answer",
        "question": "Tổng ngân sách tiết kiệm được trong giai đoạn thử nghiệm diện hẹp là bao nhiêu?",
        "ground_truth_answer": "15,8 tỷ đồng",
        "target_passages": ["VN_DOC_010::P000", "VN_DOC_010::P001", "VN_DOC_010::P002"],
        "expected_keywords": ["15,8 tỷ", "đồng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_146",
        "category": "answerable",
        "document_id": "VN_DOC_010",
        "expected_decision": "answer",
        "question": "Mức độ hài lòng của người dùng đạt được trong giai đoạn thử nghiệm là bao nhiêu phần trăm?",
        "ground_truth_answer": "94,5%",
        "target_passages": ["VN_DOC_010::P000", "VN_DOC_010::P001", "VN_DOC_010::P002"],
        "expected_keywords": ["94,5%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_147",
        "category": "answerable",
        "document_id": "VN_DOC_010",
        "expected_decision": "answer",
        "question": "Kế hoạch triển khai mở rộng toàn quốc dự kiến hoàn thành vào thời gian nào?",
        "ground_truth_answer": "quý IV năm 2026",
        "target_passages": ["VN_DOC_010::P000", "VN_DOC_010::P001", "VN_DOC_010::P002"],
        "expected_keywords": ["quý IV", "2026"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_148",
        "category": "answerable",
        "document_id": "VN_DOC_010",
        "expected_decision": "answer",
        "question": "Phương pháp nào được so sánh với tiêu chuẩn quốc tế ISO trong việc nâng cao hiệu suất?",
        "ground_truth_answer": "phương pháp truyền thống",
        "target_passages": ["VN_DOC_010::P000", "VN_DOC_010::P001", "VN_DOC_010::P002"],
        "expected_keywords": ["phương pháp truyền thống"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_149",
        "category": "answerable",
        "document_id": "VN_DOC_010",
        "expected_decision": "answer",
        "question": "Yếu tố an toàn nào được kiểm soát nghiêm ngặt cùng với độ trễ dưới 200 mili-giây?",
        "ground_truth_answer": "an toàn dữ liệu và bảo mật chuyên ngành",
        "target_passages": ["VN_DOC_010::P000", "VN_DOC_010::P001", "VN_DOC_010::P002"],
        "expected_keywords": ["an toàn dữ liệu", "bảo mật"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_150",
        "category": "answerable",
        "document_id": "VN_DOC_010",
        "expected_decision": "answer",
        "question": "Sự phối hợp của các cơ quan nào là cần thiết cho kế hoạch mở rộng toàn quốc?",
        "ground_truth_answer": "sự phối hợp của các bộ ngành chuyên trách",
        "target_passages": ["VN_DOC_010::P000", "VN_DOC_010::P001", "VN_DOC_010::P002"],
        "expected_keywords": ["bộ ngành chuyên trách"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_151",
        "category": "answerable",
        "document_id": "VN_DOC_011",
        "expected_decision": "answer",
        "question": "Lĩnh vực nghiên cứu chính của tài liệu là gì?",
        "ground_truth_answer": "Hàng không Vũ trụ",
        "target_passages": ["VN_DOC_011::P000", "VN_DOC_011::P001", "VN_DOC_011::P002"],
        "expected_keywords": ["Hàng không Vũ trụ"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_152",
        "category": "answerable",
        "document_id": "VN_DOC_011",
        "expected_decision": "answer",
        "question": "Giai đoạn áp dụng chính sách quản lý được đề cập kéo dài từ năm nào đến năm nào?",
        "ground_truth_answer": "giai đoạn 2024-2030",
        "target_passages": ["VN_DOC_011::P000", "VN_DOC_011::P001", "VN_DOC_011::P002"],
        "expected_keywords": ["2024", "2030"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_153",
        "category": "answerable",
        "document_id": "VN_DOC_011",
        "expected_decision": "answer",
        "question": "Việc áp dụng tiêu chuẩn quốc tế giúp nâng cao hiệu suất vận hành bao nhiêu phần trăm?",
        "ground_truth_answer": "35% hiệu suất vận hành",
        "target_passages": ["VN_DOC_011::P000", "VN_DOC_011::P001", "VN_DOC_011::P002"],
        "expected_keywords": ["35%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_154",
        "category": "answerable",
        "document_id": "VN_DOC_011",
        "expected_decision": "answer",
        "question": "Hệ thống vận hành được phân cấp thành bao nhiêu tầng chức năng độc lập?",
        "ground_truth_answer": "3 tầng chức năng độc lập",
        "target_passages": ["VN_DOC_011::P000", "VN_DOC_011::P001", "VN_DOC_011::P002"],
        "expected_keywords": ["3 tầng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_155",
        "category": "answerable",
        "document_id": "VN_DOC_011",
        "expected_decision": "answer",
        "question": "Tầng đầu tiên trong kiến trúc phân cấp của hệ thống đảm nhiệm vai trò gì?",
        "ground_truth_answer": "thu thập dữ liệu cơ sở",
        "target_passages": ["VN_DOC_011::P000", "VN_DOC_011::P001", "VN_DOC_011::P002"],
        "expected_keywords": ["thu thập dữ liệu"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_156",
        "category": "answerable",
        "document_id": "VN_DOC_011",
        "expected_decision": "answer",
        "question": "Tầng chức năng trung gian của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "phân tích xử lý trung gian",
        "target_passages": ["VN_DOC_011::P000", "VN_DOC_011::P001", "VN_DOC_011::P002"],
        "expected_keywords": ["phân tích", "xử lý"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_157",
        "category": "answerable",
        "document_id": "VN_DOC_011",
        "expected_decision": "answer",
        "question": "Tầng cao nhất của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "báo cáo điều hành vĩ mô",
        "target_passages": ["VN_DOC_011::P000", "VN_DOC_011::P001", "VN_DOC_011::P002"],
        "expected_keywords": ["điều hành vĩ mô", "báo cáo"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_158",
        "category": "answerable",
        "document_id": "VN_DOC_011",
        "expected_decision": "answer",
        "question": "Thời gian đáp ứng tối đa của từng tầng được quy định là bao nhiêu?",
        "ground_truth_answer": "dưới 200 mili-giây",
        "target_passages": ["VN_DOC_011::P000", "VN_DOC_011::P001", "VN_DOC_011::P002"],
        "expected_keywords": ["200", "mili-giây"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_159",
        "category": "answerable",
        "document_id": "VN_DOC_011",
        "expected_decision": "answer",
        "question": "Giai đoạn thử nghiệm diện hẹp đã được tiến hành tại bao nhiêu đơn vị cơ sở?",
        "ground_truth_answer": "5 đơn vị cơ sở",
        "target_passages": ["VN_DOC_011::P000", "VN_DOC_011::P001", "VN_DOC_011::P002"],
        "expected_keywords": ["5 đơn vị"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_160",
        "category": "answerable",
        "document_id": "VN_DOC_011",
        "expected_decision": "answer",
        "question": "Tổng ngân sách tiết kiệm được trong giai đoạn thử nghiệm diện hẹp là bao nhiêu?",
        "ground_truth_answer": "15,8 tỷ đồng",
        "target_passages": ["VN_DOC_011::P000", "VN_DOC_011::P001", "VN_DOC_011::P002"],
        "expected_keywords": ["15,8 tỷ", "đồng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_161",
        "category": "answerable",
        "document_id": "VN_DOC_011",
        "expected_decision": "answer",
        "question": "Mức độ hài lòng của người dùng đạt được trong giai đoạn thử nghiệm là bao nhiêu phần trăm?",
        "ground_truth_answer": "94,5%",
        "target_passages": ["VN_DOC_011::P000", "VN_DOC_011::P001", "VN_DOC_011::P002"],
        "expected_keywords": ["94,5%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_162",
        "category": "answerable",
        "document_id": "VN_DOC_011",
        "expected_decision": "answer",
        "question": "Kế hoạch triển khai mở rộng toàn quốc dự kiến hoàn thành vào thời gian nào?",
        "ground_truth_answer": "quý IV năm 2026",
        "target_passages": ["VN_DOC_011::P000", "VN_DOC_011::P001", "VN_DOC_011::P002"],
        "expected_keywords": ["quý IV", "2026"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_163",
        "category": "answerable",
        "document_id": "VN_DOC_011",
        "expected_decision": "answer",
        "question": "Phương pháp nào được so sánh với tiêu chuẩn quốc tế ISO trong việc nâng cao hiệu suất?",
        "ground_truth_answer": "phương pháp truyền thống",
        "target_passages": ["VN_DOC_011::P000", "VN_DOC_011::P001", "VN_DOC_011::P002"],
        "expected_keywords": ["phương pháp truyền thống"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_164",
        "category": "answerable",
        "document_id": "VN_DOC_011",
        "expected_decision": "answer",
        "question": "Yếu tố an toàn nào được kiểm soát nghiêm ngặt cùng với độ trễ dưới 200 mili-giây?",
        "ground_truth_answer": "an toàn dữ liệu và bảo mật chuyên ngành",
        "target_passages": ["VN_DOC_011::P000", "VN_DOC_011::P001", "VN_DOC_011::P002"],
        "expected_keywords": ["an toàn dữ liệu", "bảo mật"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_165",
        "category": "answerable",
        "document_id": "VN_DOC_011",
        "expected_decision": "answer",
        "question": "Sự phối hợp của các cơ quan nào là cần thiết cho kế hoạch mở rộng toàn quốc?",
        "ground_truth_answer": "sự phối hợp của các bộ ngành chuyên trách",
        "target_passages": ["VN_DOC_011::P000", "VN_DOC_011::P001", "VN_DOC_011::P002"],
        "expected_keywords": ["bộ ngành chuyên trách"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_166",
        "category": "answerable",
        "document_id": "VN_DOC_012",
        "expected_decision": "answer",
        "question": "Lĩnh vực nghiên cứu chính của tài liệu là gì?",
        "ground_truth_answer": "Tài nguyên & Môi trường",
        "target_passages": ["VN_DOC_012::P000", "VN_DOC_012::P001", "VN_DOC_012::P002"],
        "expected_keywords": ["Tài nguyên & Môi trường"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_167",
        "category": "answerable",
        "document_id": "VN_DOC_012",
        "expected_decision": "answer",
        "question": "Giai đoạn áp dụng chính sách quản lý được đề cập kéo dài từ năm nào đến năm nào?",
        "ground_truth_answer": "giai đoạn 2024-2030",
        "target_passages": ["VN_DOC_012::P000", "VN_DOC_012::P001", "VN_DOC_012::P002"],
        "expected_keywords": ["2024", "2030"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_168",
        "category": "answerable",
        "document_id": "VN_DOC_012",
        "expected_decision": "answer",
        "question": "Việc áp dụng tiêu chuẩn quốc tế giúp nâng cao hiệu suất vận hành bao nhiêu phần trăm?",
        "ground_truth_answer": "35% hiệu suất vận hành",
        "target_passages": ["VN_DOC_012::P000", "VN_DOC_012::P001", "VN_DOC_012::P002"],
        "expected_keywords": ["35%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_169",
        "category": "answerable",
        "document_id": "VN_DOC_012",
        "expected_decision": "answer",
        "question": "Hệ thống vận hành được phân cấp thành bao nhiêu tầng chức năng độc lập?",
        "ground_truth_answer": "3 tầng chức năng độc lập",
        "target_passages": ["VN_DOC_012::P000", "VN_DOC_012::P001", "VN_DOC_012::P002"],
        "expected_keywords": ["3 tầng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_170",
        "category": "answerable",
        "document_id": "VN_DOC_012",
        "expected_decision": "answer",
        "question": "Tầng đầu tiên trong kiến trúc phân cấp của hệ thống đảm nhiệm vai trò gì?",
        "ground_truth_answer": "thu thập dữ liệu cơ sở",
        "target_passages": ["VN_DOC_012::P000", "VN_DOC_012::P001", "VN_DOC_012::P002"],
        "expected_keywords": ["thu thập dữ liệu"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_171",
        "category": "answerable",
        "document_id": "VN_DOC_012",
        "expected_decision": "answer",
        "question": "Tầng chức năng trung gian của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "phân tích xử lý trung gian",
        "target_passages": ["VN_DOC_012::P000", "VN_DOC_012::P001", "VN_DOC_012::P002"],
        "expected_keywords": ["phân tích", "xử lý"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_172",
        "category": "answerable",
        "document_id": "VN_DOC_012",
        "expected_decision": "answer",
        "question": "Tầng cao nhất của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "báo cáo điều hành vĩ mô",
        "target_passages": ["VN_DOC_012::P000", "VN_DOC_012::P001", "VN_DOC_012::P002"],
        "expected_keywords": ["điều hành vĩ mô", "báo cáo"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_173",
        "category": "answerable",
        "document_id": "VN_DOC_012",
        "expected_decision": "answer",
        "question": "Thời gian đáp ứng tối đa của từng tầng được quy định là bao nhiêu?",
        "ground_truth_answer": "dưới 200 mili-giây",
        "target_passages": ["VN_DOC_012::P000", "VN_DOC_012::P001", "VN_DOC_012::P002"],
        "expected_keywords": ["200", "mili-giây"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_174",
        "category": "answerable",
        "document_id": "VN_DOC_012",
        "expected_decision": "answer",
        "question": "Giai đoạn thử nghiệm diện hẹp đã được tiến hành tại bao nhiêu đơn vị cơ sở?",
        "ground_truth_answer": "5 đơn vị cơ sở",
        "target_passages": ["VN_DOC_012::P000", "VN_DOC_012::P001", "VN_DOC_012::P002"],
        "expected_keywords": ["5 đơn vị"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_175",
        "category": "answerable",
        "document_id": "VN_DOC_012",
        "expected_decision": "answer",
        "question": "Tổng ngân sách tiết kiệm được trong giai đoạn thử nghiệm diện hẹp là bao nhiêu?",
        "ground_truth_answer": "15,8 tỷ đồng",
        "target_passages": ["VN_DOC_012::P000", "VN_DOC_012::P001", "VN_DOC_012::P002"],
        "expected_keywords": ["15,8 tỷ", "đồng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_176",
        "category": "answerable",
        "document_id": "VN_DOC_012",
        "expected_decision": "answer",
        "question": "Mức độ hài lòng của người dùng đạt được trong giai đoạn thử nghiệm là bao nhiêu phần trăm?",
        "ground_truth_answer": "94,5%",
        "target_passages": ["VN_DOC_012::P000", "VN_DOC_012::P001", "VN_DOC_012::P002"],
        "expected_keywords": ["94,5%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_177",
        "category": "answerable",
        "document_id": "VN_DOC_012",
        "expected_decision": "answer",
        "question": "Kế hoạch triển khai mở rộng toàn quốc dự kiến hoàn thành vào thời gian nào?",
        "ground_truth_answer": "quý IV năm 2026",
        "target_passages": ["VN_DOC_012::P000", "VN_DOC_012::P001", "VN_DOC_012::P002"],
        "expected_keywords": ["quý IV", "2026"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_178",
        "category": "answerable",
        "document_id": "VN_DOC_012",
        "expected_decision": "answer",
        "question": "Phương pháp nào được so sánh với tiêu chuẩn quốc tế ISO trong việc nâng cao hiệu suất?",
        "ground_truth_answer": "phương pháp truyền thống",
        "target_passages": ["VN_DOC_012::P000", "VN_DOC_012::P001", "VN_DOC_012::P002"],
        "expected_keywords": ["phương pháp truyền thống"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_179",
        "category": "answerable",
        "document_id": "VN_DOC_012",
        "expected_decision": "answer",
        "question": "Yếu tố an toàn nào được kiểm soát nghiêm ngặt cùng với độ trễ dưới 200 mili-giây?",
        "ground_truth_answer": "an toàn dữ liệu và bảo mật chuyên ngành",
        "target_passages": ["VN_DOC_012::P000", "VN_DOC_012::P001", "VN_DOC_012::P002"],
        "expected_keywords": ["an toàn dữ liệu", "bảo mật"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_180",
        "category": "answerable",
        "document_id": "VN_DOC_012",
        "expected_decision": "answer",
        "question": "Sự phối hợp của các cơ quan nào là cần thiết cho kế hoạch mở rộng toàn quốc?",
        "ground_truth_answer": "sự phối hợp của các bộ ngành chuyên trách",
        "target_passages": ["VN_DOC_012::P000", "VN_DOC_012::P001", "VN_DOC_012::P002"],
        "expected_keywords": ["bộ ngành chuyên trách"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_181",
        "category": "answerable",
        "document_id": "VN_DOC_013",
        "expected_decision": "answer",
        "question": "Lĩnh vực nghiên cứu chính của tài liệu là gì?",
        "ground_truth_answer": "Du lịch & Sinh thái",
        "target_passages": ["VN_DOC_013::P000", "VN_DOC_013::P001", "VN_DOC_013::P002"],
        "expected_keywords": ["Du lịch & Sinh thái"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_182",
        "category": "answerable",
        "document_id": "VN_DOC_013",
        "expected_decision": "answer",
        "question": "Giai đoạn áp dụng chính sách quản lý được đề cập kéo dài từ năm nào đến năm nào?",
        "ground_truth_answer": "giai đoạn 2024-2030",
        "target_passages": ["VN_DOC_013::P000", "VN_DOC_013::P001", "VN_DOC_013::P002"],
        "expected_keywords": ["2024", "2030"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_183",
        "category": "answerable",
        "document_id": "VN_DOC_013",
        "expected_decision": "answer",
        "question": "Việc áp dụng tiêu chuẩn quốc tế giúp nâng cao hiệu suất vận hành bao nhiêu phần trăm?",
        "ground_truth_answer": "35% hiệu suất vận hành",
        "target_passages": ["VN_DOC_013::P000", "VN_DOC_013::P001", "VN_DOC_013::P002"],
        "expected_keywords": ["35%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_184",
        "category": "answerable",
        "document_id": "VN_DOC_013",
        "expected_decision": "answer",
        "question": "Hệ thống vận hành được phân cấp thành bao nhiêu tầng chức năng độc lập?",
        "ground_truth_answer": "3 tầng chức năng độc lập",
        "target_passages": ["VN_DOC_013::P000", "VN_DOC_013::P001", "VN_DOC_013::P002"],
        "expected_keywords": ["3 tầng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_185",
        "category": "answerable",
        "document_id": "VN_DOC_013",
        "expected_decision": "answer",
        "question": "Tầng đầu tiên trong kiến trúc phân cấp của hệ thống đảm nhiệm vai trò gì?",
        "ground_truth_answer": "thu thập dữ liệu cơ sở",
        "target_passages": ["VN_DOC_013::P000", "VN_DOC_013::P001", "VN_DOC_013::P002"],
        "expected_keywords": ["thu thập dữ liệu"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_186",
        "category": "answerable",
        "document_id": "VN_DOC_013",
        "expected_decision": "answer",
        "question": "Tầng chức năng trung gian của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "phân tích xử lý trung gian",
        "target_passages": ["VN_DOC_013::P000", "VN_DOC_013::P001", "VN_DOC_013::P002"],
        "expected_keywords": ["phân tích", "xử lý"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_187",
        "category": "answerable",
        "document_id": "VN_DOC_013",
        "expected_decision": "answer",
        "question": "Tầng cao nhất của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "báo cáo điều hành vĩ mô",
        "target_passages": ["VN_DOC_013::P000", "VN_DOC_013::P001", "VN_DOC_013::P002"],
        "expected_keywords": ["điều hành vĩ mô", "báo cáo"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_188",
        "category": "answerable",
        "document_id": "VN_DOC_013",
        "expected_decision": "answer",
        "question": "Thời gian đáp ứng tối đa của từng tầng được quy định là bao nhiêu?",
        "ground_truth_answer": "dưới 200 mili-giây",
        "target_passages": ["VN_DOC_013::P000", "VN_DOC_013::P001", "VN_DOC_013::P002"],
        "expected_keywords": ["200", "mili-giây"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_189",
        "category": "answerable",
        "document_id": "VN_DOC_013",
        "expected_decision": "answer",
        "question": "Giai đoạn thử nghiệm diện hẹp đã được tiến hành tại bao nhiêu đơn vị cơ sở?",
        "ground_truth_answer": "5 đơn vị cơ sở",
        "target_passages": ["VN_DOC_013::P000", "VN_DOC_013::P001", "VN_DOC_013::P002"],
        "expected_keywords": ["5 đơn vị"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_190",
        "category": "answerable",
        "document_id": "VN_DOC_013",
        "expected_decision": "answer",
        "question": "Tổng ngân sách tiết kiệm được trong giai đoạn thử nghiệm diện hẹp là bao nhiêu?",
        "ground_truth_answer": "15,8 tỷ đồng",
        "target_passages": ["VN_DOC_013::P000", "VN_DOC_013::P001", "VN_DOC_013::P002"],
        "expected_keywords": ["15,8 tỷ", "đồng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_191",
        "category": "answerable",
        "document_id": "VN_DOC_013",
        "expected_decision": "answer",
        "question": "Mức độ hài lòng của người dùng đạt được trong giai đoạn thử nghiệm là bao nhiêu phần trăm?",
        "ground_truth_answer": "94,5%",
        "target_passages": ["VN_DOC_013::P000", "VN_DOC_013::P001", "VN_DOC_013::P002"],
        "expected_keywords": ["94,5%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_192",
        "category": "answerable",
        "document_id": "VN_DOC_013",
        "expected_decision": "answer",
        "question": "Kế hoạch triển khai mở rộng toàn quốc dự kiến hoàn thành vào thời gian nào?",
        "ground_truth_answer": "quý IV năm 2026",
        "target_passages": ["VN_DOC_013::P000", "VN_DOC_013::P001", "VN_DOC_013::P002"],
        "expected_keywords": ["quý IV", "2026"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_193",
        "category": "answerable",
        "document_id": "VN_DOC_013",
        "expected_decision": "answer",
        "question": "Phương pháp nào được so sánh với tiêu chuẩn quốc tế ISO trong việc nâng cao hiệu suất?",
        "ground_truth_answer": "phương pháp truyền thống",
        "target_passages": ["VN_DOC_013::P000", "VN_DOC_013::P001", "VN_DOC_013::P002"],
        "expected_keywords": ["phương pháp truyền thống"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_194",
        "category": "answerable",
        "document_id": "VN_DOC_013",
        "expected_decision": "answer",
        "question": "Yếu tố an toàn nào được kiểm soát nghiêm ngặt cùng với độ trễ dưới 200 mili-giây?",
        "ground_truth_answer": "an toàn dữ liệu và bảo mật chuyên ngành",
        "target_passages": ["VN_DOC_013::P000", "VN_DOC_013::P001", "VN_DOC_013::P002"],
        "expected_keywords": ["an toàn dữ liệu", "bảo mật"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_195",
        "category": "answerable",
        "document_id": "VN_DOC_013",
        "expected_decision": "answer",
        "question": "Sự phối hợp của các cơ quan nào là cần thiết cho kế hoạch mở rộng toàn quốc?",
        "ground_truth_answer": "sự phối hợp của các bộ ngành chuyên trách",
        "target_passages": ["VN_DOC_013::P000", "VN_DOC_013::P001", "VN_DOC_013::P002"],
        "expected_keywords": ["bộ ngành chuyên trách"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_196",
        "category": "answerable",
        "document_id": "VN_DOC_014",
        "expected_decision": "answer",
        "question": "Lĩnh vực nghiên cứu chính của tài liệu là gì?",
        "ground_truth_answer": "Sở hữu Trí tuệ",
        "target_passages": ["VN_DOC_014::P000", "VN_DOC_014::P001", "VN_DOC_014::P002"],
        "expected_keywords": ["Sở hữu Trí tuệ"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_197",
        "category": "answerable",
        "document_id": "VN_DOC_014",
        "expected_decision": "answer",
        "question": "Giai đoạn áp dụng chính sách quản lý được đề cập kéo dài từ năm nào đến năm nào?",
        "ground_truth_answer": "giai đoạn 2024-2030",
        "target_passages": ["VN_DOC_014::P000", "VN_DOC_014::P001", "VN_DOC_014::P002"],
        "expected_keywords": ["2024", "2030"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_198",
        "category": "answerable",
        "document_id": "VN_DOC_014",
        "expected_decision": "answer",
        "question": "Việc áp dụng tiêu chuẩn quốc tế giúp nâng cao hiệu suất vận hành bao nhiêu phần trăm?",
        "ground_truth_answer": "35% hiệu suất vận hành",
        "target_passages": ["VN_DOC_014::P000", "VN_DOC_014::P001", "VN_DOC_014::P002"],
        "expected_keywords": ["35%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_199",
        "category": "answerable",
        "document_id": "VN_DOC_014",
        "expected_decision": "answer",
        "question": "Hệ thống vận hành được phân cấp thành bao nhiêu tầng chức năng độc lập?",
        "ground_truth_answer": "3 tầng chức năng độc lập",
        "target_passages": ["VN_DOC_014::P000", "VN_DOC_014::P001", "VN_DOC_014::P002"],
        "expected_keywords": ["3 tầng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_200",
        "category": "answerable",
        "document_id": "VN_DOC_014",
        "expected_decision": "answer",
        "question": "Tầng đầu tiên trong kiến trúc phân cấp của hệ thống đảm nhiệm vai trò gì?",
        "ground_truth_answer": "thu thập dữ liệu cơ sở",
        "target_passages": ["VN_DOC_014::P000", "VN_DOC_014::P001", "VN_DOC_014::P002"],
        "expected_keywords": ["thu thập dữ liệu"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_201",
        "category": "answerable",
        "document_id": "VN_DOC_014",
        "expected_decision": "answer",
        "question": "Tầng chức năng trung gian của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "phân tích xử lý trung gian",
        "target_passages": ["VN_DOC_014::P000", "VN_DOC_014::P001", "VN_DOC_014::P002"],
        "expected_keywords": ["phân tích", "xử lý"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_202",
        "category": "answerable",
        "document_id": "VN_DOC_014",
        "expected_decision": "answer",
        "question": "Tầng cao nhất của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "báo cáo điều hành vĩ mô",
        "target_passages": ["VN_DOC_014::P000", "VN_DOC_014::P001", "VN_DOC_014::P002"],
        "expected_keywords": ["điều hành vĩ mô", "báo cáo"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_203",
        "category": "answerable",
        "document_id": "VN_DOC_014",
        "expected_decision": "answer",
        "question": "Thời gian đáp ứng tối đa của từng tầng được quy định là bao nhiêu?",
        "ground_truth_answer": "dưới 200 mili-giây",
        "target_passages": ["VN_DOC_014::P000", "VN_DOC_014::P001", "VN_DOC_014::P002"],
        "expected_keywords": ["200", "mili-giây"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_204",
        "category": "answerable",
        "document_id": "VN_DOC_014",
        "expected_decision": "answer",
        "question": "Giai đoạn thử nghiệm diện hẹp đã được tiến hành tại bao nhiêu đơn vị cơ sở?",
        "ground_truth_answer": "5 đơn vị cơ sở",
        "target_passages": ["VN_DOC_014::P000", "VN_DOC_014::P001", "VN_DOC_014::P002"],
        "expected_keywords": ["5 đơn vị"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_205",
        "category": "answerable",
        "document_id": "VN_DOC_014",
        "expected_decision": "answer",
        "question": "Tổng ngân sách tiết kiệm được trong giai đoạn thử nghiệm diện hẹp là bao nhiêu?",
        "ground_truth_answer": "15,8 tỷ đồng",
        "target_passages": ["VN_DOC_014::P000", "VN_DOC_014::P001", "VN_DOC_014::P002"],
        "expected_keywords": ["15,8 tỷ", "đồng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_206",
        "category": "answerable",
        "document_id": "VN_DOC_014",
        "expected_decision": "answer",
        "question": "Mức độ hài lòng của người dùng đạt được trong giai đoạn thử nghiệm là bao nhiêu phần trăm?",
        "ground_truth_answer": "94,5%",
        "target_passages": ["VN_DOC_014::P000", "VN_DOC_014::P001", "VN_DOC_014::P002"],
        "expected_keywords": ["94,5%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_207",
        "category": "answerable",
        "document_id": "VN_DOC_014",
        "expected_decision": "answer",
        "question": "Kế hoạch triển khai mở rộng toàn quốc dự kiến hoàn thành vào thời gian nào?",
        "ground_truth_answer": "quý IV năm 2026",
        "target_passages": ["VN_DOC_014::P000", "VN_DOC_014::P001", "VN_DOC_014::P002"],
        "expected_keywords": ["quý IV", "2026"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_208",
        "category": "answerable",
        "document_id": "VN_DOC_014",
        "expected_decision": "answer",
        "question": "Phương pháp nào được so sánh với tiêu chuẩn quốc tế ISO trong việc nâng cao hiệu suất?",
        "ground_truth_answer": "phương pháp truyền thống",
        "target_passages": ["VN_DOC_014::P000", "VN_DOC_014::P001", "VN_DOC_014::P002"],
        "expected_keywords": ["phương pháp truyền thống"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_209",
        "category": "answerable",
        "document_id": "VN_DOC_014",
        "expected_decision": "answer",
        "question": "Yếu tố an toàn nào được kiểm soát nghiêm ngặt cùng với độ trễ dưới 200 mili-giây?",
        "ground_truth_answer": "an toàn dữ liệu và bảo mật chuyên ngành",
        "target_passages": ["VN_DOC_014::P000", "VN_DOC_014::P001", "VN_DOC_014::P002"],
        "expected_keywords": ["an toàn dữ liệu", "bảo mật"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_210",
        "category": "answerable",
        "document_id": "VN_DOC_014",
        "expected_decision": "answer",
        "question": "Sự phối hợp của các cơ quan nào là cần thiết cho kế hoạch mở rộng toàn quốc?",
        "ground_truth_answer": "sự phối hợp của các bộ ngành chuyên trách",
        "target_passages": ["VN_DOC_014::P000", "VN_DOC_014::P001", "VN_DOC_014::P002"],
        "expected_keywords": ["bộ ngành chuyên trách"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_211",
        "category": "answerable",
        "document_id": "VN_DOC_015",
        "expected_decision": "answer",
        "question": "Lĩnh vực nghiên cứu chính của tài liệu là gì?",
        "ground_truth_answer": "Logistics & Hàng hải",
        "target_passages": ["VN_DOC_015::P000", "VN_DOC_015::P001", "VN_DOC_015::P002"],
        "expected_keywords": ["Logistics & Hàng hải"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_212",
        "category": "answerable",
        "document_id": "VN_DOC_015",
        "expected_decision": "answer",
        "question": "Giai đoạn áp dụng chính sách quản lý được đề cập kéo dài từ năm nào đến năm nào?",
        "ground_truth_answer": "giai đoạn 2024-2030",
        "target_passages": ["VN_DOC_015::P000", "VN_DOC_015::P001", "VN_DOC_015::P002"],
        "expected_keywords": ["2024", "2030"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_213",
        "category": "answerable",
        "document_id": "VN_DOC_015",
        "expected_decision": "answer",
        "question": "Việc áp dụng tiêu chuẩn quốc tế giúp nâng cao hiệu suất vận hành bao nhiêu phần trăm?",
        "ground_truth_answer": "35% hiệu suất vận hành",
        "target_passages": ["VN_DOC_015::P000", "VN_DOC_015::P001", "VN_DOC_015::P002"],
        "expected_keywords": ["35%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_214",
        "category": "answerable",
        "document_id": "VN_DOC_015",
        "expected_decision": "answer",
        "question": "Hệ thống vận hành được phân cấp thành bao nhiêu tầng chức năng độc lập?",
        "ground_truth_answer": "3 tầng chức năng độc lập",
        "target_passages": ["VN_DOC_015::P000", "VN_DOC_015::P001", "VN_DOC_015::P002"],
        "expected_keywords": ["3 tầng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_215",
        "category": "answerable",
        "document_id": "VN_DOC_015",
        "expected_decision": "answer",
        "question": "Tầng đầu tiên trong kiến trúc phân cấp của hệ thống đảm nhiệm vai trò gì?",
        "ground_truth_answer": "thu thập dữ liệu cơ sở",
        "target_passages": ["VN_DOC_015::P000", "VN_DOC_015::P001", "VN_DOC_015::P002"],
        "expected_keywords": ["thu thập dữ liệu"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_216",
        "category": "answerable",
        "document_id": "VN_DOC_015",
        "expected_decision": "answer",
        "question": "Tầng chức năng trung gian của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "phân tích xử lý trung gian",
        "target_passages": ["VN_DOC_015::P000", "VN_DOC_015::P001", "VN_DOC_015::P002"],
        "expected_keywords": ["phân tích", "xử lý"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_217",
        "category": "answerable",
        "document_id": "VN_DOC_015",
        "expected_decision": "answer",
        "question": "Tầng cao nhất của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "báo cáo điều hành vĩ mô",
        "target_passages": ["VN_DOC_015::P000", "VN_DOC_015::P001", "VN_DOC_015::P002"],
        "expected_keywords": ["điều hành vĩ mô", "báo cáo"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_218",
        "category": "answerable",
        "document_id": "VN_DOC_015",
        "expected_decision": "answer",
        "question": "Thời gian đáp ứng tối đa của từng tầng được quy định là bao nhiêu?",
        "ground_truth_answer": "dưới 200 mili-giây",
        "target_passages": ["VN_DOC_015::P000", "VN_DOC_015::P001", "VN_DOC_015::P002"],
        "expected_keywords": ["200", "mili-giây"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_219",
        "category": "answerable",
        "document_id": "VN_DOC_015",
        "expected_decision": "answer",
        "question": "Giai đoạn thử nghiệm diện hẹp đã được tiến hành tại bao nhiêu đơn vị cơ sở?",
        "ground_truth_answer": "5 đơn vị cơ sở",
        "target_passages": ["VN_DOC_015::P000", "VN_DOC_015::P001", "VN_DOC_015::P002"],
        "expected_keywords": ["5 đơn vị"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_220",
        "category": "answerable",
        "document_id": "VN_DOC_015",
        "expected_decision": "answer",
        "question": "Tổng ngân sách tiết kiệm được trong giai đoạn thử nghiệm diện hẹp là bao nhiêu?",
        "ground_truth_answer": "15,8 tỷ đồng",
        "target_passages": ["VN_DOC_015::P000", "VN_DOC_015::P001", "VN_DOC_015::P002"],
        "expected_keywords": ["15,8 tỷ", "đồng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_221",
        "category": "answerable",
        "document_id": "VN_DOC_015",
        "expected_decision": "answer",
        "question": "Mức độ hài lòng của người dùng đạt được trong giai đoạn thử nghiệm là bao nhiêu phần trăm?",
        "ground_truth_answer": "94,5%",
        "target_passages": ["VN_DOC_015::P000", "VN_DOC_015::P001", "VN_DOC_015::P002"],
        "expected_keywords": ["94,5%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_222",
        "category": "answerable",
        "document_id": "VN_DOC_015",
        "expected_decision": "answer",
        "question": "Kế hoạch triển khai mở rộng toàn quốc dự kiến hoàn thành vào thời gian nào?",
        "ground_truth_answer": "quý IV năm 2026",
        "target_passages": ["VN_DOC_015::P000", "VN_DOC_015::P001", "VN_DOC_015::P002"],
        "expected_keywords": ["quý IV", "2026"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_223",
        "category": "answerable",
        "document_id": "VN_DOC_015",
        "expected_decision": "answer",
        "question": "Phương pháp nào được so sánh với tiêu chuẩn quốc tế ISO trong việc nâng cao hiệu suất?",
        "ground_truth_answer": "phương pháp truyền thống",
        "target_passages": ["VN_DOC_015::P000", "VN_DOC_015::P001", "VN_DOC_015::P002"],
        "expected_keywords": ["phương pháp truyền thống"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_224",
        "category": "answerable",
        "document_id": "VN_DOC_015",
        "expected_decision": "answer",
        "question": "Yếu tố an toàn nào được kiểm soát nghiêm ngặt cùng với độ trễ dưới 200 mili-giây?",
        "ground_truth_answer": "an toàn dữ liệu và bảo mật chuyên ngành",
        "target_passages": ["VN_DOC_015::P000", "VN_DOC_015::P001", "VN_DOC_015::P002"],
        "expected_keywords": ["an toàn dữ liệu", "bảo mật"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_225",
        "category": "answerable",
        "document_id": "VN_DOC_015",
        "expected_decision": "answer",
        "question": "Sự phối hợp của các cơ quan nào là cần thiết cho kế hoạch mở rộng toàn quốc?",
        "ground_truth_answer": "sự phối hợp của các bộ ngành chuyên trách",
        "target_passages": ["VN_DOC_015::P000", "VN_DOC_015::P001", "VN_DOC_015::P002"],
        "expected_keywords": ["bộ ngành chuyên trách"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_226",
        "category": "answerable",
        "document_id": "VN_DOC_016",
        "expected_decision": "answer",
        "question": "Lĩnh vực nghiên cứu chính của tài liệu là gì?",
        "ground_truth_answer": "Nông nghiệp Chế biến",
        "target_passages": ["VN_DOC_016::P000", "VN_DOC_016::P001", "VN_DOC_016::P002"],
        "expected_keywords": ["Nông nghiệp Chế biến"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_227",
        "category": "answerable",
        "document_id": "VN_DOC_016",
        "expected_decision": "answer",
        "question": "Giai đoạn áp dụng chính sách quản lý được đề cập kéo dài từ năm nào đến năm nào?",
        "ground_truth_answer": "giai đoạn 2024-2030",
        "target_passages": ["VN_DOC_016::P000", "VN_DOC_016::P001", "VN_DOC_016::P002"],
        "expected_keywords": ["2024", "2030"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_228",
        "category": "answerable",
        "document_id": "VN_DOC_016",
        "expected_decision": "answer",
        "question": "Việc áp dụng tiêu chuẩn quốc tế giúp nâng cao hiệu suất vận hành bao nhiêu phần trăm?",
        "ground_truth_answer": "35% hiệu suất vận hành",
        "target_passages": ["VN_DOC_016::P000", "VN_DOC_016::P001", "VN_DOC_016::P002"],
        "expected_keywords": ["35%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_229",
        "category": "answerable",
        "document_id": "VN_DOC_016",
        "expected_decision": "answer",
        "question": "Hệ thống vận hành được phân cấp thành bao nhiêu tầng chức năng độc lập?",
        "ground_truth_answer": "3 tầng chức năng độc lập",
        "target_passages": ["VN_DOC_016::P000", "VN_DOC_016::P001", "VN_DOC_016::P002"],
        "expected_keywords": ["3 tầng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_230",
        "category": "answerable",
        "document_id": "VN_DOC_016",
        "expected_decision": "answer",
        "question": "Tầng đầu tiên trong kiến trúc phân cấp của hệ thống đảm nhiệm vai trò gì?",
        "ground_truth_answer": "thu thập dữ liệu cơ sở",
        "target_passages": ["VN_DOC_016::P000", "VN_DOC_016::P001", "VN_DOC_016::P002"],
        "expected_keywords": ["thu thập dữ liệu"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_231",
        "category": "answerable",
        "document_id": "VN_DOC_016",
        "expected_decision": "answer",
        "question": "Tầng chức năng trung gian của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "phân tích xử lý trung gian",
        "target_passages": ["VN_DOC_016::P000", "VN_DOC_016::P001", "VN_DOC_016::P002"],
        "expected_keywords": ["phân tích", "xử lý"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_232",
        "category": "answerable",
        "document_id": "VN_DOC_016",
        "expected_decision": "answer",
        "question": "Tầng cao nhất của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "báo cáo điều hành vĩ mô",
        "target_passages": ["VN_DOC_016::P000", "VN_DOC_016::P001", "VN_DOC_016::P002"],
        "expected_keywords": ["điều hành vĩ mô", "báo cáo"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_233",
        "category": "answerable",
        "document_id": "VN_DOC_016",
        "expected_decision": "answer",
        "question": "Thời gian đáp ứng tối đa của từng tầng được quy định là bao nhiêu?",
        "ground_truth_answer": "dưới 200 mili-giây",
        "target_passages": ["VN_DOC_016::P000", "VN_DOC_016::P001", "VN_DOC_016::P002"],
        "expected_keywords": ["200", "mili-giây"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_234",
        "category": "answerable",
        "document_id": "VN_DOC_016",
        "expected_decision": "answer",
        "question": "Giai đoạn thử nghiệm diện hẹp đã được tiến hành tại bao nhiêu đơn vị cơ sở?",
        "ground_truth_answer": "5 đơn vị cơ sở",
        "target_passages": ["VN_DOC_016::P000", "VN_DOC_016::P001", "VN_DOC_016::P002"],
        "expected_keywords": ["5 đơn vị"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_235",
        "category": "answerable",
        "document_id": "VN_DOC_016",
        "expected_decision": "answer",
        "question": "Tổng ngân sách tiết kiệm được trong giai đoạn thử nghiệm diện hẹp là bao nhiêu?",
        "ground_truth_answer": "15,8 tỷ đồng",
        "target_passages": ["VN_DOC_016::P000", "VN_DOC_016::P001", "VN_DOC_016::P002"],
        "expected_keywords": ["15,8 tỷ", "đồng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_236",
        "category": "answerable",
        "document_id": "VN_DOC_016",
        "expected_decision": "answer",
        "question": "Mức độ hài lòng của người dùng đạt được trong giai đoạn thử nghiệm là bao nhiêu phần trăm?",
        "ground_truth_answer": "94,5%",
        "target_passages": ["VN_DOC_016::P000", "VN_DOC_016::P001", "VN_DOC_016::P002"],
        "expected_keywords": ["94,5%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_237",
        "category": "answerable",
        "document_id": "VN_DOC_016",
        "expected_decision": "answer",
        "question": "Kế hoạch triển khai mở rộng toàn quốc dự kiến hoàn thành vào thời gian nào?",
        "ground_truth_answer": "quý IV năm 2026",
        "target_passages": ["VN_DOC_016::P000", "VN_DOC_016::P001", "VN_DOC_016::P002"],
        "expected_keywords": ["quý IV", "2026"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_238",
        "category": "answerable",
        "document_id": "VN_DOC_016",
        "expected_decision": "answer",
        "question": "Phương pháp nào được so sánh với tiêu chuẩn quốc tế ISO trong việc nâng cao hiệu suất?",
        "ground_truth_answer": "phương pháp truyền thống",
        "target_passages": ["VN_DOC_016::P000", "VN_DOC_016::P001", "VN_DOC_016::P002"],
        "expected_keywords": ["phương pháp truyền thống"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_239",
        "category": "answerable",
        "document_id": "VN_DOC_016",
        "expected_decision": "answer",
        "question": "Yếu tố an toàn nào được kiểm soát nghiêm ngặt cùng với độ trễ dưới 200 mili-giây?",
        "ground_truth_answer": "an toàn dữ liệu và bảo mật chuyên ngành",
        "target_passages": ["VN_DOC_016::P000", "VN_DOC_016::P001", "VN_DOC_016::P002"],
        "expected_keywords": ["an toàn dữ liệu", "bảo mật"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_240",
        "category": "answerable",
        "document_id": "VN_DOC_016",
        "expected_decision": "answer",
        "question": "Sự phối hợp của các cơ quan nào là cần thiết cho kế hoạch mở rộng toàn quốc?",
        "ground_truth_answer": "sự phối hợp của các bộ ngành chuyên trách",
        "target_passages": ["VN_DOC_016::P000", "VN_DOC_016::P001", "VN_DOC_016::P002"],
        "expected_keywords": ["bộ ngành chuyên trách"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_241",
        "category": "answerable",
        "document_id": "VN_DOC_017",
        "expected_decision": "answer",
        "question": "Lĩnh vực nghiên cứu chính của tài liệu là gì?",
        "ground_truth_answer": "Chính phủ Điện tử",
        "target_passages": ["VN_DOC_017::P000", "VN_DOC_017::P001", "VN_DOC_017::P002"],
        "expected_keywords": ["Chính phủ Điện tử"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_242",
        "category": "answerable",
        "document_id": "VN_DOC_017",
        "expected_decision": "answer",
        "question": "Giai đoạn áp dụng chính sách quản lý được đề cập kéo dài từ năm nào đến năm nào?",
        "ground_truth_answer": "giai đoạn 2024-2030",
        "target_passages": ["VN_DOC_017::P000", "VN_DOC_017::P001", "VN_DOC_017::P002"],
        "expected_keywords": ["2024", "2030"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_243",
        "category": "answerable",
        "document_id": "VN_DOC_017",
        "expected_decision": "answer",
        "question": "Việc áp dụng tiêu chuẩn quốc tế giúp nâng cao hiệu suất vận hành bao nhiêu phần trăm?",
        "ground_truth_answer": "35% hiệu suất vận hành",
        "target_passages": ["VN_DOC_017::P000", "VN_DOC_017::P001", "VN_DOC_017::P002"],
        "expected_keywords": ["35%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_244",
        "category": "answerable",
        "document_id": "VN_DOC_017",
        "expected_decision": "answer",
        "question": "Hệ thống vận hành được phân cấp thành bao nhiêu tầng chức năng độc lập?",
        "ground_truth_answer": "3 tầng chức năng độc lập",
        "target_passages": ["VN_DOC_017::P000", "VN_DOC_017::P001", "VN_DOC_017::P002"],
        "expected_keywords": ["3 tầng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_245",
        "category": "answerable",
        "document_id": "VN_DOC_017",
        "expected_decision": "answer",
        "question": "Tầng đầu tiên trong kiến trúc phân cấp của hệ thống đảm nhiệm vai trò gì?",
        "ground_truth_answer": "thu thập dữ liệu cơ sở",
        "target_passages": ["VN_DOC_017::P000", "VN_DOC_017::P001", "VN_DOC_017::P002"],
        "expected_keywords": ["thu thập dữ liệu"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_246",
        "category": "answerable",
        "document_id": "VN_DOC_017",
        "expected_decision": "answer",
        "question": "Tầng chức năng trung gian của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "phân tích xử lý trung gian",
        "target_passages": ["VN_DOC_017::P000", "VN_DOC_017::P001", "VN_DOC_017::P002"],
        "expected_keywords": ["phân tích", "xử lý"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_247",
        "category": "answerable",
        "document_id": "VN_DOC_017",
        "expected_decision": "answer",
        "question": "Tầng cao nhất của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "báo cáo điều hành vĩ mô",
        "target_passages": ["VN_DOC_017::P000", "VN_DOC_017::P001", "VN_DOC_017::P002"],
        "expected_keywords": ["điều hành vĩ mô", "báo cáo"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_248",
        "category": "answerable",
        "document_id": "VN_DOC_017",
        "expected_decision": "answer",
        "question": "Thời gian đáp ứng tối đa của từng tầng được quy định là bao nhiêu?",
        "ground_truth_answer": "dưới 200 mili-giây",
        "target_passages": ["VN_DOC_017::P000", "VN_DOC_017::P001", "VN_DOC_017::P002"],
        "expected_keywords": ["200", "mili-giây"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_249",
        "category": "answerable",
        "document_id": "VN_DOC_017",
        "expected_decision": "answer",
        "question": "Giai đoạn thử nghiệm diện hẹp đã được tiến hành tại bao nhiêu đơn vị cơ sở?",
        "ground_truth_answer": "5 đơn vị cơ sở",
        "target_passages": ["VN_DOC_017::P000", "VN_DOC_017::P001", "VN_DOC_017::P002"],
        "expected_keywords": ["5 đơn vị"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_250",
        "category": "answerable",
        "document_id": "VN_DOC_017",
        "expected_decision": "answer",
        "question": "Tổng ngân sách tiết kiệm được trong giai đoạn thử nghiệm diện hẹp là bao nhiêu?",
        "ground_truth_answer": "15,8 tỷ đồng",
        "target_passages": ["VN_DOC_017::P000", "VN_DOC_017::P001", "VN_DOC_017::P002"],
        "expected_keywords": ["15,8 tỷ", "đồng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_251",
        "category": "answerable",
        "document_id": "VN_DOC_017",
        "expected_decision": "answer",
        "question": "Mức độ hài lòng của người dùng đạt được trong giai đoạn thử nghiệm là bao nhiêu phần trăm?",
        "ground_truth_answer": "94,5%",
        "target_passages": ["VN_DOC_017::P000", "VN_DOC_017::P001", "VN_DOC_017::P002"],
        "expected_keywords": ["94,5%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_252",
        "category": "answerable",
        "document_id": "VN_DOC_017",
        "expected_decision": "answer",
        "question": "Kế hoạch triển khai mở rộng toàn quốc dự kiến hoàn thành vào thời gian nào?",
        "ground_truth_answer": "quý IV năm 2026",
        "target_passages": ["VN_DOC_017::P000", "VN_DOC_017::P001", "VN_DOC_017::P002"],
        "expected_keywords": ["quý IV", "2026"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_253",
        "category": "answerable",
        "document_id": "VN_DOC_017",
        "expected_decision": "answer",
        "question": "Phương pháp nào được so sánh với tiêu chuẩn quốc tế ISO trong việc nâng cao hiệu suất?",
        "ground_truth_answer": "phương pháp truyền thống",
        "target_passages": ["VN_DOC_017::P000", "VN_DOC_017::P001", "VN_DOC_017::P002"],
        "expected_keywords": ["phương pháp truyền thống"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_254",
        "category": "answerable",
        "document_id": "VN_DOC_017",
        "expected_decision": "answer",
        "question": "Yếu tố an toàn nào được kiểm soát nghiêm ngặt cùng với độ trễ dưới 200 mili-giây?",
        "ground_truth_answer": "an toàn dữ liệu và bảo mật chuyên ngành",
        "target_passages": ["VN_DOC_017::P000", "VN_DOC_017::P001", "VN_DOC_017::P002"],
        "expected_keywords": ["an toàn dữ liệu", "bảo mật"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_255",
        "category": "answerable",
        "document_id": "VN_DOC_017",
        "expected_decision": "answer",
        "question": "Sự phối hợp của các cơ quan nào là cần thiết cho kế hoạch mở rộng toàn quốc?",
        "ground_truth_answer": "sự phối hợp của các bộ ngành chuyên trách",
        "target_passages": ["VN_DOC_017::P000", "VN_DOC_017::P001", "VN_DOC_017::P002"],
        "expected_keywords": ["bộ ngành chuyên trách"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_256",
        "category": "answerable",
        "document_id": "VN_DOC_018",
        "expected_decision": "answer",
        "question": "Lĩnh vực nghiên cứu chính của tài liệu là gì?",
        "ground_truth_answer": "Ngân hàng & Giám sát",
        "target_passages": ["VN_DOC_018::P000", "VN_DOC_018::P001", "VN_DOC_018::P002"],
        "expected_keywords": ["Ngân hàng & Giám sát"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_257",
        "category": "answerable",
        "document_id": "VN_DOC_018",
        "expected_decision": "answer",
        "question": "Giai đoạn áp dụng chính sách quản lý được đề cập kéo dài từ năm nào đến năm nào?",
        "ground_truth_answer": "giai đoạn 2024-2030",
        "target_passages": ["VN_DOC_018::P000", "VN_DOC_018::P001", "VN_DOC_018::P002"],
        "expected_keywords": ["2024", "2030"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_258",
        "category": "answerable",
        "document_id": "VN_DOC_018",
        "expected_decision": "answer",
        "question": "Việc áp dụng tiêu chuẩn quốc tế giúp nâng cao hiệu suất vận hành bao nhiêu phần trăm?",
        "ground_truth_answer": "35% hiệu suất vận hành",
        "target_passages": ["VN_DOC_018::P000", "VN_DOC_018::P001", "VN_DOC_018::P002"],
        "expected_keywords": ["35%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_259",
        "category": "answerable",
        "document_id": "VN_DOC_018",
        "expected_decision": "answer",
        "question": "Hệ thống vận hành được phân cấp thành bao nhiêu tầng chức năng độc lập?",
        "ground_truth_answer": "3 tầng chức năng độc lập",
        "target_passages": ["VN_DOC_018::P000", "VN_DOC_018::P001", "VN_DOC_018::P002"],
        "expected_keywords": ["3 tầng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_260",
        "category": "answerable",
        "document_id": "VN_DOC_018",
        "expected_decision": "answer",
        "question": "Tầng đầu tiên trong kiến trúc phân cấp của hệ thống đảm nhiệm vai trò gì?",
        "ground_truth_answer": "thu thập dữ liệu cơ sở",
        "target_passages": ["VN_DOC_018::P000", "VN_DOC_018::P001", "VN_DOC_018::P002"],
        "expected_keywords": ["thu thập dữ liệu"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_261",
        "category": "answerable",
        "document_id": "VN_DOC_018",
        "expected_decision": "answer",
        "question": "Tầng chức năng trung gian của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "phân tích xử lý trung gian",
        "target_passages": ["VN_DOC_018::P000", "VN_DOC_018::P001", "VN_DOC_018::P002"],
        "expected_keywords": ["phân tích", "xử lý"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_262",
        "category": "answerable",
        "document_id": "VN_DOC_018",
        "expected_decision": "answer",
        "question": "Tầng cao nhất của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "báo cáo điều hành vĩ mô",
        "target_passages": ["VN_DOC_018::P000", "VN_DOC_018::P001", "VN_DOC_018::P002"],
        "expected_keywords": ["điều hành vĩ mô", "báo cáo"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_263",
        "category": "answerable",
        "document_id": "VN_DOC_018",
        "expected_decision": "answer",
        "question": "Thời gian đáp ứng tối đa của từng tầng được quy định là bao nhiêu?",
        "ground_truth_answer": "dưới 200 mili-giây",
        "target_passages": ["VN_DOC_018::P000", "VN_DOC_018::P001", "VN_DOC_018::P002"],
        "expected_keywords": ["200", "mili-giây"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_264",
        "category": "answerable",
        "document_id": "VN_DOC_018",
        "expected_decision": "answer",
        "question": "Giai đoạn thử nghiệm diện hẹp đã được tiến hành tại bao nhiêu đơn vị cơ sở?",
        "ground_truth_answer": "5 đơn vị cơ sở",
        "target_passages": ["VN_DOC_018::P000", "VN_DOC_018::P001", "VN_DOC_018::P002"],
        "expected_keywords": ["5 đơn vị"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_265",
        "category": "answerable",
        "document_id": "VN_DOC_018",
        "expected_decision": "answer",
        "question": "Tổng ngân sách tiết kiệm được trong giai đoạn thử nghiệm diện hẹp là bao nhiêu?",
        "ground_truth_answer": "15,8 tỷ đồng",
        "target_passages": ["VN_DOC_018::P000", "VN_DOC_018::P001", "VN_DOC_018::P002"],
        "expected_keywords": ["15,8 tỷ", "đồng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_266",
        "category": "answerable",
        "document_id": "VN_DOC_018",
        "expected_decision": "answer",
        "question": "Mức độ hài lòng của người dùng đạt được trong giai đoạn thử nghiệm là bao nhiêu phần trăm?",
        "ground_truth_answer": "94,5%",
        "target_passages": ["VN_DOC_018::P000", "VN_DOC_018::P001", "VN_DOC_018::P002"],
        "expected_keywords": ["94,5%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_267",
        "category": "answerable",
        "document_id": "VN_DOC_018",
        "expected_decision": "answer",
        "question": "Kế hoạch triển khai mở rộng toàn quốc dự kiến hoàn thành vào thời gian nào?",
        "ground_truth_answer": "quý IV năm 2026",
        "target_passages": ["VN_DOC_018::P000", "VN_DOC_018::P001", "VN_DOC_018::P002"],
        "expected_keywords": ["quý IV", "2026"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_268",
        "category": "answerable",
        "document_id": "VN_DOC_018",
        "expected_decision": "answer",
        "question": "Phương pháp nào được so sánh với tiêu chuẩn quốc tế ISO trong việc nâng cao hiệu suất?",
        "ground_truth_answer": "phương pháp truyền thống",
        "target_passages": ["VN_DOC_018::P000", "VN_DOC_018::P001", "VN_DOC_018::P002"],
        "expected_keywords": ["phương pháp truyền thống"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_269",
        "category": "answerable",
        "document_id": "VN_DOC_018",
        "expected_decision": "answer",
        "question": "Yếu tố an toàn nào được kiểm soát nghiêm ngặt cùng với độ trễ dưới 200 mili-giây?",
        "ground_truth_answer": "an toàn dữ liệu và bảo mật chuyên ngành",
        "target_passages": ["VN_DOC_018::P000", "VN_DOC_018::P001", "VN_DOC_018::P002"],
        "expected_keywords": ["an toàn dữ liệu", "bảo mật"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_270",
        "category": "answerable",
        "document_id": "VN_DOC_018",
        "expected_decision": "answer",
        "question": "Sự phối hợp của các cơ quan nào là cần thiết cho kế hoạch mở rộng toàn quốc?",
        "ground_truth_answer": "sự phối hợp của các bộ ngành chuyên trách",
        "target_passages": ["VN_DOC_018::P000", "VN_DOC_018::P001", "VN_DOC_018::P002"],
        "expected_keywords": ["bộ ngành chuyên trách"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_271",
        "category": "answerable",
        "document_id": "VN_DOC_019",
        "expected_decision": "answer",
        "question": "Lĩnh vực nghiên cứu chính của tài liệu là gì?",
        "ground_truth_answer": "Thủy sản & Công nghệ Sinh học",
        "target_passages": ["VN_DOC_019::P000", "VN_DOC_019::P001", "VN_DOC_019::P002"],
        "expected_keywords": ["Thủy sản & Công nghệ Sinh học"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_272",
        "category": "answerable",
        "document_id": "VN_DOC_019",
        "expected_decision": "answer",
        "question": "Giai đoạn áp dụng chính sách quản lý được đề cập kéo dài từ năm nào đến năm nào?",
        "ground_truth_answer": "giai đoạn 2024-2030",
        "target_passages": ["VN_DOC_019::P000", "VN_DOC_019::P001", "VN_DOC_019::P002"],
        "expected_keywords": ["2024", "2030"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_273",
        "category": "answerable",
        "document_id": "VN_DOC_019",
        "expected_decision": "answer",
        "question": "Việc áp dụng tiêu chuẩn quốc tế giúp nâng cao hiệu suất vận hành bao nhiêu phần trăm?",
        "ground_truth_answer": "35% hiệu suất vận hành",
        "target_passages": ["VN_DOC_019::P000", "VN_DOC_019::P001", "VN_DOC_019::P002"],
        "expected_keywords": ["35%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_274",
        "category": "answerable",
        "document_id": "VN_DOC_019",
        "expected_decision": "answer",
        "question": "Hệ thống vận hành được phân cấp thành bao nhiêu tầng chức năng độc lập?",
        "ground_truth_answer": "3 tầng chức năng độc lập",
        "target_passages": ["VN_DOC_019::P000", "VN_DOC_019::P001", "VN_DOC_019::P002"],
        "expected_keywords": ["3 tầng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_275",
        "category": "answerable",
        "document_id": "VN_DOC_019",
        "expected_decision": "answer",
        "question": "Tầng đầu tiên trong kiến trúc phân cấp của hệ thống đảm nhiệm vai trò gì?",
        "ground_truth_answer": "thu thập dữ liệu cơ sở",
        "target_passages": ["VN_DOC_019::P000", "VN_DOC_019::P001", "VN_DOC_019::P002"],
        "expected_keywords": ["thu thập dữ liệu"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_276",
        "category": "answerable",
        "document_id": "VN_DOC_019",
        "expected_decision": "answer",
        "question": "Tầng chức năng trung gian của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "phân tích xử lý trung gian",
        "target_passages": ["VN_DOC_019::P000", "VN_DOC_019::P001", "VN_DOC_019::P002"],
        "expected_keywords": ["phân tích", "xử lý"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_277",
        "category": "answerable",
        "document_id": "VN_DOC_019",
        "expected_decision": "answer",
        "question": "Tầng cao nhất của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "báo cáo điều hành vĩ mô",
        "target_passages": ["VN_DOC_019::P000", "VN_DOC_019::P001", "VN_DOC_019::P002"],
        "expected_keywords": ["điều hành vĩ mô", "báo cáo"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_278",
        "category": "answerable",
        "document_id": "VN_DOC_019",
        "expected_decision": "answer",
        "question": "Thời gian đáp ứng tối đa của từng tầng được quy định là bao nhiêu?",
        "ground_truth_answer": "dưới 200 mili-giây",
        "target_passages": ["VN_DOC_019::P000", "VN_DOC_019::P001", "VN_DOC_019::P002"],
        "expected_keywords": ["200", "mili-giây"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_279",
        "category": "answerable",
        "document_id": "VN_DOC_019",
        "expected_decision": "answer",
        "question": "Giai đoạn thử nghiệm diện hẹp đã được tiến hành tại bao nhiêu đơn vị cơ sở?",
        "ground_truth_answer": "5 đơn vị cơ sở",
        "target_passages": ["VN_DOC_019::P000", "VN_DOC_019::P001", "VN_DOC_019::P002"],
        "expected_keywords": ["5 đơn vị"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_280",
        "category": "answerable",
        "document_id": "VN_DOC_019",
        "expected_decision": "answer",
        "question": "Tổng ngân sách tiết kiệm được trong giai đoạn thử nghiệm diện hẹp là bao nhiêu?",
        "ground_truth_answer": "15,8 tỷ đồng",
        "target_passages": ["VN_DOC_019::P000", "VN_DOC_019::P001", "VN_DOC_019::P002"],
        "expected_keywords": ["15,8 tỷ", "đồng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_281",
        "category": "answerable",
        "document_id": "VN_DOC_019",
        "expected_decision": "answer",
        "question": "Mức độ hài lòng của người dùng đạt được trong giai đoạn thử nghiệm là bao nhiêu phần trăm?",
        "ground_truth_answer": "94,5%",
        "target_passages": ["VN_DOC_019::P000", "VN_DOC_019::P001", "VN_DOC_019::P002"],
        "expected_keywords": ["94,5%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_282",
        "category": "answerable",
        "document_id": "VN_DOC_019",
        "expected_decision": "answer",
        "question": "Kế hoạch triển khai mở rộng toàn quốc dự kiến hoàn thành vào thời gian nào?",
        "ground_truth_answer": "quý IV năm 2026",
        "target_passages": ["VN_DOC_019::P000", "VN_DOC_019::P001", "VN_DOC_019::P002"],
        "expected_keywords": ["quý IV", "2026"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_283",
        "category": "answerable",
        "document_id": "VN_DOC_019",
        "expected_decision": "answer",
        "question": "Phương pháp nào được so sánh với tiêu chuẩn quốc tế ISO trong việc nâng cao hiệu suất?",
        "ground_truth_answer": "phương pháp truyền thống",
        "target_passages": ["VN_DOC_019::P000", "VN_DOC_019::P001", "VN_DOC_019::P002"],
        "expected_keywords": ["phương pháp truyền thống"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_284",
        "category": "answerable",
        "document_id": "VN_DOC_019",
        "expected_decision": "answer",
        "question": "Yếu tố an toàn nào được kiểm soát nghiêm ngặt cùng với độ trễ dưới 200 mili-giây?",
        "ground_truth_answer": "an toàn dữ liệu và bảo mật chuyên ngành",
        "target_passages": ["VN_DOC_019::P000", "VN_DOC_019::P001", "VN_DOC_019::P002"],
        "expected_keywords": ["an toàn dữ liệu", "bảo mật"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_285",
        "category": "answerable",
        "document_id": "VN_DOC_019",
        "expected_decision": "answer",
        "question": "Sự phối hợp của các cơ quan nào là cần thiết cho kế hoạch mở rộng toàn quốc?",
        "ground_truth_answer": "sự phối hợp của các bộ ngành chuyên trách",
        "target_passages": ["VN_DOC_019::P000", "VN_DOC_019::P001", "VN_DOC_019::P002"],
        "expected_keywords": ["bộ ngành chuyên trách"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_286",
        "category": "answerable",
        "document_id": "VN_DOC_020",
        "expected_decision": "answer",
        "question": "Lĩnh vực nghiên cứu chính của tài liệu là gì?",
        "ground_truth_answer": "Đô thị & Biến đổi Khí hậu",
        "target_passages": ["VN_DOC_020::P000", "VN_DOC_020::P001", "VN_DOC_020::P002"],
        "expected_keywords": ["Đô thị & Biến đổi Khí hậu"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_287",
        "category": "answerable",
        "document_id": "VN_DOC_020",
        "expected_decision": "answer",
        "question": "Giai đoạn áp dụng chính sách quản lý được đề cập kéo dài từ năm nào đến năm nào?",
        "ground_truth_answer": "giai đoạn 2024-2030",
        "target_passages": ["VN_DOC_020::P000", "VN_DOC_020::P001", "VN_DOC_020::P002"],
        "expected_keywords": ["2024", "2030"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_288",
        "category": "answerable",
        "document_id": "VN_DOC_020",
        "expected_decision": "answer",
        "question": "Việc áp dụng tiêu chuẩn quốc tế giúp nâng cao hiệu suất vận hành bao nhiêu phần trăm?",
        "ground_truth_answer": "35% hiệu suất vận hành",
        "target_passages": ["VN_DOC_020::P000", "VN_DOC_020::P001", "VN_DOC_020::P002"],
        "expected_keywords": ["35%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_289",
        "category": "answerable",
        "document_id": "VN_DOC_020",
        "expected_decision": "answer",
        "question": "Hệ thống vận hành được phân cấp thành bao nhiêu tầng chức năng độc lập?",
        "ground_truth_answer": "3 tầng chức năng độc lập",
        "target_passages": ["VN_DOC_020::P000", "VN_DOC_020::P001", "VN_DOC_020::P002"],
        "expected_keywords": ["3 tầng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_290",
        "category": "answerable",
        "document_id": "VN_DOC_020",
        "expected_decision": "answer",
        "question": "Tầng đầu tiên trong kiến trúc phân cấp của hệ thống đảm nhiệm vai trò gì?",
        "ground_truth_answer": "thu thập dữ liệu cơ sở",
        "target_passages": ["VN_DOC_020::P000", "VN_DOC_020::P001", "VN_DOC_020::P002"],
        "expected_keywords": ["thu thập dữ liệu"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_291",
        "category": "answerable",
        "document_id": "VN_DOC_020",
        "expected_decision": "answer",
        "question": "Tầng chức năng trung gian của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "phân tích xử lý trung gian",
        "target_passages": ["VN_DOC_020::P000", "VN_DOC_020::P001", "VN_DOC_020::P002"],
        "expected_keywords": ["phân tích", "xử lý"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_292",
        "category": "answerable",
        "document_id": "VN_DOC_020",
        "expected_decision": "answer",
        "question": "Tầng cao nhất của hệ thống có nhiệm vụ gì?",
        "ground_truth_answer": "báo cáo điều hành vĩ mô",
        "target_passages": ["VN_DOC_020::P000", "VN_DOC_020::P001", "VN_DOC_020::P002"],
        "expected_keywords": ["điều hành vĩ mô", "báo cáo"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_293",
        "category": "answerable",
        "document_id": "VN_DOC_020",
        "expected_decision": "answer",
        "question": "Thời gian đáp ứng tối đa của từng tầng được quy định là bao nhiêu?",
        "ground_truth_answer": "dưới 200 mili-giây",
        "target_passages": ["VN_DOC_020::P000", "VN_DOC_020::P001", "VN_DOC_020::P002"],
        "expected_keywords": ["200", "mili-giây"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_294",
        "category": "answerable",
        "document_id": "VN_DOC_020",
        "expected_decision": "answer",
        "question": "Giai đoạn thử nghiệm diện hẹp đã được tiến hành tại bao nhiêu đơn vị cơ sở?",
        "ground_truth_answer": "5 đơn vị cơ sở",
        "target_passages": ["VN_DOC_020::P000", "VN_DOC_020::P001", "VN_DOC_020::P002"],
        "expected_keywords": ["5 đơn vị"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_295",
        "category": "answerable",
        "document_id": "VN_DOC_020",
        "expected_decision": "answer",
        "question": "Tổng ngân sách tiết kiệm được trong giai đoạn thử nghiệm diện hẹp là bao nhiêu?",
        "ground_truth_answer": "15,8 tỷ đồng",
        "target_passages": ["VN_DOC_020::P000", "VN_DOC_020::P001", "VN_DOC_020::P002"],
        "expected_keywords": ["15,8 tỷ", "đồng"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_296",
        "category": "answerable",
        "document_id": "VN_DOC_020",
        "expected_decision": "answer",
        "question": "Mức độ hài lòng của người dùng đạt được trong giai đoạn thử nghiệm là bao nhiêu phần trăm?",
        "ground_truth_answer": "94,5%",
        "target_passages": ["VN_DOC_020::P000", "VN_DOC_020::P001", "VN_DOC_020::P002"],
        "expected_keywords": ["94,5%"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_297",
        "category": "answerable",
        "document_id": "VN_DOC_020",
        "expected_decision": "answer",
        "question": "Kế hoạch triển khai mở rộng toàn quốc dự kiến hoàn thành vào thời gian nào?",
        "ground_truth_answer": "quý IV năm 2026",
        "target_passages": ["VN_DOC_020::P000", "VN_DOC_020::P001", "VN_DOC_020::P002"],
        "expected_keywords": ["quý IV", "2026"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_298",
        "category": "answerable",
        "document_id": "VN_DOC_020",
        "expected_decision": "answer",
        "question": "Phương pháp nào được so sánh với tiêu chuẩn quốc tế ISO trong việc nâng cao hiệu suất?",
        "ground_truth_answer": "phương pháp truyền thống",
        "target_passages": ["VN_DOC_020::P000", "VN_DOC_020::P001", "VN_DOC_020::P002"],
        "expected_keywords": ["phương pháp truyền thống"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_299",
        "category": "answerable",
        "document_id": "VN_DOC_020",
        "expected_decision": "answer",
        "question": "Yếu tố an toàn nào được kiểm soát nghiêm ngặt cùng với độ trễ dưới 200 mili-giây?",
        "ground_truth_answer": "an toàn dữ liệu và bảo mật chuyên ngành",
        "target_passages": ["VN_DOC_020::P000", "VN_DOC_020::P001", "VN_DOC_020::P002"],
        "expected_keywords": ["an toàn dữ liệu", "bảo mật"],
    })
    questions.append({
        "question_id": "VN_FINAL_ANS_300",
        "category": "answerable",
        "document_id": "VN_DOC_020",
        "expected_decision": "answer",
        "question": "Sự phối hợp của các cơ quan nào là cần thiết cho kế hoạch mở rộng toàn quốc?",
        "ground_truth_answer": "sự phối hợp của các bộ ngành chuyên trách",
        "target_passages": ["VN_DOC_020::P000", "VN_DOC_020::P001", "VN_DOC_020::P002"],
        "expected_keywords": ["bộ ngành chuyên trách"],
    })
    # -------------------------------------------------------------------------
    # 2. 50 QUESTIONS WITHOUT ANSWER (25 unanswerable + 25 insufficient)
    # -------------------------------------------------------------------------
    questions.append({
        "question_id": "VN_FINAL_UNANS_001",
        "category": "unanswerable",
        "document_id": "VN_DOC_001",
        "expected_decision": "refusal",
        "question": "Đội tuyển bóng đá nào đã vô địch World Cup năm 1970 tại Mexico?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_UNANS_002",
        "category": "unanswerable",
        "document_id": "VN_DOC_002",
        "expected_decision": "refusal",
        "question": "Nguyên lý bất định Heisenberg trong vật lý lượng tử được phát biểu bằng công thức toán học nào?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_UNANS_003",
        "category": "unanswerable",
        "document_id": "VN_DOC_003",
        "expected_decision": "refusal",
        "question": "Tác phẩm văn học Truyện Kiều của Nguyễn Du bao gồm chính xác bao nhiêu câu thơ lục bát?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_UNANS_004",
        "category": "unanswerable",
        "document_id": "VN_DOC_004",
        "expected_decision": "refusal",
        "question": "Hành tinh nào có khối lượng lớn nhất trong Hệ Mặt Trời của chúng ta?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_UNANS_005",
        "category": "unanswerable",
        "document_id": "VN_DOC_005",
        "expected_decision": "refusal",
        "question": "Nhà soạn nhạc Beethoven đã hoàn thành bản Giao hưởng số 9 vào năm nào?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_UNANS_006",
        "category": "unanswerable",
        "document_id": "VN_DOC_006",
        "expected_decision": "refusal",
        "question": "Tên của thủ đô nước Úc là thành phố nào?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_UNANS_007",
        "category": "unanswerable",
        "document_id": "VN_DOC_007",
        "expected_decision": "refusal",
        "question": "Công thức hóa học của hợp chất axit sunfuric là gì?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_UNANS_008",
        "category": "unanswerable",
        "document_id": "VN_DOC_008",
        "expected_decision": "refusal",
        "question": "Ai là người đầu tiên đặt chân lên Mặt Trăng vào năm 1969?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_UNANS_009",
        "category": "unanswerable",
        "document_id": "VN_DOC_009",
        "expected_decision": "refusal",
        "question": "Độ sâu tối đa của rãnh đại dương Mariana là bao nhiêu mét?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_UNANS_010",
        "category": "unanswerable",
        "document_id": "VN_DOC_010",
        "expected_decision": "refusal",
        "question": "Giải thưởng Nobel Hòa bình năm 2010 đã được trao cho cá nhân hoặc tổ chức nào?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_UNANS_011",
        "category": "unanswerable",
        "document_id": "VN_DOC_011",
        "expected_decision": "refusal",
        "question": "Đỉnh núi Everest có độ cao chính xác là bao nhiêu mét so với mực nước biển?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_UNANS_012",
        "category": "unanswerable",
        "document_id": "VN_DOC_012",
        "expected_decision": "refusal",
        "question": "Tháp Eiffel tại thủ đô Paris của Pháp được khánh thành vào năm nào?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_UNANS_013",
        "category": "unanswerable",
        "document_id": "VN_DOC_013",
        "expected_decision": "refusal",
        "question": "Vận tốc ánh sáng trong môi trường chân không xấp xỉ bằng bao nhiêu km trên giây?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_UNANS_014",
        "category": "unanswerable",
        "document_id": "VN_DOC_014",
        "expected_decision": "refusal",
        "question": "Tác phẩm Hội họa Mona Lisa của Leonardo da Vinci hiện được lưu trữ tại bảo tàng nào?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_UNANS_015",
        "category": "unanswerable",
        "document_id": "VN_DOC_015",
        "expected_decision": "refusal",
        "question": "Số lượng xương trong cơ thể một người trưởng thành bình thường là bao nhiêu chiếc?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_UNANS_016",
        "category": "unanswerable",
        "document_id": "VN_DOC_016",
        "expected_decision": "refusal",
        "question": "Kim tự tháp Giza nổi tiếng của Ai Cập cổ đại được xây dựng dưới triều đại pharaoh nào?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_UNANS_017",
        "category": "unanswerable",
        "document_id": "VN_DOC_017",
        "expected_decision": "refusal",
        "question": "Nguyên tố hóa học nào có ký hiệu là Au trong bảng tuần hoàn Mendeleev?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_UNANS_018",
        "category": "unanswerable",
        "document_id": "VN_DOC_018",
        "expected_decision": "refusal",
        "question": "Kênh đào Panama chính thức được khánh thành và đưa vào sử dụng từ năm nào?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_UNANS_019",
        "category": "unanswerable",
        "document_id": "VN_DOC_019",
        "expected_decision": "refusal",
        "question": "Loài động vật có vú nào sở hữu kích thước và khối lượng lớn nhất trên Trái Đất hiện nay?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_UNANS_020",
        "category": "unanswerable",
        "document_id": "VN_DOC_020",
        "expected_decision": "refusal",
        "question": "Ai là tác giả của thuyết Tương đối hẹp công bố vào năm 1905?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_UNANS_021",
        "category": "unanswerable",
        "document_id": "VN_DOC_001",
        "expected_decision": "refusal",
        "question": "Quốc gia nào có diện tích lãnh thổ tự nhiên lớn nhất thế giới hiện nay?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_UNANS_022",
        "category": "unanswerable",
        "document_id": "VN_DOC_002",
        "expected_decision": "refusal",
        "question": "Thành phố nào từng đăng cai tổ chức Thế vận hội Mùa hè Olympic năm 2008?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_UNANS_023",
        "category": "unanswerable",
        "document_id": "VN_DOC_003",
        "expected_decision": "refusal",
        "question": "Sông Nin chảy qua bao nhiêu quốc gia tại lục địa châu Phi?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_UNANS_024",
        "category": "unanswerable",
        "document_id": "VN_DOC_004",
        "expected_decision": "refusal",
        "question": "Hệ điều hành Linux ban đầu được sáng lập bởi lập trình viên nào?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_UNANS_025",
        "category": "unanswerable",
        "document_id": "VN_DOC_005",
        "expected_decision": "refusal",
        "question": "Tác phẩm kịch Hamlet nổi tiếng được sáng tác bởi đại văn hào nào của nước Anh?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_INSUFF_001",
        "category": "insufficient_evidence",
        "document_id": "VN_DOC_001",
        "expected_decision": "refusal",
        "question": "Tên chính xác của trưởng nhóm nghiên cứu thiết kế thuật toán SA-CMS là ai?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_INSUFF_002",
        "category": "insufficient_evidence",
        "document_id": "VN_DOC_002",
        "expected_decision": "refusal",
        "question": "Địa chỉ trụ sở chính của cơ quan thanh tra dữ liệu cá nhân nằm ở số nhà bao nhiêu?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_INSUFF_003",
        "category": "insufficient_evidence",
        "document_id": "VN_DOC_003",
        "expected_decision": "refusal",
        "question": "Chi phí phục chế chi tiết của từng chiếc bình hoa cổ trong điện Kiến Trung là bao nhiêu tiền?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_INSUFF_004",
        "category": "insufficient_evidence",
        "document_id": "VN_DOC_004",
        "expected_decision": "refusal",
        "question": "Tên tuổi cụ thể của người nông dân đầu tiên gieo cấy lúa ST25 chịu mặn tại Bến Tre là gì?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_INSUFF_005",
        "category": "insufficient_evidence",
        "document_id": "VN_DOC_005",
        "expected_decision": "refusal",
        "question": "Số điện thoại đường dây nóng của ban điều hành Quy hoạch Điện VIII là số nào?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_INSUFF_006",
        "category": "insufficient_evidence",
        "document_id": "VN_DOC_006",
        "expected_decision": "refusal",
        "question": "Danh sách họ tên 10 chuyên gia kiểm định độc lập của mạng lưới AUN-QA tại Việt Nam là gì?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_INSUFF_007",
        "category": "insufficient_evidence",
        "document_id": "VN_DOC_007",
        "expected_decision": "refusal",
        "question": "Mức lương khởi điểm chính xác tính bằng USD của kỹ sư thiết kế chip bán dẫn là bao nhiêu?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_INSUFF_008",
        "category": "insufficient_evidence",
        "document_id": "VN_DOC_008",
        "expected_decision": "refusal",
        "question": "Đơn giá vé tháng chi tiết cho học sinh trên tuyến đường sắt đô thị số 2 là bao nhiêu nghìn đồng?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_INSUFF_009",
        "category": "insufficient_evidence",
        "document_id": "VN_DOC_009",
        "expected_decision": "refusal",
        "question": "Biển kiểm soát của chiếc xe cứu thương đầu tiên tham gia diễn tập phòng chống dịch là gì?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_INSUFF_010",
        "category": "insufficient_evidence",
        "document_id": "VN_DOC_010",
        "expected_decision": "refusal",
        "question": "Mã PIN mặc định cho thẻ ghi nợ điện tử phát hành trong chương trình thử nghiệm là dãy số nào?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_INSUFF_011",
        "category": "insufficient_evidence",
        "document_id": "VN_DOC_011",
        "expected_decision": "refusal",
        "question": "Tần số vô tuyến bí mật điều khiển vệ tinh viễn thám quỹ đạo thấp là bao nhiêu megahertz?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_INSUFF_012",
        "category": "insufficient_evidence",
        "document_id": "VN_DOC_012",
        "expected_decision": "refusal",
        "question": "Nhãn hiệu loại túi nilon sinh học tự hủy được dùng tại chợ nổi miền Tây có tên thương mại là gì?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_INSUFF_013",
        "category": "insufficient_evidence",
        "document_id": "VN_DOC_013",
        "expected_decision": "refusal",
        "question": "Tên của cá thể voọc chà vá chân nâu già nhất tại Vườn Quốc gia là gì?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_INSUFF_014",
        "category": "insufficient_evidence",
        "document_id": "VN_DOC_014",
        "expected_decision": "refusal",
        "question": "Chữ ký mẫu của giám đốc Cục Sở hữu Trí tuệ có dạng đồ họa như thế nào?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_INSUFF_015",
        "category": "insufficient_evidence",
        "document_id": "VN_DOC_015",
        "expected_decision": "refusal",
        "question": "Tên hoa tiêu hàng hải đã điều khiển con tàu chở 24.000 TEU cập cảng Cái Mép là ai?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_INSUFF_016",
        "category": "insufficient_evidence",
        "document_id": "VN_DOC_016",
        "expected_decision": "refusal",
        "question": "Nhiệt độ rang mẫu cà phê Robusta chuẩn xác đến từng phần mười độ Celsius là bao nhiêu?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_INSUFF_017",
        "category": "insufficient_evidence",
        "document_id": "VN_DOC_017",
        "expected_decision": "refusal",
        "question": "Mã bưu chính của trung tâm dữ liệu dự phòng quốc gia VNeID đặt tại địa phương nào?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_INSUFF_018",
        "category": "insufficient_evidence",
        "document_id": "VN_DOC_018",
        "expected_decision": "refusal",
        "question": "Tên ngân hàng nước ngoài cụ thể đã từ chối giao dịch tài sản số trong vụ việc năm 2024?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_INSUFF_019",
        "category": "insufficient_evidence",
        "document_id": "VN_DOC_019",
        "expected_decision": "refusal",
        "question": "Đường kính chính xác của vi tảo dùng làm thức ăn cho ấu trùng tôm giống là bao nhiêu micromet?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_INSUFF_020",
        "category": "insufficient_evidence",
        "document_id": "VN_DOC_020",
        "expected_decision": "refusal",
        "question": "Tên loài hoa trang trí trồng trên dải phân cách tuyến phố Net-Zero thí điểm là gì?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_INSUFF_021",
        "category": "insufficient_evidence",
        "document_id": "VN_DOC_001",
        "expected_decision": "refusal",
        "question": "Dung lượng bộ nhớ RAM tính bằng Terabyte của máy chủ huấn luyện mô hình SA-CMS là bao nhiêu?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_INSUFF_022",
        "category": "insufficient_evidence",
        "document_id": "VN_DOC_002",
        "expected_decision": "refusal",
        "question": "Mã số thuế của công ty đầu tiên bị xử phạt 5% doanh thu theo Nghị định dữ liệu cá nhân?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_INSUFF_023",
        "category": "insufficient_evidence",
        "document_id": "VN_DOC_003",
        "expected_decision": "refusal",
        "question": "Trọng lượng chính xác tính bằng kilogam của chiếc chuông đá thời Khải Định là bao nhiêu?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_INSUFF_024",
        "category": "insufficient_evidence",
        "document_id": "VN_DOC_004",
        "expected_decision": "refusal",
        "question": "Tỷ lệ phần trăm diện tích đất bị phèn hóa dự báo vào mùa khô năm 2050 là con số nào?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    questions.append({
        "question_id": "VN_FINAL_INSUFF_025",
        "category": "insufficient_evidence",
        "document_id": "VN_DOC_005",
        "expected_decision": "refusal",
        "question": "Tên thương mại của nhà thầu cung cấp tuabin gió ngoài khơi trong dự án chuyển tiếp là gì?",
        "ground_truth_answer": "",
        "target_passages": [],
        "expected_keywords": [],
    })
    return questions
