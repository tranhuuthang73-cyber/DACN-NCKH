"""
Document QA micro-benchmark measuring perplexity and answer loss over long context.
Paper Section 9.1 & Figure 7 (Right): Evaluates QASPER-style document QA.
"""

from typing import Dict, Any, List, Tuple
import random
import torch
import torch.nn as nn
from src.training.loss import compute_next_token_loss, compute_perplexity
from src.training.online_trainer import OnlineDocumentTrainer


class DocumentQABenchmark:
    """
    Synthetic Document QA benchmark that evaluates next-token loss and perplexity
    on long structured documents with and without CMS memory updates.
    """

    def __init__(
        self,
        vocab_size: int = 1000,
        doc_length: int = 512,
        seed: int = 42,
    ):
        self.vocab_size = vocab_size
        self.doc_length = doc_length
        self.rng = random.Random(seed)

    def generate_document_qa_pair(
        self,
        doc_len: int = 512,
        qa_len: int = 32,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Generates a document context and an associated QA sequence.
        Returns:
            document_tokens: (1, doc_len)
            qa_tokens: (1, qa_len)
        """
        doc = [self.rng.randint(5, self.vocab_size - 10) for _ in range(doc_len)]
        # Pick a salient slice from doc to serve as answer anchor
        anchor_start = self.rng.randint(0, doc_len - 16)
        anchor = doc[anchor_start:anchor_start + 16]

        qa = [self.rng.randint(1, 4)] + anchor + [self.rng.randint(1, 4)]
        if len(qa) < qa_len:
            qa.extend([self.rng.randint(5, 50) for _ in range(qa_len - len(qa))])
        else:
            qa = qa[:qa_len]

        return (
            torch.tensor(doc, dtype=torch.long).unsqueeze(0),
            torch.tensor(qa, dtype=torch.long).unsqueeze(0),
        )

    def evaluate_model(
        self,
        model: nn.Module,
        num_docs: int = 5,
        doc_len: int = 256,
        qa_len: int = 32,
        enable_online_cms: bool = True,
        device: torch.device = None,
    ) -> Dict[str, Any]:
        """
        Evaluates model on document QA sequences.
        If enable_online_cms is True and model is HopeAttentionLM, ingests document via CMS first.
        """
        model.eval()
        if device is None:
            device = next(model.parameters()).device

        trainer = OnlineDocumentTrainer(model, device=device) if enable_online_cms and hasattr(model, "reset_memory") else None

        all_qa_losses: List[float] = []

        for _ in range(num_docs):
            if hasattr(model, "reset_memory"):
                model.reset_memory()

            doc_tokens, qa_tokens = self.generate_document_qa_pair(doc_len=doc_len, qa_len=qa_len)
            doc_tokens = doc_tokens.to(device)
            qa_tokens = qa_tokens.to(device)

            # Ingest document if online CMS enabled
            if trainer is not None and enable_online_cms:
                trainer.ingest_document(doc_tokens, reset_memory_first=False)

            # Evaluate on QA sequence
            inputs = qa_tokens[:, :-1]
            targets = qa_tokens[:, 1:]

            with torch.no_grad():
                logits, loss, _ = model(inputs, targets=targets)
                all_qa_losses.append(loss.item())

        avg_loss = sum(all_qa_losses) / len(all_qa_losses) if all_qa_losses else 0.0
        ppl = compute_perplexity(avg_loss)

        return {
            "num_docs": num_docs,
            "doc_len": doc_len,
            "qa_len": qa_len,
            "enable_online_cms": enable_online_cms,
            "avg_loss": avg_loss,
            "perplexity": ppl,
        }
