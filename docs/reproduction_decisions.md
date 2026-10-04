# NHẬT KÝ QUYẾT ĐỊNH KỸ THUẬT (REPRODUCTION DECISIONS) — PHASE 1

> **Dự án:** Nghiên cứu khoa học — Baseline Hope-Attention & Continuum Memory System (CMS)  
> **Tài liệu nguồn:** arXiv:2512.24695v1 & Đề cương Chatbot hỏi đáp trên tài liệu với bộ nhớ đa thang.  
> **Ngày lập:** 02/10/2026.

---

## 1. BỐI CẢNH PHẦN CỨNG & RÀNG BUỘC TÀI NGUYÊN

- **Hệ điều hành:** Windows (Shell: PowerShell).
- **GPU vật lý:** NVIDIA GeForce GTX 1650 Ti (VRAM: ~4.29 GB).
- **Môi trường tính toán:** Python 3.9.13, PyTorch 2.2.1+cu118 (CUDA khả dụng).
- **Ràng buộc quyết định:**
  - Trong bài báo gốc (arXiv:2512.24695v1), các tác giả sử dụng backbone **Llama3-8B** và **Llama-3B** cùng quá trình continual pre-training 15 tỷ token trên cụm máy chủ lớn.
  - Trên một GPU 4GB VRAM, riêng việc nạp mô hình 3B hoặc 8B ở kiểu dữ liệu FP16 đã chiếm 6GB – 16GB VRAM (ngay lập tức gây lỗi CUDA Out Of Memory). Hơn nữa, phương trình cập nhật bộ nhớ online (Equation 71) đòi hỏi tính toán gradient lan truyền ngược (backward pass) trên chuỗi token, khiến mức tiêu thụ bộ nhớ tăng gấp đôi/gấp ba.
  - **Quyết định 1:** Không sử dụng Llama-8B/3B cho Phase 1. Thay vào đó, thiết kế một **Small / Micro Backbone Transformer** có đầy đủ cấu trúc toán học của Transformer Causal Decoder nhưng có số tham số tinh gọn (~4.5M tham số) để chạy trơn tru trên 4GB VRAM hoặc CPU mà không gây nghẽn phần cứng.

---

## 2. THIẾT KẾ BACKBONE NHỎ (MICRO-TRANSFORMER BACKBONE)

| Thông số | Giá trị lựa chọn cho Baseline | Lý do kỹ thuật |
|---|---|---|
| `d_model` (Hidden dimension) | 256 | Đủ lớn để biểu diễn đa chiều, nhẹ cho VRAM (< 100MB) |
| `n_heads` (Attention heads) | 4 | Mỗi head có $d_{\text{head}} = 64$ (chuẩn phổ biến) |
| `n_layers` (Số tầng Transformer) | 4 | Đủ số tầng để mô hình hóa trừu tượng phân cấp |
| `d_ff` (Feed-forward dimension) | 1024 ($4 \times d_{\text{model}}$) | Tuân thủ đúng tỷ lệ chuẩn của Transformer / Llama |
| `vocab_size` (Kích thước từ vựng) | 1000 | Phù hợp với bài toán Document QA / MK-NIAH vi mô |
| `max_seq_len` (Độ dài ngữ cảnh tối đa) | 1024 | Đủ để thử nghiệm các chu kỳ chunk 8, 16, 32, 64, 128 |
| Dung lượng trọng số (FP32) | ~18 MB | Cực kỳ an toàn cho GPU 4GB và dễ dàng lưu/nạp checkpoint |

---

## 3. THIẾT KẾ CONTINUUM MEMORY SYSTEM (CMS)

### 3.1. Dạng kiến trúc kết nối
- Paper đề cập 2 dạng:
  - Dạng chuỗi tuần tự (Sequential Chain, Equation 70):
    $$y_t = \mathrm{MLP}^{(f_k)}\left(\dots \mathrm{MLP}^{(f_1)}(x_t)\right)$$
  - Dạng song song gộp độc lập (Head-wise / Independent CMS, Equation 74):
    $$y_t = \mathrm{Agg}\left(\mathrm{MLP}^{(f_k)}(x_t), \dots, \mathrm{MLP}^{(f_1)}(x_t)\right)$$
