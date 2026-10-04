# 📋 BIÊN BẢN BÀN GIAO CÔNG VIỆC DỞ DANG (HANDOVER FOR NEXT AGENT)
> **Dành cho**: Antigravity AI Agent / Kỹ sư tiếp quản phiên làm việc tiếp theo.  
> **Dự án**: Nghiên cứu Khoa học Sinh viên — Hệ thống Chatbot tài liệu dựa trên Nested Learning (SA-CMS & Hybrid QA).  
> **Thời điểm lập biên bản**: 04/10/2026.  
> **Trạng thái**: Đã hoàn thành 100% Phase 4.0.4 (External GPU Handoff Package) và ~85% Phase 4.1 Benchmark. Đang **tạm dừng** ở Vietnamese Benchmark (Seed 43 & 44) theo yêu cầu người dùng.

---

## ⚡ TỔNG QUAN NHANH (TL;DR CHO AGENT MỚI)
1. **Bạn KHÔNG cần phải làm lại từ đầu!** Toàn bộ kiến trúc, code lõi, và hầu hết benchmark đã chạy xong và lưu trữ an toàn.
2. **Regression Test**: Chạy `pytest tests/` $\to$ **100/100 passed** (xác nhận toàn bộ hệ thống hoàn hảo, không có lỗi tiềm ẩn).
3. **Phần việc còn dở dang DUY NHẤT**:
   - **Vietnamese Final Benchmark (20 tài liệu / 350 câu hỏi)**: Mới hoàn thành **Seed 42** (cả 6 methods: B1, B2, B4, B5, P1, P2). Đang chờ chạy nốt **Seed 43** và **Seed 44**.
   - **Tổng hợp báo cáo Master Phase 4.1**: Chạy `python scripts/aggregate_phase4_1_results.py` sau khi Seed 43 & 44 hoàn tất.
4. **Lý do tạm dừng**: Chạy Seed 42 trên GPU hiện tại (GTX 1650 Ti 4GB VRAM) mất ~4.75 tiếng. Người dùng yêu cầu tạm dừng ("*khoang chạy tiếp nhé để tớ bàn giao cho máy mạnh hơn nha*") để tạo gói bàn giao sang GPU RTX 3050 và quyết định xem chạy tiếp trên máy này hay máy khác.

---

## 🏛️ THÔNG TIN MÔI TRƯỜNG & PHẦN CỨNG HIỆN TẠI
- **Hệ điều hành**: Windows 11
- **GPU hiện tại**: NVIDIA GeForce GTX 1650 Ti (4GB VRAM)
- **Python**: 3.9.13
- **PyTorch**: 2.2.1+cu118
- **Backbone Model**: `HuggingFaceTB/SmolLM2-135M` (134,515,008 tham số, **100% frozen**)
- **Training Samples Lock**: Đúng 200 samples (`TR_DOC_001` – `TR_DOC_020`) cho 3 epochs, $lr = 1e-4$, AdamW.

---

## 📊 CHI TIẾT TIẾN ĐỘ TỪNG PHẦN

### 1. Những phần ĐÃ HOÀN THÀNH 100% (ĐÓNG BĂNG - TUYỆT ĐỐI KHÔNG CHẠY LẠI)

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
| **Phase 4.0.4: Handoff Package**| ✅ XONG | `training_handoff_rtx3050/`<br>`training_handoff_rtx3050.zip` | Gói độc lập cho RTX 3050 6GB/8GB, 14/14 preflight pass, checksum pass, 0% data leakage |

---

### 2. PHẦN VIỆC ĐANG DỞ DANG (CẦN LÀM TIẾP)

#### 🎯 Nhiệm vụ A: Chạy nốt Vietnamese Final Benchmark (Seed 43 & Seed 44)
- **Tập dữ liệu**: 20 tài liệu tiếng Việt, 350 câu hỏi (300 answerable, 50 unanswerable test từ chối).
- **Hiện trạng file `results/phase4_1/vietnamese/vietnamese_raw_results.json`**:
  - Đã có đầy đủ kết quả của **Seed 42** cho 6 methods: `B1`, `B2`, `B4`, `B5`, `P1`, `P2`.
  - Chưa có: **Seed 43** và **Seed 44** (tổng cộng 12 runs còn lại).
- **Cơ chế tự động khôi phục (Incremental Resume)**:
  File `scripts/run_phase4_1.py` đã được lập trình sẵn cơ chế thông minh:
  ```python
  completed_runs = {(r["seed"], r["method"]) for r in vn_results.get("runs", [])}
  if (seed, m_name) in completed_runs:
      logger.info(f"  [Vietnamese] Seed {seed} | Method {m_name} already completed, skipping.")
      continue
  ```
  Và sau mỗi method chạy xong, nó gọi ngay `json.dump(...)` để lưu vào đĩa lập tức.
