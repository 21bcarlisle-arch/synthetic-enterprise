"""Consumption history for the customer portal — Phase 79."""
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path("company/billing/invoices.db")


def _conn(db_path: Path):
    return sqlite3.connect(str(db_path))


def consumption_history(account_id: str, db_path: Path = DEFAULT_DB_PATH) -> list[dict]:
    """Return per-invoice consumption records for one account, oldest first."""
    if not db_path.exists():
        return []
    with _conn(db_path) as conn:
        rows = conn.execute(
            """SELECT billing_period_start, billing_period_end, consumption_kwh, commodity
               FROM invoices
               WHERE account_id = ?
               ORDER BY billing_period_start""",
            (account_id,),
        ).fetchall()
    return [
        {
            "period_start": r[0],
            "period_end": r[1],
            "kwh": r[2],
            "commodity": r[3],
            "year": int(r[0][:4]) if r[0] else None,
            "month": int(r[0][5:7]) if r[0] else None,
        }
        for r in rows
    ]


def monthly_totals(records: list[dict]) -> list[dict]:
    """Aggregate records by (year, month), return sorted list."""
    buckets: dict[tuple, dict] = {}
    for r in records:
        key = (r["year"], r["month"])
        if key not in buckets:
            buckets[key] = {"year": r["year"], "month": r["month"], "kwh": 0.0, "commodity": r["commodity"]}
        buckets[key]["kwh"] += r["kwh"]
    return sorted(buckets.values(), key=lambda x: (x["year"], x["month"]))
