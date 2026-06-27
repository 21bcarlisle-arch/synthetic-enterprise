import sqlite3
import pytest
from pathlib import Path
from company.billing.consumption import consumption_history, monthly_totals


@pytest.fixture
def db_path(tmp_path):
    db = tmp_path / "invoices.db"
    conn = sqlite3.connect(str(db))
    conn.execute("""CREATE TABLE invoices (
        account_id TEXT, billing_period_start TEXT, billing_period_end TEXT,
        consumption_kwh REAL, commodity TEXT
    )""")
    conn.executemany("INSERT INTO invoices VALUES (?,?,?,?,?)", [
        ("A001", "2022-01-01", "2022-02-01", 300.0, "electricity"),
        ("A001", "2022-02-01", "2022-03-01", 280.0, "electricity"),
        ("A002", "2022-01-01", "2022-02-01", 500.0, "gas"),
    ])
    conn.commit()
    conn.close()
    return db


class TestConsumptionHistory:
    def test_returns_empty_when_db_missing(self, tmp_path):
        records = consumption_history("A001", tmp_path / "missing.db")
        assert records == []

    def test_returns_records_for_account(self, db_path):
        records = consumption_history("A001", db_path)
        assert len(records) == 2

    def test_filters_by_account(self, db_path):
        records = consumption_history("A002", db_path)
        assert len(records) == 1
        assert records[0]["commodity"] == "gas"

    def test_record_keys_present(self, db_path):
        records = consumption_history("A001", db_path)
        r = records[0]
        for key in ("period_start", "period_end", "kwh", "commodity", "year", "month"):
            assert key in r

    def test_year_month_parsed(self, db_path):
        records = consumption_history("A001", db_path)
        assert records[0]["year"] == 2022
        assert records[0]["month"] == 1

    def test_sorted_by_period(self, db_path):
        records = consumption_history("A001", db_path)
        starts = [r["period_start"] for r in records]
        assert starts == sorted(starts)

    def test_returns_empty_for_unknown_account(self, db_path):
        records = consumption_history("UNKNOWN", db_path)
        assert records == []


class TestMonthlyTotals:
    def _records(self):
        return [
            {"year": 2022, "month": 1, "kwh": 100.0, "commodity": "electricity"},
            {"year": 2022, "month": 1, "kwh": 50.0, "commodity": "electricity"},
            {"year": 2022, "month": 2, "kwh": 200.0, "commodity": "electricity"},
        ]

    def test_aggregates_same_month(self):
        totals = monthly_totals(self._records())
        jan = next(t for t in totals if t["month"] == 1)
        assert jan["kwh"] == pytest.approx(150.0)

    def test_separate_months_preserved(self):
        totals = monthly_totals(self._records())
        assert len(totals) == 2

    def test_sorted_by_year_month(self):
        totals = monthly_totals(self._records())
        keys = [(t["year"], t["month"]) for t in totals]
        assert keys == sorted(keys)

    def test_empty_input(self):
        assert monthly_totals([]) == []
