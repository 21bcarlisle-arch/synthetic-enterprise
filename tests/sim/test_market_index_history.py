"""Elexon MID (traded wholesale price) retrieval + the W1_6b criterion-3a validity finding.

Two families here:

1. GUARDS on `sim/market_index_history.py`, each written against a fail-open OBSERVED
   in the live API on 2026-08-03 — not a hypothetical. A too-wide range returns HTTP
   200 with an empty `data` list; a reporting provider publishes price 0.00 on volume
   0.00 for the entire 2016-2020 window. Both would corrupt the series SILENTLY.

2. The MEASURED findings, which need the caches and skip without them.
"""

import math

import pytest

from sim.market_index_history import (
    MAX_RANGE_DAYS,
    MID_COVERAGE_START,
    MarketIndexUnavailable,
    cache_present,
    get_market_index_range,
    is_finite_number,
    volume_weighted_mid,
)


def _rec(date, period, provider, price, volume):
    return {
        "settlementDate": date,
        "settlementPeriod": period,
        "dataProvider": provider,
        "price": price,
        "volume": volume,
    }


# ---------------------------------------------------------------------------
# GUARD 1 — a non-reporting provider must not drag the price toward zero
# ---------------------------------------------------------------------------

def test_zero_volume_provider_is_dropped_not_averaged():
    """N2EXMIDP publishes 0.00 price on 0.00 volume in EVERY period sampled across
    2016-2020, while APXMIDP carries the real trades. A naive mean across providers
    would HALVE every wholesale price in the series — the defect this guard exists for.

    This is the R15 mutation in assertion form: the naive answer (25.0) is computed
    here explicitly so the test states what the wrong behaviour would have produced.
    """
    records = [
        _rec("2019-01-15", 13, "APXMIDP", 50.0, 700.0),
        _rec("2019-01-15", 13, "N2EXMIDP", 0.0, 0.0),
    ]
    joined = volume_weighted_mid(records)
    naive_mean_across_providers = (50.0 + 0.0) / 2
    assert joined[("2019-01-15", 13)] == pytest.approx(50.0)
    assert joined[("2019-01-15", 13)] != pytest.approx(naive_mean_across_providers)


def test_negative_volume_is_rejected_rather_than_subtracting_from_the_weight():
    """What the `volume <= 0` line UNIQUELY guards, stated honestly.

    A zero-volume provider is already neutralised by volume-weighting itself (it
    contributes 0 to both numerator and weight), so the previous test passes with or
    without that line — it proves the WEIGHTING, not the guard. A NEGATIVE volume is
    different: it subtracts from the denominator and can invert or explode the price.
    Here the unguarded arithmetic would yield (50*700 + 10*-600)/100 = 290.0.
    """
    records = [
        _rec("2019-01-15", 13, "APXMIDP", 50.0, 700.0),
        _rec("2019-01-15", 13, "N2EXMIDP", 10.0, -600.0),
    ]
    unguarded = (50.0 * 700.0 + 10.0 * -600.0) / (700.0 - 600.0)
    assert volume_weighted_mid(records)[("2019-01-15", 13)] == pytest.approx(50.0)
    assert unguarded == pytest.approx(290.0)


def test_price_is_volume_weighted_across_genuinely_reporting_providers():
    """When both providers DO trade, the join must weight by volume, not take a flat
    mean — the flat mean would over-weight a thin exchange."""
    records = [
        _rec("2019-01-15", 13, "APXMIDP", 40.0, 900.0),
        _rec("2019-01-15", 13, "N2EXMIDP", 60.0, 100.0),
    ]
    expected = (40.0 * 900.0 + 60.0 * 100.0) / 1000.0
    assert volume_weighted_mid(records)[("2019-01-15", 13)] == pytest.approx(expected)
    assert expected != pytest.approx(50.0)  # the flat-mean answer, explicitly excluded


