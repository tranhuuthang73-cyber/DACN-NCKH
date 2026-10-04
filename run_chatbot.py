"""
SA-CMS 3-Level Chatbot Backend Entry Point — Root Wrapper (Phase 3.3).

Usage:
    python run_chatbot.py --document <file_or_text_or_id> --query <text> --mode <context|memory|hybrid>
"""

import sys
from pathlib import Path

# Forward execution to scripts/run_chatbot.py
scripts_dir = Path(__file__).resolve().parent / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from run_chatbot import main

if __name__ == "__main__":
    main()
