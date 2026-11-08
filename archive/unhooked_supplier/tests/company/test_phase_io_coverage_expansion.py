"""Phase IO: deeper coverage for reporting_calendar, metering_contracts, solr_exposure."""
import datetime as dt
import pytest

# ===== reporting_calendar =====
from company.regulatory.reporting_calendar import (
    RegulatoryCalendar, ReportingFrequency, DeadlineStatus
)


def _calendar():
    cal = RegulatoryCalendar()
    cal.add_deadline("D001", "Ofgem Supply Return", "Ofgem",
                      ReportingFrequency.ANNUAL, dt.date(2023,3,31))
    cal.add_deadline("D002", "BSC SVA Report", "Elexon",
                      ReportingFrequency.QUARTERLY, dt.date(2023,1,15))
    cal.add_deadline("D003", "Monthly KPI", "Ofgem",
                      ReportingFrequency.MONTHLY, dt.date(2023,12,31))
    return cal


class TestRegulatoryCalendar:
    def test_pending_when_before_due(self):
        cal = _calendar()
        d = cal._deadlines[0]
        assert d.status(dt.date(2023,1,1)) == DeadlineStatus.PENDING

    def test_overdue_when_past_due(self):
        cal = _calendar()
        d = cal._deadlines[1]  # due 2023-01-15
        assert d.status(dt.date(2023,3,1)) == DeadlineStatus.OVERDUE

    def test_submitted_status(self):
        cal = _calendar()
        cal.mark_submitted("D001", dt.date(2023,2,28))
        d = next(x for x in cal._deadlines if x.deadline_id == "D001")
        assert d.status(dt.date(2023,4,1)) == DeadlineStatus.SUBMITTED

    def test_is_submitted_property(self):
        cal = _calendar()
        cal.mark_submitted("D001", dt.date(2023,2,28))
        d = next(x for x in cal._deadlines if x.deadline_id == "D001")
        assert d.is_submitted

    def test_days_until_due(self):
        cal = _calendar()
        d = cal._deadlines[0]  # due 2023-03-31
        days = d.days_until_due(dt.date(2023,3,1))
        assert days == 30

    def test_overdue_filter(self):
        cal = _calendar()
        overdue = cal.overdue(dt.date(2023,6,1))
        ids = [d.deadline_id for d in overdue]
        assert "D001" in ids and "D002" in ids

    def test_due_within_14_days(self):
        cal = _calendar()
        # D002 was due 2023-01-15; as_of 2023-01-10 → 5 days left
        due = cal.due_within_days(dt.date(2023,1,10), 14)
        assert any(d.deadline_id == "D002" for d in due)

    def test_by_regulator(self):
        cal = _calendar()
        ofgem = cal.by_regulator("Ofgem")
        assert len(ofgem) == 2

    def test_calendar_summary_keys(self):
        cal = _calendar()
        s = cal.calendar_summary(dt.date(2023,6,1))
        assert "overdue" in s and "pending" in s and "submitted" in s

    def test_mark_submitted_updates_deadline(self):
        cal = _calendar()
        updated = cal.mark_submitted("D002", dt.date(2023,1,10))
        assert updated.submitted_date == dt.date(2023,1,10)


# ===== metering_contracts =====
from company.market.metering_contracts import (
    MeteringContractManager, MeteringServiceType, MeterType, ServiceCallType
)


def _manager():
    mgr = MeteringContractManager()
    mgr.register_contract("MOPco", MeteringServiceType.MOP, MeterType.SMART,
                           "M001", dt.date(2022,1,1))
    mgr.register_contract("DCco", MeteringServiceType.DC, MeterType.HH,
                           "M002", dt.date(2022,3,1), dt.date(2023,2,28))
    return mgr


