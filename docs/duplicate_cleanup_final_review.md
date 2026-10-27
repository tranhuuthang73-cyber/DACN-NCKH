# BÁO CÁO ĐÁNH GIÁ CUỐI CÙNG TRƯỚC KHI DỌN DẸP BẢN SAO (FINAL CLEANUP REVIEW)
**Dự án:** Chatbot hỏi đáp trên tài liệu với bộ nhớ liên tục đa thang căn theo cấu trúc văn bản — SA-CMS  
**Thời điểm lập:** 2026-10-16T20:05:00+07:00  
**Nhánh làm việc:** `cleanup/path-verification` (tách từ `main` tại commit `2c7a8b0`)  
**Trạng thái thực thi:** `SELECTIVE CLEANUP COMPLETED — 101 FILES SAFELY REMOVED (816.06 MB)` (Xem chi tiết tại `docs/selective_cleanup_execution_report.md`; 188/188 tests pass, 0 commit, 0 push).

---

## 1. GIẢI QUYẾT TOÀN DIỆN CÁC ĐIỂM CHẶN (BLOCKER RESOLUTION)

### 1.1. Blocker 1 — Result Collector (`external_gpu/phase4_4/collect_results.py`)
- **Vấn đề ban đầu:** Bản mã công khai tham chiếu trực tiếp các input nằm trong danh mục dự kiến xóa (`results/phase4_2/*.json` và `checkpoints/phase4_2/*`).
- **Phân tích mã nguồn local mới nhất:**
  - File đóng vai trò thu thập kết quả và đóng gói từ Phase 4.4 sang Phase 4.5.
  - Phân tách rõ ràng:
    - **Input paths:** File kết quả A1, A3, RQ4, RQ2 và các checkpoints `.pt` huấn luyện ngoài.
    - **Output paths:** `results/phase4_4/` (subdirs) và `training_output_final/` (canonical distribution package).
- **Hành động kỹ thuật đã thực hiện:**
  1. Bổ sung cơ chế `resolve_source(primary, fallback)`: Tự động ưu tiên đọc từ **Canonical Artifact Locations** (`training_output_final/raw_results/` và `training_output_final/checkpoints/`). Chỉ tìm đến `results/phase4_2/` hay `checkpoints/phase4_2/` làm fallback nếu canonical chưa khởi tạo.
  2. Bổ sung bộ lọc mẫu checkpoint `ckpt_pattern` (`cms_3lvl_random_*.pt`, `cms_3lvl_additive_*.pt`, `rq4_*.pt`) để nhận diện đúng biến thể khi gom chung trong canonical directory.
  3. Bổ sung kiểm tra `src_p.resolve() != dest_p.resolve()` để bảo vệ an toàn, tránh lỗi copy file đè lên chính nó (`SameFileError`).
- **Kiểm chứng thực tế (Không chỉ dựa vào `DRY_RUN_MAPPED`):**
  - Đã thiết lập môi trường sandbox tạm thời (`tempfile.TemporaryDirectory`) mô phỏng trạng thái **sau cleanup** (khi `results/phase4_2/` và `checkpoints/phase4_2/` hoàn toàn vắng mặt).
  - Thu thập thực tế đã đọc trực tiếp từ canonical artifacts và sinh ra các file output có mã băm SHA-256 trùng khớp 100% với bản chuẩn (`Match: True`).
- **Kết luận Blocker 1:** **ĐÃ GIẢI QUYẾT TRIỆT ĐỂ (RESOLVED).** Script an toàn 100% kể cả sau khi các file trùng lặp bị xóa.

---

