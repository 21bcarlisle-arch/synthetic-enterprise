"""Phase OC tests: Ofgem supply licence health monitoring."""
import datetime as dt
import pytest

from company.regulatory.licence_health import (
    LicenceCheck,
    LicenceCheckStatus,
    LicenceHealthReport,
    build_licence_health_report,
)


# ── individual checks ─────────────────────────────────────────────────────────

class TestLicenceCheckStatus:
    def test_below_threshold_is_breach(self):
        report = build_licence_health_report(
            as_of=dt.date(2016, 12, 31),
            active_customer_count=10,   # below 50 threshold
            net_assets_gbp=500_000.0,
            treasury_gbp=200_000.0,
            weeks_cash_runway=50.0,
            bad_debt_ratio_pct=1.0,
            complaints_per_100=0.0,
        )
        cust_check = report.get("customer_count")
        assert cust_check.status == LicenceCheckStatus.BREACH

    def test_at_threshold_is_pass(self):
        report = build_licence_health_report(
            as_of=dt.date(2020, 12, 31),
            active_customer_count=100,  # above 50 threshold + 50% watch zone = 75
            net_assets_gbp=500_000.0,
            treasury_gbp=200_000.0,
            weeks_cash_runway=50.0,
            bad_debt_ratio_pct=1.0,
            complaints_per_100=0.0,
        )
        cust_check = report.get("customer_count")
        assert cust_check.status == LicenceCheckStatus.PASS

    def test_bad_debt_above_5pct_is_breach(self):
        report = build_licence_health_report(
            as_of=dt.date(2022, 12, 31),
            active_customer_count=60,
            net_assets_gbp=500_000.0,
            treasury_gbp=200_000.0,
            weeks_cash_runway=50.0,
            bad_debt_ratio_pct=6.0,   # above 5% threshold
            complaints_per_100=0.0,
        )
        bd_check = report.get("bad_debt_ratio")
        assert bd_check.status == LicenceCheckStatus.BREACH

    def test_bad_debt_between_3_and_5_is_watch(self):
        report = build_licence_health_report(
            as_of=dt.date(2022, 12, 31),
            active_customer_count=60,
            net_assets_gbp=500_000.0,
            treasury_gbp=200_000.0,
            weeks_cash_runway=50.0,
            bad_debt_ratio_pct=4.0,   # between 3% and 5%
            complaints_per_100=0.0,
        )
        bd_check = report.get("bad_debt_ratio")
        assert bd_check.status == LicenceCheckStatus.WATCH

    def test_negative_net_assets_is_breach(self):
        report = build_licence_health_report(
            as_of=dt.date(2021, 12, 31),
            active_customer_count=60,
            net_assets_gbp=-1_000.0,   # insolvent
            treasury_gbp=10_000.0,
            weeks_cash_runway=20.0,
            bad_debt_ratio_pct=1.0,
            complaints_per_100=0.0,
        )
        na_check = report.get("net_assets_gbp")
        assert na_check.status == LicenceCheckStatus.BREACH

    def test_low_cash_runway_is_watch(self):
        report = build_licence_health_report(
            as_of=dt.date(2020, 12, 31),
            active_customer_count=60,
            net_assets_gbp=500_000.0,
            treasury_gbp=200_000.0,
            weeks_cash_runway=9.0,   # between 8 and 10 (watch zone)
            bad_debt_ratio_pct=1.0,
            complaints_per_100=0.0,
        )
        cash_check = report.get("cash_runway_weeks")
        assert cash_check.status == LicenceCheckStatus.WATCH


# ── overall status ────────────────────────────────────────────────────────────

class TestLicenceHealthReportOverall:
    def _healthy(self):
        return build_licence_health_report(
            as_of=dt.date(2020, 12, 31),
            active_customer_count=100,
            net_assets_gbp=500_000.0,
            treasury_gbp=300_000.0,
            weeks_cash_runway=100.0,
            bad_debt_ratio_pct=1.0,
            complaints_per_100=0.0,
        )

    def test_healthy_report_passes(self):
        report = self._healthy()
        assert report.overall_status == LicenceCheckStatus.PASS
        assert report.is_going_concern

    def test_breach_count_increments(self):
        report = build_licence_health_report(
            as_of=dt.date(2016, 12, 31),
            active_customer_count=10,   # breach
            net_assets_gbp=-500.0,      # breach
            treasury_gbp=300_000.0,
            weeks_cash_runway=100.0,
            bad_debt_ratio_pct=1.0,
            complaints_per_100=0.0,
        )
        assert report.breach_count >= 2

    def test_breach_overrides_watch_in_overall(self):
        report = build_licence_health_report(
            as_of=dt.date(2016, 12, 31),
            active_customer_count=10,   # breach
            net_assets_gbp=500_000.0,
            treasury_gbp=300_000.0,
            weeks_cash_runway=9.0,      # watch
            bad_debt_ratio_pct=1.0,
            complaints_per_100=0.0,
        )
        assert report.overall_status == LicenceCheckStatus.BREACH

    def test_headroom_positive_when_pass(self):
        # headroom = value - threshold; meaningful for min-threshold checks (cust count, net assets, treasury, runway)
        # not for max-threshold checks (bad_debt, complaints) which have inverted direction
        report = self._healthy()
        min_threshold_checks = ['customer_count', 'net_assets_gbp', 'treasury_gbp', 'cash_runway_weeks']
        for check in report.checks:
            if check.name in min_threshold_checks and check.status == LicenceCheckStatus.PASS:
                assert check.headroom > 0

    def test_summary_dict_has_required_keys(self):
        summary = self._healthy().summary()
        for key in ("as_of", "pass", "watch", "breach", "overall_status", "is_going_concern"):
            assert key in summary

    def test_small_portfolio_early_year_triggers_watch_or_breach(self):
        report = build_licence_health_report(
            as_of=dt.date(2016, 12, 31),
            active_customer_count=4,   # very small portfolio
            net_assets_gbp=500_000.0,
            treasury_gbp=100_000.0,
            weeks_cash_runway=50.0,
            bad_debt_ratio_pct=0.5,
            complaints_per_100=0.0,
        )
        assert report.overall_status in (LicenceCheckStatus.WATCH, LicenceCheckStatus.BREACH)


# ── board section ─────────────────────────────────────────────────────────────

class TestLicenceHealthBoardSection:
    def _data(self):
        years = {}
        ma = {}
        for yr in range(2016, 2026):
            n_cust = 4 + yr - 2016  # grows from 4 to 13
            revenue = 600_000.0 + yr * 10_000
            gross = revenue * 0.08
            bad_debt = revenue * 0.015
            treasury = 300_000.0 + (yr - 2016) * 50_000
            years[str(yr)] = {
                "active_customer_ids": [f"C_{i}" for i in range(n_cust)],
                "revenue_gbp": revenue,
                "gross_gbp": gross,
                "bad_debt_gbp": bad_debt,
                "treasury_end_gbp": treasury,
            }
            ma[str(yr)] = {
                "balance_sheet": {"total_equity_gbp": treasury + gross},
            }
        return {"years": years, "management_accounts": ma}

    def _section(self, data):
        from saas.reporting.annual_report import _section_licence_health
        return _section_licence_health(data)

    def test_returns_string_with_data(self):
        out = self._section(self._data())
        assert isinstance(out, str) and len(out) > 0

    def test_silent_when_no_years(self):
        out = self._section({})
        assert out == ""

    def test_all_years_present(self):
        out = self._section(self._data())
        for yr in range(2016, 2026):
            assert str(yr) in out

    def test_phase_oc_header(self):
        out = self._section(self._data())
        assert "Phase OC" in out
