# PyInstaller spec for the TJU-Expense desktop app.
# Build from web/desktop after `npm --prefix ../frontend run build`:
#   pyinstaller tju-expense-desktop.spec
#
# Bundles the launcher, the FastAPI backend, the tju_expense scraping package,
# and the built frontend (mapped to `frontend_dist`, where app.main looks for it
# when frozen).
import os
from PyInstaller.utils.hooks import collect_submodules

asset_name = os.getenv("ASSET_NAME", "tju-expense")
ROOT = os.path.abspath(os.path.join(os.getcwd(), "..", ".."))
FRONTEND_DIST = os.path.join(ROOT, "web", "frontend", "dist")

hidden = (
    collect_submodules("uvicorn")
    + collect_submodules("webview")
    + ["app.main", "tju_expense.fetch"]
)

a = Analysis(
    ["main.py"],
    pathex=[os.path.join(ROOT, "web", "backend"), os.path.join(ROOT, "src")],
    binaries=[],
    datas=[(FRONTEND_DIST, "frontend_dist")],
    hiddenimports=hidden,
    hookspath=[],
    runtime_hooks=[],
    excludes=["matplotlib", "seaborn", "PyQt5", "tkinter"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name=asset_name,
    console=False,
    disable_windowed_traceback=False,
)
