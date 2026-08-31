"""CHARACTERIZATION: freezes current behaviour, including behaviour that may be
defective. Characterized, not endorsed.

Target: company/billing/invoice.py — the invoicing register. This is the module
that turns a simulation bill calculation into a retrievable document, and (from
the D5 R15 wiring) the INDEPENDENT control source the account ledger reconciles
against: `issued_debits_gbp` is what the ledger's bill-debit total MUST equal and
`cash_received_gbp` is what its payment-credit total MUST equal. A defect here is
therefore a defect in a control, not only in a document.

It is also the one money module that surfaces SQLite directly, so this file
doubles as the schema census the project does not otherwise have: the exact
tables, columns, declared types, NOT NULL flags, defaults and indices that
`create_schema` / `create_payments_schema` produce on first connect.

TMP-PATH-ONLY RULE (hard): `DEFAULT_DB_PATH = company/data/invoices.db` and
`_conn` does `db_path.parent.mkdir(parents=True, exist_ok=True)` — so ANY call
that omits `db_path` creates `company/data/` in the working tree. Every test here
passes an explicit `db_path` under pytest's `tmp_path`, and the autouse
`_never_touch_the_default_db` fixture below asserts that directory does not exist
before OR after each test. Nothing in this file constructs a real default-path
connection.

All inputs are fixed and explicit. No randomness: every date, amount and account
id is a literal, so these tests are stable under replay. The one wall-clock read
the module performs (`record_payment`'s `recorded_at` default) is characterized
against a clock bracket rather than a fixed value, and flagged as a finding.
"""
from __future__ import annotations

import datetime as dt
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

import pytest

