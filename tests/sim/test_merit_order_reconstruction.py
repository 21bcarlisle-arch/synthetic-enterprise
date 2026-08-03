"""W1_6b — Merit-order / gas-first price-engine reconstruction.

Unit tests on the structural SRMC-stack engine + the reconstructibility control and
its R15 mutations + the honest recorded reconstructibility result on real data
(skipped when the caches are absent, so the collected suite never depends on 100MB+
data files). See docs/design/frame/W1_6_merit_order_reconstruction_FRAME.md §3.
"""

import pytest

from sim.merit_order_reconstruction import (
    CASH_OUT_CEILING_GBP_PER_MWH,
    CPS_CARBON_GBP_PER_TONNE,
    MUST_RUN_FLOOR_MW,
    build_merit_stack,
    carbon_price_total_gbp_per_tonne,
    ccgt_srmc_gbp_per_mwh,
    gas_floor_alone_price_gbp_per_mwh,
    is_merit_order_monotone,
    reconstruct_price_gbp_per_mwh,
)
from sim.price_engine import THERMAL_EFFICIENCY

GAS = 20.0  # £/MWh, a representative ordinary NBP gas price


# --------------------------------------------------------------------------
# 1. Structural properties of the SRMC engine (fast, synthetic).
# --------------------------------------------------------------------------

def test_ccgt_srmc_exceeds_bare_gas_floor_because_carbon_and_vom_are_present():
    """The reconstruction's ordinary-hour cost includes carbon + VOM, which the
    naive gas_floor_alone omits — so it must sit strictly above the bare floor."""
    srmc = ccgt_srmc_gbp_per_mwh(GAS, 2019)
    floor = gas_floor_alone_price_gbp_per_mwh(GAS)
    assert srmc > floor


def test_carbon_term_is_active_not_the_live_engines_zero_default():
    """The live price_engine held carbon at 0.0 at runtime; here the CPS carbon
    (~£18/tCO2) is always live and MOVES the price. Nonzero, monotone in carbon."""
    assert carbon_price_total_gbp_per_tonne(2019) == pytest.approx(CPS_CARBON_GBP_PER_TONNE)
    with_ets = carbon_price_total_gbp_per_tonne(2019, ets_price_gbp_per_tonne=40.0)
    assert with_ets == pytest.approx(CPS_CARBON_GBP_PER_TONNE + 40.0)
    srmc_cps = ccgt_srmc_gbp_per_mwh(GAS, 2019)
    srmc_cps_plus_ets = ccgt_srmc_gbp_per_mwh(GAS, 2019, ets_price_gbp_per_tonne=40.0)
    assert srmc_cps_plus_ets > srmc_cps  # carbon genuinely load-bearing


def test_ordinary_day_marginal_plant_is_a_gas_ccgt():
    """On an ordinary residual-demand hour the reconstructed price equals a gas-CCGT
    SRMC (between the best- and worst-vintage CCGT SRMC), not a peaker or ceiling."""
    demand, renewables = 30000.0, 8000.0  # RD = 22000 -> mid CCGT band
    price = reconstruct_price_gbp_per_mwh(GAS, demand, renewables, 2019)
    best = ccgt_srmc_gbp_per_mwh(GAS, 2019, 0.537)
    assert best <= price <= ccgt_srmc_gbp_per_mwh(GAS, 2019, 0.44)
    assert price < CASH_OUT_CEILING_GBP_PER_MWH


def test_price_rises_with_residual_demand_across_the_ccgt_band():
    """Merit-order shape: a tighter ordinary hour dispatches a less efficient
    marginal CCGT, so price rises monotonically with residual demand."""
    low = reconstruct_price_gbp_per_mwh(GAS, 20000.0, 8000.0, 2019)   # RD=12000
    mid = reconstruct_price_gbp_per_mwh(GAS, 30000.0, 8000.0, 2019)   # RD=22000
    high = reconstruct_price_gbp_per_mwh(GAS, 38000.0, 8000.0, 2019)  # RD=30000
    assert low < mid < high


def test_oversupply_collapses_price_below_the_gas_floor():
    """When renewables flood the system (RD below the must-run floor) price collapses
    toward the curtailment floor — the low/negative prices gas_floor_alone cannot reach."""
    demand, renewables = 20000.0, 18000.0  # RD = 2000, well below must-run floor
    assert 2000.0 < MUST_RUN_FLOOR_MW
    price = reconstruct_price_gbp_per_mwh(GAS, demand, renewables, 2019)
    assert price < gas_floor_alone_price_gbp_per_mwh(GAS)


def test_tight_hours_climb_toward_the_cash_out_ceiling():
    """Above the CCGT band the price climbs convexly toward the £6,000/MWh ceiling —
    the only place a scarcity term survives (it is no longer an ordinary-hour multiplier)."""
    demand, renewables = 52000.0, 3000.0  # RD = 49000, into peaker/reserve
    price = reconstruct_price_gbp_per_mwh(GAS, demand, renewables, 2019)
    ordinary = reconstruct_price_gbp_per_mwh(GAS, 30000.0, 8000.0, 2019)
    assert price > ordinary
    assert price <= CASH_OUT_CEILING_GBP_PER_MWH


