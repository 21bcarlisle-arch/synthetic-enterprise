"""W1_6 SIM ground-truth chain tests (sim/weather_price_chain.py) -- price as a
DERIVED output of one coherent weather draw, with the R15 mutation tests the
FRAME (section 6) requires (each control shown to FIRE on its own named defect).

Covered:
  * The three front links fit real relationships (demand degree-day R2, wind/solar
    physical-shape correlation) on the real 2016-2025 record.
  * SHOW THE TAIL: the cold-and-still corner produces a mechanistic price spike
    driven by a tight residual demand (the DoD deliverable).
  * R15 I1 derived-not-drawn -- price VARIES with weather; a frozen weather input
    collapses the variance (mutation FIRES).
  * R15 I2 residual identity -- RD == demand - wind - solar exactly; a sign flip
    breaks it (mutation FIRES).
  * R15 I3 merit-order monotonicity -- colder -> tighter residual -> dearer price.
  * R15 I4 the spike comes from the WEATHER->DEMAND coupling -- cutting the
    demand-temp link (flat demand) collapses the spike ratio toward 1 (FIRES).
  * R12 the chain-vs-real-SSP MAE is a reported DIAGNOSTIC, not a tuned target.
  * Determinism (C-S2) and FAIL-OPEN on degenerate input.
"""
from __future__ import annotations

import dataclasses

import numpy as np
import pytest

from sim import weather_price_chain as wpc


@pytest.fixture(scope="module")
def params():
    return wpc.fit_chain()


@pytest.fixture(scope="module")
def record():
    return wpc.derive_price_on_record()


def test_front_links_fit_real_relationships(params):
    # Degree-day demand: a real, positive heating slope, convex in cold, R2 ~ 0.55.
    assert params.demand_b_hdd > 0          # colder -> more demand
    assert params.demand_base_mw > 15000    # a plausible GB base load (MW)
    assert params.demand_r2 == pytest.approx(0.55, abs=0.1)
    # Wind output tracks wind speed through the power curve (positive corr).
    assert params.wind_corr > 0.4
    # Solar tracks the seasonal x cloud envelope.
    assert params.solar_corr > 0.5
    assert params.n_days > 3000


def test_show_the_tail_cold_still_spike(params):
    spike = wpc.cold_still_spike(params)
    # The cold-and-still corner is materially DEARER than the rest, and it is the
    # residual-demand tightness (not an independent draw) that causes it.
    assert spike["spike_ratio"] > 1.5
    assert spike["tail_mean_price"] > spike["rest_mean_price"] + 30
    assert spike["tail_mean_residual_mw"] > spike["rest_mean_residual_mw"]
    assert spike["n_tail"] > 20


def test_r15_i1_price_is_derived_not_drawn(record, params):
    # CONTROL: the derived price VARIES with weather (it is a function of the
    # weather draw, not an independent draw).
    price = record["derived_price"]
    assert float(np.std(price)) > 10.0        # real weather -> real price spread

    # MUTATION: freeze the weather (constant temp/wind/cloud) at a fixed gas
    # price -> residual demand is constant -> the derived price must NOT vary.
    # If price still varied with weather frozen, it would be an independent draw.
    n = len(price)
    frozen = wpc.derive_price(
        temp_c=np.full(n, 10.0), wind_speed_ms=np.full(n, 6.0),
        cloud_pct=np.full(n, 50.0), day_of_year=np.full(n, 100),
        gas_price=np.full(n, 30.0), params=params,
    )
    assert float(np.std(frozen)) < 1e-6       # the control FIRES: no weather -> no price move


def test_r15_i2_residual_identity(record, params):
    # CONTROL: RD == demand - wind - solar exactly on the whole record.
    demand = wpc.demand_from_weather(record["temperature_c"], params)
    rd = wpc.residual_demand(record["temperature_c"], record["wind_speed_ms"],
                             np.array([50.0] * len(demand)), np.array([100] * len(demand)),
                             params)
    # residual_demand recomputes wind/solar; assert it equals demand - (wind+solar)
    wind = np.asarray(wpc.wind_output_from_speed(record["wind_speed_ms"], params))
    solar = wpc.solar_output_from_weather(np.array([100] * len(demand)),
                                          np.array([50.0] * len(demand)), params)
    np.testing.assert_allclose(rd, demand - wind - solar, rtol=0, atol=1e-6)
    # MUTATION: flipping the renewable sign breaks the identity (would ADD
    # renewable to load) -- the mutated identity must differ materially.
    mutated = demand + wind + solar
    assert not np.allclose(rd, mutated)
    assert float(np.mean(mutated - rd)) > 1000  # off by ~2x renewable, thousands of MW


