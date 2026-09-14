"""FastAPI application for the TJU-Expense desktop app.

Serves both the JSON API and the built frontend from a single local origin, so
the pywebview window loads one URL with no CORS. Fetched records are cached to
the local disk (see :mod:`app.storage`) and can be exported.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import stats, storage
from .config import settings
from .sessions import Session, SessionStore
from .tju.client import LoginError, TJUWebClient

cfg = settings()
store = SessionStore(ttl_minutes=cfg.session_ttl_minutes)

# Built frontend (web/frontend/dist), served at the app root when present.
def _frontend_dist() -> Path:
    override = os.getenv("TJU_FRONTEND_DIST")
    if override:
        return Path(override)
    if getattr(sys, "frozen", False):  # PyInstaller bundle
        return Path(sys._MEIPASS) / "frontend_dist"  # type: ignore[attr-defined]
    return Path(__file__).resolve().parents[2] / "frontend" / "dist"


DIST = _frontend_dist()

app = FastAPI(title="TJU-Expense", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cfg.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -- request/response models --------------------------------------------------
class LoginRequest(BaseModel):
    username: str
    password: str


# -- dependencies -------------------------------------------------------------
def current_session(x_session_id: str | None = Header(default=None)) -> Session:
    session = store.get(x_session_id)
    if session is None or not session.authenticated:
        raise HTTPException(status_code=401, detail="未登录或会话已过期，请重新登录。")
    return session


def _valid_year(raw: str | None) -> str:
    now = datetime.now()
    default = str(now.year - 1 if now.month <= 1 else now.year)
    if not raw:
        return default
    return raw if raw.isdigit() and len(raw) == 4 else default


def _records_for(session: Session, year: str, refresh: bool) -> list[dict]:
    """Return records for a year, from the local cache unless refresh is asked."""
    stuid = session.client.user_info().get("stuid") or "unknown"
    if not refresh:
        cached = storage.load_records(stuid, year)
        if cached is not None:
            return cached
    try:
        rows = session.client.records(start=f"{year}-01-01", end=f"{year}-12-31")
    except ConnectionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    storage.save_records(stuid, year, rows)
    return rows


# -- API routes ---------------------------------------------------------------
@app.get("/api/health")
def health() -> dict:
    return {"ok": True}


@app.post("/api/login")
def login(body: LoginRequest) -> dict:
    """Log in with username + password; return a session token and user info."""
    client = TJUWebClient()
    try:
        info = client.login(body.username.strip(), body.password)
    except LoginError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    token = store.create(client)
    store.get(token).authenticated = True  # type: ignore[union-attr]
    return {"token": token, "user": info}


@app.get("/api/user")
def user(session: Session = Depends(current_session)) -> dict:
    return {"user": session.client.user_info()}


@app.get("/api/records")
def records(
    year: str | None = None,
    refresh: bool = False,
    session: Session = Depends(current_session),
) -> dict:
    y = _valid_year(year)
    rows = _records_for(session, y, refresh)
    return {"year": y, "records": rows, "stats": stats.compute(rows)}


@app.get("/api/export")
def export(year: str | None = None, session: Session = Depends(current_session)) -> FileResponse:
    """Download the year's records as a CSV file (browser/local-web mode)."""
    y = _valid_year(year)
    rows = _records_for(session, y, refresh=False)
    stuid = session.client.user_info().get("stuid") or "unknown"
    path = storage.save_records(stuid, y, rows)
    return FileResponse(path, media_type="text/csv", filename=f"tju-{stuid}-{y}.csv")


@app.post("/api/logout")
def logout(x_session_id: str | None = Header(default=None)) -> dict:
    store.drop(x_session_id)
    return {"ok": True}


# -- frontend (mounted last so /api/* wins) -----------------------------------
if DIST.is_dir():
    app.mount("/", StaticFiles(directory=str(DIST), html=True), name="frontend")
