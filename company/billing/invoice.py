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
                commodity_amount_gbp REAL NOT NULL DEFAULT 0.0,
                non_commodity_amount_gbp REAL NOT NULL DEFAULT 0.0,
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
        for col, defval in (("commodity_amount_gbp", "0.0"), ("non_commodity_amount_gbp", "0.0")):
            try:
                conn.execute(f"ALTER TABLE invoices ADD COLUMN {col} REAL NOT NULL DEFAULT {defval}")
            except Exception:
                pass


def _unit_rate_from_bill(bill: dict) -> float:
    """Derive p/kWh from bill dict — bills carry total_amount_gbp and total_consumption_kwh."""
    kwh = bill.get("total_consumption_kwh", 0.0)
    gbp = bill.get("total_amount_gbp", 0.0)
    if kwh > 0:
        return (gbp / kwh) * 100.0  # convert £/kWh → p/kWh
    return 0.0


def create_invoice(bill: dict, db_path: Path = DEFAULT_DB_PATH) -> int:
    """Create an invoice from a simulation bill dict. Returns invoice_number.

    Uses line-item breakdown if available (bills from Phase 9a+ bill_generator):
    commodity_amount_gbp, non_commodity_amount_gbp, standing_charge_gbp, vat_gbp.
    Falls back to total_amount_gbp as pre-tax subtotal for legacy/test bills.
    """
    create_schema(db_path)
    kwh = bill.get("total_consumption_kwh", 0.0)
    period_end = bill.get("period_end", bill.get("period_start", ""))
    issue_date = period_end
    due_date = (
        date.fromisoformat(issue_date) + timedelta(days=PAYMENT_TERMS_DAYS)
    ).isoformat() if issue_date else ""
    unit_rate_p = _unit_rate_from_bill(bill)
    commodity = bill.get("commodity", "electricity")

    commodity_gbp = bill.get("commodity_amount_gbp", 0.0)
    non_comm_gbp = bill.get("non_commodity_amount_gbp", 0.0)
    sc_gbp = bill.get("standing_charge_gbp", 0.0)

    if commodity_gbp or non_comm_gbp or sc_gbp:
        subtotal = round(commodity_gbp + non_comm_gbp + sc_gbp, 2)
        vat = round(bill.get("vat_gbp", subtotal * VAT_RATE), 2)
    else:
        subtotal = bill.get("total_amount_gbp", 0.0)
        vat = round(subtotal * VAT_RATE, 2)
        commodity_gbp = subtotal

    total = round(subtotal + vat, 2)

    with _conn(db_path) as conn:
        cursor = conn.execute("""
            INSERT INTO invoices
                (account_id, billing_period_start, billing_period_end,
                 consumption_kwh, unit_rate_p_per_kwh,
                 commodity_amount_gbp, non_commodity_amount_gbp,
                 standing_charge_gbp, subtotal_gbp, vat_gbp, total_gbp,
                 issue_date, due_date, payment_status, commodity)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            bill["customer_id"],
            bill.get("period_start", ""),
            period_end,
            kwh,
            round(unit_rate_p, 4),
            round(commodity_gbp, 2),
            round(non_comm_gbp, 2),
            round(sc_gbp, 2),
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
    create_schema(db_path)
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


# ---------------------------------------------------------------------------
# INDEPENDENT CONTROL TOTALS (D5 R15 wiring — additive, read-oriented).
#
# The account_ledger reconciliation controls (AccountLedger.reconcile /
# verify_against_invoicing, AllocationResult.check_conserved) need control totals
# sourced INDEPENDENTLY of the ledger's own event set — otherwise they are
# tautologies (a dropped/duplicated ledger event would move both sides together
# and never be caught). This module is that independent source: the invoicing
# register holds what was BILLED (issued invoices), and a small additive cash-book
# table holds what CASH was RECEIVED. A real supplier reconciles its AR sub-ledger
# against exactly these two independently-held control accounts.
#
# ADDITIVE ONLY: a new `payments` (cash-book) table plus read accessors. No
# existing invoice behaviour changes. Epistemic wall: issued invoices and received
# cash are the supplier's OWN records — no simulation internals are read.
# ---------------------------------------------------------------------------


def _as_of_iso(as_of) -> str | None:
    """Normalise an as-of bound (a date, datetime, or ISO string) to an ISO date
    string for lexical comparison against the ISO date columns. None ⇒ no bound."""
    if as_of is None:
        return None
    if isinstance(as_of, str):
        return as_of
    iso = getattr(as_of, "isoformat", None)
    if iso is not None:
        return as_of.isoformat()[:10]
    raise TypeError(f"unsupported as_of type: {type(as_of)!r}")


def create_payments_schema(db_path: Path = DEFAULT_DB_PATH) -> None:
    """Create the cash-book (received-payments) schema. Idempotent. This is the
    INDEPENDENT record of cash received against an account — the control total the
    ledger's payment-credit total must reconcile to."""
    with _conn(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                payment_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                payment_ref     TEXT UNIQUE,        -- optional external idempotency key
                account_id      TEXT NOT NULL,
                invoice_number  INTEGER,            -- optional: invoice remitted against
                amount_gbp      REAL NOT NULL,
                value_date      TEXT NOT NULL,      -- date the cash was received (valid_time)
                recorded_at     TEXT NOT NULL       -- when we recorded it (transaction_time)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_pay_account ON payments(account_id)")


def record_payment(
    account_id: str,
    amount_gbp: float,
    value_date: str,
    invoice_number: int | None = None,
    payment_ref: str | None = None,
    recorded_at: str | None = None,
    db_path: Path = DEFAULT_DB_PATH,
) -> int | None:
    """Record cash received against an account in the independent cash book.

    Idempotent when a `payment_ref` is supplied: a re-record of the same ref is a
    no-op (returns the existing payment_id) — matching the ledger's own idempotency
    (C-S2). Returns the payment_id, or the existing one on a duplicate ref.
    """
    if amount_gbp <= 0:
        raise ValueError("payment amount must be positive")
    create_payments_schema(db_path)
    with _conn(db_path) as conn:
        if payment_ref is not None:
            existing = conn.execute(
                "SELECT payment_id FROM payments WHERE payment_ref = ?", (payment_ref,)
            ).fetchone()
            if existing is not None:
                return existing["payment_id"]
        cursor = conn.execute(
            """INSERT INTO payments
                   (payment_ref, account_id, invoice_number, amount_gbp,
                    value_date, recorded_at)
               VALUES (?,?,?,?,?,?)""",
            (
                payment_ref,
                account_id,
                invoice_number,
                round(amount_gbp, 2),
                value_date,
                recorded_at or date.today().isoformat(),
            ),
        )
        return cursor.lastrowid


def issued_debits_gbp(
    account_id: str, as_of=None, db_path: Path = DEFAULT_DB_PATH
) -> float:
    """INDEPENDENT debit control total: the gross (VAT-inclusive) value of every
    invoice issued to this account, optionally bounded to issue_date <= as_of
    (point-in-time honest). This is what the ledger's total bill-debit MUST equal.

    Sourced from the invoicing register, NOT from the ledger's events — that
    independence is what makes reconcile() a real control and not a tautology.
    """
    create_schema(db_path)
    bound = _as_of_iso(as_of)
    with _conn(db_path) as conn:
        if bound is None:
            row = conn.execute(
                "SELECT COALESCE(SUM(total_gbp), 0.0) AS t FROM invoices WHERE account_id = ?",
                (account_id,),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT COALESCE(SUM(total_gbp), 0.0) AS t FROM invoices "
                "WHERE account_id = ? AND issue_date <= ?",
                (account_id, bound),
            ).fetchone()
        return round(row["t"], 2)


def cash_received_gbp(
    account_id: str, as_of=None, db_path: Path = DEFAULT_DB_PATH
) -> float:
    """INDEPENDENT credit control total: total cash received against this account
    per the cash book, optionally bounded to value_date <= as_of. This is what the
    ledger's total payment-credit MUST equal. Sourced from the cash-book table, not
    the ledger — independent by construction."""
    create_payments_schema(db_path)
    bound = _as_of_iso(as_of)
    with _conn(db_path) as conn:
        if bound is None:
            row = conn.execute(
                "SELECT COALESCE(SUM(amount_gbp), 0.0) AS t FROM payments WHERE account_id = ?",
                (account_id,),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT COALESCE(SUM(amount_gbp), 0.0) AS t FROM payments "
                "WHERE account_id = ? AND value_date <= ?",
                (account_id, bound),
            ).fetchone()
        return round(row["t"], 2)


class InvoiceControlSource:
    """A thin, duck-typed adapter the ledger reconciles AGAINST. Wraps the invoice
    DB path and exposes exactly the two accessors AccountLedger.verify_against_
    invoicing() / verify_allocation_conserved() call — keeping the ledger free of
    any SQLite/import coupling and preserving the independence of the two stores.

    Bind it to the live invoice DB and hand it to the ledger; the ledger never
    reads the invoice store directly, it only asks this source for its totals.
    """

    def __init__(self, db_path: Path = DEFAULT_DB_PATH) -> None:
        self.db_path = db_path

    def issued_debits_gbp(self, account_id: str, as_of=None) -> float:
        return issued_debits_gbp(account_id, as_of=as_of, db_path=self.db_path)

    def cash_received_gbp(self, account_id: str, as_of=None) -> float:
        return cash_received_gbp(account_id, as_of=as_of, db_path=self.db_path)


def format_invoice_text(invoice: dict) -> str:
    """Render a structured text invoice from a stored invoice record."""
    lines = [
        'INVOICE',
        '=======',
        f'Invoice No: {invoice.get("invoice_number", "")}',
        f'Issue Date: {invoice.get("issue_date", "")}',
        f'Due Date:   {invoice.get("due_date", "")}',
        '',
        f'Account:        {invoice.get("account_id", "")}',
        f'Commodity:      {invoice.get("commodity", "electricity").capitalize()}',
        '',
        f'Billing Period: {invoice.get("billing_period_start", "")} to {invoice.get("billing_period_end", "")}',
        '',
        'LINE ITEMS',
        '----------',
    ]
    kwh = invoice.get('consumption_kwh', 0.0)
    rate_p = invoice.get('unit_rate_p_per_kwh', 0.0)
    commodity_gbp = invoice.get('commodity_amount_gbp', 0.0)
    non_comm_gbp = invoice.get('non_commodity_amount_gbp', 0.0)
    sc_gbp = invoice.get('standing_charge_gbp', 0.0)
    subtotal = invoice.get('subtotal_gbp', 0.0)
    vat = invoice.get('vat_gbp', 0.0)
    total = invoice.get('total_gbp', 0.0)

    lines += [
        f'  Consumption:          {kwh:>10,.2f} kWh',
        f'  Unit Rate:            {rate_p:>10.4f} p/kWh',
        f'  Energy Charge:          {commodity_gbp:>8,.2f}',
    ]
    if sc_gbp:
        lines.append(f'  Standing Charge:        {sc_gbp:>8,.2f}')
    if non_comm_gbp:
        lines.append(f'  Network & Levies:       {non_comm_gbp:>8,.2f}')
    lines += [
        '',
        f'Subtotal                  {subtotal:>8,.2f}',
        f'VAT                       {vat:>8,.2f}',
        '-' * 38,
        f'TOTAL DUE                 {total:>8,.2f}',
        '',
        f'Payment Status: {invoice.get("payment_status", "unpaid").upper()}',
    ]
    return chr(10).join(lines)

