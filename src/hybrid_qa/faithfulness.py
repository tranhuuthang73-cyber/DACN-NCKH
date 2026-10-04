"""
Faithfulness Metrics — evaluation interfaces for citation quality and refusal.

Does NOT auto-claim "faithful" — provides machine-readable evaluation results
that require external judge/evaluation evidence to interpret.

Metrics:
    - answer_supported: does the answer have supporting evidence?
    - citation_supported: are citations traceable and relevant?
    - refusal_correct: was refusal appropriate when no evidence exists?
    - false_refusal: was the system refusing when it shouldn't have?
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

from src.hybrid_qa.pipeline import QAResult


@dataclass
class FaithfulnessEvaluation:
    """Machine-readable evaluation result for a single QA instance."""
    question_id: str
    answer: str
    citations: List[str]
    supported: Optional[bool] = None       # None = not evaluated yet
    refused: bool = False
    refusal_correct: Optional[bool] = None  # None = not evaluated yet
    false_refusal: Optional[bool] = None    # None = not evaluated yet
    evidence_overlap_score: float = 0.0     # Token overlap between answer and evidence
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FaithfulnessEvaluator:
    """
    Evaluates QA results for citation quality and refusal appropriateness.
    
    Evaluation types:
    1. Token overlap: lexical overlap between answer and cited passages.
    2. Citation validity: structural traceability check.
    3. Refusal analysis: whether refusal decision was correct (requires gold labels).
    
    NOTE: This evaluator provides METRICS, not claims.
    A metric value alone does not constitute scientific evidence of faithfulness.
    """

    def evaluate_single(
        self,
        qa_result: QAResult,
        gold_answer: Optional[str] = None,
        gold_answerable: Optional[bool] = None,
        all_passage_texts: Optional[Dict[str, str]] = None,
    ) -> FaithfulnessEvaluation:
        """
        Evaluate a single QA result.
        
        Args:
            qa_result: The pipeline output.
            gold_answer: The expected correct answer (if available).
            gold_answerable: Whether the question is answerable from the docs (if known).
            all_passage_texts: Mapping of passage_id -> text for evidence verification.
        """
        eval_result = FaithfulnessEvaluation(
            question_id=qa_result.question_id,
            answer=qa_result.answer,
            citations=qa_result.citations,
            refused=qa_result.refused,
        )

        # 1. Evidence overlap score
        if qa_result.answer and qa_result.evidence_passages:
            evidence_text = " ".join(
                p.get("text", "") if isinstance(p, dict) else p.text 
                for p in qa_result.evidence_passages
            )
            eval_result.evidence_overlap_score = self._token_overlap(
                qa_result.answer, evidence_text
            )

        # 2. Citation validity (structural check)
        if all_passage_texts and qa_result.citations:
            valid_citations = [
                cid for cid in qa_result.citations if cid in all_passage_texts
            ]
            eval_result.metadata["citation_validity_ratio"] = (
                len(valid_citations) / max(1, len(qa_result.citations))
            )

        # 3. Refusal analysis (only if gold labels available)
        if gold_answerable is not None:
            if qa_result.refused:
                # Refused — was it correct?
                eval_result.refusal_correct = not gold_answerable  # correct if truly unanswerable
                eval_result.false_refusal = gold_answerable         # false refusal if answerable
            else:
                # Answered — mark non-refused
                eval_result.refusal_correct = None
                eval_result.false_refusal = False

        # 4. Support check (if gold answer available)
        if gold_answer is not None and qa_result.answer:
            eval_result.supported = self._check_answer_support(
                qa_result.answer, gold_answer
            )

        return eval_result

    def evaluate_batch(
        self,
        qa_results: List[QAResult],
        gold_answers: Optional[Dict[str, str]] = None,
        gold_answerable: Optional[Dict[str, bool]] = None,
        all_passage_texts: Optional[Dict[str, str]] = None,
    ) -> List[FaithfulnessEvaluation]:
        """Evaluate a batch of QA results."""
        evaluations = []
        for result in qa_results:
            gold_ans = gold_answers.get(result.question_id) if gold_answers else None
            gold_abl = gold_answerable.get(result.question_id) if gold_answerable else None
            ev = self.evaluate_single(result, gold_ans, gold_abl, all_passage_texts)
            evaluations.append(ev)
        return evaluations

    def compute_aggregate_metrics(
        self, evaluations: List[FaithfulnessEvaluation]
    ) -> Dict[str, Any]:
        """Compute aggregate metrics from a batch of evaluations."""
        n = len(evaluations)
        if n == 0:
            return {"n": 0}

        n_answered = sum(1 for e in evaluations if not e.refused)
        n_refused = sum(1 for e in evaluations if e.refused)

        # Overlap scores (for answered questions only)
        overlap_scores = [e.evidence_overlap_score for e in evaluations if not e.refused]
        avg_overlap = sum(overlap_scores) / max(1, len(overlap_scores))

        # Citation counts
        citation_counts = [len(e.citations) for e in evaluations if not e.refused]
        avg_citations = sum(citation_counts) / max(1, len(citation_counts))

        # Refusal accuracy (if gold labels available)
        refusal_evals = [e for e in evaluations if e.refusal_correct is not None]
        n_correct_refusals = sum(1 for e in refusal_evals if e.refusal_correct)

        false_refusals = [e for e in evaluations if e.false_refusal is True]

        # Support rate
        support_evals = [e for e in evaluations if e.supported is not None]
        n_supported = sum(1 for e in support_evals if e.supported)

        return {
            "n": n,
            "n_answered": n_answered,
            "n_refused": n_refused,
            "refusal_rate": n_refused / max(1, n),
            "avg_evidence_overlap": round(avg_overlap, 4),
            "avg_citations_per_answer": round(avg_citations, 2),
            "n_correct_refusals": n_correct_refusals,
            "n_false_refusals": len(false_refusals),
            "n_supported": n_supported,
            "n_support_evaluated": len(support_evals),
            "support_rate": n_supported / max(1, len(support_evals)) if support_evals else None,
        }

    @staticmethod
    def _token_overlap(text_a: str, text_b: str) -> float:
        """Compute token-level overlap (Jaccard-like) between two texts."""
        tokens_a = set(text_a.lower().split())
        tokens_b = set(text_b.lower().split())
        if not tokens_a or not tokens_b:
            return 0.0
        intersection = tokens_a & tokens_b
        union = tokens_a | tokens_b
        return len(intersection) / len(union)

    @staticmethod
    def _check_answer_support(predicted: str, gold: str) -> bool:
        """Simple token F1 check for answer support."""
        pred_tokens = set(predicted.lower().split())
        gold_tokens = set(gold.lower().split())
        if not pred_tokens or not gold_tokens:
            return False
        overlap = pred_tokens & gold_tokens
        if not overlap:
            return False
        precision = len(overlap) / len(pred_tokens)
        recall = len(overlap) / len(gold_tokens)
        f1 = 2 * precision * recall / (precision + recall)
        return f1 > 0.3  # threshold for "supported"
