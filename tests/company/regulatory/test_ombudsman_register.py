"""Tests for Ombudsman Register (Phase FB)."""
import datetime as dt
import pytest
from company.regulatory.ombudsman_register import (
    OmbudsmanOutcome, OmbudsmanAwardType, OmbudsmanAward,
    OmbudsmanCase, OmbudsmanRegister,
    _FINAL_RESPONSE_TO_REFERRAL_WINDOW_DAYS, _HIGH_UPHOLD_RATE_PCT,
)

DATE_FR = dt.date(2024, 1, 1)   # final response
DATE_REF = dt.date(2024, 2, 1)  # referral to ombudsman
ACCT = "C1"


def make_case(case_ref="OSE-000001", outcome=OmbudsmanOutcome.PENDING,
              award=None, decided_at=None):
    return OmbudsmanCase(
        case_reference=case_ref,
        account_id=ACCT,
        original_ticket_id="TKT-000001",
        referred_at=DATE_REF,
        supplier_final_response_date=DATE_FR,
        outcome=outcome,
        decided_at=decided_at,
        award=award,
    )


class TestOmbudsmanCase:
    def test_is_in_window_true(self):
        c = make_case()
        assert c.is_in_window

    def test_is_in_window_false(self):
        c = OmbudsmanCase(
            "OSE-000001", ACCT, "TKT-000001",
            referred_at=DATE_FR + dt.timedelta(days=200),
            supplier_final_response_date=DATE_FR,
        )
        assert not c.is_in_window

    def test_is_pending(self):
        assert make_case().is_pending

    def test_is_upheld_upheld(self):
        c = make_case(outcome=OmbudsmanOutcome.UPHELD)
        assert c.is_upheld

    def test_is_upheld_partially(self):
        c = make_case(outcome=OmbudsmanOutcome.PARTIALLY_UPHELD)
        assert c.is_upheld

    def test_not_upheld_not_upheld(self):
        c = make_case(outcome=OmbudsmanOutcome.NOT_UPHELD)
        assert not c.is_upheld

    def test_financial_liability_gbp(self):
        award = OmbudsmanAward(OmbudsmanAwardType.FINANCIAL, financial_amount_gbp=250.0)
        c = make_case(outcome=OmbudsmanOutcome.UPHELD, award=award)
        assert c.financial_liability_gbp == pytest.approx(250.0)

    def test_financial_liability_zero_no_award(self):
        c = make_case(outcome=OmbudsmanOutcome.UPHELD)
        assert c.financial_liability_gbp == 0.0

    def test_case_summary(self):
        c = make_case()
        s = c.case_summary()
        assert "OSE-000001" in s


class TestOmbudsmanRegister:
    def test_register_case_auto_ref(self):
        reg = OmbudsmanRegister()
        c = reg.register_case(ACCT, "TKT-000001", DATE_REF, DATE_FR)
        assert c.case_reference == "OSE-000001"
        assert c.is_pending

    def test_record_decision_upheld(self):
        reg = OmbudsmanRegister()
        c = reg.register_case(ACCT, "TKT-000001", DATE_REF, DATE_FR)
        decided = reg.record_decision(
            c.case_reference, OmbudsmanOutcome.UPHELD, dt.date(2024, 4, 1)
        )
        assert decided.outcome == OmbudsmanOutcome.UPHELD

    def test_uphold_rate_pct(self):
        reg = OmbudsmanRegister()
        c1 = reg.register_case(ACCT, "TKT-000001", DATE_REF, DATE_FR)
        c2 = reg.register_case("C2", "TKT-000002", DATE_REF, DATE_FR)
        reg.record_decision(c1.case_reference, OmbudsmanOutcome.UPHELD, dt.date(2024, 4, 1))
        reg.record_decision(c2.case_reference, OmbudsmanOutcome.NOT_UPHELD, dt.date(2024, 4, 1))
        assert reg.uphold_rate_pct() == pytest.approx(50.0)

    def test_is_high_uphold_rate(self):
        reg = OmbudsmanRegister()
        c1 = reg.register_case(ACCT, "TKT-000001", DATE_REF, DATE_FR)
        reg.record_decision(c1.case_reference, OmbudsmanOutcome.UPHELD, dt.date(2024, 4, 1))
        assert reg.is_high_uphold_rate()

    def test_total_financial_awards(self):
        reg = OmbudsmanRegister()
        c = reg.register_case(ACCT, "TKT-000001", DATE_REF, DATE_FR)
        award = OmbudsmanAward(OmbudsmanAwardType.FINANCIAL, financial_amount_gbp=500.0)
        reg.record_decision(c.case_reference, OmbudsmanOutcome.UPHELD, dt.date(2024, 4, 1), award)
        assert reg.total_financial_awards_gbp() == pytest.approx(500.0)

    def test_ombudsman_summary(self):
        reg = OmbudsmanRegister()
        reg.register_case(ACCT, "TKT-000001", DATE_REF, DATE_FR)
        s = reg.ombudsman_summary()
        assert "Ombudsman Register" in s
