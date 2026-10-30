"""Company Layer — Customer Registry (CRM foundation).

A persistent customer record store separate from the simulation's in-memory
customer objects. Backed by SQLite. The simulation updates status by calling
this registry; the company layer reads from it without touching simulation internals.

Synthetic contact details are generated deterministically from account ID.
"""

import hashlib
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Mapping, Optional

from company.crm.supply_start import (
    derive_supply_start,
    derive_term_anchor,
    migrate_legacy_supply_start,
)

DEFAULT_DB_PATH = Path("company/data/registry.db")


#: The fourteen DNO distributor IDs and the core's check-digit weights
#: (docs/domain_artefact_library/regulatory/mpan_core_structure_and_check_digit.md).
MPAN_DISTRIBUTOR_IDS = tuple(str(i) for i in range(10, 24))
MPAN_CHECK_WEIGHTS = (3, 5, 7, 13, 17, 19, 23, 29, 31, 37, 41, 43)


def mpan_core(account_id: str) -> str:
    """The supply point's MPAN core (pass `supply_point_of(account)`, not the account): distributor ID, ten digits of a hash of the account, check digit.

    The one home for it: the ledger, the customer pages and this registry each used to mint their
    own, and on the 2eeb3f0b3 book 707 electricity accounts shared 158 cores, none with a check
    digit. A display identifier only. The world draws no region, so the distributor is the hash's,
    not a place the household is in (GAP).
    """
    h = int(hashlib.sha256(account_id.encode()).hexdigest(), 16)
    first12 = MPAN_DISTRIBUTOR_IDS[h % len(MPAN_DISTRIBUTOR_IDS)] + str(h // 14 % 10**10).zfill(10)
    return first12 + str(sum(int(c) * w for c, w in zip(first12, MPAN_CHECK_WEIGHTS)) % 11 % 10)


_mpan = mpan_core


def mprn(supply_point: str) -> str:
    """The gas supply point's MPRN: ten digits of a hash. No public check-digit standard is held here.

    The one home for it. The ledger summed character codes (586 gas accounts on 164 numbers on the
    1691ec0ecd book) and the customer page hashed its own eight digits, so no gas page's header
    matched its own invoices.
    """
    return str(10**9 + int(hashlib.sha256((supply_point + "-mprn").encode()).hexdigest(), 16) % (9 * 10**9))


_mprn = mprn


def meter_serial(supply_point: str, commodity: str) -> str:
    """The supply point's meter serial (pass `supply_point_of(account)`): M and ten digits of a hash of the point and fuel.

    The one home for it. The ledger summed the id's character codes, which ignores their order, so the
    3dc5a92948 book's 1,293 pages carried 127 serials, 96 of them on 2 to 34 supply points (fifth cold
    read, N10). Ten digits keep a chance collision rare, and INV_METER_SERIAL_ONE_SUPPLY_POINT grades the
    book for any that survive. One meter for the life of the supply point: no exchange is minted here.
    No published serial format is held (that row's GAP 1), so the shape is a display choice.
    """
    h = int(hashlib.sha256("{}-{}-serial".format(supply_point, commodity).encode()).hexdigest(), 16)
    return "M" + str(h % 10**10).zfill(10)


def supply_point_of(account_id: str, predecessor_of: Mapping[str, str]) -> str:
    """The account that first held this account's meter point: the key its MPAN or MPRN is minted from.

    A supply belongs to a meter point, not to a household (docs/market_research/home_moves.md, "What a
    gas supply is, at a move"), so an incoming occupier's account (`predecessor_of`, the run's
    `occupier_successions`, one row per fuel leg) prints the number its predecessor printed. Keyed to
    the account until 2026-10-28, when 253 of 253 successions on 1691ec0ecd printed a different one.
    """
    seen = {account_id}
    while (prev := predecessor_of.get(account_id)) and prev not in seen:
        seen.add(prev)
        account_id = prev
    return account_id


def predecessors(successions) -> dict[str, str]:
    """account -> the account it succeeded, from a run's `occupier_successions` (None: no moves)."""
    return {s["account_id"]: s["predecessor_account_id"] for s in successions or ()
            if s.get("predecessor_account_id")}


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


# `supply_start` is deliberately NULLABLE: NULL means UNKNOWN -- we do not know
# when this customer's supply with us began. `term_anchor_date` carries the
# renewal-grid anchor that `supply_start` used to be silently overwritten with.
# See company/crm/supply_start.py for why the two are separate.
_SCHEMA = """
    CREATE TABLE IF NOT EXISTS customers (
        account_id       TEXT PRIMARY KEY,
        customer_type    TEXT NOT NULL,  -- residential / SME
        fuel_type        TEXT NOT NULL,  -- electricity / gas / dual
        supply_start     TEXT,           -- real relationship start; NULL = UNKNOWN
        term_anchor_date TEXT NOT NULL,  -- 365-day renewal grid anchor
        status           TEXT NOT NULL DEFAULT 'active',  -- active / churned / pending
        tariff_type      TEXT NOT NULL DEFAULT 'fixed',
        contact_name     TEXT,
        address          TEXT,
        email            TEXT,
        mpan             TEXT,
        mprn             TEXT,
        smart_meter      INTEGER NOT NULL DEFAULT 0,  -- 0/1 bool
        segment          TEXT NOT NULL,
        successor_of     TEXT,
        created_at       TEXT NOT NULL DEFAULT (datetime('now'))
    )
"""

_COLUMNS = (
    "account_id, customer_type, fuel_type, supply_start, term_anchor_date, status, "
    "tariff_type, contact_name, address, email, mpan, mprn, smart_meter, segment, "
    "successor_of"
)


def _table_columns(conn, table: str) -> list[str]:
    return [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]


def _migrate_legacy_schema(conn) -> int:
    """Split the legacy single-date `supply_start` column in place.

    A pre-separation registry has one date column, fed from `acquisition_date`
    -- i.e. it actually held the term anchor. SQLite cannot drop a NOT NULL
    constraint in place, so the table is rebuilt. The per-row split rule lives
    in `supply_start.migrate_legacy_supply_start` (successors become UNKNOWN
    rather than keeping the predecessor's date). Returns rows migrated.
    """
    columns = _table_columns(conn, "customers")
    if not columns or "term_anchor_date" in columns:
        return 0  # fresh DB, or already migrated

    legacy = conn.execute(
        "SELECT account_id, supply_start, successor_of FROM customers"
    ).fetchall()
    conn.execute("DROP INDEX IF EXISTS idx_status")
    conn.execute("DROP INDEX IF EXISTS idx_segment")
    conn.execute("ALTER TABLE customers RENAME TO customers_legacy")
    conn.execute(_SCHEMA)
    conn.execute("""
        INSERT INTO customers
            (account_id, customer_type, fuel_type, supply_start, term_anchor_date,
             status, tariff_type, contact_name, address, email, mpan, mprn,
             smart_meter, segment, successor_of, created_at)
        SELECT account_id, customer_type, fuel_type, supply_start, supply_start,
               status, tariff_type, contact_name, address, email, mpan, mprn,
               smart_meter, segment, successor_of, created_at
        FROM customers_legacy
    """)
    for row in legacy:
        conn.execute(
            "UPDATE customers SET supply_start = ? WHERE account_id = ?",
            (migrate_legacy_supply_start(row["supply_start"], row["successor_of"]),
             row["account_id"]),
        )
    conn.execute("DROP TABLE customers_legacy")
    return len(legacy)


def create_schema(db_path: Path = DEFAULT_DB_PATH) -> None:
    """Create the customer registry schema, migrating a legacy DB. Idempotent."""
    with _conn(db_path) as conn:
        _migrate_legacy_schema(conn)
        conn.execute(_SCHEMA)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON customers(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_segment ON customers(segment)")


def _customer_type(segment: str) -> str:
    return "SME" if segment == "SME" else "residential"


def seed_from_customers(
    customers: list[dict],
    db_path: Path = DEFAULT_DB_PATH,
    activation_by_account: Optional[Mapping[str, str]] = None,
) -> int:
    """Insert customer records from the simulation's customer list.

    Skips records that already exist (INSERT OR IGNORE). Returns count inserted.

    `activation_by_account` maps account_id -> ISO activation date, sourced from
    the observable acquisition/registration event stream. It is what a real CRM
    records supply-start from. Accounts absent from it fall back to the rules in
    `company.crm.supply_start.derive_supply_start` -- which resolve a successor
    with no activation observable to UNKNOWN (NULL), never to the term anchor.
    Per C-S1 the mapping need not be complete: it is read per account, so a late
    or out-of-order activation event simply arrives on a later seed.
    """
    create_schema(db_path)
    inserted = 0
    successor_of = {c["customer_id"]: c["successor_of"] for c in customers if c.get("successor_of")}
    with _conn(db_path) as conn:
        for c in customers:
            cid = c["customer_id"]
            point = supply_point_of(cid, successor_of)
            commodity = c.get("commodity", "electricity")
            fuel = _fuel_type(commodity, cid)
            ctype = _customer_type(c.get("segment", "resi"))
            is_smart = 1 if c.get("metering") == "HH" else 0
            loc = c.get("location", {})
            addr = _address(loc, c.get("home_type", ""))
            email = f"{cid.lower().replace('_', '')}@synthetic-supplier.co.uk"
            cursor = conn.execute(f"""
                INSERT OR IGNORE INTO customers ({_COLUMNS})
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                cid, ctype, fuel,
                derive_supply_start(c, activation_by_account),
                derive_term_anchor(c),
                "active",
                c.get("contract_type", "fixed_1yr").replace("_1yr", ""),
                _contact_name(cid), addr, email,
                _mpan(point), _mprn(point) if commodity in ("gas", "dual") else None,
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
