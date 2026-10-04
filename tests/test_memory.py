"""
Unit tests for MemoryChunkBuffer and base memory interfaces.
"""

import pytest
from src.memory.buffer import MemoryChunkBuffer


def test_chunk_buffer_triggers():
    # 3 levels with chunk sizes: 16 (level 0), 8 (level 1), 4 (level 2)
    chunk_sizes = [16, 8, 4]
    buffer = MemoryChunkBuffer(chunk_sizes)

    # Step 1: 4 tokens
    triggers = buffer.step(4)
    # Level 2 (chunk 4) should trigger, level 0 and 1 should not
    assert triggers == [False, False, True]

    # Step 2: 4 more tokens (total 8)
    triggers = buffer.step(4)
    # Level 1 (chunk 8) and Level 2 (chunk 4) should trigger
    assert triggers == [False, True, True]

    # Step 3: 8 more tokens (total 16)
    triggers = buffer.step(8)
    # Level 0 (16), Level 1 (8), Level 2 (4) should all trigger
    assert triggers == [True, True, True]


def test_chunk_buffer_reset():
    buffer = MemoryChunkBuffer([8, 4])
    buffer.step(3)
    assert buffer.steps_since_update == [3, 3]

    buffer.reset()
    assert buffer.token_counter == 0
    assert buffer.steps_since_update == [0, 0]
