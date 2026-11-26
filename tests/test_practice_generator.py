import os
from unittest.mock import MagicMock, patch

from src.web.practice_generator import (
    generate_practice_content,
    is_online_llm_enabled,
    is_practice_generation_query,
)


def test_practice_intent_detection():
    assert is_practice_generation_query("sinh thêm ví dụ tương tự và bài tập")
    assert is_practice_generation_query("tạo bài tập về công thức bảo toàn electron")
    assert is_practice_generation_query("cho thêm ví dụ giống bài này")
    assert not is_practice_generation_query("chất oxi hóa là gì")
    assert not is_practice_generation_query("tóm tắt nội dung chính của bài 2")


def test_offline_redox_generation():
    ctx = (
        "Định luật Bảo toàn Electron: ∑ n(e nhường) = ∑ n(e nhận). "
        "n = V / 24,79. Ví dụ 2.1: Hòa tan 11,2 gam Fe vào HNO3 thu được V lít NO."
    )
    res = generate_practice_content(
        query="sinh thêm ví dụ và bài tập tương tự về bảo toàn electron",
        context_text=ctx,
        mode="offline",
        seed=42,
    )
    assert res["engine"] == "offline_symbolic_template"
    assert res["domain"] == "chemistry_redox"
    assert "Ví dụ tương tự" in res["answer"]
    assert "Bài tập tự luyện" in res["answer"]
    assert "Đáp án kiểm tra" in res["answer"]


def test_offline_dna_generation():
    ctx = (
        "Chiều dài ADN: L = (N / 2) × 3,4. Liên kết hydro: H = 2A + 3G. "
        "Số nucleotide môi trường cung cấp: N_mt = N × (2^k - 1)."
    )
    res = generate_practice_content(
        query="tạo bài tập và ví dụ tương tự về công thức ADN",
        context_text=ctx,
        mode="offline",
        seed=7,
    )
    assert res["engine"] == "offline_symbolic_template"
    assert res["domain"] == "biology_dna"
    assert "Ví dụ tương tự" in res["answer"]
    assert "Bài tập tự luyện" in res["answer"]


def test_offline_crypto_generation():
    ctx = (
        "Công thức mã hóa affine: E(x) = (a * x + b) mod 26.\n"
        "Ví dụ 1: Cho a = 5, b = 8, x = 2 thì E(2) = 18."
    )
    res = generate_practice_content(
        query="sinh thêm ví dụ tương tự và bài tập",
        context_text=ctx,
        mode="offline",
        seed=1,
    )
    assert res["engine"] == "offline_symbolic_template"
    assert res["domain"] == "cryptography_classical"
    assert "mod 26" in res["answer"]
    assert "Bài tập tự luyện" in res["answer"]


def test_offline_generic_formula_generation():
    ctx = (
        "Định luật II Newton: F = m * a.\n"
        "Ví dụ 1: Một vật khối lượng m = 2 kg chịu gia tốc a = 3 m/s² thì lực F = 6 N."
    )
    res = generate_practice_content(
        query="sinh thêm ví dụ tương tự và bài tập",
        context_text=ctx,
        mode="offline",
        seed=1,
    )
    assert res["engine"] == "offline_symbolic_template"
    assert res["domain"] == "generic_formula"
    assert "F = m * a" in res["answer"]
    assert "Bài tập tự luyện gợi ý" in res["answer"]


def test_online_self_built_symbolic_no_external_llm(monkeypatch):
    """Verifies external LLM APIs remain strictly disabled even if env vars are set, using local SymPy + fallback."""
    monkeypatch.setenv("SA_CMS_ONLINE_LLM", "1")
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    assert is_online_llm_enabled() is False

    res = generate_practice_content(
        query="sinh thêm ví dụ và bài tập về bảo toàn electron",
        context_text="Định luật Bảo toàn Electron: ∑ n(e nhường) = ∑ n(e nhận).",
        mode="online",
        seed=42,
    )
    assert "SymbolicFormulaLab" in res["engine"]
    assert "Bài 1" in res["answer"]

    # Biology DNA falls back cleanly to local template generator (zero external APIs)
    res_dna = generate_practice_content(
        query="tạo bài tập và ví dụ tương tự về công thức ADN",
        context_text="Chiều dài ADN: L = (N / 2) × 3,4. Liên kết hydro: H = 2A + 3G.",
        mode="online",
        seed=7,
    )
    assert res_dna["engine"] in ("offline_symbolic_fallback", "SymbolicFormulaLab-SymPy-SelfBuilt")
    assert "Bài" in res_dna["answer"]
