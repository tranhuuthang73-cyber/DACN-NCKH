"""
Unit tests for HopeAttentionBlock and HopeAttentionLM.
"""

import pytest
import torch
from src.hope_attention.block import HopeAttentionBlock
from src.hope_attention.model import HopeAttentionLM


def test_hope_attention_block_forward():
    d_model = 64
    n_heads = 4
    d_ff = 128
    block = HopeAttentionBlock(
        d_model=d_model,
        n_heads=n_heads,
        d_ff=d_ff,
        num_levels=3,
        chunk_sizes=[16, 8, 4],
        max_seq_len=64,
    )

    x = torch.randn(2, 10, d_model)
    out, cache = block(x, use_cache=False)
    assert out.shape == (2, 10, d_model)
    assert cache is None


def test_hope_attention_lm_forward_and_loss():
    vocab_size = 100
    d_model = 64
    n_heads = 4
    n_layers = 2
    d_ff = 128

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

    input_ids = torch.randint(0, vocab_size, (2, 8))
    targets = torch.randint(0, vocab_size, (2, 8))

    logits, loss, _ = model(input_ids, targets=targets)
    assert logits.shape == (2, 8, vocab_size)
    assert loss is not None
    assert loss.item() > 0.0


def test_hope_attention_lm_cms_update():
    """
    Verifies that calling update_cms_online on HopeAttentionLM updates
    the scheduled CMS levels across layers.
    """
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
        max_seq_len=32,
    )

    input_ids = torch.randint(0, vocab_size, (1, 4))
    targets = torch.randint(0, vocab_size, (1, 4))

    logits, loss, _ = model(input_ids, targets=targets)
    # Advancing by 4 tokens: level 1 (chunk size 4) should update
    layer_updates = model.update_cms_online(loss, num_tokens=4)

    assert 0 in layer_updates
    assert 1 in layer_updates
    assert layer_updates[0] == [1]
    assert layer_updates[1] == [1]
