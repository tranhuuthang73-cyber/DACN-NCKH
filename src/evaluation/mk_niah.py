"""
Multi-Key Needle-In-A-Haystack (MK-NIAH) micro-benchmark generator and evaluator.
Paper Section 9.1 & Figure 7 (Left): Evaluates long-context multi-key retrieval.
"""

from typing import Dict, Any, List, Tuple
import random
import torch
import torch.nn as nn
from src.evaluation.metrics import compute_exact_match


class MKNIAHBenchmark:
    """
    Synthetic MK-NIAH benchmark for measuring multi-key retrieval accuracy in long sequences.
    """

    def __init__(
        self,
        vocab_size: int = 1000,
        needle_key_start: int = 100,
        needle_val_start: int = 500,
        haystack_token_start: int = 10,
        haystack_token_end: int = 90,
        seed: int = 42,
    ):
        self.vocab_size = vocab_size
        self.needle_key_start = needle_key_start
        self.needle_val_start = needle_val_start
        self.haystack_token_start = haystack_token_start
        self.haystack_token_end = haystack_token_end
        self.rng = random.Random(seed)

    def generate_sample(
        self,
        context_length: int = 256,
        num_needles: int = 4,
    ) -> Tuple[torch.Tensor, List[int], List[int]]:
        """
        Generates a sequence with `num_needles` key-value pairs distributed in a haystack.

        Returns:
            sequence_tensor: (1, total_len) containing haystack + needles + query prompt
            target_values: List of ground-truth value token IDs
            query_keys: List of queried key token IDs
        """
        # Haystack background tokens
        haystack = [
            self.rng.randint(self.haystack_token_start, self.haystack_token_end)
            for _ in range(context_length)
        ]

        # Generate unique needles (key, value)
        keys = self.rng.sample(range(self.needle_key_start, self.needle_key_start + 50), num_needles)
        vals = [self.needle_val_start + k - self.needle_key_start for k in keys]

        # Select random insertion points (sorted)
        insert_indices = sorted(self.rng.sample(range(10, context_length - 10), num_needles))

        # Insert needles
        full_tokens = []
        last_idx = 0
        for i, pos in enumerate(insert_indices):
            full_tokens.extend(haystack[last_idx:pos])
            full_tokens.extend([keys[i], vals[i]])
            last_idx = pos
        full_tokens.extend(haystack[last_idx:])

        # Append query for the first key: e.g. [key, ?]
        query_key = keys[0]
        target_val = vals[0]
        # Query format: [key]
        full_tokens.append(query_key)

        return (
            torch.tensor(full_tokens, dtype=torch.long).unsqueeze(0),
            [target_val],
            [query_key],
        )

    def evaluate_model(
        self,
        model: nn.Module,
        num_samples: int = 20,
        context_length: int = 256,
        num_needles: int = 4,
        enable_online_cms: bool = True,
        device: torch.device = None,
    ) -> Dict[str, Any]:
        """
        Runs evaluation on MK-NIAH and returns accuracy (%).
        If enable_online_cms is True and model is HopeAttentionLM, ingests document via CMS first.
        """
        model.eval()
        if device is None:
            device = next(model.parameters()).device

        from src.training.online_trainer import OnlineDocumentTrainer
        trainer = (
            OnlineDocumentTrainer(model, device=device)
            if enable_online_cms and hasattr(model, "reset_memory")
            else None
        )

        correct_predictions = 0
        target_token_probs = []

        for sample_idx in range(num_samples):
            # If model supports memory reset, reset between samples
            if hasattr(model, "reset_memory"):
                model.reset_memory()

            input_ids, target_vals, _ = self.generate_sample(
                context_length=context_length,
                num_needles=num_needles,
            )
            input_ids = input_ids.to(device)

            # Ingest document context into CMS memory if online CMS is enabled
            if trainer is not None and enable_online_cms:
                doc_tokens = input_ids[:, :-1]
                trainer.ingest_document(doc_tokens, reset_memory_first=False)

            with torch.no_grad():
                logits, _, _ = model(input_ids)
                # Next token prediction for the query token (at the last position)
                pred_token = torch.argmax(logits[0, -1, :]).item()
                prob = torch.softmax(logits[0, -1, :], dim=-1)[target_vals[0]].item()
                target_token_probs.append(prob)

            if pred_token == target_vals[0]:
                correct_predictions += 1

        accuracy_pct = (correct_predictions / num_samples) * 100.0
        avg_target_prob = sum(target_token_probs) / len(target_token_probs) if target_token_probs else 0.0

        return {
            "num_samples": num_samples,
            "context_length": context_length,
            "num_needles": num_needles,
            "enable_online_cms": enable_online_cms,
            "correct": correct_predictions,
            "accuracy_pct": accuracy_pct,
            "avg_target_prob": avg_target_prob,
        }
