# BÁO CÁO PHASE 3.0 — HYBRID MEMORY + RETRIEVAL FOUNDATION

**Dự án**: Chatbot hỏi đáp trên tài liệu với bộ nhớ đa thang dựa trên Nested Learning  
**Ngày hoàn thành**: 02/10/2026  
**Backbone**: SmolLM2-135M (134.5M params, frozen)  
**Đề cương đối chiếu**: `de_cuong_chatbot_nested_learning.docx`  

---

## 1. MỤC TIÊU VÀ TRẠNG THÁI

| Mục tiêu | Trạng thái |
|:---|:---:|
| Kiến trúc P2 (Hybrid Memory + Retrieval) | ✅ DONE |
| Document Store với versioning | ✅ DONE |
| BM25 Retrieval baseline | ✅ DONE |
| Evidence selection + Citation traceability | ✅ DONE |
| Refusal controller | ✅ DONE |
| 3 chế độ QA (Context / Memory / Hybrid) | ✅ DONE |
| Faithfulness metric interfaces | ✅ DONE |
| Unit tests | ✅ 41/41 PASSED |
| Smoke test (CLI) | ✅ 10/10 PASSED |
| Documentation | ✅ DONE |

---

## 2. CÁC MODULE ĐÃ TRIỂN KHAI

### 2.1 Document Store (`src/hybrid_qa/document_store.py`)
- CRUD operations: add, get, update, remove, list
- Versioning: immutable version chain (v1 → v2 → ...)
- Content hashing (SHA-256 truncated)
- Passage storage với DOC{id}::P{idx} IDs
- SA-CMS memory snapshot linkage (document_id + version)
- Filesystem/JSON backend (đơn giản, tái lập)

### 2.2 Chunker (`src/hybrid_qa/chunker.py`)
- Sentence-aware chunking (ưu tiên ranh giới câu)
- Fixed-size fallback chunking
- Configurable overlap
- Tự động gán passage_id: `DOC{id}::P{idx:03d}`
- Section title detection cho mỗi passage

### 2.3 BM25 Retriever (`src/hybrid_qa/retriever.py`)
- Pure Python BM25 (k1=1.5, b=0.75) — không dependency ngoài
- Deterministic retrieval (cùng query → cùng kết quả)
- Trả về `RetrievalResult` với full provenance
- Incremental index update

### 2.4 Evidence & Citation (`src/hybrid_qa/evidence.py`)
- `EvidenceSelector`: lọc theo score threshold + top-k
- `EvidencePackage`: đóng gói evidence + sufficiency flag
- `CitationChecker`: kiểm tra truy vết cấu trúc (passage_id → document)
- Không auto-claim "faithful"

### 2.5 Refusal Controller (`src/hybrid_qa/refusal.py`)
- 3 lý do từ chối: NO_EVIDENCE, LOW_CONFIDENCE, INSUFFICIENT_COVERAGE
- Configurable thresholds (score, count)
- Phân biệt "retriever không tìm thấy" và "evidence không đủ mạnh"
- Structured `RefusalDecision` output

### 2.6 Pipeline (`src/hybrid_qa/pipeline.py`)
- 3 chế độ theo đề cương:
  - **MODE A (Context)**: full document trong context
  - **MODE B (Memory)**: SA-CMS memory-only
  - **MODE C (Hybrid)**: memory + retrieval + citation/refusal
- Document ingestion vào SA-CMS
- Memory snapshot save/load
- Pluggable components cho B1/B2/B5/P1/P2

### 2.7 Faithfulness Metrics (`src/hybrid_qa/faithfulness.py`)
- `FaithfulnessEvaluation`: machine-readable evaluation result
- Token overlap score
- Citation validity check
- Refusal analysis (correct refusal, false refusal)
- Aggregate metrics computation
- Không auto-claim faithfulness

---

## 3. TEST RESULTS

### 3.1 Unit Tests

```
python -m pytest tests/test_hybrid_qa.py -v
============================= 41 passed in 2.82s ==============================
```

| Test Suite | Tests | Result |
|:---|:---:|:---:|
| TestDocumentStore | 9 | 9/9 PASSED |
| TestDocumentChunker | 4 | 4/4 PASSED |
| TestBM25Retriever | 7 | 7/7 PASSED |
| TestEvidenceSelector | 4 | 4/4 PASSED |
| TestRefusalController | 4 | 4/4 PASSED |
| TestHybridQAPipeline | 5 | 5/5 PASSED |
| TestFaithfulnessEvaluator | 5 | 5/5 PASSED |
| TestMemorySnapshotRestore | 3 | 3/3 PASSED |
| **TOTAL** | **41** | **41/41** |

