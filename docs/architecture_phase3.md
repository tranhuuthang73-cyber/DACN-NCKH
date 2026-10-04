# KIẾN TRÚC PHASE 3 — HYBRID MEMORY + RETRIEVAL

**Dự án**: Chatbot hỏi đáp trên tài liệu với bộ nhớ đa thang dựa trên Nested Learning  
**Phase**: 3.0 — Hybrid Foundation  
**Backbone**: SmolLM2-135M (frozen)  
**Paper gốc**: arXiv:2512.24695v1  

---

## 1. TỔNG QUAN KIẾN TRÚC

```
┌─────────────────────────────────────────────────────┐
│                    USER QUERY                       │
└─────────────────┬───────────────────────────────────┘
                  │
    ┌─────────────▼──────────────┐
    │      HybridQAPipeline      │
    │   (Orchestrator / Router)  │
    └──┬──────────┬──────────┬───┘
       │          │          │
   MODE A     MODE B     MODE C
  Context    Memory     Hybrid
       │          │          │
       ▼          ▼          ▼
┌──────────┐ ┌────────┐ ┌───────────────┐
│ Document │ │ SA-CMS │ │ SA-CMS Memory │
│ in       │ │ Memory │ │ +             │
│ Context  │ │ Only   │ │ BM25 Retrieval│
│          │ │        │ │ +             │
│          │ │        │ │ Evidence      │
│          │ │        │ │ +             │
│          │ │        │ │ Citation      │
│          │ │        │ │ +             │
│          │ │        │ │ Refusal       │
└──────┬───┘ └───┬────┘ └──────┬────────┘
       │         │             │
       └─────────┴─────────────┘
                  │
    ┌─────────────▼──────────────┐
    │      AnswerGenerator       │
    │    (SmolLM2-135M + CMS)    │
    └─────────────┬──────────────┘
                  │
    ┌─────────────▼──────────────┐
    │   QAResult + Citation(s)   │
    │   or Refusal               │
    └────────────────────────────┘
```

---

## 2. MODULE MAP

| Module | File | Chức năng |
|:---|:---|:---|
| **DocumentStore** | `src/hybrid_qa/document_store.py` | Quản lý kho tài liệu: CRUD, versioning, passage storage, memory snapshot |
| **DocumentChunker** | `src/hybrid_qa/chunker.py` | Chia tài liệu thành passages có ID duy nhất (DOC{id}::P{idx}) |
| **BM25Retriever** | `src/hybrid_qa/retriever.py` | Retrieval baseline BM25 thuần Python, không dependency ngoài |
| **EvidenceSelector** | `src/hybrid_qa/evidence.py` | Lọc passages theo score threshold, đóng gói thành EvidencePackage |
| **CitationChecker** | `src/hybrid_qa/evidence.py` | Kiểm tra truy vết citation: passage_id → document_id → version |
| **RefusalController** | `src/hybrid_qa/refusal.py` | Quyết định answer/refuse dựa trên chất lượng evidence |
| **HybridQAPipeline** | `src/hybrid_qa/pipeline.py` | Orchestrator 3 chế độ: Context, Memory, Hybrid |
| **FaithfulnessEvaluator** | `src/hybrid_qa/faithfulness.py` | Evaluation interfaces: overlap, citation validity, refusal analysis |

### Module đã có từ Phase 1-2 (không sửa đổi):

| Module | File | Vai trò |
|:---|:---|:---|
| PretrainedHopeLM | `src/hope_attention/pretrained_hope.py` | Backbone + CMS adapter |
| ContinuumMemorySystem | `src/cms/continuum_memory.py` | Multi-level memory (Eq 71) |
| StructureAlignedSchedule | `src/hope_attention/sa_cms.py` | SA-CMS update scheduling |
| DocumentStructureParser | `src/document_structure/parser.py` | Structural parsing |
| TextGenerator | `src/inference/generator.py` | Autoregressive generation |

---

## 3. DATA FLOW

### 3.1 Document Ingestion Flow

