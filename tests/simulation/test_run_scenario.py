"""Tests for the Phase 36a scenario integration runner."""
from datetime import date, timedelta

import pytest

from simulation.run_scenario import _expand_daily_to_hh, build_extended_price_feeds


def _daily_records(start_date: str, end_date: str, price: float = 50.0) -> list[dict]:
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    records = []
    d = start
    while d <= end:
        records.append({"settlementDate": d.isoformat(), "systemSellPrice": price})
        d += timedelta(days=1)
    return records


def _hh_records(start_date: str, end_date: str, price: float = 50.0) -> list[dict]:
    """Half-hourly records (48 periods per day)."""
    daily = _daily_records(start_date, end_date, price)
    hh = []
    for r in daily:
        for period in range(1, 49):
            hh.append({
                "settlementDate": r["settlementDate"],
                "settlementPeriod": period,
                "systemSellPrice": price,
            })
    return hh


def test_expand_daily_to_hh_count():
    daily = _daily_records("2027-01-01", "2027-01-03")
    hh = _expand_daily_to_hh(daily)
    assert len(hh) == 3 * 48


def test_expand_daily_to_hh_all_periods_present():
    daily = _daily_records("2027-06-01", "2027-06-01")
    hh = _expand_daily_to_hh(daily)
    periods = sorted(r["settlementPeriod"] for r in hh)
    assert periods == list(range(1, 49))


def test_expand_daily_to_hh_daily_mean_preserved():
    """The expansion now applies a MEAN-PRESERVING intraday shape (SPIKE_TAIL_SSP_RESIDUAL fix): the 48
    periods carry a within-day profile, but the day's MEAN SSP equals the daily generator price (the
    daily-generator calibration is untouched — R12/R13)."""
    from statistics import fmean
    daily = _daily_records("2027-01-01", "2027-01-01", price=123.45)
    hh = _expand_daily_to_hh(daily)
    # abs=1e-3 accommodates the per-period 4dp rounding residual across 48 periods; the shape is
    # mean-preserving by construction (see test_forward_intraday_shape for the population-level check).
    assert fmean(r["systemSellPrice"] for r in hh) == pytest.approx(123.45, abs=1e-3)


def test_expand_daily_to_hh_date_preserved():
    daily = _daily_records("2027-03-15", "2027-03-15")
    hh = _expand_daily_to_hh(daily)
    assert all(r["settlementDate"] == "2027-03-15" for r in hh)


def test_build_extended_price_feeds_extends_elec():
    hist_elec = _hh_records("2016-01-01", "2025-12-31")
    hist_gas = _daily_records("2016-01-01", "2025-12-31")
    ext_elec, ext_gas = build_extended_price_feeds(
        hist_elec, hist_gas,
        scenario="central_2027", year_from=2026, year_to=2027,
        seed="test",
    )
    assert len(ext_elec) > len(hist_elec)
    # Extended electricity should have 2026+2027 = 730 or 731 days × 48 periods appended
    appended = len(ext_elec) - len(hist_elec)
    assert appended == (365 + 365) * 48  # 2026 and 2027 are not leap years


def test_build_extended_price_feeds_extends_gas():
    hist_elec = _hh_records("2016-01-01", "2025-12-31")
    hist_gas = _daily_records("2016-01-01", "2025-12-31")
    ext_elec, ext_gas = build_extended_price_feeds(
        hist_elec, hist_gas,
        scenario="central_2027", year_from=2026, year_to=2027,
        seed="test",
    )
    assert len(ext_gas) > len(hist_gas)
    appended_gas = len(ext_gas) - len(hist_gas)
    assert appended_gas == 365 + 365  # daily gas records


def test_build_extended_no_date_overlap():
    hist_elec = _hh_records("2016-01-01", "2025-12-31")
    hist_gas = _daily_records("2016-01-01", "2025-12-31")
    ext_elec, ext_gas = build_extended_price_feeds(
        hist_elec, hist_gas,
        scenario="central_2027", year_from=2026, year_to=2027,
        seed="test",
    )
    elec_dates = sorted(set(r["settlementDate"] for r in ext_elec))
    assert elec_dates == sorted(set(elec_dates))  # no duplication
    # Scenario electricity starts 2026-01-01 — not in historical
    scenario_dates = [d for d in elec_dates if d >= "2026-01-01"]
    assert scenario_dates[0] == "2026-01-01"


def test_build_extended_deterministic():
    hist_elec = _hh_records("2016-01-01", "2025-06-30")
    hist_gas = _daily_records("2016-01-01", "2025-06-30")
    a_elec, a_gas = build_extended_price_feeds(hist_elec, hist_gas, "central_2027", 2026, 2027, "s1")
    b_elec, b_gas = build_extended_price_feeds(hist_elec, hist_gas, "central_2027", 2026, 2027, "s1")
    assert a_elec == b_elec
    assert a_gas == b_gas


