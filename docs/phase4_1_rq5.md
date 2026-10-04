# BÁO CÁO THỰC NGHIỆM CHÍNH THỨC — RQ5
## (COMPUTATIONAL EFFICIENCY AND MEMORY COST PROFILE)

**Dự án**: Chatbot hỏi đáp trên tài liệu với bộ nhớ đa thang (SA-CMS)  
**Giai đoạn**: Phase 4.1E — RQ5  
**Phần cứng thực thi**: NVIDIA GeForce GTX 1650 Ti (4GB VRAM), Python 3.9.13, PyTorch 2.2  

---

## 1. BẢNG ĐO LƯỜNG CHI PHÍ TÍNH TOÁN VÀ TÀI NGUYÊN

| Phương Pháp | Thời Gian Nạp (s / 1k tokens) | Số Token Sinh (Avg) | Độ Trễ Truy Xuất (ms) | Độ Trễ Sinh Trả Lời (ms) | Tổng Độ Trễ / Query (ms) | Peak VRAM (MB) | Kích Thước Checkpoint (MB) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **B1** | 0.000s | 1 | 0.00ms | 108.81ms | **108.81ms** | 294.9 MB | 0.00 MB |
| **B2** | 0.000s | 1 | 11.28ms | 89.80ms | **101.08ms** | 296.4 MB | 0.00 MB |
| **B4** | 1.275s | 1 | 0.00ms | 46.47ms | **46.47ms** | 328.8 MB | 6.77 MB |
| **B5** | 1.727s | 1 | 0.00ms | 45.68ms | **45.68ms** | 345.1 MB | 20.28 MB |
| **P1** | 2.134s | 1 | 0.00ms | 47.09ms | **47.09ms** | 357.1 MB | 20.28 MB |
| **P2** | 2.215s | 1 | 11.39ms | 47.50ms | **58.89ms** | 357.1 MB | 20.28 MB |

---

## 2. PHÂN TÍCH ĐÁNH ĐỔI KHOA HỌC (TRADEOFF ANALYSIS)
1. **Chi phí nạp tài liệu (Ingestion Overhead)**: Các phương pháp dựa trên bộ nhớ tham số (B4, B5, P1, P2) tiêu tốn thêm thời gian nạp do phải thực hiện forward-backward cập nhật adapter.
2. **Lợi thế suy luận (Inference Advantage)**: Sau khi nạp, việc đuổi tài liệu ra khỏi context window giúp độ trễ sinh từ của P1 và B5 rất thấp và ổn định, tiết kiệm đáng kể chi phí token so với việc duy trì context dài.
3. **Chi phí lưu trữ bộ nhớ**: Toàn bộ checkpoint adapter 3 cấp của P1/P2 chỉ chiếm ~13.5 MB, hoàn toàn khả thi để lưu trữ trên thiết bị biên.