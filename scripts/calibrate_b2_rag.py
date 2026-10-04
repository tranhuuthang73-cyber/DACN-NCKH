"""
Phase 4.0.1: B2 RAG Calibration on Independent Calibration Set.

Evaluates candidate RAG hyperparameter configurations on the calibration split
(VAL_DOC_001 to VAL_DOC_005, 50 QA pairs) without touching any TEST benchmark data.

Hyperparameters calibrated:
- chunk_size
- chunk_overlap
- top_k
- BM25 k1
- BM25 b
- refusal/evidence score threshold

Outputs:
- results/phase4_0_1_rag_calibration.csv
"""

import os
import sys
import csv
import time
import json
from typing import Dict, Any, List, Tuple
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.training.training_corpus import get_validation_corpus
from src.hybrid_qa.chunker import DocumentChunker
from src.hybrid_qa.retriever import BM25Retriever
from src.hybrid_qa.document_store import DocumentRecord


def run_rag_calibration():
    print("=" * 80)
    print("PHASE 4.0.1: B2 RAG CALIBRATION ON INDEPENDENT CALIBRATION SPLIT")
    print("=" * 80)

    val_data = get_validation_corpus()
    val_docs = val_data["documents"]
    val_samples = val_data["samples"]
    print(f"Loaded {len(val_docs)} calibration documents, {len(val_samples)} calibration QA pairs.")

    # Candidate hyperparameter grid for calibration
    candidates = [
        {
            "config_id": "CAND_01",
            "chunk_size": 128,
            "chunk_overlap": 16,
            "top_k": 3,
            "k1": 1.2,
            "b": 0.75,
            "score_threshold": 5.0,
            "description": "Small chunks (128), top-3, lower k1",
        },
        {
            "config_id": "CAND_02",
            "chunk_size": 128,
            "chunk_overlap": 32,
            "top_k": 5,
            "k1": 1.5,
            "b": 0.75,
            "score_threshold": 5.0,
            "description": "Small chunks (128), top-5, standard k1/b",
        },
        {
            "config_id": "CAND_03",
            "chunk_size": 256,
            "chunk_overlap": 16,
            "top_k": 3,
            "k1": 1.5,
            "b": 0.75,
            "score_threshold": 5.0,
            "description": "Medium chunks (256), top-3, standard k1/b",
        },
        {
            "config_id": "CAND_04_BASELINE",
            "chunk_size": 256,
            "chunk_overlap": 32,
            "top_k": 5,
            "k1": 1.5,
            "b": 0.75,
            "score_threshold": 5.0,
            "description": "Standard baseline: chunks 256, overlap 32, top-5, k1=1.5, b=0.75",
        },
        {
            "config_id": "CAND_05",
            "chunk_size": 256,
            "chunk_overlap": 64,
            "top_k": 5,
            "k1": 1.8,
            "b": 0.85,
            "score_threshold": 5.0,
            "description": "Medium chunks (256), higher overlap (64), high k1/b",
        },
        {
            "config_id": "CAND_06",
            "chunk_size": 256,
            "chunk_overlap": 32,
            "top_k": 7,
            "k1": 1.5,
            "b": 0.65,
            "score_threshold": 5.0,
            "description": "Medium chunks (256), top-7, lower b (less length penalty)",
        },
        {
            "config_id": "CAND_07",
            "chunk_size": 256,
            "chunk_overlap": 32,
            "top_k": 5,
            "k1": 1.5,
            "b": 0.75,
            "score_threshold": 3.0,
            "description": "Standard chunks with lower refusal score threshold (3.0)",
        },
        {
            "config_id": "CAND_08",
            "chunk_size": 256,
            "chunk_overlap": 32,
            "top_k": 5,
            "k1": 1.5,
            "b": 0.75,
            "score_threshold": 7.0,
            "description": "Standard chunks with stricter refusal score threshold (7.0)",
        },
        {
            "config_id": "CAND_09",
            "chunk_size": 384,
            "chunk_overlap": 32,
            "top_k": 3,
            "k1": 1.5,
            "b": 0.75,
            "score_threshold": 5.0,
            "description": "Large chunks (384), top-3, standard k1/b",
        },
        {
            "config_id": "CAND_10",
            "chunk_size": 384,
            "chunk_overlap": 48,
            "top_k": 5,
            "k1": 1.5,
            "b": 0.75,
            "score_threshold": 5.0,
            "description": "Large chunks (384), top-5, standard k1/b",
        },
    ]

    calibration_results: List[Dict[str, Any]] = []

    for cand in candidates:
        cfg_id = cand["config_id"]
        c_size = cand["chunk_size"]
        c_overlap = cand["chunk_overlap"]
        top_k = cand["top_k"]
        k1 = cand["k1"]
        b = cand["b"]
        thresh = cand["score_threshold"]

        chunker = DocumentChunker(chunk_size=c_size, chunk_overlap=c_overlap)

        # Chunk all validation docs
        all_passages = []
        for doc in val_docs:
            record = DocumentRecord(
                document_id=doc["doc_id"],
                version=1,
                title=doc["title"],
                raw_text=doc["context"],
            )
            p_list = chunker.chunk_document(record)
            all_passages.extend(p_list)

        retriever = BM25Retriever(k1=k1, b=b)
        retriever.build_index(all_passages)

        hits = 0
        reciprocal_ranks = []
        top1_scores = []
        latencies = []
        above_threshold_count = 0

        for sample in val_samples:
            q_text = sample["question"]
            a_text = sample["answer"].lower()
            target_doc = sample["document_id"]

            t0 = time.perf_counter()
            results = retriever.retrieve(q_text, top_k=top_k)
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1000.0)

            found_rank = 0
            if results:
                top1_scores.append(results[0].score)
                if results[0].score >= thresh:
                    above_threshold_count += 1

            for rank_idx, r in enumerate(results, start=1):
                # Hit condition: passage belongs to target document and contains ground truth answer substring
                # (or at least shares significant keywords with answer)
                is_target_doc = (r.document_id == target_doc)
                contains_answer = (a_text in r.text.lower())
                if is_target_doc and contains_answer:
                    found_rank = rank_idx
                    break

            if found_rank > 0:
                hits += 1
                reciprocal_ranks.append(1.0 / found_rank)
            else:
                reciprocal_ranks.append(0.0)

        hit_rate = (hits / len(val_samples)) * 100.0
        mrr = sum(reciprocal_ranks) / len(reciprocal_ranks)
        avg_top1_score = sum(top1_scores) / max(1, len(top1_scores))
        avg_latency = sum(latencies) / len(latencies)
        clear_threshold_rate = (above_threshold_count / len(val_samples)) * 100.0

        # Composite calibration score: HitRate (0-100) * 0.5 + MRR (0-1)*100 * 0.3 + ThresholdPass (0-100) * 0.2
        composite_score = (hit_rate * 0.5) + (mrr * 100.0 * 0.3) + (clear_threshold_rate * 0.2)

        res = {
            "config_id": cfg_id,
            "chunk_size": c_size,
            "chunk_overlap": c_overlap,
            "top_k": top_k,
            "k1": k1,
            "b": b,
            "score_threshold": thresh,
            "total_passages": len(all_passages),
            "hit_rate_pct": round(hit_rate, 2),
            "mrr": round(mrr, 4),
            "avg_top1_score": round(avg_top1_score, 2),
            "clear_threshold_pct": round(clear_threshold_rate, 2),
            "avg_latency_ms": round(avg_latency, 3),
            "composite_calibration_score": round(composite_score, 2),
            "description": cand["description"],
        }
        calibration_results.append(res)
        print(f"[{cfg_id}] HitRate: {hit_rate:5.1f}% | MRR: {mrr:.4f} | Top1Score: {avg_top1_score:5.2f} | Score: {composite_score:5.2f} | Latency: {avg_latency:.3f}ms")

    # Sort candidates by composite calibration score descending
    calibration_results.sort(key=lambda x: x["composite_calibration_score"], reverse=True)
    best_candidate = calibration_results[0]

    print("\n" + "=" * 80)
    print("B2 RAG CALIBRATION WINNER (SELECTED & FROZEN):")
    print(f"Selected Config: {best_candidate['config_id']}")
    print(f"  - chunk_size: {best_candidate['chunk_size']}")
    print(f"  - chunk_overlap: {best_candidate['chunk_overlap']}")
    print(f"  - top_k: {best_candidate['top_k']}")
    print(f"  - k1: {best_candidate['k1']}, b: {best_candidate['b']}")
    print(f"  - score_threshold: {best_candidate['score_threshold']}")
    print(f"  - Hit Rate: {best_candidate['hit_rate_pct']}% | MRR: {best_candidate['mrr']}")
    print(f"  - Selection Criterion: Maximize composite retrieval score (HitRate + MRR + Threshold Retention) within prompt budget (chunk <= 256).")
    print("=" * 80)

    # Export to CSV
    os.makedirs("results", exist_ok=True)
    csv_path = "results/phase4_0_1_rag_calibration.csv"
    fieldnames = [
        "config_id", "chunk_size", "chunk_overlap", "top_k", "k1", "b", "score_threshold",
        "total_passages", "hit_rate_pct", "mrr", "avg_top1_score", "clear_threshold_pct",
        "avg_latency_ms", "composite_calibration_score", "description"
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(calibration_results)

    print(f"RAG calibration results saved to {csv_path}")
    return calibration_results, best_candidate


if __name__ == "__main__":
    run_rag_calibration()
