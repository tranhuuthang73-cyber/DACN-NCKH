# Hệ thống Bộ nhớ Đa thang SA-CMS và Kiến trúc Mô hình Ngôn ngữ Nhỏ SmolLM2-135M

## 1. Giới thiệu Kiến trúc Nested Learning và SmolLM2
Nghiên cứu Nested Learning đề xuất một phương thức biểu diễn tri thức liên tục bằng cách thay thế các lớp MLP tĩnh bằng Hệ thống Bộ nhớ Đa thang (Continuum Memory System - CMS). Trong phạm vi tái lập cấp học viên, mô hình backbone được lựa chọn là HuggingFaceTB/SmolLM2-135M với đúng 134.5 triệu tham số (134,514,432 tham số). Mô hình được giữ đóng băng (frozen) 100% trong toàn bộ quá trình cập nhật bộ nhớ online.

Tầng Hope-Attention kết nối backbone với bộ nhớ tham số thông qua chuẩn hóa LayerNorm (cms_norm). Tầng này cho phép các trạng thái ẩn (hidden states) của transformer kết hợp với phần dư bộ nhớ (mem_residual) theo Phương trình 70 và 74 của bài báo arXiv:2512.24695v1.

## 2. Cấu hình Phần cứng và Siêu tham số Huấn luyện
Toàn bộ quy trình thử nghiệm được tối ưu hóa nghiêm ngặt trên môi trường phần cứng giới hạn: Card đồ họa NVIDIA GeForce GTX 1650 Ti với dung lượng VRAM 4GB chạy trên hệ điều hành Windows 11 và Python 3.9.

Các siêu tham số của bộ nhớ CMS được thiết lập chính xác như sau:
Số mức thời gian (num_levels) là 2 mức bộ nhớ.
Kích thước khối tối thiểu (lowest_chunk_size) là 64 token.
Tốc độ học cơ sở (base_lr) của thuật toán tối ưu online được cố định ở mức 0.01.
Số lượng tham số bổ sung của CMS là 3.54 triệu tham số, chiếm chưa đến 2.6% tổng số tham số mô hình.

## 3. Thuật toán Căn chỉnh Ranh giới Cấu trúc SA-CMS
Phương pháp đề xuất Structure-Aligned CMS (SA-CMS) giải quyết hạn chế của việc cắt token cố định bằng cách căn chỉnh các sự kiện cập nhật gradient online (Phương trình 71) theo ranh giới tài liệu thực tế bao gồm tiêu đề mục, đoạn văn và ranh giới câu.

Bộ phân tích cú pháp tài liệu (Document Structure Parser) bóc tách văn bản thành cây cấu trúc phân cấp. Mỗi đoạn văn bản được gán mã định danh độc nhất dạng DOC{id}::P{idx} nhằm đảm bảo tính truy vết nguồn gốc 100%.

## 4. Kết quả Thực nghiệm Kiểm soát Ngân sách Phase 2.5
Trong thử nghiệm kiểm soát ngân sách nghiêm ngặt với 3 hạt giống ngẫu nhiên (seeds 42, 43, 44), ngân sách cập nhật được chuẩn hóa chính xác: Level 2 gồm 1540 updates và Level 3 gồm 1650 updates.

Kết quả kiểm toán thống kê chính thức tại file results/phase2_5_final_results.csv ghi nhận:
Xác suất mục tiêu MK-NIAH (Target Probability) của SA-CMS đạt 0.0296, vượt trội có ý nghĩa thống kê so với Fixed-Token (0.0210) với p-value nhỏ hơn 1e-17.
Điểm perplexity (PPL) hiệu chuẩn trên tập QASPER sau khi kiểm soát ngân sách là 98.19, phản ánh hiện tượng trôi dạt biểu diễn (representation drift) khi cập nhật online với hàm mất mát CLM.
Bộ dữ liệu QASPER dùng trong đánh giá học viên gồm đúng 10 tài liệu khoa học chuẩn.