def test_a_period_with_no_traded_volume_is_omitted_not_recorded_as_zero_price():
    """No trades is NOT a £0 trade. The period must vanish from the series so a caller
    joins on its absence, rather than averaging a fictitious zero into a cell mean."""
    records = [
        _rec("2019-01-15", 13, "APXMIDP", 0.0, 0.0),
        _rec("2019-01-15", 13, "N2EXMIDP", 0.0, 0.0),
    ]
    assert volume_weighted_mid(records) == {}


def test_non_finite_price_or_volume_is_rejected():
    """Fail-open pattern: NaN propagates through a weighted mean and poisons the cell
    mean silently, because every downstream comparison against NaN is False."""
    records = [
        _rec("2019-01-15", 13, "APXMIDP", float("nan"), 700.0),
        _rec("2019-01-15", 14, "APXMIDP", 50.0, float("inf")),
        _rec("2019-01-15", 15, "APXMIDP", 50.0, 700.0),
    ]
    joined = volume_weighted_mid(records)
    assert set(joined) == {("2019-01-15", 15)}
    assert all(is_finite_number(v) for v in joined.values())


def test_malformed_records_are_skipped_without_raising():
    records = [
        {"settlementDate": "2019-01-15"},                       # no period
        _rec("2019-01-15", "13", "APXMIDP", 50.0, 700.0),       # period not an int
        _rec("2019-01-15", 16, "APXMIDP", 50.0, 700.0),         # good
    ]
    assert set(volume_weighted_mid(records)) == {("2019-01-15", 16)}


def test_is_finite_number_excludes_bool():
    """bool is an int subclass; letting True through would make a flag readable as a
    price of 1.0. Mirrors the guard family in sim/merit_order_reconstruction.py."""
    assert is_finite_number(42.0) and is_finite_number(0)
    assert not is_finite_number(True)
    assert not is_finite_number(float("nan")) and not is_finite_number(None)


# ---------------------------------------------------------------------------
# GUARD 2 — an empty 200 is the too-wide-range failure mode, never "no trading"
# ---------------------------------------------------------------------------

def test_empty_response_inside_coverage_raises_rather_than_leaving_a_silent_hole(
    monkeypatch,
):
    """OBSERVED 2026-08-03: a 31-day window returned `{"data": []}` with HTTP 200 while
    the same window in 7-day chunks returned ~1,490 records/week. Treating that as an
    absence of trading would zero out arbitrary stretches of history, and every cell
    mean downstream would be computed on an undeclared subset."""
    monkeypatch.setattr(
        "sim.market_index_history._fetch_window", lambda *a, **k: []
    )
    with pytest.raises(MarketIndexUnavailable, match="ZERO records"):
        get_market_index_range("2019-01-01", "2019-01-05")


def test_a_request_before_coverage_start_raises_as_a_named_gap():
    """MID begins 2016-09-12 (bisected against the live API). Returning [] for an
    earlier date would let a caller average "no wholesale price existed" into a
    verdict. The gap must be NAMED."""
    with pytest.raises(MarketIndexUnavailable, match="coverage begins"):
        get_market_index_range("2016-03-01", "2016-03-08")


def test_range_is_chunked_no_wider_than_the_width_proven_to_return_data(monkeypatch):
    """10, 14, 16 and 20-day windows all silently returned ZERO with a 200; 7 returned
    data. The fetcher must never issue a window wider than the proven width.

    The bound is the LITERAL 7, not `MAX_RANGE_DAYS`. Asserting the issued width
    against the same constant that produced it is the R15 TAUTOLOGY pattern — it
    passes for any value of the constant, which is exactly how this test first failed
    to fire when the constant was mutated 7 -> 31. The literal is the independent
    oracle: it is the width MEASURED against the live API on 2026-08-03.
    """
    PROVEN_MAX_WIDTH_DAYS = 7
    assert MAX_RANGE_DAYS <= PROVEN_MAX_WIDTH_DAYS, (
        f"MAX_RANGE_DAYS is {MAX_RANGE_DAYS}; widths above {PROVEN_MAX_WIDTH_DAYS} "
        "silently returned ZERO records with a 200 when measured against the live API"
    )
    windows = []

    def _capture(from_iso, to_iso):
        windows.append((from_iso, to_iso))
        return [_rec("2019-01-01", 1, "APXMIDP", 50.0, 700.0)]

    monkeypatch.setattr("sim.market_index_history._fetch_window", _capture)
    get_market_index_range("2019-01-01", "2019-02-15")

    assert windows, "no request was issued"
    for from_iso, to_iso in windows:
        from datetime import datetime

        span = (
            datetime.strptime(to_iso, "%Y-%m-%dT%H:%MZ")
            - datetime.strptime(from_iso, "%Y-%m-%dT%H:%MZ")
        ).days
        assert span <= PROVEN_MAX_WIDTH_DAYS, (
            f"window {from_iso}..{to_iso} spans {span} days"
        )