def test_build_extended_returns_unmodified_when_no_extension_needed():
    """When year_from > year_to (impossible range), historical records returned unchanged."""
    hist_elec = _hh_records("2016-01-01", "2025-12-31")
    hist_gas = _daily_records("2016-01-01", "2025-12-31")
    ext_elec, ext_gas = build_extended_price_feeds(
        hist_elec, hist_gas,
        scenario="central_2027", year_from=2030, year_to=2025,  # year_from > year_to → no-op
        seed="noop",
    )
    assert ext_elec == hist_elec
    assert ext_gas == hist_gas


def test_build_extended_tags_data_regime_on_every_record():
    """W1_2 L1->L2 / epistemic-wall rule (.claude/rules/epistemic-wall-sim.md): every record in the
    extended feed must carry a data_regime tag -- an untagged record makes real and synthetic
    structurally indistinguishable once concatenated (the exact gap the FRAME names)."""
    hist_elec = _hh_records("2016-01-01", "2025-12-31")
    hist_gas = _daily_records("2016-01-01", "2025-12-31")
    ext_elec, ext_gas = build_extended_price_feeds(
        hist_elec, hist_gas, scenario="central_2027", year_from=2026, year_to=2027, seed="test")
    assert all(r.get("data_regime") in ("historical", "synthetic") for r in ext_elec)
    assert all(r.get("data_regime") in ("historical", "synthetic") for r in ext_gas)


def test_build_extended_data_regime_matches_origin():
    """Provenance must be CORRECT, not merely present: historical-dated records read 'historical',
    scenario-dated records read 'synthetic'. A synthetic record reading 'historical' would be a
    wall-provenance leak -- the exact thing this tag exists to make catchable."""
    hist_elec = _hh_records("2016-01-01", "2025-12-31")
    hist_gas = _daily_records("2016-01-01", "2025-12-31")
    ext_elec, ext_gas = build_extended_price_feeds(
        hist_elec, hist_gas, scenario="central_2027", year_from=2026, year_to=2027, seed="test")
    for r in ext_elec:
        expected = "historical" if r["settlementDate"] <= "2025-12-31" else "synthetic"
        assert r["data_regime"] == expected, (r["settlementDate"], r["data_regime"])
    for r in ext_gas:
        expected = "historical" if r["settlementDate"] <= "2025-12-31" else "synthetic"
        assert r["data_regime"] == expected, (r["settlementDate"], r["data_regime"])


def test_build_extended_no_op_path_also_tags_historical():
    """The no-extension-needed early return tags historical records too -- provenance is never
    dropped on any return path."""
    hist_elec = _hh_records("2016-01-01", "2025-12-31")
    hist_gas = _daily_records("2016-01-01", "2025-12-31")
    ext_elec, ext_gas = build_extended_price_feeds(
        hist_elec, hist_gas, scenario="central_2027", year_from=2030, year_to=2025, seed="noop")
    assert all(r.get("data_regime") == "historical" for r in ext_elec)
    assert all(r.get("data_regime") == "historical" for r in ext_gas)


def test_expand_daily_to_hh_keys_present():
    records = _daily_records("2020-01-01", "2020-01-01")
    hh = _expand_daily_to_hh(records)
    expected_keys = {"settlementDate", "settlementPeriod", "systemSellPrice"}
    assert set(hh[0].keys()) == expected_keys


def test_expand_daily_to_hh_settlement_periods_1_to_48():
    records = _daily_records("2020-01-01", "2020-01-01")
    hh = _expand_daily_to_hh(records)
    periods = sorted({r["settlementPeriod"] for r in hh})
    assert periods == list(range(1, 49))


def test_expand_daily_to_hh_empty_input():
    result = _expand_daily_to_hh([])
    assert result == []


def test_expand_daily_to_hh_empty_list():
    assert _expand_daily_to_hh([]) == []


def test_expand_daily_to_hh_two_days():
    daily = _daily_records("2027-04-01", "2027-04-02")
    hh = _expand_daily_to_hh(daily)
    assert len(hh) == 96


def test_build_extended_scenario_dates_start_at_year_from():
    hist_elec = _hh_records("2016-01-01", "2025-12-31")
    hist_gas = _daily_records("2016-01-01", "2025-12-31")
    ext_elec, _ = build_extended_price_feeds(
        hist_elec, hist_gas,
        scenario="central_2027", year_from=2026, year_to=2026,
        seed="x",
    )
    scenario_dates = sorted(
        r["settlementDate"] for r in ext_elec if r["settlementDate"] >= "2026-01-01"
    )
    assert scenario_dates[0] == "2026-01-01"


