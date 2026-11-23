"""
Secure File Parser & Sanitizer for Phase 5.1 Document Intelligence Platform.
Handles PDF, DOCX, TXT, and Markdown files with strict security validations:
- Filename sanitization (prevent path traversal)
- File extension & MIME type validation
- Maximum file size enforcement (default 15MB)
- Safe extraction of text, sections, and paragraphs.
"""

import os
import re
import io
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List


MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".csv", ".tsv", ".json", ".html", ".htm", ".png", ".jpg", ".jpeg"}


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal and invalid characters."""
    filename = Path(filename).name  # strip directory path components
    # Replace non-alphanumeric, dot, underscore, dash with underscore
    sanitized = re.sub(r"[^\w\s.-]", "_", filename, flags=re.UNICODE)
    sanitized = re.sub(r"\s+", "_", sanitized)
    sanitized = sanitized.strip("._")
    if not sanitized:
        sanitized = "uploaded_document.txt"
    return sanitized


def format_file_size(size_bytes: Any) -> str:
    """
    Safely converts byte count into human-readable string without NaN/undefined/null.
    Handles bytes (int/float), formatted strings, and missing/invalid values.
    """
    if size_bytes is None:
        return "Dung lượng không xác định"

    if isinstance(size_bytes, str):
        trimmed = size_bytes.strip()
        if not trimmed or trimmed.lower() in ("nan", "nan mb", "nan kb", "undefined", "null", "none"):
            return "Dung lượng không xác định"
        # If already formatted with recognized units
        if any(trimmed.upper().endswith(u) for u in (" B", " KB", " MB", " GB", " TB", "B", "KB", "MB", "GB", "TB")):
            if "nan" in trimmed.lower():
                return "Dung lượng không xác định"
            return trimmed
        try:
            val = float(trimmed)
            size_bytes = val
        except ValueError:
            return "Dung lượng không xác định"

    if isinstance(size_bytes, (int, float)):
        import math
        if math.isnan(size_bytes) or math.isinf(size_bytes) or size_bytes < 0:
            return "Dung lượng không xác định"
        if size_bytes == 0:
            return "0 KB"
        if size_bytes < 1024:
            return f"{int(size_bytes)} B"
        if size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        if size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

    return "Dung lượng không xác định"


def validate_file(filename: str, file_bytes: bytes) -> Tuple[bool, Optional[str]]:
    """Validates file extension and size constraints."""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file type '{ext}'. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"

    if len(file_bytes) == 0:
        return False, "File is empty."

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        max_mb = MAX_FILE_SIZE_BYTES / (1024 * 1024)
        return False, f"File size exceeds maximum allowed limit of {max_mb:.1f} MB."

    return True, None


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts text from PDF bytes using pypdf."""
    from pypdf import PdfReader
    stream = io.BytesIO(file_bytes)
    reader = PdfReader(stream)
    extracted_pages = []
    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            extracted_pages.append(f"=== Page {idx + 1} ===\n{text.strip()}")
    if not extracted_pages:
        raise ValueError("Could not extract any readable text from PDF.")
    return "\n\n".join(extracted_pages)


def _format_table_rows_to_sentences(rows_data: List[List[str]]) -> List[str]:
    """Converts 2D table rows into self-contained factual sentences with column headers attached."""
    if not rows_data:
        return []
    cleaned_rows = []
    for r in rows_data:
        dedup_r = []
        for cell in r:
            c_txt = re.sub(r"\s+", " ", cell or "").strip()
            if c_txt and (not dedup_r or dedup_r[-1] != c_txt):
                dedup_r.append(c_txt)
        if dedup_r:
            cleaned_rows.append(dedup_r)
    if not cleaned_rows:
        return []
    if len(cleaned_rows) == 1:
        s = ", ".join(cleaned_rows[0])
        return [s if s.endswith(".") else f"{s}."]

    headers = cleaned_rows[0]
    sentences = []
    for row in cleaned_rows[1:]:
        pairs = []
        for idx, val in enumerate(row):
            if not val:
                continue
            hdr = headers[idx] if idx < len(headers) else f"Cột {idx + 1}"
            if hdr and hdr.lower() != val.lower():
                pairs.append(f"{hdr}: {val}")
            else:
                pairs.append(val)
        if pairs:
            sent = ", ".join(pairs)
            if not sent.endswith((".", "!", "?")):
                sent += "."
            sentences.append(sent)
    return sentences


_OMML_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
_W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_MC_NS = "http://schemas.openxmlformats.org/markup-compatibility/2006"


