"""Compute consumption statistics as plain JSON-serialisable dicts.

Mirrors the aggregations in ``tju_expense.analyze.print_statistics`` but emits
structured data for the web frontend instead of Rich tables. Kept dependency-
light (pandas only) and pure so it is trivially testable.
"""
from __future__ import annotations

import pandas as pd

# Slots match the CLI: breakfast / lunch / dinner by hour of day.
TIME_SLOTS = {"breakfast": (5, 11), "lunch": (11, 17), "dinner": (17, 24)}
# Records whose type mentions water/electricity are excluded from "dining" views.
_UTILITY = "水|电"


def _to_frame(records: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(records)
    if df.empty:
        return df
    df["time"] = pd.to_datetime(df["time"])
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["amount"])
    for col in ("type", "place"):
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("")
    return df


def _txn(row: pd.Series) -> dict:
    return {
        "amount": round(float(row["amount"]), 2),
        "time": row["time"].strftime("%Y-%m-%d %H:%M:%S"),
        "place": row.get("place", ""),
        "type": row.get("type", ""),
    }


def daily_series(df: pd.DataFrame) -> list[dict]:
    """Per-day totals from Jan 1st to the last record, missing days zero-filled."""
    max_date = df["time"].max().date()
    start = pd.Timestamp(max_date.year, 1, 1)
    full = pd.date_range(start=start, end=max_date, freq="D")
    series = (
        df.assign(date=df["time"].dt.normalize())
        .groupby("date")["amount"]
        .sum()
        .reindex(full, fill_value=0)
    )
    return [
        {"date": d.strftime("%Y-%m-%d"), "amount": round(float(v), 2)}
        for d, v in series.items()
    ]


def compute(records: list[dict]) -> dict:
    """Return the full statistics payload for a set of records."""
    df = _to_frame(records)
    if df.empty:
        return {"empty": True}

    dining = df[~df["type"].str.contains(_UTILITY, na=False)]
    total = float(df["amount"].sum())
    daily_totals = df.groupby(df["time"].dt.date)["amount"].sum()

    summary = {
        "total": round(total, 2),
        "count": int(len(df)),
        "daily_average": round(float(daily_totals.mean()), 2),
        "per_transaction_average": round(float(df["amount"].mean()), 2),
        "active_days": int(daily_totals.size),
        "first_day": df["time"].min().strftime("%Y-%m-%d"),
        "last_day": df["time"].max().strftime("%Y-%m-%d"),
    }

    by_type = [
        {
            "type": idx,
            "count": int(row["count"]),
            "sum": round(float(row["sum"]), 2),
            "mean": round(float(row["mean"]), 2),
        }
        for idx, row in df.groupby("type")["amount"]
        .agg(["count", "sum", "mean"])
        .sort_values("sum", ascending=False)
        .iterrows()
    ]

    monthly = df.groupby(df["time"].dt.month)["amount"].agg(["count", "sum"])
    by_month = [
        {"month": int(m), "count": int(row["count"]), "sum": round(float(row["sum"]), 2)}
        for m, row in monthly.iterrows()
    ]

    by_time_slot = []
    for slot, (lo, hi) in TIME_SLOTS.items():
        mask = (dining["time"].dt.hour >= lo) & (dining["time"].dt.hour < hi)
        sub = dining[mask]["amount"]
        by_time_slot.append(
            {
                "slot": slot,
                "count": int(sub.size),
                "sum": round(float(sub.sum()), 2),
                "mean": round(float(sub.mean()), 2) if sub.size else 0.0,
            }
        )

    top_places = [
        {"place": place, "count": int(row["count"]), "sum": round(float(row["sum"]), 2)}
        for place, row in dining.groupby("place")["amount"]
        .agg(["count", "sum"])
        .sort_values("sum", ascending=False)
        .head(10)
        .iterrows()
    ]

    extremes = {
        "max": _txn(df.loc[df["amount"].idxmax()]),
        "min": _txn(df.loc[df["amount"].idxmin()]),
        "earliest": _txn(df.loc[df["time"].idxmin()]),
        "latest": _txn(df.loc[df["time"].idxmax()]),
        "earliest_of_day": _txn(df.loc[df["time"].dt.time.idxmin()]),
        "latest_of_day": _txn(df.loc[df["time"].dt.time.idxmax()]),
    }
    if not dining.empty:
        extremes["max_dining"] = _txn(dining.loc[dining["amount"].idxmax()])

    return {
        "empty": False,
        "summary": summary,
        "by_type": by_type,
        "by_month": by_month,
        "by_time_slot": by_time_slot,
        "top_places": top_places,
        "extremes": extremes,
        "daily_series": daily_series(df),
    }
