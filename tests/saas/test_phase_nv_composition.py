"""Tests for saas/reporting/portfolio_composition.py -- Phase NV."""

import pytest
from saas.reporting.portfolio_composition import (
    PortfolioComposition,
    build_composition_series,
    _dominant,
    _concentration_rag,
    _CONCENTRATION_RED,
    _CONCENTRATION_AMBER,
)


def _ss(resi=10_000, sme=5_000, ic=0):
    ss = {}
    if resi:
        ss["resi electricity"] = {"gross_gbp": resi * 0.7}
        ss["resi gas"] = {"gross_gbp": resi * 0.3}
    if sme:
        ss["SME electricity"] = {"gross_gbp": sme}
    if ic:
        ss["I&C electricity"] = {"gross_gbp": ic * 0.9}
        ss["I&C gas"] = {"gross_gbp": ic * 0.1}
    return ss


def _year(resi=10_000, sme=5_000, ic=0):
    return {
        "segment_split": _ss(resi, sme, ic),
        "commodity_split": {
            "electricity": {"gross_gbp": resi * 0.7 + sme + ic * 0.9},
            "gas": {"gross_gbp": resi * 0.3 + ic * 0.1},
        },
    }


def _run(*year_dicts):
    keys = [str(2020 + i) for i in range(len(year_dicts))]
    return {"years": dict(zip(keys, year_dicts))}


class TestDominant:
    def test_ic_wins_when_largest(self):
        assert _dominant(20.0, 10.0, 70.0) == "ic"

    def test_resi_wins_when_largest(self):
        assert _dominant(60.0, 30.0, 10.0) == "resi"

    def test_sme_wins_when_largest(self):
        assert _dominant(20.0, 60.0, 20.0) == "sme"


class TestConcentrationRag:
    def test_red_above_threshold(self):
        assert _concentration_rag(_CONCENTRATION_RED + 1) == "RED"

    def test_amber_above_amber_threshold(self):
        assert _concentration_rag(_CONCENTRATION_AMBER + 1) == "AMBER"

    def test_green_below_amber(self):
        assert _concentration_rag(_CONCENTRATION_AMBER - 1) == "GREEN"

    def test_exactly_at_red_threshold(self):
        assert _concentration_rag(_CONCENTRATION_RED) == "RED"


class TestBuildSeries:
    def test_resi_pct_correct(self):
        run = _run(_year(resi=100_000, sme=0, ic=0))
        s = build_composition_series(run)
        assert s[0].resi_gross_pct == pytest.approx(100.0)

    def test_ic_pct_correct(self):
        run = _run(_year(resi=0, sme=0, ic=100_000))
        s = build_composition_series(run)
        assert s[0].ic_gross_pct == pytest.approx(100.0)

    def test_ic_concentration_red(self):
        run = _run(_year(resi=1_000, sme=0, ic=100_000))
        s = build_composition_series(run)
        assert s[0].dominant_segment == "ic"
        assert s[0].concentration_rag == "RED"

    def test_balanced_portfolio_green(self):
        run = _run(_year(resi=40_000, sme=30_000, ic=30_000))
        s = build_composition_series(run)
        assert s[0].concentration_rag == "GREEN"

    def test_elec_pct_correct(self):
        run = _run(_year(resi=10_000, sme=0, ic=0))
        s = build_composition_series(run)
        assert s[0].elec_gross_pct == pytest.approx(70.0)
        assert s[0].gas_gross_pct == pytest.approx(30.0)

    def test_series_length_matches_years(self):
        run = _run(_year(), _year(), _year())
        s = build_composition_series(run)
        assert len(s) == 3

    def test_empty_returns_empty(self):
        assert build_composition_series({}) == []

    def test_year_field_correct(self):
        run = _run(_year())
        s = build_composition_series(run)
        assert s[0].year == 2020

    def test_total_gross_sums_segments(self):
        run = _run(_year(resi=10_000, sme=5_000, ic=0))
        s = build_composition_series(run)
        assert s[0].total_gross_gbp == pytest.approx(10_000 + 5_000)

    def test_zero_gross_no_crash(self):
        run = _run({"segment_split": {}, "commodity_split": {}})
        s = build_composition_series(run)
        assert s[0].resi_gross_pct == 0.0
        assert s[0].ic_gross_pct == 0.0