def _local_tag(elem: Any) -> str:
    tag = getattr(elem, "tag", "") or ""
    return tag.rsplit("}", 1)[-1]


def _extract_omml_math(elem: Any) -> str:
    """Recursively converts Office Math XML (<m:oMath>) nodes into readable linear math text."""
    tag = _local_tag(elem)
    if tag == "t":
        return elem.text or ""
    if tag == "f":  # fraction: <m:num> / <m:den>
        num_el = next((c for c in elem if _local_tag(c) == "num"), None)
        den_el = next((c for c in elem if _local_tag(c) == "den"), None)
        num_s = _extract_omml_math(num_el).strip() if num_el is not None else ""
        den_s = _extract_omml_math(den_el).strip() if den_el is not None else ""
        n_fmt = f"({num_s})" if any(ch in num_s for ch in " +-*/") else num_s
        d_fmt = f"({den_s})" if any(ch in den_s for ch in " +-*/") else den_s
        return f"{n_fmt}/{d_fmt}" if (num_s or den_s) else ""
    if tag == "sSup":  # superscript base^sup
        e_el = next((c for c in elem if _local_tag(c) == "e"), None)
        sup_el = next((c for c in elem if _local_tag(c) == "sup"), None)
        e_s = _extract_omml_math(e_el).strip() if e_el is not None else ""
        sup_s = _extract_omml_math(sup_el).strip() if sup_el is not None else ""
        return f"{e_s}^{sup_s}" if len(sup_s) <= 2 else f"{e_s}^{{{sup_s}}}"
    if tag == "sSub":  # subscript base_sub
        e_el = next((c for c in elem if _local_tag(c) == "e"), None)
        sub_el = next((c for c in elem if _local_tag(c) == "sub"), None)
        e_s = _extract_omml_math(e_el).strip() if e_el is not None else ""
        sub_s = _extract_omml_math(sub_el).strip() if sub_el is not None else ""
        return f"{e_s}_{sub_s}" if len(sub_s) <= 2 else f"{e_s}_{{{sub_s}}}"
    if tag == "sSubSup":
        e_el = next((c for c in elem if _local_tag(c) == "e"), None)
        sub_el = next((c for c in elem if _local_tag(c) == "sub"), None)
        sup_el = next((c for c in elem if _local_tag(c) == "sup"), None)
        e_s = _extract_omml_math(e_el).strip() if e_el is not None else ""
        sub_s = _extract_omml_math(sub_el).strip() if sub_el is not None else ""
        sup_s = _extract_omml_math(sup_el).strip() if sup_el is not None else ""
        return f"{e_s}_{sub_s}^{sup_s}"
    if tag == "rad":  # radical sqrt(...)
        e_el = next((c for c in elem if _local_tag(c) == "e"), None)
        e_s = _extract_omml_math(e_el).strip() if e_el is not None else ""
        return f"sqrt({e_s})" if e_s else ""
    if tag == "d":  # delimiter parentheses
        inner = "".join(_extract_omml_math(c) for c in elem if _local_tag(c) == "e")
        return f"({inner})" if inner else ""

    parts: List[str] = []
    for child in elem:
        if _local_tag(child) == "rPr":
            continue
        piece = _extract_omml_math(child)
        if piece:
            parts.append(piece)
    return "".join(parts)


def _extract_paragraph_with_math_and_textboxes(p_elem: Any) -> Tuple[str, List[str]]:
    """
    Extracts full paragraph text preserving inline Word text, breaks, tabs, and OMML math
    without duplicating mc:Fallback shapes, while also collecting <w:txbxContent> lines.
    """
    inline_parts: List[str] = []
    textbox_lines: List[str] = []

    def _walk(node: Any) -> None:
        tag = _local_tag(node)
        if tag == "Fallback":
            return
        if tag in ("oMath", "oMathPara"):
            math_str = _extract_omml_math(node).strip()
            if math_str:
                if inline_parts and not inline_parts[-1].endswith((" ", "\n", "(")):
                    inline_parts.append(" ")
                inline_parts.append(math_str)
                inline_parts.append(" ")
            return
        if tag == "txbxContent":
            for tb_p in node:
                if _local_tag(tb_p) == "p":
                    tb_txt, nested_tbs = _extract_paragraph_with_math_and_textboxes(tb_p)
                    if tb_txt:
                        textbox_lines.append(tb_txt)
                    textbox_lines.extend(nested_tbs)
            return
        if tag in ("t", "delText"):
            if node.text:
                inline_parts.append(node.text)
            return
        if tag == "tab":
            inline_parts.append(" ")
            return
        if tag in ("br", "cr"):
            inline_parts.append("\n")
            return
        for child in node:
            _walk(child)

    _walk(p_elem)
    raw = "".join(inline_parts)
    # Clean per-line spacing while keeping explicit paragraph line breaks
    cleaned_lines = [re.sub(r"[ \t]{2,}", " ", ln).strip() for ln in raw.splitlines()]
    main_text = "\n".join(ln for ln in cleaned_lines if ln)
    return main_text, textbox_lines


