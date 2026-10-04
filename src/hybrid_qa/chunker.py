"""
Chunker — splits documents into retrievable passages with unique IDs.

Design:
- Sentence-aware chunking to avoid splitting mid-sentence.
- Falls back to fixed-token chunking if no sentence boundaries found.
- Assigns passage IDs in format DOC{id}::P{idx}.
- Preserves character and token offsets for citation traceability.
"""

import re
from typing import List, Optional, Tuple
from src.hybrid_qa.document_store import Passage, DocumentRecord


class DocumentChunker:
    """
    Chunks a document into passages suitable for retrieval.
    Supports sentence-aware and fixed-size chunking strategies.
    """

    SENTENCE_BOUNDARY = re.compile(
        r'(?<=[.!?])\s+(?=[A-Z\u00C0-\u024F])|'  # Period/excl/question + space + uppercase
        r'(?<=\n)\s*\n+'                             # Blank line
    )

    def __init__(
        self,
        chunk_size: int = 256,
        chunk_overlap: int = 32,
        min_chunk_size: int = 64,
        strategy: str = "sentence",  # "sentence" or "fixed"
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self.strategy = strategy

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
        """Sentence-aware chunking with overlap."""
        # Split into sentences
        sentences = self._split_sentences(text)
        if not sentences:
            return self._fixed_chunk(text)

        chunks = []
        current_sentences = []
        current_len = 0
        current_start = 0

        for sent_text, sent_start, sent_end in sentences:
            sent_len = len(sent_text)

            if current_len + sent_len > self.chunk_size and current_sentences:
                # Emit current chunk
                chunk_text = " ".join(s[0] for s in current_sentences)
                chunk_start = current_sentences[0][1]
                chunk_end = current_sentences[-1][2]
                chunks.append((chunk_text.strip(), chunk_start, chunk_end))

                # Overlap: keep last few sentences
                overlap_len = 0
                overlap_start = len(current_sentences)
                for i in range(len(current_sentences) - 1, -1, -1):
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
                # Merge short trailing chunk with previous
                prev_text, prev_start, prev_end = chunks[-1]
                chunks[-1] = (prev_text + " " + chunk_text.strip(), prev_start, chunk_end)

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
        """Split text into (sentence_text, start_char, end_char) tuples."""
        sentences = []
        last_end = 0
        for match in self.SENTENCE_BOUNDARY.finditer(text):
            sent_text = text[last_end:match.start()].strip()
            if sent_text:
                sentences.append((sent_text, last_end, match.start()))
            last_end = match.end()

        # Last sentence
        remaining = text[last_end:].strip()
        if remaining:
            sentences.append((remaining, last_end, len(text)))

        return sentences

    @staticmethod
    def _find_section_title(full_text: str, char_pos: int) -> str:
        """Find the nearest preceding section heading for a character position."""
        heading_patterns = [
            re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE),
            re.compile(r"^(\d+(\.\d+)*)\.\s+([A-Z][^\n]+)$", re.MULTILINE),
        ]
        best_title = ""
        best_pos = -1
        for pattern in heading_patterns:
            for match in pattern.finditer(full_text):
                if match.start() <= char_pos and match.start() > best_pos:
                    best_pos = match.start()
                    best_title = match.group(0).strip().lstrip("#").strip()
        return best_title

    @staticmethod
    def _find_section_id(full_text: str, char_pos: int) -> str:
        """Find the section ID (e.g. SEC001) for a character position."""
        heading_patterns = [
            re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE),
            re.compile(r"^(\d+(\.\d+)*)\.\s+([A-Z][^\n]+)$", re.MULTILINE),
        ]
        headings = []
        for pattern in heading_patterns:
            for match in pattern.finditer(full_text):
                headings.append((match.start(), match.group(0).strip()))
        headings.sort(key=lambda x: x[0])

        sec_idx = 0
        for i, (pos, _) in enumerate(headings):
            if pos <= char_pos:
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

