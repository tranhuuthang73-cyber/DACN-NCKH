"""
Pytest integration for smoke test.
"""

from smoke_test import run_smoke_test


def test_full_smoke_pipeline():
    assert run_smoke_test() is True
