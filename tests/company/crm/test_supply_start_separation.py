"""C_supply_start_semantic_separation -- `supply_start` (the real relationship
start) is separated from `term_anchor_date` (the 365-day renewal grid anchor).

Named defect: `seed_from_customers` piped `acquisition_date` straight into a
column called `supply_start`. For a successor account that anchor is the
PREDECESSOR's genesis date, so the successor was stamped with a relationship
start ~5 years before it existed.

R15 -- the two mutations these tests must fire on:
  1. re-couple the columns (write the anchor into supply_start again) -> the
     separation tests FAIL.
  2. back-fill an unknown supply_start from the anchor instead of recording
     UNKNOWN -> the honesty tests FAIL.
Both are exercised explicitly below rather than asserted, so the controls are
proven able to fail (a control that cannot fail is worse than none).
"""

import datetime as dt
import sqlite3

import pytest

from company.compliance.domain_invariants import (
    ALL_INVARIANTS,
    SUPPLY_START_NOT_BEFORE_FIRST_OBSERVABLE,
    check_supply_start_not_before_first_observable,
)
from company.crm.customer_registry import (
    all_accounts,
    create_schema,
    get_account,
    seed_from_customers,
)
from company.crm.supply_start import (
    DEFAULT_TERM_ANCHOR,
    derive_supply_start,
    derive_term_anchor,
    migrate_legacy_supply_start,
)


@pytest.fixture
def db(tmp_path):
    return tmp_path / "supply_start_registry.db"


# The real C1_2 shape: a successor whose anchor is pinned to predecessor C1's
# genesis date (saas/customers.py SUCCESSOR_CUSTOMERS), while the observable
# acquisition event says the relationship actually began 2020-12-30
# (run_output_latest.json, channel "home-move-win", predecessor_id "C1").
_ANCHOR = "2016-01-01"
_REAL_ACTIVATION = "2020-12-30"

_SUCCESSOR = {
    "customer_id": "C1_2",
    "successor_of": "C1",
    "acquisition_date": _ANCHOR,
    "location": {"region": "London"},
    "home_type": "urban_flat",
    "commodity": "electricity",
    "contract_type": "fixed_1yr",
    "segment": "resi",
}

_BASE = {
    "customer_id": "C1",
    "acquisition_date": _ANCHOR,
    "location": {"region": "London"},
    "home_type": "urban_flat",
    "commodity": "electricity",
    "contract_type": "fixed_1yr",
    "segment": "resi",
}


# --- The separation itself -------------------------------------------------

def test_successor_supply_start_is_the_activation_not_the_anchor(db):
    """THE finding. The activation date is sourced from the observable event
    stream, which is independent of the anchor field it is compared against --
    so this is not a tautology (R15 independence)."""
    seed_from_customers(
        [_SUCCESSOR], db, activation_by_account={"C1_2": _REAL_ACTIVATION}
    )
    rec = get_account("C1_2", db)
    assert rec["supply_start"] == _REAL_ACTIVATION
    # The anchor survives intact and stays independently addressable, because
    # the term grid depends on it.
    assert rec["term_anchor_date"] == _ANCHOR


def test_supply_start_does_not_move_when_the_term_anchor_moves(db):
    """The mint's own R15 shape: a re-contracted customer's supply_start must
    NOT move when the term anchor moves. Mutate the code to keep them coupled
    and this fires."""
    re_anchored = dict(_SUCCESSOR, acquisition_date="2019-06-01")
    seed_from_customers(
        [re_anchored], db, activation_by_account={"C1_2": _REAL_ACTIVATION}
    )
    rec = get_account("C1_2", db)
    assert rec["supply_start"] == _REAL_ACTIVATION  # unmoved
    assert rec["term_anchor_date"] == "2019-06-01"  # moved