# --------------------------------------------------------------------------
# 2. R15 mutation — the reconstructibility control must FAIL on its named defects.
# --------------------------------------------------------------------------

def test_R15_a_wellformed_stack_is_monotone():
    stack = build_merit_stack(GAS, 2019)
    assert is_merit_order_monotone(stack)


def test_R15_a_mis_ordered_stack_fires_the_monotone_check():
    """Frozen-independence mutation #1 (FRAME §3d): a non-monotone / mis-ordered merit
    stack (a peaker priced below a CCGT) must make the check go RED, not pass silently."""
    stack = build_merit_stack(GAS, 2019)
    mutated = list(reversed(stack))  # dearest-first — a broken merit order
    assert not is_merit_order_monotone(mutated)


def test_R15_verdict_is_per_cell_not_aggregate_hiding():
    """Frozen-independence mutation #2 (FRAME §3d, crisis-carry): a verdict graded on
    AGGREGATE lift would FAIL-OPEN when one big winning cell hides a renewables-heavy
    losing cell. The per-cell control must return NOT-MET here despite positive aggregate."""
    from simulation.run_merit_order_reconstructibility import reconstructibility_verdict

    crisis_carry = {
        "2019": {"reconstruction_wins": False, "mae_lift": -3.0},   # the cell that matters, losing
        "2022": {"reconstruction_wins": True, "mae_lift": +20.0},   # crisis cell carries aggregate
    }
    verdict = reconstructibility_verdict(crisis_carry)
    assert verdict["aggregate_lift"] > 0        # aggregate looks good...
    assert verdict["met"] is False              # ...but the per-cell control still fires
    assert "2019" in verdict["losing_cells"]


def test_R15_frozen_ruler_naive_family_is_unchanged_by_identity():
    """Exit criterion 2 / FRAME §3b: the naive baseline family is the RULER, not a knob.
    gas_floor_alone must reproduce gas over the pre-existing THERMAL_EFFICIENCY with zero
    carbon, and the frozen family id must still be present. Editing either to inflate the
    lift is exactly the tuning this pins."""
    from background.fidelity_emitter import _NAIVE_FAMILY_IDS

    assert "gas_floor_alone" in _NAIVE_FAMILY_IDS
    assert gas_floor_alone_price_gbp_per_mwh(30.0) == pytest.approx(30.0 / THERMAL_EFFICIENCY)
    assert THERMAL_EFFICIENCY == 0.50  # the ruler's efficiency is unmoved


# --------------------------------------------------------------------------
# 3. The measured reconstructibility result on REAL data (honest recorded state).
#    Skipped when the caches are absent — the suite never depends on 100MB+ files.
# --------------------------------------------------------------------------

_CELLS_CACHE: dict = {}


def _measured_cells():
    from simulation.run_merit_order_reconstructibility import (
        build_calm_dataset,
        caches_present,
        per_cell_reconstructibility,
    )
    if not caches_present():
        pytest.skip("elexon demand/agws caches absent — reconstructibility measured offline")
    if "cells" not in _CELLS_CACHE:  # load the 100MB+ caches once per module run
        _CELLS_CACHE["cells"] = per_cell_reconstructibility(build_calm_dataset())
    return _CELLS_CACHE["cells"]


def test_reconstruction_wins_in_the_renewables_heavy_calm_cells_2019_2020():
    """The genuine repair: the reconstruction beats gas_floor_alone in exactly the
    renewables-heavy calm cells (2019, 2020) where the live reduced-form posted NEGATIVE
    lift (-0.79, -3.22). This is the structural win, from grounded carbon+VOM+merit
    shape, NOT a tuned constant (R12)."""
    cells = _measured_cells()
    assert cells["2019"]["reconstruction_wins"], cells["2019"]
    assert cells["2020"]["reconstruction_wins"], cells["2020"]


def test_exit_criterion_3a_partial_pending_ets_series_no_tuning():
    """HONEST recorded state (R12: the measurement is a diagnostic, never a target):
    exit criterion 3a is NOT YET fully met — the reconstruction wins a MAJORITY of calm
    cells but not the LOW-carbon early cells, because the flat CPS-only carbon (~£18)
    overshoots them while the real EU-ETS market price was very low. The binding missing
    input is the EU/UK-ETS carbon time-series (DISCOVER §4b NAMED R10 GAP, not fabricated).
    This guards the regression floor (>=3/5 cells) without breaking when a future
    ETS-series build legitimately closes the remaining cells."""
    from simulation.run_merit_order_reconstructibility import reconstructibility_verdict

    cells = _measured_cells()
    verdict = reconstructibility_verdict(cells)
    assert verdict["n_won"] >= 3, verdict                 # regression floor
    assert verdict["aggregate_lift"] == pytest.approx(
        sum(c["mae_lift"] for c in cells.values())
    )