def test_non_200_raises_rather_than_returning_empty(monkeypatch):
    class _Resp:
        status_code = 503

        def json(self):  # pragma: no cover - must not be reached
            raise AssertionError("json() must not be consulted on a non-200")

    monkeypatch.setattr("sim.market_index_history._session.get", lambda *a, **k: _Resp())
    with pytest.raises(MarketIndexUnavailable, match="HTTP 503"):
        get_market_index_range("2019-01-01", "2019-01-05")


# ---------------------------------------------------------------------------
# MEASURED — needs the cache; skips (never passes) without it
# ---------------------------------------------------------------------------

_MID_CACHE: dict = {}


def _mid_rows():
    from simulation.run_merit_order_reconstructibility import build_calm_dataset, caches_present

    if not (caches_present() and cache_present()):
        pytest.skip("elexon demand/agws/MID caches absent — measured offline")
    if "rows" not in _MID_CACHE:
        _MID_CACHE["rows"] = build_calm_dataset(with_mid=True)
    return _MID_CACHE["rows"]


def test_mid_coverage_starts_where_the_constant_says_it_does():
    """The coverage bound is load-bearing (it makes the 2016 cell a part-year), so it
    is asserted against the cached data rather than trusted as a comment."""
    rows = _mid_rows()
    dated = sorted(r["date"] for r in rows if "mid" in r)
    assert dated[0] >= MID_COVERAGE_START
    assert dated[0][:7] == MID_COVERAGE_START[:7], (
        f"first MID row {dated[0]} — if this moved, the part-year bound on the 2016 "
        "cell must be re-stated, not silently inherited"
    )


def test_the_2016_cell_is_a_part_year_and_says_so():
    """R15: the honest bound must be MECHANICAL. If a later fetch backfills 2016, this
    fails and forces the evidence doc's 'not like-for-like' caveat to be revisited."""
    from simulation.run_merit_order_reconstructibility import (
        per_cell_reconstructibility_vs_target,
    )

    cells = per_cell_reconstructibility_vs_target(_mid_rows(), "mid")
    assert cells["2016"]["first_date"] >= MID_COVERAGE_START
    assert cells["2016"]["n_ordinary"] < cells["2017"]["n_ordinary"] / 2, (
        "the 2016 MID cell is ~30% covered; if it is no longer a part-year the "
        "evidence doc's comparability caveat is stale"
    )


def test_rows_outside_mid_coverage_carry_no_substitute_value():
    """The target must never be filled in. A carried-back or interpolated MID would
    make the 2016 comparison look complete while being invented."""
    rows = _mid_rows()
    pre_coverage = [r for r in rows if r["date"] < MID_COVERAGE_START]
    assert pre_coverage, "expected calm-window rows before MID coverage begins"
    assert all("mid" not in r for r in pre_coverage)


