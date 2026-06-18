"""Company Layer — Customer Registry (CRM foundation).

A persistent customer record store separate from the simulation's in-memory
customer objects. Backed by SQLite. The simulation updates status by calling
this registry; the company layer reads from it without touching simulation internals.

Synthetic contact details are generated deterministically from account ID.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

DEFAULT_DB_PATH = Path("company/data/registry.db")


def _mpan(account_id: str) -> str:
    """Synthetic MPAN (Meter Point Administration Number) — 13 digits."""
    seed = sum(ord(c) for c in account_id)
    return f"1{seed:012d}"[:13]


def _mprn(account_id: str) -> str:
    """Synthetic MPRN (Meter Point Reference Number) — 10 digits."""
    seed = sum(ord(c) * 17 for c in account_id)
    return f"{seed:010d}"[:10]


def _contact_name(account_id: str) -> str:
    names = {
        "C1": "Alice Thompson", "C2": "Ben Hargreaves", "C3": "Celia McBride",
        "C4": "David Whitfield", "C5": "Everton Supplies Ltd", "C6": "Fenwick Warehouse Co",
        "C7": "George Patel", "C8": "Hannah Osei", "C9": "Ivan Kowalski",
        "C1_2": "James Thornton", "C2_2": "Karen Mehta", "C3_2": "Liam Donnelly",
        "C4_2": "Meera Patel", "C5_2": "Nexus Office Solutions", "C6_2": "Orion Storage Ltd",
    }
    return names.get(account_id, f"Customer {account_id}")


def _address(location: dict, home_type: str) -> str:
    region = location.get("region", "Unknown")
    type_map = {
        "urban_flat": "Flat 4, 12 High Street",
        "suburban_semi": "42 Maple Avenue",
        "tenement_flat": "2F1, 88 Byres Road",
        "rural_detached": "The Old Mill, Mill Lane",
        "small_office": "Suite 3, Business Centre",
        "warehouse_unit": "Unit 7, Industrial Estate",
    }
    street = type_map.get(home_type, "1 Main Street")
    return f"{street}, {region}"


def _fuel_type(commodity: str, customer_id: str) -> str:
    """Determine fuel type from customer data."""
    if commodity == "gas":
        return "gas"
    # Check if there's a corresponding gas leg (C1g-C4g)
    base = customer_id.rstrip("g")
    if customer_id.endswith("g"):
        return "gas"
    if base in ("C1", "C2", "C3", "C4") and not customer_id.endswith("_2"):
        return "dual"
    return "electricity"


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
    """Create the customer registry schema. Idempotent."""
    with _conn(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                account_id      TEXT PRIMARY KEY,
                customer_type   TEXT NOT NULL,  -- residential / SME
                fuel_type       TEXT NOT NULL,  -- electricity / gas / dual
                supply_start    TEXT NOT NULL,
                status          TEXT NOT NULL DEFAULT 'active',  -- active / churned / pending
                tariff_type     TEXT NOT NULL DEFAULT 'fixed',
                contact_name    TEXT,
                address         TEXT,
                email           TEXT,
                mpan            TEXT,
                mprn            TEXT,
                smart_meter     INTEGER NOT NULL DEFAULT 0,  -- 0/1 bool
                segment         TEXT NOT NULL,
                successor_of    TEXT,
                created_at      TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON customers(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_segment ON customers(segment)")


def _customer_type(segment: str) -> str:
    return "SME" if segment == "SME" else "residential"


def seed_from_customers(customers: list[dict], db_path: Path = DEFAULT_DB_PATH) -> int:
    """Insert customer records from the simulation's customer list.

    Skips records that already exist (INSERT OR IGNORE). Returns count inserted.
    """
    create_schema(db_path)
    inserted = 0
    with _conn(db_path) as conn:
        for c in customers:
            cid = c["customer_id"]
            commodity = c.get("commodity", "electricity")
            fuel = _fuel_type(commodity, cid)
            ctype = _customer_type(c.get("segment", "resi"))
            is_smart = 1 if c.get("metering") == "HH" else 0
            loc = c.get("location", {})
            addr = _address(loc, c.get("home_type", ""))
            email = f"{cid.lower().replace('_', '')}@synthetic-supplier.co.uk"
            cursor = conn.execute("""
                INSERT OR IGNORE INTO customers
                    (account_id, customer_type, fuel_type, supply_start, status,
                     tariff_type, contact_name, address, email, mpan, mprn,
                     smart_meter, segment, successor_of)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                cid, ctype, fuel, c.get("acquisition_date", "2016-01-01"), "active",
                c.get("contract_type", "fixed_1yr").replace("_1yr", ""),
                _contact_name(cid), addr, email,
                _mpan(cid), _mprn(cid) if commodity in ("gas", "dual") else None,
                is_smart, c.get("segment", "resi"),
                c.get("successor_of"),
            ))
            inserted += cursor.rowcount
    return inserted


def get_account(account_id: str, db_path: Path = DEFAULT_DB_PATH) -> dict | None:
    """Return a customer record as a dict, or None if not found."""
    with _conn(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM customers WHERE account_id = ?", (account_id,)
        ).fetchone()
        return dict(row) if row else None


def update_status(
    account_id: str,
    status: str,
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    """Update a customer's status (active / churned / pending)."""
    if status not in ("active", "churned", "pending"):
        raise ValueError(f"Invalid status: {status!r}")
    with _conn(db_path) as conn:
        conn.execute(
            "UPDATE customers SET status = ? WHERE account_id = ?",
            (status, account_id),
        )


def all_accounts(
    status_filter: str | None = None,
    db_path: Path = DEFAULT_DB_PATH,
) -> list[dict]:
    """Return all customer records, optionally filtered by status."""
    with _conn(db_path) as conn:
        if status_filter:
            rows = conn.execute(
                "SELECT * FROM customers WHERE status = ? ORDER BY account_id",
                (status_filter,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM customers ORDER BY account_id"
            ).fetchall()
        return [dict(r) for r in rows]


def account_count(db_path: Path = DEFAULT_DB_PATH) -> int:
    """Total accounts in the registry."""
    with _conn(db_path) as conn:
        return conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
