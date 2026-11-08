import pytest
from company.regulatory.remit_book import (
    REMITReportingBook, REMITReport, REMITProductType, REMITStatus
)


def _report(rid="R001", tid="T001", pt=REMITProductType.ELECTRICITY_FORWARD,
            tdate="2022-09-01", ddate="2022-10-01", vol=50.0, price=200.0, cpty="BARCLAYS"):
    return REMITReport(
        report_id=rid, trade_id=tid, product_type=pt,
        trade_date=tdate, delivery_date=ddate, volume_mwh=vol,
        price_gbp_per_mwh=price, counterparty=cpty,
    )


def test_notional_value_gbp():
    r = _report(vol=50.0, price=200.0)
    assert abs(r.notional_value_gbp - 10_000.0) < 0.01


def test_is_large_trade():
    big = _report(vol=100.0)
    small = _report(vol=50.0)
    assert big.is_large_trade is True
    assert small.is_large_trade is False


def test_initial_status_pending():
    r = _report()
    assert r.status == REMITStatus.PENDING
    assert r.is_submitted is False


def test_submit_report():
    book = REMITReportingBook()
    book.record_report(_report())
    submitted = book.submit_report("R001", "2022-09-02")
    assert submitted is not None
    assert submitted.status == REMITStatus.SUBMITTED
    assert submitted.submitted_date == "2022-09-02"


def test_acknowledge_report():
    book = REMITReportingBook()
    book.record_report(_report())
    book.submit_report("R001", "2022-09-02")
    acked = book.acknowledge_report("R001")
    assert acked is not None
    assert acked.status == REMITStatus.ACKNOWLEDGED


def test_pending_reports():
    book = REMITReportingBook()
    book.record_report(_report(rid="R001"))
    book.record_report(_report(rid="R002"))
    book.submit_report("R001", "2022-09-02")
    assert len(book.pending_reports()) == 1


def test_compliance_rate_all_submitted():
    book = REMITReportingBook()
    book.record_report(_report(rid="R001"))
    book.record_report(_report(rid="R002"))
    book.submit_report("R001", "2022-09-02")
    book.submit_report("R002", "2022-09-02")
    assert abs(book.compliance_rate() - 100.0) < 0.01


def test_compliance_rate_partial():
    book = REMITReportingBook()
    book.record_report(_report(rid="R001"))
    book.record_report(_report(rid="R002"))
    book.submit_report("R001", "2022-09-02")
    assert abs(book.compliance_rate() - 50.0) < 0.01


def test_reports_for_product():
    book = REMITReportingBook()
    book.record_report(_report(pt=REMITProductType.ELECTRICITY_FORWARD))
    book.record_report(_report(rid="R002", pt=REMITProductType.GAS_DAY_AHEAD))
    assert len(book.reports_for_product(REMITProductType.ELECTRICITY_FORWARD)) == 1


def test_remit_summary_keys():
    book = REMITReportingBook()
    book.record_report(_report())
    s = book.remit_summary()
    for k in ("total_reports", "pending", "compliance_rate_pct", "large_trades"):
        assert k in s


# --- Phase LE depth tests ---

def test_report_id_stored():
    r = _report(rid='R_LE')
    assert r.report_id == 'R_LE'


def test_trade_id_stored():
    r = _report(tid='T_LE')
    assert r.trade_id == 'T_LE'


def test_product_type_stored():
    r = _report(pt=REMITProductType.GAS_FORWARD)
    assert r.product_type == REMITProductType.GAS_FORWARD


def test_volume_stored():
    r = _report(vol=200.0)
    assert r.volume_mwh == pytest.approx(200.0)


def test_price_stored():
    r = _report(price=150.0)
    assert r.price_gbp_per_mwh == pytest.approx(150.0)


def test_counterparty_stored():
    r = _report(cpty='HSBC_ENERGY')
    assert r.counterparty == 'HSBC_ENERGY'


def test_status_default_pending():
    r = _report()
    assert r.status == REMITStatus.PENDING


def test_is_submitted_false_when_pending():
    r = _report()
    assert r.is_submitted is False


def test_notional_zero_zero_volume():
    r = _report(vol=0.0)
    assert r.notional_value_gbp == pytest.approx(0.0)


def test_is_large_trade_false_below_100():
    r = _report(vol=50.0)
    assert r.is_large_trade is False
