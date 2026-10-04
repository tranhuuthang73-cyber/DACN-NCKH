"""
Unit tests for Phase 3.0 — Hybrid Memory + Retrieval Foundation.

Tests:
- Document add/remove/update/versioning
- Chunk IDs (DOC{id}::P{idx} format)
- Retrieval deterministic behavior (BM25)
- Citation traceability
- Refusal when no evidence
- Answer when evidence exists
- Memory-only mode
- Hybrid mode
- Reset/snapshot/restore memory
"""

import os
import sys
import json
import shutil
import tempfile
import unittest

# Ensure project root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.hybrid_qa.document_store import DocumentStore, DocumentRecord, Passage
from src.hybrid_qa.chunker import DocumentChunker
from src.hybrid_qa.retriever import BM25Retriever, RetrievalResult
from src.hybrid_qa.evidence import EvidenceSelector, CitationChecker, EvidencePackage, Citation
from src.hybrid_qa.refusal import RefusalController, DecisionType, RefusalReason
from src.hybrid_qa.pipeline import HybridQAPipeline, QAMode, QAResult
from src.hybrid_qa.faithfulness import FaithfulnessEvaluator, FaithfulnessEvaluation


class TestDocumentStore(unittest.TestCase):
    """Tests for document add/remove/update/versioning."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_docstore_")
        self.store = DocumentStore(store_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_add_document(self):
        doc = self.store.add_document(
            title="Test Paper",
            raw_text="This is a test document about machine learning.",
        )
        self.assertEqual(doc.document_id, "DOC001")
        self.assertEqual(doc.version, 1)
        self.assertEqual(doc.title, "Test Paper")
        self.assertTrue(len(doc.content_hash) > 0)

    def test_add_multiple_documents(self):
        doc1 = self.store.add_document(title="First", raw_text="First document.")
        doc2 = self.store.add_document(title="Second", raw_text="Second document.")
        self.assertEqual(doc1.document_id, "DOC001")
        self.assertEqual(doc2.document_id, "DOC002")
        self.assertEqual(self.store.document_count, 2)

    def test_get_document(self):
        self.store.add_document(title="Test", raw_text="Content here.")
        doc = self.store.get_document("DOC001")
        self.assertEqual(doc.title, "Test")
        self.assertEqual(doc.raw_text, "Content here.")

    def test_update_document(self):
        self.store.add_document(title="Original", raw_text="Original content.")
        updated = self.store.update_document("DOC001", raw_text="Updated content.")
        self.assertEqual(updated.version, 2)
        self.assertEqual(updated.raw_text, "Updated content.")

        # Can still retrieve v1
        v1 = self.store.get_document("DOC001", version=1)
        self.assertEqual(v1.raw_text, "Original content.")

        # Latest is v2
        latest = self.store.get_document("DOC001")
        self.assertEqual(latest.version, 2)

    def test_remove_document(self):
        self.store.add_document(title="Removable", raw_text="To be removed.")
        self.assertTrue(self.store.remove_document("DOC001"))
        self.assertEqual(self.store.document_count, 0)
        with self.assertRaises(KeyError):
            self.store.get_document("DOC001")

    def test_remove_nonexistent(self):
        self.assertFalse(self.store.remove_document("DOC999"))

    def test_list_documents(self):
        self.store.add_document(title="A", raw_text="Content A.")
        self.store.add_document(title="B", raw_text="Content B.")
        docs = self.store.list_documents()
        self.assertEqual(len(docs), 2)
        titles = {d["title"] for d in docs}
        self.assertIn("A", titles)
        self.assertIn("B", titles)

    def test_duplicate_id_raises(self):
        self.store.add_document(title="X", raw_text="Y.", document_id="DOC001")
        with self.assertRaises(ValueError):
            self.store.add_document(title="Z", raw_text="W.", document_id="DOC001")

    def test_persistence(self):
        self.store.add_document(title="Persistent", raw_text="Will survive reload.")
        store2 = DocumentStore(store_dir=self.test_dir)
        doc = store2.get_document("DOC001")
        self.assertEqual(doc.title, "Persistent")


class TestDocumentChunker(unittest.TestCase):
    """Tests for chunk IDs and chunking logic."""

    def test_chunk_ids_format(self):
        doc = DocumentRecord(
            document_id="DOC001",
            version=1,
            title="Test",
            raw_text="First sentence. Second sentence. Third sentence. " * 20,
        )
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
        passages = chunker.chunk_document(doc)
        self.assertTrue(len(passages) > 0)
        for p in passages:
            self.assertTrue(p.passage_id.startswith("DOC001::P"))
            self.assertEqual(p.document_id, "DOC001")

    def test_unique_ids(self):
        doc = DocumentRecord(
            document_id="DOC005",
            version=1,
            title="Unique IDs",
            raw_text="A sentence. " * 100,
        )
        chunker = DocumentChunker(chunk_size=50, chunk_overlap=10)
        passages = chunker.chunk_document(doc)
        ids = [p.passage_id for p in passages]
        self.assertEqual(len(ids), len(set(ids)), "Passage IDs must be unique")

    def test_empty_document(self):
        doc = DocumentRecord(document_id="DOC001", version=1, title="Empty", raw_text="")
        chunker = DocumentChunker()
        passages = chunker.chunk_document(doc)
        self.assertEqual(len(passages), 0)

    def test_fixed_chunking(self):
        doc = DocumentRecord(
            document_id="DOC001", version=1, title="Fixed",
            raw_text="A" * 500,
        )
        chunker = DocumentChunker(chunk_size=100, strategy="fixed")
        passages = chunker.chunk_document(doc)
        self.assertTrue(len(passages) >= 5)


class TestBM25Retriever(unittest.TestCase):
    """Tests for retrieval determinism and correctness."""

    def setUp(self):
        self.passages = [
            Passage(passage_id="DOC001::P000", document_id="DOC001",
                    text="Machine learning is a subfield of artificial intelligence.",
                    start_char=0, end_char=60),
            Passage(passage_id="DOC001::P001", document_id="DOC001",
                    text="Deep learning uses neural networks with many layers.",
                    start_char=60, end_char=112),
            Passage(passage_id="DOC002::P000", document_id="DOC002",
                    text="Natural language processing handles text and speech.",
                    start_char=0, end_char=53),
            Passage(passage_id="DOC002::P001", document_id="DOC002",
                    text="Computer vision analyzes images and videos using deep learning.",
                    start_char=53, end_char=116),
        ]
        self.retriever = BM25Retriever()
        self.retriever.build_index(self.passages)

    def test_index_built(self):
        self.assertTrue(self.retriever._indexed)
        self.assertEqual(self.retriever.passage_count, 4)

    def test_retrieve_returns_results(self):
        results = self.retriever.retrieve("machine learning AI", top_k=3)
        self.assertTrue(len(results) > 0)
        self.assertIsInstance(results[0], RetrievalResult)

    def test_retrieve_relevance(self):
        results = self.retriever.retrieve("neural networks deep learning", top_k=2)
        top_ids = [r.passage_id for r in results]
        # "deep learning" passage should rank high
        self.assertIn("DOC001::P001", top_ids)

    def test_retrieve_deterministic(self):
        results1 = self.retriever.retrieve("machine learning", top_k=4)
        results2 = self.retriever.retrieve("machine learning", top_k=4)
        ids1 = [r.passage_id for r in results1]
        ids2 = [r.passage_id for r in results2]
        self.assertEqual(ids1, ids2, "Retrieval must be deterministic")

    def test_retrieve_scores_descending(self):
        results = self.retriever.retrieve("learning", top_k=4)
        scores = [r.score for r in results]
        for i in range(len(scores) - 1):
            self.assertGreaterEqual(scores[i], scores[i + 1])

    def test_empty_query(self):
        results = self.retriever.retrieve("", top_k=3)
        self.assertEqual(len(results), 0)

    def test_no_index(self):
        empty = BM25Retriever()
        results = empty.retrieve("test", top_k=3)
        self.assertEqual(len(results), 0)


class TestEvidenceSelector(unittest.TestCase):
    """Tests for evidence selection and citation checking."""

    def test_sufficient_evidence(self):
        selector = EvidenceSelector(score_threshold=0.5, min_evidence=1)
        results = [
            RetrievalResult("DOC001::P000", "DOC001", "Some text.", 2.5, 0, 10),
            RetrievalResult("DOC001::P001", "DOC001", "More text.", 1.0, 10, 20),
        ]
        evidence = selector.select_evidence("query", results)
        self.assertTrue(evidence.has_sufficient_evidence)
        self.assertEqual(len(evidence.evidence_passages), 2)

    def test_insufficient_evidence(self):
        selector = EvidenceSelector(score_threshold=5.0, min_evidence=1)
        results = [
            RetrievalResult("DOC001::P000", "DOC001", "Weak.", 0.1, 0, 5),
        ]
        evidence = selector.select_evidence("query", results)
        self.assertFalse(evidence.has_sufficient_evidence)

    def test_citation_check_valid(self):
        evidence = EvidencePackage(
            query="test",
            evidence_passages=[
                Citation("DOC001::P000", "DOC001", "text", 2.0),
            ],
            has_sufficient_evidence=True,
            max_evidence_score=2.0,
            total_passages_searched=5,
        )
        result = CitationChecker.verify_citations(
            ["DOC001::P000"], evidence
        )
        self.assertTrue(result["all_valid"])
        self.assertIn("DOC001::P000", result["in_evidence"])

    def test_citation_check_invalid(self):
        evidence = EvidencePackage(
            query="test",
            evidence_passages=[
                Citation("DOC001::P000", "DOC001", "text", 2.0),
            ],
            has_sufficient_evidence=True,
            max_evidence_score=2.0,
            total_passages_searched=5,
        )
        result = CitationChecker.verify_citations(
            ["DOC999::P999"], evidence
        )
        self.assertFalse(result["all_valid"])
        self.assertIn("DOC999::P999", result["invalid"])


class TestRefusalController(unittest.TestCase):
    """Tests for refusal decisions."""

    def test_refuse_no_evidence(self):
        controller = RefusalController(min_evidence_score=1.0, min_evidence_count=1)
        evidence = EvidencePackage(
            query="test", evidence_passages=[],
            has_sufficient_evidence=False,
            max_evidence_score=0.0, total_passages_searched=10,
        )
        decision = controller.decide(evidence)
        self.assertTrue(decision.should_refuse)
        self.assertEqual(decision.reason, RefusalReason.NO_EVIDENCE)

    def test_refuse_low_confidence(self):
        controller = RefusalController(min_evidence_score=5.0, min_evidence_count=1)
        evidence = EvidencePackage(
            query="test",
            evidence_passages=[Citation("DOC001::P000", "DOC001", "weak", 0.5)],
            has_sufficient_evidence=True,
            max_evidence_score=0.5, total_passages_searched=10,
        )
        decision = controller.decide(evidence)
        self.assertTrue(decision.should_refuse)
        self.assertEqual(decision.reason, RefusalReason.LOW_CONFIDENCE)

    def test_answer_when_sufficient(self):
        controller = RefusalController(min_evidence_score=1.0, min_evidence_count=1)
        evidence = EvidencePackage(
            query="test",
            evidence_passages=[Citation("DOC001::P000", "DOC001", "good evidence", 3.0)],
            has_sufficient_evidence=True,
            max_evidence_score=3.0, total_passages_searched=10,
        )
        decision = controller.decide(evidence)
        self.assertTrue(decision.should_answer)
        self.assertEqual(decision.decision, DecisionType.ANSWER)

    def test_configurable_threshold(self):
        strict = RefusalController(min_evidence_score=10.0)
        lenient = RefusalController(min_evidence_score=0.1)

        evidence = EvidencePackage(
            query="test",
            evidence_passages=[Citation("DOC001::P000", "DOC001", "medium", 2.0)],
            has_sufficient_evidence=True,
            max_evidence_score=2.0, total_passages_searched=5,
        )
        self.assertTrue(strict.decide(evidence).should_refuse)
        self.assertTrue(lenient.decide(evidence).should_answer)


class TestHybridQAPipeline(unittest.TestCase):
    """Tests for QA pipeline modes (without GPU model)."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_pipeline_")
        self.store = DocumentStore(store_dir=self.test_dir)
        self.chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)

        # Add test documents
        doc1 = self.store.add_document(
            title="ML Basics",
            raw_text=(
                "Machine learning is a branch of artificial intelligence. "
                "It involves training models on data to make predictions. "
                "Common algorithms include decision trees, neural networks, and SVMs. "
                "Deep learning is a subset of machine learning that uses neural networks with many layers."
            ),
        )
        doc2 = self.store.add_document(
            title="NLP Overview",
            raw_text=(
                "Natural language processing is the ability of a computer to understand human language. "
                "NLP techniques include tokenization, parsing, and named entity recognition. "
                "Modern NLP relies heavily on transformer architectures and large language models."
            ),
        )

        # Chunk and store passages
        for doc_id in ["DOC001", "DOC002"]:
            doc = self.store.get_document(doc_id)
            passages = self.chunker.chunk_document(doc)
            doc.passages = passages
            # Save back with passages
            doc_path = self.store.docs_dir / doc_id / f"v{doc.version}.json"
            with open(doc_path, "w", encoding="utf-8") as f:
                json.dump(doc.to_dict(), f, indent=2, ensure_ascii=False)

        # Build retriever index
        self.retriever = BM25Retriever()
        all_passages = self.store.get_all_passages()
        self.retriever.build_index(all_passages)

        self.evidence_selector = EvidenceSelector(score_threshold=0.5)
        self.refusal_controller = RefusalController(min_evidence_score=0.5)

        # Pipeline without model (test structure only)
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

    def test_hybrid_mode_with_evidence(self):
        result = self.pipeline.answer_question(
            question="What is machine learning?",
            question_id="Q001",
            mode=QAMode.HYBRID,
        )
        self.assertIsInstance(result, QAResult)
        self.assertEqual(result.mode, "hybrid")
        # Should not refuse because there is relevant evidence
        if not result.refused:
            self.assertTrue(len(result.citations) > 0)

    def test_hybrid_mode_refusal(self):
        # Use strict thresholds to trigger refusal
        strict_controller = RefusalController(min_evidence_score=100.0)
        pipeline = HybridQAPipeline(
            retriever=self.retriever,
            evidence_selector=EvidenceSelector(score_threshold=100.0),
            refusal_controller=strict_controller,
        )
        result = pipeline.answer_question(
            question="What is quantum entanglement?",
            question_id="Q002",
            mode=QAMode.HYBRID,
        )
        self.assertTrue(result.refused)
        self.assertTrue(len(result.refusal_message) > 0)

    def test_context_mode(self):
        result = self.pipeline.answer_question(
            question="What is ML?",
            question_id="Q003",
            mode=QAMode.CONTEXT,
            document_id="DOC001",
        )
        self.assertEqual(result.mode, "context")

    def test_memory_mode(self):
        result = self.pipeline.answer_question(
            question="What is ML?",
            question_id="Q004",
            mode=QAMode.MEMORY,
        )
        self.assertEqual(result.mode, "memory")

    def test_qa_result_serializable(self):
        result = self.pipeline.answer_question(
            question="What is NLP?",
            question_id="Q005",
            mode=QAMode.HYBRID,
        )
        d = result.to_dict()
        self.assertIsInstance(d, dict)
        self.assertIn("question_id", d)
        self.assertIn("citations", d)
        # Must be JSON serializable
        json_str = json.dumps(d)
        self.assertIsInstance(json_str, str)


