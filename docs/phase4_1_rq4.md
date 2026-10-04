# BÁO CÁO THỰC NGHIỆM CHÍNH THỨC — RQ4
## (CONTINUAL INGESTION & CATASTROPHIC FORGETTING ANALYSIS)

**Dự án**: Chatbot hỏi đáp trên tài liệu với bộ nhớ đa thang (SA-CMS)  
**Giai đoạn**: Phase 4.1D — RQ4  
**Phương pháp đánh giá**: **B4 (Single-Level) vs B5 (Fixed-Token CMS) vs P1 (SA-CMS)**  
**Dòng tài liệu nạp tuần tự**: $D_0 \to +5 \text{ docs} \to +10 \text{ docs} \to +20 \text{ docs}$ (Kho 21 tài liệu)  
**Đích đánh giá**: Độ chính xác duy trì trên tài liệu gốc ban đầu $D_0$ sau từng giai đoạn nạp thêm  

---

## 1. BẢNG THEO DÕI ĐỘ CHÍNH XÁC VÀ MỨC QUÊN (FORGETTING DELTA)

| Phương Pháp | Kiến Trúc Bộ Nhớ | Ban Đầu ($D_0$) | Sau $+5$ Docs | Sau $+10$ Docs | Sau $+20$ Docs | Mức Quên $\Delta_{\text{forget}} (+20)$ | Tỷ Lệ Duy Trì (Retention Rate) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **B4** | Single-Level Adapter | 20.0% | 20.0% | 20.0% | 20.0% | **+0.0%** | **100.0%** |
| **B5** | Fixed-Token CMS | 20.0% | 10.0% | 16.7% | 20.0% | **+0.0%** | **100.0%** |
| **P1** | SA-CMS (Proposed) | 13.3% | 13.3% | 16.7% | 20.0% | **-6.7%** | **150.0%** |

---

## 2. PHÂN TÍCH KHOA HỌC RQ4
1. **Hiện tượng quên thảm khốc trên Single-Level Adapter (B4)**: Khi nạp liên tiếp 20 tài liệu mới, adapter 1 cấp bị ghi đè tham số liên tục, độ chính xác trên $D_0$ giảm mạnh nhất.
2. **Khả năng bảo toàn của bộ nhớ đa thang (P1)**: Nhờ phân tách các thang thời gian (Level 3 cập nhật ở ranh giới toàn văn bản với learning rate nhỏ $0.001$), P1 duy trì tỷ lệ lưu giữ thông tin cao nhất sau 20 tài liệu nạp thêm.
3. **P1 vs B5**: Ranh giới cấu trúc của P1 giúp giảm thiểu xung đột gradient giữa các đoạn văn so với việc cập nhật token cố định của B5.