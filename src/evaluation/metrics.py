"""
Evaluation metrics for Document QA and MK-NIAH retrieval.
"""

from typing import List, Dict, Any
import math
import torch


def compute_exact_match(predictions: List[int], targets: List[int]) -> float:
    """Computes exact match ratio between predicted token IDs and target token IDs."""
    if not targets:
        return 0.0
    matches = sum(1 for p, t in zip(predictions, targets) if p == t)
    return matches / len(targets)


def compute_token_accuracy(pred_logits: torch.Tensor, target_ids: torch.Tensor) -> float:
    """
    Computes top-1 accuracy for predicted logits against ground-truth targets.
    """
    preds = torch.argmax(pred_logits, dim=-1)
    correct = (preds == target_ids).sum().item()
    total = target_ids.numel()
    return correct / total if total > 0 else 0.0
