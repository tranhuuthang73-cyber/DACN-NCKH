"""
Token-Efficient Answering Engine ("Concise Evidence Mode") — Task 10.
Implements exploratory answering modes (Balanced, Concise, Minimal) designed to reduce
output token footprint while strictly preserving citations, key facts, and refusal integrity.

RULES:
- Never omit citations or key facts
- Never fabricate external knowledge
- Never convert a refusal into an answer
- No hidden chain-of-thought
- Explicitly marked as exploratory product feature (does NOT modify Phase 4.x benchmark)
"""

from typing import Tuple, Optional, List, Dict, Any


class AnswerLengthMode:
    BALANCED = "balanced"
    CONCISE = "concise"
    MINIMAL = "minimal"


def build_token_efficient_prompt(
    question: str,
    context_text: str = "",
    answer_mode: str = AnswerLengthMode.BALANCED,
    language: str = "en",
) -> Tuple[str, int]:
    """
    Constructs a prompt tailored to the requested answer length mode.
    Returns:
        (prompt_string, max_answer_tokens)
    """
    mode = (answer_mode or AnswerLengthMode.BALANCED).lower()

    if language in ("vi", "vietnamese"):
        if mode == AnswerLengthMode.MINIMAL:
            max_tokens = 24
            if context_text:
                instruction = (
                    "Dựa vào ngữ cảnh sau, trả lời câu hỏi bằng một cụm từ hoặc một câu tối thiểu cực ngắn. "
                    "BẮT BUỘC giữ nguyên trích dẫn [DOC...::P...]. Không giải thích thêm."
                )
            else:
                instruction = (
                    "Dựa vào bộ nhớ, trả lời câu hỏi thật ngắn gọn (tối đa 1 câu ngắn). Không giải thích thêm."
                )
        elif mode == AnswerLengthMode.CONCISE:
            max_tokens = 40
            if context_text:
                instruction = (
                    "Dựa vào các đoạn trích sau, hãy trả lời câu hỏi trực tiếp, súc tích trong 1-2 câu ngắn, đủ sự kiện chính. "
                    "BẮT BUỘC ghi rõ mã trích dẫn [DOC...::P...]. Không dùng từ đệm dư thừa."
                )
            else:
                instruction = (
                    "Dựa vào bộ nhớ, trả lời câu hỏi trực tiếp và súc tích trong 1-2 câu ngắn, đủ ý chính."
                )
        else:  # balanced
            max_tokens = 64
            if context_text:
                instruction = (
                    "Dựa trên các đoạn trích sau, hãy trả lời câu hỏi một cách ngắn gọn, chính xác bằng tiếng Việt. "
                    "Kèm theo trích dẫn nguồn."
                )
            else:
                instruction = (
                    "Dựa trên kiến thức trong bộ nhớ, hãy trả lời câu hỏi sau bằng tiếng Việt:"
                )

        if context_text:
            prompt = (
                f"{instruction}\n\n"
                f"Ngữ cảnh:\n{context_text}\n\n"
                f"Câu hỏi: {question}\n"
                f"Trả lời:"
            )
        else:
            prompt = (
                f"{instruction}\n\n"
                f"Câu hỏi: {question}\n"
                f"Trả lời:"
            )

    else:  # English
        if mode == AnswerLengthMode.MINIMAL:
            max_tokens = 20
            if context_text:
                instruction = (
                    "Based on the context, provide a minimal single-clause answer with source citation [DOC...::P...]. "
                    "Zero conversational filler."
                )
            else:
                instruction = "Answer minimally from memory in a single phrase. No filler."
        elif mode == AnswerLengthMode.CONCISE:
            max_tokens = 36
            if context_text:
                instruction = (
                    "Based on the context, provide a direct, fact-dense answer in 1-2 sentences with citations. "
                    "Avoid preamble and redundant phrases."
                )
            else:
                instruction = "Answer directly and concisely from memory in 1-2 sentences."
        else:  # balanced
            max_tokens = 64
            if context_text:
                instruction = "Based on the following context, answer the question accurately with citations."
            else:
                instruction = "Answer the following question based on your memory."

        if context_text:
            prompt = (
                f"{instruction}\n\n"
                f"Context:\n{context_text}\n\n"
                f"Question: {question}\n"
                f"Answer:"
            )
        else:
            prompt = (
                f"{instruction}\n\n"
                f"Question: {question}\n"
                f"Answer:"
            )

    return prompt, max_tokens


def postprocess_concise_answer(
    raw_answer: str,
    citations: List[str],
    answer_mode: str,
    refused: bool,
) -> str:
    """
    Ensures that concise/minimal answers remain grammatically sound and contain citations.
    """
    if refused or not raw_answer:
        return raw_answer

    ans = raw_answer.strip()

    # Clean repetitive loop endings common in small 135M backbones
    lines = [l.strip() for l in ans.split("\n") if l.strip()]
    if lines:
        ans = lines[0]

    # Ensure citation presence if citations list is non-empty and not in text
    if citations:
        has_cit = any(cit in ans for cit in citations)
        if not has_cit:
            ans = f"{ans} [{citations[0]}]"

    return ans
