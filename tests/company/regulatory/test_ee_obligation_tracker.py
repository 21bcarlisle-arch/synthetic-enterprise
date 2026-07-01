import datetime as dt
import pytest
from company.regulatory.ee_obligation_tracker import (
    EEScheme, MeasureType, ReferralStatus, EEReferral, EEObligationTracker
)


def test_refer_and_status():
    tracker = EEObligationTracker()
    ref = tracker.refer('R001', 'C001', EEScheme.ECO4, MeasureType.LOFT_INSULATION,
                         dt.date(2022, 3, 1))
    assert ref.status == ReferralStatus.REFERRED
    assert not ref.is_completed


def test_typical_savings():
    tracker = EEObligationTracker()
    ref = tracker.refer('R002', 'C001', EEScheme.ECO4, MeasureType.HEAT_PUMP,
                         dt.date(2022, 3, 1))
    assert ref.typical_annual_saving_kwh == pytest.approx(3000.0)


def test_install_completes():
    tracker = EEObligationTracker()
    ref = tracker.refer('R003', 'C001', EEScheme.GBIS, MeasureType.CAVITY_WALL,
                         dt.date(2022, 4, 1))
    ref.install(dt.date(2022, 6, 15), 'Green Homes Ltd', cost_gbp=2000.0)
    assert ref.is_completed
    assert ref.cost_gbp == pytest.approx(2000.0)


def test_completed_measures_by_year():
    tracker = EEObligationTracker()
    ref = tracker.refer('R004', 'C002', EEScheme.ECO4, MeasureType.SOLID_WALL,
                         dt.date(2022, 1, 1))
    ref.install(dt.date(2022, 9, 1), 'Eco Solutions')
    assert len(tracker.completed_measures(2022)) == 1
    assert len(tracker.completed_measures(2021)) == 0


def test_obligation_mwh_delivered():
    tracker = EEObligationTracker()
    ref = tracker.refer('R005', 'C003', EEScheme.ECO4, MeasureType.CAVITY_WALL,
                         dt.date(2022, 2, 1))
    ref.install(dt.date(2022, 8, 1), 'Installer A')
    mwh = tracker.obligation_mwh_delivered(EEScheme.ECO4, 2022)
    assert mwh == pytest.approx(0.8, rel=0.01)


def test_total_savings_kwh():
    tracker = EEObligationTracker()
    r1 = tracker.refer('R006', 'C004', EEScheme.BUS, MeasureType.SOLAR_PV,
                        dt.date(2022, 5, 1))
    r2 = tracker.refer('R007', 'C005', EEScheme.BUS, MeasureType.LOFT_INSULATION,
                        dt.date(2022, 5, 1))
    r1.install(dt.date(2022, 7, 1), 'Solar Co')
    r2.install(dt.date(2022, 7, 15), 'Eco Co')
    total = tracker.total_savings_kwh(2022)
    assert total == pytest.approx(1800.0 + 600.0)


def test_vulnerable_customer_count():
    tracker = EEObligationTracker()
    tracker.refer('R008', 'C006', EEScheme.WHD, MeasureType.SMART_HEATING,
                   dt.date(2022, 1, 1), is_vulnerable=True)
    tracker.refer('R009', 'C007', EEScheme.WHD, MeasureType.GLAZING,
                   dt.date(2022, 2, 1), is_vulnerable=False)
    assert tracker.vulnerable_customer_count(EEScheme.WHD) == 1


def test_portfolio_summary():
    tracker = EEObligationTracker()
    ref = tracker.refer('R010', 'C008', EEScheme.HUG2, MeasureType.BOILER_UPGRADE,
                         dt.date(2022, 3, 1))
    ref.install(dt.date(2022, 10, 1), 'Boiler Co')
    s = tracker.portfolio_summary(2022)
    assert s['total_referrals'] == 1
    assert s['completed'] == 1
    assert 'hug2' in s['by_scheme']


# --- Phase KR depth tests ---

def test_referral_id_stored():
    tracker = EEObligationTracker()
    ref = tracker.refer('R_ID', 'C001', EEScheme.ECO4, MeasureType.LOFT_INSULATION, dt.date(2022,1,1))
    assert ref.referral_id == 'R_ID'


def test_customer_id_stored():
    tracker = EEObligationTracker()
    ref = tracker.refer('R_CID', 'CUST_99', EEScheme.ECO4, MeasureType.CAVITY_WALL, dt.date(2022,1,1))
    assert ref.customer_id == 'CUST_99'


def test_scheme_stored():
    tracker = EEObligationTracker()
    ref = tracker.refer('R_SCH', 'C001', EEScheme.GBIS, MeasureType.LOFT_INSULATION, dt.date(2022,1,1))
    assert ref.scheme == EEScheme.GBIS


def test_measure_type_stored():
    tracker = EEObligationTracker()
    ref = tracker.refer('R_MT', 'C001', EEScheme.ECO4, MeasureType.HEAT_PUMP, dt.date(2022,1,1))
    assert ref.measure_type == MeasureType.HEAT_PUMP


def test_referral_date_stored():
    tracker = EEObligationTracker()
    ref = tracker.refer('R_DT', 'C001', EEScheme.ECO4, MeasureType.SOLID_WALL, dt.date(2022,5,15))
    assert ref.referral_date == dt.date(2022, 5, 15)


def test_not_vulnerable_by_default():
    tracker = EEObligationTracker()
    ref = tracker.refer('R_NV', 'C001', EEScheme.WHD, MeasureType.GLAZING, dt.date(2022,1,1))
    assert ref.is_vulnerable is False


def test_cost_stored_after_install():
    tracker = EEObligationTracker()
    ref = tracker.refer('R_CST', 'C001', EEScheme.ECO4, MeasureType.CAVITY_WALL, dt.date(2022,1,1))
    ref.install(dt.date(2022,6,1), 'Green Co', cost_gbp=1800.0)
    assert ref.cost_gbp == pytest.approx(1800.0)


def test_installer_name_stored():
    tracker = EEObligationTracker()
    ref = tracker.refer('R_INS', 'C001', EEScheme.GBIS, MeasureType.LOFT_INSULATION, dt.date(2022,1,1))
    ref.install(dt.date(2022,7,1), 'EcoSolutions Ltd')
    assert ref.installer_name == 'EcoSolutions Ltd'


def test_completed_measures_empty_year():
    tracker = EEObligationTracker()
    assert tracker.completed_measures(2099) == []


def test_total_savings_zero_no_installs():
    tracker = EEObligationTracker()
    tracker.refer('R_TS', 'C001', EEScheme.ECO4, MeasureType.LOFT_INSULATION, dt.date(2022,1,1))
    assert tracker.total_savings_kwh(2022) == pytest.approx(0.0)