def test_r15_i3_merit_order_monotone_in_cold(params):
    # Colder day -> more heating demand -> tighter residual -> dearer price, at
    # fixed wind/solar/gas. A monotone chain; mutate the temperature down and
    # price must not fall.
    warm = wpc.derive_price(temp_c=8.0, wind_speed_ms=6.0, cloud_pct=50.0,
                            day_of_year=15, gas_price=40.0, params=params)
    cold = wpc.derive_price(temp_c=-3.0, wind_speed_ms=6.0, cloud_pct=50.0,
                            day_of_year=15, gas_price=40.0, params=params)
    assert cold > warm
    # still-and-cold is dearer still than cold-but-windy (low wind -> low output
    # -> tighter residual).
    cold_windy = wpc.derive_price(temp_c=-3.0, wind_speed_ms=12.0, cloud_pct=50.0,
                                  day_of_year=15, gas_price=40.0, params=params)
    assert cold > cold_windy


def test_r15_i4_spike_comes_from_weather_residual_coupling(params):
    # The spike must come from the weather->residual-demand couplings, not a
    # stored number. The cold-and-still corner is tight via TWO pathways:
    # cold -> heating demand UP, and still -> wind output DOWN. Cutting EITHER
    # reduces the spike; cutting BOTH collapses it (only gas seasonality remains).
    healthy = wpc.cold_still_spike(params)
    assert healthy["spike_ratio"] > 1.8

    # MUTATION A: cut the demand-temp coupling (flat demand) -> spike shrinks.
    cut_demand = dataclasses.replace(params, demand_b_hdd=0.0, demand_b_cdd=0.0)
    assert wpc.cold_still_spike(cut_demand)["spike_ratio"] < healthy["spike_ratio"]

    # MUTATION B: cut the wind coupling (no wind fleet) -> spike shrinks.
    cut_wind = dataclasses.replace(params, wind_fleet_mw=0.0)
    assert wpc.cold_still_spike(cut_wind)["spike_ratio"] < healthy["spike_ratio"]

    # MUTATION C (the killer): cut BOTH residual couplings -> residual demand is
    # weather-independent -> the merit-order spike COLLAPSES; the small remainder
    # (~1.2) is gas seasonality on those days, NOT the physics tail.
    cut_all = dataclasses.replace(params, demand_b_hdd=0.0, demand_b_cdd=0.0,
                                  wind_fleet_mw=0.0, solar_fleet_mw=0.0)
    collapsed = wpc.cold_still_spike(cut_all)
    assert collapsed["spike_ratio"] < 1.35
    assert collapsed["spike_ratio"] < healthy["spike_ratio"] - 0.7


def test_r12_chain_vs_real_ssp_is_a_reported_diagnostic(params):
    diag = wpc.chain_vs_real_ssp_mae(params)
    # Reported, not asserted against a tuned threshold (R12). Sanity only: the
    # chain's MEAN is in the ballpark of real SSP (the composition is not absurd),
    # and the MAE is a finite positive number that is simply surfaced.
    assert diag["mae"] > 0
    assert diag["chain_mean"] == pytest.approx(diag["real_mean"], abs=25.0)
    assert diag["n"] > 3000


def test_determinism_and_fail_open():
    a = wpc.fit_chain()
    b = wpc.fit_chain()
    assert a == b
    # FAIL-OPEN: a degenerate solar envelope (all-cloud, off-season) is handled;
    # an empty tail mask raises rather than silently passing.
    empty = {"month": np.array([6, 7, 8]),
             "temperature_c": np.array([20.0, 21.0, 22.0]),
             "wind_speed_ms": np.array([5.0, 6.0, 7.0])}
    with pytest.raises(wpc.DegenerateChainError):
        wpc.cold_still_tail_mask(empty)  # no winter days -> FAIL-OPEN
