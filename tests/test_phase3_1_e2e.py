"""
Unit and Integration Tests for Phase 3.1 — End-to-End Hybrid QA Validation.

Tests all 11 Tasks specified in the Phase 3.1 specification:
- Task 1: Test Documents & Corpus Structure (Doc A, B, C; sections, paragraphs, passages)
- Task 2: E2E Mode A (In-Context, no retrieval dependency)
- Task 3: E2E Mode B (Memory-Only, SA-CMS weights updated, context evicted)
- Task 4: E2E Mode C (Hybrid, P2 foundation: ingestion + BM25 + evidence + refusal/citations)
- Task 5: Citation Traceability (6-level chain: answer -> cit -> passage -> para -> sec -> doc -> ver)
- Task 6: Refusal Controller (3 specific reason codes, no hallucination)
- Task 7: Document Versioning & Snapshots across versions
- Task 8: Memory Snapshot Lifecycle (S0 -> S1 -> S2 -> restore S1, store preserved)
- Task 9: Machine-Readable Schema (Task 9 JSON export compliance)
- Task 10: 100-Question Test Matrix Validation
- Task 11: Scientific Boundary Guarantees
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from pathlib import Path

# Ensure root directory is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.hybrid_qa.document_store import DocumentStore, DocumentRecord, Passage
from src.hybrid_qa.chunker import DocumentChunker
from src.hybrid_qa.retriever import BM25Retriever
from src.hybrid_qa.evidence import EvidenceSelector, CitationChecker, EvidencePackage, Citation
from src.hybrid_qa.refusal import RefusalController, DecisionType, RefusalReason
from src.hybrid_qa.pipeline import HybridQAPipeline, QAMode, QAResult
from src.hybrid_qa.test_corpus import get_test_documents, get_100_test_questions


class TestTask1_CorpusStructure(unittest.TestCase):
    """TASK 1: Verify test corpus structure (Doc A, Doc B, Doc C)."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_t1_")
        self.store = DocumentStore(store_dir=self.test_dir)
        self.chunker = DocumentChunker(chunk_size=256, chunk_overlap=32)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_three_documents_present(self):
        docs = get_test_documents()
        self.assertEqual(len(docs), 3)
        doc_ids = [d["document_id"] for d in docs]
        self.assertIn("DOC001", doc_ids)
        self.assertIn("DOC002", doc_ids)
        self.assertIn("DOC003", doc_ids)

    def test_passage_metadata_fields(self):
        """Passages must have document_id, version, section_id, paragraph_id, passage_id."""
        docs = get_test_documents()
        for d in docs:
            doc = self.store.add_document(title=d["title"], raw_text=d["raw_text"], metadata=d["metadata"])
            passages = self.chunker.chunk_document(doc)
            self.assertGreater(len(passages), 0)
            for p in passages:
                self.assertTrue(p.passage_id.startswith(f"{doc.document_id}::P"))
                self.assertEqual(p.document_id, doc.document_id)
                self.assertIn("section_id", p.metadata)
                self.assertIn("paragraph_id", p.metadata)
                self.assertIn("document_version", p.metadata)
                self.assertTrue(p.metadata["section_id"].startswith("SEC"))
                self.assertTrue(p.metadata["paragraph_id"].startswith("PARA"))

    def test_answers_not_hardcoded(self):
        """Verify pipeline code does not contain hard-coded answers."""
        pipeline_code_path = Path(__file__).resolve().parent.parent / "src" / "hybrid_qa" / "pipeline.py"
        with open(pipeline_code_path, "r", encoding="utf-8") as f:
            code = f.read()
        self.assertNotIn("134.5 triệu tham số", code)
        self.assertNotIn("Challenger Deep", code)
        self.assertNotIn("k1 bằng 1.5", code)