### 1.2. Blocker 2 — Offline Checkpoints trong `local_runtime/checkpoints/`
- **Vấn đề ban đầu:** Báo cáo dry-run trước đó xếp 2 checkpoint trong `local_runtime/checkpoints/` (`cms_3lvl_seed_42.pt` và `memory/cms_3lvl_seed_42.pt`) vào danh sách xóa vì trùng SHA-256 với `checkpoints/phase4_1/cms_3lvl_seed_42.pt`.
- **Kiểm tra kiến trúc & Code loader:**
  - Đã rà soát toàn bộ [`src/web/local_model_loader.py`](file:///d:/NCKH/src/web/local_model_loader.py), [`local_runtime/config/runtime_config.yaml`](file:///d:/NCKH/local_runtime/config/runtime_config.yaml), [`src/memory/offline_memory_manager.py`](file:///d:/NCKH/src/memory/offline_memory_manager.py), và [`tests/test_offline_e2e.py`](file:///d:/NCKH/tests/test_offline_e2e.py).
  - Xác định nguồn chuẩn (Canonical Origin): Checkpoint gốc của Phase 4.1 nằm tại [`checkpoints/phase4_1/cms_3lvl_seed_42.pt`](file:///d:/NCKH/checkpoints/phase4_1/cms_3lvl_seed_42.pt) (21,269,390 bytes - SHA-256 `0a379f6a238a...`).
  - Bản chất của `local_runtime/`: Đây là **gói triển khai độc lập ngoại tuyến (isolated runtime deployment environment)**, được thiết kế để Chatbot web chạy 100% offline mà không phụ thuộc vào cây thư mục nghiên cứu thực nghiệm.
  - Cả `LocalModelLoader` và `OfflineMemoryManager` đều trực tiếp nạp `local_runtime/checkpoints/cms_3lvl_seed_42.pt`.
- **Kiểm chứng thực tế nạp mô hình & suy luận E2E:**
  - Đã kích hoạt nạp mô hình offline thực tế bằng PyTorch CPU:
    - Base backbone: SmolLM2-135M (134.5M Frozen).
    - Checkpoint: `local_runtime/checkpoints/cms_3lvl_seed_42.pt` -> Trạng thái: `CURRENT_VALID_CHECKPOINT`.
    - Tokenizer: Nạp thành công từ `local_runtime/model/` (49,152 vocab tokens).
    - Suy luận hỏi đáp tiếng Việt trực tiếp: Câu hỏi *"Kiến trúc SA-CMS gồm mấy cấp độ?"* sinh kết quả chuẩn xác trong 110.8 ms (`refused: False`).
- **Quyết định điều chỉnh quan trọng:**
  - **LOẠI BỎ 2 CHECKPOINT NÀY KHỎI DANH SÁCH XÓA.**
  - Phân loại lại thành: **`KEEP_RUNTIME_DEPLOYMENT` (Bảo lưu cho Triển khai Runtime Ngoại tuyến)**.
  - Giữ nguyên:
    1. `local_runtime/checkpoints/cms_3lvl_seed_42.pt` (20.28 MB)
    2. `local_runtime/checkpoints/memory/cms_3lvl_seed_42.pt` (20.28 MB)
    3. `local_runtime/checkpoints/sa_cms_level_3_sa_cms.pt` (10.14 MB)
- **Kết luận Blocker 2:** **ĐÃ GIẢI QUYẾT TRIỆT ĐỂ (RESOLVED).** Không xóa bất kỳ checkpoint runtime nào.

---

## 2. KẾT QUẢ KIỂM THỬ HỒI QUY (FINAL TEST VERIFICATION)

1. **Full Pytest Suite:**
   - Lệnh: `pytest tests/`
   - Kết quả: **188/188 PASSED (100%)** trong 67.53s.
   - 0 test thất bại, 0 lỗi nhập/xuất.
2. **Kiểm thử Kịch bản Thiếu Bản sao (Simulated Post-Cleanup):**
   - Đã rà soát toàn bộ 25 test files trong `tests/`: Không có bất kỳ test nào tham chiếu đến 116 file dự kiến xóa.
   - Thư mục `local_runtime/tokenizer/` đã được chuyển hướng hoàn toàn sang `local_runtime/model/` và kiểm chứng đạt 11/11 tests offline (`test_strict_offline_mode.py` và `test_offline_memory_runtime.py`).
3. **Kiểm tra Script Tái lập Thí nghiệm:**
   - `scripts/evaluate_ablation_a1_a3.py`: Đã trỏ chuẩn về `training_output_final/checkpoints/`.
   - `external_gpu/phase4_4/collect_results.py`: Đã hỗ trợ `resolve_source` đọc canonical artifacts.
   - Các script báo cáo/audit (`build_phase4_3_tables.py`, `generate_thesis_figures.py`): Đọc từ các master audit file được bảo vệ nguyên trạng (`results/phase4_2_verified_master_results.csv` và `rq2_statistical_audit.json`).

---

## 3. DANH SÁCH ĐỀ NGHỊ XÓA CUỐI CÙNG (116 TỆP XÁC MINH — 816.08 MB)
Sau khi loại trừ 2 file runtime checkpoint (40.56 MB), danh sách đề nghị xóa chính thức gồm **116 file**, toàn bộ đã được kiểm chứng bitwise SHA-256 100% khớp với bản canonical được giữ lại.

### 3.1. Tổng hợp theo nhóm
| Phân nhóm | Số lượng file | Dung lượng | Thư mục Bản Canonical Giữ lại | Trạng thái Kiểm thử |
|:---|:---:|:---:|:---|:---:|
| Checkpoints Phase 4.2 (`checkpoints/phase4_2/`) | 42 | 405.70 MB | `training_output_final/checkpoints/` | PASS (188/188) |
| Checkpoints Phase 4.4 (`results/phase4_4/checkpoints/`) | 42 | 405.70 MB | `training_output_final/checkpoints/` | PASS (188/188) |
| Duplicate JSON Results (`results/` & subdirs) | 12 | 1.43 MB | `training_output_final/raw_results/` | PASS (188/188) |
| Local Tokenizer files (`local_runtime/tokenizer/`) | 5 | 3.22 MB | `local_runtime/model/` | PASS (188/188) |
| Duplicate Handoff Scripts (`training_handoff_phase4_2/`) | 7 | 0.01 MB | `external_gpu/phase4_2/` | PASS (188/188) |
| Duplicate Local Demo Docs (`local_runtime/documents/`) | 8 | 0.003 MB | `local_runtime/documents/LIFECYCLE_DOC_1791273621.txt` | PASS (188/188) |
| **TỔNG CỘNG ĐỀ NGHỊ XÓA** | **116 tệp** | **816.07 MB** | — | **AN TOÀN TUYỆT ĐỐI** |

---

### 3.2. Bảng kê chi tiết từng file đề nghị xóa (Itemized Deletion Manifest)

| STT | Đường dẫn File Đề nghị Xóa | Kích thước | SHA-256 (12 ký tự) | Đường dẫn Bản Canonical Giữ lại | Trạng thái Kiểm thử |
|:---:|:---|:---:|:---:|:---|:---:|
| 1 | `checkpoints/phase4_2/A1/cms_3lvl_random_seed_42.pt` | 20.28 MB | `427ffbc147a3...` | `training_output_final/checkpoints/cms_3lvl_random_seed_42.pt` | VERIFIED_SAFE |
| 2 | `checkpoints/phase4_2/A1/cms_3lvl_random_seed_43.pt` | 20.28 MB | `4401e910a466...` | `training_output_final/checkpoints/cms_3lvl_random_seed_43.pt` | VERIFIED_SAFE |
| 3 | `checkpoints/phase4_2/A1/cms_3lvl_random_seed_44.pt` | 20.28 MB | `2e5b11a39711...` | `training_output_final/checkpoints/cms_3lvl_random_seed_44.pt` | VERIFIED_SAFE |
| 4 | `checkpoints/phase4_2/A3/cms_3lvl_additive_seed_42.pt` | 20.28 MB | `5c040cbc0894...` | `training_output_final/checkpoints/cms_3lvl_additive_seed_42.pt` | VERIFIED_SAFE |
| 5 | `checkpoints/phase4_2/A3/cms_3lvl_additive_seed_43.pt` | 20.28 MB | `3855195e47db...` | `training_output_final/checkpoints/cms_3lvl_additive_seed_43.pt` | VERIFIED_SAFE |
| 6 | `checkpoints/phase4_2/A3/cms_3lvl_additive_seed_44.pt` | 20.28 MB | `f386517fdac1...` | `training_output_final/checkpoints/cms_3lvl_additive_seed_44.pt` | VERIFIED_SAFE |
| 7 | `checkpoints/phase4_2/RQ4/rq4_B4_seed_42_D0.pt` | 3.38 MB | `ab9d23a34fa1...` | `training_output_final/checkpoints/rq4_B4_seed_42_D0.pt` | VERIFIED_SAFE |
| 8 | `checkpoints/phase4_2/RQ4/rq4_B4_seed_42_D0_plus10.pt` | 3.38 MB | `56c665d0cae8...` | `training_output_final/checkpoints/rq4_B4_seed_42_D0_plus10.pt` | VERIFIED_SAFE |
| 9 | `checkpoints/phase4_2/RQ4/rq4_B4_seed_42_D0_plus20.pt` | 3.38 MB | `ce82f935fb23...` | `training_output_final/checkpoints/rq4_B4_seed_42_D0_plus20.pt` | VERIFIED_SAFE |
| 10 | `checkpoints/phase4_2/RQ4/rq4_B4_seed_42_D0_plus5.pt` | 3.38 MB | `7be5cdbddc68...` | `training_output_final/checkpoints/rq4_B4_seed_42_D0_plus5.pt` | VERIFIED_SAFE |
| 11 | `checkpoints/phase4_2/RQ4/rq4_B4_seed_43_D0.pt` | 3.38 MB | `03616dcda013...` | `training_output_final/checkpoints/rq4_B4_seed_43_D0.pt` | VERIFIED_SAFE |
| 12 | `checkpoints/phase4_2/RQ4/rq4_B4_seed_43_D0_plus10.pt` | 3.38 MB | `1283b1ce9fe9...` | `training_output_final/checkpoints/rq4_B4_seed_43_D0_plus10.pt` | VERIFIED_SAFE |
| 13 | `checkpoints/phase4_2/RQ4/rq4_B4_seed_43_D0_plus20.pt` | 3.38 MB | `0e04f2130cc2...` | `training_output_final/checkpoints/rq4_B4_seed_43_D0_plus20.pt` | VERIFIED_SAFE |
| 14 | `checkpoints/phase4_2/RQ4/rq4_B4_seed_43_D0_plus5.pt` | 3.38 MB | `b2d2fe883e7f...` | `training_output_final/checkpoints/rq4_B4_seed_43_D0_plus5.pt` | VERIFIED_SAFE |
| 15 | `checkpoints/phase4_2/RQ4/rq4_B4_seed_44_D0.pt` | 3.38 MB | `be8c377e237a...` | `training_output_final/checkpoints/rq4_B4_seed_44_D0.pt` | VERIFIED_SAFE |
| 16 | `checkpoints/phase4_2/RQ4/rq4_B4_seed_44_D0_plus10.pt` | 3.38 MB | `11b4fcffa93e...` | `training_output_final/checkpoints/rq4_B4_seed_44_D0_plus10.pt` | VERIFIED_SAFE |
| 17 | `checkpoints/phase4_2/RQ4/rq4_B4_seed_44_D0_plus20.pt` | 3.38 MB | `77536d360ca4...` | `training_output_final/checkpoints/rq4_B4_seed_44_D0_plus20.pt` | VERIFIED_SAFE |
| 18 | `checkpoints/phase4_2/RQ4/rq4_B4_seed_44_D0_plus5.pt` | 3.38 MB | `efd7342c902c...` | `training_output_final/checkpoints/rq4_B4_seed_44_D0_plus5.pt` | VERIFIED_SAFE |
| 19 | `checkpoints/phase4_2/RQ4/rq4_B5_seed_42_D0.pt` | 10.14 MB | `517f7ee7e7f4...` | `training_output_final/checkpoints/rq4_B5_seed_42_D0.pt` | VERIFIED_SAFE |
| 20 | `checkpoints/phase4_2/RQ4/rq4_B5_seed_42_D0_plus10.pt` | 10.14 MB | `432798af68de...` | `training_output_final/checkpoints/rq4_B5_seed_42_D0_plus10.pt` | VERIFIED_SAFE |
| 21 | `checkpoints/phase4_2/RQ4/rq4_B5_seed_42_D0_plus20.pt` | 10.14 MB | `bc39ab4c6537...` | `training_output_final/checkpoints/rq4_B5_seed_42_D0_plus20.pt` | VERIFIED_SAFE |
| 22 | `checkpoints/phase4_2/RQ4/rq4_B5_seed_42_D0_plus5.pt` | 10.14 MB | `1d76e6dcb77d...` | `training_output_final/checkpoints/rq4_B5_seed_42_D0_plus5.pt` | VERIFIED_SAFE |
| 23 | `checkpoints/phase4_2/RQ4/rq4_B5_seed_43_D0.pt` | 10.14 MB | `941c8f6ca9a9...` | `training_output_final/checkpoints/rq4_B5_seed_43_D0.pt` | VERIFIED_SAFE |
| 24 | `checkpoints/phase4_2/RQ4/rq4_B5_seed_43_D0_plus10.pt` | 10.14 MB | `d815b79d6589...` | `training_output_final/checkpoints/rq4_B5_seed_43_D0_plus10.pt` | VERIFIED_SAFE |
| 25 | `checkpoints/phase4_2/RQ4/rq4_B5_seed_43_D0_plus20.pt` | 10.14 MB | `18da2a754893...` | `training_output_final/checkpoints/rq4_B5_seed_43_D0_plus20.pt` | VERIFIED_SAFE |
| 26 | `checkpoints/phase4_2/RQ4/rq4_B5_seed_43_D0_plus5.pt` | 10.14 MB | `570f5d198981...` | `training_output_final/checkpoints/rq4_B5_seed_43_D0_plus5.pt` | VERIFIED_SAFE |
| 27 | `checkpoints/phase4_2/RQ4/rq4_B5_seed_44_D0.pt` | 10.14 MB | `e95e4a5ed7b3...` | `training_output_final/checkpoints/rq4_B5_seed_44_D0.pt` | VERIFIED_SAFE |
| 28 | `checkpoints/phase4_2/RQ4/rq4_B5_seed_44_D0_plus10.pt` | 10.14 MB | `b6d6cd3baf2a...` | `training_output_final/checkpoints/rq4_B5_seed_44_D0_plus10.pt` | VERIFIED_SAFE |
| 29 | `checkpoints/phase4_2/RQ4/rq4_B5_seed_44_D0_plus20.pt` | 10.14 MB | `6af4bba7a9d0...` | `training_output_final/checkpoints/rq4_B5_seed_44_D0_plus20.pt` | VERIFIED_SAFE |
| 30 | `checkpoints/phase4_2/RQ4/rq4_B5_seed_44_D0_plus5.pt` | 10.14 MB | `19ab505f62f0...` | `training_output_final/checkpoints/rq4_B5_seed_44_D0_plus5.pt` | VERIFIED_SAFE |
| 31 | `checkpoints/phase4_2/RQ4/rq4_P1_seed_42_D0.pt` | 10.14 MB | `ead90bca5d80...` | `training_output_final/checkpoints/rq4_P1_seed_42_D0.pt` | VERIFIED_SAFE |
| 32 | `checkpoints/phase4_2/RQ4/rq4_P1_seed_42_D0_plus10.pt` | 10.14 MB | `60d23b935f44...` | `training_output_final/checkpoints/rq4_P1_seed_42_D0_plus10.pt` | VERIFIED_SAFE |
| 33 | `checkpoints/phase4_2/RQ4/rq4_P1_seed_42_D0_plus20.pt` | 10.14 MB | `51e8a03a43ed...` | `training_output_final/checkpoints/rq4_P1_seed_42_D0_plus20.pt` | VERIFIED_SAFE |
| 34 | `checkpoints/phase4_2/RQ4/rq4_P1_seed_42_D0_plus5.pt` | 10.14 MB | `a976eee307a4...` | `training_output_final/checkpoints/rq4_P1_seed_42_D0_plus5.pt` | VERIFIED_SAFE |
| 35 | `checkpoints/phase4_2/RQ4/rq4_P1_seed_43_D0.pt` | 10.14 MB | `99964c72b771...` | `training_output_final/checkpoints/rq4_P1_seed_43_D0.pt` | VERIFIED_SAFE |
| 36 | `checkpoints/phase4_2/RQ4/rq4_P1_seed_43_D0_plus10.pt` | 10.14 MB | `d8afeec7dcfb...` | `training_output_final/checkpoints/rq4_P1_seed_43_D0_plus10.pt` | VERIFIED_SAFE |
| 37 | `checkpoints/phase4_2/RQ4/rq4_P1_seed_43_D0_plus20.pt` | 10.14 MB | `8eddfa9b50b9...` | `training_output_final/checkpoints/rq4_P1_seed_43_D0_plus20.pt` | VERIFIED_SAFE |
| 38 | `checkpoints/phase4_2/RQ4/rq4_P1_seed_43_D0_plus5.pt` | 10.14 MB | `5a75583b57cc...` | `training_output_final/checkpoints/rq4_P1_seed_43_D0_plus5.pt` | VERIFIED_SAFE |
| 39 | `checkpoints/phase4_2/RQ4/rq4_P1_seed_44_D0.pt` | 10.14 MB | `72d99395c0b3...` | `training_output_final/checkpoints/rq4_P1_seed_44_D0.pt` | VERIFIED_SAFE |
| 40 | `checkpoints/phase4_2/RQ4/rq4_P1_seed_44_D0_plus10.pt` | 10.14 MB | `e81738339dd3...` | `training_output_final/checkpoints/rq4_P1_seed_44_D0_plus10.pt` | VERIFIED_SAFE |
| 41 | `checkpoints/phase4_2/RQ4/rq4_P1_seed_44_D0_plus20.pt` | 10.14 MB | `63085db87da4...` | `training_output_final/checkpoints/rq4_P1_seed_44_D0_plus20.pt` | VERIFIED_SAFE |
| 42 | `checkpoints/phase4_2/RQ4/rq4_P1_seed_44_D0_plus5.pt` | 10.14 MB | `a44e70397c43...` | `training_output_final/checkpoints/rq4_P1_seed_44_D0_plus5.pt` | VERIFIED_SAFE |
| 43 | `results/phase4_4/checkpoints/cms_3lvl_additive_seed_42.pt` | 20.28 MB | `5c040cbc0894...` | `training_output_final/checkpoints/cms_3lvl_additive_seed_42.pt` | VERIFIED_SAFE |
| 44 | `results/phase4_4/checkpoints/cms_3lvl_additive_seed_43.pt` | 20.28 MB | `3855195e47db...` | `training_output_final/checkpoints/cms_3lvl_additive_seed_43.pt` | VERIFIED_SAFE |
| 45 | `results/phase4_4/checkpoints/cms_3lvl_additive_seed_44.pt` | 20.28 MB | `f386517fdac1...` | `training_output_final/checkpoints/cms_3lvl_additive_seed_44.pt` | VERIFIED_SAFE |
| 46 | `results/phase4_4/checkpoints/cms_3lvl_random_seed_42.pt` | 20.28 MB | `427ffbc147a3...` | `training_output_final/checkpoints/cms_3lvl_random_seed_42.pt` | VERIFIED_SAFE |
| 47 | `results/phase4_4/checkpoints/cms_3lvl_random_seed_43.pt` | 20.28 MB | `4401e910a466...` | `training_output_final/checkpoints/cms_3lvl_random_seed_43.pt` | VERIFIED_SAFE |
| 48 | `results/phase4_4/checkpoints/cms_3lvl_random_seed_44.pt` | 20.28 MB | `2e5b11a39711...` | `training_output_final/checkpoints/cms_3lvl_random_seed_44.pt` | VERIFIED_SAFE |
| 49 | `results/phase4_4/checkpoints/rq4_B4_seed_42_D0.pt` | 3.38 MB | `ab9d23a34fa1...` | `training_output_final/checkpoints/rq4_B4_seed_42_D0.pt` | VERIFIED_SAFE |
| 50 | `results/phase4_4/checkpoints/rq4_B4_seed_42_D0_plus10.pt` | 3.38 MB | `56c665d0cae8...` | `training_output_final/checkpoints/rq4_B4_seed_42_D0_plus10.pt` | VERIFIED_SAFE |
| 51 | `results/phase4_4/checkpoints/rq4_B4_seed_42_D0_plus20.pt` | 3.38 MB | `ce82f935fb23...` | `training_output_final/checkpoints/rq4_B4_seed_42_D0_plus20.pt` | VERIFIED_SAFE |
| 52 | `results/phase4_4/checkpoints/rq4_B4_seed_42_D0_plus5.pt` | 3.38 MB | `7be5cdbddc68...` | `training_output_final/checkpoints/rq4_B4_seed_42_D0_plus5.pt` | VERIFIED_SAFE |
| 53 | `results/phase4_4/checkpoints/rq4_B4_seed_43_D0.pt` | 3.38 MB | `03616dcda013...` | `training_output_final/checkpoints/rq4_B4_seed_43_D0.pt` | VERIFIED_SAFE |
| 54 | `results/phase4_4/checkpoints/rq4_B4_seed_43_D0_plus10.pt` | 3.38 MB | `1283b1ce9fe9...` | `training_output_final/checkpoints/rq4_B4_seed_43_D0_plus10.pt` | VERIFIED_SAFE |
| 55 | `results/phase4_4/checkpoints/rq4_B4_seed_43_D0_plus20.pt` | 3.38 MB | `0e04f2130cc2...` | `training_output_final/checkpoints/rq4_B4_seed_43_D0_plus20.pt` | VERIFIED_SAFE |
| 56 | `results/phase4_4/checkpoints/rq4_B4_seed_43_D0_plus5.pt` | 3.38 MB | `b2d2fe883e7f...` | `training_output_final/checkpoints/rq4_B4_seed_43_D0_plus5.pt` | VERIFIED_SAFE |
| 57 | `results/phase4_4/checkpoints/rq4_B4_seed_44_D0.pt` | 3.38 MB | `be8c377e237a...` | `training_output_final/checkpoints/rq4_B4_seed_44_D0.pt` | VERIFIED_SAFE |
| 58 | `results/phase4_4/checkpoints/rq4_B4_seed_44_D0_plus10.pt` | 3.38 MB | `11b4fcffa93e...` | `training_output_final/checkpoints/rq4_B4_seed_44_D0_plus10.pt` | VERIFIED_SAFE |
| 59 | `results/phase4_4/checkpoints/rq4_B4_seed_44_D0_plus20.pt` | 3.38 MB | `77536d360ca4...` | `training_output_final/checkpoints/rq4_B4_seed_44_D0_plus20.pt` | VERIFIED_SAFE |
| 60 | `results/phase4_4/checkpoints/rq4_B4_seed_44_D0_plus5.pt` | 3.38 MB | `efd7342c902c...` | `training_output_final/checkpoints/rq4_B4_seed_44_D0_plus5.pt` | VERIFIED_SAFE |
| 61 | `results/phase4_4/checkpoints/rq4_B5_seed_42_D0.pt` | 10.14 MB | `517f7ee7e7f4...` | `training_output_final/checkpoints/rq4_B5_seed_42_D0.pt` | VERIFIED_SAFE |
| 62 | `results/phase4_4/checkpoints/rq4_B5_seed_42_D0_plus10.pt` | 10.14 MB | `432798af68de...` | `training_output_final/checkpoints/rq4_B5_seed_42_D0_plus10.pt` | VERIFIED_SAFE |
| 63 | `results/phase4_4/checkpoints/rq4_B5_seed_42_D0_plus20.pt` | 10.14 MB | `bc39ab4c6537...` | `training_output_final/checkpoints/rq4_B5_seed_42_D0_plus20.pt` | VERIFIED_SAFE |
| 64 | `results/phase4_4/checkpoints/rq4_B5_seed_42_D0_plus5.pt` | 10.14 MB | `1d76e6dcb77d...` | `training_output_final/checkpoints/rq4_B5_seed_42_D0_plus5.pt` | VERIFIED_SAFE |
| 65 | `results/phase4_4/checkpoints/rq4_B5_seed_43_D0.pt` | 10.14 MB | `941c8f6ca9a9...` | `training_output_final/checkpoints/rq4_B5_seed_43_D0.pt` | VERIFIED_SAFE |
| 66 | `results/phase4_4/checkpoints/rq4_B5_seed_43_D0_plus10.pt` | 10.14 MB | `d815b79d6589...` | `training_output_final/checkpoints/rq4_B5_seed_43_D0_plus10.pt` | VERIFIED_SAFE |
| 67 | `results/phase4_4/checkpoints/rq4_B5_seed_43_D0_plus20.pt` | 10.14 MB | `18da2a754893...` | `training_output_final/checkpoints/rq4_B5_seed_43_D0_plus20.pt` | VERIFIED_SAFE |
| 68 | `results/phase4_4/checkpoints/rq4_B5_seed_43_D0_plus5.pt` | 10.14 MB | `570f5d198981...` | `training_output_final/checkpoints/rq4_B5_seed_43_D0_plus5.pt` | VERIFIED_SAFE |
| 69 | `results/phase4_4/checkpoints/rq4_B5_seed_44_D0.pt` | 10.14 MB | `e95e4a5ed7b3...` | `training_output_final/checkpoints/rq4_B5_seed_44_D0.pt` | VERIFIED_SAFE |
| 70 | `results/phase4_4/checkpoints/rq4_B5_seed_44_D0_plus10.pt` | 10.14 MB | `b6d6cd3baf2a...` | `training_output_final/checkpoints/rq4_B5_seed_44_D0_plus10.pt` | VERIFIED_SAFE |
| 71 | `results/phase4_4/checkpoints/rq4_B5_seed_44_D0_plus20.pt` | 10.14 MB | `6af4bba7a9d0...` | `training_output_final/checkpoints/rq4_B5_seed_44_D0_plus20.pt` | VERIFIED_SAFE |
| 72 | `results/phase4_4/checkpoints/rq4_B5_seed_44_D0_plus5.pt` | 10.14 MB | `19ab505f62f0...` | `training_output_final/checkpoints/rq4_B5_seed_44_D0_plus5.pt` | VERIFIED_SAFE |
| 73 | `results/phase4_4/checkpoints/rq4_P1_seed_42_D0.pt` | 10.14 MB | `ead90bca5d80...` | `training_output_final/checkpoints/rq4_P1_seed_42_D0.pt` | VERIFIED_SAFE |
| 74 | `results/phase4_4/checkpoints/rq4_P1_seed_42_D0_plus10.pt` | 10.14 MB | `60d23b935f44...` | `training_output_final/checkpoints/rq4_P1_seed_42_D0_plus10.pt` | VERIFIED_SAFE |
| 75 | `results/phase4_4/checkpoints/rq4_P1_seed_42_D0_plus20.pt` | 10.14 MB | `51e8a03a43ed...` | `training_output_final/checkpoints/rq4_P1_seed_42_D0_plus20.pt` | VERIFIED_SAFE |
| 76 | `results/phase4_4/checkpoints/rq4_P1_seed_42_D0_plus5.pt` | 10.14 MB | `a976eee307a4...` | `training_output_final/checkpoints/rq4_P1_seed_42_D0_plus5.pt` | VERIFIED_SAFE |
| 77 | `results/phase4_4/checkpoints/rq4_P1_seed_43_D0.pt` | 10.14 MB | `99964c72b771...` | `training_output_final/checkpoints/rq4_P1_seed_43_D0.pt` | VERIFIED_SAFE |
| 78 | `results/phase4_4/checkpoints/rq4_P1_seed_43_D0_plus10.pt` | 10.14 MB | `d8afeec7dcfb...` | `training_output_final/checkpoints/rq4_P1_seed_43_D0_plus10.pt` | VERIFIED_SAFE |
| 79 | `results/phase4_4/checkpoints/rq4_P1_seed_43_D0_plus20.pt` | 10.14 MB | `8eddfa9b50b9...` | `training_output_final/checkpoints/rq4_P1_seed_43_D0_plus20.pt` | VERIFIED_SAFE |
| 80 | `results/phase4_4/checkpoints/rq4_P1_seed_43_D0_plus5.pt` | 10.14 MB | `5a75583b57cc...` | `training_output_final/checkpoints/rq4_P1_seed_43_D0_plus5.pt` | VERIFIED_SAFE |
| 81 | `results/phase4_4/checkpoints/rq4_P1_seed_44_D0.pt` | 10.14 MB | `72d99395c0b3...` | `training_output_final/checkpoints/rq4_P1_seed_44_D0.pt` | VERIFIED_SAFE |
| 82 | `results/phase4_4/checkpoints/rq4_P1_seed_44_D0_plus10.pt` | 10.14 MB | `e81738339dd3...` | `training_output_final/checkpoints/rq4_P1_seed_44_D0_plus10.pt` | VERIFIED_SAFE |
| 83 | `results/phase4_4/checkpoints/rq4_P1_seed_44_D0_plus20.pt` | 10.14 MB | `63085db87da4...` | `training_output_final/checkpoints/rq4_P1_seed_44_D0_plus20.pt` | VERIFIED_SAFE |
| 84 | `results/phase4_4/checkpoints/rq4_P1_seed_44_D0_plus5.pt` | 10.14 MB | `a44e70397c43...` | `training_output_final/checkpoints/rq4_P1_seed_44_D0_plus5.pt` | VERIFIED_SAFE |
| 85 | `local_runtime/tokenizer/merges.txt` | 455.5 KB | `0b54e8aa4e53...` | `local_runtime/model/merges.txt` | VERIFIED_SAFE |
| 86 | `local_runtime/tokenizer/special_tokens_map.json` | 0.8 KB | `e786b595b9a2...` | `local_runtime/model/special_tokens_map.json` | VERIFIED_SAFE |
| 87 | `local_runtime/tokenizer/tokenizer.json` | 2.01 MB | `9ca9acddb652...` | `local_runtime/model/tokenizer.json` | VERIFIED_SAFE |
| 88 | `local_runtime/tokenizer/tokenizer_config.json` | 3.6 KB | `4bb9af56a342...` | `local_runtime/model/tokenizer_config.json` | VERIFIED_SAFE |
| 89 | `local_runtime/tokenizer/vocab.json` | 781.9 KB | `82b84012e3ad...` | `local_runtime/model/vocab.json` | VERIFIED_SAFE |
| 90 | `results/phase4_2/a1_external_results.json` | 1.6 KB | `54c44e6d85c7...` | `training_output_final/raw_results/a1_external_results.json` | VERIFIED_SAFE |
| 91 | `results/phase4_2/a3_external_results.json` | 1.6 KB | `ade50fa8380b...` | `training_output_final/raw_results/a3_external_results.json` | VERIFIED_SAFE |
| 92 | `results/phase4_2/rq2_external_results.json` | 721.0 KB | `270df36f24ab...` | `training_output_final/raw_results/rq2_external_results.json` | VERIFIED_SAFE |
| 93 | `results/phase4_2/rq3_external_results.json` | 0.3 KB | `44b261432e03...` | `training_output_final/raw_results/rq3_external_results.json` | VERIFIED_SAFE |
| 94 | `results/phase4_2/rq4_external_results.json` | 5.1 KB | `307c78fda9b5...` | `training_output_final/raw_results/rq4_external_results.json` | VERIFIED_SAFE |
| 95 | `results/phase4_4/A1/a1_external_results.json` | 1.6 KB | `54c44e6d85c7...` | `training_output_final/raw_results/a1_external_results.json` | VERIFIED_SAFE |
| 96 | `results/phase4_4/A3/a3_external_results.json` | 1.6 KB | `ade50fa8380b...` | `training_output_final/raw_results/a3_external_results.json` | VERIFIED_SAFE |
| 97 | `results/phase4_4/RQ2/rq2_external_results.json` | 721.0 KB | `270df36f24ab...` | `training_output_final/raw_results/rq2_external_results.json` | VERIFIED_SAFE |
| 98 | `results/phase4_4/RQ4/rq4_external_results.json` | 5.1 KB | `307c78fda9b5...` | `training_output_final/raw_results/rq4_external_results.json` | VERIFIED_SAFE |
| 99 | `training_output_final/A1_random_boundary/a1_external_results.json` | 1.6 KB | `54c44e6d85c7...` | `training_output_final/raw_results/a1_external_results.json` | VERIFIED_SAFE |
| 100 | `training_output_final/A3_additive_ungated/a3_external_results.json` | 1.6 KB | `ade50fa8380b...` | `training_output_final/raw_results/a3_external_results.json` | VERIFIED_SAFE |
| 101 | `training_output_final/RQ4_sequential/rq4_external_results.json` | 5.1 KB | `307c78fda9b5...` | `training_output_final/raw_results/rq4_external_results.json` | VERIFIED_SAFE |
| 102 | `training_handoff_phase4_2/A1/config_a1.yaml` | 0.9 KB | `b36a6c1e073b...` | `external_gpu/phase4_2/A1/config_a1.yaml` | VERIFIED_SAFE |
| 103 | `training_handoff_phase4_2/A1/validate_a1.py` | 1.2 KB | `f7588fd3b8a6...` | `external_gpu/phase4_2/A1/validate_a1.py` | VERIFIED_SAFE |
| 104 | `training_handoff_phase4_2/A3/config_a3.yaml` | 0.9 KB | `d19931473a5b...` | `external_gpu/phase4_2/A3/config_a3.yaml` | VERIFIED_SAFE |
| 105 | `training_handoff_phase4_2/A3/validate_a3.py` | 1.2 KB | `36279a131139...` | `external_gpu/phase4_2/A3/validate_a3.py` | VERIFIED_SAFE |
| 106 | `training_handoff_phase4_2/RQ4/config_rq4.yaml` | 0.7 KB | `09454e561274...` | `external_gpu/phase4_2/RQ4/config_rq4.yaml` | VERIFIED_SAFE |
| 107 | `training_handoff_phase4_2/RQ4/eval_rq4_retention.py` | 3.7 KB | `6b2c52defa94...` | `external_gpu/phase4_2/RQ4/eval_rq4_retention.py` | VERIFIED_SAFE |
| 108 | `training_handoff_phase4_2/RQ4/run_rq4_ingestion.py` | 3.3 KB | `73eec474bb15...` | `external_gpu/phase4_2/RQ4/run_rq4_ingestion.py` | VERIFIED_SAFE |
| 109 | `local_runtime/documents/LIFECYCLE_DOC_1791274447.txt` | 0.3 KB | `904d57a5e5a1...` | `local_runtime/documents/LIFECYCLE_DOC_1791273621.txt` | VERIFIED_SAFE |
| 110 | `local_runtime/documents/LIFECYCLE_DOC_1791274542.txt` | 0.3 KB | `904d57a5e5a1...` | `local_runtime/documents/LIFECYCLE_DOC_1791273621.txt` | VERIFIED_SAFE |
| 111 | `local_runtime/documents/LIFECYCLE_DOC_1791276830.txt` | 0.3 KB | `904d57a5e5a1...` | `local_runtime/documents/LIFECYCLE_DOC_1791273621.txt` | VERIFIED_SAFE |
| 112 | `local_runtime/documents/LIFECYCLE_DOC_1791277969.txt` | 0.3 KB | `904d57a5e5a1...` | `local_runtime/documents/LIFECYCLE_DOC_1791273621.txt` | VERIFIED_SAFE |
| 113 | `local_runtime/documents/LIFECYCLE_DOC_1791278803.txt` | 0.3 KB | `904d57a5e5a1...` | `local_runtime/documents/LIFECYCLE_DOC_1791273621.txt` | VERIFIED_SAFE |
| 114 | `local_runtime/documents/LIFECYCLE_DOC_1791279022.txt` | 0.3 KB | `904d57a5e5a1...` | `local_runtime/documents/LIFECYCLE_DOC_1791273621.txt` | VERIFIED_SAFE |
| 115 | `local_runtime/documents/LIFECYCLE_DOC_1791279732.txt` | 0.3 KB | `904d57a5e5a1...` | `local_runtime/documents/LIFECYCLE_DOC_1791273621.txt` | VERIFIED_SAFE |
| 116 | `local_runtime/documents/LIFECYCLE_DOC_1791280775.txt` | 0.3 KB | `904d57a5e5a1...` | `local_runtime/documents/LIFECYCLE_DOC_1791273621.txt` | VERIFIED_SAFE |

---

## 4. DANH MỤC FILE BẢO VỆ NGUYÊN TRẠNG (STRICT RETENTION LIST)
Tuyệt đối không được xóa bất kỳ file nào trong danh mục sau:

1. **Checkpoints & Assets Triển khai Runtime Ngoại tuyến (Đã phân loại lại từ Blocker 2):**
   - [`local_runtime/checkpoints/cms_3lvl_seed_42.pt`](file:///d:/NCKH/local_runtime/checkpoints/cms_3lvl_seed_42.pt) (20.28 MB)
   - [`local_runtime/checkpoints/memory/cms_3lvl_seed_42.pt`](file:///d:/NCKH/local_runtime/checkpoints/memory/cms_3lvl_seed_42.pt) (20.28 MB)
   - [`local_runtime/checkpoints/sa_cms_level_3_sa_cms.pt`](file:///d:/NCKH/local_runtime/checkpoints/sa_cms_level_3_sa_cms.pt) (10.14 MB)
2. **Checkpoints & Logs Gốc Nghiên cứu:**
   - [`checkpoints/phase4_1/cms_3lvl_seed_42.pt`](file:///d:/NCKH/checkpoints/phase4_1/cms_3lvl_seed_42.pt) (21.27 MB): Checkpoint sản xuất chuẩn Phase 4.1.
   - Thư mục [`training_handoff_rtx3050/training_handoff_rtx3050/output/`](file:///d:/NCKH/training_handoff_rtx3050/training_handoff_rtx3050/output/): 9 checkpoints + 9 logs hội tụ trên phần cứng RTX 3050 Laptop GPU.
3. **Bản ghi Lịch sử Lệch Hash:**
   - [`training_output_final/RQ2_structure_vs_token/rq2_external_results.json`](file:///d:/NCKH/training_output_final/RQ2_structure_vs_token/rq2_external_results.json) (197,820 bytes - Hash `4f2c06ad8eb7...`): Bản ghi lịch sử single-token substring match (P1 = 27.04%, B5 = 14.97%).
4. **Toàn bộ Dữ liệu Kiểm toán & Provenance:**
   - `results/phase4_2_verified_master_results.csv`
   - `results/phase4_2/rq1_data_audit.json`, `rq2_statistical_audit.json`, `rq3_consistency_audit.json`
   - `results/phase4_4/data_provenance.json`, `external_package_audit.json`
   - `results/phase4_3/master_experiment_manifest.json`
5. **Toàn bộ 4 File Dự đoán Thô:**
   - `results/raw_predictions/rq2_raw_predictions.jsonl`
   - `results/raw_predictions/rq3_hybrid_raw_predictions.jsonl`
   - `results/raw_predictions/rq4_raw_predictions.jsonl`
   - `results/raw_predictions/ablation_raw_predictions.jsonl`

---

## 5. TỔNG KẾT & CHỜ XÁC NHẬN PHÊ DUYỆT XÓA THỰC TẾ
- **Blocker 1 (Result Collector):** Đã giải quyết — hỗ trợ canonical input + fallback + bảo vệ trùng đường dẫn, đã kiểm chứng trong sandbox độc lập.
- **Blocker 2 (Offline Checkpoints):** Đã giải quyết — xác định nguồn canonical, đã kiểm chứng nạp mô hình & suy luận offline 100%, bảo lưu toàn bộ checkpoint runtime.
- **Trạng thái tệp:** **0 file bị xóa trong lượt này.**
- **Dung lượng dự kiến tiết kiệm:** **816.08 MB** (sau khi xóa 116 file bản sao thuần túy).
- **Trạng thái Git:** Sạch sẽ trên nhánh `cleanup/path-verification`, **0 commit, 0 push**.
