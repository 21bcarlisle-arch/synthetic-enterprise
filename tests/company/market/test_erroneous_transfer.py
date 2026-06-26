from __future__ import annotations

import dataclasses
import datetime
import pytest

from company.market.erroneous_transfer import (
    ETClaim,
    ETResolutionType,
    ETStatus,
    ErroneousTransferRegister,
)

MONDAY = datetime.date(2022, 1, 3)


def make_claim(claim_id="ET-001", status=ETStatus.OPEN, claim_date=MONDAY):
    return ETClaim(
        claim_id=claim_id,
        mpan="1012345678900",
        affected_account_id="C1",
        claim_date=claim_date,
        original_supplier="OldEnergy Ltd",
        gaining_supplier="NewEnergy Ltd",
        status=status,
    )


class TestETClaim:
    def test_frozen(self):
        claim = make_claim()
        try:
            claim.status = ETStatus.INVESTIGATING
            pytest.fail("Expected FrozenInstanceError")
        except (dataclasses.FrozenInstanceError, AttributeError, TypeError):
            pass

    def test_working_days_open_skips_weekends(self):
        claim = make_claim(claim_date=MONDAY)
        as_of = datetime.date(2022, 1, 10)
        assert claim.working_days_open(as_of) == 5

    def test_working_days_open_same_day(self):
        claim = make_claim(claim_date=MONDAY)
        assert claim.working_days_open(MONDAY) == 0

    def test_is_overdue_false_at_exactly_20_days(self):
        claim = make_claim(claim_date=MONDAY)
        as_of = datetime.date(2022, 1, 31)
        assert claim.working_days_open(as_of) == 20
        assert not claim.is_overdue(as_of)

    def test_is_overdue_true_at_21_days(self):
        claim = make_claim(claim_date=MONDAY)
        as_of = datetime.date(2022, 2, 1)
        assert claim.working_days_open(as_of) == 21
        assert claim.is_overdue(as_of)

    def test_compensation_gbp_when_overdue_and_open(self):
        claim = make_claim(status=ETStatus.OPEN)
        overdue_date = datetime.date(2022, 2, 1)
        assert claim.compensation_gbp(overdue_date) == 30.0

    def test_compensation_gbp_zero_when_resolved(self):
        claim = make_claim(status=ETStatus.RESOLVED_CORRECTED)
        overdue_date = datetime.date(2022, 2, 1)
        assert claim.compensation_gbp(overdue_date) == 0.0

    def test_compensation_gbp_zero_when_not_yet_overdue(self):
        claim = make_claim(status=ETStatus.OPEN)
        early_date = datetime.date(2022, 1, 10)
        assert claim.compensation_gbp(early_date) == 0.0


class TestErroneousTransferRegister:
    def test_raise_claim_appears_in_open_claims(self):
        reg = ErroneousTransferRegister()
        claim = make_claim()
        reg.raise_claim(claim)
        assert len(reg.open_claims()) == 1
        assert reg.open_claims()[0].claim_id == "ET-001"

    def test_update_status_transitions_correctly(self):
        reg = ErroneousTransferRegister()
        reg.raise_claim(make_claim(claim_id="ET-002"))
        reg.update_status("ET-002", ETStatus.INVESTIGATING)
        updated = next(c for c in reg._claims if c.claim_id == "ET-002")
        assert updated.status == ETStatus.INVESTIGATING

    def test_resolve_claim_returned_gives_resolved_corrected(self):
        reg = ErroneousTransferRegister()
        reg.raise_claim(make_claim(claim_id="ET-003"))
        reg.resolve_claim(
            "ET-003",
            datetime.date(2022, 1, 20),
            ETResolutionType.RETURNED_TO_ORIGINAL,
        )
        resolved = next(c for c in reg._claims if c.claim_id == "ET-003")
        assert resolved.status == ETStatus.RESOLVED_CORRECTED
        assert resolved.resolution_type == ETResolutionType.RETURNED_TO_ORIGINAL

    def test_resolve_claim_accepted_gives_resolved_accepted(self):
        reg = ErroneousTransferRegister()
        reg.raise_claim(make_claim(claim_id="ET-004"))
        reg.resolve_claim(
            "ET-004",
            datetime.date(2022, 1, 20),
            ETResolutionType.CUSTOMER_ACCEPTED_GAIN,
        )
        resolved = next(c for c in reg._claims if c.claim_id == "ET-004")
        assert resolved.status == ETStatus.RESOLVED_ACCEPTED

    def test_overdue_claims_filtered(self):
        reg = ErroneousTransferRegister()
        reg.raise_claim(make_claim(claim_id="ET-005", claim_date=MONDAY))
        reg.raise_claim(make_claim(claim_id="ET-006", claim_date=datetime.date(2022, 1, 28)))
        overdue_date = datetime.date(2022, 2, 1)
        overdue = reg.overdue_claims(overdue_date)
        assert len(overdue) == 1
        assert overdue[0].claim_id == "ET-005"

    def test_et_rate_pct(self):
        reg = ErroneousTransferRegister()
        reg.raise_claim(make_claim(claim_id="ET-R1"))
        reg.raise_claim(make_claim(claim_id="ET-R2"))
        assert reg.et_rate_pct(400) == 0.5

    def test_et_rate_zero_when_no_switches(self):
        reg = ErroneousTransferRegister()
        assert reg.et_rate_pct(0) == 0.0

    def test_compensation_outstanding_gbp(self):
        reg = ErroneousTransferRegister()
        reg.raise_claim(make_claim(claim_id="ET-A", claim_date=MONDAY))
        reg.raise_claim(make_claim(claim_id="ET-B", claim_date=MONDAY))
        overdue_date = datetime.date(2022, 2, 1)
        assert reg.compensation_outstanding_gbp(overdue_date) == 60.0

    def test_claims_by_status_covers_all_statuses(self):
        reg = ErroneousTransferRegister()
        reg.raise_claim(make_claim())
        by_status = reg.claims_by_status()
        assert set(by_status.keys()) == {s.value for s in ETStatus}
        assert by_status["open"] == 1
        assert by_status["resolved_corrected"] == 0

    def test_et_summary_keys_and_above_threshold(self):
        reg = ErroneousTransferRegister()
        for i in range(3):
            reg.raise_claim(make_claim(claim_id="ET-" + str(i)))
        summary = reg.et_summary(datetime.date(2022, 1, 10), total_switches=100)
        required_keys = {
            "total_claims", "open_claims", "overdue_claims",
            "resolved_corrected", "resolved_accepted",
            "et_rate_pct", "compensation_outstanding_gbp", "above_threshold",
        }
        assert required_keys.issubset(summary.keys())
        assert summary["above_threshold"] is True
        assert summary["total_claims"] == 3

    def test_resolved_claim_excluded_from_open_claims(self):
        reg = ErroneousTransferRegister()
        reg.raise_claim(make_claim(claim_id="ET-X"))
        reg.resolve_claim(
            "ET-X",
            datetime.date(2022, 1, 15),
            ETResolutionType.RETURNED_TO_ORIGINAL,
        )
        assert len(reg.open_claims()) == 0