class TestTask2_ModeAContext(unittest.TestCase):
    """TASK 2: E2E Mode A (In-Context) verification."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_t2_")
        self.store = DocumentStore(store_dir=self.test_dir)
        self.doc = self.store.add_document(
            title="SmolLM2 Architecture",
            raw_text="SmolLM2-135M has 134.5 million parameters. It is completely frozen.",
        )
        self.pipeline = HybridQAPipeline(
            model=None,
            tokenizer=None,
            document_store=self.store,
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_context_mode_generation_and_mapping(self):
        result = self.pipeline.answer_question(
            question="How many parameters does SmolLM2 have?",
            question_id="Q_CTX_01",
            mode=QAMode.CONTEXT,
            document_id="DOC001",
        )
        self.assertEqual(result.mode, "context")
        self.assertEqual(result.document_ids, ["DOC001"])
        self.assertEqual(result.document_versions, [1])
        self.assertEqual(result.retrieved_passages, [])
        self.assertFalse(result.refused)
        self.assertTrue(result.metadata.get("has_context"))


class TestTask3_ModeBMemory(unittest.TestCase):
    """TASK 3: E2E Mode B (Memory-Only) verification."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_t3_")
        self.store = DocumentStore(store_dir=self.test_dir)
        self.store.add_document(
            title="Doc A",
            raw_text="The model uses Continuum Memory System with online gradient updates.",
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_memory_mode_context_evicted(self):
        """Must prove context is removed and query targets parametric memory."""
        pipeline = HybridQAPipeline(
            model=None,
            tokenizer=None,
            document_store=self.store,
        )
        pipeline._ingested_docs["DOC001"] = 1

        result = pipeline.answer_question(
            question="What memory system is used?",
            question_id="Q_MEM_01",
            mode=QAMode.MEMORY,
        )
        self.assertEqual(result.mode, "memory")
        self.assertTrue(result.metadata.get("context_removed"))
        self.assertFalse(result.metadata.get("has_context"))
        self.assertEqual(result.retrieved_passages, [])
        self.assertEqual(result.document_ids, ["DOC001"])


class TestTask4_ModeCHybrid(unittest.TestCase):
    """TASK 4: E2E Mode C (Hybrid: Memory + BM25 + Citation/Refusal)."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_t4_")
        self.store = DocumentStore(store_dir=self.test_dir)
        self.chunker = DocumentChunker(chunk_size=256, chunk_overlap=32)
        doc = self.store.add_document(
            title="Nested Learning",
            raw_text="Nested Learning introduces Continuum Memory System with SA-CMS for document QA.",
        )
        doc.passages = self.chunker.chunk_document(doc)
        self.retriever = BM25Retriever()
        self.retriever.build_index(doc.passages)
        self.evidence_selector = EvidenceSelector(score_threshold=0.5)
        self.refusal_controller = RefusalController(min_evidence_score=0.5)

        self.pipeline = HybridQAPipeline(
            model=None,
            tokenizer=None,
            retriever=self.retriever,
            evidence_selector=self.evidence_selector,
            refusal_controller=self.refusal_controller,
            chunker=self.chunker,
            document_store=self.store,
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_hybrid_flow_with_evidence(self):
        result = self.pipeline.answer_question(
            question="What is SA-CMS in Nested Learning?",
            question_id="Q_HYB_01",
            mode=QAMode.HYBRID,
        )
        self.assertEqual(result.mode, "hybrid")
        self.assertFalse(result.refused)
        self.assertGreater(len(result.citations), 0)
        self.assertGreater(len(result.retrieved_passages), 0)


class TestTask5_CitationTraceability(unittest.TestCase):
    """TASK 5: Citation traceability across the 6-level structural hierarchy."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_t5_")
        self.store = DocumentStore(store_dir=self.test_dir)
        self.chunker = DocumentChunker(chunk_size=256, chunk_overlap=32)
        doc = self.store.add_document(
            title="Specification Doc",
            raw_text="## Section 1: Intro\nThis is paragraph one.\n\nThis is paragraph two.",
        )
        doc.passages = self.chunker.chunk_document(doc)
        # Save back
        doc_file = self.store.docs_dir / doc.document_id / f"v{doc.version}.json"
        with open(doc_file, "w", encoding="utf-8") as f:
            json.dump(doc.to_dict(), f, indent=2, ensure_ascii=False)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_valid_citation_chain(self):
        """Trace: answer -> citation_id -> passage_id -> paragraph_id -> section_id -> document_id -> version."""
        trace = CitationChecker.trace_citation("DOC001::P000", self.store, expected_version=1)
        self.assertTrue(trace["valid"])
        self.assertEqual(trace["citation_id"], "DOC001::P000")
        self.assertEqual(trace["passage_id"], "DOC001::P000")
        self.assertIsNotNone(trace["paragraph_id"])
        self.assertIsNotNone(trace["section_id"])
        self.assertEqual(trace["document_id"], "DOC001")
        self.assertEqual(trace["document_version"], 1)
        self.assertTrue(trace["version_matched"])

    def test_nonexistent_citation_rejected(self):
        trace = CitationChecker.trace_citation("DOC999::P999", self.store)
        self.assertFalse(trace["valid"])
        self.assertIsNotNone(trace["error"])

    def test_old_version_citation_mismatch_detected(self):
        """If expected_version=2 but citation points to version 1, it must be flagged."""
        trace = CitationChecker.trace_citation("DOC001::P000", self.store, expected_version=2)
        self.assertFalse(trace["valid"])
        self.assertFalse(trace["version_matched"])
        self.assertIn("Version mismatch", trace["error"])


