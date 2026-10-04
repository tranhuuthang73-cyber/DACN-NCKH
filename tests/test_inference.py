"""
Unit tests for text generation and autoregressive inference.
"""

import pytest
import torch
from src.hope_attention.model import HopeAttentionLM
from src.inference.generator import TextGenerator


def test_greedy_generation_length_and_shape():
    vocab_size = 50
    d_model = 32
    n_heads = 2
    n_layers = 2
    d_ff = 64

    model = HopeAttentionLM(
        vocab_size=vocab_size,
        d_model=d_model,
        n_heads=n_heads,
        n_layers=n_layers,
        d_ff=d_ff,
        num_levels=2,
        chunk_sizes=[8, 4],
        max_seq_len=64,
    )

    generator = TextGenerator(model)
    prompt = torch.tensor([[1, 2, 3, 4]], dtype=torch.long)
    max_new_tokens = 8

    generated = generator.generate(
        prompt,
        max_new_tokens=max_new_tokens,
        temperature=0.0,  # greedy
    )

    assert generated.shape == (1, 4 + max_new_tokens)
    # Check that original prompt is preserved at the beginning
    assert (generated[:, :4] == prompt).all()


def test_temperature_sampling_validity():
    vocab_size = 50
    d_model = 32
    n_heads = 2
    n_layers = 2
    d_ff = 64

    model = HopeAttentionLM(
        vocab_size=vocab_size,
        d_model=d_model,
        n_heads=n_heads,
        n_layers=n_layers,
        d_ff=d_ff,
        num_levels=2,
        chunk_sizes=[8, 4],
        max_seq_len=64,
    )

    generator = TextGenerator(model)
    prompt = torch.tensor([[10, 20]], dtype=torch.long)
    max_new_tokens = 10

    generated = generator.generate(
        prompt,
        max_new_tokens=max_new_tokens,
        temperature=0.8,
        top_k=5,
    )

    assert generated.shape == (1, 2 + max_new_tokens)
    assert (generated >= 0).all() and (generated < vocab_size).all()
