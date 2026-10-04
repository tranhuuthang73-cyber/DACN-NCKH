"""
Tests for Phase 3.3 — SA-CMS 3-Level Chatbot Backend Integration & Vietnamese Readiness Validation.
"""

import os
import sys
import json
import pytest
import tempfile
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.document_structure.parser import DocumentStructureParser
from src.document_structure.types import BoundaryType
from src.hope_attention.sa_cms import StructureAlignedHopeLM, StructureAlignedSchedule
from src.hybrid_qa.document_store import DocumentStore, Passage
from src.hybrid_qa.chunker import DocumentChunker
from src.hybrid_qa.retriever import BM25Retriever
from src.hybrid_qa.evidence import EvidenceSelector, CitationChecker, Citation, EvidencePackage
from src.hybrid_qa.refusal import RefusalController, RefusalReason, DecisionType
from src.hybrid_qa.pipeline import HybridQAPipeline, QAMode, QAResult
from src.hybrid_qa.vietnamese_corpus import (
    get_vietnamese_documents,
    get_vietnamese_smoke_questions,
    get_vietnamese_v2_update,
)
from scripts.run_chatbot import run_chatbot, build_chatbot_pipeline


class TestPhase33Architecture:
    """Test SA-CMS 3-Level architecture compliance."""

    def test_sa_cms_three_level_configuration(self):
        """Verify SA-CMS operates strictly on 3 levels: Paragraph, Section, Document."""
        model = StructureAlignedHopeLM(
            model_name_or_path="HuggingFaceTB/SmolLM2-135M",
            num_levels=3,
            device="cpu",
        )
        assert model.num_levels == 3, "Pipeline must use num_levels=3 (no reverting to 2)"

        cms_params = sum(p.numel() for p in model.get_cms_parameters())
        backbone_params = sum(p.numel() for p in model.backbone.parameters())

        assert cms_params == 5315904, f"Expected 5,315,904 trainable CMS parameters, got {cms_params}"
        assert backbone_params == 134515008, f"Expected 134,515,008 frozen backbone parameters, got {backbone_params}"

        # Verify schedule labels
        sched = StructureAlignedSchedule(
            num_levels=3,
            total_tokens=100,
            schedule_mode="fixed_token",
            fixed_chunk_sizes=[16, 32, 64],
        )
        assert sched.num_levels == 3


class TestVietnameseReadiness:
    """Test Vietnamese documents parsing, passage IDs, and smoke test questions."""

    def test_vietnamese_documents_structure(self):
        docs = get_vietnamese_documents()
        assert len(docs) >= 5, f"Expected at least 5 documents, got {len(docs)}"

        parser = DocumentStructureParser()
        for doc in docs:
            assert doc["document_id"].startswith("VN_DOC_")
            assert doc["version"] == 1
            assert len(doc["title"]) > 5
            assert len(doc["raw_text"]) > 100

            struct = parser.parse_text(doc["raw_text"])
            assert len(struct.sections) >= 2, f"{doc['document_id']} should have at least 2 sections"
            assert len(struct.paragraphs) >= 4, f"{doc['document_id']} should have at least 4 paragraphs"

    def test_vietnamese_smoke_questions_distribution(self):
        questions = get_vietnamese_smoke_questions()
        assert len(questions) == 40, f"Expected exactly 40 questions, got {len(questions)}"

        answerable = [q for q in questions if q["category"] == "answerable"]
        unanswerable = [q for q in questions if q["category"] == "unanswerable"]
        insufficient = [q for q in questions if q["category"] == "insufficient_evidence"]

        assert len(answerable) == 20, f"Expected 20 answerable, got {len(answerable)}"
        assert len(unanswerable) == 10, f"Expected 10 unanswerable, got {len(unanswerable)}"
        assert len(insufficient) == 10, f"Expected 10 insufficient, got {len(insufficient)}"


