# ĐÁNH GIÁ CÁC MÔ HÌNH NỀN TIỀN HUẤN LUYỆN (PRETRAINED BACKBONE OPTIONS)

> **Dự án:** Nghiên cứu khoa học — Tái hiện & Mở rộng Nested Learning (Hope-Attention / CMS)  
> **Tài liệu nguồn:** arXiv:2512.24695v1 (Section 7.1, 7.3, 8.3, 9.1 & Table 1)  
> **Mục tiêu:** Khảo sát các mô hình ngôn ngữ decoder-only tiền huấn luyện cỡ nhỏ ($\le 500\text{M}$ tham số) có khả năng chạy cục bộ trên GPU NVIDIA GeForce GTX 1650 Ti (4GB VRAM).

---

## 1. TIÊU CHÍ LỰA CHỌN MÔ HÌNH NỀN KHOA HỌC

Để đảm bảo tính trung thực khoa học và khả năng tái hiện:
1. **Kiến trúc tương đồng với Paper:** Bài báo gốc sử dụng kiến trúc **Llama** (Llama-3-8B). Ưu tiên các mô hình sử dụng các khối chuẩn hóa RMSNorm, nhúng vị trí RoPE, hàm kích hoạt SwiGLU, và cơ chế Grouped Query Attention (GQA).
2. **Khả thi về phần cứng 4GB VRAM:** Trọng số mô hình ở định dạng FP16 cộng với KV-cache, activations và gradients của CMS khi chạy online backward pass (Equation 71) không được vượt quá ngưỡng an toàn **3.5 GB VRAM**.
3. **Mô hình Base (Pretrained Base):** Ưu tiên base model đã học biểu diễn ngôn ngữ tự nhiên và mạch Induction Heads, không sử dụng model chuyên chat/instruction-tuned bị can thiệp bias an toàn hoặc ép khuôn prompt hội thoại.
4. **Giấy phép & Tính mở (Openness & Reproducibility):** Trọng số mở hoàn toàn, có tài liệu kỹ thuật rõ ràng, giấy phép mã nguồn mở (Apache 2.0 / MIT).

---

## 2. BẢNG SO SÁNH CHI TIẾT 5 ỨNG VIÊN MÔ HÌNH NỀN

| Tiêu chí | Ứng viên 1: **SmolLM2-135M** | Ứng viên 2: **Pythia-160M** | Ứng viên 3: **Qwen2.5-0.5B** | Ứng viên 4: **SmolLM2-360M** | Ứng viên 5: **GPT-2 Small (124M)** |
|---|:---:|:---:|:---:|:---:|:---:|
| **Số tham số** | **134.5M (0.13B)** | 162.3M (0.16B) | 490M (0.49B) | 362M (0.36B) | 124.4M (0.12B) |
| **Kiến trúc** | **Llama-based** (RoPE, RMSNorm, SwiGLU, GQA) | GPT-NeoX (RoPE, LayerNorm, GELU, MHA) | Llama-based (RoPE, RMSNorm, SwiGLU, GQA) | Llama-based (RoPE, RMSNorm, SwiGLU, GQA) | Cổ điển (Abs Pos, Pre-LN, GELU, MHA) |
| **Dung lượng trọng số FP16** | **~269 MB** | ~324 MB | ~980 MB | ~724 MB | ~248 MB |
| **Tập dữ liệu Pretrain** | 2.0 Trillion tokens (FineWeb-Edu, DCLM, Stack) | 300 Billion tokens (The Pile) | >18 Trillion tokens | 4.0 Trillion tokens | WebText (~40 GB) |
| **Context Length tối đa** | 2,048 (mở rộng 8,192) | 2,048 | 32,768 | 2,048 (mở rộng 8,192) | 1,024 |
| **Đỉnh VRAM ước tính (Inference + CMS Update)** | **~1.2 GB – 1.6 GB** (Dư > 2.0 GB an toàn) | ~1.4 GB – 1.8 GB | ~2.9 GB – 3.5 GB (Rất sát ngưỡng OOM) | ~2.0 GB – 2.6 GB | ~1.1 GB – 1.4 GB |
| **Khả năng huấn luyện Adapter / CMS trên GTX 1650 Ti** | **Rất cao (Rất mượt mà)** | Rất cao | Trung bình (Dễ OOM nếu context > 1k) | Khá | Rất cao |
| **Giấy phép bản quyền** | **Apache 2.0** | Apache 2.0 | Apache 2.0 | Apache 2.0 | MIT |
| **Độ tương đồng kiến trúc với Paper** | **Hoàn hảo (Isomorphic với Llama-3)** | Trung bình (Khác LayerNorm & MLP) | Hoàn hảo (Isomorphic với Llama-3) | Hoàn hảo (Isomorphic với Llama-3) | Thấp (Kiến trúc cũ 2019) |

