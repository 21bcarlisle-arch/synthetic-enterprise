import pytest
from company.regulatory.fit_book import (
    FITBook, FITInstallation, FITPayment, FITTechnology,
    _GENERATION_RATE_P_PER_KWH, FIT_SCHEME_END_DATE
)


def _install(iid="FIT001", account="C1", tech=FITTechnology.SOLAR_PV, kw=3.5, date="2015-06-01"):
    return FITInstallation(
        installation_id=iid, account_id=account, technology=tech,
        capacity_kw=kw, accreditation_date=date, tariff_group="E"
    )


def _payment(iid="FIT001", quarter="2018-Q1", gen=750.0, exp=200.0):
    return FITPayment(
        installation_id=iid, quarter=quarter,
        generation_kwh=gen, export_kwh=exp,
        generation_rate_p=_GENERATION_RATE_P_PER_KWH.get(quarter[:4], 4.0),
        export_rate_p=5.24,
    )


def test_is_active_before_end():
    i = _install(date="2015-06-01")
    assert i.is_active is True


def test_is_active_after_end():
    i = _install(date="2020-01-01")
    assert i.is_active is False


def test_generation_payment():
    p = _payment(gen=1000.0)
    rate = _GENERATION_RATE_P_PER_KWH["2018"]
    expected = round(1000.0 * rate / 100, 2)
    assert abs(p.generation_payment_gbp - expected) < 0.01


def test_total_payment():
    p = _payment(gen=1000.0, exp=300.0)
    assert p.total_payment_gbp == round(p.generation_payment_gbp + p.export_payment_gbp, 2)


def test_register_and_count():
    book = FITBook()
    book.register_installation(_install())
    book.register_installation(_install(iid="FIT002", tech=FITTechnology.WIND))
    assert book.installations_count() == 2
    assert book.installations_count(FITTechnology.SOLAR_PV) == 1
    assert book.installations_count(FITTechnology.WIND) == 1


def test_record_payment_and_total():
    book = FITBook()
    book.register_installation(_install())
    book.record_payment(_payment(quarter="2018-Q1"))
    book.record_payment(_payment(quarter="2018-Q2"))
    assert book.total_paid_gbp(2018) > 0


def test_payments_for_installation():
    book = FITBook()
    book.record_payment(_payment(iid="FIT001"))
    book.record_payment(_payment(iid="FIT002"))
    book.record_payment(_payment(iid="FIT001", quarter="2018-Q2"))
    assert len(book.payments_for_installation("FIT001")) == 2


def test_levelisation_charge():
    book = FITBook()
    charge = book.levelisation_charge_gbp(2017, 50000.0)
    assert charge > 0


def test_levelisation_zero_after_2020():
    book = FITBook()
    assert book.levelisation_charge_gbp(2020, 50000.0) == 0.0


def test_fit_summary_keys():
    book = FITBook()
    book.register_installation(_install())
    s = book.fit_summary()
    for k in ("installations", "total_paid_gbp", "solar_pv_count", "scheme_end_date"):
        assert k in s


def test_fit_summary_empty():
    book = FITBook()
    s = book.fit_summary()
    assert s["installations"] == 0
    assert s["total_paid_gbp"] == 0.0
