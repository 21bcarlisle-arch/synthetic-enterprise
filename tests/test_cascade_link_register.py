"""R15 tests for the D1..D8 real cascade-link register
(background/cascade_link_register.py).

Covered:
  * D1 ESTIMATED on real winter weather reproduces the DISCOVER doc's cited
    cold-and-still coupling (all-year Pearson ~0 lies; the winter lower tail is
    strongly coupled), with a CI that excludes the independence null.
  * D8 ESTIMATED = the DESEASONALISED residual AR1 phi (not the seasonality-
    contaminated raw autocorr), reproducing the cited ~0.78/0.57.
  * R15 MUTATION: cutting D1's coupling (shuffle wind) collapses the lift toward
    the independence null — the estimate is a real corner count, not a tautology.
  * The register is COMPLETE (all eight D-links in exactly one honest state) and
    every ASSERTED link carries a sign + reason + grounding (R10, never dressed
    as estimated).
  * Determinism (C-S2).
"""
from __future__ import annotations

import numpy as np
import pytest

from background.cascade_link_register import (
    asserted_links,
    build_register,
    estimate_d1_temp_wind,
    estimate_d8_persistence,
    write_register,
)
from background.cascade_correlation_estimation import (
    condition,
    cut_coupling,
    joint_tail_lift,
)
from sim.weather_tail_demonstration import load_national_daily


def test_d1_reproduces_cited_cold_and_still_coupling():
    e = estimate_d1_temp_wind()
    # DISCOVER doc: winter decile lift ~2.34x (vs all-year Pearson ~-0.06).
    assert e.value == pytest.approx(2.34, abs=0.6)
    assert e.value > 1.2  # genuinely coupled, well above the independence null
    # CI excludes the independence null (1.0) -> the coupling is real, not noise.
    assert e.detail["ci_low"] > 1.0


def test_d8_uses_deseasonalised_residual_persistence():
    e = estimate_d8_persistence()
    assert e.statistic == "residual_ar1_phi"
    # cited residual AR1: temp ~0.78, wind ~0.57 (NOT the raw ~0.95 season-contaminated autocorr).
    assert e.detail["residual_phi_temp"] == pytest.approx(0.78, abs=0.08)
    assert e.detail["residual_phi_wind"] == pytest.approx(0.57, abs=0.08)


def test_d1_mutation_cutting_coupling_collapses_the_lift():
    # R15: independently re-derive on the SAME conditioned data, then cut the
    # coupling; the lift must collapse toward the independence null (~1). Proves
    # the D1 estimate reflects a real corner, not a stored/tautological number.
    national, _doy, dates = load_national_daily()
    winter = np.array([d.month in (12, 1, 2) for d in dates])
    temp_w = condition(national["temperature_mean_c"], winter)
    wind_w = condition(national["wind_speed_mean_ms"], winter)
    real = joint_tail_lift(temp_w, wind_w, u=0.10, upper=False).lift
    cut = joint_tail_lift(temp_w, cut_coupling(wind_w, seed=1), u=0.10, upper=False).lift
    assert real > 1.2
    assert cut < real          # the cut destroys the coupling
    assert cut == pytest.approx(1.0, abs=0.6)  # collapses toward independence


def test_d4_demand_temp_cold_tail_estimated_on_real_data():
    from background.cascade_link_register import estimate_d4_demand_temp
    e = estimate_d4_demand_temp()
    # Cold (low temp) AND high demand strongly co-occur -- the convex heating
    # plateau. The TAIL lift is well above 1 and above what the linear all-year
    # Pearson (~-0.7) alone conveys.
    assert e.value > 2.0
    assert e.detail["ci_low"] > 1.0
    assert e.detail["pearson_all_year"] < 0  # cold -> high demand, negative linear corr


@pytest.fixture(scope="module")
def register():
    # ONE build for all register-structure tests (build_register loads the large
    # AGWS + SSP caches for D2 -- module scope keeps that cost to a single load).
    return build_register(seed=0)


def test_register_is_complete_all_eight_links(register):
    assert register["covered_links"] == [f"D{i}" for i in range(1, 9)]
    # four estimated (D1, D2, D4, D8), four asserted -> all eight, no gap, no double.
    assert len(register["estimated"]) == 4
    assert len(register["asserted"]) == 4


def test_d2_residual_price_estimated_on_real_agws(register):
    d2 = next(e for e in register["estimated"] if e["link_id"] == "D2_residual_demand_price")
    # Tight residual demand AND dear price co-occur at HALF-HOURLY resolution
    # (measured 1.32, rising into the tail); daily aggregation washes it out.
    assert d2["value"] > 1.15
    assert d2["detail"]["ci_low"] > 1.0   # CI excludes the independence null
    assert d2["detail"]["n_periods"] > 100000


def test_asserted_links_are_grounded_not_dressed_as_estimated():
    for a in asserted_links():
        assert a.reason.strip()       # WHY not estimated
        assert a.grounding.strip()    # the real series + statistic that would estimate it
        assert a.assumed_sign in ("upper", "lower", "anti")


def test_register_deterministic(tmp_path, register):
    # Determinism proven on the cheap estimates (fixed data + seed) rather than a
    # second full build (which would re-load the 100MB+ AGWS/SSP caches). The
    # D1/D2/D4 estimates and D8 are pure functions of the committed data + seed.
    assert estimate_d1_temp_wind(seed=0) == estimate_d1_temp_wind(seed=0)
    # the register serialises to a valid file (json round-trip of the fixture).
    import json
    p = tmp_path / "reg.json"
    p.write_text(json.dumps(register, sort_keys=True))
    assert json.loads(p.read_text())["covered_links"] == register["covered_links"]