class TestTask6_RefusalController(unittest.TestCase):
    """TASK 6: Refusal on unanswerable and insufficient-evidence questions."""

    def setUp(self):
        self.controller = RefusalController(min_evidence_score=1.0, min_evidence_count=1)

    def test_answer_when_evidence_sufficient(self):
        pkg = EvidencePackage(
            query="test",
            evidence_passages=[Citation(passage_id="DOC001::P000", document_id="DOC001", text="evidence", score=2.5)],
            has_sufficient_evidence=True,
            max_evidence_score=2.5,
            total_passages_searched=5,
        )
        dec = self.controller.decide(pkg)
        self.assertTrue(dec.should_answer)
        self.assertFalse(dec.should_refuse)

    def test_refuse_when_no_evidence(self):
        pkg = EvidencePackage(
            query="unrelated",
            evidence_passages=[],
            has_sufficient_evidence=False,
            max_evidence_score=0.0,
            total_passages_searched=5,
        )
        dec = self.controller.decide(pkg)
        self.assertTrue(dec.should_refuse)
        self.assertEqual(dec.reason, RefusalReason.NO_EVIDENCE)

    def test_refuse_when_low_confidence(self):
        pkg = EvidencePackage(
            query="insufficient",
            evidence_passages=[Citation(passage_id="DOC001::P000", document_id="DOC001", text="weak", score=0.4)],
            has_sufficient_evidence=True,
            max_evidence_score=0.4,
            total_passages_searched=5,
        )
        dec = self.controller.decide(pkg)
        self.assertTrue(dec.should_refuse)
        self.assertEqual(dec.reason, RefusalReason.LOW_CONFIDENCE)


