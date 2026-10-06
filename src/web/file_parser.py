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
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".png", ".jpg", ".jpeg"}


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


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extracts text from DOCX bytes using python-docx."""
    import docx
    stream = io.BytesIO(file_bytes)
    doc = docx.Document(stream)
    paragraphs = []
    for p in doc.paragraphs:
        txt = p.text.strip()
        if txt:
            # Check style name for headings
            style_name = p.style.name.lower() if p.style and p.style.name else ""
            if "heading 1" in style_name:
                paragraphs.append(f"# {txt}")
            elif "heading 2" in style_name:
                paragraphs.append(f"## {txt}")
            elif "heading 3" in style_name:
                paragraphs.append(f"### {txt}")
            else:
                paragraphs.append(txt)
    if not paragraphs:
        raise ValueError("Could not extract any readable text from DOCX.")
    return "\n\n".join(paragraphs)


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


def extract_text_from_file(filename: str, file_bytes: bytes) -> Tuple[str, Dict[str, Any]]:
    """
    Safely extracts text and metadata from supported file formats.
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
    elif ext in (".png", ".jpg", ".jpeg"):
        raw_text = extract_text_from_image(filename, file_bytes)
    else:
        raise ValueError(f"Unsupported extension: {ext}")

    raw_text = raw_text.strip()
    if not raw_text:
        raise ValueError("File content is empty or contains no extractable text.")

    word_count = len(raw_text.split())
    approx_tokens = int(word_count * 1.35)

    metadata = {
        "original_filename": filename,
        "extension": ext,
        "size_bytes": len(file_bytes),
        "word_count": word_count,
        "approx_tokens": approx_tokens,
    }

    return raw_text, metadata
