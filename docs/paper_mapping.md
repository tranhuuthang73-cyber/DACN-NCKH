# BẢNG ÁNH XẠ TOÀN DIỆN: PAPER 2512.24695v1 ↔ THIẾT KẾ REPRODUCTION BASELINE (PHASE 1)

> **Tài liệu nguồn:**
> 1. *Nested Learning: The Illusion of Deep Learning Architecture* (arXiv:2512.24695v1).
> 2. *Đề cương: Chatbot hỏi đáp trên tài liệu với bộ nhớ đa thang dựa trên Nested Learning*.

---

## 1. TỔNG QUAN HỆ THỐNG CÁC THÀNH PHẦN

Bài báo *Nested Learning* (NL) tiếp cận kiến trúc mạng nơ-ron sâu dưới góc nhìn: **các tầng/khối mạng nơ-ron và các bộ tối ưu hóa đều là các mô-đun nhớ kết hợp (Associative Memory Modules) được tối ưu hóa lồng nhau ở các dải tần số (frequency/timescale) khác nhau**.

Mục tiêu duy nhất của Phase 1: **Dựng lại mô hình từ bài báo ở quy mô nhỏ để có một baseline có thể chạy được**, tập trung vào **Hope-Attention** kết hợp **Continuum Memory System (CMS)** cho bài toán hỏi đáp trên tài liệu (Document QA / Long-context).

---

## 2. BẢNG ÁNH XẠ CHI TIẾT TỪNG THÀNH PHẦN

### 2.1. Nested Learning Framework (Khung lý thuyết Học Lồng nhau)
- **Section trong paper:** Section 3 (3.1, 3.2, 3.3), Definition 1, Definition 2, Appendix A (Definition 6).
- **Equation / Figure / Table:**
  - *Equation (1):* Bộ nhớ kết hợp $\mathcal{M}(x) = W x$ tối ưu hóa $\min_W \mathcal{L}(W; x)$.
  - *Equation (2) – (4):* Quá trình tối ưu hóa lồng nhau giữa các mức $\ell = 1, \dots, K$.
  - *Equation (5) – (10):* Các hình thức truyền tri thức giữa các mức: Forward pass, Hyperparameter modulation, Backpropagation.
  - *Figure 1, 2, 3:* Minh họa chu kỳ học lồng nhau và ánh xạ thời gian (timescale hierarchy).
- **Input:** Chuỗi biểu diễn token/ngữ cảnh theo thời gian $\{x_t\}_{t=1}^T$.
- **Output:** Biểu diễn ẩn hoặc tham số được cập nhật ở từng mức thời gian.
- **Update rule:** Mỗi mức $\ell$ chạy một vòng lặp tối ưu hóa ứng với tần số $f_\ell$:
  $$f_\ell = \frac{\max_i C^{(i)}}{C^{(\ell)}}$$
  với $C^{(\ell)}$ là độ dài khối (chunk size) trước khi tham số mức $\ell$ được cập nhật.
- **Tham số quan trọng:** Số mức $K$, chu kỳ/tần số cập nhật $\{f_\ell\}$, chunk size $\{C^{(\ell)}\}$, tốc độ học nội tại $\{\eta^{(\ell)}\}$.
- **Bắt buộc implement ở Phase 1:** Khái niệm chia mức tần số (multi-timescale/chunk-based scheduling) điều khiển cập nhật tham số bộ nhớ.
- **Chưa cần implement ở Phase 1:** Khung lý thuyết tổng quát dạng giải tích liên tục (continuous-time ODE/PDE), các dạng truyền tri thức qua hypernetwork phức tạp.

---

