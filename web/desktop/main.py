"""TJU-Expense desktop app.

Starts the local FastAPI server (which serves both the API and the built
frontend) on a loopback port, then opens it in a native pywebview window. All
campus-card requests happen in-process via Python, so there is no browser CORS
limitation and no server to host — everything runs on the user's own machine.
"""
from __future__ import annotations

import shutil
import socket
import sys
import threading
import time
from pathlib import Path

import uvicorn
import webview

# Make the backend package importable (web/backend), then the app.
BACKEND = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app import storage  # noqa: E402
from app.main import app  # noqa: E402


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _serve(port: int) -> None:
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


def _wait_until_up(port: int, timeout: float = 15.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.1)
    return False


class Api:
    """Methods callable from the frontend as ``window.pywebview.api.*``."""

    def export_csv(self, stuid: str, year: str) -> dict:
        """Save the cached CSV for (stuid, year) via a native Save dialog."""
        src = storage.cache_path(str(stuid), str(year))
        if not src.is_file():
            return {"ok": False, "error": "请先加载该年份的数据"}
        window = webview.windows[0]
        dest = window.create_file_dialog(
            webview.SAVE_DIALOG, save_filename=f"tju-{stuid}-{year}.csv"
        )
        if not dest:
            return {"ok": False, "error": "已取消"}
        dest_path = dest if isinstance(dest, str) else dest[0]
        shutil.copyfile(src, dest_path)
        return {"ok": True, "path": dest_path}


def main() -> None:
    port = _free_port()
    threading.Thread(target=_serve, args=(port,), daemon=True).start()
    if not _wait_until_up(port):
        print("后端启动失败", file=sys.stderr)
        sys.exit(1)
    webview.create_window(
        "TJU Expense",
        f"http://127.0.0.1:{port}",
        width=1200,
        height=860,
        min_size=(880, 600),
        js_api=Api(),
    )
    webview.start()


if __name__ == "__main__":
    main()
