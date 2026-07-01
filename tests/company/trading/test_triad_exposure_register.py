"""Tests for Triad Exposure Register (Phase FG)."""
import datetime as dt
import pytest
from company.trading.triad_exposure_register import (
    TriadSeason, CustomerExposureClass, TriadObservation,
    CustomerTriadExposure, TriadExposureRegister,
)

SEASON = TriadSeason.Y2023_24


def make_obs(n=1, sp=36, demand=55.0):
    return TriadObservation(
        season=SEASON,
        triad_number=n,
        settlement_date=dt.date(2024, 1, 10 + n),
        settlement_period=sp,
        national_demand_gw=demand,
    )


def make_exposure(acct="C1", d1=0.01, d2=0.01, d3=0.01, tariff=80.0):
    return CustomerTriadExposure(
        account_id=acct,
        season=SEASON,
        demand_mw_triad_1=d1,
        demand_mw_triad_2=d2,
        demand_mw_triad_3=d3,
        tnu_os_tariff_gbp_per_kw=tariff,
    )


class TestTriadObservation:
    def test_is_valid(self):
        assert make_obs(n=1).is_valid

    def test_invalid_triad_number(self):
        o = TriadObservation(SEASON, 0, dt.date(2024, 1, 1), 36, 50.0)
        assert not o.is_valid

    def test_invalid_sp(self):
        o = TriadObservation(SEASON, 1, dt.date(2024, 1, 1), 0, 50.0)
        assert not o.is_valid


class TestCustomerTriadExposure:
    def test_avg_demand(self):
        e = make_exposure(d1=0.01, d2=0.02, d3=0.03)
        assert e.avg_demand_mw == pytest.approx(0.02)

    def test_tnuos_charge(self):
        e = make_exposure(d1=0.01, d2=0.01, d3=0.01, tariff=80.0)
        # avg_mw=0.01, kW=10, charge=10*80=800
        assert e.tnu_os_charge_gbp == pytest.approx(800.0)

    def test_exposure_summary(self):
        s = make_exposure().exposure_summary()
        assert "TNUoS" in s


class TestTriadExposureRegister:
    def test_record_triad(self):
        reg = TriadExposureRegister()
        reg.record_triad(make_obs())
        assert len(reg.triads_for_season(SEASON)) == 1

    def test_triads_sorted_by_number(self):
        reg = TriadExposureRegister()
        reg.record_triad(make_obs(n=3))
        reg.record_triad(make_obs(n=1))
        triads = reg.triads_for_season(SEASON)
        assert triads[0].triad_number == 1

    def test_record_customer_exposure(self):
        reg = TriadExposureRegister()
        reg.record_customer_exposure(make_exposure())
        assert len(reg.exposures_for_season(SEASON)) == 1

    def test_total_tnuos(self):
        reg = TriadExposureRegister()
        reg.record_customer_exposure(make_exposure(d1=0.01, d2=0.01, d3=0.01, tariff=80.0))
        reg.record_customer_exposure(make_exposure(acct="C2", d1=0.02, d2=0.02, d3=0.02))
        total = reg.total_tnu_os_charge_gbp(SEASON)
        assert total == pytest.approx(800.0 + 1600.0)

    def test_high_exposure_accounts(self):
        reg = TriadExposureRegister()
        reg.record_customer_exposure(make_exposure())  # default HIGH
        assert len(reg.high_exposure_accounts(SEASON)) == 1

    def test_triad_register_summary(self):
        reg = TriadExposureRegister()
        reg.record_triad(make_obs())
        reg.record_customer_exposure(make_exposure())
        s = reg.triad_register_summary(SEASON)
        assert "Triad Register" in s


# --- Phase MF depth tests ---

def test_season_stored_in_observation():
    obs = make_obs(n=1)
    assert obs.season == SEASON


def test_triad_number_stored():
    obs = make_obs(n=2)
    assert obs.triad_number == 2


def test_settlement_date_stored():
    obs = make_obs(n=1)
    assert obs.settlement_date == dt.date(2024, 1, 11)


def test_settlement_period_stored():
    obs = make_obs(n=1, sp=36)
    assert obs.settlement_period == 36


def test_national_demand_gw_stored():
    obs = make_obs(n=1, demand=58.3)
    assert obs.national_demand_gw == pytest.approx(58.3)


def test_account_id_stored_in_exposure():
    exp = CustomerTriadExposure(
        account_id="ACC-MF", season=SEASON,
        demand_mw_triad_1=0.5, demand_mw_triad_2=0.6, demand_mw_triad_3=0.4,
    )
    assert exp.account_id == "ACC-MF"


def test_demand_mw_triad_1_stored():
    exp = CustomerTriadExposure(
        account_id="ACC-MF", season=SEASON,
        demand_mw_triad_1=1.2, demand_mw_triad_2=0.0, demand_mw_triad_3=0.0,
    )
    assert exp.demand_mw_triad_1 == pytest.approx(1.2)


def test_exposure_class_default_high():
    exp = CustomerTriadExposure(
        account_id="ACC-MF", season=SEASON,
        demand_mw_triad_1=0.5, demand_mw_triad_2=0.5, demand_mw_triad_3=0.5,
    )
    assert exp.exposure_class == CustomerExposureClass.HIGH


def test_triad_season_has_9_members():
    assert len(list(TriadSeason)) == 9


def test_customer_exposure_class_has_3_members():
    assert len(list(CustomerExposureClass)) == 3
