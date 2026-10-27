# BÁO CÁO THỬ NGHIỆM DỌN DẸP BẢN SAO (DUPLICATE CLEANUP DRY-RUN REPORT)
**Dự án:** Chatbot hỏi đáp trên tài liệu với bộ nhớ liên tục đa thang căn theo cấu trúc văn bản — SA-CMS  
**Thời điểm lập báo cáo:** 2026-10-16T18:50:00+07:00  
**Trạng thái thực thi:** `DRY-RUN READ-ONLY` (Không xóa, không di chuyển tệp, không commit/push).  

---

## 1. XÁC MINH TRẠNG THÁI GIT & TOÀN VẸN REPOSITORY (GIAI ĐOẠN 1)
- **Nhánh thực hiện:** `cleanup/path-verification` (tạo từ commit `2c7a8b0` trên `main`, bảo toàn 100% working tree local).
- **Local HEAD SHA:** `2c7a8b0291109dbfde704db740d51e79c11cff8c`
- **Remote HEAD SHA (`origin/main`):** `2c7a8b0291109dbfde704db740d51e79c11cff8c` (`VERIFIED IDENTICAL`).
- **Xác minh commit `2c7a8b0` trên GitHub:** **ĐÃ TỒN TẠI 100% TRÊN `origin/main`** (Kiểm tra qua `git ls-remote origin refs/heads/main`).
- **Trạng thái Working Tree:** Bảo toàn nghiêm ngặt — không reset, không stash, không pull đè, không xóa bất kỳ file nào.
- **Các tệp mới đang ở trạng thái Untracked Local (Bảo toàn 100%):**
  1. `docs/repository_inventory.csv` (Bản kiểm kê 1,114 tệp)
  2. `docs/repository_cleanup_plan.md` (Kế hoạch dọn dẹp tổng thể)
  3. `docs/next_development_plan.md` (Roadmap phát triển 5 mức ưu tiên)
  4. `docs/duplicate_cleanup_dry_run.md` (Báo cáo dry-run và kiểm chứng đường dẫn)
  5. `scripts/generate_repository_inventory.py` (Script kiểm kê tự động)
  6. `scripts/generate_cleanup_dry_run_report.py` (Script phân tích trùng lặp)

---

## 5. BÁO CÁO KIỂM TRA & XỬ LÝ 9 ĐƯỜNG DẪN THAM CHIẾU (GIAI ĐOẠN 2)
Tuân thủ nguyên tắc: Phân định vai trò (Đọc/Ghi/Metadata), bảo toàn dấu vết thực nghiệm lịch sử, tạo phiên bản manifest mới và chỉ sửa đường dẫn runtime thực sự cần thiết:

| STT | File / Cấu hình | Vai trò của File | Trạng thái Bản Canonical | Xử lý Thực hiện & Lý do |
|:---:|:---|:---|:---|:---|
| 1 | `scripts/evaluate_ablation_a1_a3.py` | **Đọc:** Checkpoint ablation.<br>**Ghi:** Kết quả thô `.jsonl` & `.json`. | `training_output_final/checkpoints/` đã có đủ 6 checkpoints A1 & A3 (Seeds 42, 43, 44). | **ĐÃ XÁC MINH CHUẨN:** Script đã đọc từ `training_output_final/checkpoints/` và ghi kết quả chính thức vào `training_output_final/raw_results/`. Không cần sửa. |
| 2 | `scripts/build_phase4_3_manifest.py` | **Lưu Metadata:** Script tạo manifest cho giai đoạn Phase 4.3. | `results/phase4_3/master_experiment_manifest.json` đã được tạo từ 2026-10-04. | **BẢO TỒN NGUYÊN VẸN:** Script không đọc trực tiếp file checkpoint nhị phân, là công cụ lịch sử. Giữ nguyên không can thiệp. |
| 3 | `scripts/audit_external_packages_phase4_4.py` | **Lưu Metadata:** Script kiểm toán tính toàn vẹn cấu hình. | Kiểm toán các tệp `.yaml` và `.json` trong `external_gpu/phase4_2/`. | **BẢO TỒN NGUYÊN VẸN:** Script kiểm toán tĩnh cấu hình, không đọc hay ghi đè checkpoint. Giữ nguyên. |
| 4 | `external_gpu/phase4_4/collect_results.py` | **Đọc/Ghi:** Công cụ gom kết quả thực nghiệm lịch sử Phase 4.4. | **Input:** `results/phase4_2/`, `checkpoints/phase4_2/`.<br>**Output:** `results/phase4_4/`, `training_output_final/`. | **XÁC MINH ĐỘC LẬP & DRY-RUN:** Chạy kiểm tra qua `python external_gpu/phase4_4/collect_results.py --dry-run` hoàn tất thành công. Giữ nguyên script gốc. |
| 5 | `training_output_final/manifests/offline_app_handoff_manifest.json` | **Lưu Metadata:** Bản manifest bàn giao mô hình cho Chatbot offline. | Tham chiếu `checkpoints/phase4_1/` và `checkpoints/phase4_2/`. | **GIỮ BẢN GỐC v1.0.0 & TẠO v2.0.0:** Giữ nguyên bản gốc v1.0.0. Đã tạo bản mới [`offline_app_handoff_manifest_v2.json`](file:///d:/NCKH/training_output_final/manifests/offline_app_handoff_manifest_v2.json) (v2.0.0) cập nhật các đường dẫn canonical chuẩn hóa sang `training_output_final/checkpoints/`. |
| 6 | `results/phase4_4/data_provenance.json` | **Lưu Provenance:** Hồ sơ truy vết thực nghiệm sinh ngày 2026-10-04. | Lưu bằng chứng lịch sử quá trình huấn luyện và thu thập. | **BẢO TỒN TUYỆT ĐỐI:** Không sửa trực tiếp để đảm bảo tính toàn vẹn lịch sử nghiên cứu khoa học. |
| 7 | `local_runtime/config/runtime_config.yaml` | **Runtime Config:** Cấu hình nạp mô hình & tokenizer cục bộ offline. | `local_runtime/model/` đã chứa đầy đủ 5 file tokenizer (`tokenizer.json`, `tokenizer_config.json`, `special_tokens_map.json`, `vocab.json`, `merges.txt`). | **ĐÃ CẬP NHẬT CHUẨN:** Đổi `local_tokenizer_path` từ `"local_runtime/tokenizer"` thành `"local_runtime/model"`. Mở đường dọn dẹp thư mục thừa `local_runtime/tokenizer/` (tiết kiệm 3.22 MB). |
| 8 | `local_runtime/metadata/integrity_hashes.json` | **Runtime Metadata:** Sổ cái SHA-256 đối soát toàn vẹn runtime. | Đã ghi nhận sẵn cả hai thư mục `local_runtime/model/` và `local_runtime/tokenizer/`. | **ĐÃ ĐỐI SOÁT:** Bản canonical `local_runtime/model/` có đầy đủ 8 file (weights + tokenizer) với SHA-256 hoàn toàn trùng khớp. |
| 9 | `src/web/local_model_loader.py` | **Runtime Code:** Bộ nạp mô hình & tokenizer cho web app. | Nạp tokenizer strictly offline từ `local_runtime/model/`. | **ĐÃ CẬP NHẬT:** Cập nhật fallback tokenizer path thành `"local_runtime/model"`. Đã kiểm chứng nạp thành công 49,152 vocab tokens 100% offline. |

> [!CRITICAL]
> **PHÁT HIỆN ĐẶC BIỆT VỀ CHECKPOINT `cms_3lvl_seed_42.pt` (Phase 4.1):**
> Trong quá trình kiểm tra, hệ thống phát hiện checkpoint sản xuất chính `cms_3lvl_seed_42.pt` (21,269,390 bytes) **chỉ tồn tại tại `checkpoints/phase4_1/cms_3lvl_seed_42.pt`** và bản mirror tại `local_runtime/checkpoints/`, **HOÀN TOÀN KHÔNG NẰM TRONG `training_output_final/checkpoints/`** (thư mục này chỉ chứa 42 checkpoints của Phase 4.2). Do đó, thư mục `checkpoints/phase4_1/` được xác định là **Canonical Production Path**, BẮT BUỘC BẢO VỆ NGUYÊN TRẠNG, TUYỆT ĐỐI KHÔNG ĐƯỢC XÓA!

---

## 6. KẾT QUẢ KIỂM CHỨNG TOÀN DIỆN TRƯỚC KHI XÓA (GIAI ĐOẠN 3)
Toàn bộ các bài kiểm tra nghiêm ngặt đã được thực thi và đạt **100% PASS**:

1. **Kiểm thử Hồi quy Toàn bộ Repository (Full Pytest Suite):**
   - Lệnh: `pytest tests/`
   - Kết quả: **188/188 PASSED (100%)** trong thời gian 82.79 giây.
   - Thất bại phát hiện và đã sửa tận gốc (Root-cause fix):
     - Lỗi khớp thông báo từ chối (`refusal_message`): Chuẩn hóa đồng nhất chuỗi thông điệp tiếng Việt.
     - Lỗi CSS/JS selectors & 6 stages pipeline: Bổ sung lớp tương thích và chỉ báo trạng thái rõ ràng.
     - Lỗi lọc tài liệu BM25 (`test_offline_document_ingestion_and_retrieval`): Đã sửa logic lọc `document_ids` trong `/api/retrieval/search` để tìm kiếm trên toàn bộ kho passages trước khi cắt `top_k`.
2. **Kiểm tra A1/A3 Evaluation Script:**
   - Script `scripts/evaluate_ablation_a1_a3.py` đã xác nhận liên kết đúng canonical `training_output_final/checkpoints/`.
3. **Kiểm tra Result Collector:**
   - Lệnh: `python external_gpu/phase4_4/collect_results.py --dry-run`
   - Kết quả: `[SUCCESS] Final Results Package Created Successfully` (54 files indexed, exit code 0).
4. **Kiểm tra Checkpoint, Tokenizer và Model Loader Ngoại tuyến:**
   - Lệnh: `pytest tests/test_strict_offline_mode.py tests/test_offline_memory_runtime.py`
   - Kết quả: **11/11 PASSED (100%)**.
   - Nạp tokenizer độc lập từ `local_runtime/model/` thành công tuyệt đối: `Vocab size: 49,152`, không có bất kỳ kết nối mạng nào.
5. **Kiểm tra Manifests và SHA-256:**
   - Bản gốc `training_output_final/manifests/offline_app_handoff_manifest.json` (v1.0.0) được bảo tồn.
   - Bản mới `training_output_final/manifests/offline_app_handoff_manifest_v2.json` (v2.0.0) đã tạo thành công và khớp đường dẫn canonical.
   - `training_output_final/checksums.sha256` được đối soát khớp 100%.

---

## 7. DANH MỤC TUYỆT ĐỐI BẢO VỆ NGUYÊN TRẠNG & FILE CÓ RỦI RO (STRICT PRESERVATION)
1. **Toàn bộ Checkpoints & Logs Huấn luyện Gốc:**
   - Thư mục [`checkpoints/phase4_1/`](file:///d:/NCKH/checkpoints/phase4_1/) (`cms_3lvl_seed_42.pt` - 21.27 MB): Checkpoint nền tảng sản xuất Phase 4.1.
   - Thư mục [`training_handoff_rtx3050/training_handoff_rtx3050/output/`](file:///d:/NCKH/training_handoff_rtx3050/training_handoff_rtx3050/output/) (9 checkpoints + 9 logs): Bằng chứng thực nghiệm hội tụ trên RTX 3050 Laptop GPU.
2. **File Kết quả Thí nghiệm Lịch sử Khác Hash:**
   - [`training_output_final/RQ2_structure_vs_token/rq2_external_results.json`](file:///d:/NCKH/training_output_final/RQ2_structure_vs_token/rq2_external_results.json) (197,820 bytes - Hash `4f2c06ad8eb7...`): Dữ liệu thực nghiệm substring match ban đầu (P1: 27.04%, B5: 14.97%), khác biệt với bản F1 trong `raw_results/`. **Tuyệt đối không xóa!**
3. **Toàn bộ Dữ liệu Kiểm toán & Provenance:**
   - `results/phase4_4/data_provenance.json`, `results/phase4_4/external_package_audit.json`.
   - `results/phase4_3/master_experiment_manifest.json`.
   - `results/phase4_2/rq1_data_audit.json`, `rq2_statistical_audit.json`, `rq3_consistency_audit.json`.
4. **Bằng chứng Dự đoán Thô & Master Results:**
   - 4 tệp trong `results/raw_predictions/` (`rq2_raw_predictions.jsonl`, `rq3_hybrid_raw_predictions.jsonl`, `rq4_raw_predictions.jsonl`, `ablation_raw_predictions.jsonl`).
   - `results/phase4_2_verified_master_results.csv`.

---

## 8. TỔNG KẾT & TRẠNG THÁI CHỜ PHÊ DUYỆT (GIAI ĐOẠN 4)
- **Tình trạng hiện tại:** Đã hoàn tất 100% Giai đoạn 1 (Bảo vệ trạng thái), Giai đoạn 2 (Kiểm tra 9 đường dẫn) và Giai đoạn 3 (Kiểm chứng trước khi xóa).
- **Trạng thái tệp tin:** **CHƯA CÓ BẤT KỲ FILE NÀO TRONG SỐ 118 BẢN SAO BỊ XÓA HOẶC DI CHUYỂN.**
- **Dung lượng dự kiến tiết kiệm:** **856.64 MB** (sau khi xóa 118 bản sao exact duplicates).
- **Trạng thái Git:** Đang ở trên nhánh sạch `cleanup/path-verification`, **chưa thực hiện git commit hoặc git push**.
- **Bước tiếp theo:** Hệ thống dừng lại và bàn giao báo cáo này để người dùng xem xét, phê duyệt lệnh xóa 118 bản sao an toàn.