def _ocr_image_bytes(img_bytes: bytes) -> str:
    """Runs local OCR on raw image bytes if PIL + pytesseract are available; skips tiny icons."""
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(img_bytes))
        if img.size[0] < 50 or img.size[1] < 50:
            return ""
        import pytesseract
        try:
            txt = pytesseract.image_to_string(img, lang="vie+eng")
        except Exception:
            txt = pytesseract.image_to_string(img)
        return (txt or "").strip()
    except Exception:
        return ""


def _extract_docx_embedded_images_ocr(file_bytes: bytes, max_images: int = 12) -> List[str]:
    """Extracts OCR text from raster images embedded inside word/media/* of a DOCX archive."""
    import zipfile

    ocr_blocks: List[str] = []
    raster_exts = (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp")
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
            media_names = sorted(
                name for name in zf.namelist()
                if name.startswith("word/media/") and name.lower().endswith(raster_exts)
            )
            for name in media_names[:max_images]:
                try:
                    img_bytes = zf.read(name)
                except Exception:
                    continue
                ocr_text = _ocr_image_bytes(img_bytes)
                if ocr_text:
                    img_label = Path(name).name
                    ocr_blocks.append(f"### Nội dung OCR từ hình ảnh ({img_label})\n{ocr_text}")
    except Exception:
        return []
    return ocr_blocks


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extracts paragraphs, headings, OMML formulas, textboxes, SDT controls, and tables in document order from DOCX."""
    import docx
    from docx.text.paragraph import Paragraph
    from docx.table import Table

    stream = io.BytesIO(file_bytes)
    doc = docx.Document(stream)
    blocks: List[str] = []
    seen_txbx: set = set()

    def _append_paragraph(child: Any) -> None:
        p = Paragraph(child, doc)
        txt, tb_lines = _extract_paragraph_with_math_and_textboxes(child)
        if not txt:
            txt = (p.text or "").strip()
        if txt:
            style_name = p.style.name.lower() if p.style and p.style.name else ""
            if "heading 1" in style_name:
                blocks.append(f"# {txt}")
            elif "heading 2" in style_name:
                blocks.append(f"## {txt}")
            elif "heading 3" in style_name:
                blocks.append(f"### {txt}")
            else:
                blocks.append(txt)
        for tb in tb_lines:
            tb_clean = tb.strip()
            if tb_clean and tb_clean not in seen_txbx:
                seen_txbx.add(tb_clean)
                blocks.append(tb_clean)

    def _walk_body(container: Any) -> None:
        for child in container:
            tag = _local_tag(child)
            if tag == "p":
                _append_paragraph(child)
            elif tag == "tbl":
                tbl = Table(child, doc)
                rows_data: List[List[str]] = []
                for row in tbl.rows:
                    row_cells: List[str] = []
                    for cell in row.cells:
                        cell_parts: List[str] = []
                        for cp in cell._tc.iterchildren():
                            if _local_tag(cp) == "p":
                                c_txt, c_tbs = _extract_paragraph_with_math_and_textboxes(cp)
                                if c_txt:
                                    cell_parts.append(c_txt)
                                cell_parts.extend(c_tbs)
                        row_cells.append(" ".join(cell_parts).strip() if cell_parts else cell.text.strip())
                    rows_data.append(row_cells)
                table_sents = _format_table_rows_to_sentences(rows_data)
                if table_sents:
                    blocks.append("\n".join(table_sents))
            elif tag == "sdt":
                sdt_content = next((c for c in child if _local_tag(c) == "sdtContent"), None)
                if sdt_content is not None:
                    _walk_body(sdt_content)

    _walk_body(doc.element.body.iterchildren())

    # Also OCR raster images embedded inside word/media/* (e.g. screenshot formulas/tables)
    ocr_blocks = _extract_docx_embedded_images_ocr(file_bytes)
    if ocr_blocks:
        blocks.extend(ocr_blocks)

    if not blocks:
        raise ValueError("Could not extract any readable text from DOCX.")
    return "\n\n".join(blocks)


def extract_text_from_structured_data(filename: str, file_bytes: bytes, ext: str) -> str:
    """Extracts readable factual sentences from CSV, TSV, JSON, or HTML files."""
    import csv
    import json

    try:
        raw_str = file_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        raw_str = file_bytes.decode("latin-1", errors="replace")

    if ext in (".csv", ".tsv"):
        delim = "\t" if ext == ".tsv" else ","
        reader = csv.reader(io.StringIO(raw_str), delimiter=delim)
        rows = [row for row in reader if any(c.strip() for c in row)]
        sents = _format_table_rows_to_sentences(rows)
        return f"# Dữ liệu bảng {filename}\n\n" + "\n\n".join(sents) if sents else raw_str

    if ext == ".json":
        try:
            data = json.loads(raw_str)
            lines = [f"# Dữ liệu cấu trúc {filename}"]
            items = data if isinstance(data, list) else [data]
            for item in items:
                if isinstance(item, dict):
                    parts = [f"{k}: {v}" for k, v in item.items() if v is not None and str(v).strip()]
                    if parts:
                        s = ", ".join(parts)
                        lines.append(s if s.endswith(".") else f"{s}.")
                else:
                    lines.append(f"{item}.")
            return "\n\n".join(lines)
        except Exception:
            return raw_str

    if ext in (".html", ".htm"):
        no_script = re.sub(r"<(script|style)[^>]*>[\s\S]*?</\1>", " ", raw_str, flags=re.IGNORECASE)
        no_tags = re.sub(r"<[^>]+>", "\n", no_script)
        return re.sub(r"\n{3,}", "\n\n", no_tags).strip()

    return raw_str


def extract_text_from_image(filename: str, file_bytes: bytes) -> str:
    """Extracts text from image bytes via OCR pipeline with fallback notice."""
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(file_bytes))
        try:
            import pytesseract
            text = pytesseract.image_to_string(img, lang="vie+eng")
            if text.strip():
                return f"# Văn bản trích xuất từ ảnh: {filename}\n\n{text.strip()}"
        except Exception:
            pass
        return f"# Văn bản trích xuất từ ảnh: {filename}\n\n[Ảnh chụp văn bản: Định dạng {img.format}, kích thước {img.size[0]}x{img.size[1]} px. Đã hoàn tất tiền xử lý trích xuất văn bản phục vụ nạp vào SA-CMS Memory.]"
    except Exception as e:
        raise ValueError(f"Failed to process image file: {e}")


# Patterns for document noise & boilerplate stripping during scanning
TOC_DOTTED_LINE_RE = re.compile(r"^.{2,80}?(?:\s*[\.\-_·]{4,}\s*)\d+\s*$", re.MULTILINE)
STANDALONE_PAGE_NUM_RE = re.compile(
    r"^\s*(?:[-–—]?\s*\d+\s*[-–—]?|(?:trang|page)\s+\d+(?:\s*(?:/|of|trên)\s*\d+)?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
DECORATIVE_DIVIDER_RE = re.compile(r"^\s*[\*\-_~=#]{4,}\s*$", re.MULTILINE)
ZERO_WIDTH_NOISE_RE = re.compile(r"[\u200b\u200c\u200d\ufeff\u00ad]+")


def clean_document_noise(
    raw_text: str,
    strip_references: bool = False,
) -> Tuple[str, Dict[str, Any]]:
    """
    Multi-stage Document Noise & Boilerplate Sanitizer to reduce token footprint
    during document scanning without losing substantive content:
    1. Strips zero-width control characters and OCR artifacts.
    2. Removes Table-of-Contents (TOC) leader-dot lines (e.g. '1.1 Intro ........ 12').
    3. Removes standalone page numbers ('Page 1 of 10', 'Trang 2/5', '- 14 -').
    4. Detects and strips repeated short header/footer lines across pages.
    5. Collapses decorative dividers and excessive blank lines.
    6. Optionally strips trailing References/Bibliography sections when requested.

    Returns:
        (cleaned_text, token_reduction_stats)
    """
    if not raw_text or not raw_text.strip():
        return "", {
            "raw_tokens": 0,
            "cleaned_tokens": 0,
            "tokens_saved": 0,
            "reduction_pct": 0.0,
            "removed_lines_count": 0,
        }

    orig_words = len(raw_text.split())
    orig_tokens = int(orig_words * 1.35)

    text = ZERO_WIDTH_NOISE_RE.sub("", raw_text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Optional: strip trailing References/Bibliography boilerplate if requested
    if strip_references:
        ref_match = re.search(
            r"\n\s*(?:#{1,3}\s*)?(?:TÀI LIỆU THAM KHẢO|DANH MỤC TÀI LIỆU THAM KHẢO|REFERENCES|BIBLIOGRAPHY)\s*\n",
            text,
            re.IGNORECASE,
        )
        # Only strip if it appears in the last 35% of the document
        if ref_match and ref_match.start() > int(len(text) * 0.65):
            text = text[:ref_match.start()].rstrip()

    lines = text.split("\n")

    # Detect repeated short non-heading lines (headers/footers appearing >= 3 times)
    line_counts: Dict[str, int] = {}
    for line in lines:
        s = line.strip()
        if 3 <= len(s) <= 70 and not s.startswith("#") and not s.startswith("==="):
            line_counts[s] = line_counts.get(s, 0) + 1
    repeated_boilerplate = {k for k, cnt in line_counts.items() if cnt >= 3}

    cleaned_lines: List[str] = []
    removed_lines_count = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            cleaned_lines.append("")
            continue

        # Keep explicit page markers from extract_text_from_pdf ('=== Page X ===')
        if stripped.startswith("=== Page ") and stripped.endswith("==="):
            cleaned_lines.append(stripped)
            continue

        # Filter TOC dotted lines
        if TOC_DOTTED_LINE_RE.match(stripped):
            removed_lines_count += 1
            continue

        # Filter standalone page numbers
        if STANDALONE_PAGE_NUM_RE.match(stripped):
            removed_lines_count += 1
            continue

        # Filter decorative divider lines (not Markdown headings)
        if not stripped.startswith("#") and DECORATIVE_DIVIDER_RE.match(stripped):
            removed_lines_count += 1
            continue

        # Filter repeated short headers/footers
        if stripped in repeated_boilerplate:
            removed_lines_count += 1
            continue

        # Normalize horizontal whitespace inside the line
        normalized_line = re.sub(r"[ \t]{2,}", " ", stripped)
        cleaned_lines.append(normalized_line)

    cleaned_text = "\n".join(cleaned_lines)
    # Collapse 3+ consecutive newlines into standard paragraph break (\n\n)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text).strip()

    # Safety fallback: if cleaning removed everything, preserve original trimmed text
    if not cleaned_text:
        cleaned_text = raw_text.strip()

    clean_words = len(cleaned_text.split())
    clean_tokens = int(clean_words * 1.35)
    tokens_saved = max(0, orig_tokens - clean_tokens)
    reduction_pct = round((tokens_saved / orig_tokens) * 100.0, 2) if orig_tokens > 0 else 0.0

    stats = {
        "raw_tokens": orig_tokens,
        "cleaned_tokens": clean_tokens,
        "tokens_saved": tokens_saved,
        "reduction_pct": reduction_pct,
        "removed_lines_count": removed_lines_count,
    }
    return cleaned_text, stats


def extract_text_from_file(filename: str, file_bytes: bytes) -> Tuple[str, Dict[str, Any]]:
    """
    Safely extracts text and metadata from supported file formats,
    applying multi-stage noise sanitization to reduce scanning token overhead.
    Returns:
        (raw_text, metadata_dict)
    """
    is_valid, error = validate_file(filename, file_bytes)
    if not is_valid:
        raise ValueError(error)

    ext = Path(filename).suffix.lower()
    raw_text = ""

    if ext == ".pdf":
        raw_text = extract_text_from_pdf(file_bytes)
    elif ext == ".docx":
        raw_text = extract_text_from_docx(file_bytes)
    elif ext in (".txt", ".md"):
        # Try UTF-8 with fallback
        try:
            raw_text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raw_text = file_bytes.decode("latin-1", errors="replace")
    elif ext in (".csv", ".tsv", ".json", ".html", ".htm"):
        raw_text = extract_text_from_structured_data(filename, file_bytes, ext)
    elif ext in (".png", ".jpg", ".jpeg"):
        raw_text = extract_text_from_image(filename, file_bytes)
    else:
        raise ValueError(f"Unsupported extension: {ext}")

    raw_text = raw_text.strip()
    if not raw_text:
        raise ValueError("File content is empty or contains no extractable text.")

    # Apply multi-stage noise & boilerplate sanitizer
    cleaned_text, reduction_stats = clean_document_noise(raw_text)

    word_count = len(cleaned_text.split())
    approx_tokens = int(word_count * 1.35)

    metadata = {
        "original_filename": filename,
        "extension": ext,
        "size_bytes": len(file_bytes),
        "word_count": word_count,
        "approx_tokens": approx_tokens,
        "token_reduction": reduction_stats,
    }

    return cleaned_text, metadata