- **Quyết định 2:** Cài đặt dạng chuỗi tuần tự (Equation 70) làm mặc định chính xác theo đúng mục 4 của Đề cương nghiên cứu. Đồng thời thiết kế module có cờ `cms_type: "sequential" | "independent"` để có thể chuyển đổi khi nghiên cứu mở rộng.

### 3.2. Khởi tạo trọng số (Ad-hoc Level Stacking - Section 7.3)
- Paper chỉ ra rằng các khối $\mathrm{MLP}^{(f_\ell)}$ được khởi tạo bằng trọng số của MLP pre-trained ban đầu:
  $$\mathrm{MLP}^{(f_\ell)}_0 = \mathrm{MLP}_{\text{pre-trained}}$$
- **Quyết định 3:** Khởi tạo mức 1 đến mức $k$ bằng bản sao của MLP gốc. Khi learning rate nội tại $\eta^{(\ell)} = 0$, mô hình hoạt động tương đương backbone gốc (ICL baseline).

### 3.3. Lịch cập nhật đa thang (Multi-timescale Schedule)
- Paper Figure 7 khảo sát 1, 2, 3, 4 mức bộ nhớ với dải "Lowest Freq = 512, 2K, 8K".
- Paper **không chỉ định (not specified in paper)** chunk size của các mức nhanh hơn ($\ell > 1$).
- **Quyết định 4:** Thiết kế lịch cập nhật theo tỷ lệ cấp số chia lũy thừa 2 từ mức chậm nhất:
  - Ví dụ với $k=4$ và Lowest Chunk $C^{(1)} = 64$:
    - Mức 1 (chậm nhất - persistent): $C^{(1)} = 64$ tokens
    - Mức 2: $C^{(2)} = 32$ tokens
    - Mức 3: $C^{(3)} = 16$ tokens
    - Mức 4 (nhanh nhất - adaptive): $C^{(4)} = 8$ tokens
  - Việc này mô phỏng chính xác tính chất: mức chậm lưu giữ tri thức lâu dài, mức nhanh thích ứng với biến đổi cục bộ.

### 3.4. Learning Rate cho CMS ($\eta^{(\ell)}$)
- Paper **không công bố giá trị số cụ thể** của $\eta^{(\ell)}$.
- **Quyết định 5:** Đặt giá trị mặc định trong config là $\eta = 1 \times 10^{-4}$ với optimizer SGD/AdamW nội bộ; cho phép cấu hình riêng `lr_cms` qua file cấu hình `configs/baseline_config.yaml`.

---

## 4. BỘ DỮ LIỆU ĐÁNH GIÁ (EVALUATION PROTOCOLS)

- Paper kiểm chứng trên:
  1. **MK-NIAH (Multi-Key Needle In A Haystack)** từ RULER: Đánh giá khả năng tìm kiếm nhiều cặp key-value rải rác trong văn bản dài.
  2. **QASPER:** Đánh giá hỏi đáp trên văn bản nghiên cứu dài qua perplexity và F1.
- **Quyết định 6:**
  - Tạo generator sinh dữ liệu tổng hợp **MK-NIAH Micro Benchmark**: chèn $N$ cặp key-value phân tán ngẫu nhiên trong chuỗi token nhiễu (haystack), yêu cầu mô hình truy xuất đúng giá trị khi hỏi key. Đo đạc độ chính xác Retrieval Accuracy (%).
  - Tạo generator sinh dữ liệu **Document QA Micro Benchmark**: mô phỏng tài liệu dài có chứa thông tin mục tiêu, đo Cross-Entropy Loss và Perplexity ($\text{PPL} = \exp(\text{loss})$) của mô hình khi đọc qua tài liệu với các mức bộ nhớ khác nhau (1 mức, 2 mức, 3 mức, 4 mức).

---

## 5. CƠ CHẾ RESET BỘ NHỚ (STATE MANAGEMENT)

- Trong ứng dụng Document QA và Continual Learning, bộ nhớ tham số CMS tích lũy thông tin của tài liệu đang đọc.
- **Quyết định 7:**
  - Cung cấp hàm `model.reset_memory()`: đưa toàn bộ trọng số CMS về trạng thái khởi tạo `theta_0` trước khi đọc tài liệu mới, tránh hiện tượng rò rỉ thông tin (information leakage) hoặc nhiễu chéo giữa các văn bản độc lập.
  - Hỗ trợ lưu trữ trạng thái bộ nhớ riêng biệt với checkpoint chính (`save_memory_state` / `load_memory_state`).
