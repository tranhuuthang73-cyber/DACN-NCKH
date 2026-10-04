# PHẠM VI TÁI LẬP THỰC NGHIỆM (REPRODUCTION SCOPE) — PHASE 1

> **Dự án:** Nghiên cứu khoa học — Baseline Hope-Attention & Continuum Memory System (CMS)  
> **Tài liệu nguồn:** arXiv:2512.24695v1 & Đề cương Chatbot hỏi đáp trên tài liệu với bộ nhớ đa thang.  
> **Giai đoạn:** Phase 1 (Nền tảng: Xây dựng baseline có thể chạy và kiểm chứng được).

---

## 1. MỤC TIÊU DUY NHẤT CỦA PHASE 1
Dựng lại kiến trúc mô hình từ bài báo **ở quy mô nhỏ (small scale)** để có một hệ thống **baseline hoàn chỉnh, độc lập và chạy được thực tế** trên máy tính hiện có, làm nền tảng vững chắc trước khi bước vào các cải tiến ở các giai đoạn sau.

---

## 2. RANH GIỚI VÀ PHẠM VI (SCOPE BOUNDARIES)

### 2.1. Những thành phần NẰM TRONG phạm vi Phase 1 (In-Scope)
1. **Kiến trúc mô hình cốt lõi:**
   - Causal Multi-Head Self-Attention chuẩn (Transformer decoder-only).
   - Khối **Continuum Memory System (CMS)** thay thế MLP truyền thống:
     - Dạng chuỗi tuần tự $y_t = \mathrm{MLP}^{(f_k)}(\dots \mathrm{MLP}^{(f_1)}(x_t))$ (Equation 70).
     - Hỗ trợ cả dạng gộp độc lập $y_t = \mathrm{Agg}(\dots)$ (Equation 74).
     - Cơ chế khởi tạo Ad-hoc từ MLP nền (Section 7.3).
   - Tầng **Hope-Attention** tích hợp Attention + CMS + Residual + LayerNorm (Section 8.3).
   - Mô hình ngôn ngữ hoàn chỉnh `HopeAttentionLM`.
2. **Cơ chế cập nhật bộ nhớ online (Continuum Update Mechanism):**
   - Bộ đệm tích lũy gradient qua $C^{(\ell)}$ token (Equation 71).
   - Lịch cập nhật đa thang thời gian (Multi-timescale schedule): mức chậm $C^{(1)}$ (Lowest Freq) cập nhật thưa hơn, mức nhanh $C^{(k)}$ cập nhật dày hơn.
   - Cơ chế nạp tài liệu vào bộ nhớ tham số (Document Context Ingestion) qua tối ưu hóa gradient bước nhỏ.
   - Cơ chế cô lập/reset trạng thái bộ nhớ giữa các tài liệu khác nhau.
3. **Phần cứng và quy mô thực thi:**
   - Tương thích trực tiếp với GPU NVIDIA GeForce GTX 1650 Ti (4GB VRAM) và CPU.
   - Backbone nhỏ (Micro-scale Transformer, ~5M tham số), đảm bảo forward/backward pass mượt mà không tràn VRAM.
4. **Bộ kiểm thử & Đánh giá (Evaluation & Benchmarks):**
   - **Unit Tests:** Kiểm thử độc lập cho từng module nhỏ (Attention, MemoryBuffer, CMS, HopeBlock, Checkpoint, Loss).
   - **Smoke Test:** Xác minh end-to-end (Init $\to$ Forward $\to$ Memory Update $\to$ Save/Load $\to$ Inference).
   - **Thực nghiệm vi mô (Micro-scale Experiments):**
     - **MK-NIAH Micro:** Bài toán tìm nhiều khóa trong văn bản dài (mô phỏng RULER MK-NIAH trong Figure 7 Left).
     - **Document QA / Perplexity Micro:** Đo perplexity và loss dự đoán câu trả lời khi nạp tài liệu dài (mô phỏng QASPER trong Figure 7 Right).
     - So sánh giữa: Baseline 1 mức (ICL / Static MLP) vs. Hope-Attention 2 mức, 3 mức, 4 mức.
5. **Quản lý artifacts và tính minh bạch:**
   - Lưu trữ toàn bộ file cấu hình (`configs/*.yaml`).
   - Lưu trữ log chạy thực tế (`logs/*.log` và `logs/*.json`).
   - Lưu trữ checkpoint mô hình và bộ nhớ (`checkpoints/*.pt`).
   - Xuất bảng chỉ số thực tế (`results/`).

---

### 2.2. Những việc TUYỆT ĐỐI KHÔNG LÀM ở Phase 1 (Out-of-Scope)
Theo đúng chỉ đạo nghiêm ngặt của đề cương và yêu cầu nghiên cứu:
- ❌ **Không làm Web, không làm Mobile, không làm Chatbot UI.**
- ❌ **Không làm SA-CMS (Structure-Aligned CMS)** — Đây là nội dung của Phase 2 (Giai đoạn đề xuất cải tiến căn theo cấu trúc đoạn/mục).
- ❌ **Không tự ý cải tiến thuật toán, không tự thêm kiến trúc lai mới.**
- ❌ **Không lấy repo bên ngoài làm implementation chính** — Tự cài đặt mã nguồn chuẩn tắc dựa trên công thức toán học của bài báo.
- ❌ **Không tự tuyên bố kết quả tốt hơn paper.**
- ❌ **Không dùng số liệu của bài báo làm kết quả của dự án** — Mọi con số báo cáo phải đến từ lần chạy mã nguồn thực tế trên máy.
- ❌ **Không chạy pre-training 15 tỷ token hay huấn luyện mô hình 8B** — Giới hạn quy mô phù hợp tài nguyên thực tế.
- ❌ **Không tự mở rộng phạm vi sang các bài toán ngoài văn bản (M3 optimizer, ViT, audio, RL).**

---

## 3. TIÊU CHÍ HOÀN THÀNH PHASE 1 (ACCEPTANCE GATES)

| Cổng kiểm tra | Tiêu chí nghiệm thu | Trạng thái dự kiến |
|---|---|---|
| **Gate 1: Documentation** | `paper_mapping.md`, `reproduction_scope.md`, `reproduction_decisions.md` đầy đủ, chính xác | Sẵn sàng |
| **Gate 2: Skeleton & Tests** | Cấu trúc module sạch sẽ, 100% Unit Tests pass | Sẵn sàng |
| **Gate 3: Smoke Test** | Init, Forward, Memory Update, Save/Load, Generation đều chạy thông suốt | Bắt buộc PASS |
| **Gate 4: Experiment** | Chạy kiểm chứng xu hướng đa mức bộ nhớ trên dữ liệu vi mô (MK-NIAH & QA Perplexity), lưu đủ log/config/metrics | Bắt buộc hoàn thành |
| **Gate 5: Phase 1 Report** | `PHASE1_REPORT.md` trung thực, minh bạch sai khác, sẵn sàng bàn giao | Hoàn thiện |
