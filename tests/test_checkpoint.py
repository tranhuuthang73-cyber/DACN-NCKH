"""
Unit tests for checkpoint saving and loading.
"""

import os
import tempfile
import pytest
import torch
from src.hope_attention.model import HopeAttentionLM
from src.utils.checkpoint import save_checkpoint, load_checkpoint


def test_checkpoint_save_and_load():
    with tempfile.TemporaryDirectory() as tmpdir:
        ckpt_path = os.path.join(tmpdir, "test_model.pt")

        vocab_size = 50
        d_model = 32
        n_heads = 2
        n_layers = 2
        d_ff = 64

        model1 = HopeAttentionLM(
            vocab_size=vocab_size,
            d_model=d_model,
            n_heads=n_heads,
            n_layers=n_layers,
            d_ff=d_ff,
            num_levels=2,
            chunk_sizes=[8, 4],
            max_seq_len=32,
        )

        # Perturb one parameter to ensure it's not default zeros
        with torch.no_grad():
            model1.embedding.tok_emb.weight.add_(0.5)

        # Save checkpoint
        save_checkpoint(
            model=model1,
            save_path=ckpt_path,
            step=10,
            config={"num_levels": 2},
            metrics={"loss": 2.5},
        )
        assert os.path.exists(ckpt_path), "Checkpoint file was not created"

        # Initialize fresh model with different initial weights
        model2 = HopeAttentionLM(
            vocab_size=vocab_size,
            d_model=d_model,
            n_heads=n_heads,
            n_layers=n_layers,
            d_ff=d_ff,
            num_levels=2,
            chunk_sizes=[8, 4],
            max_seq_len=32,
        )

        # Verify weights differ initially
        diff_before = torch.norm(model1.embedding.tok_emb.weight - model2.embedding.tok_emb.weight).item()
        assert diff_before > 1e-4

        # Load checkpoint
        loaded = load_checkpoint(ckpt_path, model2)
        assert loaded["step"] == 10
        assert loaded["metrics"]["loss"] == 2.5

        # Verify weights are identical after loading
        diff_after = torch.norm(model1.embedding.tok_emb.weight - model2.embedding.tok_emb.weight).item()
        assert diff_after == 0.0, f"Loaded weights do not match original! Diff: {diff_after}"