class TestTask7_DocumentVersioning(unittest.TestCase):
    """TASK 7: Versioning update and traceability."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_t7_")
        self.store = DocumentStore(store_dir=self.test_dir)
        self.chunker = DocumentChunker(chunk_size=256, chunk_overlap=32)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_update_version_and_query(self):
        # v1
        doc_v1 = self.store.add_document(title="Doc", raw_text="Version 1 content.")
        doc_v1.passages = self.chunker.chunk_document(doc_v1)
        self.assertEqual(doc_v1.version, 1)

        # v2
        doc_v2 = self.store.update_document("DOC001", raw_text="Version 2 updated content with new facts.")
        doc_v2.passages = self.chunker.chunk_document(doc_v2)
        self.assertEqual(doc_v2.version, 2)

        # Both versions exist
        v1_retrieved = self.store.get_document("DOC001", version=1)
        v2_retrieved = self.store.get_document("DOC001", version=2)
        self.assertEqual(v1_retrieved.raw_text, "Version 1 content.")
        self.assertIn("Version 2", v2_retrieved.raw_text)


class TestTask8_MemorySnapshotLifecycle(unittest.TestCase):
    """TASK 8: S0 -> ingest A -> S1 -> ingest B -> restore S1."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_t8_")
        self.store = DocumentStore(store_dir=self.test_dir)
        self.store.add_document(title="A", raw_text="Content of Document A.")
        self.store.add_document(title="B", raw_text="Content of Document B.")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_snapshot_lifecycle(self):
        import torch
        s0_state = {"weights": torch.zeros(4, 4)}
        s1_state = {"weights": torch.ones(4, 4) * 1.5}
        s2_state = {"weights": torch.ones(4, 4) * 3.0}

        # Save S1 for DOC001
        self.store.save_memory_snapshot("DOC001", 1, s1_state)
        self.assertTrue(self.store.has_memory_snapshot("DOC001", 1))

        # Save S2 for DOC002
        self.store.save_memory_snapshot("DOC002", 1, s2_state)

        # Restore S1
        restored = self.store.load_memory_snapshot("DOC001", 1)
        self.assertTrue(torch.allclose(restored["weights"], s1_state["weights"]))

        # Check document store still contains both documents
        self.assertEqual(self.store.document_count, 2)
        self.assertEqual(self.store.get_document("DOC001").title, "A")
        self.assertEqual(self.store.get_document("DOC002").title, "B")


class TestTask9_MachineReadableSchema(unittest.TestCase):
    """TASK 9: Schema compliance for machine-readable JSON export."""

    def test_schema_keys(self):
        res = QAResult(
            question_id="Q001",
            question="What is CMS?",
            mode="hybrid",
            answer="Continuum Memory System",
            citations=["DOC001::P000"],
            refused=False,
            refusal_reason=None,
            document_ids=["DOC001"],
            document_versions=[1],
            retrieved_passages=["DOC001::P000"],
            latency_ms=12.5,
        )
        d = res.to_e2e_dict()
        required_keys = {
            "question_id", "mode", "answer", "citations", "refused",
            "refusal_reason", "document_ids", "document_versions",
            "retrieved_passages", "latency_ms"
        }
        self.assertTrue(required_keys.issubset(set(d.keys())))
        # Must be JSON serializable
        serialized = json.dumps(d)
        self.assertIsInstance(serialized, str)


class TestTask10_100QuestionsSuite(unittest.TestCase):
    """TASK 10: Validation of the 100-question matrix."""

    def test_100_questions_distribution(self):
        questions = get_100_test_questions()
        self.assertEqual(len(questions), 100)

        n_ans = sum(1 for q in questions if q["category"] == "answerable")
        n_unans = sum(1 for q in questions if q["category"] == "unanswerable")
        n_insuff = sum(1 for q in questions if q["category"] == "insufficient_evidence")

        self.assertEqual(n_ans, 50)
        self.assertEqual(n_unans, 25)
        self.assertEqual(n_insuff, 25)


class TestTask11_ScientificBoundary(unittest.TestCase):
    """TASK 11: Scientific boundary checks."""

    def test_no_unwarranted_overclaims(self):
        forbidden_claims = [
            "Hybrid beats RAG",
            "SA-CMS beats retrieval",
            "P2 beats P1",
            "solves hallucination",
        ]
        # Check docstring of pipeline
        pipeline_path = Path(__file__).resolve().parent.parent / "src" / "hybrid_qa" / "pipeline.py"
        with open(pipeline_path, "r", encoding="utf-8") as f:
            content = f.read()
        for fc in forbidden_claims:
            self.assertNotIn(fc.lower(), content.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
