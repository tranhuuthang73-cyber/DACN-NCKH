# BÁO CÁO KIỂM TOÁN PHẦN CỨNG & RÀNG BUỘC TÀI NGUYÊN (HARDWARE AUDIT)

> **Dự án:** Nghiên cứu khoa học — Tái hiện & Mở rộng Nested Learning (Hope-Attention / CMS)  
> **Giai đoạn:** Phase 1.5 — Xác định đường dẫn tái hiện khả thi quy mô học viên (Student-Scale Reproduction Path)  
> **Thời điểm kiểm toán:** 02/10/2026 (Local Machine)

---

## 1. THÔNG SỐ PHẦN CỨNG VÀ PHẦN MỀM THỰC TẾ

| Thành phần | Thông số đo đạc thực tế | Ghi chú & Ràng buộc kỹ thuật |
|---|---|---|
| **GPU Model** | NVIDIA GeForce GTX 1650 Ti Mobile | Kiến trúc Turing (Compute Capability 7.5) |
| **VRAM vật lý** | **4.0 GB (4,096 MB)** GDDR6 | Windows WDDM chiếm ~350–500 MB cho display. **VRAM khả dụng tối đa cho PyTorch: ~3.5 GB**. |
| **Hỗ trợ độ chính xác** | FP32, FP16 Native (Tensor Cores) | **Không hỗ trợ native BF16**; FP16 là lựa chọn tối ưu về tốc độ và bộ nhớ. |
| **System RAM** | **24.0 GB** (24,947,652 KB) | Khả dụng: ~10.0 GB free (Đủ tải model weights vào RAM trước khi đưa lên VRAM). |
| **Disk Space (Ổ C:)** | 41.18 GB Free (trên tổng 274.7 GB) | Có thể dùng cho Hugging Face cache nếu ổ D thiếu không gian. |
| **Disk Space (Ổ D:)** | **9.33 GB Free** (trên tổng 199.93 GB) | **Ràng buộc lưu trữ:** Ổ D: (Workspace) chỉ còn 9.3 GB, toàn bộ checkpoints và cache chỉ được chiếm tối đa ~3–4 GB. |
| **Hệ điều hành** | Windows 11 (64-bit) | PowerShell 5.1 / UTF-8 |
| **Python** | Python 3.9.13 (64-bit) | `C:\Users\ASUS\AppData\Local\Programs\Python\Python39\python.exe` |
| **PyTorch Stack** | PyTorch 2.2.1+cu118 | CUDA 11.8, cuDNN tích hợp sẵn |

---

## 2. TÍNH TOÁN NGÂN SÁCH BỘ NHỚ VRAM (VRAM BUDGET FORMULATION)

Để thực hiện thuật toán **Continuum Memory System (CMS)** theo bài báo *Nested Learning* (Equation 71):
$$\theta_k^{(t+1)} = \theta_k^{(t)} - \eta_k \nabla_{\theta_k} \mathcal{L}(X_{\tau_k(t)})$$,
hệ thống bắt buộc phải tính toán forward và backward pass trực tuyến (online gradient update) trên các chunk ngữ cảnh.

Tổng bộ nhớ VRAM yêu cầu gồm 4 thành phần:
$$M_{\text{total}} = M_{\text{backbone}} + M_{\text{CMS\_params}} + M_{\text{KV\_cache}} + M_{\text{gradients\_optimizer}} + M_{\text{activations}} \le 3.5 \text{ GB}$$

### Chi tiết phân bổ cho từng hạng mục:
1. **$M_{\text{backbone}}$ (Trọng số mô hình nền - Freeze):**
   - Lưu trữ ở định dạng FP16 ($2 \text{ bytes/param}$).
   - Với model 135M params: $135 \times 10^6 \times 2 \approx 270 \text{ MB}$.
   - Với model 500M params: $500 \times 10^6 \times 2 \approx 1,000 \text{ MB} = 1.0 \text{ GB}$.
   - Với model 1B params: $1.0 \times 10^9 \times 2 \approx 2.0 \text{ GB}$ (Quá sát ngưỡng, dễ văng OOM khi backward).
2. **$M_{\text{CMS\_params}}$ (Trọng số bộ nhớ đa thang - Trainable):**
   - Các tầng MLP Chain (Equation 70 & 74) xen kẽ giữa các block Transformer.
   - Thường chiếm ~5% đến 15% kích thước backbone: $\approx 20\text{ MB} - 100\text{ MB}$.
3. **$M_{\text{gradients\_optimizer}}$ (Bộ nhớ gradient cho Eq 71):**
   - Chỉ tính gradient cho $\theta_{\text{CMS}}$ (backbone đã đóng băng `requires_grad=False`).
   - Nếu dùng SGD with momentum hoặc AdamW cho CMS: $\approx 2 \times \text{size}(\theta_{\text{CMS}}) \approx 40\text{ MB} - 200\text{ MB}$.
4. **$M_{\text{KV\_cache}} + M_{\text{activations}}$ (Ngữ cảnh dài):**
   - Cho context length $L = 2048$ tokens, FP16: $\approx 200\text{ MB} - 400\text{ MB}$.

### Giới hạn an toàn (Safety Boundary) cho nghiên cứu:
- **Ngưỡng kích thước tối đa cho Backbone:** $\le 360\text{M}$ tham số (lý tưởng nhất: **$100\text{M} - 160\text{M}$ tham số**).
- Không chọn các mô hình $\ge 1\text{B}$ tham số trên GPU GTX 1650 Ti 4GB vì sẽ lập tức gây Out-Of-Memory (OOM) khi backward gradient online.

---

## 3. KẾT LUẬN & NGUYÊN TẮC THIẾT KẾ

1. **Tuân thủ thực tế phần cứng:** GTX 1650 Ti (4GB VRAM) hoàn toàn đủ khả năng chạy suy luận và backward pass cho các mô hình decoder tiền huấn luyện kích thước nhỏ ($100\text{M} - 360\text{M}$) kết hợp bộ nhớ CMS đóng băng backbone.
2. **Quản lý ổ cứng:** Tải duy nhất 01 mô hình được chọn về máy, không tải dàn trải để bảo vệ dung lượng trống 9.3 GB của ổ D:.
3. **Phân định ranh giới nghiên cứu:** Mô hình micro ngẫu nhiên (4.5M) được giữ lại độc lập để phục vụ kiểm chứng cơ chế kỹ thuật (sanity check); việc tái hiện xu hướng bài báo (reproduction baseline) bắt buộc phải tiến hành trên mô hình tiền huấn luyện phù hợp.
