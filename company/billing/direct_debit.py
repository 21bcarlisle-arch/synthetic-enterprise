"""Direct Debit mandate and payment schedule management.

UK energy suppliers collect recurring payments via BACS Direct Debit.
This module manages DD mandates, payment schedules, and failed-payment
tracking — all from company-observable data (no SIM internals).

Mandate lifecycle: active → cancelled | failed → reinstated.
Failed DDs trigger debt escalation after 2 missed payments.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Literal


_DD_SCHEDULE_DAYS = 28  # standard BACS cycle


@dataclass
class DirectDebitMandate:
    customer_id: str
    mandate_reference: str
    bank_sort_code: str  # masked, e.g. "12-34-**"
    bank_account_last4: str
    monthly_amount_gbp: float
    status: Literal["active", "cancelled", "suspended"] = "active"
    setup_date: str = ""
    next_collection_date: str = ""
    failed_attempts: int = 0
    # Bacs rails observability (W5_1_banking_payment_rails, 2026-07-12,
    # L2->L3): the AUDDIS submission reference/confirmation date for this
    # mandate's own setup, and for its most recent amendment (if any) --
    # populated by simulation/dd_collection_book.py via
    # simulation/bacs_rails.py, never set directly by this module. Empty
    # string means "not yet observed via the rails layer" (e.g. a mandate
    # created through a path that doesn't use the rails wiring).
    setup_rails_reference: str = ""
    setup_confirmed_date: str = ""
    last_amendment_rails_reference: str = ""
    last_amendment_confirmed_date: str = ""


@dataclass
class DDPaymentAttempt:
    mandate_reference: str
    customer_id: str
    attempt_date: str
    amount_gbp: float
    outcome: Literal["collected", "failed", "cancelled"]
    failure_reason: str = ""


class DirectDebitBook:
    """In-memory mandate + attempt store for the company billing layer."""

    def __init__(self):
        self._mandates: dict[str, DirectDebitMandate] = {}
        self._attempts: list[DDPaymentAttempt] = []

    def create_mandate(
        self,
        customer_id: str,
        sort_code: str,
        account_last4: str,
        monthly_amount_gbp: float,
        setup_date: str,
        setup_rails_reference: str = "",
        setup_confirmed_date: str = "",
    ) -> DirectDebitMandate:
        """Register a new DD mandate and return it. `setup_rails_reference`/
        `setup_confirmed_date` are optional Bacs-rails observability fields
        (simulation/dd_collection_book.py -- AUDDIS confirmation timing);
        omit for a mandate created outside that wiring."""
        ref = f"DD-{customer_id}-{setup_date.replace('-', '')}"
        next_collect = _add_days(setup_date, _DD_SCHEDULE_DAYS)
        m = DirectDebitMandate(
            customer_id=customer_id,
            mandate_reference=ref,
            bank_sort_code=sort_code,
            bank_account_last4=account_last4,
            monthly_amount_gbp=monthly_amount_gbp,
            setup_date=setup_date,
            next_collection_date=next_collect,
            setup_rails_reference=setup_rails_reference,
            setup_confirmed_date=setup_confirmed_date,
        )
        self._mandates[customer_id] = m
        return m

    def amend_mandate(
        self,
        customer_id: str,
        new_monthly_amount_gbp: float,
        rails_reference: str = "",
        confirmed_date: str = "",
    ) -> DirectDebitMandate | None:
        """Update an existing mandate's collection amount (a real, common
        occurrence -- 'most energy suppliers adjust the monthly collection
        amount to match estimated annual consumption', per this project's
        own dd_mandate_register.py docstring). Returns None if no mandate
        exists for this customer yet (caller's responsibility to create one
        first via create_mandate). `rails_reference`/`confirmed_date` are the
        same Bacs-rails (ADDACS) observability fields as create_mandate's."""
        m = self._mandates.get(customer_id)
        if m is None:
            return None
        m.monthly_amount_gbp = new_monthly_amount_gbp
        m.last_amendment_rails_reference = rails_reference
        m.last_amendment_confirmed_date = confirmed_date
        return m

    def get_mandate(self, customer_id: str) -> DirectDebitMandate | None:
        return self._mandates.get(customer_id)

    def active_mandates(self) -> list[DirectDebitMandate]:
        return [m for m in self._mandates.values() if m.status == "active"]

    def record_attempt(self, attempt: DDPaymentAttempt) -> None:
        """Record a collection attempt and update mandate state."""
        self._attempts.append(attempt)
        m = self._mandates.get(attempt.customer_id)
        if m is None:
            return
        if attempt.outcome == "collected":
            m.failed_attempts = 0
            m.next_collection_date = _add_days(attempt.attempt_date, _DD_SCHEDULE_DAYS)
        elif attempt.outcome == "failed":
            m.failed_attempts += 1
            if m.failed_attempts >= 2:
                m.status = "suspended"

    def cancel_mandate(self, customer_id: str) -> bool:
        m = self._mandates.get(customer_id)
        if m is None:
            return False
        m.status = "cancelled"
        return True

    def reinstate_mandate(self, customer_id: str) -> bool:
        m = self._mandates.get(customer_id)
        if m is None:
            return False
        m.status = "active"
        m.failed_attempts = 0
        return True

    def failed_mandates(self) -> list[DirectDebitMandate]:
        return [m for m in self._mandates.values() if m.status == "suspended"]

    def attempts_for_customer(self, customer_id: str) -> list[DDPaymentAttempt]:
        return [a for a in self._attempts if a.customer_id == customer_id]

    def failed_attempts_for_customer(self, customer_id: str) -> list[DDPaymentAttempt]:
        return [a for a in self.attempts_for_customer(customer_id) if a.outcome == "failed"]

    def dd_summary(self) -> dict:
        all_m = list(self._mandates.values())
        return {
            "total": len(all_m),
            "active": sum(1 for m in all_m if m.status == "active"),
            "suspended": sum(1 for m in all_m if m.status == "suspended"),
            "cancelled": sum(1 for m in all_m if m.status == "cancelled"),
            "total_monthly_gbp": round(
                sum(m.monthly_amount_gbp for m in all_m if m.status == "active"), 2
            ),
        }


