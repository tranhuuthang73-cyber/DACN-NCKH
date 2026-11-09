"""
Self-Study REST API Router for SA-CMS Document QA.
Provides dedicated local endpoints for autonomous self-study, parametric memory adaptation,
and neural grounded question answering without any external network calls.
"""

import time
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from src.self_study.types import SelfStudyQAPair
from src.self_study.extractor import QAPairExtractor
from src.self_study.trainer import SelfStudyTrainer
from src.self_study.reader import NeuralReaderEngine, NeuralReaderResult
from src.reasoning.hypergraph import ConceptHypergraph, MultiHopChain
from src.reasoning.cross_doc_scanner import CrossDocumentContradictionScanner, ContradictionScanReport
from src.reasoning.entropy_gate import EntropySurprisalGate, SurprisalResult
from src.reasoning.sleep_replay import SleepReplayEngine, ConsolidationReport
from src.reasoning.dialogue_tracker import ParametricDialogueTracker, DialogueSessionState, DialogueTurn
from src.reasoning.meta_cognition import MetaCognitiveEvaluator, MetaCognitiveReport

logger = logging.getLogger(__name__)

self_study_router = APIRouter(prefix="/api/self-study", tags=["Self-Study Brain"])

# Global singleton trainer, reader, hypergraph, contradiction scanner, sleep engine, dialogue tracker, meta evaluator
_trainer: Optional[SelfStudyTrainer] = None
_reader: Optional[NeuralReaderEngine] = None
_extractor = QAPairExtractor()
_hypergraph = ConceptHypergraph()
_contradiction_scanner = CrossDocumentContradictionScanner()
_entropy_gate = EntropySurprisalGate(surprisal_threshold=3.5)
_sleep_engine: Optional[SleepReplayEngine] = None
_dialogue_tracker = ParametricDialogueTracker()
_meta_evaluator = MetaCognitiveEvaluator()


def _get_service():
    """Lazy resolver for PipelineService to prevent top-level circular imports."""
    from src.web.app import PipelineService
    return PipelineService.get_instance()


def get_trainer() -> SelfStudyTrainer:
    global _trainer
    if _trainer is None:
        service = _get_service()
        service.load_model_if_requested(prefer_gpu=False)
        _trainer = SelfStudyTrainer(
            model=service.model,
            tokenizer=service.tokenizer,
        )
    return _trainer


def get_reader() -> NeuralReaderEngine:
    global _reader
    if _reader is None:
        service = _get_service()
        service.load_model_if_requested(prefer_gpu=False)
        _reader = NeuralReaderEngine(
            model=service.model,
            tokenizer=service.tokenizer,
            min_confidence=0.20,
        )
    return _reader


class IngestSelfStudyRequest(BaseModel):
    document_id: Optional[str] = Field(None, description="ID of an existing document in store")
    text: Optional[str] = Field(None, description="Raw document text if not in store")
    title: Optional[str] = Field("Tài liệu tự học", description="Document title")
    max_pairs: int = Field(15, ge=1, le=50, description="Max QA pairs to generate")
    epochs: int = Field(2, ge=1, le=5, description="Training epochs")
    max_steps: int = Field(15, ge=1, le=50, description="Max gradient steps")
    train_memory: bool = Field(True, description="Whether to update Level 2 & 3 memory")


class AskSelfStudyRequest(BaseModel):
    query: str = Field(..., min_length=2, description="User's question")
    document_id: Optional[str] = Field(None, description="Optional document ID for memory isolation")
    answer_mode: str = Field("balanced", description="concise | balanced | comprehensive")
    top_k: int = Field(4, ge=1, le=10, description="Number of evidence passages")


class MultiHopDeduceRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Relational reasoning query")
    start_concept: str = Field(..., description="Starting concept node")
    target_concept: str = Field(..., description="Target concept node to bridge to")
    max_hops: int = Field(4, ge=1, le=8, description="Maximum hops in graph BFS")


class ContradictionScanRequest(BaseModel):
    document_ids: Optional[List[str]] = Field(None, description="List of document IDs to scan (default: all)")


class EntropyFilterRequest(BaseModel):
    text: str = Field(..., min_length=2, description="Text to evaluate and prune")
    surprisal_threshold: float = Field(3.5, ge=1.0, le=10.0, description="Minimum bits of surprisal")


