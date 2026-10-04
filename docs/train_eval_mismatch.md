# PHÂN TÍCH CHUYÊN SÂU NGUYÊN NHÂN LỆCH PHA HUẤN LUYỆN / ĐÁNH GIÁ (TRAIN/EVAL MISMATCH ANALYSIS)

> **Dự án:** Nghiên cứu khoa học — Tái hiện & Mở rộng Nested Learning (Hope-Attention / CMS)  
> **Tài liệu nguồn:** arXiv:2512.24695v1 (Section 7.1, 7.3, 8.3, 9.1 & Table 1)  
> **Mục tiêu:** Phân tích toán học và cơ chế mạng sâu giải thích tại sao mô hình micro ngẫu nhiên đạt 0.00% MK-NIAH và cách khắc phục có cơ sở khoa học.

---

## 1. SO SÁNH THIẾT LẬP THỰC NGHIỆM GIỮA PAPER VÀ PHASE 1 MICRO-SCALE

| Thành phần | Thiết lập của Paper (*Nested Learning*, Section 9.1) | Thiết lập Phase 1 Micro Baseline | Hệ quả khoa học |
|---|---|---|---|
| **Mô hình nền (Backbone)** | **Llama-3-8B** (8.03 tỷ tham số) | Micro Transformer (4.53 triệu tham số) | Mô hình micro nhỏ hơn ~1,770 lần |
| **Dữ liệu tiền huấn luyện (Pretraining Data)** | **15.000 tỷ tokens (15T tokens)** + 15B tokens continual pretraining | **0 tokens (Khởi tạo ngẫu nhiên $\mathcal{N}(0, 0.02)$)** | Không có biểu diễn ngôn ngữ hay quan hệ từ vựng |
| **Mạch ghi nhớ trong ngữ cảnh (Induction Heads)** | **Đã phát triển hoàn chỉnh** qua 15T tokens pretraining | **Hoàn toàn không tồn tại** | Attention weights là nhiễu đồng đều $\approx 1/T$ |
| **Độ chính xác ICL trên MK-NIAH** | **88.5%** (Figure 7 Left & Table 1) | **0.00%** | ICL của Paper hoạt động nhờ attention sao chép được token |
| **Cơ chế nạp bộ nhớ CMS (Equation 71)** | Cập nhật gradient trực tuyến trên các chunk tài liệu | Đã thực hiện toán học, nhưng bị tắt trong evaluator ban đầu | CMS cần nạp online trước khi query |

---

## 2. GIẢ THUYẾT MẠCH QUAN HỆ (INDUCTION HEAD HYPOTHESIS)

Theo công trình kinh điển của *Elhage et al. (Anthropic, 2021) — "A Mathematical Framework for Transformer Circuits"*:
- Khả năng **In-Context Learning (ICL)** và truy xuất thông tin trong ngữ cảnh dài (như kim trong bọc - Needle In A Haystack) của Transformer không phải là thuộc tính ngẫu nhiên của kiến trúc, mà là một **pha chuyển tiếp (phase change)** xảy ra trong quá trình pretraining.
- Trong pha chuyển tiếp này, mạng hình thành cặp **Induction Heads**:
  1. Head ở tầng $l$ hướng chú ý về token đứng trước ($[A] \to [B]$).
  2. Head ở tầng $l+1$ hướng chú ý về token xuất hiện ngay sau phiên bản trước đó của $[A]$ trong ngữ cảnh, thực hiện phép toán sao chép:
     $$\text{Attn}(Q_{[A]}, K_{[A]}) \cdot V_{[B]} \implies \text{Dự đoán tiếp theo là } [B]$$
- **Hệ quả đối với mô hình khởi tạo ngẫu nhiên:**
  - Ma trận trọng số $W_Q, W_K, W_V$ là các ma trận Gaussian ngẫu nhiên.
  - Tích vô hướng attention $\frac{q_i k_j^\top}{\sqrt{d}}$ phân bố chuẩn với kỳ vọng 0, dẫn đến softmax phân bố đều:
    $$\alpha_{i, j} \approx \frac{1}{T} = \frac{1}{135} \approx 0.0074$$
  - Không có bất kỳ liên kết ưu tiên nào giữa token `query_key` ở cuối chuỗi với `needle_key` ở giữa chuỗi.
  - Phân phối xác suất ở đầu ra trên tập từ vựng $V = 1000$ là nhiễu ngẫu nhiên ($P(w) \approx 0.001$). Xác suất chọn trúng token đích qua phép lấy `argmax` là $0.1\% \approx 0/25 = 0.00\%$.

