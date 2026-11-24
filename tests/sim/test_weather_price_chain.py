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

# A test input for the carbon argument, not a domain value: CPS + an allowance price of
# the order the record shows (GBP 22-98/t across 2016-2025).
_CARBON = 40.0


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
        gas_price=np.full(n, 30.0), params=params, carbon_price_gbp_per_tonne=_CARBON,
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
                            day_of_year=15, gas_price=40.0, params=params,
                            carbon_price_gbp_per_tonne=_CARBON)
    cold = wpc.derive_price(temp_c=-3.0, wind_speed_ms=6.0, cloud_pct=50.0,
                            day_of_year=15, gas_price=40.0, params=params,
                            carbon_price_gbp_per_tonne=_CARBON)
    assert cold > warm
    # still-and-cold is dearer still than cold-but-windy (low wind -> low output
    # -> tighter residual).
    cold_windy = wpc.derive_price(temp_c=-3.0, wind_speed_ms=12.0, cloud_pct=50.0,
                                  day_of_year=15, gas_price=40.0, params=params,
                            carbon_price_gbp_per_tonne=_CARBON)
    assert cold > cold_windy


def test_r15_i3_price_monotone_in_residual_demand(params, monkeypatch):
    # Invariant 3 (FRAME §6) stated DIRECTLY and mutation-proven both ways -- the
    # sibling test above checks two cold-range POINTS but carries no mutation arm
    # (the FRAME requires "mutate to non-monotone and it fails"). The invariant's
    # own wording is "price non-decreasing in RESIDUAL DEMAND at a fixed gas floor"
    # -- NOT in temperature (price is U-shaped in temp: CDD cooling load lifts the
    # warm tail), so this orders by residual, not by temperature.
    #
    # Sweep residual via a HEATING-range temperature sweep (all <= T_HEAT_C -> pure
    # HDD, CDD == 0 -> demand strictly rising as it cools -> residual strictly
    # rising) at fixed wind/cloud/doy/gas, order by residual, and assert the
    # derived price never FALLS as residual rises.
    temps = np.linspace(15.0, -12.0, 60)
    assert float(temps.max()) <= wpc.T_HEAT_C          # pure-HDD sweep (no CDD kink)
    kw = dict(wind_speed_ms=np.full(60, 6.0), cloud_pct=np.full(60, 50.0),
              day_of_year=np.full(60, 15), gas_price=np.full(60, 40.0), params=params,
              carbon_price_gbp_per_tonne=_CARBON)
    price = wpc.derive_price(temp_c=temps, **kw)
    rd = wpc.residual_demand(temps, kw["wind_speed_ms"], kw["cloud_pct"],
                             kw["day_of_year"], params)
    order = np.argsort(rd)
    # CONTROL: monotone non-decreasing in residual demand (float tol only).
    assert np.all(np.diff(price[order]) >= -1e-6)

    # MUTATION: replace the merit-order price response with a NON-MONOTONE one
    # (price falls as residual rises -- dearer when slack, cheaper when tight).
    # The monotonicity control must FIRE (a downward step appears in residual order)
    # -- proving it has teeth, not a property that always passes on any price map.
    monkeypatch.setattr(wpc, "synthetic_price",
                        lambda gas, demand, renewable, **_kw: -1.0 * float(demand - renewable))
    price_mut = wpc.derive_price(temp_c=temps, **kw)
    assert np.any(np.diff(price_mut[order]) < -1e-6)   # control FIRES on the non-monotone mutant


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
    # The collapse removes at least three quarters of the excess over 1 (measured 24 Nov,
    # fleet curve: 1.90 -> 1.20; the single curve's ratio was larger, so was its fall).
    assert collapsed["spike_ratio"] - 1.0 < 0.25 * (healthy["spike_ratio"] - 1.0)


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


def test_the_fleet_curve_has_no_still_cliff_and_no_storm_fall(record):
    """Defect named: one turbine's curve on a town wind gave exactly zero on 28% of record days
    and 100.8 GW on the windiest (area map C1), and the fitted aggregate curve falls above about
    10 m/s where the record has 2 days. The hold must be REACHABLE on the record before its
    value is asserted, or a hold that never binds passes."""
    curve = wpc.fit_fleet_curve()
    w = record["wind_speed_ms"]
    held = w >= curve.hold_from_ms
    assert held.any() and (~held).any()            # the hold binds on some days, not all
    f = wpc.fleet_wind_fraction(w)
    assert np.all(f[held] == curve.hold_fraction)
    assert np.all(f > 0)                           # no still-day cliff to zero
    storm = wpc.fleet_wind_fraction(np.array([curve.hold_from_ms, 15.0, 24.0, 30.0]))
    assert np.all(storm == curve.hold_fraction)    # no fall into a forward storm draw
    rec = wpc.load_daily_record()
    assert float(np.max(record["renewable_mw"])) < 2.0 * float(np.max(rec["wind_gen_mw"]
                                                                       + rec["solar_gen_mw"]))


def test_the_price_leg_refuses_a_call_without_carbon(params):
    """Defect named: the refitted multiplier no longer carries carbon, so a call that omits it
    under-prices silently. The refusal must name its reason, and the same call with carbon
    must price (the branch is takeable both ways)."""
    kw = dict(temp_c=5.0, wind_speed_ms=6.0, cloud_pct=50.0, day_of_year=15, gas_price=40.0,
              params=params)
    with pytest.raises(wpc.CarbonRequiredError, match="carbon"):
        wpc.derive_price(**kw)
    low = wpc.derive_price(**kw, carbon_price_gbp_per_tonne=20.0)
    high = wpc.derive_price(**kw, carbon_price_gbp_per_tonne=80.0)
    assert high > low > 0


def test_the_carbon_table_is_one_series_and_ends_where_its_record_does():
    from sim.merit_order_reconstruction import (
        CPS_CARBON_GBP_PER_TONNE,
        carbon_price_in_month_gbp_per_tonne,
        ets_carbon_price_gbp_per_tonne,
        uka_auction_vwap_by_month,
    )

    assert carbon_price_in_month_gbp_per_tonne("2018-06") == pytest.approx(
        CPS_CARBON_GBP_PER_TONNE + ets_carbon_price_gbp_per_tonne(2018))
    months = uka_auction_vwap_by_month()
    assert carbon_price_in_month_gbp_per_tonne("2022-06") == pytest.approx(
        CPS_CARBON_GBP_PER_TONNE + months["2022-06"])
    with pytest.raises(ValueError, match="curriculum"):
        carbon_price_in_month_gbp_per_tonne("2027-01")
    assert wpc.carbon_on("2023-03-15") == carbon_price_in_month_gbp_per_tonne("2023-03")
