"""
Unit tests for Causal Self-Attention module.
"""

import pytest
import torch
from src.attention.causal_attention import CausalSelfAttention


def test_attention_output_shape():
    batch_size = 2
    seq_len = 16
    d_model = 64
    n_heads = 4

    attn = CausalSelfAttention(d_model=d_model, n_heads=n_heads, max_seq_len=64)
    x = torch.randn(batch_size, seq_len, d_model)

    out, cache = attn(x, use_cache=False)
    assert out.shape == (batch_size, seq_len, d_model), f"Expected shape {(batch_size, seq_len, d_model)}, got {out.shape}"
    assert cache is None


def test_causal_masking():
    """
    Verifies that the attention is strictly causal:
    Modifying a future token does NOT affect earlier token outputs.
    """
    d_model = 32
    n_heads = 2
    attn = CausalSelfAttention(d_model=d_model, n_heads=n_heads, max_seq_len=32)
    attn.eval()

    x1 = torch.randn(1, 10, d_model)
    x2 = x1.clone()
    # Modify the last token of x2
    x2[0, -1, :] = torch.randn(d_model)

    with torch.no_grad():
        out1, _ = attn(x1)
        out2, _ = attn(x2)

    # Positions 0 to 8 must be identical
    diff = torch.max(torch.abs(out1[0, :-1, :] - out2[0, :-1, :])).item()
    assert diff < 1e-6, f"Causality violated! Max diff on preceding tokens: {diff}"


def test_kv_caching():
    """
    Verifies that autoregressive decoding with KV cache produces identical outputs
    to full-sequence forward pass.
    """
    d_model = 32
    n_heads = 2
    attn = CausalSelfAttention(d_model=d_model, n_heads=n_heads, max_seq_len=32)
    attn.eval()

    x = torch.randn(1, 6, d_model)

    # 1. Full sequence forward
    with torch.no_grad():
        full_out, _ = attn(x)

    # 2. Step-by-step cached forward
    cached_outputs = []
    kv_cache = None
    with torch.no_grad():
        for t in range(6):
            token_x = x[:, t : t + 1, :]
            step_out, kv_cache = attn(token_x, kv_cache=kv_cache, use_cache=True)
            cached_outputs.append(step_out)

    concatenated_out = torch.cat(cached_outputs, dim=1)
    diff = torch.max(torch.abs(full_out - concatenated_out)).item()
    assert diff < 1e-5, f"KV Cache output mismatch! Max diff: {diff}"
