# 📋 BIÊN BẢN BÀN GIAO CÔNG VIỆC DỰ ÁN (PROJECT STATUS & HANDOVER)
> **Dành cho**: Antigravity AI Agent / Kỹ sư tiếp quản & Nhóm Nghiên cứu.  
> **Dự án**: Nghiên cứu Khoa học Sinh viên — Hệ thống Chatbot tài liệu dựa trên Nested Learning (SA-CMS & Hybrid QA).  
> **Thời điểm cập nhật**: 04/10/2026.  
> **Trạng thái**: 🎉 **ĐÃ HOÀN THÀNH 100% TOÀN BỘ PHASE 4.1 BENCHMARK & TỔNG HỢP XONG BÁO CÁO MASTER!**  
> 🔒 **CHÍNH SÁCH ĐÓNG BĂNG HUẤN LUYỆN (TRAINING FREEZE)**: Tuyệt đối KHÔNG chạy training mới trên máy hiện tại. Mọi thực nghiệm chỉ được dùng checkpoint sẵn có. Nếu cần train bắt buộc đánh dấu `NEED_EXTERNAL_GPU` và STOP! Chi tiết: [`docs/training_freeze_protocol.md`](docs/training_freeze_protocol.md).

---

## ⚡ TỔNG QUAN NHANH (TL;DR)
1. **Toàn bộ Phase 4.1 đã hoàn thành 100%**:
   - Tất cả 5 câu hỏi nghiên cứu RQ1, RQ2, RQ3, RQ4, RQ5 đã hoàn tất trên cả 3 seeds ngẫu nhiên [42, 43, 44].
   - **Vietnamese Final Benchmark (20 tài liệu / 350 câu hỏi)** đã hoàn tất toàn bộ 18/18 runs trên card đồ họa **NVIDIA GeForce RTX 3050 Laptop GPU**.
2. **Master Reports & Kết quả thống kê chính thức**:
   - Đã chạy tổng hợp thành công qua `scripts/aggregate_phase4_1_results.py`.
   - Bảng kết quả tổng hợp chính thức: `results/phase4_1_master_results.csv` và `results/phase4_1_master_results.json`.
   - Bộ 6 báo cáo học thuật chuyên sâu đã sinh tại thư mục `docs/`:
     - `docs/phase4_1_rq1.md` (MK-NIAH, QASPER, LongHealth)
     - `docs/phase4_1_rq2.md` (Controlled update budget)
     - `docs/phase4_1_rq3.md` (Faithfulness, Citation & Refusal)
     - `docs/phase4_1_rq4.md` (Catastrophic Forgetting)
     - `docs/phase4_1_rq5.md` (3-Level Hardware Profiling & Latency)
     - `docs/phase4_1_vietnamese.md` (20 tài liệu tiếng Việt, 350 câu hỏi)
3. **Regression Test Suite**: Đạt **100/100 passed** (`pytest tests/`).

---

## 🏛️ THÔNG TIN MÔI TRƯỜNG & PHẦN CỨNG THỰC NGHIỆM
- **Hệ điều hành**: Windows 11
- **GPU thực thi**: NVIDIA GeForce RTX 3050 Laptop GPU (4GB VRAM)
- **Python**: 3.9.13 / PyTorch 2.0.0+cu118
- **Transformers**: 4.41.2
- **Backbone Model**: `HuggingFaceTB/SmolLM2-135M` (134,515,008 tham số, **100% frozen**)
- **Training Samples Lock**: Đúng 200 samples (`TR_DOC_001` – `TR_DOC_020`) cho 3 epochs, $lr = 1e-4$, AdamW.

---

## 📊 CHI TIẾT TIẾN ĐỘ TỪNG PHẦN (TẤT CẢ ĐÃ HOÀN THÀNH 100%)

| Thành phần / Giai đoạn | Trạng thái | Vị trí lưu trữ / Artifact | Ghi chú |
| :--- | :---: | :--- | :--- |
| **Phase 1 -> Phase 3.3** | ✅ XONG | `src/`, `tests/`, `docs/` | Toàn bộ core SA-CMS, Hybrid QA, Evidence, Refusal controller |
| **Phase 4.0 - 4.0.3** | ✅ XONG | `configs/`, `docs/phase4_0_*.md` | Protocol Freeze, Fairness Lock, Scope Lock |
| **9 Adapter Checkpoints** | ✅ XONG | `checkpoints/phase4_1/` | B4, B5, P1/P2 cho cả 3 seeds [42, 43, 44] đã train xong trên 200 samples |
| **RQ1: MK-NIAH Benchmark** | ✅ XONG | `results/phase4_1/rq1/rq1_raw_results.json` | 100% pass across all configurations |
| **RQ2: QASPER Benchmark** | ✅ XONG | `results/phase4_1/rq2/rq2_raw_results.json` | 100% pass across all configurations |
| **RQ3: Faithfulness & Refusal** | ✅ XONG | `results/phase4_1/rq3/rq3_raw_results.json` | Đã xong 3 seeds + `blinded_manual_verification_100.csv` |
| **RQ4: Catastrophic Forgetting**| ✅ XONG | `results/phase4_1/rq4/rq4_raw_results.json` | Đã xong 3 seeds |
| **RQ5: 3-Level Efficiency** | ✅ XONG | `results/phase4_1/rq5/rq5_raw_results.json` | Đã xong đo đạc latency, memory, VRAM |
| **Phase 4.1F: Vietnamese Benchmark** | ✅ XONG | `results/phase4_1/vietnamese/vietnamese_raw_results.json` | 18/18 runs hoàn thành trên RTX 3050 (Seeds 42, 43, 44) |
| **Phase 4.1 Master Aggregation** | ✅ XONG | `results/phase4_1_master_results.csv`<br>`results/phase4_1_master_results.json` | Thống kê Mean ± SD, Bootstrap 95% CI |
| **Phase 4.0.4: Handoff Package**| ✅ XONG | `training_handoff_rtx3050/`<br>`training_handoff_rtx3050.zip` | Gói độc lập cho RTX 3050 6GB/8GB, 14/14 preflight pass, checksum pass |

