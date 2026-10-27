"""
Internationalization Router (Ticket 3.4) — /api/v2/i18n.
Serves localized UI strings (vi.json, en.json) for 100% offline bilingual interface.
"""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v2/i18n", tags=["i18n"])
I18N_DIR = Path(__file__).resolve().parent.parent / "i18n"


@router.get("/{lang}")
async def get_locale_strings(lang: str):
    """Lấy danh mục bản dịch giao diện song ngữ theo mã ngôn ngữ (vi | en)."""
    lang_code = lang.lower().strip()
    if lang_code not in ("vi", "en"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ ngôn ngữ 'vi' hoặc 'en'.")

    file_path = I18N_DIR / f"{lang_code}.json"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Không tìm thấy file từ điển cho '{lang_code}'.")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            translations = json.load(f)
        return {
            "lang": lang_code,
            "count": len(translations),
            "strings": translations,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi đọc file ngôn ngữ: {str(e)}")
