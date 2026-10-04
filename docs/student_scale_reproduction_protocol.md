# GIAO THỨC TÁI HIỆN QUY MÔ HỌC VIÊN (STUDENT-SCALE REPRODUCTION PROTOCOL)

> **Dự án:** Nghiên cứu khoa học — Tái hiện & Mở rộng Nested Learning (Hope-Attention / CMS)  
> **Tài liệu nguồn:** arXiv:2512.24695v1 & Đề cương NCKH  
> **Mục tiêu:** Định nghĩa quy trình thực nghiệm nghiêm ngặt, minh bạch hóa toàn bộ độ lệch (deviations) so với bài báo gốc do giới hạn tài nguyên tính toán (GTX 1650 Ti 4GB VRAM).

---

## 1. NGUYÊN TẮC KHOA HỌC CỐT LÕI

1. **Tái hiện Cơ chế và Xu hướng, không phải Tuyệt đối hóa Con số:**  
   Bài báo gốc sử dụng mô hình Llama-3-8B được huấn luyện liên tục trên 15 tỷ tokens với hàng trăm GPU H100. Đề tài của học viên hướng đến mục tiêu: **Kiểm chứng tính đúng đắn của cơ chế Continuum Memory System (CMS) và xu hướng cải thiện hiệu năng (hiệu quả nén ngữ cảnh, giảm perplexity, cải thiện khả năng truy xuất) khi tăng số mức bộ nhớ ($K = 1 \to 2 \to 3 \to 4$)**.
2. **Minh bạch tuyệt đối (Full Transparency):**  
   Mọi khác biệt giữa quy mô của bài báo và quy mô của phòng thí nghiệm sinh viên phải được lượng hóa và ghi nhận rõ ràng trong các báo cáo khoa học. Không ngụy tạo kết quả, không so sánh khập khiễng giữa mô hình ngẫu nhiên và mô hình pre-trained.

---

## 2. BẢNG ĐỐI CHIẾU THIẾT LẬP (PAPER VS. STUDENT-SCALE DEVIATIONS)

| Thành phần | Thiết lập Paper (*Nested Learning*) | Thiết lập Tái hiện Quy mô Học viên (Student-Scale) | Cơ sở lý luận & Tính bất biến toán học |
|---|---|---|---|
| **Backbone Architecture** | Llama-3 (RMSNorm, RoPE, SwiGLU, GQA) | **SmolLM2-135M** (RMSNorm, RoPE, SwiGLU, GQA) | **Bất biến cấu trúc:** Cùng kiến trúc toán học 100%, chỉ thu nhỏ số chiều ($d_{\text{model}} = 576$, $L = 30$). |
| **Quy mô tham số** | 8.03 tỷ tham số (~8B) | **134.5 triệu tham số (~135M)** | Tối ưu vừa vặn trong 270 MB FP16, an toàn tuyệt đối trên 4GB VRAM. |
| **Huấn luyện Backbone** | Huấn luyện trước trên 15T tokens + Continual pretrain 15B tokens | **Giữ nguyên trọng số pretrained có sẵn của SmolLM2**, **ĐÓNG BĂNG HOÀN TOÀN** (`requires_grad=False`). | Tận dụng Induction Heads đã học sẵn, không tốn tài nguyên pretraining khổng lồ. |
| **Kiến trúc CMS** | MLP Chain kết nối thặng dư (Eq 70 & 74): $\mathbf{h}_k = \mathbf{h}_{k-1} + \text{MLP}_k(\mathbf{h}_{k-1})$ | **Giữ nguyên 100% công thức toán Eq 70 & 74**, tích hợp vào hidden states của backbone. | **Bảo toàn nguyên vẹn thuật toán của paper.** |
| **Quy tắc cập nhật CMS** | Gradient descent online (Eq 71): $\theta_k^{(t+1)} = \theta_k^{(t)} - \eta_k \nabla_{\theta_k} \mathcal{L}(X_{\tau_k(t)})$ | **Giữ nguyên 100% công thức Eq 71**, tối ưu bằng SGD/AdamW trên chunk loss. | **Bảo toàn nguyên vẹn thuật toán của paper.** |
| **Lịch trình bộ nhớ (Memory Schedule)** | Phân cấp theo lũy thừa 2 dựa trên độ dài token cố định | **Giữ nguyên 100% lịch trình dựa trên token:** Level 1: [64], Level 2: [64, 32], Level 3: [64, 32, 16]. | **KHÔNG đưa SA-CMS vào Phase này.** |
| **Phần cứng thực nghiệm** | Cụm máy chủ NVIDIA H100 | 01 máy tính cá nhân: GPU NVIDIA GTX 1650 Ti (4GB VRAM), RAM 24GB. | Phù hợp với năng lực phòng thí nghiệm sinh viên. |

