import datetime as dt
import pytest
from company.regulatory.ccl_ledger import (
    CCLFuel, CCLExemptReason, CCLCharge, CCLQuarterlyReturn, CCLLedger
)


def test_electricity_rate_2016():
    assert CCLLedger.rate_for_year(2016, CCLFuel.ELECTRICITY) == 0.554


def test_electricity_rate_2019_spike():
    rate_2018 = CCLLedger.rate_for_year(2018, CCLFuel.ELECTRICITY)
    rate_2019 = CCLLedger.rate_for_year(2019, CCLFuel.ELECTRICITY)
    assert rate_2019 == 0.847
    assert rate_2019 / rate_2018 > 1.40


def test_gas_rate_2019_spike():
    rate_2018 = CCLLedger.rate_for_year(2018, CCLFuel.GAS)
    rate_2019 = CCLLedger.rate_for_year(2019, CCLFuel.GAS)
    assert rate_2019 == 0.339
    assert rate_2019 / rate_2018 > 1.60


def test_gas_rate_2022():
    assert CCLLedger.rate_for_year(2022, CCLFuel.GAS) == 0.465


def test_unknown_year_falls_back_to_nearest():
    rate = CCLLedger.rate_for_year(2026, CCLFuel.ELECTRICITY)
    assert rate == CCLLedger.rate_for_year(2025, CCLFuel.ELECTRICITY)


def test_business_electricity_charge():
    ledger = CCLLedger()
    charge = ledger.record_charge("SME1", 2022, CCLFuel.ELECTRICITY, 10_000, is_business=True)
    assert not charge.is_exempt
    assert charge.rate_p_per_kwh == 0.775
    assert charge.charge_gbp == pytest.approx(77.50)


def test_residential_exempt():
    ledger = CCLLedger()
    charge = ledger.record_charge("RES1", 2022, CCLFuel.ELECTRICITY, 3_000, is_business=False)
    assert charge.is_exempt
    assert charge.exempt_reason == CCLExemptReason.RESIDENTIAL
    assert charge.charge_gbp == 0.0


def test_lec_covered_exempt():
    ledger = CCLLedger()
    charge = ledger.record_charge("BIZ1", 2022, CCLFuel.ELECTRICITY, 50_000,
                                  is_business=True, lec_covered=True)
    assert charge.is_exempt
    assert charge.exempt_reason == CCLExemptReason.LEC_COVERED
    assert charge.charge_gbp == 0.0


def test_gas_charge_ic_customer():
    ledger = CCLLedger()
    charge = ledger.record_charge("IC1", 2022, CCLFuel.GAS, 100_000, is_business=True)
    assert not charge.is_exempt
    assert charge.charge_gbp == pytest.approx(465.0)


def test_charges_for_account_filters():
    ledger = CCLLedger()
    ledger.record_charge("A", 2022, CCLFuel.ELECTRICITY, 5_000, is_business=True)
    ledger.record_charge("B", 2022, CCLFuel.ELECTRICITY, 5_000, is_business=True)
    ledger.record_charge("A", 2022, CCLFuel.GAS, 10_000, is_business=True)
    assert len(ledger.charges_for_account("A")) == 2
    assert len(ledger.charges_for_account("B")) == 1


def test_charges_for_year_filters():
    ledger = CCLLedger()
    ledger.record_charge("X", 2021, CCLFuel.ELECTRICITY, 5_000, is_business=True)
    ledger.record_charge("X", 2022, CCLFuel.ELECTRICITY, 5_000, is_business=True)
    assert len(ledger.charges_for_year(2021)) == 1
    assert len(ledger.charges_for_year(2022)) == 1


def test_total_due_excludes_exempt():
    ledger = CCLLedger()
    ledger.record_charge("BIZ", 2022, CCLFuel.ELECTRICITY, 10_000, is_business=True)
    ledger.record_charge("RES", 2022, CCLFuel.ELECTRICITY, 3_000, is_business=False)
    total = ledger.total_due_gbp(2022)
    assert total == pytest.approx(77.50)


def test_quarterly_return_aggregates():
    ledger = CCLLedger()
    ledger.record_charge("BIZ", 2022, CCLFuel.ELECTRICITY, 10_000, is_business=True)
    ledger.record_charge("BIZ", 2022, CCLFuel.GAS, 20_000, is_business=True)
    qr = ledger.quarterly_return(dt.date(2022, 12, 31))
    assert qr.electricity_due_gbp == pytest.approx(77.50)
    assert qr.gas_due_gbp == pytest.approx(93.0)
    assert qr.total_due_gbp == pytest.approx(170.50)
    assert qr.filed is False


def test_quarterly_return_filed_flag():
    ledger = CCLLedger()
    ledger.record_charge("BIZ", 2022, CCLFuel.ELECTRICITY, 5_000, is_business=True)
    qr = ledger.quarterly_return(dt.date(2022, 9, 30), filed=True)
    assert qr.filed is True


def test_ccl_summary_keys():
    ledger = CCLLedger()
    ledger.record_charge("BIZ", 2022, CCLFuel.ELECTRICITY, 10_000, is_business=True)
    ledger.record_charge("RES", 2022, CCLFuel.ELECTRICITY, 3_000, is_business=False)
    s = ledger.ccl_summary()
    assert s["total_charges_recorded"] == 2
    assert s["exempt_charges"] == 1
    assert s["chargeable_charges"] == 1
    assert s["residential_exempt"] == 1
    assert s["lec_exempt"] == 0
    assert 2022 in s["years_covered"]
    assert s["total_due_by_year"][2022] == pytest.approx(77.50)


def test_electricity_rate_stable_post_2021():
    for year in (2021, 2022, 2023, 2024, 2025):
        assert CCLLedger.rate_for_year(year, CCLFuel.ELECTRICITY) == 0.775

