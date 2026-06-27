import datetime as dt
import pytest
from company.billing.dd_indemnity import (
    DDIndemnityClaim, DDIndemnityStatus, DDIndemnityReason, DDIndemnityRegister,
)


def make_claim(claim_id="C1", account_id="A1",
               receipt=dt.date(2023, 5, 1),
               payment=dt.date(2023, 4, 28),
               amount=85.0,
               reason=DDIndemnityReason.NOT_AUTHORISED,
               status=DDIndemnityStatus.RECEIVED,
               resolved=None, notes=""):
    return DDIndemnityClaim(
        claim_id=claim_id, account_id=account_id,
        receipt_date=receipt, payment_date=payment,
        claimed_amount_gbp=amount, reason=reason,
        status=status, resolution_date=resolved, resolution_notes=notes,
    )


class TestDDIndemnityClaim:
    def test_is_active_received(self):
        c = make_claim()
        assert c.is_active() is True

    def test_is_active_investigating(self):
        c = make_claim(status=DDIndemnityStatus.INVESTIGATING)
        assert c.is_active() is True

    def test_is_active_false_upheld(self):
        c = make_claim(status=DDIndemnityStatus.UPHELD)
        assert c.is_active() is False

    def test_is_active_false_rejected(self):
        c = make_claim(status=DDIndemnityStatus.REJECTED)
        assert c.is_active() is False

    def test_creates_debt_true_upheld(self):
        c = make_claim(status=DDIndemnityStatus.UPHELD)
        assert c.creates_debt() is True

    def test_creates_debt_false_active(self):
        c = make_claim()
        assert c.creates_debt() is False

    def test_investigation_overdue_false_resolved(self):
        c = make_claim(status=DDIndemnityStatus.UPHELD)
        assert c.is_investigation_overdue(dt.date(2023, 6, 1)) is False

    def test_investigation_overdue_false_within_10_days(self):
        c = make_claim(receipt=dt.date(2023, 5, 1))
        assert c.is_investigation_overdue(dt.date(2023, 5, 8)) is False

    def test_investigation_overdue_true_after_10_working_days(self):
        c = make_claim(receipt=dt.date(2023, 5, 1))
        assert c.is_investigation_overdue(dt.date(2023, 5, 16)) is True

    def test_frozen(self):
        c = make_claim()
        with pytest.raises((AttributeError, TypeError)):
            c.claimed_amount_gbp = 0


class TestDDIndemnityRegister:
    def test_receive_claim(self):
        reg = DDIndemnityRegister()
        reg.receive_claim(make_claim())
        assert len(reg.active_claims()) == 1

    def test_start_investigation(self):
        reg = DDIndemnityRegister()
        reg.receive_claim(make_claim(claim_id="C1"))
        result = reg.start_investigation("C1")
        assert result.status == DDIndemnityStatus.INVESTIGATING

    def test_uphold(self):
        reg = DDIndemnityRegister()
        reg.receive_claim(make_claim(claim_id="C1"))
        result = reg.uphold("C1", dt.date(2023, 5, 10), notes="accepted")
        assert result.status == DDIndemnityStatus.UPHELD
        assert result.resolution_date == dt.date(2023, 5, 10)

    def test_reject(self):
        reg = DDIndemnityRegister()
        reg.receive_claim(make_claim(claim_id="C1"))
        result = reg.reject("C1", dt.date(2023, 5, 10))
        assert result.status == DDIndemnityStatus.REJECTED

    def test_write_off(self):
        reg = DDIndemnityRegister()
        reg.receive_claim(make_claim(claim_id="C1"))
        result = reg.write_off("C1", dt.date(2023, 5, 10))
        assert result.status == DDIndemnityStatus.WRITTEN_OFF

    def test_active_excludes_upheld(self):
        reg = DDIndemnityRegister()
        reg.receive_claim(make_claim(claim_id="C1"))
        reg.receive_claim(make_claim(claim_id="C2"))
        reg.uphold("C1", dt.date(2023, 5, 10))
        assert len(reg.active_claims()) == 1

    def test_overdue_investigations(self):
        reg = DDIndemnityRegister()
        reg.receive_claim(make_claim(claim_id="C1", receipt=dt.date(2023, 5, 1)))
        assert len(reg.overdue_investigations(dt.date(2023, 5, 16))) == 1
        assert len(reg.overdue_investigations(dt.date(2023, 5, 8))) == 0

    def test_total_exposure(self):
        reg = DDIndemnityRegister()
        reg.receive_claim(make_claim(claim_id="C1", amount=85.0))
        reg.receive_claim(make_claim(claim_id="C2", amount=60.0))
        assert reg.total_exposure_gbp() == 145.0

    def test_total_exposure_excludes_resolved(self):
        reg = DDIndemnityRegister()
        reg.receive_claim(make_claim(claim_id="C1", amount=85.0))
        reg.uphold("C1", dt.date(2023, 5, 10))
        assert reg.total_exposure_gbp() == 0.0

    def test_total_upheld(self):
        reg = DDIndemnityRegister()
        reg.receive_claim(make_claim(claim_id="C1", amount=85.0))
        reg.uphold("C1", dt.date(2023, 5, 10))
        assert reg.total_upheld_gbp() == 85.0

    def test_claims_by_reason(self):
        reg = DDIndemnityRegister()
        reg.receive_claim(make_claim(claim_id="C1", reason=DDIndemnityReason.NOT_AUTHORISED))
        reg.receive_claim(make_claim(claim_id="C2", reason=DDIndemnityReason.AMOUNT_INCORRECT))
        assert len(reg.claims_by_reason(DDIndemnityReason.NOT_AUTHORISED)) == 1

    def test_update_raises_not_found(self):
        reg = DDIndemnityRegister()
        with pytest.raises(ValueError):
            reg.start_investigation("MISSING")

    def test_summary_keys(self):
        reg = DDIndemnityRegister()
        s = reg.dd_indemnity_summary()
        for k in ("total_claims", "active", "upheld", "rejected",
                  "total_exposure_gbp", "total_upheld_gbp"):
            assert k in s