### 3.2 Smoke Test

```
python run_hybrid_qa.py smoke
SMOKE TEST RESULT: 10/10 PASSED
```

| Test | Description | Result |
|:---:|:---|:---:|
| 1 | Document ingestion (2 docs, 6 passages) | PASS |
| 2 | BM25 retrieval (top score: 2.32) | PASS |
| 3 | Evidence selection (3 passages, sufficient) | PASS |
| 4 | Refusal for off-topic question | PASS |
| 5 | Answer for in-topic question | PASS |
| 6 | Full hybrid pipeline | PASS |
| 7 | Citation traceability | PASS |
| 8 | Faithfulness evaluation | PASS |
| 9 | Document versioning | PASS |
| 10 | Memory snapshot save/restore | PASS |

---

## 4. CLI COMMANDS

```bash
# Ingest a document
python run_hybrid_qa.py ingest --doc-path path/to/doc.txt --title "My Document"

# Query in hybrid mode
python run_hybrid_qa.py query --question "What is CMS?" --mode hybrid

# Query in context mode (with full document)
python run_hybrid_qa.py query --question "What is CMS?" --mode context --document-id DOC001

# Query in memory-only mode
python run_hybrid_qa.py query --question "What is CMS?" --mode memory

# List documents
python run_hybrid_qa.py list

# Run smoke test
python run_hybrid_qa.py smoke

# With SA-CMS model (requires GPU)
python run_hybrid_qa.py --use-model ingest --doc-path paper.txt
python run_hybrid_qa.py --use-model query --question "What is CMS?" --mode hybrid
```

---

## 5. ĐỐI CHIẾU VỚI ĐỀ CƯƠNG

| Yêu cầu đề cương (Mục 6.5 / Phương án B) | Implementation | Trạng thái |
|:---|:---|:---:|
| Retrieval branch (RAG external evidence) | BM25Retriever | ✅ |
| SA-CMS parametric memory branch | PretrainedHopeLM + CMS | ✅ (từ Phase 2) |
| Bộ giải mã có cổng kiểm tra căn cứ | RefusalController + EvidenceSelector | ✅ |
| Trả lời kèm trích dẫn [Doc ID, Section] | Citation system (DOC{id}::P{idx}) | ✅ |
| Từ chối khi không đủ bằng chứng | RefusalController (3 reasons) | ✅ |
| 3 chế độ trả lời | MODE A/B/C | ✅ |
| Corpus management | DocumentStore + versioning | ✅ |

---

## 6. CÂU LỆNH ĐÃ CHẠY

```bash
# Unit tests
python -m pytest tests/test_hybrid_qa.py -v --tb=short
# Result: 41 passed in 2.82s

# Smoke test
python run_hybrid_qa.py smoke
# Result: 10/10 PASSED
```

---

## 7. TRẠNG THÁI KHOA HỌC

> **Phase 3.0 chỉ chứng minh: "pipeline đã được triển khai và có thể kiểm thử."**
>
> Chưa có claim nào về hiệu năng tương đối giữa B1/B2/B5/P1/P2.
> Benchmark controlled sẽ được thực hiện ở Phase 4.

---

## 8. FILES CHÍNH THỨC

| File | Mô tả |
|:---|:---|
| `src/hybrid_qa/__init__.py` | Package init |
| `src/hybrid_qa/document_store.py` | Document Store |
| `src/hybrid_qa/chunker.py` | Document Chunker |
| `src/hybrid_qa/retriever.py` | BM25 Retriever |
| `src/hybrid_qa/evidence.py` | Evidence + Citation |
| `src/hybrid_qa/refusal.py` | Refusal Controller |
| `src/hybrid_qa/pipeline.py` | Hybrid QA Pipeline |
| `src/hybrid_qa/faithfulness.py` | Faithfulness Metrics |
| `tests/test_hybrid_qa.py` | Unit Tests (41 tests) |
| `run_hybrid_qa.py` | CLI Entry Point |
| `results/phase3_0_smoke_test.json` | Smoke Test Results |
| `docs/architecture_phase3.md` | Architecture Documentation |
| `docs/phase3_0_hybrid_foundation.md` | This Report |

---

**PHASE 3.0 HOÀN THÀNH. CHỜ REVIEW TRƯỚC KHI CHUYỂN SANG PHASE 4.**
