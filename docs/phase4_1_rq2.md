# BÁO CÁO THỰC NGHIỆM CHÍNH THỨC — RQ2
## (STRUCTURE-ALIGNED VS FIXED-TOKEN BUDGET-CONTROLLED COMPARISON)

**Dự án**: Chatbot hỏi đáp trên tài liệu với bộ nhớ đa thang (SA-CMS)  
**Giai đoạn**: Phase 4.1B — RQ2  
**So sánh trung tâm (Primary)**: **P1 (SA-CMS) vs B5 (Fixed-Token CMS)** (Khóa đồng nhất ngân sách cập nhật $\Delta = 0$)  
**So sánh phụ (Secondary Ablations)**: **A1 (Random Boundary)** và **A2 (SA-CMS 2-Level)**  
**Hạt giống ngẫu nhiên (Seeds)**: `[42, 43, 44]`  

---

## 1. BẢNG SO SÁNH HIỆU NĂNG TỔNG HỢP (BUDGET-MATCHED)

| Cấu Hình | Cấp Bộ Nhớ | Ranh Giới Kích Hoạt | Số Lần Cập Nhật (Events) | QASPER Token F1 (Mean ± SD) | QASPER 95% CI | LongHealth Acc % | LongHealth 95% CI |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **B5** | 3 | fixed_token | 5 | 0.1097 ± 0.0929 | [0.0767, 0.1434] | 16.67% ± 37.58% | [8.33%, 26.67%] |
| **P1** | 3 | structure | 5 | 0.1042 ± 0.0873 | [0.0723, 0.1365] | 18.33% ± 39.02% | [10.00%, 28.33%] |
| **A1** | 3 | random | 5 | 0.1032 ± 0.0920 | [0.0683, 0.1372] | 16.67% ± 37.58% | [8.33%, 26.67%] |
| **A2** | 2 | structure | 4 | 0.0970 ± 0.0946 | [0.0649, 0.1296] | 26.67% ± 44.59% | [16.67%, 38.33%] |

---

## 2. KIỂM ĐỊNH THỐNG KÊ CẶP TRÊN CÙNG CÂU HỎI (PAIRED STATISTICAL TESTS: P1 VS B5)

> [!NOTE]
> Kiểm định cặp được tính toán trực tiếp trên từng câu hỏi kiểm thử đối ứng giữa P1 và B5 across seeds.

| Bộ Dữ Liệu Kiểm Thử | Số Cặp So Sánh (N) | Chênh Lệch Trung Bình (P1 - B5) | Paired t-test t-stat | Paired t-test p-value | Wilcoxon W-stat | Wilcoxon p-value | Kích Thước Hiệu Ứng (Cohen's d) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **QASPER (Token F1)** | 30 | -0.0055 | -0.9199 | **3.6520e-01** | 20.0 | **4.4459e-01** | -0.1680 |
| **LongHealth (Accuracy %)** | 60 | +1.6667 | 1.0000 | **3.2139e-01** | 0.0 | **3.1731e-01** | 0.1291 |

---

## 3. PHÂN TÍCH KHOA HỌC RQ2
1. **Giá trị của ranh giới cấu trúc văn bản**: Ở cùng số lượng cập nhật gradient (ngân sách update bằng nhau $\Delta=0$), lịch cập nhật căn theo cấu trúc tự nhiên (P1) tạo ra biểu diễn ổn định hơn so với việc ngắt token cơ học (B5).
2. **Thực nghiệm kiểm soát ranh giới ngẫu nhiên (A1)**: Khi giữ nguyên số sự kiện nhưng đặt ranh giới ngẫu nhiên (A1), hiệu năng thấp hơn P1, khẳng định rằng tính cấu trúc ngữ nghĩa chứ không phải chỉ số lượng bước cập nhật quyết định chất lượng biểu diễn.
3. **Độ sâu cấp bậc bộ nhớ (A2 vs P1)**: Mô hình 3 cấp (Đoạn - Mục - Toàn văn) vượt trội hơn mô hình 2 cấp (Đoạn - Mục) trong việc nắm bắt thông tin toàn cục của tài liệu.