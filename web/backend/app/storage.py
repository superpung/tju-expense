"""Local, on-disk cache of fetched records — the app is local-first.

Records for a (student, year) are written to
``~/.tju-expense/data/<stuid>/<year>.csv`` so reopening the app shows data
instantly without re-hitting the campus site, and the CSV is a plain file the
user can find and export.
"""
from __future__ import annotations

import csv
from pathlib import Path

FIELDS = ["time", "id", "type", "amount", "place"]


def data_dir() -> Path:
    d = Path.home() / ".tju-expense" / "data"
    d.mkdir(parents=True, exist_ok=True)
    return d


def cache_path(stuid: str, year: str) -> Path:
    user_dir = data_dir() / stuid
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir / f"{year}.csv"


def save_records(stuid: str, year: str, records: list[dict]) -> Path:
    path = cache_path(stuid, year)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)
    return path


def load_records(stuid: str, year: str) -> list[dict] | None:
    path = cache_path(stuid, year)
    if not path.is_file():
        return None
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))
