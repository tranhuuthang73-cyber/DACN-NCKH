"""
Chunker — splits documents into retrievable passages with unique IDs.

Design:
- Sentence-aware chunking to avoid splitting mid-sentence.
- Falls back to fixed-token chunking if no sentence boundaries found.
- Assigns passage IDs in format DOC{id}::P{idx}.
- Preserves character and token offsets for citation traceability.
- Adaptive Structural Boundary Overlap: zero-overlap across paragraph boundaries
  and strict zero-overlap on section / topic boundaries (Topic N, Chủ đề N, etc.).
"""

import re
from typing import List, Optional, Tuple
from src.hybrid_qa.document_store import Passage, DocumentRecord


TOPIC_HEADING_KEYWORDS = (
    r"topic|chủ đề|chu de|bài|bai|mục|muc|chương|chuong|phần|phan|section|chapter|lesson|unit"
)


class DocumentChunker:
    """
    Chunks a document into passages suitable for retrieval.
    Supports sentence-aware and fixed-size chunking strategies.
    Strictly enforces structural isolation on heading / topic boundaries.
    """

    SENTENCE_BOUNDARY = re.compile(
        r'(?<=[.!?])\s+(?=[A-Z\u00C0-\u024F])|'  # Period/excl/question + space + uppercase
        r'(?<=\n)\s*\n+'                             # Blank line
    )

    # Shared Heading Regex: recognizes Markdown headers, topic headers, and numbered sections
    HEADING_RE = re.compile(
        rf"^\s*(?:#{{1,6}}\s+\S.*|(?:{TOPIC_HEADING_KEYWORDS})\s*\d+\s*[:.\-–].*|\d+(?:\.\d+)*\.\s+[A-ZÀ-Ỹ].*)$",
        re.MULTILINE | re.IGNORECASE,
    )

    # Heading Finder Regex: locates headings occurring at line start or inline after sentence boundaries
    HEADING_FINDER = re.compile(
        rf"(?:^|(?<=[\n.!?]))\s*(?P<heading>(?:#{{1,6}}\s+\S[^\n]*|(?:{TOPIC_HEADING_KEYWORDS})\s*\d+\s*[:.\-–][^\n]*|\d+(?:\.\d+)*\.\s+[A-ZÀ-Ỹ][^\n]*))",
        re.IGNORECASE | re.MULTILINE,
    )

    ABBREVIATIONS = {
        "tp.", "ts.", "pgs.", "gs.", "ths.", "ks.", "cn.", "bs.", "đc.", "tr.",
        "dr.", "mr.", "mrs.", "ms.", "prof.", "fig.", "eq.", "sec.", "vol.", "no.", "vs.", "al.",
    }

    def __init__(
        self,
        chunk_size: int = 256,
        chunk_overlap: int = 32,
        min_chunk_size: int = 64,
        strategy: str = "sentence",  # "sentence" or "fixed"
        adaptive_overlap: bool = True,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self.strategy = strategy
        self.adaptive_overlap = adaptive_overlap

    @classmethod
    def is_heading(cls, text: str) -> bool:
        """Checks if a string represents or starts with a recognized section/topic heading."""
        if not text:
            return False
        clean = text.strip()
        first_line = clean.split("\n")[0].strip()
        return bool(cls.HEADING_RE.match(first_line))

    def chunk_document(self, doc: DocumentRecord) -> List[Passage]:
        """
        Chunk a document into passages and assign unique IDs.
        Returns list of Passage objects with DOC{id}::P{idx} identifiers.
        """
        text = doc.raw_text
        if not text.strip():
            return []

        if self.strategy == "sentence":
            raw_chunks = self._sentence_chunk(text)
        else:
            raw_chunks = self._fixed_chunk(text)

        passages = []
        for idx, (chunk_text, start_char, end_char) in enumerate(raw_chunks):
            passage_id = f"{doc.document_id}::P{idx:03d}"
            section_title = self._find_section_title(text, start_char)
            section_id = self._find_section_id(text, start_char)
            paragraph_id = self._find_paragraph_id(text, start_char)

            metadata = {
                "section_id": section_id,
                "paragraph_id": paragraph_id,
                "document_version": doc.version,
            }
            if doc.metadata:
                for k, v in doc.metadata.items():
                    if k not in metadata:
                        metadata[k] = v

            passages.append(Passage(
                passage_id=passage_id,
                document_id=doc.document_id,
                text=chunk_text,
                start_char=start_char,
                end_char=end_char,
                section_title=section_title,
                metadata=metadata,
            ))

        return passages

    def _sentence_chunk(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Sentence-aware chunking with Adaptive Structural Boundary Overlap:
        - If a candidate sentence is a section/topic heading (HEADING_RE), the accumulated
          sentences are immediately flushed with ZERO overlap. Overlap never crosses a heading.
        - If a chunk ends at a natural paragraph boundary (blank line) or before a new section heading,
          overlap is set to 0 to eliminate redundant token duplication across paragraphs.
        - If a single long paragraph is split mid-paragraph, sentence overlap is preserved.
        """
        sentences = self._split_sentences(text)
        if not sentences:
            return self._fixed_chunk(text)

        chunks = []
        current_sentences = []
        current_len = 0
        current_start = 0

        for sent_text, sent_start, sent_end in sentences:
            sent_len = len(sent_text)
            sent_is_heading = self.is_heading(sent_text)

            # RULE: A heading must never be conjoined with previous section/topic sentences!
            if sent_is_heading and current_sentences:
                chunk_text = " ".join(s[0] for s in current_sentences)
                chunk_start = current_sentences[0][1]
                chunk_end = current_sentences[-1][2]
                chunks.append((chunk_text.strip(), chunk_start, chunk_end))
                # Strict ZERO overlap across heading boundaries
                current_sentences = []
                current_len = 0
                current_start = sent_start

            elif current_len + sent_len > self.chunk_size and current_sentences:
                # Emit current chunk
                chunk_text = " ".join(s[0] for s in current_sentences)
                chunk_start = current_sentences[0][1]
                chunk_end = current_sentences[-1][2]
                chunks.append((chunk_text.strip(), chunk_start, chunk_end))

                # Check if boundary between chunk_end and sent_start is a natural paragraph/section break
                gap_text = text[chunk_end:sent_start] if sent_start >= chunk_end else ""
                is_natural_boundary = ("\n\n" in gap_text) or sent_text.lstrip().startswith("#") or sent_is_heading

                if self.adaptive_overlap and is_natural_boundary:
                    # Zero-overlap on natural structural boundaries to save tokens
                    current_sentences = []
                    current_len = 0
                    current_start = sent_start
                else:
                    # Mid-paragraph split: keep last few sentences for continuity,
                    # but never allow overlap to step backward across a heading
                    overlap_len = 0
                    overlap_start = len(current_sentences)
                    for i in range(len(current_sentences) - 1, -1, -1):
                        if self.is_heading(current_sentences[i][0]):
                            overlap_start = i
                            break
                        overlap_len += len(current_sentences[i][0])
                        if overlap_len >= self.chunk_overlap:
                            overlap_start = i
                            break

                    current_sentences = current_sentences[overlap_start:]
                    current_len = sum(len(s[0]) for s in current_sentences)
                    current_start = current_sentences[0][1] if current_sentences else sent_start

            current_sentences.append((sent_text, sent_start, sent_end))
            current_len += sent_len

        # Emit remaining
        if current_sentences:
            chunk_text = " ".join(s[0] for s in current_sentences)
            chunk_start = current_sentences[0][1]
            chunk_end = current_sentences[-1][2]
            if len(chunk_text.strip()) >= self.min_chunk_size:
                chunks.append((chunk_text.strip(), chunk_start, chunk_end))
            elif chunks:
                # Only merge trailing chunk if both chunks share the same section and neither is a heading
                prev_text, prev_start, prev_end = chunks[-1]
                prev_sec = self._find_section_title(text, prev_start)
                curr_sec = self._find_section_title(text, chunk_start)
                if prev_sec == curr_sec and not any(self.is_heading(s[0]) for s in current_sentences):
                    chunks[-1] = (prev_text + " " + chunk_text.strip(), prev_start, chunk_end)
                else:
                    chunks.append((chunk_text.strip(), chunk_start, chunk_end))
            else:
                chunks.append((chunk_text.strip(), chunk_start, chunk_end))

        return chunks

    def _fixed_chunk(self, text: str) -> List[Tuple[str, int, int]]:
        """Fixed-size character chunking with overlap."""
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk_text = text[start:end]
            if chunk_text.strip():
                chunks.append((chunk_text.strip(), start, end))
            start += self.chunk_size - self.chunk_overlap
        return chunks

    def _split_sentences(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Split text into (sentence_text, start_char, end_char) tuples.
        Protects common Vietnamese/English abbreviations and numbering from false splits.
        Isolates section headings (Markdown, Topic N, Chủ đề N, etc.) as distinct units.
        """
        if not text.strip():
            return []

        boundaries: List[Tuple[int, int, str]] = []

        # 1. Standard sentence boundary matches (punctuation + space + uppercase, or \n\n)
        for match in self.SENTENCE_BOUNDARY.finditer(text):
            boundaries.append((match.start(), match.end(), "std"))

        # 2. Structural heading boundaries (lines or inline occurrences)
        for match in self.HEADING_FINDER.finditer(text):
            h_start = match.start("heading")
            h_end = match.end("heading")
            if h_start > 0:
                boundaries.append((h_start, h_start, "head_start"))
            next_pos = h_end
            while next_pos < len(text) and text[next_pos] in " \t\r\n":
                next_pos += 1
            boundaries.append((h_end, next_pos, "head_end"))

        # Sort and merge overlapping / adjacent split boundaries
        boundaries.sort(key=lambda x: (x[0], x[1]))
        merged: List[List[Any]] = []
        for b_start, b_end, b_type in boundaries:
            if not merged:
                merged.append([b_start, b_end, b_type])
            else:
                prev = merged[-1]
                if b_start <= prev[1]:
                    prev[1] = max(prev[1], b_end)
                    if b_type != "std":
                        prev[2] = b_type
                else:
                    merged.append([b_start, b_end, b_type])

        sentences = []
        last_end = 0
        for b_start, b_end, b_type in merged:
            segment = text[last_end:b_start]
            cand = segment.strip()
            if not cand:
                last_end = max(last_end, b_end)
                continue

            # Check if split occurred right after an abbreviation (e.g. 'TS.', 'Tp.', 'Fig.')
            last_word = cand.split()[-1].lower() if cand.split() else ""
            if last_word in self.ABBREVIATIONS and b_type == "std" and "\n" not in text[b_start:b_end]:
                continue

            lead = len(segment) - len(segment.lstrip())
            s_start = last_end + lead
            s_end = s_start + len(cand)
            sentences.append((cand, s_start, s_end))
            last_end = max(last_end, b_end)

        remaining = text[last_end:]
        if remaining.strip():
            cand = remaining.strip()
            lead = len(remaining) - len(remaining.lstrip())
            s_start = last_end + lead
            sentences.append((cand, s_start, s_start + len(cand)))

        return sentences

    @classmethod
    def _find_section_title(cls, full_text: str, char_pos: int) -> str:
        """Find the nearest preceding section heading for a character position."""
        best_title = ""
        best_pos = -1
        for match in cls.HEADING_FINDER.finditer(full_text):
            h_start = match.start("heading")
            if h_start <= (char_pos + 2) and h_start > best_pos:
                best_pos = h_start
                best_title = match.group("heading").strip().lstrip("#").strip()
        return best_title

    @classmethod
    def _find_section_id(cls, full_text: str, char_pos: int) -> str:
        """Find the section ID (e.g. SEC001) for a character position."""
        headings = []
        for match in cls.HEADING_FINDER.finditer(full_text):
            headings.append((match.start("heading"), match.group("heading").strip()))
        headings.sort(key=lambda x: x[0])

        sec_idx = 0
        for i, (pos, _) in enumerate(headings):
            if pos <= (char_pos + 2):
                sec_idx = i + 1
            else:
                break
        return f"SEC{sec_idx:03d}"

    @staticmethod
    def _find_paragraph_id(full_text: str, char_pos: int) -> str:
        """Find the paragraph ID (e.g. PARA001) for a character position."""
        prefix = full_text[:char_pos]
        paras = re.split(r'\n\s*\n+', prefix.strip())
        para_idx = len(paras) if paras and paras[0] else 1
        return f"PARA{para_idx:03d}"
