"""Phase CF: TPI Commission Book tests."""
import pytest
from company.market.tpi_commission_book import (
    TPICommissionBook, TPITier, CommissionType, TPIAgreement, TPIPayment
)


def _book():
    return TPICommissionBook()


def _ic_book():
    b = _book()
    # Register a national TPI for C_IC1
    b.register_tpi(
        "TPI001", "Make It Cheaper", TPITier.NATIONAL,
        CommissionType.HYBRID, upfront_gbp=500, trail_gbp_per_mwh=2.5,
        is_disclosed=True, customer_id="C_IC1", contract_start_year=2018,
    )
    # Record payments
    b.record_payment("PAY001", "TPI001", "C_IC1", 2018, CommissionType.UPFRONT, 500, annual_kwh=500000)
    b.record_payment("PAY002", "TPI001", "C_IC1", 2019, CommissionType.TRAIL, 1250, annual_kwh=500000)
    b.record_payment("PAY003", "TPI001", "C_IC1", 2020, CommissionType.TRAIL, 1250, annual_kwh=500000)
    return b


# 1. register_tpi returns TPIAgreement
def test_register_tpi_returns_agreement():
    b = _book()
    a = b.register_tpi("T1", "Acme", TPITier.REGIONAL, CommissionType.UPFRONT, upfront_gbp=200)
    assert a.tpi_id == "T1"
    assert a.upfront_gbp == 200


# 2. Non-disclosed agreement is non-compliant
def test_non_disclosed_non_compliant():
    b = _book()
    a = b.register_tpi("T1", "Acme", TPITier.REGIONAL, CommissionType.UPFRONT,
                        upfront_gbp=200, is_disclosed=False)
    assert not a.is_compliant


# 3. Disclosed agreement is compliant
def test_disclosed_is_compliant():
    b = _book()
    a = b.register_tpi("T1", "Acme", TPITier.REGIONAL, CommissionType.UPFRONT,
                        upfront_gbp=200, is_disclosed=True)
    assert a.is_compliant


# 4. non_compliant_agreements returns undisclosed TPIs
def test_non_compliant_list():
    b = _book()
    b.register_tpi("T1", "Acme", TPITier.REGIONAL, CommissionType.UPFRONT, is_disclosed=False)
    b.register_tpi("T2", "Beta", TPITier.ONLINE, CommissionType.TRAIL, is_disclosed=True)
    assert len(b.non_compliant_agreements) == 1
    assert b.non_compliant_agreements[0].tpi_id == "T1"


# 5. record_payment returns TPIPayment
def test_record_payment():
    b = _book()
    p = b.record_payment("PAY001", "TPI001", "C_IC1", 2018, CommissionType.UPFRONT, 500)
    assert p.amount_gbp == 500
    assert p.payment_year == 2018


# 6. rate_gbp_per_mwh correct
def test_rate_gbp_per_mwh():
    b = _book()
    p = b.record_payment("PAY001", "TPI001", "C_IC1", 2019, CommissionType.TRAIL, 1250, annual_kwh=500000)
    # rate = 1250 / (500000/1000) = 1250/500 = 2.5 GBP/MWh
    assert abs(p.rate_gbp_per_mwh - 2.5) < 0.01


# 7. payments_for_year filters correctly
def test_payments_for_year():
    b = _ic_book()
    yr2019 = b.payments_for_year(2019)
    assert len(yr2019) == 1
    assert yr2019[0].payment_year == 2019


# 8. payments_for_customer filters by customer
def test_payments_for_customer():
    b = _ic_book()
    cic1 = b.payments_for_customer("C_IC1")
    assert len(cic1) == 3


# 9. total_commission_gbp sums all payments
def test_total_commission():
    b = _ic_book()
    assert abs(b.total_commission_gbp() - 3000) < 1  # 500 + 1250 + 1250


# 10. total_for_year sums year-specific payments
def test_total_for_year():
    b = _ic_book()
    assert abs(b.total_for_year(2018) - 500) < 1  # only upfront in 2018
    assert abs(b.total_for_year(2019) - 1250) < 1  # trail in 2019


# 11. avg_rate_gbp_per_mwh over trail payments
def test_avg_trail_rate():
    b = _ic_book()
    # Trail payments: 2019 (1250 at 2.5/MWh), 2020 (1250 at 2.5/MWh)
    avg = b.avg_rate_gbp_per_mwh()
    assert abs(avg - 2.5) < 0.01


# 12. tpi_summary contains key fields
def test_tpi_summary():
    b = _ic_book()
    summary = b.tpi_summary()
    assert "TPI Commission" in summary
    assert "Total" in summary
    assert "Non-disclosed" in summary


# --- Phase LY depth tests ---

def test_tpi_id_stored():
    book = _book()
    book.register_tpi('TPI-LY', 'LY Agency', TPITier.REGIONAL, CommissionType.UPFRONT)
    agr = book.all_agreements[0]
    assert agr.tpi_id == 'TPI-LY'


def test_tpi_name_stored():
    book = _book()
    book.register_tpi('TPI-LY', 'LY Agency', TPITier.INDEPENDENT, CommissionType.UPFRONT)
    agr = book.all_agreements[0]
    assert agr.tpi_name == 'LY Agency'


def test_tier_stored():
    book = _book()
    book.register_tpi('TPI-LY', 'LY Agency', TPITier.ONLINE, CommissionType.UPFRONT)
    agr = book.all_agreements[0]
    assert agr.tier == TPITier.ONLINE


def test_commission_type_stored():
    book = _book()
    book.register_tpi('TPI-LY', 'LY Agency', TPITier.NATIONAL, CommissionType.TRAIL)
    agr = book.all_agreements[0]
    assert agr.commission_type == CommissionType.TRAIL


def test_upfront_gbp_default_zero():
    book = _book()
    book.register_tpi('TPI-LY', 'LY Agency', TPITier.NATIONAL, CommissionType.UPFRONT)
    agr = book.all_agreements[0]
    assert agr.upfront_gbp == pytest.approx(0.0)


def test_trail_gbp_per_mwh_default_zero():
    book = _book()
    book.register_tpi('TPI-LY', 'LY Agency', TPITier.NATIONAL, CommissionType.TRAIL)
    agr = book.all_agreements[0]
    assert agr.trail_gbp_per_mwh == pytest.approx(0.0)


def test_is_disclosed_default_false():
    book = _book()
    book.register_tpi('TPI-LY', 'LY Agency', TPITier.NATIONAL, CommissionType.UPFRONT)
    agr = book.all_agreements[0]
    assert agr.is_disclosed_to_customer is False


def test_is_compliant_false_when_not_disclosed():
    book = _book()
    book.register_tpi('TPI-LY', 'LY Agency', TPITier.NATIONAL, CommissionType.UPFRONT)
    agr = book.all_agreements[0]
    assert agr.is_compliant is False


def test_customer_id_default_none():
    book = _book()
    book.register_tpi('TPI-LY', 'LY Agency', TPITier.NATIONAL, CommissionType.UPFRONT)
    agr = book.all_agreements[0]
    assert agr.customer_id is None


def test_contract_start_year_default_none():
    book = _book()
    book.register_tpi('TPI-LY', 'LY Agency', TPITier.NATIONAL, CommissionType.UPFRONT)
    agr = book.all_agreements[0]
    assert agr.contract_start_year is None