---

## 3. PHÂN TÍCH ƯU - NHƯỢC ĐIỂM TỪNG MÔ HÌNH

### 1. SmolLM2-135M (Hugging Face) — *Độ ưu tiên cao nhất*
- **Ưu điểm:**
  - Kiến trúc giống hệt Llama-3 (RMSNorm, RoPE, SwiGLU, GQA) giúp việc tích hợp các khối CMS MLP Chain (Equation 70 & 74) hoàn toàn tương đồng về mặt toán học với thí nghiệm trong bài báo gốc.
  - Được huấn luyện trên 2.000 tỷ tokens dữ liệu chất lượng cao (FineWeb-Edu), hình thành đầy đủ các mạch Induction Heads giúp thực hiện truy xuất in-context (ICL).
  - Trọng số FP16 chỉ ~269 MB, chỉ chiếm ~1.3 GB VRAM khi tính backward pass cho CMS, đảm bảo 100% không bao giờ bị OOM trên GPU 4GB.
- **Nhược điểm:** Cần cài đặt thư viện quản lý mô hình hoặc module nạp trọng số tương thích.

### 2. Qwen2.5-0.5B (Alibaba Cloud) — *Ứng viên chất lượng cao nhưng rủi ro phần cứng*
- **Ưu điểm:** Khả năng ngôn ngữ và suy luận vượt trội ở phân khúc dưới 1 tỷ tham số.
- **Nhược điểm:** Trọng số FP16 chiếm ~1 GB. Khi thực hiện online gradient backward pass trên chuỗi ngữ cảnh dài (1024-2048 tokens), bộ nhớ tính toán activations và cache sẽ đẩy tổng VRAM lên 3.2 - 3.5 GB, chạm sát trần 4GB của GTX 1650 Ti trên Windows, tiềm ẩn nguy cơ văng OOM ngẫu nhiên.

### 3. Pythia-160M (EleutherAI) — *Ứng viên dự phòng (Fallback)*
- **Ưu điểm:** Mô hình nghiên cứu khoa học thuần túy, minh bạch hoàn toàn về từng checkpoint trong quá trình pretraining. Kích thước 160M rất vừa vặn với 4GB VRAM.
- **Nhược điểm:** Sử dụng LayerNorm tiêu chuẩn và GELU MLP cổ điển thay vì RMSNorm và SwiGLU của họ Llama trong bài báo *Nested Learning*.

### 4. SmolLM2-360M (Hugging Face)
- **Ưu điểm:** Năng lực ngôn ngữ mạnh hơn bản 135M, kiến trúc Llama chuẩn.
- **Nhược điểm:** Nặng gấp 2.7 lần bản 135M (~724 MB FP16), tốc độ chạy lặp thực nghiệm trên GTX 1650 Ti sẽ chậm hơn đáng kể.

### 5. GPT-2 Small (124M)
- **Ưu điểm:** Nhẹ, phổ biến.
- **Nhược điểm:** Kiến trúc năm 2019 không có RoPE, không có RMSNorm, context chỉ 1024 tokens. Không phù hợp với mục tiêu tái hiện công nghệ Attention hiện đại của paper (2024–2025).