class TestRefusalAndLanguageBehavior:
    """Test refusal controller language adaptation with frozen thresholds."""

    def test_vietnamese_refusal_messages(self):
        ctrl = RefusalController(min_evidence_score=5.0, min_evidence_count=1)

        # Vietnamese query with no evidence
        ev_vi = EvidencePackage(
            query="Thủ đô của nước Úc là gì?",
            evidence_passages=[],
            has_sufficient_evidence=False,
            max_evidence_score=0.0,
            total_passages_searched=10,
        )
        dec_vi = ctrl.decide(ev_vi)
        assert dec_vi.should_refuse
        assert dec_vi.reason == RefusalReason.NO_EVIDENCE
        assert "Tài liệu được cung cấp không chứa thông tin" in dec_vi.refusal_message

        # English query with no evidence
        ev_en = EvidencePackage(
            query="What is the capital of Australia?",
            evidence_passages=[],
            has_sufficient_evidence=False,
            max_evidence_score=0.0,
            total_passages_searched=10,
        )
        dec_en = ctrl.decide(ev_en)
        assert dec_en.should_refuse
        assert dec_en.reason == RefusalReason.NO_EVIDENCE
        assert "The provided documents do not contain" in dec_en.refusal_message

    def test_frozen_thresholds_maintained(self):
        ctrl = RefusalController(min_evidence_score=5.0, min_evidence_count=1, min_query_coverage=0.35)
        assert ctrl.min_evidence_score == 5.0
        assert ctrl.min_evidence_count == 1
        assert ctrl.min_query_coverage == 0.35


class TestUnifiedModesAndVersioning:
    """Test 3 memory modes and document versioning."""

    def test_unified_three_modes(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = DocumentStore(store_dir=tmp_dir)
            doc = store.add_document(
                title="Tài liệu Thử nghiệm SA-CMS",
                raw_text="SA-CMS tích hợp 3 cấp độ bộ nhớ: Paragraph, Section và Document.",
                document_id="VN_DOC_TEST",
            )
            pipeline = HybridQAPipeline(
                model=None,
                tokenizer=None,
                document_store=store,
            )

            # Mode A: Context
            res_ctx = pipeline.answer_question(
                "SA-CMS có mấy cấp độ?",
                mode=QAMode.CONTEXT,
                document_id="VN_DOC_TEST",
            )
            assert res_ctx.mode == "context"
            assert res_ctx.document_ids == ["VN_DOC_TEST"]

            # Mode B: Memory
            res_mem = pipeline.answer_question(
                "SA-CMS có mấy cấp độ?",
                mode=QAMode.MEMORY,
            )
            assert res_mem.mode == "memory"
            assert res_mem.metadata.get("context_removed") is True

            # Mode C: Hybrid
            res_hyb = pipeline.answer_question(
                "SA-CMS có mấy cấp độ?",
                mode=QAMode.HYBRID,
            )
            assert res_hyb.mode == "hybrid"

    def test_document_versioning_update(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = DocumentStore(store_dir=tmp_dir)
            v1_doc = store.add_document(
                title="Tài liệu SA-CMS v1",
                raw_text="SA-CMS v1 sử dụng tốc độ học 0.01 cho Section Memory.",
                document_id="VN_DOC_001",
            )
            assert v1_doc.version == 1

            v2_doc = store.update_document(
                document_id="VN_DOC_001",
                raw_text="SA-CMS v2 nâng cấp tốc độ học Section Memory lên 0.005.",
                title="Tài liệu SA-CMS v2",
            )
            assert v2_doc.version == 2

            doc_retrieved_v1 = store.get_document("VN_DOC_001", version=1)
            doc_retrieved_v2 = store.get_document("VN_DOC_001", version=2)
            assert doc_retrieved_v1.version == 1
            assert doc_retrieved_v2.version == 2
            assert "0.01" in doc_retrieved_v1.raw_text
            assert "0.005" in doc_retrieved_v2.raw_text


class TestChatbotCLIOutputSchema:
    """Test Section VII standardized CLI JSON output schema."""

    def test_cli_json_schema(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out = run_chatbot(
                document="Hệ thống bộ nhớ đa quy mô SA-CMS giải quyết vấn đề trôi ngữ cảnh.",
                query="SA-CMS giải quyết vấn đề gì?",
                mode="hybrid",
                store_dir=tmp_dir,
                use_model=False,
            )

            # Check required keys from Section VII
            required_keys = ["language", "mode", "answer", "refused", "citations", "document_version", "evidence"]
            for key in required_keys:
                assert key in out, f"Missing required key '{key}' in chatbot output JSON"

            assert isinstance(out["language"], str)
            assert isinstance(out["mode"], str)
            assert isinstance(out["refused"], bool)
            assert isinstance(out["citations"], list)
            assert isinstance(out["evidence"], list)
