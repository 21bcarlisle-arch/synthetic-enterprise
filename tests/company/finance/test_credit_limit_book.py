import pytest
from company.finance.credit_limit_book import (
    CreditLimitBook, CreditLimit, ExposureRecord, CounterpartyType
)


def _limit(cid="BARCLAYS", ctype=CounterpartyType.BANK, gbp=5_000_000.0,
           date="2022-01-01", by="credit_committee"):
    return CreditLimit(counterparty_id=cid, counterparty_type=ctype,
                       limit_gbp=gbp, approved_date=date, approved_by=by)


def _exp(cid="BARCLAYS", date="2022-09-01", mtm=1_000_000.0, pfe=200_000.0):
    return ExposureRecord(counterparty_id=cid, as_of_date=date,
                          current_mtm_gbp=mtm, potential_future_exposure_gbp=pfe)


def test_total_exposure_gbp():
    e = _exp(mtm=1_000_000.0, pfe=200_000.0)
    assert abs(e.total_exposure_gbp - 1_200_000.0) < 0.01


def test_is_stress_exposure():
    e = _exp(mtm=500_000.0, pfe=1_100_000.0)
    assert e.is_stress_exposure is True


def test_not_stress_exposure():
    e = _exp(mtm=1_000_000.0, pfe=100_000.0)
    assert e.is_stress_exposure is False


def test_is_material_limit():
    lim = _limit(gbp=2_000_000.0)
    assert lim.is_material is True


def test_not_material_limit():
    lim = _limit(gbp=500_000.0)
    assert lim.is_material is False


def test_set_and_get_limit():
    book = CreditLimitBook()
    book.set_limit(_limit())
    assert book.get_limit("BARCLAYS") is not None
    assert book.get_limit("UNKNOWN") is None


def test_utilisation_pct():
    book = CreditLimitBook()
    book.set_limit(_limit(gbp=5_000_000.0))
    book.record_exposure(_exp(mtm=3_000_000.0, pfe=500_000.0))
    util = book.utilisation_pct("BARCLAYS")
    assert abs(util - 70.0) < 0.01


def test_is_breach():
    book = CreditLimitBook()
    book.set_limit(_limit(gbp=1_000_000.0))
    book.record_exposure(_exp(mtm=900_000.0, pfe=200_000.0))
    assert book.is_breach("BARCLAYS") is True


def test_not_breach():
    book = CreditLimitBook()
    book.set_limit(_limit(gbp=5_000_000.0))
    book.record_exposure(_exp(mtm=1_000_000.0, pfe=200_000.0))
    assert book.is_breach("BARCLAYS") is False


def test_latest_exposure_picks_most_recent():
    book = CreditLimitBook()
    book.record_exposure(_exp(date="2022-01-01", mtm=500_000.0))
    book.record_exposure(_exp(date="2022-09-01", mtm=900_000.0))
    latest = book.latest_exposure("BARCLAYS")
    assert latest.as_of_date == "2022-09-01"


def test_breaches_list():
    book = CreditLimitBook()
    book.set_limit(_limit(cid="A", gbp=1_000_000.0))
    book.set_limit(_limit(cid="B", gbp=5_000_000.0))
    book.record_exposure(_exp(cid="A", mtm=900_000.0, pfe=200_000.0))
    book.record_exposure(_exp(cid="B", mtm=1_000_000.0, pfe=200_000.0))
    assert book.breaches() == ["A"]


def test_limit_summary_keys():
    book = CreditLimitBook()
    book.set_limit(_limit())
    book.record_exposure(_exp())
    s = book.limit_summary()
    for k in ("counterparty_count", "total_limit_gbp", "total_exposure_gbp",
               "portfolio_utilisation_pct", "breach_count", "material_limits"):
        assert k in s
