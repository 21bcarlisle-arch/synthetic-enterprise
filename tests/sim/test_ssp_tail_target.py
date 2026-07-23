"""R15 for the empirical real-SSP-tail TARGET (sim/ssp_tail_target.py) -- step 1 of the spike-tail
attack plan (SPIKE_TAIL_SSP_RESIDUAL). The target is what the future T1 tail-fidelity test grades the
generator against, so the target itself must be (a) reproducible and consistent with the G4 ledger and
(b) FAIL-CLOSED -- an empty/uncomputable distribution must RAISE, never return a silently-zero pass
(the plan's named fail-open guard: "a missing/empty ledger figure is a FAILED check, never green").
"""
import pytest

import sim.ssp_tail_target as tgt


# ---- FAIL-CLOSED (the guard must be able to fire) -------------------------------------------------

def test_fail_closed_on_missing_records(monkeypatch):
    monkeypatch.setattr("sim.cache_store.get_cached_prices", lambda s, e: None)
    with pytest.raises(ValueError):
        tgt.real_ssp_tail("2016-03-01", "2025-06-07")


def test_fail_closed_on_no_numeric_ssp(monkeypatch):
    monkeypatch.setattr("sim.cache_store.get_cached_prices",
                        lambda s, e: [{"settlementDate": "2020-01-01", "systemSellPrice": None}])
    with pytest.raises(ValueError):
        tgt.real_ssp_tail("2016-03-01", "2025-06-07")


def test_percentile_rejects_empty():
    with pytest.raises(ValueError):
        tgt._percentile([], 95)


# ---- SHAPE (a synthetic distribution proves the maths, no cache needed) ---------------------------

def test_exceedance_and_negative_fraction_from_synthetic(monkeypatch):
    # 100 periods: 10 negative, 5 above GBP200 (two above GBP500), rest mid.
    vals = ([-5.0] * 10) + ([50.0] * 85) + ([250.0, 250.0, 250.0, 600.0, 600.0])
    monkeypatch.setattr("sim.cache_store.get_cached_prices",
                        lambda s, e: [{"systemSellPrice": v} for v in vals])
    t = tgt.real_ssp_tail("2016-03-01", "2025-06-07")
    assert t["n"] == 100
    assert t["frac_negative"] == pytest.approx(0.10)
    assert t["exceedance_gbp"]["frac_gt_200"] == pytest.approx(0.05)
    assert t["exceedance_gbp"]["frac_gt_500"] == pytest.approx(0.02)
    # exceedance is a monotonically non-increasing curve as the threshold rises
    fr = [t["exceedance_gbp"][f"frac_gt_{k}"] for k in (200, 300, 500, 1000, 2000, 3000)]
    assert fr == sorted(fr, reverse=True)


# ---- CONSISTENT WITH THE G4 LEDGER (real cache; skip if absent in this build env) ----------------

def test_real_tail_matches_ledger_headlines():
    from sim.cache_store import get_cached_prices
    if not get_cached_prices(tgt.MODEL_START_DATE, tgt.MODEL_END_DATE):
        pytest.skip("real Elexon SSP cache not present in this environment")
    t = tgt.real_ssp_tail()
    # Ledger (site/data/fidelity.json): real max 4037.8, frac_negative 0.02241, real p95 220.
    assert t["max"] == pytest.approx(4037.8, abs=1.0), "real max must match the ledger's GBP4038 peak"
    assert t["frac_negative"] == pytest.approx(0.02241, abs=0.002), "neg-fraction within ledger tolerance"
    assert 200.0 <= t["p95"] <= 240.0, "p95 near the ledger's real GBP220"
    # the tail the model STARVES: a materially non-trivial fraction sits in the scarcity-spike regime
    assert t["exceedance_gbp"]["frac_gt_500"] > 0.001, "real world spends real time above GBP500 (the model does not)"
    assert t["exceedance_gbp"]["frac_gt_2000"] > 0.0, "real world reaches the multi-thousand-pound spike regime"


# ---- DAILY-granularity target (step-3 diagnosis: the generator's real comparand) -----------------

def test_daily_fail_closed_on_missing_records(monkeypatch):
    monkeypatch.setattr("sim.cache_store.get_cached_prices", lambda s, e: None)
    with pytest.raises(ValueError):
        tgt.real_ssp_daily_tail("mean", "2016-03-01", "2025-06-07")


def test_daily_aggregate_rejects_unknown_agg():
    with pytest.raises(ValueError):
        tgt._daily_aggregate([{"settlementDate": "2020-01-01", "systemSellPrice": 50.0}], "p99")


def test_daily_aggregate_mean_and_max(monkeypatch):
    # Two days: day A has SPs {0, 100} (mean 50, max 100); day B is a spike day {50, 4000} (mean 2025, max 4000).
    recs = (
        [{"settlementDate": "2021-01-08", "systemSellPrice": 50.0},
         {"settlementDate": "2021-01-08", "systemSellPrice": 4000.0}]
        + [{"settlementDate": "2020-06-01", "systemSellPrice": 0.0},
           {"settlementDate": "2020-06-01", "systemSellPrice": 100.0}]
    )
    means = sorted(tgt._daily_aggregate(recs, "mean"))
    maxes = sorted(tgt._daily_aggregate(recs, "max"))
    assert means == pytest.approx([50.0, 2025.0])
    assert maxes == pytest.approx([100.0, 4000.0])


def test_daily_mean_max_is_far_below_hh_max():
    """The load-bearing granularity fact (step-3 diagnosis, blind to P&L): the real DAILY-MEAN SSP max is
    an order of magnitude BELOW the half-hourly GBP4,038 -- because the GBP4,038 is a single settlement
    period, not a day's average. So grading the forward generator's daily price against the half-hourly
    max is a category error; a daily-mean series that reached GBP4,038 would be LESS real, not more.
    This is the empirical basis for redirecting the fix to intraday shape rather than a bigger daily number."""
    from sim.cache_store import get_cached_prices
    if not get_cached_prices(tgt.MODEL_START_DATE, tgt.MODEL_END_DATE):
        pytest.skip("real Elexon SSP cache not present in this environment")
    daily_mean = tgt.real_ssp_daily_tail("mean")
    daily_max = tgt.real_ssp_daily_tail("max")
    hh = tgt.real_ssp_tail()
    # daily-mean max is well under GBP1,000 and a small fraction of the half-hourly peak
    assert daily_mean["max"] < 1000.0, "no real DAY averaged above GBP1,000"
    assert daily_mean["max"] < 0.5 * hh["max"], "daily-mean peak is far below the half-hourly GBP4,038"
    # the half-hourly spike survives in the daily-MAX view (worst SP of the day) -- so the tail is real,
    # just sub-daily; it is the flat daily generator, not reality, that lacks it
    assert daily_max["max"] == pytest.approx(hh["max"], abs=1.0)
    # daily-mean negative fraction is far thinner than half-hourly: negatives are sub-daily too
    assert daily_mean["frac_negative"] < 0.3 * hh["frac_negative"]