from company.billing.invoice import (
    DEFAULT_DB_PATH,
    PAYMENT_TERMS_DAYS,
    VAT_RATE,
    InvoiceControlSource,
    bulk_create_invoices,
    cash_received_gbp,
    create_invoice,
    create_payments_schema,
    create_schema,
    format_invoice_text,
    get_invoice,
    invoice_summary,
    invoices_for_account,
    issued_debits_gbp,
    record_payment,
    update_payment_status,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DB_DIR = REPO_ROOT / DEFAULT_DB_PATH.parent   # company/data
DEFAULT_DB_FILE = REPO_ROOT / DEFAULT_DB_PATH         # company/data/invoices.db


def _default_db_fingerprint():
    """Everything about the REAL invoice DB a test in this file could disturb:
    whether its directory exists, whether the DB exists, and — if it does — its
    exact size and mtime. Compared before/after, so creating the directory,
    creating the DB, or WRITING to an existing one all fail."""
    dir_exists = DEFAULT_DB_DIR.exists()
    if not DEFAULT_DB_FILE.exists():
        return (dir_exists, False, None, None)
    st = DEFAULT_DB_FILE.stat()
    return (dir_exists, True, st.st_size, st.st_mtime_ns)


@pytest.fixture(autouse=True)
def _never_touch_the_default_db():
    """HARD RULE guard: no test in this file may create OR MODIFY the real invoice
    DB or its parent directory. `_conn` mkdirs the parent, so an accidental
    default-arg call would silently materialise `company/data/` in the working tree.

    Asserted as a before/after FINGERPRINT rather than "the directory must not
    exist" (2026-08-08). The absence form was a false positive that wedged the
    publish gate: `company/data/` is gitignored RUNTIME state and legitimately
    exists on the live machine (it holds `service_log.db`, written by a running
    daemon), so the guard reddened on a healthy tree and blamed a test that had
    done nothing. Fingerprinting is strictly STRONGER — the old form could not
    see a write to an already-existing DB, this one does — and it still attributes
    a leak to the test that caused it."""
    before = _default_db_fingerprint()
    yield
    assert _default_db_fingerprint() == before, (
        f"a test in this file created or modified the REAL invoice DB "
        f"({DEFAULT_DB_FILE}); every call must be given an explicit tmp_path DB"
    )


@pytest.fixture
def db(tmp_path) -> Path:
    """A fresh, non-existent DB path under tmp_path. Injected into every call."""
    return tmp_path / "invoices.db"


@pytest.fixture
def db2(tmp_path) -> Path:
    """A second independent DB path, for store-isolation characterization."""
    return tmp_path / "other.db"


@contextmanager
def raw(db_path: Path):
    """A direct connection, used only to OBSERVE (or pre-seed) what the module holds.

    Closes on exit — sqlite3.Connection's own `with` commits but does NOT close, and a
    leaked handle would hold locks that the two-connection tests below rely on being
    absent."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def bill(**overrides) -> dict:
    """A legacy-shape simulation bill: a single pre-tax total, no line items."""
    b = {
        "customer_id": "A1",
        "period_start": "2024-01-01",
        "period_end": "2024-01-31",
        "total_amount_gbp": 100.0,
        "total_consumption_kwh": 1000.0,
    }
    b.update(overrides)
    return b


def rich_bill(**overrides) -> dict:
    """A Phase-9a+ bill carrying the line-item breakdown."""
    b = bill(
        commodity_amount_gbp=120.0,
        non_commodity_amount_gbp=25.0,
        standing_charge_gbp=8.0,
        vat_gbp=7.65,
        total_amount_gbp=160.65,
    )
    b.update(overrides)
    return b


# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------


def test_module_constants_are_frozen():
    assert VAT_RATE == 0.05  # UK domestic reduced rate
    assert PAYMENT_TERMS_DAYS == 14
    assert DEFAULT_DB_PATH == Path("company/data/invoices.db")
    # SURPRISE (configuration class): DEFAULT_DB_PATH is a RELATIVE path, so which
    # file the whole invoicing register resolves to depends on the process's cwd.
    # Two processes started from different directories keep two different sets of
    # books, and neither reports an error.
    assert not DEFAULT_DB_PATH.is_absolute()


# ---------------------------------------------------------------------------
# SCHEMA CENSUS — the exact shape create_schema() produces on first connect.
# Columns are (cid, name, declared_type, notnull, default, pk).
# ---------------------------------------------------------------------------


INVOICES_COLUMNS = [
    (0, "invoice_number", "INTEGER", 0, None, 1),
    (1, "account_id", "TEXT", 1, None, 0),
    (2, "billing_period_start", "TEXT", 1, None, 0),
    (3, "billing_period_end", "TEXT", 1, None, 0),
    (4, "consumption_kwh", "REAL", 1, None, 0),
    (5, "unit_rate_p_per_kwh", "REAL", 1, None, 0),
    (6, "commodity_amount_gbp", "REAL", 1, "0.0", 0),
    (7, "non_commodity_amount_gbp", "REAL", 1, "0.0", 0),
    (8, "standing_charge_gbp", "REAL", 1, "0.0", 0),
    (9, "subtotal_gbp", "REAL", 1, None, 0),
    (10, "vat_gbp", "REAL", 1, None, 0),
    (11, "total_gbp", "REAL", 1, None, 0),
    (12, "issue_date", "TEXT", 1, None, 0),
    (13, "due_date", "TEXT", 1, None, 0),
    (14, "payment_status", "TEXT", 1, "'unpaid'", 0),
    (15, "commodity", "TEXT", 1, "'electricity'", 0),
]

PAYMENTS_COLUMNS = [
    (0, "payment_id", "INTEGER", 0, None, 1),
    (1, "payment_ref", "TEXT", 0, None, 0),
    (2, "account_id", "TEXT", 1, None, 0),
    (3, "invoice_number", "INTEGER", 0, None, 0),
    (4, "amount_gbp", "REAL", 1, None, 0),
    (5, "value_date", "TEXT", 1, None, 0),
    (6, "recorded_at", "TEXT", 1, None, 0),
]


def test_schema_census_invoices_table(db):
    create_schema(db)
    with raw(db) as conn:
        cols = [tuple(r) for r in conn.execute("PRAGMA table_info(invoices)")]
    assert cols == INVOICES_COLUMNS
    # Note: money is REAL (binary float), not INTEGER pence or DECIMAL — see the
    # rounding-coherence tests below for what that costs.
    assert all(c[2] == "REAL" for c in cols if c[1].endswith("_gbp"))
    # Every date column is TEXT, compared LEXICALLY everywhere in this module.
    assert [c[2] for c in cols if c[1] in ("issue_date", "due_date")] == ["TEXT", "TEXT"]


def test_schema_census_invoices_indices_and_constraints(db):
    create_schema(db)
    with raw(db) as conn:
        objects = {
            (r["type"], r["name"]): (r["sql"] or "")
            for r in conn.execute("SELECT type, name, sql FROM sqlite_master")
        }
    assert ("table", "invoices") in objects
    assert ("table", "sqlite_sequence") in objects  # created by AUTOINCREMENT
    indices = sorted(n for (t, n) in objects if t == "index")
    assert indices == ["idx_account", "idx_period", "idx_status"]
    assert objects[("index", "idx_account")] == "CREATE INDEX idx_account ON invoices(account_id)"
    assert objects[("index", "idx_status")] == (
        "CREATE INDEX idx_status ON invoices(payment_status)"
    )
    assert objects[("index", "idx_period")] == (
        "CREATE INDEX idx_period ON invoices(billing_period_start)"
    )
    # SURPRISE (integrity class): there is NO UNIQUE constraint anywhere on the
    # invoices table — not on (account_id, billing_period_start, billing_period_end),
    # not on any external bill reference. Nothing in the schema can stop the same
    # bill being invoiced twice; see the replay tests below.
    assert "UNIQUE" not in objects[("table", "invoices")].upper()
    # Nor is there an index on issue_date, the column issued_debits_gbp filters on.
    assert "idx_issue_date" not in indices


def test_schema_census_payments_table(db):
    create_payments_schema(db)
    with raw(db) as conn:
        cols = [tuple(r) for r in conn.execute("PRAGMA table_info(payments)")]
        objects = {
            (r["type"], r["name"]): (r["sql"] or "")
            for r in conn.execute("SELECT type, name, sql FROM sqlite_master")
        }
    assert cols == PAYMENTS_COLUMNS
    assert sorted(n for (t, n) in objects if t == "index") == [
        "idx_pay_account",
        "sqlite_autoindex_payments_1",  # implicit index behind payment_ref UNIQUE
    ]
    assert "payment_ref     TEXT UNIQUE" in objects[("table", "payments")]
    # SURPRISE (integrity class): payments.invoice_number is a plain INTEGER with no
    # FOREIGN KEY to invoices — a payment can be recorded against an invoice number
    # that does not exist, and nothing objects (frozen below).
    assert "FOREIGN KEY" not in objects[("table", "payments")].upper()


def test_the_two_schemas_are_created_independently(db, db2):
    """create_schema and create_payments_schema each create ONLY their own table, so
    a DB can hold one control account and not the other."""
    create_schema(db)
    with raw(db) as conn:
        assert "payments" not in {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
    create_payments_schema(db2)
    with raw(db2) as conn:
        assert "invoices" not in {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}


# ---------------------------------------------------------------------------
# create_schema(): first connect, idempotency, migration, hostile pre-existing table
# ---------------------------------------------------------------------------


def test_first_connect_creates_missing_parent_directories(tmp_path):
    """This is exactly why the tmp-path-only rule exists: _conn mkdirs the whole
    parent chain, so a default-arg call would create company/data/ in the repo."""
    nested = tmp_path / "deep" / "nested"
    assert not nested.exists()
    create_schema(nested / "invoices.db")
    assert nested.is_dir() and (nested / "invoices.db").exists()


def test_create_schema_is_idempotent_and_preserves_data(db):
    number = create_invoice(bill(), db)
    create_schema(db)
    create_schema(db)
    assert get_invoice(number, db)["total_gbp"] == 105.0
    with raw(db) as conn:
        cols = [tuple(r) for r in conn.execute("PRAGMA table_info(invoices)")]
    assert cols == INVOICES_COLUMNS  # no duplicated columns from the ALTER pass
    # SURPRISE (fail-silent class, R15): create_schema unconditionally issues two
    # `ALTER TABLE invoices ADD COLUMN ...` statements wrapped in a bare
    # `except Exception: pass`. On an already-current schema BOTH always fail with
    # "duplicate column name" and both failures are swallowed — every single call.
    # The swallow is not scoped to that error, so a genuine migration failure on a
    # legacy DB would be equally invisible: the function would return normally with
    # the column absent.


def test_create_schema_migrates_a_legacy_table_by_appending_columns(db):
    """A pre-9a DB lacking the two commodity split columns is migrated in place."""
    with raw(db) as conn:
        conn.execute("""
            CREATE TABLE invoices (
                invoice_number INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id TEXT NOT NULL,
                billing_period_start TEXT NOT NULL,
                billing_period_end TEXT NOT NULL,
                consumption_kwh REAL NOT NULL,
                unit_rate_p_per_kwh REAL NOT NULL,
                standing_charge_gbp REAL NOT NULL DEFAULT 0.0,
                subtotal_gbp REAL NOT NULL, vat_gbp REAL NOT NULL, total_gbp REAL NOT NULL,
                issue_date TEXT NOT NULL, due_date TEXT NOT NULL,
                payment_status TEXT NOT NULL DEFAULT 'unpaid',
                commodity TEXT NOT NULL DEFAULT 'electricity')
        """)
        conn.execute(
            "INSERT INTO invoices (account_id, billing_period_start, billing_period_end,"
            " consumption_kwh, unit_rate_p_per_kwh, subtotal_gbp, vat_gbp, total_gbp,"
            " issue_date, due_date) VALUES"
            " ('A1','2024-01-01','2024-01-31',1000.0,10.0,100.0,5.0,105.0,"
            "'2024-01-31','2024-02-14')"
        )
        conn.commit()

    create_schema(db)

    with raw(db) as conn:
        names = [r[1] for r in conn.execute("PRAGMA table_info(invoices)")]
        row = dict(conn.execute("SELECT * FROM invoices").fetchone())
    # SURPRISE (schema-drift class): ALTER TABLE appends, so on a migrated DB the two
    # columns land at the END, in a different position than on a fresh DB. The census
    # above is therefore only true of a DB created from scratch — `SELECT *` column
    # ORDER depends on the file's history. (Every read in this module goes through
    # sqlite3.Row/dict, so ordering does not bite today; positional access would.)
    assert names[-2:] == ["commodity_amount_gbp", "non_commodity_amount_gbp"]
    assert names[:2] == ["invoice_number", "account_id"]
    # SURPRISE (money class): the migrated row now reports £0.00 of energy charge
    # against a £100.00 subtotal — the DEFAULT backfills zero rather than the
    # pre-split amount, so every legacy invoice silently claims its entire value was
    # neither commodity, non-commodity, nor standing charge.
    assert row["subtotal_gbp"] == 100.0
    assert row["commodity_amount_gbp"] == 0.0
    assert row["non_commodity_amount_gbp"] == 0.0
    assert issued_debits_gbp("A1", db_path=db) == 105.0  # the total still reconciles


def test_create_schema_raises_on_a_foreign_invoices_table(db):
    """CREATE TABLE IF NOT EXISTS is a silent no-op against an unrelated table of the
    same name, so the failure surfaces later, from CREATE INDEX."""
    with raw(db) as conn:
        conn.execute("CREATE TABLE invoices (junk TEXT)")
        conn.commit()
    with pytest.raises(sqlite3.OperationalError, match="no such column: account_id"):
        create_schema(db)


# ---------------------------------------------------------------------------
# create_invoice(): derived fields
# ---------------------------------------------------------------------------


def test_create_invoice_derives_issue_and_due_dates_from_period_end(db):
    inv = get_invoice(create_invoice(bill(period_end="2024-01-31"), db), db)
    assert inv["issue_date"] == "2024-01-31"      # issue date IS the period end
    assert inv["due_date"] == "2024-02-14"        # + 14 days
    assert inv["payment_status"] == "unpaid"
    assert inv["commodity"] == "electricity"
    # SURPRISE (temporal class): the invoice is dated the last day of the period it
    # bills, so it is modelled as issued the instant the period closes — there is no
    # billing run lag at all, and no column records when it was actually produced.


def test_create_invoice_falls_back_to_period_start_when_period_end_is_absent(db):
    inv = get_invoice(create_invoice(
        {"customer_id": "A1", "period_start": "2024-03-05",
         "total_amount_gbp": 10.0, "total_consumption_kwh": 100.0}, db), db)
    # billing_period_end is backfilled from period_start: a zero-length period.
    assert inv["billing_period_start"] == "2024-03-05"
    assert inv["billing_period_end"] == "2024-03-05"
    assert inv["issue_date"] == "2024-03-05"
    assert inv["due_date"] == "2024-03-19"


def test_create_invoice_accepts_a_bill_with_no_dates_at_all(db):
    """SURPRISE (fail-open class, R15): a bill carrying neither period_start nor
    period_end is accepted and stored with EMPTY-STRING dates. The NOT NULL
    constraints pass ('' is not NULL), so an undated invoice is a first-class row.
    See test_as_of_never_excludes_an_undated_invoice for what that does to the
    point-in-time control total."""
    inv = get_invoice(create_invoice({"customer_id": "A1"}, db), db)
    assert inv["issue_date"] == "" and inv["due_date"] == ""
    assert inv["billing_period_start"] == "" and inv["billing_period_end"] == ""
    assert inv["consumption_kwh"] == 0.0 and inv["total_gbp"] == 0.0


def test_create_invoice_requires_customer_id_and_nothing_else(db):
    """customer_id is the ONLY mandatory key — everything else has a .get default."""
    with pytest.raises(KeyError, match="customer_id"):
        create_invoice({"period_end": "2024-01-31"}, db)


def test_create_invoice_raises_on_a_non_iso_period_end(db):
    with pytest.raises(ValueError, match="Invalid isoformat string"):
        create_invoice(bill(period_end="31/01/2024"), db)


def test_invoice_numbers_are_sequential_and_never_reused(db):
    assert create_invoice(bill(), db) == 1
    assert create_invoice(bill(), db) == 2
    with raw(db) as conn:
        conn.execute("DELETE FROM invoices")
        conn.commit()
    # AUTOINCREMENT (not bare INTEGER PRIMARY KEY): the counter survives deletion, so
    # a purged register cannot silently re-mint an already-issued invoice number.
    assert create_invoice(bill(), db) == 3


def test_commodity_is_carried_through_from_the_bill(db):
    inv = get_invoice(create_invoice(bill(commodity="gas"), db), db)
    assert inv["commodity"] == "gas"


# ---------------------------------------------------------------------------
# create_invoice(): the two VAT branches
# ---------------------------------------------------------------------------


def test_legacy_bill_treats_the_whole_total_as_pre_tax_commodity(db):
    """A bill with no line items: total_amount_gbp is taken as the pre-tax subtotal
    and VAT is ADDED on top, so the stored total EXCEEDS the bill's own total."""
    inv = get_invoice(create_invoice(bill(total_amount_gbp=100.0), db), db)
    assert inv["subtotal_gbp"] == 100.0
    assert inv["vat_gbp"] == 5.0
    assert inv["total_gbp"] == 105.0
    # The entire amount is booked as commodity — no standing charge, no levies.
    assert inv["commodity_amount_gbp"] == 100.0
    assert inv["non_commodity_amount_gbp"] == 0.0
    assert inv["standing_charge_gbp"] == 0.0


def test_line_item_bill_sums_the_three_components_and_trusts_the_bills_vat(db):
    inv = get_invoice(create_invoice(rich_bill(), db), db)
    assert inv["subtotal_gbp"] == 153.0  # 120 + 25 + 8
    assert inv["vat_gbp"] == 7.65        # taken from the bill, not recomputed
    assert inv["total_gbp"] == 160.65


def test_a_bills_declared_vat_is_never_sanity_checked(db):
    """SURPRISE (fail-open class, R15): `bill.get("vat_gbp", subtotal * VAT_RATE)`
    accepts whatever the bill says. A £999 VAT charge on a £100 subtotal (999%) is
    stored and flows straight into the issued-debits control total. The 5% rate is a
    fallback, never a validation."""
    inv = get_invoice(create_invoice(bill(commodity_amount_gbp=100.0, vat_gbp=999.0), db), db)
    assert inv["vat_gbp"] == 999.0
    assert inv["total_gbp"] == 1099.0
    assert issued_debits_gbp("A1", db_path=db) == 1099.0


def test_line_item_bill_without_a_vat_key_falls_back_to_five_percent(db):
    b = bill(commodity_amount_gbp=100.0, non_commodity_amount_gbp=0.0, standing_charge_gbp=0.0)
    b.pop("vat_gbp", None)
    inv = get_invoice(create_invoice(b, db), db)
    assert inv["vat_gbp"] == 5.0 and inv["total_gbp"] == 105.0


def test_all_zero_line_items_fall_through_to_the_legacy_branch(db):
    """SURPRISE (boundary class): the branch is chosen by TRUTHINESS
    (`if commodity_gbp or non_comm_gbp or sc_gbp`), not by key presence. A genuine
    line-item bill that happens to total zero on all three components is treated as a
    legacy bill instead — its total_amount_gbp is re-read as a pre-tax subtotal and
    VAT is charged on it a second time. Here a £100 bill whose line items are all
    £0.00 becomes a £105.00 invoice with £100.00 of 'commodity'."""
    inv = get_invoice(create_invoice(bill(
        commodity_amount_gbp=0.0, non_commodity_amount_gbp=0.0,
        standing_charge_gbp=0.0, vat_gbp=0.0, total_amount_gbp=100.0), db), db)
    assert inv["commodity_amount_gbp"] == 100.0
    assert inv["vat_gbp"] == 5.0
    assert inv["total_gbp"] == 105.0


def test_vat_gbp_of_none_raises_a_type_error_from_round(db):
    """SURPRISE (defensiveness class): an explicit `vat_gbp: None` — a plausible
    shape for 'VAT not yet computed' — reaches round() and dies with a TypeError
    naming __round__, not a billing-level error message."""
    with pytest.raises(TypeError, match="__round__"):
        create_invoice(bill(commodity_amount_gbp=100.0, vat_gbp=None), db)


def test_negative_bill_produces_a_negative_invoice_with_negative_vat(db):
    """SURPRISE (sign class): a credit note is representable only as a negative
    invoice. Nothing rejects it, VAT is reclaimed at -5%, and it reduces the
    issued-debits control total — a refund and an un-issued bill are indistinguishable
    in the register."""
    inv = get_invoice(create_invoice(bill(total_amount_gbp=-50.0), db), db)
    assert inv["subtotal_gbp"] == -50.0
    assert inv["vat_gbp"] == -2.5
    assert inv["total_gbp"] == -52.5
    assert issued_debits_gbp("A1", db_path=db) == -52.5


# ---------------------------------------------------------------------------
# create_invoice(): unit rate derivation
# ---------------------------------------------------------------------------


def test_unit_rate_is_derived_from_the_bills_total_not_its_energy_charge(db):
    """SURPRISE (unit class, money-relevant): `_unit_rate_from_bill` divides
    total_amount_gbp by kWh. On a line-item bill that total is VAT-INCLUSIVE and also
    carries standing charge and levies, so the stored 'unit rate' is neither the tariff
    unit rate nor a pre-tax figure: £105 incl. VAT over 1000 kWh prints as 10.5000
    p/kWh when the energy charge is 10.0000 p/kWh."""
    inv = get_invoice(create_invoice(bill(
        commodity_amount_gbp=100.0, vat_gbp=5.0,
        total_amount_gbp=105.0, total_consumption_kwh=1000.0), db), db)
    assert inv["unit_rate_p_per_kwh"] == 10.5
    assert inv["commodity_amount_gbp"] == 100.0  # i.e. 10.0 p/kWh of actual energy


def test_unit_rate_is_rounded_to_four_decimal_places(db):
    inv = get_invoice(create_invoice(bill(
        total_amount_gbp=100.005, total_consumption_kwh=1000.0), db), db)
    assert inv["unit_rate_p_per_kwh"] == 10.0005


@pytest.mark.parametrize("kwh", [0.0, -5.0])
def test_zero_or_negative_consumption_yields_a_zero_unit_rate(db, kwh):
    """The guard is `if kwh > 0`, so negative consumption (a corrected read) silently
    reports a 0.0000 p/kWh rate rather than a negative one or an error."""
    inv = get_invoice(create_invoice(bill(total_consumption_kwh=kwh), db), db)
    assert inv["unit_rate_p_per_kwh"] == 0.0
    assert inv["consumption_kwh"] == kwh  # but the consumption itself is stored as-is


# ---------------------------------------------------------------------------
# Rounding coherence — REAL money and a double-rounding path
# ---------------------------------------------------------------------------


def test_stored_line_items_do_not_always_sum_to_the_stored_total(db):
    """SURPRISE (money class, arithmetic): in the legacy branch `subtotal` is NOT
    rounded before use — the total is computed from the raw value and only the
    COLUMN is rounded at INSERT time. For a £0.125 bill the register stores
    subtotal 0.12 + VAT 0.01 = 0.13, but total_gbp 0.14. A penny exists in the total
    that exists in no line item, and a bill rendered from these columns does not add
    up."""
    inv = get_invoice(create_invoice(bill(total_amount_gbp=0.125), db), db)
    assert (inv["subtotal_gbp"], inv["vat_gbp"], inv["total_gbp"]) == (0.12, 0.01, 0.14)
    assert inv["subtotal_gbp"] + inv["vat_gbp"] != inv["total_gbp"]


def test_sub_penny_bills_round_away_to_a_zero_value_invoice(db):
    """A £0.001 bill is stored as a £0.00 invoice — but it is still a row, still
    counted, and still carries a due date."""
    inv = get_invoice(create_invoice(bill(total_amount_gbp=0.001), db), db)
    assert inv["subtotal_gbp"] == 0.0 and inv["total_gbp"] == 0.0
    assert invoice_summary(db)["total_count"] == 1


def test_aggregate_sums_already_rounded_per_invoice_totals_so_error_accumulates(db):
    """SURPRISE (money class, aggregation): issued_debits_gbp is a SUM OF ROUNDINGS,
    not a rounded sum — it adds the already-rounded total_gbp column, so the
    half-penny each invoice gains from the double-rounding above compounds instead of
    cancelling. Three £0.125 bills are each stored as £0.14, giving a control total of
    £0.42, where the correct VAT-inclusive value of the same three bills is
    3 x 0.13125 = £0.39. The independent debit control the ledger reconciles against
    is 3p adrift on three invoices, and the drift grows with the register."""
    for _ in range(3):
        create_invoice(bill(total_amount_gbp=0.125), db)
    stored = [inv["total_gbp"] for inv in invoices_for_account("A1", db)]
    assert stored == [0.14, 0.14, 0.14]
    assert issued_debits_gbp("A1", db_path=db) == 0.42
    assert round(3 * 0.125 * (1 + VAT_RATE), 2) == 0.39  # what it should be


# ---------------------------------------------------------------------------
# Idempotency / double-issue on replay — what ACTUALLY happens
# ---------------------------------------------------------------------------


def test_issuing_the_same_bill_twice_creates_two_invoices(db):
    """SURPRISE (idempotency class, C-S2, money-relevant): create_invoice has NO
    idempotency key of any kind — no bill id, no (account, period) uniqueness, no
    check for an existing invoice over the same period. Replaying an identical bill
    dict mints a second invoice number and DOUBLES the account's debit. Because
    issued_debits_gbp is the INDEPENDENT control total the account ledger reconciles
    against, a replayed billing run does not fail the control — it moves the control
    away from the ledger and the ledger is then reported as wrong."""
    b = bill()
    first, second = create_invoice(b, db), create_invoice(b, db)
    assert (first, second) == (1, 2)
    rows = invoices_for_account("A1", db)
    assert len(rows) == 2
    assert rows[0]["billing_period_start"] == rows[1]["billing_period_start"]
    assert issued_debits_gbp("A1", db_path=db) == 210.0  # not 105.0


def test_bulk_create_invoices_replays_just_as_freely(db):
    """The bulk path is a plain loop over create_invoice, so it inherits the same
    non-idempotency AND re-runs create_schema once per bill on top of its own call."""
    b = bill()
    assert bulk_create_invoices([b, b], db) == 2
    assert bulk_create_invoices([b, b], db) == 2
    assert len(invoices_for_account("A1", db)) == 4
    assert issued_debits_gbp("A1", db_path=db) == 420.0


def test_bulk_create_invoices_on_an_empty_list_creates_the_schema_and_returns_zero(db):
    assert bulk_create_invoices([], db) == 0
    with raw(db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM invoices").fetchone()[0] == 0


def test_the_bill_dict_is_not_mutated_by_invoicing(db):
    b = bill()
    snapshot = dict(b)
    create_invoice(b, db)
    assert b == snapshot


# ---------------------------------------------------------------------------
# Reads: empty DB, missing account, missing schema
# ---------------------------------------------------------------------------


def test_readers_that_create_the_schema_return_empty_on_a_virgin_db(db):
    """issued_debits_gbp / cash_received_gbp both call their create_*_schema first,
    so they answer 0.0 on a database that did not exist a moment ago."""
    assert issued_debits_gbp("A1", db_path=db) == 0.0
    assert cash_received_gbp("A1", db_path=db) == 0.0
    assert db.exists()


def test_get_invoice_returns_none_for_an_unknown_number(db):
    create_invoice(bill(), db)
    assert get_invoice(9999, db) is None


def test_issued_debits_returns_zero_for_an_account_that_has_never_been_billed(db):
    create_invoice(bill(customer_id="A1"), db)
    assert issued_debits_gbp("NO-SUCH-ACCOUNT", db_path=db) == 0.0
    # COALESCE makes "no such account" and "billed exactly nothing" indistinguishable.
    assert issued_debits_gbp("A1", as_of="1999-01-01", db_path=db) == 0.0


@pytest.mark.parametrize(
    "call",
    [
        pytest.param(lambda p: invoices_for_account("A1", p), id="invoices_for_account"),
        pytest.param(lambda p: invoice_summary(p), id="invoice_summary"),
        pytest.param(lambda p: update_payment_status(1, "paid", p), id="update_payment_status"),
    ],
)
def test_three_functions_omit_create_schema_and_raise_on_a_virgin_db(tmp_path, call):
    """SURPRISE (consistency class): create_invoice, get_invoice, issued_debits_gbp
    and bulk_create_invoices all call create_schema defensively; these three do not,
    and fail with a raw sqlite3 error. Worse, _conn has ALREADY run
    `db_path.parent.mkdir(parents=True)` and connected by then — so the failing call
    still leaves an empty database file (and, on the default path, a freshly created
    `company/data/` directory) behind."""
    db_path = tmp_path / "virgin.db"
    with pytest.raises(sqlite3.OperationalError, match="no such table: invoices"):
        call(db_path)
    assert db_path.exists()  # the side effect happened anyway


def test_invoice_summary_returns_none_not_zero_on_an_empty_register(db):
    """SURPRISE (fail-open class, R15): SUM() over zero rows is NULL, and the summary
    passes it straight out. Every money field is None rather than 0.0, so any consumer
    doing arithmetic on a fresh register gets a TypeError instead of £0.00 — and any
    consumer doing `or 0` silently cannot distinguish empty from genuinely zero."""
    create_schema(db)
    summary = invoice_summary(db)
    assert summary == {
        "total_count": 0,
        "total_billed_gbp": None,
        "paid_gbp": None,
        "outstanding_gbp": None,
        "bad_debt_gbp": None,
    }


def test_invoices_for_account_orders_lexically_by_period_start(db):
    create_invoice(bill(period_start="2024-03-01", period_end="2024-03-31"), db)
    create_invoice(bill(period_start="2024-01-01", period_end="2024-01-31"), db)
    create_invoice({"customer_id": "A1"}, db)  # the undated invoice
    ordered = [(r["invoice_number"], r["billing_period_start"])
               for r in invoices_for_account("A1", db)]
    # The undated invoice sorts FIRST — '' precedes every date string lexically.
    assert ordered == [(3, ""), (2, "2024-01-01"), (1, "2024-03-01")]


def test_invoices_for_account_is_scoped_to_the_account(db):
    create_invoice(bill(customer_id="A1"), db)
    create_invoice(bill(customer_id="A2"), db)
    assert [r["account_id"] for r in invoices_for_account("A1", db)] == ["A1"]


# ---------------------------------------------------------------------------
# update_payment_status() and invoice_summary()
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("status", ["unpaid", "paid", "partially_paid", "bad_debt"])
def test_valid_payment_statuses(db, status):
    number = create_invoice(bill(), db)
    update_payment_status(number, status, db)
    assert get_invoice(number, db)["payment_status"] == status


@pytest.mark.parametrize("status", ["overdue", "PAID", "", "Paid"])
def test_invalid_payment_statuses_are_rejected_case_sensitively(db, status):
    create_invoice(bill(), db)
    with pytest.raises(ValueError, match="Invalid payment status"):
        update_payment_status(1, status, db)


def test_updating_a_nonexistent_invoice_is_a_silent_no_op(db):
    """SURPRISE (fail-silent class, R15): the UPDATE matches zero rows and the
    function returns None. Marking a typo'd invoice number as paid looks identical to
    marking a real one as paid — rowcount is never inspected."""
    create_invoice(bill(), db)
    assert update_payment_status(9999, "paid", db) is None
    assert get_invoice(1, db)["payment_status"] == "unpaid"


def test_invoice_summary_buckets_by_status(db):
    a = create_invoice(bill(total_amount_gbp=100.0), db)   # 105.00
    create_invoice(bill(total_amount_gbp=200.0), db)       # 210.00
    c = create_invoice(bill(total_amount_gbp=300.0), db)   # 315.00
    update_payment_status(a, "paid", db)
    update_payment_status(c, "bad_debt", db)
    assert invoice_summary(db) == {
        "total_count": 3,
        "total_billed_gbp": 630.0,
        "paid_gbp": 105.0,
        "outstanding_gbp": 210.0,
        "bad_debt_gbp": 315.0,
    }


def test_partially_paid_invoices_fall_out_of_every_summary_bucket(db):
    """SURPRISE (completeness class, money-relevant): the summary's CASE arms cover
    only paid / unpaid / bad_debt. A `partially_paid` invoice — a status the module
    itself declares valid — is counted in total_billed_gbp and in NO bucket, so
    paid + outstanding + bad_debt silently stops equalling total billed. £105 of
    receivable disappears from the outstanding view without appearing anywhere else."""
    number = create_invoice(bill(total_amount_gbp=100.0), db)
    update_payment_status(number, "partially_paid", db)
    summary = invoice_summary(db)
    assert summary["total_billed_gbp"] == 105.0
    assert (summary["paid_gbp"], summary["outstanding_gbp"], summary["bad_debt_gbp"]) == (0, 0, 0)
    assert summary["paid_gbp"] + summary["outstanding_gbp"] + summary["bad_debt_gbp"] != 105.0


# ---------------------------------------------------------------------------
# issued_debits_gbp(): the independent debit control total and its as_of bound
# ---------------------------------------------------------------------------


@pytest.fixture
def two_invoice_db(db) -> Path:
    """£105.00 issued 2024-01-31 and £210.00 issued 2024-02-29 — £315.00 total."""
    create_invoice(bill(period_end="2024-01-31", total_amount_gbp=100.0), db)
    create_invoice(bill(period_start="2024-02-01", period_end="2024-02-29",
                        total_amount_gbp=200.0), db)
    return db


def test_issued_debits_is_the_gross_vat_inclusive_total(two_invoice_db):
    assert issued_debits_gbp("A1", db_path=two_invoice_db) == 315.0
    # It sums total_gbp, i.e. VAT-inclusive — NOT subtotal_gbp.
    assert sum(r["subtotal_gbp"] for r in invoices_for_account("A1", two_invoice_db)) == 300.0


@pytest.mark.parametrize(
    "as_of, expected",
    [
        (dt.date(2024, 1, 30), 0.0),
        (dt.date(2024, 1, 31), 105.0),   # the issue day itself counts (<= is inclusive)
        (dt.date(2024, 2, 1), 105.0),
        (dt.date(2024, 2, 29), 315.0),
        (dt.date(2024, 3, 1), 315.0),
        (None, 315.0),
    ],
)
def test_as_of_date_boundaries_are_inclusive_of_the_issue_day(two_invoice_db, as_of, expected):
    assert issued_debits_gbp("A1", as_of=as_of, db_path=two_invoice_db) == expected


@pytest.mark.parametrize(
    "as_of, expected",
    [
        (dt.datetime(2024, 1, 31, 0, 0, 0), 105.0),
        (dt.datetime(2024, 1, 31, 23, 59, 59), 105.0),
        (dt.datetime(2024, 1, 30, 23, 59, 59), 0.0),
    ],
)
def test_a_datetime_as_of_is_truncated_to_its_date(two_invoice_db, as_of, expected):
    """`_as_of_iso` slices `[:10]`, so the time of day is discarded entirely: an
    instant one second into the issue day and an instant one second before midnight
    on it are the same bound. Sub-day point-in-time queries are not representable."""
    assert issued_debits_gbp("A1", as_of=as_of, db_path=two_invoice_db) == expected


def test_a_string_as_of_is_passed_through_untruncated_and_compared_lexically(two_invoice_db):
    """SURPRISE (type-asymmetry class): a str bypasses the `[:10]` truncation a
    date/datetime gets and is compared LEXICALLY against the ISO date column. It
    happens to give the right answer for well-formed ISO timestamps only because
    '2024-01-31' < '2024-01-31T00:00:00' as text."""
    assert issued_debits_gbp("A1", as_of="2024-01-31", db_path=two_invoice_db) == 105.0
    assert issued_debits_gbp("A1", as_of="2024-01-31T00:00:00", db_path=two_invoice_db) == 105.0
    assert issued_debits_gbp("A1", as_of="2024-01-30T23:59:59", db_path=two_invoice_db) == 0.0


@pytest.mark.parametrize("junk, expected", [("not-a-date", 315.0), ("9999", 315.0), ("", 0.0)])
def test_a_malformed_string_as_of_is_never_validated(two_invoice_db, junk, expected):
    """SURPRISE (fail-open class, R15, point-in-time relevant): a str as_of is never
    parsed — `_as_of_iso` returns it unchanged and SQLite compares it as text. A
    typo'd or non-date bound therefore does not raise: 'not-a-date' and '9999' sort
    ABOVE every ISO date, so the bound silently admits EVERY invoice (the answer a
    caller asking for a point-in-time total least wants), while '' silently excludes
    every one. A control that cannot fail on a bad bound is not a control."""
    assert issued_debits_gbp("A1", as_of=junk, db_path=two_invoice_db) == expected


@pytest.mark.parametrize("as_of", [0.0, 20240131, ["2024-01-31"]])
def test_an_as_of_with_no_isoformat_method_raises_type_error(two_invoice_db, as_of):
    """The one input class that IS rejected: anything without .isoformat and not a
    str. Note this makes an int bound louder than a nonsense string bound."""
    with pytest.raises(TypeError, match="unsupported as_of type"):
        issued_debits_gbp("A1", as_of=as_of, db_path=two_invoice_db)


def test_as_of_never_excludes_an_undated_invoice(db):
    """SURPRISE (fail-open class, temporal): an invoice stored with issue_date '' (see
    test_create_invoice_accepts_a_bill_with_no_dates_at_all) satisfies
    `issue_date <= ?` for EVERY bound, because '' precedes every date lexically. It is
    therefore included in a control total as of 1999 — before the company existed."""
    create_invoice({"customer_id": "A1", "total_amount_gbp": 100.0,
                    "total_consumption_kwh": 1.0}, db)
    assert issued_debits_gbp("A1", as_of="1999-01-01", db_path=db) == 105.0
    assert issued_debits_gbp("A1", as_of=dt.date(1999, 1, 1), db_path=db) == 105.0


def test_issued_debits_rounds_the_aggregate_to_pence(db):
    create_invoice(bill(commodity_amount_gbp=10.001, vat_gbp=0.0), db)
    create_invoice(bill(commodity_amount_gbp=10.004, vat_gbp=0.0), db)
    assert issued_debits_gbp("A1", db_path=db) == 20.0


# ---------------------------------------------------------------------------
# record_payment() / cash_received_gbp(): the independent credit control total
# ---------------------------------------------------------------------------


def test_record_payment_stores_the_cash_book_row(db):
    pid = record_payment("A1", 50.0, "2024-02-01", invoice_number=7, payment_ref="REF-1",
                         recorded_at="2024-02-02", db_path=db)
    with raw(db) as conn:
        row = dict(conn.execute("SELECT * FROM payments WHERE payment_id = ?", (pid,)).fetchone())
    assert row == {
        "payment_id": 1, "payment_ref": "REF-1", "account_id": "A1",
        "invoice_number": 7, "amount_gbp": 50.0,
        "value_date": "2024-02-01", "recorded_at": "2024-02-02",
    }
    assert cash_received_gbp("A1", db_path=db) == 50.0


@pytest.mark.parametrize("amount", [0.0, -1.0, -0.001])
def test_non_positive_payments_are_rejected(db, amount):
    with pytest.raises(ValueError, match="payment amount must be positive"):
        record_payment("A1", amount, "2024-02-01", db_path=db)


def test_record_payment_is_idempotent_on_payment_ref(db):
    first = record_payment("A1", 50.0, "2024-02-01", payment_ref="REF-1",
                           recorded_at="2024-02-01", db_path=db)
    replay = record_payment("A1", 50.0, "2024-02-01", payment_ref="REF-1",
                            recorded_at="2024-02-01", db_path=db)
    assert first == replay == 1
    assert cash_received_gbp("A1", db_path=db) == 50.0


def test_a_replayed_ref_with_a_different_amount_silently_keeps_the_first(db):
    """SURPRISE (idempotency class, money-relevant): the dedup is on payment_ref
    ALONE — the incoming amount is never compared to the stored one. A corrected
    remittance re-sent under the same reference is discarded and the ORIGINAL
    payment_id is returned, so the caller sees success while £950 of cash never
    enters the credit control total."""
    record_payment("A1", 50.0, "2024-02-01", payment_ref="REF-1",
                   recorded_at="2024-02-01", db_path=db)
    assert record_payment("A1", 1000.0, "2024-02-01", payment_ref="REF-1",
                          recorded_at="2024-02-01", db_path=db) == 1
    assert cash_received_gbp("A1", db_path=db) == 50.0


def test_a_ref_collision_across_accounts_drops_the_second_accounts_cash(db):
    """SURPRISE (scoping class, money-relevant, worst in this file): the duplicate
    lookup is `WHERE payment_ref = ?` with NO account filter, and payment_ref is
    UNIQUE table-wide. A reference reused by a DIFFERENT account is treated as a
    replay of the first account's payment: B2's £900 is never recorded, and the
    function cheerfully returns A1's payment_id. B2's cash control total then reads
    £0.00 and the ledger reconciliation blames the ledger."""
    a1 = record_payment("A1", 50.0, "2024-02-01", payment_ref="SHARED",
                        recorded_at="2024-02-01", db_path=db)
    b2 = record_payment("B2", 900.0, "2024-02-01", payment_ref="SHARED",
                        recorded_at="2024-02-01", db_path=db)
    assert b2 == a1 == 1
    assert cash_received_gbp("A1", db_path=db) == 50.0
    assert cash_received_gbp("B2", db_path=db) == 0.0


def test_payments_without_a_ref_are_not_deduplicated_at_all(db):
    """SQLite permits unlimited NULLs under a UNIQUE column, so a ref-less payment has
    no idempotency: the identical remittance replays into a second row and doubles the
    credit control total."""
    first = record_payment("A1", 10.0, "2024-03-01", recorded_at="2024-03-01", db_path=db)
    second = record_payment("A1", 10.0, "2024-03-01", recorded_at="2024-03-01", db_path=db)
    assert (first, second) == (1, 2)
    assert cash_received_gbp("A1", db_path=db) == 20.0


def test_payment_amount_is_rounded_to_pence_on_insert(db):
    record_payment("A1", 10.005, "2024-03-01", recorded_at="2024-03-01", db_path=db)
    assert cash_received_gbp("A1", db_path=db) == 10.01


def test_a_payment_may_reference_an_invoice_that_does_not_exist(db):
    """No foreign key, and no lookup: the cash book will happily point at invoice
    99999 in a database whose invoices table has not even been created."""
    pid = record_payment("A1", 1.0, "2024-04-01", invoice_number=99999,
                         recorded_at="2024-04-01", db_path=db)
    with raw(db) as conn:
        assert conn.execute(
            "SELECT invoice_number FROM payments WHERE payment_id = ?", (pid,)
        ).fetchone()[0] == 99999
        assert conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE name='invoices'").fetchone()[0] == 0


def test_recorded_at_defaults_to_the_wall_clock(db):
    """SURPRISE (determinism class, C-S2): `recorded_at or date.today().isoformat()`
    is the module's only wall-clock read. The transaction-time leg of this bitemporal
    row is therefore the machine's local date at insert, not a value derived from the
    simulated clock — so a replay of the same events records different transaction
    times, and a backfill of historical cash is stamped today. Bracketed rather than
    pinned here so the test cannot flake across midnight."""
    before = dt.date.today().isoformat()
    pid = record_payment("A1", 1.0, "2024-05-01", db_path=db)
    after = dt.date.today().isoformat()
    with raw(db) as conn:
        stored = conn.execute(
            "SELECT recorded_at FROM payments WHERE payment_id = ?", (pid,)).fetchone()[0]
    assert stored in (before, after)
    # value_date (the valid-time leg) is caller-supplied and is NOT touched.
    with raw(db) as conn:
        assert conn.execute(
            "SELECT value_date FROM payments WHERE payment_id = ?", (pid,)
        ).fetchone()[0] == "2024-05-01"


@pytest.mark.parametrize(
    "as_of, expected",
    [
        (None, 70.0),
        (dt.date(2024, 1, 31), 0.0),
        (dt.date(2024, 2, 1), 50.0),   # value_date boundary is inclusive
        (dt.date(2024, 3, 1), 70.0),
        ("2024-02-01", 50.0),
        ("not-a-date", 70.0),          # same fail-open as issued_debits_gbp
        ("", 0.0),
    ],
)
def test_cash_received_as_of_mirrors_the_debit_side_including_its_fail_open(db, as_of, expected):
    record_payment("A1", 50.0, "2024-02-01", recorded_at="2024-02-01", db_path=db)
    record_payment("A1", 20.0, "2024-03-01", recorded_at="2024-03-01", db_path=db)
    assert cash_received_gbp("A1", as_of=as_of, db_path=db) == expected


def test_cash_received_bounds_on_value_date_not_recorded_at(db):
    """The as_of bound is the VALID time (when the cash arrived), never the
    transaction time — a payment backdated into an already-reported period moves a
    historical control total. Frozen, not endorsed."""
    record_payment("A1", 50.0, "2024-01-05", recorded_at="2024-06-30", db_path=db)
    assert cash_received_gbp("A1", as_of="2024-01-31", db_path=db) == 50.0
    assert cash_received_gbp("A1", as_of="2024-06-01", db_path=db) == 50.0


def test_cash_received_is_zero_for_an_unknown_account(db):
    record_payment("A1", 50.0, "2024-02-01", recorded_at="2024-02-01", db_path=db)
    assert cash_received_gbp("NOBODY", db_path=db) == 0.0


# ---------------------------------------------------------------------------
# InvoiceControlSource — the adapter the ledger reconciles against
# ---------------------------------------------------------------------------


def test_control_source_binds_a_db_path_and_delegates_both_accessors(db):
    create_invoice(bill(total_amount_gbp=100.0), db)
    record_payment("A1", 30.0, "2024-02-01", recorded_at="2024-02-01", db_path=db)
    source = InvoiceControlSource(db)
    assert source.db_path == db
    assert source.issued_debits_gbp("A1") == 105.0
    assert source.cash_received_gbp("A1") == 30.0
    assert source.issued_debits_gbp("A1", as_of=dt.date(2024, 1, 30)) == 0.0
    assert source.cash_received_gbp("A1", as_of=dt.date(2024, 1, 30)) == 0.0


def test_control_source_answers_zero_rather_than_failing_on_an_empty_store(db):
    """SURPRISE (fail-open class, R15, control-relevant): the ledger's
    verify_against_invoicing() fails CLOSED when the source cannot answer — but this
    source always answers. Pointed at a database that has never been written (a wrong
    path, a wiped file, a fresh container), it CREATES the empty schema and returns
    0.00 for both legs. "I have no records" is indistinguishable from "nothing was
    ever billed", and a ledger carrying real bills then reconciles against zero."""
    source = InvoiceControlSource(db)
    assert not db.exists()
    assert source.issued_debits_gbp("A1") == 0.0
    assert source.cash_received_gbp("A1") == 0.0
    assert db.exists()


def test_control_source_default_constructor_binds_the_default_path_without_touching_it():
    """Constructing the adapter is pure — it only stores the path. No connection is
    opened until an accessor is called, which is why this assertion is safe under the
    tmp-path-only rule.

    Purity is asserted as "the real DB is byte-for-byte untouched by constructing
    the adapter", not "company/data does not exist" — that directory is gitignored
    runtime state and legitimately exists on the live machine (2026-08-08)."""
    before = _default_db_fingerprint()
    assert InvoiceControlSource().db_path == DEFAULT_DB_PATH
    assert _default_db_fingerprint() == before


def test_two_control_sources_on_two_paths_are_fully_isolated(db, db2):
    create_invoice(bill(customer_id="A1", total_amount_gbp=100.0), db)
    create_invoice(bill(customer_id="A1", total_amount_gbp=999.0), db2)
    assert InvoiceControlSource(db).issued_debits_gbp("A1") == 105.0
    assert InvoiceControlSource(db2).issued_debits_gbp("A1") == 1048.95


# ---------------------------------------------------------------------------
# format_invoice_text()
# ---------------------------------------------------------------------------


STORED_INVOICE = {
    "invoice_number": 42, "account_id": "A1", "commodity": "electricity",
    "issue_date": "2024-01-31", "due_date": "2024-02-14",
    "billing_period_start": "2024-01-01", "billing_period_end": "2024-01-31",
    "consumption_kwh": 1500.0, "unit_rate_p_per_kwh": 12.5,
    "commodity_amount_gbp": 187.50, "non_commodity_amount_gbp": 25.30,
    "standing_charge_gbp": 8.60, "subtotal_gbp": 221.40,
    "vat_gbp": 11.07, "total_gbp": 232.47, "payment_status": "unpaid",
}


def test_format_invoice_text_renders_the_full_document():
    text = format_invoice_text(STORED_INVOICE)
    assert text.splitlines()[:3] == ["INVOICE", "=======", "Invoice No: 42"]
    assert "Commodity:      Electricity" in text
    assert "Consumption:            1,500.00 kWh" in text
    assert "Unit Rate:               12.5000 p/kWh" in text
    assert "Energy Charge:            187.50" in text
    assert "Standing Charge:            8.60" in text
    assert "Network & Levies:          25.30" in text
    assert "TOTAL DUE                   232.47" in text
    assert "Payment Status: UNPAID" in text
    # SURPRISE (presentation class): no currency symbol appears anywhere in the
    # rendered document — the amounts are bare numbers on a page headed only
    # "INVOICE". Nothing states the amounts are GBP, and nothing carries the
    # R14 clock (settled / billed / banked) either.
    assert "£" not in text and "GBP" not in text


def test_format_invoice_text_hides_zero_line_items_but_not_a_zero_energy_charge():
    """Standing charge and levies are suppressed when zero; the energy charge line is
    printed unconditionally, so a £0.00 energy charge is still shown."""
    zeroed = dict(STORED_INVOICE, standing_charge_gbp=0.0,
                  non_commodity_amount_gbp=0.0, commodity_amount_gbp=0.0)
    text = format_invoice_text(zeroed)
    assert "Standing Charge" not in text
    assert "Network & Levies" not in text
    assert "Energy Charge:              0.00" in text


def test_format_invoice_text_renders_an_empty_dict_as_a_blank_but_valid_invoice():
    """SURPRISE (fail-open class, R15): every field is a `.get` with a benign default,
    so a completely empty dict renders a well-formed £0.00 invoice with no number, no
    dates and no account — a document that looks issued and is entirely hollow. There
    is no 'this is not an invoice' path."""
    text = format_invoice_text({})
    assert text.startswith("INVOICE\n=======\nInvoice No: \n")
    assert "TOTAL DUE                     0.00" in text
    assert "Payment Status: UNPAID" in text


def test_format_invoice_text_raises_when_commodity_is_explicitly_none():
    """The `.get("commodity", "electricity")` default only fires on a MISSING key; a
    stored NULL reaches .capitalize() and dies. Every other field tolerates None only
    because it is never method-called."""
    with pytest.raises(AttributeError, match="capitalize"):
        format_invoice_text(dict(STORED_INVOICE, commodity=None))


def test_format_invoice_text_round_trips_a_real_stored_row(db):
    number = create_invoice(rich_bill(), db)
    text = format_invoice_text(get_invoice(number, db))
    assert "Invoice No: 1" in text
    assert "Issue Date: 2024-01-31" in text
    assert "Due Date:   2024-02-14" in text
    assert "TOTAL DUE                   160.65" in text


# ---------------------------------------------------------------------------
# Two-connection behaviour (no threads — see the concurrency gap note below)
# ---------------------------------------------------------------------------


def test_the_module_holds_no_connection_between_calls(db):
    """_conn opens, commits and CLOSES per call, so nothing is held open across calls:
    a second connection with a zero busy-timeout can write the instant a module call
    returns. Committed-per-call is also why every read below sees prior writes."""
    create_invoice(bill(), db)
    other = sqlite3.connect(str(db), timeout=0)
    other.execute(
        "INSERT INTO invoices (account_id, billing_period_start, billing_period_end,"
        " consumption_kwh, unit_rate_p_per_kwh, subtotal_gbp, vat_gbp, total_gbp,"
        " issue_date, due_date) VALUES"
        " ('A1','2024-02-01','2024-02-29',1.0,1.0,10.0,0.5,10.5,'2024-02-29','2024-03-14')"
    )
    other.commit()
    other.close()
    assert issued_debits_gbp("A1", db_path=db) == 115.5


def test_a_long_lived_reader_sees_module_writes_made_after_it_connected(db):
    """A separate connection opened BEFORE the write observes it on its next SELECT —
    the module commits on every call and python-sqlite3 does not open a read
    transaction for a bare SELECT, so there is no snapshot to go stale."""
    create_schema(db)
    reader = sqlite3.connect(str(db))
    assert reader.execute("SELECT COUNT(*) FROM invoices").fetchone()[0] == 0
    create_invoice(bill(), db)
    assert reader.execute("SELECT COUNT(*) FROM invoices").fetchone()[0] == 1
    reader.close()


def test_readers_are_not_blocked_by_another_connections_open_write_transaction(db):
    """An uncommitted write elsewhere is invisible here and does not block the read:
    the default rollback journal gives readers the pre-transaction state."""
    create_invoice(bill(), db)
    writer = sqlite3.connect(str(db))
    writer.execute("UPDATE invoices SET total_gbp = 9999.0")  # RESERVED lock, uncommitted
    try:
        assert issued_debits_gbp("A1", db_path=db) == 105.0   # not 9999.0
    finally:
        writer.rollback()
        writer.close()


def test_a_second_writer_blocks_for_the_default_busy_timeout_then_raises(db):
    """SURPRISE (concurrency class, operational): sqlite3.connect is called with no
    `timeout=` and no WAL pragma, so a second writer waits the DEFAULT 5-second busy
    timeout and then fails with a bare OperationalError. Two billing runs against one
    invoices.db therefore do not queue and do not retry — one of them stalls five
    seconds and dies mid-run, having already committed the invoices it wrote before
    the collision. This test deliberately pays that ~5s wait once, to document it.

    NOTE the surviving gap: this is a two-CONNECTION test, not a two-THREAD one. True
    concurrent invoicing (interleaved create_invoice calls, partial bulk runs, lost
    updates under retry) is NOT characterized here — no threads by design, so nothing
    below asserts what happens when the writes genuinely race."""
    create_invoice(bill(), db)
    blocker = sqlite3.connect(str(db))
    blocker.execute("UPDATE invoices SET payment_status = 'paid'")  # holds the write lock
    started = time.monotonic()
    try:
        with pytest.raises(sqlite3.OperationalError, match="database is locked"):
            create_invoice(bill(), db)
        assert time.monotonic() - started >= 4.0  # waited out the undeclared default
    finally:
        blocker.rollback()
        blocker.close()
    # The register is unchanged — the failed write left nothing behind.
    assert issued_debits_gbp("A1", db_path=db) == 105.0


# ── A UNIT RATE'S MONEY AND ITS VOLUME MUST COUNT THE SAME PERIOD (2026-08-31) ────────────────
# `_unit_rate_from_bill` divided `total_amount_gbp` by `total_consumption_kwh`. On a catch-up bill
# those legs are different populations: the money reconciles up to thirteen earlier periods of
# estimated reads, the volume is this period alone. Measured across the real book (11,167 bills,
# 959 of them catch-ups):
#
#     total/kwh               median 17.90 p   min -173.52   max 398.09   178 NEGATIVE invoices
#     (total - catchup)/kwh   median 20.21 p   min    3.33   max  81.51     0 negative
#     every other bill        median 19.48 p   min    3.20   max 100.03     0 negative
#
# The sign is the only reason any of the 178 was visible; every other catch-up bill was wrong by
# an amount nothing announced. Found by the end-to-end journey walk on a single household, where
# one bill came to -£5.78 over 328 kWh.

def test_a_catchup_bill_does_not_divide_thirteen_periods_of_money_by_one_of_volume():
    """MUTATION: drop the `- catchup_adjustment_gbp` and this fires on the negative rate."""
    from company.billing.invoice import _unit_rate_from_bill

    # Real shape: a year of under-estimates reconciled downward on one 328 kWh month.
    catchup_bill = {
        "total_consumption_kwh": 328.0,
        "total_amount_gbp": -5.78,
        "catchup_adjustment_gbp": -72.10,
    }
    rate = _unit_rate_from_bill(catchup_bill)
    assert rate > 0, (
        "an invoice carrying a negative unit rate is arithmetic, not a price: the money spans "
        "thirteen periods and the volume spans one"
    )
    assert rate == pytest.approx((66.32 / 328.0) * 100.0, abs=0.01)


def test_an_ordinary_bill_is_untouched_by_the_catchup_netting():
    """The blast-radius leg. 10,208 of 11,167 bills carry no catch-up at all, and a change to the
    common path dressed as a fix for the rare one is how a repair becomes a regression."""
    from company.billing.invoice import _unit_rate_from_bill

    assert _unit_rate_from_bill(
        {"total_consumption_kwh": 1000.0, "total_amount_gbp": 200.0}
    ) == pytest.approx(20.0)
    # An explicit null adjustment reads the same as an absent one.
    assert _unit_rate_from_bill(
        {"total_consumption_kwh": 1000.0, "total_amount_gbp": 200.0,
         "catchup_adjustment_gbp": None}
    ) == pytest.approx(20.0)


def test_a_zero_volume_bill_still_claims_no_rate():
    """Unchanged, and asserted because it is the branch the netting could quietly reorder into a
    division by zero."""
    from company.billing.invoice import _unit_rate_from_bill

    assert _unit_rate_from_bill(
        {"total_consumption_kwh": 0.0, "total_amount_gbp": 42.0,
         "catchup_adjustment_gbp": 10.0}
    ) == 0.0