---

## 3. PHÂN ĐỊNH HAI LUỒNG THỰC NGHIỆM ĐỘC LẬP (TWO EXPERIMENTAL TRACKS)

Để tránh bất kỳ sự nhầm lẫn nào trong phân tích dữ liệu, hệ thống chia tách thành hai luồng độc lập:

### **TRACK 1: MICRO SCRATCH MODEL (4.5M) — XÁC MINH CƠ CHẾ KỸ THUẬT (MECHANISM VALIDATION ONLY)**
- **Mục đích:** Kiểm chứng tính khả thi và độ ổn định của mã nguồn toán học (Eq 70, 71, 74), độ hồi tiếp gradient, khả năng lưu trữ thông tin cục bộ và khả năng reset bộ nhớ sạch sẽ.
- **Tập kiểm thử:** Bài toán tổng hợp sao chép/truy xuất ngắn (Synthetic Copy/Retrieval Task — `tests/synthetic_memory_test.py`).
- **Gắn nhãn bắt buộc:** Mọi biểu đồ, nhật ký, bảng số liệu của Track 1 phải ghi rõ:  
  *`"Mechanism validation only — NOT a paper reproduction result"`*.

### **TRACK 2: PRETRAINED SMALL BACKBONE (SmolLM2-135M) — TÁI HIỆN XU HƯỚNG KHOA HỌC (REPRODUCTION BASELINE)**
- **Mục đích:** Tái hiện kết quả so sánh giữa Baseline ICL (Level 1) và các cấu hình Continuum Memory đa thang (Level 2, 3, 4) trên các tác vụ ngữ cảnh dài thực tế.
- **Tiêu chí đánh giá chính:**
  1. **Document QA (QASPER subset):** Đo lường xu hướng giảm của Perplexity / Cross-Entropy Loss khi tăng số mức bộ nhớ ($K = 1 \to 2 \to 3$).
  2. **MK-NIAH / RULER (Multi-Key Needle In A Haystack):** Đo lường khả năng truy xuất chính xác của mô hình khi ngữ cảnh được nạp vào bộ nhớ CMS so với ICL thông thường.
- **Gắn nhãn bắt buộc:**  
  *`"Student-scale reproduction baseline on SmolLM2-135M"`*.

---

## 4. QUY TRÌNH THỰC THI VÀ GIAO DIỆN KIỂM SOÁT (DECISION & REPRODUCTION GATES)

1. **Bước 1 (Xác minh cơ chế Track 1):** Chạy `tests/synthetic_memory_test.py` xác nhận:
   - Gradient delta $\|\theta_{\text{after}} - \theta_{\text{before}}\| > 0$.
   - Xác suất token đích tăng và thứ hạng target rank cải thiện rõ rệt sau khi nạp.
   - `reset_memory()` đưa toàn bộ trạng thái về nguyên bản.
2. **Bước 2 (Kiểm toán môi trường nạp Track 2):**
   - Kiểm tra khả năng nạp `SmolLM2-135M` và tokenizer tương thích vào bộ nhớ GPU.
   - Đo đạc VRAM thực tế ở chế độ FP16.
3. **Bước 3 (Kiểm tra mẫu thủ công MK-NIAH):**
   - Chạy 01 mẫu thủ công với đầy đủ context, needle, expected answer, logits distribution, và xác nhận evaluator hoạt động chính xác trước khi mở rộng.
4. **Bước 4 (Chạy benchmark vi mô):**
   - Chạy các cấu hình Level 1 (ICL), Level 2 (CMS), Level 3 (CMS) trên tập con đại diện của MK-NIAH và Document QA.
   - Ghi nhận đầy đủ thông số: runtime, VRAM, loss, accuracy.
5. **Điều kiện Dừng / Hủy bỏ (Abort Conditions):**
   - Dừng ngay lập tức nếu VRAM vượt quá 3.5 GB gây OOM.
   - Dừng ngay nếu phát hiện giả định ngầm không có căn cứ từ paper gốc.
