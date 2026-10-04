"""
Unit tests for Continuum Memory System (CMS) chains, schedule, and Equation 71 updates.
"""

import pytest
import torch
from src.cms.schedule import CMSSchedule
from src.cms.mlp_chain import SequentialMLPChain, IndependentMLPChain, MLPBlock
from src.cms.continuum_memory import ContinuumMemorySystem


def test_cms_schedule_hierarchy():
    schedule = CMSSchedule(num_levels=3, lowest_chunk_size=64)
    assert schedule.chunk_sizes == [64, 32, 16]
    assert schedule.frequencies == [1.0, 2.0, 4.0]
    assert schedule.get_chunk_size(0) == 64
    assert schedule.get_chunk_size(2) == 16


def test_sequential_mlp_chain_forward():
    d_model = 64
    d_ff = 128
    chain = SequentialMLPChain(num_levels=3, d_model=d_model, d_ff=d_ff)
    x = torch.randn(2, 8, d_model)
    out = chain(x)
    assert out.shape == (2, 8, d_model)


def test_independent_mlp_chain_forward():
    d_model = 64
    d_ff = 128
    chain = IndependentMLPChain(num_levels=3, d_model=d_model, d_ff=d_ff)
    x = torch.randn(2, 8, d_model)
    out = chain(x)
    assert out.shape == (2, 8, d_model)


def test_cms_equation_71_update_and_reset():
    """
    Tests that:
    1. ContinuumMemorySystem executes gradient update according to Equation 71 when chunk boundary is met.
    2. Parameters actually change after update.
    3. reset_memory() restores parameters exactly to initial theta_0.
    """
    d_model = 32
    d_ff = 64
    cms = ContinuumMemorySystem(
        d_model=d_model,
        d_ff=d_ff,
        num_levels=2,
        chunk_sizes=[8, 4],  # level 0 updates at 8 tokens, level 1 updates at 4 tokens
        base_lr=0.01,
    )

    # Initial state of Level 1 W1 weight
    initial_w1 = cms.chain.blocks[1].w1.weight.clone()

    x = torch.randn(1, 4, d_model, requires_grad=True)
    out = cms(x)
    dummy_loss = out.sum()

    # Advancing by 4 tokens: level 1 (chunk=4) must update, level 0 (chunk=8) must not
    updated_levels = cms.update_scheduled_levels(dummy_loss, num_tokens=4)
    assert updated_levels == [1], f"Expected only level 1 to update, got: {updated_levels}"

    # Verify that level 1 parameter changed
    updated_w1 = cms.chain.blocks[1].w1.weight
    diff = torch.norm(updated_w1 - initial_w1).item()
    assert diff > 1e-4, f"Parameter should have changed, but diff is {diff}"

    # Verify that reset_memory restores initial state
    cms.reset_memory()
    reset_w1 = cms.chain.blocks[1].w1.weight
    reset_diff = torch.norm(reset_w1 - initial_w1).item()
    assert reset_diff == 0.0, f"Reset memory did not restore initial weights! Diff: {reset_diff}"