- **Nếu tiếp tục chạy trên máy này**:
  ```powershell
  python scripts/run_phase4_1.py
  ```
  *Nó sẽ tự động:*
  - Nhận diện RQ1, RQ2, RQ3, RQ4, RQ5 đã xong $\to$ bỏ qua trong 0 giây.
  - Nhận diện Seed 42 của Vietnamese Benchmark đã xong $\to$ bỏ qua trong 0 giây.
  - Bắt đầu chạy ngay từ **Seed 43** $\to$ **Seed 44**.
  - *Thời gian ước tính*: ~4.5 - 5 tiếng / seed trên GTX 1650 Ti (tổng ~9-10 tiếng). Nếu chạy qua đêm hoặc trên máy mạnh hơn (RTX 3050 / 4060) sẽ nhanh hơn đáng kể.

---

#### 🎯 Nhiệm vụ B: Tổng hợp Báo cáo Master Phase 4.1
- **Điều kiện tiên quyết**: Nhiệm vụ A (Seed 43 và 44 của Vietnamese Benchmark) phải hoàn thành xong.
- **Lệnh thực thi**:
  ```powershell
  python scripts/aggregate_phase4_1_results.py
  ```
- **Tự động sinh ra các artifacts**:
  1. `results/phase4_1_master_results.csv`: Bảng tổng hợp số liệu Mean $\pm$ Std của toàn bộ các phương pháp qua các RQ.
  2. `results/phase4_1_master_results.json`: Dữ liệu JSON chính thức phục vụ vẽ biểu đồ và viết báo cáo.
  3. Bộ 6 tài liệu học thuật hoàn chỉnh trong thư mục `docs/`:
     - `docs/phase4_1_executive_summary.md`
     - `docs/phase4_1_rq1_rq2_benchmark.md`
     - `docs/phase4_1_rq3_faithfulness.md`
     - `docs/phase4_1_rq4_forgetting.md`
     - `docs/phase4_1_rq5_3level_efficiency.md`
     - `docs/phase4_1_vietnamese_final_report.md`

---

#### 🎯 Nhiệm vụ C: Sử dụng gói bàn giao Phase 4.0.4 (Nếu bàn giao cho máy RTX 3050)
- Nếu người dùng chuyển việc huấn luyện sang máy bạn có GPU RTX 3050 (6GB hoặc 8GB):
  1. Gửi file `d:\NCKH\training_handoff_rtx3050.zip` (103 KB) cho cộng sự.
  2. Máy nhận giải nén, cài đặt theo `training_handoff_rtx3050/README.md`:
     ```powershell
     pip install -r requirements.txt
     python scripts/preflight_rtx3050.py
     python scripts/run_training.py --seed 42
     python scripts/run_training.py --seed 43
     python scripts/run_training.py --seed 44
     python scripts/verify_checkpoint.py
     ```
  3. Lấy thư mục `output/checkpoints/` từ máy cộng sự copy đè vào `d:\NCKH\checkpoints/phase4_1/` nếu muốn thay thế checkpoint hiện tại bằng checkpoint train trên RTX 3050.

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
d:\NCKH\
├── README_HANDOVER.md              <-- FILE NÀY (Hướng dẫn bàn giao cho agent tiếp theo)
├── scripts/
│   ├── run_phase4_1.py            <-- Script chạy toàn bộ Phase 4.1 Benchmark (đã có resume logic)
│   ├── aggregate_phase4_1_results.py <-- Script gom toàn bộ kết quả xuất CSV/JSON và Markdown
│   └── build_vietnamese_final_dataset.py <-- Script sinh bộ 20 docs / 350 câu hỏi tiếng Việt
├── results/phase4_1/
│   ├── rq1/rq1_raw_results.json   <-- [ĐÃ XONG]
│   ├── rq2/rq2_raw_results.json   <-- [ĐÃ XONG]
│   ├── rq3/rq3_raw_results.json   <-- [ĐÃ XONG]
│   ├── rq4/rq4_raw_results.json   <-- [ĐÃ XONG]
│   ├── rq5/rq5_raw_results.json   <-- [ĐÃ XONG]
│   └── vietnamese/
│       └── vietnamese_raw_results.json <-- [ĐÃ XONG SEED 42, CẦN CHẠY TIẾP SEED 43 & 44]
├── checkpoints/phase4_1/          <-- Nơi chứa 9 checkpoint đã train của seeds 42, 43, 44
├── training_handoff_rtx3050/      <-- Thư mục gói bàn giao độc lập cho RTX 3050 6GB/8GB
├── training_handoff_rtx3050.zip  <-- File zip gói bàn giao (103 KB)
└── tests/                         <-- Bộ 100 unit tests (chạy: pytest tests/)
```

---
*Chúc bạn tiếp quản phiên làm việc suôn sẻ và đạt kết quả nghiên cứu khoa học xuất sắc!*
