"""
Loss and perplexity computation functions for Causal Language Modeling.
"""

import math
import torch
import torch.nn.functional as F


def compute_next_token_loss(
    logits: torch.Tensor,
    targets: torch.Tensor,
    ignore_index: int = -100,
) -> torch.Tensor:
    """
    Computes cross-entropy loss for next-token prediction.
    Args:
        logits: (batch_size, seq_len, vocab_size)
        targets: (batch_size, seq_len)
    """
    vocab_size = logits.size(-1)
    loss = F.cross_entropy(
        logits.view(-1, vocab_size),
        targets.view(-1),
        ignore_index=ignore_index,
    )
    return loss


def compute_perplexity(loss: float) -> float:
    """Computes perplexity from cross-entropy loss: PPL = exp(loss)."""
    try:
        return math.exp(loss)
    except OverflowError:
        return float("inf")
