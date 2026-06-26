"""Collections queue: overdue invoice tracking and debt management.

Queries the invoice DB for unpaid/partially_paid invoices past due date.
Groups by customer and assigns aging tier (30/60/90+ days overdue).
"""

from __future__ import annotations
from datetime import date
from pathlib import Path
import sqlite3
from contextlib import contextmanager

from company.billing.invoice import DEFAULT_DB_PATH, create_schema


@contextmanager
def _conn(db_path: Path):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def _aging_tier(days_overdue: int) -> str:
    if days_overdue >= 90:
        return "90+"
    if days_overdue >= 60:
        return "60-90"
    if days_overdue >= 30:
        return "30-60"
    return "0-30"


def get_overdue_invoices(db_path: Path = DEFAULT_DB_PATH,
                         as_of: date | None = None) -> list[dict]:
    """All unpaid/partially_paid invoices past their due date."""
    create_schema(db_path)
    today = (as_of or date.today()).isoformat()
    with _conn(db_path) as conn:
        rows = conn.execute(
            """SELECT * FROM invoices
               WHERE payment_status IN ('unpaid', 'partially_paid')
               AND due_date < ?
               ORDER BY due_date""",
            (today,),
        ).fetchall()
    result = []
    for row in rows:
        due = date.fromisoformat(row["due_date"])
        pivot = as_of or date.today()
        days = (pivot - due).days
        result.append({
            "invoice_number": row["invoice_number"],
            "account_id": row["account_id"],
            "due_date": row["due_date"],
            "total_gbp": row["total_gbp"],
            "payment_status": row["payment_status"],
            "days_overdue": days,
            "tier": _aging_tier(days),
        })
    return result


def get_collections_queue(db_path: Path = DEFAULT_DB_PATH,
                           as_of: date | None = None) -> list[dict]:
    """Collections queue: one row per customer, aggregated overdue amounts."""
    invoices = get_overdue_invoices(db_path, as_of)
    by_customer: dict[str, dict] = {}
    for inv in invoices:
        cid = inv["account_id"]
        if cid not in by_customer:
            by_customer[cid] = {
                "account_id": cid,
                "overdue_count": 0,
                "total_overdue_gbp": 0.0,
                "oldest_due_date": inv["due_date"],
                "max_days_overdue": 0,
                "tier": "0-30",
            }
        entry = by_customer[cid]
        entry["overdue_count"] += 1
        entry["total_overdue_gbp"] = round(entry["total_overdue_gbp"] + inv["total_gbp"], 2)
        if inv["days_overdue"] > entry["max_days_overdue"]:
            entry["max_days_overdue"] = inv["days_overdue"]
            entry["tier"] = inv["tier"]
        if inv["due_date"] < entry["oldest_due_date"]:
            entry["oldest_due_date"] = inv["due_date"]
    return sorted(by_customer.values(), key=lambda x: -x["max_days_overdue"])
