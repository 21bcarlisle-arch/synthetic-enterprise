"""Direct Debit mandate management (company layer).

Stores active DD mandates in SQLite. A mandate records the customer's bank
details and preferred collection day. Used by billing to know whether to
collect via DD or send a paper invoice for manual payment.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DB_PATH = Path("company/data/direct_debit.db")


@dataclass
class DDMandate:
    account_id: str
    sort_code: str
    account_number: str
    payment_day: int
    created_at: str
    active: bool = True


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


def _create_schema(db_path: Path = DEFAULT_DB_PATH) -> None:
    with _conn(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dd_mandates (
                account_id    TEXT PRIMARY KEY,
                sort_code     TEXT NOT NULL,
                account_number TEXT NOT NULL,
                payment_day   INTEGER NOT NULL CHECK(payment_day BETWEEN 1 AND 28),
                created_at    TEXT NOT NULL,
                active        INTEGER NOT NULL DEFAULT 1
            )
        """)


def set_mandate(
    account_id: str,
    sort_code: str,
    account_number: str,
    payment_day: int = 1,
    db_path: Path = DEFAULT_DB_PATH,
) -> DDMandate:
    """Create or replace the DD mandate for this account."""
    if not 1 <= payment_day <= 28:
        raise ValueError(f"payment_day must be 1-28, got {payment_day}")
    _create_schema(db_path)
    created_at = datetime.now(timezone.utc).isoformat()
    with _conn(db_path) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO dd_mandates"
            " (account_id, sort_code, account_number, payment_day, created_at, active)"
            " VALUES (?, ?, ?, ?, ?, 1)",
            (account_id, sort_code, account_number, payment_day, created_at),
        )
    return DDMandate(account_id, sort_code, account_number, payment_day, created_at)


def get_mandate(
    account_id: str,
    db_path: Path = DEFAULT_DB_PATH,
) -> DDMandate | None:
    """Return the active DDMandate for an account, or None."""
    _create_schema(db_path)
    with _conn(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM dd_mandates WHERE account_id = ? AND active = 1",
            (account_id,),
        ).fetchone()
    if row is None:
        return None
    return DDMandate(
        account_id=row["account_id"],
        sort_code=row["sort_code"],
        account_number=row["account_number"],
        payment_day=row["payment_day"],
        created_at=row["created_at"],
        active=bool(row["active"]),
    )


def cancel_mandate(
    account_id: str,
    db_path: Path = DEFAULT_DB_PATH,
) -> bool:
    """Cancel the mandate for this account. Returns True if one existed."""
    _create_schema(db_path)
    with _conn(db_path) as conn:
        n = conn.execute(
            "UPDATE dd_mandates SET active = 0 WHERE account_id = ? AND active = 1",
            (account_id,),
        ).rowcount
    return n > 0


def is_dd_customer(account_id: str, db_path: Path = DEFAULT_DB_PATH) -> bool:
    """Return True if this account has an active DD mandate."""
    return get_mandate(account_id, db_path) is not None


def list_mandates(db_path: Path = DEFAULT_DB_PATH) -> list[DDMandate]:
    """Return all active DD mandates."""
    _create_schema(db_path)
    with _conn(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM dd_mandates WHERE active = 1 ORDER BY account_id"
        ).fetchall()
    return [
        DDMandate(
            account_id=r["account_id"],
            sort_code=r["sort_code"],
            account_number=r["account_number"],
            payment_day=r["payment_day"],
            created_at=r["created_at"],
            active=bool(r["active"]),
        )
        for r in rows
    ]