class SleepConsolidateRequest(BaseModel):
    document_ids: Optional[List[str]] = Field(None, description="Optional document IDs to replay")
    steps: int = Field(3, ge=1, le=20, description="Number of consolidation rehearsal steps")
    ewc_lambda: float = Field(200.0, ge=10.0, le=2000.0, description="EWC quadratic penalty strength")


class DialogueResolveRequest(BaseModel):
    session_id: str = Field("default", description="Session ID for tracking turns")
    query: str = Field(..., min_length=1, description="Current turn user query")
    previous_answer: Optional[str] = Field(None, description="Previous assistant answer if any")
    register_turn: bool = Field(False, description="Whether to record this query/answer as a completed turn")
    document_id: Optional[str] = Field(None, description="Active document ID")


class DialogueTurnRequest(BaseModel):
    session_id: str = Field("default", description="Session ID for tracking turns")
    query: str = Field(..., min_length=1, description="User query")
    answer: str = Field(..., min_length=1, description="Assistant answer")
    document_id: Optional[str] = Field(None, description="Active document ID")


class MetaCognitiveEvalRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User's query")
    answer: str = Field(..., min_length=1, description="Generated answer to evaluate")
    citations: Optional[List[Dict[str, Any]]] = Field(None, description="Citations supporting the answer")
    raw_confidence: float = Field(0.80, ge=0.0, le=1.0, description="Raw confidence score")


@self_study_router.post("/ingest")
async def ingest_document_self_study(req: IngestSelfStudyRequest):
    """
    Analyzes document text, auto-generates grounded QA pairs across all sections,
    and trains SA-CMS Level 2 (Section) & Level 3 (Document) memory.
    """
    service = _get_service()
    doc_text = ""
    doc_id = req.document_id or f"doc_self_study_{int(time.time())}"

    if req.text:
        doc_text = req.text
        doc_id = req.document_id or f"doc_self_study_{int(time.time())}"
    elif req.document_id:
        try:
            doc = service.store.get_document(req.document_id)
            doc_text = doc.raw_text
            doc_id = req.document_id
        except Exception:
            raise HTTPException(status_code=404, detail=f"Document {req.document_id} not found in store.")
    else:
        raise HTTPException(status_code=400, detail="Either document_id or text must be provided.")

    if not doc_text.strip():
        raise HTTPException(status_code=400, detail="Document text cannot be empty.")

    # 1. Extract QA pairs using deterministic syntactic rules
    report = _extractor.extract_from_text(
        text=doc_text,
        document_id=doc_id,
        max_pairs=req.max_pairs,
    )

    training_report = {}
    if req.train_memory and report.pairs:
        try:
            trainer = get_trainer()
            training_report = trainer.train(
                qa_pairs=report.pairs,
                epochs=req.epochs,
                max_steps=req.max_steps,
                document_id=doc_id,
            )
        except Exception as e:
            logger.warning(f"Self-study training failed or skipped: {e}")
            training_report = {"status": "error", "error": str(e)}

    return {
        "status": "success",
        "document_id": doc_id,
        "pairs_count": len(report.pairs),
        "pairs_by_rule": report.pairs_by_rule,
        "training_report": training_report,
        "pairs": [p.to_dict() for p in report.pairs],
    }


@self_study_router.get("/{doc_id}/pairs")
async def get_document_self_study_pairs(doc_id: str, max_pairs: int = 15):
    """
    Returns auto-extracted QA pairs for a given document.
    """
    service = _get_service()
    try:
        doc = service.store.get_document(doc_id)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found.")

    report = _extractor.extract_from_text(
        text=doc.raw_text,
        document_id=doc_id,
        max_pairs=max_pairs,
    )
    return report.to_dict()


