"""Tests for Phase GC: Energy Price Guarantee Reconciliation Register."""
import datetime as dt
import pytest
from company.regulatory.epg_reconciliation_register import (
    EPGClaimStatus,
    EPGMonthlyRecord,
    EPGReconciliationRegister,
    _EPG_START,
    _EPG_END,
    _is_epg_period,
    _EPG_ELEC_UNIT_PENCE,
    _EPG_GAS_UNIT_PENCE,
)

# ── helpers ──────────────────────────────────────────────────────────────────

OCT22 = dt.date(2022, 10, 1)   # first EPG month
JUN23 = dt.date(2023, 6, 1)   # last EPG month
SEP22 = dt.date(2022, 9, 1)   # before EPG
JUL23 = dt.date(2023, 7, 1)   # after EPG


def make_record(
    billing_month=OCT22,
    elec_kwh=10_000.0,
    gas_kwh=15_000.0,
    elec_pence=45.0,   # actual cost above EPG cap
    gas_pence=15.0,    # above EPG cap
    accounts=1000,
    status=EPGClaimStatus.DRAFT,
):
    return EPGMonthlyRecord(
        record_id="EPG-00001",
        billing_month=billing_month,
        elec_kwh_billed=elec_kwh,
        gas_kwh_billed=gas_kwh,
        elec_actual_pence_per_kwh=elec_pence,
        gas_actual_pence_per_kwh=gas_pence,
        domestic_account_count=accounts,
        claim_status=status,
    )


# ── _is_epg_period ───────────────────────────────────────────────────────────

class TestIsEPGPeriod:

    def test_start_of_epg_is_eligible(self):
        assert _is_epg_period(OCT22)

    def test_end_of_epg_is_eligible(self):
        assert _is_epg_period(JUN23)

    def test_before_epg_not_eligible(self):
        assert not _is_epg_period(SEP22)

    def test_after_epg_not_eligible(self):
        assert not _is_epg_period(JUL23)


# ── EPGMonthlyRecord ─────────────────────────────────────────────────────────

class TestEPGMonthlyRecord:

    def test_is_eligible_in_period(self):
        r = make_record(OCT22)
        assert r.is_eligible

    def test_not_eligible_outside_period(self):
        r = make_record(SEP22)
        assert not r.is_eligible  # billing_month check only; record can exist

    def test_elec_epg_revenue_uses_cap_rate(self):
        r = make_record(elec_kwh=10_000.0, elec_pence=45.0)
        expected = 10_000.0 * _EPG_ELEC_UNIT_PENCE / 100.0
        assert abs(r.elec_epg_revenue_gbp - expected) < 1e-6

    def test_gas_epg_revenue_uses_cap_rate(self):
        r = make_record(gas_kwh=15_000.0, gas_pence=15.0)
        expected = 15_000.0 * _EPG_GAS_UNIT_PENCE / 100.0
        assert abs(r.gas_epg_revenue_gbp - expected) < 1e-6

    def test_elec_subsidy_is_positive_when_actual_above_epg(self):
        r = make_record(elec_pence=45.0)  # 45p vs 34p EPG cap
        assert r.elec_subsidy_gbp > 0

    def test_gas_subsidy_is_positive_when_actual_above_epg(self):
        r = make_record(gas_pence=15.0)  # 15p vs 10.3p EPG cap
        assert r.gas_subsidy_gbp > 0

    def test_subsidy_is_zero_when_actual_below_epg(self):
        r = make_record(elec_pence=20.0, gas_pence=5.0)  # below EPG cap
        assert r.elec_subsidy_gbp == 0.0
        assert r.gas_subsidy_gbp == 0.0

    def test_total_subsidy_sums_fuels(self):
        r = make_record(elec_pence=45.0, gas_pence=15.0)
        assert abs(r.total_subsidy_gbp - r.elec_subsidy_gbp - r.gas_subsidy_gbp) < 1e-9

    def test_is_settled(self):
        r = make_record(status=EPGClaimStatus.SETTLED)
        assert r.is_settled

    def test_not_settled_when_draft(self):
        r = make_record(status=EPGClaimStatus.DRAFT)
        assert not r.is_settled

    def test_record_summary_contains_month_and_subsidy(self):
        r = make_record()
        s = r.record_summary()
        assert "2022-10" in s and "EPG-00001" in s

    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.elec_kwh_billed = 0.0


# ── EPGReconciliationRegister ────────────────────────────────────────────────