# ── W1_2 HARDEN 2026-07-28: reconcile_baseline_fidelity -- the PRODUCTION CALLER ──────────
# check_scenario_fidelity's six hardened moments had ZERO production callers for the entire
# hardening arc (blade sharpened on synthetic red-team fixtures, never swung on the ACTUAL
# baseline generator's output -> R15 "an uninvoked check is a failed check"). These tests are
# that caller and lock what it found: the baseline_2025 generator UNDER-CLUSTERS volatility vs
# real 2016-2025 SSP (vol_clustering ~0.21 generated vs ~0.42-0.51 real, robust across every
# real window), a genuine fidelity gap in the generator mechanism (fix lives in
# bimodal_generator.py, OUTSIDE this atom's file_scope -- registered as a tracked simplification).
from simulation.run_scenario import (
    _daily_returns,
    load_real_ssp_daily_returns,
    reconcile_baseline_fidelity,
)
from sim.scenario import fidelity_check as F


def test_daily_returns_are_first_differences():
    """ΔP (not log/pct returns -- SSP goes negative/through-zero, which breaks those)."""
    r = _daily_returns([10.0, 12.0, 9.0, 9.0])
    assert list(r) == [2.0, -3.0, 0.0]


def test_real_ssp_fixture_loads_and_is_non_degenerate():
    """The compact committed real reference exists and is a usable return series."""
    ref = load_real_ssp_daily_returns()
    assert len(ref) > 2000                      # ~3500 days of real 2016-2025 SSP
    assert F._std(F._clean(ref, min_len=20)) > 0  # real dispersion, not degenerate


def test_reconcile_swings_the_blade_on_real_generated_output():
    """The point of the atom's fidelity machinery: the check actually RUNS on the real
    baseline generator vs real history, reporting every hardened moment (not zero callers)."""
    v = reconcile_baseline_fidelity()
    assert {c.moment for c in v.checks} == set(F.MOMENTS)   # all six moments swung
    assert len(F.MOMENTS) == 6


def test_reconcile_detects_baseline_vol_clustering_gap():
    """LOCKS the 2026-07-28 finding: run against real history, the baseline_2025 generator
    diverges on vol_clustering (it under-clusters volatility -- real energy stress arrives in
    multi-day spells the generator's fast-turnover Markov regime does not sustain). This is the
    control FIRING on a REAL generator defect -- stronger than a synthetic mutation. When the
    generator is later fixed (bimodal_generator.py, out of file_scope), this sentinel flips and
    must be revisited, not silently deleted."""
    v = reconcile_baseline_fidelity()
    assert not v.passed
    assert "vol_clustering" in v.diverging()


def test_reconcile_deterministic():
    """C-S2 replay: same inputs -> identical verdict (fixed generator seed + check seed)."""
    a = reconcile_baseline_fidelity()
    b = reconcile_baseline_fidelity()
    assert a.diverging() == b.diverging()
    assert [c.ref_ci for c in a.checks] == [c.ref_ci for c in b.checks]


def test_reconcile_passes_on_a_matching_generator():
    """R15 the control CAN pass (not fail-closed/tautological): a generated series drawn from
    the real reference itself agrees on every moment -> passed=True, nothing diverging."""
    ref = load_real_ssp_daily_returns()
    v = reconcile_baseline_fidelity(generated_returns=ref, reference_returns=ref)
    assert v.passed, v.diverging()


def test_reconcile_fires_on_an_injected_mean_shift():
    """R15 the control fires on a clearly-wrong generator: a +50 GBP/MWh return-mean shift
    (a mis-calibrated generator) is caught on the mean moment."""
    ref = load_real_ssp_daily_returns()
    v = reconcile_baseline_fidelity(generated_returns=ref + 50.0, reference_returns=ref)
    assert not v.passed
    assert "mean" in v.diverging()


def test_reconcile_is_nonblocking_never_raises_on_divergence():
    """R12/R4: a divergence is a DIAGNOSTIC, never a raise/publish-blocker. The known hazard
    (a false-fire jamming the reporting pipeline) is why this is diagnostic-only -- it returns a
    verdict even when the baseline diverges, rather than raising."""
    v = reconcile_baseline_fidelity()          # currently DIVERGES on vol_clustering
    assert isinstance(v, F.FidelityVerdict)     # returned, not raised


def test_reconcile_fail_open_loud_on_degenerate_reference():
    """FAIL-OPEN loud: a degenerate/missing reference raises rather than returning a passing
    verdict (an unavailable check is a failed check, never a silent green)."""
    with pytest.raises(F.DegenerateSeriesError):
        reconcile_baseline_fidelity(
            generated_returns=load_real_ssp_daily_returns(),
            reference_returns=[3.0] * 500,      # constant -> no dispersion
        )