@self_study_router.post("/ask")
async def ask_neural_reader(req: AskSelfStudyRequest):
    """
    Answers user question using NeuralReaderEngine with 100% grounded facts,
    structured key points, in-text citations, and follow-up self-study questions.
    """
    service = _get_service()
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # 1. If document_id provided, ensure memory checkpoint is loaded if available
    if req.document_id:
        try:
            trainer = get_trainer()
            trainer.load_document_checkpoint(req.document_id)
        except Exception:
            pass

    # 2. Retrieve relevant evidence passages
    retrieval_results = service.retriever.retrieve(query, top_k=req.top_k)
    citations_data = []

    def _extract_field(obj, name, default=""):
        if hasattr(obj, name):
            val = getattr(obj, name)
            return val if val is not None else default
        if isinstance(obj, dict):
            return obj.get(name, default)
        return default

    for idx, r in enumerate(retrieval_results):
        passage_id = _extract_field(r, "passage_id", "")
        # Filter by document_id if requested
        if req.document_id and not passage_id.startswith(f"{req.document_id}::"):
            continue

        raw_text = _extract_field(r, "text", "")
        score = _extract_field(r, "score", 0.0)
        meta = _extract_field(r, "metadata", {})
        doc_id = _extract_field(r, "document_id", "")
        sec_title = _extract_field(r, "section_title", "")
        doc_title = meta.get("document_title", meta.get("title", doc_id or "Tài liệu"))

        citations_data.append({
            "passage_id": passage_id,
            "document_id": doc_id or req.document_id or "",
            "document_title": doc_title,
            "section_title": sec_title,
            "citation_label": f"[{idx + 1}]",
            "score": round(float(score), 4),
            "text": raw_text,
        })

    # Fallback to general passages if document filter returned nothing
    if not citations_data and retrieval_results:
        for idx, r in enumerate(retrieval_results[:req.top_k]):
            meta = _extract_field(r, "metadata", {})
            doc_id = _extract_field(r, "document_id", "")
            citations_data.append({
                "passage_id": _extract_field(r, "passage_id", ""),
                "document_id": doc_id,
                "document_title": meta.get("document_title", meta.get("title", doc_id or "Tài liệu")),
                "section_title": _extract_field(r, "section_title", ""),
                "citation_label": f"[{idx + 1}]",
                "score": round(float(_extract_field(r, "score", 0.0)), 4),
                "text": _extract_field(r, "text", ""),
            })

    # 3. Read and synthesize with NeuralReaderEngine
    reader = get_reader()
    res: NeuralReaderResult = reader.synthesize(
        query=query,
        passages=citations_data,
        answer_mode=req.answer_mode,
        include_followup=True,
    )

    return res.to_dict()


@self_study_router.post("/reset")
async def reset_self_study_memory():
    """
    Resets CMS Level 2 & 3 back to base state.
    """
    try:
        trainer = get_trainer()
        trainer.reset_memory()
        return {"status": "success", "message": "SA-CMS memory successfully reset to initial base state."}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@self_study_router.post("/hypergraph/build")
async def build_concept_hypergraph():
    """
    Builds the concept hypergraph by analyzing all documents in the local store.
    """
    service = _get_service()
    docs = service.store.list_documents()
    total_extracted = 0

    from src.self_study.reader import split_clean_sentences

    for d_meta in docs:
        doc_id = d_meta.get("document_id", "")
        try:
            doc = service.store.get_document(doc_id)
            sentences = split_clean_sentences(doc.raw_text)
            count = _hypergraph.extract_from_sentences(
                sentences=sentences,
                document_id=doc_id,
                section_title=doc.title,
            )
            total_extracted += count
        except Exception:
            continue

    stats = _hypergraph.get_statistics()
    return {
        "status": "success",
        "total_documents_analyzed": len(docs),
        "relations_extracted": total_extracted,
        "hypergraph_statistics": stats,
    }


@self_study_router.post("/hypergraph/deduce")
async def deduce_multi_hop_path(req: MultiHopDeduceRequest):
    """
    Executes multi-hop deduction across document boundaries.
    """
    chain = _hypergraph.synthesize_multi_hop_deduction(
        query=req.query,
        start_concept=req.start_concept,
        target_concept=req.target_concept,
        max_hops=req.max_hops,
    )
    if not chain:
        return {
            "status": "no_path_found",
            "message": f"Không tìm thấy chuỗi liên kết suy luận trực tiếp giữa '{req.start_concept}' và '{req.target_concept}'.",
            "chain": None,
        }
    return {
        "status": "success",
        "chain": chain.to_dict(),
    }