class TestEPGReconciliationRegister:

    def setup_method(self):
        self.reg = EPGReconciliationRegister()

    def test_record_month_stored(self):
        r = self.reg.record_month(OCT22, 10_000, 15_000, 45.0, 15.0, 1000)
        assert r.claim_status == EPGClaimStatus.DRAFT

    def test_record_month_auto_id(self):
        r1 = self.reg.record_month(OCT22, 10_000, 15_000, 45.0, 15.0, 1000)
        r2 = self.reg.record_month(dt.date(2022, 11, 1), 10_000, 15_000, 45.0, 15.0, 1000)
        assert r1.record_id != r2.record_id

    def test_record_month_outside_period_raises(self):
        with pytest.raises(ValueError):
            self.reg.record_month(SEP22, 10_000, 15_000, 45.0, 15.0, 1000)

    def test_record_month_after_period_raises(self):
        with pytest.raises(ValueError):
            self.reg.record_month(JUL23, 10_000, 15_000, 45.0, 15.0, 1000)

    def test_submit_claim(self):
        r = self.reg.record_month(OCT22, 10_000, 15_000, 45.0, 15.0, 1000)
        sub = self.reg.submit_claim(r.record_id)
        assert sub.claim_status == EPGClaimStatus.SUBMITTED

    def test_mark_approved(self):
        r = self.reg.record_month(OCT22, 10_000, 15_000, 45.0, 15.0, 1000)
        approved = self.reg.mark_approved(r.record_id)
        assert approved.claim_status == EPGClaimStatus.APPROVED

    def test_mark_settled(self):
        r = self.reg.record_month(OCT22, 10_000, 15_000, 45.0, 15.0, 1000)
        settled = self.reg.mark_settled(r.record_id)
        assert settled.is_settled

    def test_mark_disputed(self):
        r = self.reg.record_month(OCT22, 10_000, 15_000, 45.0, 15.0, 1000)
        disp = self.reg.mark_disputed(r.record_id)
        assert disp.claim_status == EPGClaimStatus.DISPUTED

    def test_update_missing_raises(self):
        with pytest.raises(KeyError):
            self.reg.mark_settled("EPG-99999")

    def test_records_for_month(self):
        self.reg.record_month(OCT22, 10_000, 15_000, 45.0, 15.0, 1000)
        self.reg.record_month(dt.date(2022, 11, 1), 10_000, 15_000, 45.0, 15.0, 1000)
        assert len(self.reg.records_for_month(OCT22)) == 1

    def test_unsettled_records(self):
        r1 = self.reg.record_month(OCT22, 10_000, 15_000, 45.0, 15.0, 1000)
        r2 = self.reg.record_month(dt.date(2022, 11, 1), 10_000, 15_000, 45.0, 15.0, 1000)
        self.reg.mark_settled(r1.record_id)
        assert len(self.reg.unsettled_records()) == 1

    def test_disputed_records(self):
        r = self.reg.record_month(OCT22, 10_000, 15_000, 45.0, 15.0, 1000)
        self.reg.mark_disputed(r.record_id)
        assert len(self.reg.disputed_records()) == 1

    def test_total_subsidy_claimed_gbp(self):
        r1 = self.reg.record_month(OCT22, 10_000, 15_000, 45.0, 15.0, 1000)
        r2 = self.reg.record_month(dt.date(2022, 11, 1), 10_000, 15_000, 45.0, 15.0, 1000)
        total = self.reg.total_subsidy_claimed_gbp()
        assert total > 0
        assert abs(total - r1.total_subsidy_gbp - r2.total_subsidy_gbp) < 1e-6

    def test_total_subsidy_settled_gbp(self):
        r = self.reg.record_month(OCT22, 10_000, 15_000, 45.0, 15.0, 1000)
        assert self.reg.total_subsidy_settled_gbp() == 0.0
        self.reg.mark_settled(r.record_id)
        assert self.reg.total_subsidy_settled_gbp() > 0

    def test_outstanding_subsidy_excludes_settled_and_disputed(self):
        r1 = self.reg.record_month(OCT22, 10_000, 15_000, 45.0, 15.0, 1000)
        r2 = self.reg.record_month(dt.date(2022, 11, 1), 10_000, 15_000, 45.0, 15.0, 1000)
        r3 = self.reg.record_month(dt.date(2022, 12, 1), 10_000, 15_000, 45.0, 15.0, 1000)
        self.reg.mark_settled(r1.record_id)
        self.reg.mark_disputed(r2.record_id)
        # Only r3 is outstanding
        outstanding = self.reg.outstanding_subsidy_gbp()
        assert abs(outstanding - r3.total_subsidy_gbp) < 1e-6

    def test_epg_summary_string(self):
        r = self.reg.record_month(OCT22, 10_000, 15_000, 45.0, 15.0, 1000)
        self.reg.mark_settled(r.record_id)
        s = self.reg.epg_summary()
        assert "1 monthly records" in s and "1 settled" in s

    def test_empty_register_summary(self):
        s = self.reg.epg_summary()
        assert "0 monthly records" in s
