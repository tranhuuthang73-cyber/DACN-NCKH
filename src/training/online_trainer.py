"""
Online Document Ingestion and Continuum Memory Updating Loop (Equation 71).
"""

from typing import Dict, Any, List, Optional
import torch
import torch.nn as nn
from src.hope_attention.model import HopeAttentionLM
from src.training.loss import compute_perplexity


class OnlineDocumentTrainer:
    """
    Ingests long document token streams into HopeAttentionLM's multi-timescale CMS memory.
    Implements Equation 71 of arXiv:2512.24695v1.
    """

    def __init__(
        self,
        model: HopeAttentionLM,
        device: torch.device = None,
        step_chunk_size: int = 16,
    ):
        self.model = model
        self.device = device if device is not None else next(model.parameters()).device
        self.step_chunk_size = step_chunk_size

    def ingest_document(
        self,
        token_ids: torch.Tensor,
        reset_memory_first: bool = True,
    ) -> Dict[str, Any]:
        """
        Stream document tokens through the model, updating CMS memory levels according to
        their multi-timescale schedules (Equation 71).

        Args:
            token_ids: 1D or 2D tensor of token ids (seq_len) or (1, seq_len)
            reset_memory_first: Whether to reset memory to theta_0 before reading this document

        Returns:
            stats: Dictionary with ingestion statistics, losses, and update counts per level
        """
        if reset_memory_first:
            self.model.reset_memory()

        if token_ids.dim() == 1:
            token_ids = token_ids.unsqueeze(0)  # (1, seq_len)
        token_ids = token_ids.to(self.device)

        seq_len = token_ids.size(1)
        losses: List[float] = []
        updates_per_level: Dict[int, int] = {l: 0 for l in range(self.model.num_levels)}

        # Stream in chunks
        for start_idx in range(0, seq_len - 1, self.step_chunk_size):
            end_idx = min(start_idx + self.step_chunk_size + 1, seq_len)
            chunk_tokens = token_ids[:, start_idx:end_idx]

            if chunk_tokens.size(1) < 2:
                continue

            input_chunk = chunk_tokens[:, :-1]
            target_chunk = chunk_tokens[:, 1:]
            num_tokens = input_chunk.size(1)

            # Forward pass
            logits, loss, _ = self.model(input_chunk, targets=target_chunk)
            losses.append(loss.item())

            # Equation 71: update scheduled levels based on token advancement
            layer_updates = self.model.update_cms_online(loss, num_tokens=num_tokens)
            for layer_idx, levels in layer_updates.items():
                for lvl in levels:
                    updates_per_level[lvl] += 1

        avg_loss = sum(losses) / len(losses) if losses else 0.0
        ppl = compute_perplexity(avg_loss)

        return {
            "total_tokens": seq_len,
            "num_chunks": len(losses),
            "avg_loss": avg_loss,
            "perplexity": ppl,
            "updates_per_level": updates_per_level,
        }