### 2.2. Continuum Memory System (CMS - Hệ thống Bộ nhớ Liên tục)
- **Section trong paper:** Section 7 (7.1, 7.3).
- **Equation / Figure / Table:**
  - *Equation (70) (Sequential Chain CMS):*
    $$y_t = \mathrm{MLP}^{(f_k)}\left(\mathrm{MLP}^{(f_{k-1})}\left(\dots \mathrm{MLP}^{(f_1)}(x_t)\right)\right)$$
  - *Equation (71) (Quy tắc cập nhật tham số theo chu kỳ):*
    $$\theta^{(f_\ell)}_{i+1} = \theta^{(f_\ell)}_i - \begin{cases} \sum_{t=i-C^{(\ell)}}^i \eta^{(\ell)}_t f(\theta^{(f_\ell)}_t; x_t) & \text{nếu } i \equiv 0 \pmod{C^{(\ell)}} \\ 0 & \text{ngược lại} \end{cases}$$
    Trong đó $f(\cdot)$ là thành phần gradient lỗi của bài toán (ví dụ: gradient của cross-entropy loss dự đoán token tiếp theo $\nabla \mathcal{L}_{\text{NTP}}$).
  - *Equation (72) (Nested CMS):* Khởi tạo trạng thái ban đầu qua meta-learning giữa các mức ngữ cảnh.
  - *Equation (73) (Sequential CMS meta-initialization):* Khởi tạo liên kết qua backprop ở mức tần số thấp nhất.
  - *Equation (74) (Independent / Head-wise CMS):*
    $$y_t = \mathrm{Agg}\left(\mathrm{MLP}^{(f_k)}(x_t), \mathrm{MLP}^{(f_{k-1})}(x_t), \dots, \mathrm{MLP}^{(f_1)}(x_t)\right)$$
  - *Section 7.3 (Ad-hoc Level Stacking):* Khởi tạo các mức CMS bằng trọng số MLP đã pre-train:
    $$\mathrm{MLP}^{(f_\ell)}_0(\cdot) = \mathrm{MLP}_{\text{pre-trained}}(\cdot)$$
    Khi $\eta^{(\ell)}_t \to 0$, mô-đun giữ nguyên hành vi của mô hình gốc.
- **Input:** Vector biểu diễn ẩn $x_t \in \mathbb{R}^{d_{\text{model}}}$.
- **Output:** Vector biểu diễn sau bộ nhớ $y_t \in \mathbb{R}^{d_{\text{model}}}$.
- **Update rule:** Tích lũy gradient của hàm mất mát qua cửa sổ $C^{(\ell)}$ token; cập nhật tham số $\theta^{(f_\ell)}$ tại các mốc chia hết cho $C^{(\ell)}$; giữ nguyên tham số ở các bước trung gian.
- **Tham số quan trọng:**
  - Số mức $k$ (trong paper thử nghiệm từ $k=1$ đến $k=4$).
  - Chunk size $C^{(\ell)}$ của từng mức.
  - Learning rate của từng mức $\eta^{(\ell)}$.
  - Hàm Aggregation (đối với biến thể Equation 74) hoặc chuỗi tuần tự (Equation 70).
- **Chi tiết paper KHÔNG nêu rõ (Not specified in paper):**
  - Giá trị chính xác của learning rate $\eta^{(\ell)}$ dùng trong thực nghiệm Figure 7.
  - Tỷ lệ bước chunk giữa các mức khi có 2, 3, 4 mức bộ nhớ (chỉ nêu "Lowest Freq = 512, 2K, 8K").
  - Liệu optimizer nội tại $f(\cdot)$ dùng SGD thuần túy hay có momentum/AdamW.
- **Bắt buộc implement ở Phase 1:**
  - Chuỗi MLP nhiều mức (hỗ trợ cả dạng tuần tự Equation 70 và độc lập Equation 74).
  - Bộ đệm tích lũy gradient (gradient accumulator) theo chunk size $C^{(\ell)}$.
  - Cơ chế cập nhật ngắt quãng theo bước token (Equation 71).
  - Cơ chế nạp trọng số khởi tạo ban đầu từ MLP nền (Section 7.3).
  - Cơ chế reset bộ nhớ về trạng thái ban đầu giữa các tài liệu.
- **Chưa cần implement ở Phase 1:**
  - Bộ tối ưu M3 (Multi-scale Momentum Muon - Section 7.2) vì đây là optimizer cho pre-training/vision, không nằm trong baseline Document QA.
  - Huấn luyện meta-learning 15 tỷ token để tìm trạng thái khởi tạo (Eq 72-73) vì vượt quá tài nguyên phần cứng.

---

### 2.3. Hope Architecture (Kiến trúc Hope đầy đủ)
- **Section trong paper:** Section 8 (8.1, 8.2, 8.3).
- **Equation / Figure / Table:**
  - *Figure 5:* Sơ đồ khối Hope: Self-referential Titans $\to$ Continuum Memory System (CMS).
  - *Equation (86) – (89):* Mô-đun Deep Self-Referential Titans tạo $q, k, v, \eta, \alpha$ và cập nhật qua Delta Gradient Descent (DGD).
  - *Equation (90) – (93):* Huấn luyện song song theo chunk và các dạng biểu diễn truy hồi ma trận.
  - *Equation (94) – (97):* Lan truyền tiến của Hope:
    $$o_t = \mathrm{Titans}(x_t), \quad y_t = \mathrm{CMS}(o_t) = \mathrm{MLP}^{(f_k)}(\dots \mathrm{MLP}^{(f_1)}(o_t))$$