# --------------------------------------------------------------------------
# 4. BUILD-fork re-verification (2026-07-30, W1_6b re-audit) — R15 mutation tests
#    written against the CLAIMED prior state, per criterion-bearing control.
#    Independent re-run confirmed the real-data measurement holds exactly as
#    recorded (3/5 cells, same MAE table) — see docs/fidelity/ evidence doc.
# --------------------------------------------------------------------------

def test_R15_criterion1_control_not_tautological_identical_reconstruction_shows_no_wins(
    monkeypatch,
):
    """Mutation for exit criterion 1's control (`per_cell_reconstructibility` /
    `reconstructibility_verdict`): if the 'reconstruction' collapsed to being
    LITERALLY IDENTICAL to `gas_floor_alone` (the defect this atom exists to repair
    — a reduced-form multiplier indistinguishable from the naive floor), the win
    count must go to exactly ZERO, not silently show a spurious win from floating-
    point noise or a tautological same-source comparison (R15 pattern #1). This
    proves the MAE-lift check genuinely compares two INDEPENDENT computations."""
    import simulation.run_merit_order_reconstructibility as runner
    from sim.merit_order_reconstruction import gas_floor_alone_price_gbp_per_mwh

    def _identical_to_floor(gas, demand, renewables, year, **kw):
        return gas_floor_alone_price_gbp_per_mwh(gas)

    monkeypatch.setattr(runner, "reconstruct_price_gbp_per_mwh", _identical_to_floor)

    rows = [
        {"year": 2019, "gas_price": 20.0, "demand_mw": 30000.0, "renewable_mw": 8000.0, "ssp": 45.0},
        {"year": 2019, "gas_price": 22.0, "demand_mw": 28000.0, "renewable_mw": 9000.0, "ssp": 30.0},
        {"year": 2019, "gas_price": 18.0, "demand_mw": 31000.0, "renewable_mw": 7500.0, "ssp": 60.0},
    ]
    cells = runner.per_cell_reconstructibility(rows)
    verdict = runner.reconstructibility_verdict(cells)
    assert cells["2019"]["mae_lift"] == pytest.approx(0.0)
    assert cells["2019"]["reconstruction_wins"] is False
    assert verdict["met"] is False
    assert verdict["n_won"] == 0


def test_R15_frozen_ruler_survives_a_price_engine_mutation(monkeypatch):
    """R15 mutation for exit criterion 2 (frozen-baseline independence): if someone
    later tunes `price_engine.THERMAL_EFFICIENCY` (e.g. chasing a better-looking
    lift — exactly the R12/R13 violation this ruler exists to prevent), the frozen
    `gas_floor_alone` ruler in THIS module must NOT move, because
    `from sim.price_engine import THERMAL_EFFICIENCY` binds the VALUE at import
    time, not a live read. Proves the ruler is genuinely decoupled from the source
    it freezes against — not silently re-coupled through a shared reference."""
    import sim.price_engine as price_engine
    from sim.merit_order_reconstruction import gas_floor_alone_price_gbp_per_mwh

    before = gas_floor_alone_price_gbp_per_mwh(30.0)
    monkeypatch.setattr(price_engine, "THERMAL_EFFICIENCY", 0.90)  # attempted mutation
    after = gas_floor_alone_price_gbp_per_mwh(30.0)
    assert before == after == pytest.approx(60.0), (
        "the frozen ruler moved when price_engine.THERMAL_EFFICIENCY changed — "
        "it is no longer independent of the value it is meant to freeze against"
    )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "FOUND DEFECT, not fixed here (2026-07-30 W1_6b re-audit): "
        "simulation/run_merit_order_reconstructibility.py is OUTSIDE this BUILD "
        "fork's file_scope (sim/, tests/sim/, docs/fidelity/, docs/market_research/ "
        "only) — the fix belongs to whoever owns simulation/. "
        "reconstructibility_verdict({}) currently returns met=True on EMPTY input "
        "(a FAIL-OPEN, R15 killer pattern #2: a control that passes on missing/"
        "empty data): losing_cells is vacuously empty when there are no cells at "
        "all, so a caller that accidentally hands it malformed/empty data (e.g. a "
        "silent cache-load failure) would see 'exit criterion 3a: MET' with ZERO "
        "measured evidence behind it. This xfail is strict so it flips to a hard "
        "failure — forcing this marker's removal — the moment the guard is added."
    ),
)
def test_R15_KNOWN_GAP_reconstructibility_verdict_fails_open_on_empty_cells():
    from simulation.run_merit_order_reconstructibility import reconstructibility_verdict

    verdict = reconstructibility_verdict({})
    assert verdict["met"] is False, (
        f"expected a not-met verdict on empty input, got vacuous met=True: {verdict}"
    )