```
Text File
    │
    ▼
DocumentStore.add_document()
    │
    ├── DocumentRecord (document_id, version, content_hash)
    │
    ▼
DocumentChunker.chunk_document()
    │
    ├── List[Passage] with DOC{id}::P{idx} IDs
    │
    ▼
BM25Retriever.build_index()
    │
    ├── BM25 inverted index
    │
    ▼ (optional, requires GPU)
HybridQAPipeline.ingest_document()
    │
    ├── SA-CMS online gradient updates (Eq 71)
    │
    ▼
DocumentStore.save_memory_snapshot()
    │
    └── {document_id}_v{version}.pt
```

### 3.2 Query Flow (Hybrid Mode C)

```
Question
    │
    ▼
BM25Retriever.retrieve(query, top_k=5)
    │
    ├── List[RetrievalResult] with scores
    │
    ▼
EvidenceSelector.select_evidence()
    │
    ├── EvidencePackage with Citation objects
    │
    ▼
RefusalController.decide()
    │
    ├── REFUSAL → return refusal message
    │
    └── ANSWER ──▼
                 │
    Build prompt with evidence passages
                 │
                 ▼
    AnswerGenerator (backbone forward)
                 │
                 ▼
    QAResult {
        answer: "...",
        citations: ["DOC001::P003", ...],
        refused: false,
        confidence: 0.85
    }
```

---

## 4. PASSAGE ID FORMAT

Mọi passage đều có ID duy nhất theo format:

```
{document_id}::P{index:03d}

Ví dụ:
DOC001::P000    (đoạn đầu tiên của tài liệu 1)
DOC001::P003    (đoạn thứ 4 của tài liệu 1)
DOC002::P001    (đoạn thứ 2 của tài liệu 2)
```

Citation traceability:
```
answer
  → cited passage_id (DOC001::P003)
    → document_id (DOC001)
      → version (v1)
        → content_hash (a02a7cbf...)
```

---

## 5. CẤU HÌNH THÍ NGHIỆM (cho Phase 4)

| Config | Memory | Retrieval | Mode |
|:---|:---:|:---:|:---|
| **B1** | ❌ | ❌ | ICL baseline (document in context) |
| **B2** | ❌ | ✅ BM25 | RAG baseline |
| **B5** | ✅ Fixed-Token CMS | ❌ | Memory-only CMS |
| **P1** | ✅ SA-CMS | ❌ | Memory-only SA-CMS |
| **P2** | ✅ SA-CMS | ✅ BM25 | **Hybrid (main proposal)** |

Bật/tắt thành phần qua constructor args của `HybridQAPipeline`.

---

## 6. GIẢ ĐỊNH VÀ HẠN CHẾ BIẾT TRƯỚC

### Giả định:
1. BM25 là retriever khởi đầu. Dense retriever có thể thêm sau nhưng KHÔNG bắt buộc cho Phase 3.
2. Answer generation dùng greedy decoding từ backbone. Chất lượng answer phụ thuộc vào backbone 135M.
3. Refusal threshold là configurable và cần được hiệu chỉnh trên validation set ở Phase 4.
4. Memory snapshot gắn với (document_id, version) cụ thể.

### Hạn chế đã biết:
1. Backbone 135M có năng lực sinh ngôn ngữ hạn chế — answer quality sẽ thấp so với mô hình lớn.
2. BM25 là lexical matching — không bắt semantic similarity.
3. Faithfulness evaluator dùng token overlap (thô) — KHÔNG thay thế human evaluation hay NLI-based judge.
4. Pipeline chưa xử lý multi-document reasoning (nhiều tài liệu cùng lúc).
5. Chưa có answer post-processing hay hallucination detection nâng cao.

---

## 7. TRẠNG THÁI KHOA HỌC

> [!IMPORTANT]
> Phase 3.0 chỉ chứng minh: **"pipeline đã được triển khai và có thể kiểm thử."**
>
> Không có claim nào về:
> - "Hybrid tốt hơn RAG"
> - "SA-CMS cải thiện faithfulness"  
> - "P2 vượt B2"
>
> Các claim trên chỉ được đưa ra sau khi có thực nghiệm controlled ở Phase 4.