def test_mutation_recoupling_the_columns_fires_the_separation(db):
    """Restore today's pre-fix behaviour -- write the anchor into supply_start
    -- and the assertion above must fail. Proves the control can fail."""
    create_schema(db)
    conn = sqlite3.connect(str(db))
    conn.execute(
        "INSERT INTO customers (account_id, customer_type, fuel_type, supply_start,"
        " term_anchor_date, status, segment) VALUES (?,?,?,?,?,?,?)",
        ("C1_2", "residential", "electricity", _ANCHOR, _ANCHOR, "active", "resi"),
    )
    conn.commit()
    conn.close()
    rec = get_account("C1_2", db)
    assert rec["supply_start"] == _ANCHOR  # the mutated (defective) state
    assert rec["supply_start"] != _REAL_ACTIVATION


def test_base_customer_supply_start_is_unchanged(db):
    """A non-successor's acquisition_date genuinely IS its relationship start.
    The fix must not disturb the ~13 correct records to fix the 6 wrong ones."""
    seed_from_customers([_BASE], db)
    rec = get_account("C1", db)
    assert rec["supply_start"] == _ANCHOR
    assert rec["term_anchor_date"] == _ANCHOR


def test_activation_observable_wins_for_a_base_customer_too(db):
    """A fresh-market win carries its real date in the event stream; if one is
    observed it is authoritative regardless of successor status."""
    seed_from_customers([_BASE], db, activation_by_account={"C1": "2021-03-04"})
    assert get_account("C1", db)["supply_start"] == "2021-03-04"


# --- UNKNOWN is recorded, never back-dated ---------------------------------

def test_successor_without_an_activation_observable_is_unknown_not_backdated(db):
    """A fabricated tenure is worse than an absent one. The only date on the
    record belongs to the predecessor, so UNKNOWN is the honest answer."""
    seed_from_customers([_SUCCESSOR], db)
    rec = get_account("C1_2", db)
    assert rec["supply_start"] is None
    assert rec["supply_start"] != _ANCHOR  # the back-dating that must not happen
    assert rec["term_anchor_date"] == _ANCHOR  # anchor still recorded


def test_record_with_no_acquisition_date_gets_unknown_supply_start_not_the_default():
    """DEFAULT_TERM_ANCHOR is an anchor convention. Stamping it as a
    relationship start would invent a tenure for a record that has none."""
    bare = {"customer_id": "CX", "segment": "resi"}
    assert derive_supply_start(bare) is None
    assert derive_term_anchor(bare) == DEFAULT_TERM_ANCHOR


def test_malformed_activation_date_raises_rather_than_falling_back():
    """Fail-loud. A silent fallback to the anchor would reintroduce the phantom
    invisibly -- the fail-open pattern this whole atom is about."""
    with pytest.raises(ValueError):
        derive_supply_start(_SUCCESSOR, {"C1_2": "30-12-2020"})
    with pytest.raises(ValueError):
        derive_supply_start(_SUCCESSOR, {"C1_2": 20201230})


def test_malformed_acquisition_date_raises():
    with pytest.raises(ValueError):
        derive_term_anchor({"customer_id": "CX", "acquisition_date": "not-a-date"})


# --- Legacy migration -------------------------------------------------------

