"""FastAPI application exposing the TJU campus-card data to the web frontend."""
from __future__ import annotations

from datetime import datetime

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import stats
from .config import settings
from .sessions import Session, SessionStore
from .tju.client import LoginError, TJUWebClient

cfg = settings()
store = SessionStore(ttl_minutes=cfg.session_ttl_minutes)

app = FastAPI(title="TJU-Expense Web API", version="1.0.0")
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


# -- routes -------------------------------------------------------------------
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
def records(year: str | None = None, session: Session = Depends(current_session)) -> dict:
    y = _valid_year(year)
    try:
        rows = session.client.records(start=f"{y}-01-01", end=f"{y}-12-31")
    except ConnectionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"year": y, "records": rows, "stats": stats.compute(rows)}


@app.post("/api/logout")
def logout(x_session_id: str | None = Header(default=None)) -> dict:
    store.drop(x_session_id)
    return {"ok": True}
