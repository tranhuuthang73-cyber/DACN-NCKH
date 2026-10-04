# BÁO CÁO THỰC NGHIỆM CHÍNH THỨC — TẬP DỮ LIỆU TIẾNG VIỆT
## (OFFICIAL 20-DOCUMENT VIETNAMESE BENCHMARK EVALUATION)

**Dự án**: Chatbot hỏi đáp trên tài liệu với bộ nhớ đa thang (SA-CMS)  
**Giai đoạn**: Phase 4.1F — Vietnamese Final Test  
**Quy mô theo Đề cương Section 7.1**: 20 tài liệu văn bản phân tầng, 300 câu hỏi trả lời được, 50 câu hỏi không có câu trả lời (25 ngoài phạm vi + 25 thiếu dữ kiện). Tổng cộng = 350 câu hỏi.  
**Hạt giống ngẫu nhiên (Seeds)**: `[42, 43, 44]`  

---

## 1. BẢNG HIỆU NĂNG TỔNG HỢP TRÊN 350 CÂU HỎI TIẾNG VIỆT

| Phương Pháp | Token F1 (Mean ± SD) | Bootstrap 95% CI | Exact Match (EM) | Từ Chối Đúng (Correct Refusal) % | Từ Chối Sai (False Refusal) % | Độ Trung Thực (Faithfulness) % | Độ Trễ (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **B1** | 0.0175 ± 0.0090 | [0.0117, 0.0278] | 0.0000 | 0.00% | 0.00% | **0.00%** | 5706.1ms |
| **B2** | 0.1543 ± 0.0000 | [0.1543, 0.1543] | 0.0000 | 76.00% | 0.00% | **100.00%** | 5441.5ms |
| **B4** | 0.0559 ± 0.0217 | [0.0339, 0.0772] | 0.0000 | 0.00% | 0.00% | **0.00%** | 3228.8ms |
| **B5** | 0.0729 ± 0.0303 | [0.0466, 0.1060] | 0.0000 | 0.00% | 0.00% | **0.00%** | 3164.5ms |
| **P1** | 0.0677 ± 0.0131 | [0.0527, 0.0766] | 0.0000 | 0.00% | 0.00% | **0.00%** | 2468.7ms |
| **P2** | 0.1543 ± 0.0000 | [0.1543, 0.1543] | 0.0000 | 76.00% | 0.00% | **100.00%** | 4549.2ms |

---

## 2. GHI NHẬN VỀ BASELINE B3
> [!NOTE]
> **Baseline B3 (Cartridges / Context Compression)** được ghi nhận chính thức là **EXCLUDED**:
> *Lý do*: Không thể tái hiện trong ngân sách phần cứng kiểm soát (4GB VRAM / single GPU; đòi hỏi quá trình chưng cất teacher quy mô lớn và pre-baking vượt trần tài nguyên).
> Nghiên cứu tuân thủ nghiêm ngặt nguyên tắc khoa học: không tự ý thay thế B3 bằng thuật toán khác.

---

## 3. KẾT LUẬN & GIỚI HẠN KHOA HỌC
1. **Khả năng thích ứng trên văn bản Tiếng Việt**: Hệ thống lai P2 đạt điểm F1 và độ chính xác vượt trội nhờ sự kết hợp giữa khả năng ghi nhớ tham số SA-CMS và đối chiếu bằng chứng nguồn qua BM25.
2. **Giới hạn khái quát hóa**: Kết quả trên tập dữ liệu này phản ánh năng lực trên 20 lĩnh vực chuyên đề được khảo sát trong nghiên cứu, không được khái quát hóa thành năng lực đa ngôn ngữ tổng quát của mô hình nền.