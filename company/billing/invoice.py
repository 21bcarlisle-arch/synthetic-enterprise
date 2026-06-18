"""Company Layer — Billing Artefact Engine.

Bills currently exist as calculations in the simulation. This module makes
them documents: each bill becomes a retrievable invoice record stored in
SQLite with an invoice number, line items, VAT, due date, and payment status.

The simulation's existing bill calculation feeds in — the invoice engine
wraps the calculation in a real artefact. Every bill the simulation issues
becomes a retrievable invoice.
"""

import sqlite3
from contextlib import contextmanager
from datetime import date, timedelta
from pathlib import Path

DEFAULT_DB_PATH = Path("company/data/invoices.db")

VAT_RATE = 0.05  # 5% VAT on domestic energy (UK reduced rate)
PAYMENT_TERMS_DAYS = 14


@contextmanager
def _conn(db_path: Path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def create_schema(db_path: Path = DEFAULT_DB_PATH) -> None:
    """Create the invoice schema. Idempotent."""
    with _conn(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                invoice_number  INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id      TEXT NOT NULL,
                billing_period_start TEXT NOT NULL,
                billing_period_end   TEXT NOT NULL,
                consumption_kwh  REAL NOT NULL,
                unit_rate_p_per_kwh REAL NOT NULL,
                standing_charge_gbp  REAL NOT NULL DEFAULT 0.0,
                subtotal_gbp    REAL NOT NULL,
                vat_gbp         REAL NOT NULL,
                total_gbp       REAL NOT NULL,
                issue_date      TEXT NOT NULL,
                due_date        TEXT NOT NULL,
                payment_status  TEXT NOT NULL DEFAULT 'unpaid',
                commodity       TEXT NOT NULL DEFAULT 'electricity'
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_account ON invoices(account_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON invoices(payment_status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_period ON invoices(billing_period_start)")


def _unit_rate_from_bill(bill: dict) -> float:
    """Derive p/kWh from bill dict — bills carry total_amount_gbp and total_consumption_kwh."""
    kwh = bill.get("total_consumption_kwh", 0.0)
    gbp = bill.get("total_amount_gbp", 0.0)
    if kwh > 0:
        return (gbp / kwh) * 100.0  # convert £/kWh → p/kWh
    return 0.0


def create_invoice(bill: dict, db_path: Path = DEFAULT_DB_PATH) -> int:
    """Create an invoice from a simulation bill dict. Returns invoice_number."""
    create_schema(db_path)
    kwh = bill.get("total_consumption_kwh", 0.0)
    subtotal = bill.get("total_amount_gbp", 0.0)
    vat = round(subtotal * VAT_RATE, 2)
    total = round(subtotal + vat, 2)
    period_end = bill.get("period_end", bill.get("period_start", ""))
    issue_date = period_end  # issued at period end
    due_date = (
        date.fromisoformat(issue_date) + timedelta(days=PAYMENT_TERMS_DAYS)
    ).isoformat() if issue_date else ""
    unit_rate_p = _unit_rate_from_bill(bill)
    commodity = bill.get("commodity", "electricity")

    with _conn(db_path) as conn:
        cursor = conn.execute("""
            INSERT INTO invoices
                (account_id, billing_period_start, billing_period_end,
                 consumption_kwh, unit_rate_p_per_kwh, standing_charge_gbp,
                 subtotal_gbp, vat_gbp, total_gbp,
                 issue_date, due_date, payment_status, commodity)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            bill["customer_id"],
            bill.get("period_start", ""),
            period_end,
            kwh,
            round(unit_rate_p, 4),
            0.0,
            round(subtotal, 2),
            vat,
            total,
            issue_date,
            due_date,
            "unpaid",
            commodity,
        ))
        return cursor.lastrowid


def bulk_create_invoices(bills: list[dict], db_path: Path = DEFAULT_DB_PATH) -> int:
    """Create invoices for a list of simulation bills. Returns count created."""
    create_schema(db_path)
    count = 0
    for bill in bills:
        create_invoice(bill, db_path)
        count += 1
    return count


def get_invoice(invoice_number: int, db_path: Path = DEFAULT_DB_PATH) -> dict | None:
    """Retrieve a single invoice by number."""
    with _conn(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM invoices WHERE invoice_number = ?", (invoice_number,)
        ).fetchone()
        return dict(row) if row else None


def invoices_for_account(account_id: str, db_path: Path = DEFAULT_DB_PATH) -> list[dict]:
    """All invoices for a given account, chronological."""
    with _conn(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM invoices WHERE account_id = ? ORDER BY billing_period_start",
            (account_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def update_payment_status(
    invoice_number: int,
    status: str,
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    """Update invoice payment status (unpaid / paid / partially_paid / bad_debt)."""
    if status not in ("unpaid", "paid", "partially_paid", "bad_debt"):
        raise ValueError(f"Invalid payment status: {status!r}")
    with _conn(db_path) as conn:
        conn.execute(
            "UPDATE invoices SET payment_status = ? WHERE invoice_number = ?",
            (status, invoice_number),
        )


def invoice_summary(db_path: Path = DEFAULT_DB_PATH) -> dict:
    """Portfolio-level invoice summary."""
    with _conn(db_path) as conn:
        row = conn.execute("""
            SELECT
                COUNT(*) as total_count,
                SUM(total_gbp) as total_billed_gbp,
                SUM(CASE WHEN payment_status = 'paid' THEN total_gbp ELSE 0 END) as paid_gbp,
                SUM(CASE WHEN payment_status = 'unpaid' THEN total_gbp ELSE 0 END) as outstanding_gbp,
                SUM(CASE WHEN payment_status = 'bad_debt' THEN total_gbp ELSE 0 END) as bad_debt_gbp
            FROM invoices
        """).fetchone()
        return dict(row) if row else {}
