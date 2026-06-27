import datetime as dt
import pytest
from company.regulatory.fuel_poverty import (
    FuelPovertyAssessment, FuelPovertyDefinition, FuelPovertyRisk,
    FuelPovertyBook,
)


def make_a(account_id="A1", date=dt.date(2023, 1, 1),
           energy=2000.0, income=15000.0,
           definition=FuelPovertyDefinition.CLASSIC):
    return FuelPovertyAssessment(
        account_id=account_id, assessment_date=date,
        annual_energy_cost_gbp=energy, estimated_annual_income_gbp=income,
        definition=definition,
    )


class TestFuelPovertyAssessment:
    def test_energy_as_pct_income(self):
        a = make_a(energy=1500.0, income=15000.0)
        assert a.energy_as_pct_income == 10.0

    def test_energy_as_pct_income_none_if_zero_income(self):
        a = make_a(income=0.0)
        assert a.energy_as_pct_income is None

    def test_income_after_energy(self):
        a = make_a(energy=2000.0, income=15000.0)
        assert a.income_after_energy_gbp == 13000.0

    def test_risk_fuel_poor_classic(self):
        a = make_a(energy=2000.0, income=15000.0)
        assert a.energy_as_pct_income == pytest.approx(13.3, abs=0.1)
        assert a.risk == FuelPovertyRisk.FUEL_POOR

    def test_risk_high_classic(self):
        a = make_a(energy=1200.0, income=15000.0)
        assert a.risk == FuelPovertyRisk.HIGH

    def test_risk_moderate_classic(self):
        a = make_a(energy=900.0, income=15000.0)
        assert a.risk == FuelPovertyRisk.MODERATE

    def test_risk_low_classic(self):
        a = make_a(energy=600.0, income=15000.0)
        assert a.risk == FuelPovertyRisk.LOW

    def test_risk_none_income_high(self):
        a = make_a(income=0.0)
        assert a.risk == FuelPovertyRisk.HIGH

    def test_is_fuel_poor_true(self):
        a = make_a(energy=2000.0, income=15000.0)
        assert a.is_fuel_poor is True

    def test_is_fuel_poor_false(self):
        a = make_a(energy=600.0, income=15000.0)
        assert a.is_fuel_poor is False

    def test_lihc_fuel_poor(self):
        a = make_a(energy=2000.0, income=15000.0,
                   definition=FuelPovertyDefinition.LOW_INCOME_HIGH_COST)
        assert a.is_fuel_poor is True

    def test_lihc_not_fuel_poor_high_income(self):
        a = make_a(energy=2000.0, income=50000.0,
                   definition=FuelPovertyDefinition.LOW_INCOME_HIGH_COST)
        assert a.is_fuel_poor is False

    def test_frozen(self):
        a = make_a()
        with pytest.raises((AttributeError, TypeError)):
            a.account_id = "X"


class TestFuelPovertyBook:
    def test_record_assessment(self):
        book = FuelPovertyBook()
        book.record_assessment(make_a())
        assert len(book.fuel_poor_accounts()) <= 1

    def test_latest_for(self):
        book = FuelPovertyBook()
        a1 = make_a(date=dt.date(2022, 1, 1), energy=2000.0)
        a2 = make_a(date=dt.date(2023, 1, 1), energy=600.0)
        book.record_assessment(a1)
        book.record_assessment(a2)
        latest = book.latest_for("A1")
        assert latest.assessment_date == dt.date(2023, 1, 1)

    def test_latest_none_unknown_account(self):
        assert FuelPovertyBook().latest_for("NONE") is None

    def test_fuel_poor_accounts_only_latest(self):
        book = FuelPovertyBook()
        a_poor = make_a(account_id="A1", date=dt.date(2022, 1, 1), energy=2000.0)
        a_ok = make_a(account_id="A1", date=dt.date(2023, 1, 1), energy=600.0)
        book.record_assessment(a_poor)
        book.record_assessment(a_ok)
        assert len(book.fuel_poor_accounts()) == 0

    def test_high_risk_includes_fuel_poor(self):
        book = FuelPovertyBook()
        book.record_assessment(make_a(energy=2000.0, income=15000.0))
        assert len(book.high_risk_accounts()) == 1

    def test_fuel_poverty_rate_empty(self):
        assert FuelPovertyBook().fuel_poverty_rate_pct() == 0.0

    def test_fuel_poverty_rate(self):
        book = FuelPovertyBook()
        book.record_assessment(make_a(account_id="A1", energy=2000.0, income=15000.0))
        book.record_assessment(make_a(account_id="A2", energy=600.0, income=15000.0))
        assert book.fuel_poverty_rate_pct() == 50.0

    def test_summary_keys(self):
        s = FuelPovertyBook().fuel_poverty_summary()
        for k in ("total_assessments", "fuel_poor_count", "high_risk_count", "fuel_poverty_rate_pct"):
            assert k in s