@self_study_router.post("/contradictions/scan")
async def scan_cross_document_contradictions(req: ContradictionScanRequest):
    """
    Scans document store for factual, numerical, and polarity contradictions.
    """
    service = _get_service()
    docs_to_scan = []

    if req.document_ids:
        target_ids = req.document_ids
    else:
        target_ids = [d.get("document_id", "") for d in service.store.list_documents()]

    for d_id in target_ids:
        try:
            doc = service.store.get_document(d_id)
            docs_to_scan.append({
                "document_id": d_id,
                "title": doc.title,
                "text": doc.raw_text,
            })
        except Exception:
            continue

    report = _contradiction_scanner.scan_documents(docs_to_scan)
    return {
        "status": "success",
        "report": report.to_dict(),
    }


@self_study_router.post("/entropy/filter")
async def filter_low_surprisal_text(req: EntropyFilterRequest):
    """
    Evaluates informational surprisal and prunes low-entropy filler sentences.
    """
    gate = EntropySurprisalGate(surprisal_threshold=req.surprisal_threshold)
    res = gate.filter_text(req.text)
    return {
        "status": "success",
        "result": res.to_dict(),
        "filtered_text": res.filtered_text,
    }


@self_study_router.post("/sleep/consolidate")
async def consolidate_sleep_memory(req: SleepConsolidateRequest):
    """
    Triggers sleep-phase synaptic memory consolidation and EWC protection.
    """
    global _sleep_engine
    service = _get_service()
    service.load_model_if_requested(prefer_gpu=False)

    if _sleep_engine is None:
        _sleep_engine = SleepReplayEngine(
            model=service.model,
            device=service.device,
            ewc_lambda=req.ewc_lambda,
        )
    else:
        _sleep_engine.ewc_lambda = req.ewc_lambda

    all_pairs = []
    target_ids = req.document_ids or [d.get("document_id", "") for d in service.store.list_documents()[:3]]

    for d_id in target_ids:
        try:
            doc = service.store.get_document(d_id)
            report = _extractor.extract_from_text(doc.raw_text, document_id=d_id, max_pairs=3)
            all_pairs.extend(report.pairs)
        except Exception:
            continue

    trainer = get_trainer()
    report = _sleep_engine.consolidate(
        sample_pairs=all_pairs,
        trainer=trainer,
        steps=req.steps,
    )
    return {
        "status": "success",
        "consolidation_report": report.to_dict(),
    }


@self_study_router.post("/dialogue/resolve")
async def resolve_dialogue_query(req: DialogueResolveRequest):
    """
    Resolves anaphora and elliptic context in multi-turn dialogue
    using active entities and discourse history without prompt bloating.
    """
    resolved_query, session = _dialogue_tracker.resolve_query(req.session_id, req.query)

    if req.register_turn and req.previous_answer:
        _dialogue_tracker.record_turn(
            session_id=req.session_id,
            raw_query=req.query,
            resolved_query=resolved_query,
            bot_summary=req.previous_answer,
        )

    compact_prompt = _dialogue_tracker.get_compact_context_prompt(req.session_id)

    return {
        "status": "success",
        "session_id": req.session_id,
        "original_query": req.query,
        "resolved_query": resolved_query,
        "active_subject": session.active_subject,
        "entity_registry": session.entity_registry,
        "compact_prompt": compact_prompt,
    }


@self_study_router.post("/dialogue/turn")
async def record_dialogue_turn(req: DialogueTurnRequest):
    """
    Records a completed Q&A turn into parametric dialogue memory.
    """
    resolved_query, _ = _dialogue_tracker.resolve_query(req.session_id, req.query)
    turn = _dialogue_tracker.record_turn(
        session_id=req.session_id,
        raw_query=req.query,
        resolved_query=resolved_query,
        bot_summary=req.answer,
    )
    session = _dialogue_tracker.get_or_create_session(req.session_id)
    return {
        "status": "success",
        "turn": turn.to_dict(),
        "session_state": session.to_dict(),
    }


@self_study_router.post("/meta-cognition/evaluate")
async def evaluate_meta_cognition(req: MetaCognitiveEvalRequest):
    """
    Evaluates response quality, epistemically tagging statements as
    [Chắc chắn] vs [Có khả năng cao / Giả thuyết] and identifying knowledge gaps.
    """
    report = _meta_evaluator.evaluate_response(
        query=req.query,
        answer_text=req.answer,
        citations=req.citations or [],
        raw_confidence=req.raw_confidence,
    )
    return {
        "status": "success",
        "report": report.to_dict(),
    }
