"""FastAPI backend for the TJU-Expense web app.

The scraping and record-parsing logic is reused verbatim from the root
``tju_expense`` package. When that package is not installed into the active
environment, we add the repository ``src`` directory to ``sys.path`` so
``import tju_expense`` still resolves during development.
"""
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[3] / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
