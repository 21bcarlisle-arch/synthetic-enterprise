"""Tests for company.crm.customer_registry."""

import tempfile
from pathlib import Path

import pytest

from company.crm.customer_registry import (
    account_count,
    all_accounts,
    create_schema,
    get_account,
    seed_from_customers,
    update_status,
)


@pytest.fixture
def db(tmp_path):
    """Temporary in-process SQLite database for each test."""
    return tmp_path / "test_registry.db"


_SAMPLE_CUSTOMERS = [
    {
        "customer_id": "C1",
        "acquisition_date": "2016-01-01",
        "location": {"lat": 51.5074, "lon": -0.1278, "region": "London"},
        "home_type": "urban_flat",
        "bedrooms": 2,
        "epc_rating": "D",
        "eac_kwh": 2800,
        "commodity": "electricity",
        "contract_type": "fixed_1yr",
        "segment": "resi",
    },
    {
        "customer_id": "C5",
        "acquisition_date": "2016-01-01",
        "location": {"lat": 51.5074, "lon": -0.1278, "region": "London"},
        "home_type": "small_office",
        "bedrooms": None,
        "epc_rating": "C",
        "eac_kwh": 25000,
        "profile_class": 3,
        "commodity": "electricity",
        "contract_type": "fixed_1yr",
        "segment": "SME",
    },
    {
        "customer_id": "C7",
        "acquisition_date": "2016-01-01",
        "location": {"lat": 51.5074, "lon": -0.1278, "region": "London"},
        "home_type": "urban_flat",
        "bedrooms": 1,
        "epc_rating": "C",
        "eac_kwh": None,
        "metering": "HH",
        "commodity": "electricity",
        "contract_type": "fixed_1yr",
        "segment": "resi",
    },
]


def test_create_schema_is_idempotent(db):
    create_schema(db)
    create_schema(db)  # second call should not error


def test_seed_from_customers_inserts_records(db):
    n = seed_from_customers(_SAMPLE_CUSTOMERS, db)
    assert n == 3


def test_seed_from_customers_is_idempotent(db):
    seed_from_customers(_SAMPLE_CUSTOMERS, db)
    n2 = seed_from_customers(_SAMPLE_CUSTOMERS, db)
    assert n2 == 0  # all already exist — INSERT OR IGNORE


def test_get_account_returns_record(db):
    seed_from_customers(_SAMPLE_CUSTOMERS, db)
    rec = get_account("C1", db)
    assert rec is not None
    assert rec["account_id"] == "C1"
    assert rec["segment"] == "resi"
    assert rec["status"] == "active"


def test_get_account_returns_none_for_unknown(db):
    create_schema(db)
    assert get_account("C99", db) is None


def test_sme_customer_type_is_sme(db):
    seed_from_customers(_SAMPLE_CUSTOMERS, db)
    rec = get_account("C5", db)
    assert rec["customer_type"] == "SME"


def test_residential_customer_type_is_residential(db):
    seed_from_customers(_SAMPLE_CUSTOMERS, db)
    rec = get_account("C1", db)
    assert rec["customer_type"] == "residential"


def test_smart_meter_flag_set_for_hh_customers(db):
    seed_from_customers(_SAMPLE_CUSTOMERS, db)
    rec = get_account("C7", db)
    assert rec["smart_meter"] == 1


def test_smart_meter_flag_unset_for_profile_class_customers(db):
    seed_from_customers(_SAMPLE_CUSTOMERS, db)
    rec = get_account("C1", db)
    assert rec["smart_meter"] == 0


def test_update_status_churned(db):
    seed_from_customers(_SAMPLE_CUSTOMERS, db)
    update_status("C1", "churned", db)
    assert get_account("C1", db)["status"] == "churned"


def test_update_status_invalid_raises(db):
    create_schema(db)
    with pytest.raises(ValueError):
        update_status("C1", "gone", db)


def test_all_accounts_returns_all(db):
    seed_from_customers(_SAMPLE_CUSTOMERS, db)
    accounts = all_accounts(db_path=db)
    assert len(accounts) == 3


def test_all_accounts_status_filter(db):
    seed_from_customers(_SAMPLE_CUSTOMERS, db)
    update_status("C1", "churned", db)
    active = all_accounts(status_filter="active", db_path=db)
    assert all(a["status"] == "active" for a in active)
    assert len(active) == 2


def test_account_count(db):
    seed_from_customers(_SAMPLE_CUSTOMERS, db)
    assert account_count(db) == 3


# --- Phase MN depth tests ---

def test_mpan_stored(db):
    seed_from_customers(_SAMPLE_CUSTOMERS, db)
    rec = get_account('C1', db)
    assert rec['mpan'] is not None and len(rec['mpan']) > 0


def test_email_stored(db):
    seed_from_customers(_SAMPLE_CUSTOMERS, db)
    rec = get_account('C1', db)
    assert '@synthetic-supplier.co.uk' in rec['email']


def test_address_stored(db):
    seed_from_customers(_SAMPLE_CUSTOMERS, db)
    rec = get_account('C1', db)
    assert rec['address'] is not None and len(rec['address']) > 0


def test_fuel_type_electricity(db):
    # C5 is SME, not in the dual-fuel C1-C4 group, so fuel_type=electricity
    seed_from_customers(_SAMPLE_CUSTOMERS, db)
    rec = get_account('C5', db)
    assert rec['fuel_type'] == 'electricity'


def test_tariff_type_stored(db):
    seed_from_customers(_SAMPLE_CUSTOMERS, db)
    rec = get_account('C1', db)
    assert rec['tariff_type'] == 'fixed'


def test_update_status_pending(db):
    seed_from_customers(_SAMPLE_CUSTOMERS, db)
    update_status('C1', 'pending', db)
    assert get_account('C1', db)['status'] == 'pending'


def test_segment_stored(db):
    seed_from_customers(_SAMPLE_CUSTOMERS, db)
    rec = get_account('C1', db)
    assert rec['segment'] == 'resi'


def test_contact_name_stored(db):
    seed_from_customers(_SAMPLE_CUSTOMERS, db)
    rec = get_account('C1', db)
    assert rec['contact_name'] == 'Alice Thompson'


def test_supply_start_stored(db):
    seed_from_customers(_SAMPLE_CUSTOMERS, db)
    rec = get_account('C1', db)
    assert rec['supply_start'] == '2016-01-01'


def test_all_accounts_sorted_by_account_id(db):
    seed_from_customers(_SAMPLE_CUSTOMERS, db)
    accounts = all_accounts(db_path=db)
    ids = [a['account_id'] for a in accounts]
    assert ids == sorted(ids)