- **Input:** Token embeddings $x_t \in \mathbb{R}^{d_{\text{model}}}$.
- **Output:** Token hidden state $y_t \in \mathbb{R}^{d_{\text{model}}}$.
- **Update rule:** Kết hợp cập nhật nhanh của Titans (theo từng token hoặc chunk nhỏ) và cập nhật đa thang của CMS.
- **Bắt buộc implement ở Phase 1:** Hiểu rõ cấu trúc phân tầng giữa working memory và persistent memory.
- **Chưa cần implement ở Phase 1:** Khối Self-referential Titans đầy đủ (6 mạng MLP $M_k, M_v, M_q, M_\eta, M_\alpha, M_{\text{mem}}$), vì thực nghiệm Document QA của paper và đề cương chọn **Hope-Attention**.

---

### 2.4. Hope-Attention (Biến thể Baseline cho Document QA)
- **Section trong paper:** Section 8.3 (đoạn "Hope-Attention", trang 33), Section 9.1 (trang 34–35), Đề cương mục 4.
- **Equation / Figure / Table:**
  - *Paper Section 8.3:*
    > *"Hope-Attention. We also use another variant of Hope, in which we simply replace the self-modifying Titans with softmax global attention (Vaswani et al. 2017)."*
  - *Đề cương mục 4:*
    > *"Baseline thay khối MLP của Transformer bằng một chuỗi k khối MLP cập nhật ở các tần số khác nhau, và giữ nguyên attention (biến thể Hope-Attention)."*
  - Công thức lan truyền tầng Hope-Attention:
    $$x'_t = \mathrm{LayerNorm}\left(x_t + \mathrm{SelfAttention}(x_t)\right)$$
    $$y_t = \mathrm{LayerNorm}\left(x'_t + \mathrm{CMS}(x'_t)\right)$$
    Trong đó $\mathrm{SelfAttention}$ là causal masked multi-head attention tiêu chuẩn.
- **Input:** Chuỗi token embedding $x \in \mathbb{R}^{B \times L \times d_{\text{model}}}$.
- **Output:** Phân phối xác suất token kế tiếp (logits) $\in \mathbb{R}^{B \times L \times V}$.
- **Update rule:**
  - Tầng Attention và LayerNorm được giữ cố định trong quá trình đọc tài liệu (hoặc tối ưu ở outer-loop).
  - Các khối $\mathrm{MLP}^{(f_\ell)}$ trong CMS được cập nhật online theo Equation (71) dựa trên gradient của loss mô hình ngôn ngữ trên các token tài liệu.
- **Tham số quan trọng:**
  - Hidden dimension $d_{\text{model}}$, số attention heads $n_{\text{heads}}$, head dimension $d_{\text{head}}$.
  - Feed-forward intermediate dimension $d_{\text{ff}}$ (thường bằng $4 \times d_{\text{model}}$).
  - Số tầng Transformer $L_{\text{layers}}$.
  - Cấu hình CMS trên mỗi tầng: số mức $k$, chunk sizes $C^{(\ell)}$, learning rates $\eta^{(\ell)}$.
- **Bắt buộc implement ở Phase 1:**
  - Lớp `CausalSelfAttention` chuẩn với causal mask.
  - Lớp `ContinuumMemorySystem` (CMS) thay thế MLP chuẩn.
  - Khối `HopeAttentionBlock` kết hợp Attention + CMS + Residual + LayerNorm.
  - Mô hình ngôn ngữ hoàn chỉnh `HopeAttentionLM` (Embedding $\to N \times$ HopeAttentionBlock $\to$ Final Norm $\to$ LM Head).

---

### 2.5. Cơ chế nhiều mức bộ nhớ & Lịch cập nhật (Multi-Timescale Schedule)
- **Section trong paper:** Section 3.2, 7.1, 8.2, 9.1.
- **Equation / Figure / Table:**
  - *Equation (71):* Cập nhật điều kiện $i \equiv 0 \pmod{C^{(\ell)}}$.
  - *Figure 7:* 4 cấu hình số mức (1 mức = ICL baseline, 2 mức, 3 mức, 4 mức) và 3 dải tần số chậm nhất (Lowest Freq = 512, 2K, 8K).
- **Nguyên lý hoạt động:**
  - Mức 1 ($\ell=1$): Tần số thấp nhất $\to$ Chu kỳ $C^{(1)}$ lớn nhất $\to$ Bộ nhớ chậm, lưu giữ thông tin dài hạn, ít bị quên.
  - Mức cao hơn ($\ell > 1$): Tần số cao hơn $\to$ Chu kỳ $C^{(\ell)}$ nhỏ hơn $\to$ Bộ nhớ nhanh, thích nghi linh hoạt với ngữ cảnh cục bộ.
