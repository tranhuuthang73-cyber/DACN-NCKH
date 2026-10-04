"""
Hybrid QA Pipeline — integrates SA-CMS memory, retrieval, evidence, and refusal
into 3 modes as specified by the research proposal:

    MODE A: Document in context → answer directly
    MODE B: Document left context → memory-only (SA-CMS)
    MODE C: Hybrid → memory + retrieved evidence → answer + citation/refusal

Design:
- Each mode uses the same backbone model and tokenizer.
- Modes are switchable for creating B1/B2/B5/P1/P2 configurations.
- Answer generation uses the existing TextGenerator with evidence-augmented prompts.
- No claim of faithfulness without evaluation evidence.
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class QAMode(Enum):
    """Three modes from the research proposal."""
    CONTEXT = "context"       # MODE A: full document in context
    MEMORY = "memory"         # MODE B: memory-only after document leaves context
    HYBRID = "hybrid"         # MODE C: memory + retrieval + citation/refusal


@dataclass
class QAResult:
    """Structured result from the QA pipeline."""
    question_id: str
    question: str
    mode: str
    answer: str
    citations: List[str] = field(default_factory=list)  # passage IDs
    refused: bool = False
    refusal_message: str = ""
    evidence_passages: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    refusal_reason: Optional[str] = None
    document_ids: List[str] = field(default_factory=list)
    document_versions: List[int] = field(default_factory=list)
    retrieved_passages: List[str] = field(default_factory=list)
    latency_ms: float = 0.0
    language: str = "en"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_e2e_dict(self) -> Dict[str, Any]:
        return {
            "question_id": self.question_id,
            "mode": self.mode,
            "answer": self.answer,
            "citations": self.citations,
            "refused": self.refused,
            "refusal_reason": self.refusal_reason,
            "document_ids": self.document_ids,
            "document_versions": self.document_versions,
            "retrieved_passages": self.retrieved_passages,
            "latency_ms": round(self.latency_ms, 2),
            "language": self.language,
        }

    def to_chatbot_dict(self) -> Dict[str, Any]:
        """Section VII standardized CLI output format."""
        ver_str = ""
        if self.document_versions:
            ver_str = f"v{self.document_versions[0]}"
        elif self.document_ids:
            ver_str = "v1"

        return {
            "language": self.language,
            "mode": self.mode,
            "answer": self.answer if not self.refused else (self.refusal_message or self.answer),
            "refused": self.refused,
            "citations": self.citations,
            "document_version": ver_str,
            "evidence": [
                {
                    "passage_id": e.get("passage_id", ""),
                    "document_id": e.get("document_id", ""),
                    "score": round(float(e.get("score", 0.0)), 4),
                    "section_title": e.get("section_title", ""),
                    "text": e.get("text", "")[:300],
                }
                for e in self.evidence_passages
            ],
            "metadata": {
                "question_id": self.question_id,
                "confidence": round(self.confidence, 4),
                "refusal_reason": self.refusal_reason,
                "latency_ms": round(self.latency_ms, 2),
            },
        }


class HybridQAPipeline:
    """
    Orchestrates the three QA modes with pluggable components.
    
    Components:
        - model: PretrainedHopeLM (with SA-CMS)
        - retriever: BM25Retriever
        - evidence_selector: EvidenceSelector
        - refusal_controller: RefusalController
        - chunker: DocumentChunker
        - document_store: DocumentStore
    """

    def __init__(
        self,
        model=None,
        tokenizer=None,
        retriever=None,
        evidence_selector=None,
        refusal_controller=None,
        chunker=None,
        document_store=None,
        max_context_tokens: int = 512,
        max_answer_tokens: int = 64,
        device: str = "cpu",
    ):
        self.model = model
        self.tokenizer = tokenizer
        self.retriever = retriever
        self.evidence_selector = evidence_selector
        self.refusal_controller = refusal_controller
        self.chunker = chunker
        self.document_store = document_store
        self.max_context_tokens = max_context_tokens
        self.max_answer_tokens = max_answer_tokens
        self.device = device

        # Track ingested documents for memory mode
        self._ingested_docs: Dict[str, int] = {}  # doc_id -> version

    @staticmethod
    def _detect_language(text: str) -> str:
        if not text:
            return "en"
        vi_chars = set("àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"
                       "ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ")
        return "vi" if any(c in vi_chars for c in text) else "en"

    def ingest_document(
        self,
        document_id: str,
        learning_rate: float = 0.01,
        schedule_mode: str = "structure",
    ) -> Dict[str, Any]:
        """
        Ingest a document into SA-CMS memory.
        
        Steps:
        1. Load document from store
        2. Ingest via SA-CMS 3-level structure-aligned updates (Eq 71) if available
        3. Save memory snapshot
        
        Returns dict with ingestion statistics.
        """
        if self.document_store is None or self.model is None:
            raise RuntimeError("DocumentStore and model must be set for ingestion.")

        doc = self.document_store.get_document(document_id)
        logger.info(f"Ingesting document {document_id} v{doc.version}: '{doc.title}'")

        # Reset memory before ingestion
        self.model.reset_memory()

        # Ingest via SA-CMS 3-level structure-aligned if available, else sequential chunks
        if hasattr(self.model, "ingest_structured_document"):
            result = self.model.ingest_structured_document(
                document_text=doc.raw_text,
                schedule_mode=schedule_mode,
            )
        else:
            token_ids = self.tokenizer.encode(doc.raw_text, add_special_tokens=False)
            chunk_size = 64  # default CMS chunk
            chunks = []
            for i in range(0, len(token_ids), chunk_size):
                chunk = token_ids[i:i + chunk_size]
                if len(chunk) > 0:
                    import torch
                    chunks.append(torch.tensor([chunk], dtype=torch.long))
            result = self.model.ingest_document_chunks(chunks, learning_rate=learning_rate)

        # Save memory snapshot
        if self.document_store and hasattr(self.model, 'cms') and self.model.cms is not None:
            snapshot = {
                "cms_state_dict": self.model.cms.state_dict(),
                "cms_norm_state_dict": self.model.cms_norm.state_dict() if self.model.cms_norm else None,
                "document_id": document_id,
                "version": doc.version,
                "num_levels": getattr(self.model, "num_levels", 3),
            }
            self.document_store.save_memory_snapshot(document_id, doc.version, snapshot)

        self._ingested_docs[document_id] = doc.version
        result["document_id"] = document_id
        result["version"] = doc.version
        return result

    def answer_question(
        self,
        question: str,
        question_id: str = "",
        mode: QAMode = QAMode.HYBRID,
        document_id: Optional[str] = None,
        top_k: int = 5,
        language: Optional[str] = None,
    ) -> QAResult:
        """
        Answer a question using the specified mode.
        """
        import time
        t_start = time.perf_counter()

        lang = language if language else self._detect_language(question)

        if mode == QAMode.CONTEXT:
            result = self._answer_context_mode(question, question_id, document_id, language=lang)
        elif mode == QAMode.MEMORY:
            result = self._answer_memory_mode(question, question_id, language=lang)
        elif mode == QAMode.HYBRID:
            result = self._answer_hybrid_mode(question, question_id, top_k, language=lang)
        else:
            raise ValueError(f"Unknown mode: {mode}")

        result.latency_ms = (time.perf_counter() - t_start) * 1000
        result.language = lang
        return result

    def _answer_context_mode(
        self,
        question: str,
        question_id: str,
        document_id: Optional[str],
        language: str = "en",
    ) -> QAResult:
        """MODE A: Full document in context."""
        context = ""
        doc_ids = []
        doc_versions = []
        if document_id and self.document_store:
            doc = self.document_store.get_document(document_id)
            context = doc.raw_text
            doc_ids = [document_id]
            doc_versions = [doc.version]

        prompt = self._build_prompt(question, context_text=context, language=language)
        answer = self._generate_answer(prompt)

        return QAResult(
            question_id=question_id,
            question=question,
            mode=QAMode.CONTEXT.value,
            answer=answer,
            confidence=1.0,
            document_ids=doc_ids,
            document_versions=doc_versions,
            retrieved_passages=[],
            refusal_reason=None,
            metadata={"has_context": bool(context)},
            language=language,
        )

    def _answer_memory_mode(
        self,
        question: str,
        question_id: str,
        language: str = "en",
    ) -> QAResult:
        """MODE B: Memory-only, document has left context."""
        prompt = self._build_prompt(question, context_text="", language=language)
        answer = self._generate_answer(prompt)

        return QAResult(
            question_id=question_id,
            question=question,
            mode=QAMode.MEMORY.value,
            answer=answer,
            document_ids=list(self._ingested_docs.keys()),
            document_versions=list(self._ingested_docs.values()),
            retrieved_passages=[],
            refusal_reason=None,
            metadata={"ingested_docs": dict(self._ingested_docs), "has_context": False, "context_removed": True},
            language=language,
        )

    def _answer_hybrid_mode(
        self,
        question: str,
        question_id: str,
        top_k: int = 5,
        language: str = "en",
    ) -> QAResult:
        """MODE C: Hybrid — memory + retrieval + citation/refusal."""
        # Step 1: Retrieve evidence
        retrieval_results = []
        if self.retriever:
            retrieval_results = self.retriever.retrieve(question, top_k=top_k)

        retrieved_ids = [r.passage_id for r in retrieval_results]
        retrieved_docs = list(dict.fromkeys(r.document_id for r in retrieval_results if hasattr(r, 'document_id')))

        # Step 2: Select evidence
        evidence = None
        if self.evidence_selector and retrieval_results:
            evidence = self.evidence_selector.select_evidence(question, retrieval_results)
        else:
            from src.hybrid_qa.evidence import EvidencePackage
            evidence = EvidencePackage(
                query=question,
                evidence_passages=[],
                has_sufficient_evidence=False,
                max_evidence_score=0.0,
                total_passages_searched=len(retrieval_results),
            )

        # Step 3: Refusal decision (language-aware)
        refusal_decision = None
        if self.refusal_controller:
            refusal_decision = self.refusal_controller.decide(evidence, language=language)

        # Step 4: Generate answer or refuse
        if refusal_decision and refusal_decision.should_refuse:
            reason_str = refusal_decision.reason.value if refusal_decision.reason else None
            return QAResult(
                question_id=question_id,
                question=question,
                mode=QAMode.HYBRID.value,
                answer="",
                refused=True,
                refusal_reason=reason_str,
                refusal_message=refusal_decision.refusal_message,
                document_ids=retrieved_docs,
                retrieved_passages=retrieved_ids,
                confidence=refusal_decision.confidence,
                metadata=refusal_decision.to_dict(),
                language=language,
            )

        # Build context from evidence passages
        evidence_text = "\n\n".join(
            f"[{c.passage_id}] {c.text}" for c in evidence.evidence_passages
        )
        prompt = self._build_prompt(question, context_text=evidence_text, language=language)
        answer = self._generate_answer(prompt)

        # Extract citations (passage IDs from evidence)
        citations = [c.passage_id for c in evidence.evidence_passages]
        evidence_docs = list(dict.fromkeys(c.document_id for c in evidence.evidence_passages))
        evidence_versions = []
        for c in evidence.evidence_passages:
            v = c.metadata.get("document_version") or c.metadata.get("version")
            if v and v not in evidence_versions:
                evidence_versions.append(v)

        return QAResult(
            question_id=question_id,
            question=question,
            mode=QAMode.HYBRID.value,
            answer=answer,
            citations=citations,
            refused=False,
            refusal_reason=None,
            document_ids=evidence_docs if evidence_docs else retrieved_docs,
            document_versions=evidence_versions,
            retrieved_passages=retrieved_ids,
            evidence_passages=[c.to_dict() for c in evidence.evidence_passages],
            confidence=refusal_decision.confidence if refusal_decision else 0.5,
            metadata={
                "retrieval_count": len(retrieval_results),
                "evidence_count": len(evidence.evidence_passages),
            },
            language=language,
        )

    def _build_prompt(self, question: str, context_text: str = "", language: str = "en") -> str:
        """Build a prompt for the language model."""
        if language in ("vi", "vietnamese"):
            if context_text:
                prompt = (
                    f"Dựa trên các đoạn trích sau, hãy trả lời câu hỏi một cách ngắn gọn, chính xác bằng tiếng Việt.\n\n"
                    f"Ngữ cảnh:\n{context_text}\n\n"
                    f"Câu hỏi: {question}\n"
                    f"Trả lời:"
                )
            else:
                prompt = (
                    f"Dựa trên kiến thức trong bộ nhớ, hãy trả lời câu hỏi sau bằng tiếng Việt:\n\n"
                    f"Câu hỏi: {question}\n"
                    f"Trả lời:"
                )
        else:
            if context_text:
                prompt = (
                    f"Based on the following context, answer the question.\n\n"
                    f"Context:\n{context_text}\n\n"
                    f"Question: {question}\n"
                    f"Answer:"
                )
            else:
                prompt = (
                    f"Answer the following question based on your memory.\n\n"
                    f"Question: {question}\n"
                    f"Answer:"
                )
        return prompt

    def _generate_answer(self, prompt: str) -> str:
        """Generate an answer using the backbone model."""
        if self.model is None or self.tokenizer is None:
            return "[MODEL NOT AVAILABLE]"

        import torch

        input_ids = self.tokenizer.encode(
            prompt,
            add_special_tokens=True,
            truncation=True,
            max_length=self.max_context_tokens,
        )
        input_tensor = torch.tensor([input_ids], dtype=torch.long).to(self.device)

        self.model.eval()
        with torch.no_grad():
            logits, _ = self.model(input_tensor)
            # Greedy decode max_answer_tokens
            generated = list(input_ids)
            for _ in range(self.max_answer_tokens):
                next_logits = logits[0, -1, :]
                next_token = next_logits.argmax().item()
                if next_token == self.tokenizer.eos_token_id:
                    break
                generated.append(next_token)
                # Re-run model on extended sequence
                input_tensor = torch.tensor([generated[-self.max_context_tokens:]], 
                                          dtype=torch.long).to(self.device)
                logits, _ = self.model(input_tensor)

        # Decode only the generated part (after prompt)
        answer_tokens = generated[len(input_ids):]
        answer = self.tokenizer.decode(answer_tokens, skip_special_tokens=True).strip()
        return answer

    def reset_memory(self):
        """Reset SA-CMS memory to initial state."""
        if self.model:
            self.model.reset_memory()
        self._ingested_docs.clear()

    def load_memory_for_document(self, document_id: str, version: Optional[int] = None):
        """Load a previously saved memory snapshot."""
        if self.document_store is None or self.model is None:
            raise RuntimeError("DocumentStore and model must be set.")
        if version is None:
            doc = self.document_store.get_document(document_id)
            version = doc.version
        snapshot = self.document_store.load_memory_snapshot(document_id, version)
        if self.model.cms is not None and "cms_state_dict" in snapshot:
            self.model.cms.load_state_dict(snapshot["cms_state_dict"])
        if self.model.cms_norm is not None and snapshot.get("cms_norm_state_dict"):
            self.model.cms_norm.load_state_dict(snapshot["cms_norm_state_dict"])
        self._ingested_docs[document_id] = version
