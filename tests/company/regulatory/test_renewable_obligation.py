import pytest
from company.regulatory.renewable_obligation import (
    RenewableObligationBook, ROAnnualReturn, ROSettlementMethod,
    _BUYOUT_PRICE_GBP_PER_ROC, _OBLIGATION_LEVEL_ROC_PER_MWH
)


def _return(year=2022, mwh=10000.0, surrendered=None, purchased=0.0):
    level = _OBLIGATION_LEVEL_ROC_PER_MWH.get(year, 0.10)
    if surrendered is None:
        surrendered = mwh * level
    method = (ROSettlementMethod.SURRENDER_ROC if surrendered >= mwh * level
              else ROSettlementMethod.BUYOUT)
    return ROAnnualReturn(
        obligation_year=year, electricity_supplied_mwh=mwh,
        rocs_surrendered=surrendered, rocs_purchased=purchased,
        settlement_method=method,
    )


def test_obligation_rocs():
    r = _return(2022, mwh=10000.0)
    expected = 10000.0 * _OBLIGATION_LEVEL_ROC_PER_MWH[2022]
    assert abs(r.obligation_rocs - expected) < 0.01


def test_compliant_when_fully_surrendered():
    r = _return(2022, mwh=10000.0)
    assert r.is_compliant is True
    assert r.shortfall_rocs == 0.0


def test_shortfall_and_buyout():
    level = _OBLIGATION_LEVEL_ROC_PER_MWH[2022]
    r = ROAnnualReturn(
        obligation_year=2022, electricity_supplied_mwh=10000.0,
        rocs_surrendered=0.0, rocs_purchased=0.0,
        settlement_method=ROSettlementMethod.BUYOUT,
    )
    expected_shortfall = round(10000.0 * level, 2)
    assert abs(r.shortfall_rocs - expected_shortfall) < 0.01
    expected_buyout = round(expected_shortfall * _BUYOUT_PRICE_GBP_PER_ROC[2022], 2)
    assert abs(r.buyout_cost_gbp - expected_buyout) < 0.01
    assert r.is_compliant is False


def test_file_return_and_retrieve():
    book = RenewableObligationBook()
    r = _return(2022)
    book.file_return(r)
    assert book.return_for_year(2022) is r


def test_return_for_year_missing():
    book = RenewableObligationBook()
    assert book.return_for_year(2099) is None


def test_non_compliant_years():
    book = RenewableObligationBook()
    r_nc = ROAnnualReturn(
        obligation_year=2021, electricity_supplied_mwh=10000.0,
        rocs_surrendered=0.0, rocs_purchased=0.0,
        settlement_method=ROSettlementMethod.BUYOUT,
    )
    book.file_return(_return(2022))
    book.file_return(r_nc)
    nc = book.non_compliant_years()
    assert 2021 in nc
    assert 2022 not in nc


def test_compliance_record_sorted():
    book = RenewableObligationBook()
    book.file_return(_return(2023))
    book.file_return(_return(2021))
    rec = book.compliance_record()
    assert rec[0]["year"] == 2021
    assert rec[1]["year"] == 2023


def test_compliance_record_keys():
    book = RenewableObligationBook()
    book.file_return(_return(2022))
    r = book.compliance_record()[0]
    for k in ("year", "obligation_rocs", "surrendered_rocs", "shortfall_rocs",
               "buyout_cost_gbp", "total_ro_cost_gbp", "compliant"):
        assert k in r


def test_ro_summary_keys():
    book = RenewableObligationBook()
    book.file_return(_return(2022))
    s = book.ro_summary()
    for k in ("years_filed", "total_buyout_gbp", "non_compliant_years", "total_ro_cost_gbp"):
        assert k in s


def test_ro_summary_empty():
    book = RenewableObligationBook()
    s = book.ro_summary()
    assert s["years_filed"] == 0
    assert s["total_buyout_gbp"] == 0.0
