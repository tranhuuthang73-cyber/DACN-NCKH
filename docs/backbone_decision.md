# QUYẾT ĐỊNH LỰA CHỌN MÔ HÌNH NỀN CHO TÁI HIỆN QUY MÔ HỌC VIÊN (BACKBONE DECISION)

> **Dự án:** Nghiên cứu khoa học — Tái hiện & Mở rộng Nested Learning (Hope-Attention / CMS)  
> **Tài liệu nguồn:** arXiv:2512.24695v1 (Section 7.1, 7.3, 8.3, 9.1 & Table 1)  
> **Mục tiêu:** Chọn chính xác 01 mô hình nền chính và 01 mô hình nền dự phòng tối ưu cho GPU 4GB VRAM.

---

## 1. QUYẾT ĐỊNH CUỐI CÙNG (FINAL DECISION)

### **MÔ HÌNH CHÍNH ĐƯỢC CHỌN (PRIMARY MODEL):**
### 👉 **`HuggingFaceTB/SmolLM2-135M` (Pretrained Base)**

- **Đơn vị phát triển:** Hugging Face TB (Loubna Ben Allal et al., 2024).
- **Quy mô:** **134.5 triệu tham số (~0.13B)**.
- **Kiến trúc:** **Llama Architecture Chuẩn** (RoPE, RMSNorm, SwiGLU, Grouped Query Attention - GQA).
- **Tập dữ liệu tiền huấn luyện:** 2.000 tỷ tokens (2T tokens) từ FineWeb-Edu, DCLM, The Stack.
- **Dung lượng trọng số FP16:** **~269 MB** (Cực kỳ nhẹ).
- **Giấy phép:** **Apache 2.0** (Mở hoàn toàn, phi thương mại & thương mại).

---

### **MÔ HÌNH DỰ PHÒNG (FALLBACK MODEL):**
### 👉 **`EleutherAI/pythia-160M` (Pretrained Base)**

- **Đơn vị phát triển:** EleutherAI (Stella Biderman et al., 2023).
- **Quy mô:** **162.3 triệu tham số (~0.16B)**.
- **Kiến trúc:** GPT-NeoX.
- **Giấy phép:** Apache 2.0.
- **Vai trò:** Dự phòng trong trường hợp xuất hiện xung đột phụ thuộc môi trường không lường trước với kiến trúc RoPE/GQA.

---

## 2. NĂM LUẬN ĐIỂM KHOA HỌC CHO SỰ LỰA CHỌN `SmolLM2-135M`

| Tiêu chuẩn khoa học | Lý giải chi tiết với SmolLM2-135M |
|---|---|
| **1. Tính tương thích cấu trúc (Structural Isomorphism)** | Paper gốc arXiv:2512.24695v1 sử dụng họ **Llama-3**. `SmolLM2-135M` sử dụng chính xác các thành phần của Llama-3: **RMSNorm, SwiGLU, RoPE, GQA**. Nhờ đó, việc chèn các tầng CMS MLP Chain (Equation 70 & 74) có cùng cấu trúc không gian biểu diễn toán học như trong paper. |
| **2. Đảm bảo an toàn phần cứng 100% (Zero OOM Risk)** | Với kích thước 269 MB, khi tải lên VRAM ở FP16: <br>- Model weights: 270 MB<br>- CMS params: ~40 MB<br>- KV-cache + Activations (2048 tokens): ~350 MB<br>- Online backward gradients (Equation 71): ~250 MB<br>**Tổng VRAM đỉnh: ~1.2 GB - 1.5 GB**, cách xa giới hạn 3.5 GB của GTX 1650 Ti. |
| **3. Giải quyết triệt để Train/Eval Mismatch** | `SmolLM2-135M` đã được huấn luyện trên 2 nghìn tỷ tokens, đã hình thành các mạch **Induction Heads** tự nhiên trong attention heads. Nhờ đó, baseline ICL (In-Context Learning) có khả năng copy/retrieval thực chất, làm điểm tựa chuẩn mực để so sánh sự đóng góp của bộ nhớ CMS. |
| **4. Tiết kiệm lưu trữ đĩa cứng** | Toàn bộ model weights và tokenizer chỉ chiếm ~300 MB ổ cứng, hoàn toàn nằm trong giới hạn an toàn 9.3 GB trống của ổ D:. |
| **5. Chu kỳ lặp thực nghiệm nhanh** | Với 135M tham số, mỗi bước forward-backward trực tuyến chỉ tốn vài mili-giây, cho phép chạy trọn vẹn benchmark MK-NIAH và QASPER trên máy local mà không cần đến cụm server đắt đỏ. |

---

## 3. NGUYÊN TẮC THỰC THI (OPERATIONAL DIRECTIVE)

1. **Chỉ dùng Base Model:** Tuyệt đối không dùng bản `SmolLM2-135M-Instruct` để tránh bias căn chỉnh hội thoại.
2. **Đóng băng trọng số nền (Freeze Backbone):** Toàn bộ 135M tham số của SmolLM2 được đóng băng (`requires_grad = False`). Chỉ các tham số của các tầng Continuum Memory (CMS MLP Chains) mới nhận gradient từ Equation 71.
3. **Phân tách hoàn toàn hai luồng:**
   - **Track 1:** Random Micro Model (4.5M) $\to$ Phục vụ kiểm tra cơ chế cô lập (Mechanism sanity check).
   - **Track 2:** Pretrained SmolLM2-135M $\to$ Tái hiện đường xu hướng khoa học của Paper (Reproduction Baseline).