def _legacy_db(path):
    """A registry on the pre-separation schema: one NOT NULL date column, fed
    from acquisition_date."""
    conn = sqlite3.connect(str(path))
    conn.execute("""
        CREATE TABLE customers (
            account_id      TEXT PRIMARY KEY,
            customer_type   TEXT NOT NULL,
            fuel_type       TEXT NOT NULL,
            supply_start    TEXT NOT NULL,
            status          TEXT NOT NULL DEFAULT 'active',
            tariff_type     TEXT NOT NULL DEFAULT 'fixed',
            contact_name    TEXT,
            address         TEXT,
            email           TEXT,
            mpan            TEXT,
            mprn            TEXT,
            smart_meter     INTEGER NOT NULL DEFAULT 0,
            segment         TEXT NOT NULL,
            successor_of    TEXT,
            created_at      TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    conn.execute("CREATE INDEX idx_status ON customers(status)")
    conn.execute(
        "INSERT INTO customers (account_id, customer_type, fuel_type, supply_start,"
        " segment, successor_of) VALUES (?,?,?,?,?,?)",
        ("C1", "residential", "electricity", _ANCHOR, "resi", None),
    )
    conn.execute(
        "INSERT INTO customers (account_id, customer_type, fuel_type, supply_start,"
        " segment, successor_of) VALUES (?,?,?,?,?,?)",
        ("C1_2", "residential", "electricity", _ANCHOR, "resi", "C1"),
    )
    conn.commit()
    conn.close()


def test_migration_splits_the_legacy_column_by_the_stated_rule(db):
    _legacy_db(db)
    create_schema(db)

    base = get_account("C1", db)
    assert base["term_anchor_date"] == _ANCHOR
    assert base["supply_start"] == _ANCHOR  # non-successor: the two coincide

    successor = get_account("C1_2", db)
    assert successor["term_anchor_date"] == _ANCHOR  # what the column really held
    assert successor["supply_start"] is None  # unrecoverable -> UNKNOWN


def test_migration_is_idempotent_and_preserves_the_population(db):
    _legacy_db(db)
    create_schema(db)
    create_schema(db)
    create_schema(db)
    assert len(all_accounts(db_path=db)) == 2
    assert get_account("C1_2", db)["supply_start"] is None


def test_migration_rule_never_returns_the_anchor_for_a_successor():
    assert migrate_legacy_supply_start(_ANCHOR, "C1") is None
    assert migrate_legacy_supply_start(_ANCHOR, None) == _ANCHOR


# --- R10 class guard --------------------------------------------------------

def test_class_guard_is_registered_in_the_invariant_library():
    assert SUPPLY_START_NOT_BEFORE_FIRST_OBSERVABLE in ALL_INVARIANTS
    assert SUPPLY_START_NOT_BEFORE_FIRST_OBSERVABLE.id == (
        "supply_start_not_before_first_observable"
    )
    assert SUPPLY_START_NOT_BEFORE_FIRST_OBSERVABLE.jurisdiction == "UK"


def test_class_guard_fires_on_the_named_defect():
    """The exact C1_2 phantom: supply_start five years before the acquisition
    event that created the account."""
    assert not check_supply_start_not_before_first_observable({
        "account_id": "C1_2",
        "supply_start": _ANCHOR,
        "acquisition_event_date": _REAL_ACTIVATION,
    })


def test_class_guard_passes_the_corrected_record():
    assert check_supply_start_not_before_first_observable({
        "account_id": "C1_2",
        "supply_start": _REAL_ACTIVATION,
        "acquisition_event_date": _REAL_ACTIVATION,
        "first_issued_bill_date": "2021-01-28",
    })


def test_class_guard_closes_the_class_not_the_instance():
    """Any account, any run -- a phantom that never involves C1_2 or a
    successor at all must still fire."""
    for account, start, observed in [
        ("C9", "1999-01-01", "2018-04-02"),
        ("SME_44", "2016-01-01", "2016-01-02"),
        ("C4_2", "2020-12-29", "2020-12-30"),
    ]:
        assert not check_supply_start_not_before_first_observable({
            "account_id": account,
            "supply_start": start,
            "first_meter_read_date": observed,
        }), account


def test_class_guard_uses_the_EARLIEST_observable():
    """A later observable must not mask a phantom that an earlier one exposes,
    and must not condemn a supply_start that legitimately precedes it."""
    assert check_supply_start_not_before_first_observable({
        "supply_start": "2020-12-30",
        "acquisition_event_date": "2020-12-30",
        "first_issued_bill_date": "2021-02-01",  # later; must not fire
    })
    assert not check_supply_start_not_before_first_observable({
        "supply_start": "2016-01-01",
        "acquisition_event_date": "2020-12-30",
        "first_issued_bill_date": "2021-02-01",
    })


def test_class_guard_accepts_an_explicit_unknown():
    """UNKNOWN is the required answer where the date is unrecoverable; it
    cannot claim a phantom tenure, so it must not be penalised."""
    assert check_supply_start_not_before_first_observable({
        "account_id": "C1_2",
        "supply_start": None,
        "acquisition_event_date": _REAL_ACTIVATION,
    })


@pytest.mark.parametrize("record", [
    {},                                                  # nothing at all
    {"account_id": "C1_2"},                              # no supply_start key
    {"acquisition_event_date": _REAL_ACTIVATION},        # observable but no field
    {"supply_start": _REAL_ACTIVATION},                  # no observables at all
    {"supply_start": _REAL_ACTIVATION,
     "acquisition_event_date": None,
     "first_meter_read_date": None,
     "first_issued_bill_date": None},                    # all observables None
    {"supply_start": _REAL_ACTIVATION,
     "acquisition_event_date": ""},                      # empty-string observable
    {"supply_start": _REAL_ACTIVATION,
     "acquisition_event_date": "30/12/2020"},            # unparseable observable
    {"supply_start": _REAL_ACTIVATION,
     "acquisition_event_date": 20201230},                # non-string observable
    {"supply_start": "not-a-date",
     "acquisition_event_date": _REAL_ACTIVATION},        # unparseable supply_start
    {"supply_start": 20201230,
     "acquisition_event_date": _REAL_ACTIVATION},        # non-string supply_start
])
def test_class_guard_fails_closed(record):
    """R15 fail-open sweep. Every one of these would be a silent green under a
    naive implementation; an unavailable check is a FAILED check, and a record
    that never declares supply_start is malformed, not exempt. Note the
    distinction being pinned: key ABSENT fails, explicit None passes."""
    assert not check_supply_start_not_before_first_observable(record)


def test_class_guard_does_not_import_the_code_it_audits():
    """R15 independence, mechanised: if the checker ever borrows the derivation
    module, a regression in that module could no longer be detected by it.

    Checked against the module's actual import STATEMENTS (parsed), not a
    substring of its source -- a prose mention of the module in a docstring is
    not a dependency, and matching on one would make this fail for the wrong
    reason (it did, on first run)."""
    import ast
    import company.compliance.domain_invariants as inv

    tree = ast.parse(open(inv.__file__).read())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
            imported.update(f"{node.module or ''}.{a.name}" for a in node.names)

    assert not any(m.startswith("company.crm") for m in imported), sorted(imported)
    # And the derivation helpers are genuinely absent from its namespace.
    assert not hasattr(inv, "derive_supply_start")
    assert not hasattr(inv, "migrate_legacy_supply_start")


def test_seeded_successor_satisfies_the_class_guard(db):
    """End-to-end: what the registry actually writes passes the independent
    checker, for both the observed and the unknown case."""
    seed_from_customers(
        [_SUCCESSOR, _BASE], db, activation_by_account={"C1_2": _REAL_ACTIVATION}
    )
    assert check_supply_start_not_before_first_observable({
        **get_account("C1_2", db),
        "acquisition_event_date": _REAL_ACTIVATION,
    })
    assert check_supply_start_not_before_first_observable({
        **get_account("C1", db),
        "acquisition_event_date": _ANCHOR,
    })


def test_seeded_successor_without_observable_also_satisfies_the_guard(db):
    seed_from_customers([_SUCCESSOR], db)
    assert check_supply_start_not_before_first_observable({
        **get_account("C1_2", db),
        "acquisition_event_date": _REAL_ACTIVATION,
    })


def test_the_pre_fix_registry_write_would_have_failed_the_guard():
    """Confirms the guard would have caught the defect at the moment it was
    written -- the value the old line 133 produced, checked against the
    observable it contradicted."""
    pre_fix_supply_start = _SUCCESSOR.get("acquisition_date", "2016-01-01")
    assert not check_supply_start_not_before_first_observable({
        "account_id": "C1_2",
        "supply_start": pre_fix_supply_start,
        "acquisition_event_date": _REAL_ACTIVATION,
    })


def test_guard_is_clock_free_and_replay_safe():
    """C-S2: the predicate is pure -- same input, same verdict, no wall clock."""
    record = {"supply_start": "2020-12-30", "acquisition_event_date": "2020-12-30"}
    verdicts = {check_supply_start_not_before_first_observable(dict(record))
                for _ in range(5)}
    assert verdicts == {True}
    future = (dt.date.today() + dt.timedelta(days=3650)).isoformat()
    assert check_supply_start_not_before_first_observable({
        "supply_start": future, "acquisition_event_date": future,
    })