class TestMeteringContracts:
    def test_annual_cost_mop_smart(self):
        mgr = _manager()
        assert mgr._contracts[0].annual_cost_gbp == pytest.approx(28.0)

    def test_annual_cost_dc_hh(self):
        mgr = _manager()
        assert mgr._contracts[1].annual_cost_gbp == pytest.approx(30.0)

    def test_is_active_within_dates(self):
        mgr = _manager()
        assert mgr._contracts[1].is_active(dt.date(2022,6,1))

    def test_is_not_active_after_end(self):
        mgr = _manager()
        assert not mgr._contracts[1].is_active(dt.date(2023,6,1))

    def test_cost_for_period_gbp(self):
        mgr = _manager()
        # 30 days = 28/365 * 30
        cost = mgr._contracts[0].cost_for_period_gbp(dt.date(2022,1,1), dt.date(2022,1,30))
        assert cost == pytest.approx(28.0/365*29, abs=0.1)

    def test_log_service_call_id_format(self):
        mgr = _manager()
        sc = mgr.log_service_call("M001", ServiceCallType.METER_READ,
                                    dt.date(2022,6,1), 15.0)
        assert sc.call_id == "SC-0001"

    def test_active_contracts_filter_by_type(self):
        mgr = _manager()
        mop_only = mgr.active_contracts(dt.date(2022,6,1), MeteringServiceType.MOP)
        assert len(mop_only) == 1

    def test_service_call_cost_gbp(self):
        mgr = _manager()
        mgr.log_service_call("M001", ServiceCallType.SMART_COMMISSIONING,
                              dt.date(2022,6,1), 50.0)
        mgr.log_service_call("M002", ServiceCallType.FAULT_REPAIR,
                              dt.date(2022,7,1), 80.0)
        assert mgr.service_call_cost_gbp(2022) == pytest.approx(130.0)

    def test_metering_summary_keys(self):
        mgr = _manager()
        s = mgr.metering_summary(2022)
        assert "active_contracts" in s and "annual_contract_cost_gbp" in s

    def test_annual_contract_cost_all_active(self):
        mgr = _manager()
        # Both active at 2022-12-31
        cost = mgr.annual_contract_cost_gbp(2022)
        assert cost == pytest.approx(28.0 + 30.0)


# ===== solr_exposure =====
from company.regulatory.solr_exposure import (
    SoLRBook, SoLREvent, SoLRAcquisitionPrice,
    get_solr_levy_gbp_per_mwh, SoLREventStatus
)


def _book():
    b = SoLRBook()
    b.record_event("EV001", "Bulb Energy", dt.date(2021,11,22),
                    1_700_000, 3500.0, legacy_credit_gbp=300_000_000.0)
    b.record_event("EV002", "Green", dt.date(2021,9,1), 50_000, 3200.0)
    return b


class TestSoLRExposure:
    def test_levy_rate_known_year(self):
        assert get_solr_levy_gbp_per_mwh(2021) == pytest.approx(4.14)

    def test_levy_rate_2022_peak(self):
        assert get_solr_levy_gbp_per_mwh(2022) == pytest.approx(10.0)

    def test_total_annual_kwh(self):
        b = _book()
        ev = b.get("EV001")
        assert ev.total_annual_kwh == pytest.approx(1_700_000 * 3500.0)

    def test_total_annual_mwh(self):
        b = _book()
        ev = b.get("EV001")
        assert ev.total_annual_mwh == pytest.approx(ev.total_annual_kwh / 1000)

    def test_levy_cost_gbp(self):
        b = _book()
        ev = b.get("EV002")
        rate = get_solr_levy_gbp_per_mwh(2021)
        expected = round(50_000 * 3200.0 / 1000 * rate, 2)
        assert ev.levy_cost_gbp(2021) == pytest.approx(expected)

    def test_is_above_svt(self):
        price = SoLRAcquisitionPrice("EV001", 28.5, 28.0, 5.0)
        assert price.is_above_svt

    def test_complete_transfer_changes_status(self):
        b = _book()
        b.complete_transfer("EV001", dt.date(2021,12,1), "Our Supplier")
        ev = b.get("EV001")
        assert ev.status == SoLREventStatus.CUSTOMERS_TRANSFERRED

    def test_annual_levy_cost_gbp(self):
        b = _book()
        ev1 = b.get("EV001")
        ev2 = b.get("EV002")
        expected = round(ev1.levy_cost_gbp(2021) + ev2.levy_cost_gbp(2021), 2)
        assert b.annual_levy_cost_gbp(2021) == pytest.approx(expected)

    def test_total_legacy_credit_gbp(self):
        b = _book()
        assert b.total_legacy_credit_gbp() == pytest.approx(300_000_000.0)

    def test_events_summary_keys(self):
        b = _book()
        s = b.events_summary(2021)
        assert "events_count" in s and "annual_levy_gbp" in s