---

## 3. TẠI SAO residual connection DẪN ĐẾN DỰ ĐOÁN = QUERY_TOKEN?

Trong phân tích mẫu thủ công `tests/debug_mkniah.py`:
- Queried Key = `116`, Target Value = `516`.
- Mô hình ngẫu nhiên dự đoán: `116` với xác suất cao vượt trội ($0.02123$ so với trung bình $0.001$).
- **Nguyên nhân giải tích:**
  Mô hình dùng kỹ thuật **Weight Tying** giữa ma trận nhúng token `tok_emb` và ma trận chiếu đầu ra `lm_head`:
  $$W_{\text{head}} = W_{\text{emb}} \in \mathbb{R}^{V \times d}$$
  Trạng thái ẩn ở tầng cuối cùng $x_T$ chịu ảnh hưởng mạnh bởi đường truyền thẳng (residual shortcut):
  $$x_T = x_0 + \sum_{l=1}^L \Delta x_l \approx W_{\text{emb}}[116] + \text{noise}$$
  Khi nhân với `lm_head`:
  $$\text{logits} = x_T W_{\text{emb}}^\top$$
  Phần tử lớn nhất tất yếu là:
  $$\text{logit}[116] \approx \|W_{\text{emb}}[116]\|^2 > \text{logit}[w], \quad \forall w \ne 116$$
  Do đó, khi không có cơ chế chú ý định hướng, mô hình ngẫu nhiên luôn có xu hướng **lặp lại chính token vừa được đưa vào**!

---

## 4. VAI TRÒ CHÍNH XÁC CỦA CMS TRONG BÀI BÁO GỐC

Trong *Nested Learning*, CMS giải quyết bài toán:
- Khi ngữ cảnh quá dài (vượt quá dung lượng attention window hoặc context budget), attention thông thường bị phân tán hoặc không thể nạp hết.
- CMS nạp kiến thức vào các trọng số MLP Chain $\theta_k$ qua gradient descent cục bộ (Equation 71):
  $$\theta_k^{(t+1)} = \theta_k^{(t)} - \eta_k \nabla_{\theta_k} \mathcal{L}(X_{\tau_k(t)})$$
- Bài test cô lập trong `tests/debug_mkniah.py` đã chứng minh:
  Khi tối ưu hóa 10 bước gradient trên needle, loss giảm từ $7.10 \to 1.95$, xác suất token đích tăng từ $0.0008 \to 0.141$ và dự đoán chính xác $100\%$ ($516 == 516$).
- Tuy nhiên, trong đánh giá MK-NIAH tự nhiên:
  - Nếu mô hình nền không biết token nào là needle cần nhớ (vì không có induction head hoặc task instruction), gradient của generic cross-entropy loss bị phân bổ đều cho toàn bộ 135-256 tokens của chunk.
  - Mỗi token chỉ nhận một lượng gradient rất nhỏ, dẫn đến xác suất tăng nhẹ ($0.0008 \to 0.0011$, tức $+27.5\%$), nhưng chưa đủ để vượt qua đỉnh nhúng residual của query token.

---

## 5. KẾT LUẬN & ĐƯỜNG DẪN GIẢI QUYẾT KHOA HỌC (THE SCIENTIFIC REMEDY)

1. **Không thể ép mô hình ngẫu nhiên đạt kết quả của mô hình pre-trained:** Việc so sánh điểm MK-NIAH tuyệt đối của mô hình ngẫu nhiên với Llama-3 pre-trained 15T tokens là một ngụy biện khoa học (apples-to-oranges comparison).
2. **Cần tách bạch 2 nhiệm vụ nghiên cứu:**
   - **Track 1 (Kiểm chứng cơ chế - Mechanism Validation):** Dùng mô hình micro để kiểm tra tính đúng đắn toán học của Equation 70, 71, 74 và khả năng lưu trữ/xóa bộ nhớ qua bài toán tổng hợp (synthetic retrieval task).
   - **Track 2 (Tái hiện xu hướng bài báo - Reproduction Baseline):** Dùng mô hình decoder tiền huấn luyện phù hợp phần cứng (**`SmolLM2-135M`**, đóng băng backbone, chỉ học CMS MLPs) để kiểm tra xem CMS có giúp cải thiện độ chính xác truy xuất và giảm perplexity so với ICL hay không.
