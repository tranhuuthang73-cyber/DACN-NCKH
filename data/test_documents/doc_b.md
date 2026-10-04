# Hệ thống Truy xuất Thông tin BM25, Quản lý Trích dẫn và Cổng Từ chối RefusalController

## 1. Cơ chế Truy xuất BM25 Thuần Python
Hệ thống con truy xuất sử dụng giải thuật BM25 Okapi được viết bằng Python thuần túy nhằm loại bỏ hoàn toàn các phụ thuộc thư viện bên ngoài và đảm bảo tính tái lập 100%.

Các tham số hiệu chỉnh của thuật toán BM25 được cố định theo chuẩn kinh điển:
Tham số k1 điều chỉnh độ bão hòa tần số từ (term frequency saturation) được đặt bằng 1.5.
Tham số b điều chỉnh độ dài văn bản (length normalization) được đặt bằng 0.75.
Chỉ mục BM25 lưu trữ toàn bộ các đoạn văn bản (passages) và cập nhật tăng dần khi có tài liệu mới nạp vào hệ thống.

## 2. Quản lý Kho Tài liệu và Phân đoạn Văn bản
Kho lưu trữ DocumentStore lưu trữ dữ liệu dưới định dạng JSON trên hệ thống tệp cục bộ. Mỗi tài liệu khi được thêm vào sẽ được cấp một mã document_id tuần tự (như DOC001, DOC002).

Tính toàn vẹn của nội dung được kiểm soát bằng mã băm SHA-256 rút gọn 16 ký tự hexa (content_hash). Hệ thống áp dụng chuỗi phiên bản bất biến (v1, v2, v3), trong đó mỗi bản cập nhật tạo ra một snapshot mới mà không ghi đè làm mất lịch sử phiên bản trước.
Bộ cắt đoạn DocumentChunker phân tách văn bản theo ranh giới câu (sentence-aware) với kích thước khối mặc định 256 ký tự và độ gối đầu 32 ký tự.

## 3. Hệ thống Trích dẫn và Cổng Từ chối RefusalController
Bộ kiểm tra trích dẫn CitationChecker đảm bảo mỗi khẳng định trong câu trả lời phải liên kết ngược về đoạn văn gốc thông qua chuỗi truy vết cấu trúc: answer -> citation_id -> passage_id -> paragraph_id -> section_id -> document_id -> document_version.

Cổng từ chối RefusalController ngăn chặn triệt để hiện tượng ảo giác (hallucination) dựa trên 3 mã lý do cụ thể:
Lý do thứ nhất: NO_EVIDENCE (no_relevant_evidence_found) khi bộ truy xuất không tìm thấy bất kỳ đoạn văn nào liên quan.
Lý do thứ hai: LOW_CONFIDENCE (evidence_below_confidence_threshold) khi điểm liên quan BM25 cao nhất nhỏ hơn ngưỡng tối thiểu 1.0.
Lý do thứ ba: INSUFFICIENT_COVERAGE (insufficient_evidence_coverage) khi số lượng đoạn bằng chứng tìm thấy ít hơn số lượng tối thiểu quy định (mặc định 1 đoạn).