---

### 📁 DANH MỤC ARTIFACTS VÀ BÁO CÁO HỌC THUẬT VỪA TẠO
1. **Dữ liệu tổng hợp toàn diện**:
   - `results/phase4_1_master_results.csv`: Bảng tổng hợp thống kê Mean ± SD và Bootstrap 95% Confidence Interval cho toàn bộ 5 RQs và Vietnamese Benchmark.
   - `results/phase4_1_master_results.json`: Tập tin JSON cấu trúc đầy đủ phục vụ sinh biểu đồ luận văn.
2. **Bộ 6 Báo cáo Nghiên cứu Khoa học Chính thức**:
   - `docs/phase4_1_rq1.md`: Đánh giá dung lượng ghi nhớ (MK-NIAH, QASPER, LongHealth).
   - `docs/phase4_1_rq2.md`: Đối sánh căn chỉnh cấu trúc văn bản vs cố định token với cùng ngân sách cập nhật.
   - `docs/phase4_1_rq3.md`: Đo lường tính trung thực (Faithfulness), độ chính xác trích dẫn và cổng từ chối.
   - `docs/phase4_1_rq4.md`: Đánh giá hiện tượng quên thảm khốc (Catastrophic Forgetting) trên kho tài liệu tăng dần.
   - `docs/phase4_1_rq5.md`: Định lượng tài nguyên phần cứng, độ trễ và bộ nhớ 3 cấp độ.
   - `docs/phase4_1_vietnamese.md`: Đánh giá độc lập trên 20 tài liệu / 350 câu hỏi tiếng Việt.

---

## ⚠️ NGUYÊN TẮC BẤT BIẾN KHI TIẾP QUẢN (CRITICAL INVARIANTS)
1. **KHÔNG xóa file kết quả trong `results/phase4_1/`**: Các kết quả RQ1 - RQ5 và Seed 42 đã tốn gần 20 giờ chạy GPU. Xóa đi sẽ mất công chạy lại rất lâu.
2. **KHÔNG thay đổi cấu hình huấn luyện**:
   - Backbone: `SmolLM2-135M` đông cứng 100%.
   - Số mẫu train: Cố định tuyệt đối đúng 200 samples (`TR_DOC_001` - `TR_DOC_020`).
   - Optimizer: AdamW, $lr = 1e-4$, epochs = 3, effective batch size = 4.
3. **KHÔNG để rò rỉ dữ liệu test (Zero Data Leakage)**:
   - Tuyệt đối không dùng 20 văn bản test tiếng Việt, QASPER test, LongHealth test hay MK-NIAH test vào bất kỳ bước huấn luyện hay cân chỉnh nào.
4. **Giữ nguyên Refusal Threshold của P2 & B2**:
   - `score_threshold = 3.0`
   - `min_evidence = 1`
   - `coverage_threshold = 0.35`
   - Tuyệt đối không tinh chỉnh ngưỡng này theo kết quả test để "làm đẹp số liệu".

---

## 📂 SƠ ĐỒ CÁC FILE QUAN TRỌNG NHẤT TRONG REPO
```
DACN-NCKH/
├── README.md                      <-- Báo cáo tổng thể toàn bộ dự án NCKH
├── README_HANDOVER.md             <-- FILE NÀY (Bàn giao tiến độ & danh mục báo cáo chính thức)
├── scripts/
│   ├── run_phase4_1.py            <-- Runner thực thi toàn bộ Phase 4.1 Benchmark
│   ├── aggregate_phase4_1_results.py <-- Runner tổng hợp số liệu Master và xuất 6 Markdown docs
│   └── build_vietnamese_final_dataset.py <-- Bộ 20 docs / 350 câu hỏi tiếng Việt
├── results/phase4_1/
│   ├── phase4_1_master_results.csv<-- [ĐÃ XONG] BẢNG KẾT QUẢ TỔNG HỢP CHÍNH THỨC
│   ├── phase4_1_master_results.json<-- [ĐÃ XONG] DỮ LIỆU TỔNG HỢP TOÀN BỘ RQS VÀ VIETNAMESE
│   ├── rq1/rq1_raw_results.json   <-- [ĐÃ XONG]
│   ├── rq2/rq2_raw_results.json   <-- [ĐÃ XONG]
│   ├── rq3/rq3_raw_results.json   <-- [ĐÃ XONG]
│   ├── rq4/rq4_raw_results.json   <-- [ĐÃ XONG]
│   ├── rq5/rq5_raw_results.json   <-- [ĐÃ XONG]
│   └── vietnamese/
│       └── vietnamese_raw_results.json <-- [ĐÃ XONG 100% CẢ 3 SEEDS 42, 43, 44]
├── docs/                          <-- 6 Báo cáo khoa học chính thức vừa sinh (phase4_1_*.md)
├── checkpoints/phase4_1/          <-- 9 checkpoint đã train của seeds 42, 43, 44
├── training_handoff_rtx3050/      <-- Gói bàn giao độc lập cho GPU RTX 3050
└── tests/                         <-- Bộ 100 unit tests (chạy: pytest tests/)
```

---
*Chúc bạn tiếp quản phiên làm việc suôn sẻ và đạt kết quả nghiên cứu khoa học xuất sắc!*
