"""Phase OB tests: Elexon BSC settlement reconciliation cash flow exposure."""
import pytest

from company.regulatory.settlement_reconciliation import (
    ReconciliationExposure,
    build_reconciliation_series,
    largest_exposure_year,
    _blended_variance,
    _rag,
    _HH_RECON_VARIANCE,
    _NON_HH_RECON_VARIANCE,
    _GREEN_THRESHOLD,
    _AMBER_THRESHOLD,
)


# ── blended variance ──────────────────────────────────────────────────────────

class TestBlendedVariance:
    def test_pure_hh_portfolio(self):
        v = _blended_variance(1.0)
        assert v == pytest.approx(_HH_RECON_VARIANCE, rel=1e-6)

    def test_pure_non_hh_portfolio(self):
        v = _blended_variance(0.0)
        assert v == pytest.approx(_NON_HH_RECON_VARIANCE, rel=1e-6)

    def test_90_pct_hh_blended(self):
        v = _blended_variance(0.90)
        expected = 0.90 * _HH_RECON_VARIANCE + 0.10 * _NON_HH_RECON_VARIANCE
        assert v == pytest.approx(expected, rel=1e-6)

    def test_variance_is_between_hh_and_non_hh(self):
        for frac in [0.0, 0.3, 0.6, 0.9, 1.0]:
            v = _blended_variance(frac)
            assert _HH_RECON_VARIANCE <= v <= _NON_HH_RECON_VARIANCE


# ── rag thresholds ────────────────────────────────────────────────────────────

class TestRAGThresholds:
    def test_green_below_threshold(self):
        monthly_rev = 100_000.0
        max_adverse = monthly_rev * _GREEN_THRESHOLD / 100 * 0.9
        assert _rag(max_adverse, monthly_rev) == "GREEN"

    def test_amber_between_thresholds(self):
        monthly_rev = 100_000.0
        max_adverse = monthly_rev * (_GREEN_THRESHOLD + _AMBER_THRESHOLD) / 200
        assert _rag(max_adverse, monthly_rev) == "AMBER"

    def test_red_above_amber(self):
        monthly_rev = 100_000.0
        max_adverse = monthly_rev * _AMBER_THRESHOLD / 100 * 2.0
        assert _rag(max_adverse, monthly_rev) == "RED"

    def test_zero_monthly_revenue_is_green(self):
        assert _rag(999999.0, 0.0) == "GREEN"


# ── build series ──────────────────────────────────────────────────────────────

def _make_accounts(years_revenue: dict) -> dict:
    by_year = {yr: {"revenue_gbp": rev} for yr, rev in years_revenue.items()}
    return {"by_year": by_year}


class TestBuildReconciliationSeries:
    def test_empty_accounts_returns_empty(self):
        assert build_reconciliation_series({}) == []

    def test_series_length_matches_year_count(self):
        accts = _make_accounts({"2020": 600_000.0, "2021": 700_000.0, "2022": 900_000.0})
        series = build_reconciliation_series(accts)
        assert len(series) == 3

    def test_years_in_ascending_order(self):
        accts = _make_accounts({"2022": 900_000.0, "2020": 600_000.0, "2021": 700_000.0})
        series = build_reconciliation_series(accts)
        years = [r.year for r in series]
        assert years == sorted(years)

    def test_max_adverse_proportional_to_revenue(self):
        accts = _make_accounts({"2020": 600_000.0, "2021": 1_200_000.0})
        series = build_reconciliation_series(accts, hh_revenue_fraction=0.9)
        r2020 = next(r for r in series if r.year == 2020)
        r2021 = next(r for r in series if r.year == 2021)
        assert r2021.max_adverse_gbp == pytest.approx(2 * r2020.max_adverse_gbp, rel=1e-3)

    def test_crisis_years_flagged(self):
        accts = _make_accounts({"2021": 700_000.0, "2022": 900_000.0, "2023": 600_000.0})
        series = build_reconciliation_series(accts)
        for r in series:
            if r.year in {2021, 2022}:
                assert r.is_crisis_year
            else:
                assert not r.is_crisis_year

    def test_hh_dominated_portfolio_gives_low_variance(self):
        accts = _make_accounts({"2020": 1_000_000.0})
        s_hh = build_reconciliation_series(accts, hh_revenue_fraction=1.0)
        s_non = build_reconciliation_series(accts, hh_revenue_fraction=0.0)
        assert s_hh[0].max_adverse_gbp < s_non[0].max_adverse_gbp

    def test_rag_is_green_for_hh_dominated(self):
        accts = _make_accounts({"2020": 600_000.0})
        series = build_reconciliation_series(accts, hh_revenue_fraction=0.90)
        assert series[0].rag == "GREEN"

    def test_outstanding_pool_less_than_annual_revenue(self):
        accts = _make_accounts({"2020": 600_000.0})
        series = build_reconciliation_series(accts)
        assert series[0].outstanding_pool_gbp < 600_000.0

    def test_zero_revenue_year_excluded(self):
        accts = _make_accounts({"2020": 0.0, "2021": 600_000.0})
        series = build_reconciliation_series(accts)
        assert all(r.year != 2020 for r in series)

    def test_expected_adjustment_less_than_max_adverse(self):
        accts = _make_accounts({"2020": 600_000.0})
        series = build_reconciliation_series(accts)
        assert series[0].expected_adjustment_gbp < series[0].max_adverse_gbp


# ── largest exposure year ─────────────────────────────────────────────────────

class TestLargestExposureYear:
    def test_returns_none_for_empty_series(self):
        assert largest_exposure_year([]) is None

    def test_returns_year_with_highest_adverse(self):
        accts = _make_accounts({"2020": 600_000.0, "2022": 900_000.0, "2023": 400_000.0})
        series = build_reconciliation_series(accts)
        largest = largest_exposure_year(series)
        assert largest.year == 2022


# ── board section ─────────────────────────────────────────────────────────────

class TestSettlementReconciliationBoardSection:
    def _data(self, years=None):
        if years is None:
            years = {str(yr): 600_000.0 + yr * 10_000 for yr in range(2016, 2026)}
        ma = {}
        for yr_str, rev in years.items():
            ma[yr_str] = {"income_statement": {"revenue_gbp": rev}}
        return {"management_accounts": ma}

    def _section(self, data):
        from saas.reporting.annual_report import _section_settlement_reconciliation
        return _section_settlement_reconciliation(data)

    def test_returns_string_with_data(self):
        out = self._section(self._data())
        assert isinstance(out, str) and len(out) > 0

    def test_silent_when_no_management_accounts(self):
        out = self._section({})
        assert out == ""

    def test_phase_ob_header_present(self):
        out = self._section(self._data())
        assert "Phase OB" in out

    def test_all_years_present(self):
        out = self._section(self._data())
        for yr in range(2016, 2026):
            assert str(yr) in out

    def test_crisis_year_flagged(self):
        out = self._section(self._data())
        assert "CREDIT EXPECTED" in out
