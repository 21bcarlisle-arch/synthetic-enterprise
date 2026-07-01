import datetime as dt
import pytest
from company.crm.eep_book import EEPMeasure, EEPScheme, EEPInstallation, EEPBook


def _book():
    book = EEPBook()
    book.record('C001', '1200011111', EEPMeasure.LOFT_INSULATION, EEPScheme.ECO4,
                dt.date(2022, 9, 15), estimated_annual_saving_gbp=180.0,
                cost_gbp=1500.0, subsidy_gbp=1500.0)
    book.record('C002', '1200022222', EEPMeasure.HEAT_PUMP, EEPScheme.BUS,
                dt.date(2022, 11, 1), estimated_annual_saving_gbp=600.0,
                cost_gbp=14_000.0, subsidy_gbp=7_500.0)
    book.record('C003', '1200033333', EEPMeasure.SOLAR_PV, EEPScheme.SEG,
                dt.date(2021, 5, 20), estimated_annual_saving_gbp=350.0,
                cost_gbp=6_000.0, subsidy_gbp=0.0)
    return book


def test_customer_cost_zero_for_full_subsidy():
    book = _book()
    inst = book.installs_for_customer('C001')[0]
    assert inst.customer_cost_gbp == pytest.approx(0.0)


def test_simple_payback_years():
    book = _book()
    inst = book.installs_for_customer('C002')[0]
    assert inst.simple_payback_years == pytest.approx(6500 / 600, rel=0.01)


def test_installs_for_customer():
    book = _book()
    assert len(book.installs_for_customer('C002')) == 1


def test_total_subsidy_eco4():
    book = _book()
    assert book.total_subsidy_gbp(scheme=EEPScheme.ECO4) == pytest.approx(1500.0)


def test_estimated_savings_portfolio():
    book = _book()
    total = book.estimated_savings_portfolio_gbp(year=2022)
    assert total == pytest.approx(180.0 + 600.0)


def test_annual_summary_keys():
    book = _book()
    s = book.annual_summary(2022)
    assert s['installations'] == 2
    assert 'by_measure' in s
    assert 'total_subsidy_gbp' in s
    assert 'estimated_savings_gbp' in s


def test_solar_self_funded_payback():
    book = _book()
    inst = book.installs_for_customer('C003')[0]
    assert inst.customer_cost_gbp == pytest.approx(6000.0)
    assert inst.simple_payback_years == pytest.approx(6000 / 350, rel=0.01)


# --- Phase KC depth tests ---

def test_installation_id_format():
    book = EEPBook()
    inst = book.record('C001', '1200011111', EEPMeasure.LOFT_INSULATION, EEPScheme.ECO4,
                       dt.date(2022, 9, 15), 180.0, 1500.0, 1500.0)
    assert inst.installation_id == 'EEP-00001'


def test_installation_id_sequential():
    book = EEPBook()
    i1 = book.record('C001', '1200011111', EEPMeasure.LOFT_INSULATION, EEPScheme.ECO4,
                     dt.date(2022, 9, 15), 180.0, 1500.0, 1500.0)
    i2 = book.record('C002', '1200022222', EEPMeasure.HEAT_PUMP, EEPScheme.BUS,
                     dt.date(2022, 11, 1), 600.0, 14_000.0, 7_500.0)
    assert i1.installation_id == 'EEP-00001'
    assert i2.installation_id == 'EEP-00002'


def test_payback_none_when_zero_saving():
    book = EEPBook()
    inst = book.record('C001', '1200011111', EEPMeasure.SMART_CONTROLS, EEPScheme.SELF_FUNDED,
                       dt.date(2022, 6, 1), 0.0, 500.0, 0.0)
    assert inst.simple_payback_years is None


def test_payback_zero_when_zero_customer_cost():
    book = EEPBook()
    inst = book.record('C001', '1200011111', EEPMeasure.LOFT_INSULATION, EEPScheme.ECO4,
                       dt.date(2022, 9, 15), 180.0, 1500.0, 1500.0)
    assert inst.simple_payback_years == pytest.approx(0.0)


def test_total_subsidy_no_filter():
    book = _book()
    # 1500 + 7500 + 0 = 9000
    assert book.total_subsidy_gbp() == pytest.approx(9000.0)


def test_total_subsidy_year_filter():
    book = _book()
    # C003 is 2021; C001 + C002 are 2022
    assert book.total_subsidy_gbp(year=2021) == pytest.approx(0.0)
    assert book.total_subsidy_gbp(year=2022) == pytest.approx(9000.0)


def test_annual_summary_empty_year():
    book = _book()
    s = book.annual_summary(2099)
    assert s['installations'] == 0
    assert s['total_subsidy_gbp'] == pytest.approx(0.0)


def test_measure_stored():
    book = _book()
    inst = book.installs_for_customer('C001')[0]
    assert inst.measure == EEPMeasure.LOFT_INSULATION


def test_scheme_stored():
    book = _book()
    inst = book.installs_for_customer('C002')[0]
    assert inst.scheme == EEPScheme.BUS


def test_installs_unknown_customer_empty():
    book = _book()
    assert book.installs_for_customer('UNKNOWN') == []