def test_the_reconstruction_beats_the_naive_floor_on_EVERY_cell_against_wholesale():
    """THE MEASURED FINDING (2026-08-03). Against MID — the price the SRMC stack is
    actually a model of — the reconstruction wins 5/5, where against SSP it wins 2/5.
    Same engine, same frozen naive ruler, same ordinary-hour mask; only the target
    differs."""
    from simulation.run_merit_order_reconstructibility import (
        per_cell_reconstructibility_vs_target,
        reconstructibility_verdict,
    )

    cells = per_cell_reconstructibility_vs_target(_mid_rows(), "mid")
    verdict = reconstructibility_verdict(cells)
    assert verdict["met"], verdict
    assert verdict["n_won"] == 5, verdict


def test_criterion_3a_is_VALID_because_the_real_traded_price_passes_it():
    """THE ORACLE TEST, and it REFUTED the hypothesis that motivated this work.

    The suspicion was that criterion 3a might be unpassable by any wholesale model,
    because SSP is a cash-out price ~12.30 £/MWh away from the traded price. If that
    were so, the criterion would be measuring the instrument gap, not the model.

    It is NOT so. Scoring the REAL TRADED PRICE as if it were the predictor — the
    best any wholesale model could possibly do — beats gas_floor_alone in all five
    calm cells. So the criterion is passable, the 2/5 shortfall is the ENGINE's and
    not the target's, and criterion 3a stands unchanged.

    This test exists to keep that refutation standing. If a later change to the naive
    ruler or the ordinary-hour mask ever makes the true price FAIL its own criterion,
    the criterion has become invalid and this fails loudly."""
    import numpy as np

    from sim.merit_order_reconstruction import gas_floor_alone_price_gbp_per_mwh
    from sim.price_engine import DISPATCHABLE_CAPACITY_MW, X_TIGHT

    rows = [r for r in _mid_rows() if "mid" in r]
    ssp = np.array([r["ssp"] for r in rows])
    mid = np.array([r["mid"] for r in rows])
    gas = np.array([r["gas_price"] for r in rows])
    dem = np.array([r["demand_mw"] for r in rows])
    ren = np.array([r["renewable_mw"] for r in rows])
    yr = np.array([r["year"] for r in rows])
    ordinary = ((dem - ren) / DISPATCHABLE_CAPACITY_MW) <= X_TIGHT
    floor = np.array([gas_floor_alone_price_gbp_per_mwh(g) for g in gas])

    for year in sorted(set(yr.tolist())):
        mask = (yr == year) & ordinary
        mae_floor = float(np.mean(np.abs(ssp[mask] - floor[mask])))
        mae_true = float(np.mean(np.abs(ssp[mask] - mid[mask])))
        assert mae_true < mae_floor, (
            f"{year}: the REAL traded price scores {mae_true:.2f} against SSP versus "
            f"the naive floor's {mae_floor:.2f} — if the true "
            "price cannot beat the naive ruler, criterion 3a is measuring the "
            "instrument gap and is invalid as a test of reconstruction"
        )


def test_the_two_instruments_are_genuinely_different_prices():
    """The quantified reason the SSP score is harsh: on ordinary hours the cash-out
    price sits ~12 £/MWh from the traded price and carries roughly twice its
    dispersion. Recorded as a DIAGNOSTIC (R12) — it explains the residual, it is not
    a target and nothing is tuned to it."""
    import numpy as np

    from sim.price_engine import DISPATCHABLE_CAPACITY_MW, X_TIGHT

    rows = [r for r in _mid_rows() if "mid" in r]
    ssp = np.array([r["ssp"] for r in rows])
    mid = np.array([r["mid"] for r in rows])
    dem = np.array([r["demand_mw"] for r in rows])
    ren = np.array([r["renewable_mw"] for r in rows])
    ordinary = ((dem - ren) / DISPATCHABLE_CAPACITY_MW) <= X_TIGHT

    gap = float(np.mean(np.abs(ssp[ordinary] - mid[ordinary])))
    assert 8.0 < gap < 18.0, f"instrument gap {gap:.2f} outside its recorded band"
    assert ssp[ordinary].std() > mid[ordinary].std(), (
        "cash-out is expected to be the noisier instrument; if that inverts, the "
        "explanation in the evidence doc no longer holds"
    )
    assert math.isfinite(gap)