- **Chi tiết paper KHÔNG nêu rõ:**
  - Khi có $k=4$ mức và chunk dài nhất là 512 (hoặc 2K, 8K), các chunk con là bao nhiêu?
  - *Quyết định thiết kế cho Phase 1:* Áp dụng cấp số nhân chia đôi lũy thừa 2:
    - Ví dụ: với $k=3$, chunk cơ sở $C_0=16$, ta có $C^{(1)}=64, C^{(2)}=32, C^{(3)}=16$.
    - Tham số hóa linh hoạt qua config để kiểm chứng thực nghiệm.

---

### 2.6. Thực nghiệm liên quan tới Document QA & Long-Context
- **Section trong paper:** Section 9.1 (trang 34–35).
- **Equation / Figure / Table:**
  - *Figure 7 (Right):* Benchmark **QASPER** (Dasigi et al. 2021) — Đo perplexity trên toàn văn bài báo NLP.
    - Kết quả paper: ICL baseline $\approx 3.53$, DuoAttention $\approx 4.11$. Hope-Attention đạt perplexity tốt hơn (thấp hơn) khi tăng từ 1 đến 4 mức bộ nhớ (đạt $\approx 3.16$ ở mức 4 với Lowest Freq = 512).
  - *Figure 7 (Left):* Benchmark **MK-NIAH** (Multi-Key Needle In A Haystack từ RULER) — Đo độ chính xác truy xuất nhiều khóa trong văn bản dài.
    - Kết quả paper: ICL baseline $\approx 88.5\%$, DuoAttention $\approx 47.3\%$. Hope-Attention tăng từ $90.1\%$ (1 level) lên $100\%$ (4 levels).
  - *Figure 7 (Middle):* Benchmark **LongHealth** (Adams et al. 2025) — 20 bệnh án dài, 200 câu hỏi trắc nghiệm.
- **Bắt buộc implement ở Phase 1:**
  - Tạo bộ dữ liệu vi mô (micro-benchmarks) mô phỏng chính xác cấu trúc của:
    1. **MK-NIAH Micro:** Bài toán tìm khóa-giá trị phân tán trong chuỗi văn bản dài.
    2. **Document QA / Next-Token Perplexity Micro:** Đọc văn bản tài liệu liên tục và đo loss/perplexity của câu trả lời.
  - Chạy so sánh thực nghiệm thực tế giữa:
    - Baseline 1 mức (tương đương ICL / MLP tĩnh hoặc cập nhật đơn lẻ).
    - Hope-Attention đa mức (2 mức, 3 mức, 4 mức).
- **Chưa cần implement ở Phase 1:**
  - Tải toàn bộ 15GB dữ liệu QASPER/LongHealth và chạy trên cụm GPU lớn.
  - Fine-tuning quy mô lớn 15 tỷ token.

---

## 3. TỔNG HỢP CÁC ĐIỂM "NOT SPECIFIED IN PAPER"

| STT | Chi tiết kỹ thuật | Trạng thái trong Paper | Cách xử lý trong Baseline Phase 1 |
|---|---|---|---|
| 1 | Learning rate $\eta^{(\ell)}$ của từng mức CMS | Không cung cấp giá trị số cụ thể | Đưa vào config (`lr_cms`), thiết lập mặc định $1 \times 10^{-4}$ (hoặc điều chỉnh qua grid test) |
| 2 | Bộ chia chunk cụ thể cho các mức trung gian | Chỉ ghi "Lowest Freq = 512, 2K, 8K" | Sử dụng tỷ lệ lũy thừa 2: $C^{(\ell)} = C_{\text{base}} \times 2^{k - \ell}$ |
| 3 | Optimizer nội tại của CMS | Chỉ ghi "error component of an arbitrary optimizer" | Sử dụng SGD tích lũy gradient (phương trình 71) hoặc AdamW mini-step |
| 4 | Cơ chế reset bộ nhớ giữa các tài liệu | Ghi khái quát "re-initialized to $\theta_0$" | Khởi tạo lại trọng số CMS về trạng thái ban đầu trước mỗi tài liệu mới |
| 5 | Dạng kết nối CMS (Tuần tự Eq 70 hay Song song Eq 74) | Paper đề cập cả hai, Eq 70 là chính | Cài đặt dạng tuần tự (Eq 70) làm mặc định theo đề cương mục 4, đồng thời hỗ trợ dạng độc lập qua cờ config |
