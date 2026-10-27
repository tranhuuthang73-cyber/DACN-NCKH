"""
Pipeline Singleton & Service Manager for NeuroRead / SA-CMS Studio.
Manages DocumentStore, Retriever, SA-CMS Multi-Level Memory, Telemetry, and Frozen Pipeline.
STRICT RULE: NO TRAINING, NO GRADIENT UPDATES, FROZEN INFERENCE ONLY.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any

from src.hybrid_qa.document_store import DocumentStore
from src.hybrid_qa.chunker import DocumentChunker
from src.hybrid_qa.retriever import BM25Retriever
from src.hybrid_qa.evidence import EvidenceSelector
from src.hybrid_qa.refusal import RefusalController
from src.hybrid_qa.pipeline import HybridQAPipeline
from src.document_structure.parser import DocumentStructureParser
from src.web.telemetry import TelemetryLogger
from src.web.session_manager import SessionManager
from src.web.question_router import QuestionRouter
from src.hybrid_qa.grounding_validator import AnswerGroundingValidator
from src.memory.mechanistic_inspector import MemoryMechanisticInspector
from src.evaluation.token_efficiency_scorecard import TokenEfficiencyScorecard
from src.evaluation.rq_deep_analyzer import DeepRQAnalyzer
from src.memory.offline_memory_manager import OfflineMemoryManager
from src.web.local_model_loader import LocalModelLoader


class PipelineService:
    """Singleton service to manage DocumentStore, Retriever, SA-CMS, and Telemetry."""

    _instance: Optional["PipelineService"] = None

    def __init__(self, store_dir: str = "data/document_store"):
        self.store_dir = Path(store_dir)
        self.store = DocumentStore(store_dir=str(self.store_dir))
        self.chunker = DocumentChunker(chunk_size=256, chunk_overlap=32)
        self.retriever = BM25Retriever(k1=1.5, b=0.75)
        self.evidence_selector = EvidenceSelector(score_threshold=3.0, max_evidence=5, min_evidence=1, min_query_coverage=0.35)
        self.refusal_controller = RefusalController(min_evidence_score=3.0, min_evidence_count=1, min_query_coverage=0.35)
        self.structure_parser = DocumentStructureParser()
        self.telemetry = TelemetryLogger()
        self.session_manager = SessionManager()
        self.question_router = QuestionRouter()
        self.grounding_validator = AnswerGroundingValidator()
        self.mechanistic_inspector = MemoryMechanisticInspector()
        self.efficiency_generator = TokenEfficiencyScorecard()
        self.rq_analyzer = DeepRQAnalyzer()
        self.memory_manager = OfflineMemoryManager.get_instance()

        self.pipeline: Optional[HybridQAPipeline] = None
        self.model = None
        self.tokenizer = None
        self.device = "cpu"
        self.model_loaded = False
        self.model_error = None

        self._initialize_retriever()

    @classmethod
    def get_instance(cls) -> "PipelineService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _initialize_retriever(self):
        """Builds or rebuilds BM25 index over all passages in store."""
        passages = self.store.get_all_passages()
        if passages:
            self.retriever.build_index(passages)

    def load_model_if_requested(self, prefer_gpu: bool = False):
        """Loads SmolLM2 / SA-CMS in frozen evaluation mode from local_runtime/ strictly offline."""
        if self.model_loaded and self.model is not None:
            return

        loader = LocalModelLoader.get_instance()
        model, tokenizer = loader.load_offline_model(prefer_gpu=prefer_gpu)
        self.model = model
        self.tokenizer = tokenizer
        self.device = loader.device
        self.model_loaded = loader.model_loaded
        self.model_error = loader.model_error

        # Build pipeline wrapper
        self.pipeline = HybridQAPipeline(
            model=self.model,
            tokenizer=self.tokenizer,
            retriever=self.retriever,
            evidence_selector=self.evidence_selector,
            refusal_controller=self.refusal_controller,
            chunker=self.chunker,
            document_store=self.store,
            device=self.device,
        )
