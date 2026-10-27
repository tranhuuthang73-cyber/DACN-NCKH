# KẾ HOẠCH DỌN DẸP & TỔ CHỨC LẠI REPOSITORY (REPOSITORY CLEANUP PLAN)
**Dự án:** Chatbot hỏi đáp trên tài liệu với bộ nhớ liên tục đa thang căn theo cấu trúc văn bản — SA-CMS  
**Repository:** [https://github.com/tranhuuthang73-cyber/DACN-NCKH](https://github.com/tranhuuthang73-cyber/DACN-NCKH)  
**Commit cơ sở kiểm tra:** `a6055a488314ab350ddd2caba3039051dbabed08` (HEAD tại `2c7a8b0`)  
**Nguyên tắc cốt lõi:** Bảo toàn 100% bằng chứng khoa học, không xóa checkpoint/dữ liệu nghiên cứu trong lượt đầu tiên, loại bỏ lãng phí đĩa có kiểm soát.

---

## 1. THỐNG KÊ TỔNG QUAN KIỂM KÊ (INVENTORY SUMMARY)
Tệp kiểm kê toàn diện đã được tạo lập tại [`docs/repository_inventory.csv`](file:///d:/NCKH/docs/repository_inventory.csv) với đầy đủ 10 cột quy chuẩn: `path`, `file_type`, `size_bytes`, `sha256`, `git_tracked`, `referenced_by`, `role`, `classification`, `recommended_action`, `reason`.

### Bảng phân loại 1,214 file trước khi dọn dẹp:
| Phân loại (Classification) | Số lượng file | Tỷ lệ (%) | Định nghĩa & Nguyên tắc phân loại |
|:---|:---:|:---:|:---|
| **`KEEP_SOURCE`** | 285 | 23.5% | Mã nguồn chính (`src/`), bộ test (`tests/`), cấu hình (`configs/`), đề cương gốc, bài báo, scripts tiện ích. |
| **`KEEP_RAW_EVIDENCE`** | 254 | 20.9% | Raw predictions JSONL, logs huấn luyện phần cứng thực tế, dataset nguồn (`data/`), báo cáo kiểm toán pháp y. |
| **`KEEP_CANONICAL`** | 102 | 8.4% | Checkpoints chính thức (Phase 4.4, RTX 3050), master results CSV, checksum baseline, handoff manifests. |
| **`DUPLICATE_CANDIDATE`** | 122 | 10.0% | File trùng khớp bitwise SHA-256 với một bản canonical khác (866.79 MB dữ liệu dư thừa). |
| **`ARCHIVE_CANDIDATE`** | 98 | 8.1% | Báo cáo giai đoạn cũ (`docs/phase1-3`), pilot checkpoints cũ, tài liệu trích dẫn (`paper_text.txt`). |
| **`SAFE_DELETE`** | 258 | 21.3% | Cache bytecode (`__pycache__`, `.pyc`, `.pytest_cache`) và snapshots tạm local runtime. |
| **`UNCERTAIN`** | 95 | 7.8% | File hỗ trợ phụ trợ đang được đối soát provenance để phân loại chính xác trong giai đoạn tiếp theo. |
| **TỔNG CỘNG** | **1,214** | **100%** | **Dung lượng tổng thể: 4.084 GB (4,385,453,685 bytes)** |

---

## 2. ĐIỀU TRA CHI TIẾT CÁC VỊ TRÍ TRÙNG LẶP (PART B FORENSIC AUDIT)
Qua quét mã băm SHA-256 trên toàn bộ cây thư mục, phát hiện **66 nhóm trùng lặp nội dung hoàn toàn** tạo ra **866.79 MB** dung lượng dư thừa.

### 2.1. Nhóm Checkpoint Trùng lặp 3 Bản sao (Triplicate Checkpoints)
Hiện tại, toàn bộ 42 checkpoints cốt lõi của Phase 4.4 đang bị sao chép ở 3 thư mục song song:
1. `training_output_final/checkpoints/` (Thư mục phát hành chính thức, có mã băm trong `checksums.sha256`)
2. `results/phase4_4/checkpoints/` (Thư mục sao chép khi chạy benchmark)
3. `checkpoints/phase4_2/` (Thư mục checkpoint ban đầu của phase 4.2)

#### Danh sách chi tiết các nhóm Checkpoint trùng khớp SHA-256:
| Mã SHA-256 (Rút gọn) | Kích thước | Số bản sao | Tên tệp artifact | Các đường dẫn đang chứa bản sao |
|:---|:---:|:---:|:---|:---|
| `5c040cbc0894...` | 20.28 MB | 3 | `cms_3lvl_additive_seed_42.pt` | `training_output_final/checkpoints/`, `results/phase4_4/checkpoints/`, `checkpoints/phase4_2/A3/` |
| `3855195e47db...` | 20.28 MB | 3 | `cms_3lvl_additive_seed_43.pt` | `training_output_final/checkpoints/`, `results/phase4_4/checkpoints/`, `checkpoints/phase4_2/A3/` |
| `f386517fdac1...` | 20.28 MB | 3 | `cms_3lvl_additive_seed_44.pt` | `training_output_final/checkpoints/`, `results/phase4_4/checkpoints/`, `checkpoints/phase4_2/A3/` |
| `427ffbc147a3...` | 20.28 MB | 3 | `cms_3lvl_random_seed_42.pt` | `training_output_final/checkpoints/`, `results/phase4_4/checkpoints/`, `checkpoints/phase4_2/A1/` |
| `4401e910a466...` | 20.28 MB | 3 | `cms_3lvl_random_seed_43.pt` | `training_output_final/checkpoints/`, `results/phase4_4/checkpoints/`, `checkpoints/phase4_2/A1/` |
| `2e5b11a39711...` | 20.28 MB | 3 | `cms_3lvl_random_seed_44.pt` | `training_output_final/checkpoints/`, `results/phase4_4/checkpoints/`, `checkpoints/phase4_2/A1/` |
| `bc39ab4c6537...` | 10.14 MB | 3 | `rq4_B5_seed_42_D0_plus20.pt` | `training_output_final/checkpoints/`, `results/phase4_4/checkpoints/`, `checkpoints/phase4_2/RQ4/` |
| `18da2a754893...` | 10.14 MB | 3 | `rq4_B5_seed_43_D0_plus20.pt` | `training_output_final/checkpoints/`, `results/phase4_4/checkpoints/`, `checkpoints/phase4_2/RQ4/` |
| `6af4bba7a9d0...` | 10.14 MB | 3 | `rq4_B5_seed_44_D0_plus20.pt` | `training_output_final/checkpoints/`, `results/phase4_4/checkpoints/`, `checkpoints/phase4_2/RQ4/` |
| `51e8a03a43ed...` | 10.14 MB | 3 | `rq4_P1_seed_42_D0_plus20.pt` | `training_output_final/checkpoints/`, `results/phase4_4/checkpoints/`, `checkpoints/phase4_2/RQ4/` |
| `8eddfa9b50b9...` | 10.14 MB | 3 | `rq4_P1_seed_43_D0_plus20.pt` | `training_output_final/checkpoints/`, `results/phase4_4/checkpoints/`, `checkpoints/phase4_2/RQ4/` |
| `63085db87da4...` | 10.14 MB | 3 | `rq4_P1_seed_44_D0_plus20.pt` | `training_output_final/checkpoints/`, `results/phase4_4/checkpoints/`, `checkpoints/phase4_2/RQ4/` |
| *(Còn lại 27 snapshots RQ4)* | 3.38 – 10.14 MB | 3 | `rq4_{B4,B5,P1}_seed_{42,43,44}_*` | Tương tự: xuất hiện đồng thời ở 3 vị trí trên |

### 2.2. Nhóm Tệp JSON Kết quả Thực nghiệm Trùng lặp (Duplicate Results JSON)
- **`rq2_external_results.json` (738,303 bytes - Hash `270df36f24ab...`):**
  - Bản 1 (Canonical): `training_output_final/raw_results/rq2_external_results.json`
  - Bản 2 (Duplicate): `results/phase4_4/RQ2/rq2_external_results.json`
  - Bản 3 (Duplicate): `results/phase4_2/rq2_external_results.json`
- **`rq4_external_results.json` (5,228 bytes - Hash `307c78fda9b5...`):**
  - Bản 1 (Canonical): `training_output_final/raw_results/rq4_external_results.json`
  - Bản 2 (Duplicate): `training_output_final/RQ4_sequential/rq4_external_results.json`
  - Bản 3 (Duplicate): `results/phase4_4/RQ4/rq4_external_results.json`
  - Bản 4 (Duplicate): `results/phase4_2/rq4_external_results.json`
- **`a1_external_results.json` & `a3_external_results.json` (~1,590 bytes - Hash `54c44e6d85c7...` & `ade50fa8380b...`):**
  - Trùng lặp 4 bản sao giữa `training_output_final/raw_results/`, `training_output_final/A1_random_boundary/`, `results/phase4_4/A1/`, và `results/phase4_2/`.

### 2.3. Phát hiện Quan trọng về Tính Độc nhất của Checkpoint RTX 3050 (P1 & Baselines)
- Các checkpoint gốc được huấn luyện trực tiếp trên card **NVIDIA GeForce RTX 3050 6GB Laptop GPU** (`cms_1lvl_seed_*.pt`, `cms_2lvl_seed_*.pt`, `cms_3lvl_seed_*.pt` x 3 seeds = 9 files, ~21.27 MB/file) và 9 tệp logs JSON tương ứng **chỉ tồn tại độc nhất** trong:
  `training_handoff_rtx3050/training_handoff_rtx3050/output/checkpoints/`
- **Tuyệt đối KHÔNG có bản sao** của các checkpoint này trong `training_output_final/` hay `results/phase4_4/`. Do đó, thư mục `training_handoff_rtx3050` là **nguồn lưu trữ duy nhất và canonical** cho trọng số adapter chính thức của P1, B4 và A2!

---

## 3. VỊ TRÍ LƯU TRỮ CHÍNH THỨC (CANONICAL ARTIFACT LOCATIONS)
Để xóa bỏ tình trạng phân mảnh và mâu thuẫn giữa các bản sao, chuẩn hóa các vị trí lưu trữ chính thức như sau:

| Loại Artifact | Vị trí Lưu trữ Chính thức (Canonical Path) | Tiêu chí & Căn cứ Chứng thực |
|:---|:---|:---|
| **Checkpoints Phase 4.4 / RQ4 / Ablations** | `training_output_final/checkpoints/` | Đã khóa trong `checksums.sha256` (53/53 PASSED), có đầy đủ 42 file `.pt`. |
| **Checkpoints Gốc RTX 3050 (P1, B4, A2)** | `training_handoff_rtx3050/training_handoff_rtx3050/output/checkpoints/` | Trọng số huấn luyện gốc 150 steps trên card RTX 3050 Laptop GPU kèm log JSON. |
| **Bảng Kết quả Thực nghiệm Tổng thể** | `results/phase4_2_verified_master_results.csv` | File master đã xác minh đa token, kiểm định bootstrap và paired t-test. |
| **Raw Predictions Chi tiết (.jsonl)** | `results/raw_predictions/` | Bằng chứng dự đoán chi tiết từng câu hỏi cho RQ2, RQ3, RQ4 và Ablation. |
| **Logs Thực nghiệm Phần cứng** | `training_handoff_rtx3050/training_handoff_rtx3050/output/logs/` | Bằng chứng sử dụng VRAM đỉnh, throughput, loss giảm thực tế. |
| **Mã băm Xác thực Hệ thống** | `training_output_final/checksums.sha256` | Mã nguồn chân lý (Source of Truth) cho toàn bộ 53 artifacts cốt lõi. |
| **Manifests Handoff Chatbot Offline** | `training_output_final/manifests/` | Cấu hình nạp mô hình vào Web Demo ngoại tuyến. |

---

## 4. BẢNG ÁNH XẠ ĐƯỜNG DẪN CẦN SỬA TRƯỚC KHI LOẠI BỎ BẢN SAO (PATH CORRECTION MAPPINGS)
Trước khi xóa bỏ các bản duplicate trong `results/phase4_4/` và `checkpoints/phase4_2/`, các đường dẫn sau đây **bắt buộc phải được cập nhật** trong mã nguồn và scripts:

| File Tham chiếu Hiện tại | Dòng / Vị trí | Đường dẫn Cũ (Sắp dọn) | Đường dẫn Mới Chuẩn hóa (Canonical) |
|:---|:---|:---|:---|
| `scripts/evaluate_ablation_a1_a3.py` | Line 23-25 | `results/phase4_4/checkpoints/` | `training_output_final/checkpoints/` |
| `scripts/build_phase4_3_manifest.py` | Line 19, 34 | `checkpoints/phase4_2/` | `training_output_final/checkpoints/` |
| `scripts/audit_external_packages_phase4_4.py` | Line 45 | `results/phase4_4/` | `training_output_final/` |
| `external_gpu/phase4_4/collect_results.py` | Line 31 | `results/phase4_4/` | `training_output_final/raw_results/` |
| `training_output_final/manifests/offline_app_handoff_manifest.json` | Line 12 | `checkpoints/phase4_2/RQ4/` | `training_output_final/checkpoints/` |
| `results/phase4_4/data_provenance.json` | Line 18-24 | `checkpoints/phase4_2/` | `training_output_final/checkpoints/` |
| `src/hope_attention/sa_cms.py` (nếu có hardcode) | Default path | `checkpoints/phase4_1/` | Giữ nguyên hoặc trỏ về `training_handoff_rtx3050` |

*Lưu ý: Chỉ thực hiện xóa bản sao sau khi toàn bộ các file trên được cập nhật và kiểm thử tự động pass 100%.*

---

## 5. KẾ HOẠCH LƯU TRỮ VÀ TỔ CHỨC CÓ HỆ THỐNG (ORGANIZED ARCHIVE)
Nhằm giữ cho thư mục gốc và thư mục tài liệu tinh gọn mà không làm mất lịch sử nghiên cứu:

1. **Chuyển các báo cáo phase cũ vào `docs/archive/`:**
   - `docs/PHASE1_REPORT.md`
   - `docs/phase2_5_*.md` (3 files)
   - `docs/phase3_*.md` (8 files)
   - `docs/phase4_1_*.md` (7 files)
   - `docs/phase4_2_*.md` (4 files)
   - `docs/phase4_3_*.md` (4 files)
   - `docs/round2_*.md` (7 files)
   - `docs/phase3_2_training_pilot.md.bak`
2. **Chuyển tài liệu tham khảo và hình ảnh trích xuất vào `docs/references/`:**
   - `paper_text.txt` -> `docs/references/paper_text.txt`
   - `de_cuong_text.txt` -> `docs/references/de_cuong_text.txt`
   - `fig7_extracted/` -> `docs/references/fig7_extracted/`
3. **Chuyển các runner scripts giai đoạn thử nghiệm ban đầu vào `scripts/legacy/`:**
   - `run_phase2_5_controlled.py`
   - `run_pretrained_experiment.py`
   - `run_experiment.py`
   - `run_hybrid_qa.py`
   - `run_chatbot.py`
   - `scratch_bench.py`
   *(Đã kiểm tra không có file nào trong pipeline hiện tại `src/` hoặc `tests/` phụ thuộc vào các script này).*

---

## 6. DỌN DẸP AN TOÀN ĐÃ THỰC HIỆN (VERIFIED SAFE CLEANUP)
Trong lượt kiểm kê đầu tiên, hệ thống đã thực hiện **xóa dọn an toàn 102 tệp cache và bytecode**:
- **Đối tượng xóa:** Toàn bộ thư mục `__pycache__/`, `.pytest_cache/`, và các file nhị phân compiled `.pyc`.
- **Dung lượng đã giải phóng:** **1,090,681 bytes (~1.04 MB)**.
- **Trạng thái Git:** 100% các file đã xóa không nằm trong danh sách theo dõi của Git (`git-untracked`), working tree hoàn toàn sạch.
- **Bảo toàn dữ liệu khoa học:** Tuyệt đối không xóa bất kỳ checkpoint, raw predictions, logs hay mã nguồn nào.

### Danh mục Tuyệt đối Không được Xóa (Strict Non-Deletables):
- `de_cuong_chatbot_nested_learning.docx` & `2512.24695v1.pdf` (Tài liệu gốc đề tài)
- `src/` (Toàn bộ mã nguồn kiến trúc SA-CMS, HopeLM, Hybrid QA, Web App)
- `tests/` (Toàn bộ test suites)
- `configs/` (Cấu hình đóng băng locked_training.yaml)
- `data/` (Tập dữ liệu 200 mẫu, câu hỏi kiểm chuẩn tiếng Việt và LongHealth)
- `training_output_final/checksums.sha256` & `training_output_final/checkpoints/*.pt`
- `training_handoff_rtx3050/.../output/` (Checkpoints và logs RTX 3050 gốc)
- `results/raw_predictions/*.jsonl` (Dự đoán thô của toàn bộ câu hỏi)
- `results/phase4_2_verified_master_results.csv` (Bảng kết quả chuẩn)

---

## 7. BÁO CÁO KIỂM TOÁN TÍNH NHẤT QUÁN THỰC NGHIỆM (PART E AUDIT)
Dưới đây là kết luận pháp y chi tiết cho 6 mâu thuẫn/nghi vấn được người dùng chỉ định điều tra:

### Vấn đề 1: Độ dài ngữ cảnh (Context Length 512 vs 256)
- **Hiện trạng:** Đề cương và tài liệu kế hoạch ghi 512 tokens, nhưng log audit ghi nhận 256 tokens (`locked_training.yaml:45`).
- **Phân loại:** `EXPLAINED_BY_DIFFERENT_PROTOCOL`.
- **Giải trình khoa học:** Trên phần cứng mục tiêu là card đồ họa rời phổ thông **NVIDIA GeForce RTX 3050 6GB Laptop GPU**, việc thiết lập `max_sequence_length: 256` là giải pháp cân bằng bắt buộc để duy trì effective batch size = 4 và gradient accumulation steps = 2 mà không gây tràn bộ nhớ (Out-Of-Memory) và đảm bảo tốc độ huấn luyện đạt ~55 giây cho 150 gradient steps. Trong báo cáo chính thức, cần tuyên bố rõ ràng đây là tham số thích ứng phần cứng (hardware-constrained adaptation) thay vì che giấu.

### Vấn đề 2: Cơ chế chấm điểm RQ2 (Single-token substring vs Multi-token Token F1)
- **Hiện trạng:** Tệp kết quả cũ `rq2_external_results.json` ghi nhận cách chấm single-token, trong khi các báo cáo mới khẳng định đã chuyển sang Token F1 đa token.
- **Phân loại:** `RESOLVED`.
- **Giải trình khoa học:** 
  - Trong đợt chạy ban đầu trên GPU ngoài (`rq2_external_results.json`), script sử dụng greedy decoding lấy đúng 1 token đầu tiên (`logits[0, -1, :].argmax()`) và kiểm tra chuỗi con `ans in gt`, dẫn đến tỷ lệ chính xác bị thổi phồng (P1: 27.04%, B5: 14.97%).
  - Đợt đánh giá lại độc lập tại [`results/raw_predictions/rq2_raw_predictions.jsonl`](file:///d:/NCKH/results/raw_predictions/rq2_raw_predictions.jsonl) đã cài đặt thuật toán chuẩn học thuật SQuAD/QASPER: sinh tự do đa token (`max_new_tokens=32`), chuẩn hóa ký tự (`normalize_answer`), tính Bag-of-Words Token F1, Exact Match và Target Logprob trên toàn bộ $N = 1,140$ câu hỏi. Kết quả mới: P1 = 0.0421 ± 0.1188, B5 = 0.0036 ± 0.0202, $p = 3.03 \times 10^{-7}$ (Vẫn giữ vững ý nghĩa thống kê vượt trội của P1).

### Vấn đề 3: Phân định Huấn luyện P1 vs B5 & Ngân sách Cập nhật (Fair Budget)
- **Hiện trạng:** Cần xác nhận P1 và B5 thực sự được huấn luyện theo hai lịch cập nhật tương ứng, với ngân sách công bằng, chứ không chỉ nạp chung checkpoint rồi đổi lịch ingest khi đánh giá.
- **Phân loại:** `EXPLAINED_BY_DIFFERENT_PROTOCOL`.
- **Giải trình khoa học:**
  - Kiểm tra mã nguồn [`external_gpu/phase4_4/run_rq2.py:215-228`](file:///d:/NCKH/external_gpu/phase4_4/run_rq2.py#L215-L228) xác nhận: Cả P1 và B5 đều nạp chung bộ trọng số adapter CMS 3-tầng đã hội tụ sau 150 bước ngôn ngữ nhân quả (`cms_3lvl_seed_{s}.pt`).
  - Sự khác biệt về lịch cập nhật diễn ra **tại thời điểm nạp văn bản khi suy luận (Inference Document Ingestion)**: P1 cập nhật theo ranh giới cấu trúc văn bản (`schedule_mode="structure"`, $b_\ell(t)=1$), còn B5 cập nhật theo số token cố định (`schedule_mode="fixed_token"`, mỗi 64 tokens).
  - Cả hai phương pháp đều xử lý cùng một văn bản với cùng độ dài và cùng ngân sách token. Trong bản thảo bài báo, cần định danh chính xác đây là "Lịch cập nhật bộ nhớ trực tuyến khi nạp văn bản" (*Inference-time Online Ingestion Schedule*) chứ không tuyên bố là hai mô hình được pre-train bằng 2 optimizer schedules khác nhau.

### Vấn đề 4: Số liệu RQ2 xuất hiện nhiều con số khác nhau giữa các bảng
- **Hiện trạng:** RQ2 có nơi ghi P1 = 27.04%, nơi ghi P1 = 0.0421.
- **Phân loại:** `RESOLVED`.
- **Giải trình khoa học:** Sự chênh lệch bắt nguồn trực tiếp từ 2 hệ thước đo:
  1. Con số 27.04% là độ chính xác chuỗi con 1-token ban đầu (Legacy metric).
  2. Con số 0.0421 là Token F1 đa token chuẩn SQuAD trên 1,140 mẫu (Academic metric).
  Toàn bộ các bảng tổng hợp kết quả chính thức trong [`results/phase4_2_verified_master_results.csv`](file:///d:/NCKH/results/phase4_2_verified_master_results.csv) và [`docs/final_scientific_report.md`](file:///d:/NCKH/docs/final_scientific_report.md) đã được khóa thống nhất theo con số Token F1 học thuật (0.0421).

### Vấn đề 5: QASPER P1 có giá trị 0.2014 ở một bảng nhưng 0.0895 trong bảng tổng hợp RQ1
- **Hiện trạng:** Điểm QASPER của P1 xuất hiện 2 giá trị khác biệt lớn (0.2014 và 0.0895).
- **Phân loại:** `EXPLAINED_BY_DIFFERENT_PROTOCOL`.
- **Giải trình khoa học:**
  - Giá trị **`0.0895`** trong RQ1 được đo lường dưới giao thức **Context Eviction (Zero Document Context)**: Toàn bộ văn bản tài liệu bị đẩy ra khỏi prompt, mô hình bị ép trả lời câu hỏi chỉ bằng bộ nhớ nội tại tham số CMS đã nạp trước đó.
  - Giá trị **`0.2014`** trong bảng Ablation được đo lường dưới giao thức **Document-Grounded Ingestion**: Mô hình được nạp đầy đủ cấu trúc văn bản với adapter SA-CMS 3-tầng hoàn chỉnh có cơ chế cổng động $g_\ell(x_t)$. Hai con số phản ánh hai bài toán hoàn toàn khác nhau.

### Vấn đề 6: Giới hạn tập câu hỏi nhỏ $D_0$ trong RQ4 (10 câu hỏi)
- **Hiện trạng:** Đánh giá độ quên liên tục trên tài liệu ban đầu $D_0$ chỉ có 10 câu hỏi.
- **Phân loại:** `RESOLVED`.
- **Giải trình khoa học:**
  - Tập câu hỏi cho tài liệu $D_0$ trong `incremental_corpus.py` chỉ bao gồm 10 câu hỏi chẩn đoán (`D0_Q01` đến `D0_Q10`), dẫn đến hiện tượng lượng tử hóa 10% cho mỗi câu trả lời đúng và gây ra độ quên âm giả tạo ($F_{20} = -10\%$) khi dùng accuracy nhị phân.
  - Tệp raw predictions mới [`results/raw_predictions/rq4_raw_predictions.jsonl`](file:///d:/NCKH/results/raw_predictions/rq4_raw_predictions.jsonl) đã giải quyết triệt để vấn đề này bằng việc đo lường **Continuous Token F1** ($F_{20} = -0.0034$) và **Target Log-probability** (+0.3990 cải thiện cho P1).
  - Giới hạn $N=10$ câu hỏi của $D_0$ đã được ghi chú minh bạch trong master CSV và cần được trình bày trung thực như một giới hạn thực nghiệm trong bài báo khoa học.