class TestFaithfulnessEvaluator(unittest.TestCase):
    """Tests for faithfulness metrics."""

    def test_evaluate_answered_result(self):
        result = QAResult(
            question_id="Q001",
            question="What is ML?",
            mode="hybrid",
            answer="Machine learning is AI",
            citations=["DOC001::P000"],
            evidence_passages=[{"text": "Machine learning is a branch of artificial intelligence."}],
        )
        evaluator = FaithfulnessEvaluator()
        ev = evaluator.evaluate_single(result, gold_answer="Machine learning is artificial intelligence")
        self.assertIsInstance(ev, FaithfulnessEvaluation)
        self.assertFalse(ev.refused)
        self.assertGreater(ev.evidence_overlap_score, 0.0)

    def test_evaluate_refused_result(self):
        result = QAResult(
            question_id="Q002",
            question="What is quantum gravity?",
            mode="hybrid",
            answer="",
            refused=True,
            refusal_message="No evidence found.",
        )
        evaluator = FaithfulnessEvaluator()
        ev = evaluator.evaluate_single(result, gold_answerable=False)
        self.assertTrue(ev.refused)
        self.assertTrue(ev.refusal_correct)
        self.assertFalse(ev.false_refusal)

    def test_false_refusal_detection(self):
        result = QAResult(
            question_id="Q003",
            question="What is ML?",
            mode="hybrid",
            answer="",
            refused=True,
            refusal_message="No evidence.",
        )
        evaluator = FaithfulnessEvaluator()
        ev = evaluator.evaluate_single(result, gold_answerable=True)
        self.assertTrue(ev.false_refusal)

    def test_aggregate_metrics(self):
        evaluator = FaithfulnessEvaluator()
        evals = [
            FaithfulnessEvaluation("Q1", "ans1", ["DOC001::P000"], supported=True, evidence_overlap_score=0.5),
            FaithfulnessEvaluation("Q2", "", [], refused=True, refusal_correct=True),
            FaithfulnessEvaluation("Q3", "ans3", ["DOC002::P000"], supported=False, evidence_overlap_score=0.1),
        ]
        metrics = evaluator.compute_aggregate_metrics(evals)
        self.assertEqual(metrics["n"], 3)
        self.assertEqual(metrics["n_answered"], 2)
        self.assertEqual(metrics["n_refused"], 1)

    def test_evaluation_serializable(self):
        ev = FaithfulnessEvaluation(
            question_id="Q1", answer="test", citations=["DOC001::P000"],
            supported=True, refused=False, evidence_overlap_score=0.5,
        )
        d = ev.to_dict()
        json_str = json.dumps(d)
        self.assertIsInstance(json_str, str)


class TestMemorySnapshotRestore(unittest.TestCase):
    """Tests for memory snapshot save/load via DocumentStore."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_snapshot_")
        self.store = DocumentStore(store_dir=self.test_dir)
        self.store.add_document(title="Snapshot Test", raw_text="Content.")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_save_and_load_snapshot(self):
        import torch
        fake_state = {"weight": torch.randn(10, 10), "bias": torch.randn(10)}
        path = self.store.save_memory_snapshot("DOC001", 1, fake_state)
        self.assertTrue(os.path.exists(path))

        loaded = self.store.load_memory_snapshot("DOC001", 1)
        self.assertTrue(torch.allclose(fake_state["weight"], loaded["weight"]))

    def test_has_snapshot(self):
        import torch
        self.assertFalse(self.store.has_memory_snapshot("DOC001", 1))
        self.store.save_memory_snapshot("DOC001", 1, {"data": torch.zeros(5)})
        self.assertTrue(self.store.has_memory_snapshot("DOC001", 1))

    def test_load_nonexistent_raises(self):
        with self.assertRaises(FileNotFoundError):
            self.store.load_memory_snapshot("DOC001", 99)


if __name__ == "__main__":
    unittest.main(verbosity=2)