def _add_days(date_str: str, days: int) -> str:
    d = date.fromisoformat(date_str)
    return (d + timedelta(days=days)).isoformat()


# ---------------------------------------------------------------------------
# SQLite-backed portal helpers (used by company/portal/app.py)
# ---------------------------------------------------------------------------

import sqlite3
from pathlib import Path


def _init_db(db_path):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mandates (
            customer_id TEXT PRIMARY KEY,
            sort_code TEXT,
            account_number TEXT,
            payment_day INTEGER,
            monthly_amount_gbp REAL DEFAULT 0.0,
            status TEXT DEFAULT 'active',
            created_date TEXT
        )
    """)
    conn.commit()
    return conn


def get_mandate(customer_id, db_path):
    from pathlib import Path
    db_path = Path(db_path)
    if not db_path.exists():
        return None
    conn = _init_db(db_path)
    row = conn.execute("SELECT * FROM mandates WHERE customer_id=?", (customer_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def set_mandate(customer_id, sort_code, account_number, payment_day, db_path):
    from datetime import date as _date
    from pathlib import Path
    db_path = Path(db_path)
    if payment_day < 1 or payment_day > 28:
        raise ValueError("Payment day must be between 1 and 28")
    conn = _init_db(db_path)
    today = _date.today().isoformat()
    conn.execute("""
        INSERT INTO mandates (customer_id, sort_code, account_number, payment_day, status, created_date)
        VALUES (?, ?, ?, ?, 'active', ?)
        ON CONFLICT(customer_id) DO UPDATE SET
            sort_code=excluded.sort_code,
            account_number=excluded.account_number,
            payment_day=excluded.payment_day,
            status='active'
    """, (customer_id, sort_code, account_number, payment_day, today))
    conn.commit()
    row = conn.execute("SELECT * FROM mandates WHERE customer_id=?", (customer_id,)).fetchone()
    conn.close()
    return dict(row)


def cancel_mandate(customer_id, db_path):
    from pathlib import Path
    db_path = Path(db_path)
    if not db_path.exists():
        return False
    conn = _init_db(db_path)
    conn.execute("UPDATE mandates SET status='cancelled' WHERE customer_id=?", (customer_id,))
    conn.commit()
    conn.close()
    return True


def is_dd_customer(customer_id, db_path):
    mandate = get_mandate(customer_id, db_path)
    return mandate is not None and mandate.get("status") == "active"
