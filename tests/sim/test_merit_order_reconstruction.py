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
    """The live price_engine held carbon at 0.0 at runtime; here carbon is always live
    and MOVES the price. Since 2026-08-03 the default is CPS + the GROUNDED ETS series
    (the named gap closed), so 2019 carries CPS (~£18) + the 2019 EUA price (~£21.6)."""
    from sim.merit_order_reconstruction import ets_carbon_price_gbp_per_tonne

    total_2019 = carbon_price_total_gbp_per_tonne(2019)
    assert total_2019 == pytest.approx(
        CPS_CARBON_GBP_PER_TONNE + ets_carbon_price_gbp_per_tonne(2019)
    )
    assert total_2019 > CPS_CARBON_GBP_PER_TONNE, "the grounded ETS series is inert"
    # An explicit value still OVERRIDES the series (counterfactuals + the old behaviour).
    assert carbon_price_total_gbp_per_tonne(2019, ets_price_gbp_per_tonne=0.0) == pytest.approx(
        CPS_CARBON_GBP_PER_TONNE
    )
    assert carbon_price_total_gbp_per_tonne(2019, ets_price_gbp_per_tonne=40.0) == pytest.approx(
        CPS_CARBON_GBP_PER_TONNE + 40.0
    )
    srmc_cps = ccgt_srmc_gbp_per_mwh(GAS, 2019, ets_price_gbp_per_tonne=0.0)
    srmc_cps_plus_ets = ccgt_srmc_gbp_per_mwh(GAS, 2019, ets_price_gbp_per_tonne=40.0)
    assert srmc_cps_plus_ets > srmc_cps  # carbon genuinely load-bearing


def test_grounded_ets_series_matches_its_cited_provenance():
    """The ETS series is REAL DATA, not a knob: EUA annual volume-weighted auction
    clearing price (EEX primary-auction archive) converted at the ECB annual average
    reference rate, 2016-2020; the DESNZ statutory same-year UK figure for 2021.
    Provenance: docs/market_research/eu_uk_ets_carbon_price_series_2026-08-03.md.
    This pins the DERIVATION (EUR x FX), so a silent edit to either input is caught."""
    from sim.merit_order_reconstruction import (
        ECB_GBP_PER_EUR_ANNUAL_AVERAGE_BY_YEAR,
        ETS_SERIES_NAMED_GAP_YEARS,
        EUA_AUCTION_VWAP_EUR_PER_TONNE_BY_YEAR,
        ets_carbon_price_gbp_per_tonne,
    )

    for year in (2016, 2017, 2018, 2019, 2020):
        assert ets_carbon_price_gbp_per_tonne(year) == pytest.approx(
            EUA_AUCTION_VWAP_EUR_PER_TONNE_BY_YEAR[year]
            * ECB_GBP_PER_EUR_ANNUAL_AVERAGE_BY_YEAR[year]
        )
    # The real EU-ETS carbon price ROSE sharply over the calm window (~EUR 5 -> ~EUR 25).
    # That is a fact about the world and the reason a FLAT carbon term mis-tracked it.
    assert (ets_carbon_price_gbp_per_tonne(2016)
            < ets_carbon_price_gbp_per_tonne(2018)
            < ets_carbon_price_gbp_per_tonne(2019))
    assert ets_carbon_price_gbp_per_tonne(2021) == pytest.approx(47.96)  # DESNZ, same-year
    # The still-open gap years return 0.0 and are NAMED as a gap, never claimed as zero.
    for year in ETS_SERIES_NAMED_GAP_YEARS:
        assert ets_carbon_price_gbp_per_tonne(year) == 0.0


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


def _measured_rows():
    """The real joined calm-window dataset, loaded ONCE per module run (100MB+ caches)."""
    from simulation.run_merit_order_reconstructibility import build_calm_dataset, caches_present

    if not caches_present():
        pytest.skip("elexon demand/agws caches absent — reconstructibility measured offline")
    if "rows" not in _CELLS_CACHE:
        _CELLS_CACHE["rows"] = build_calm_dataset()
    return _CELLS_CACHE["rows"]


def _measured_cells():
    from simulation.run_merit_order_reconstructibility import per_cell_reconstructibility

    rows = _measured_rows()
    if "cells" not in _CELLS_CACHE:
        _CELLS_CACHE["cells"] = per_cell_reconstructibility(rows)
    return _CELLS_CACHE["cells"]


def test_reconstruction_wins_in_the_renewables_heavy_calm_cells_2019_2020():
    """The genuine repair: the reconstruction beats gas_floor_alone in exactly the
    renewables-heavy calm cells (2019, 2020) where the live reduced-form posted NEGATIVE
    lift (-0.79, -3.22). This is the structural win, from grounded carbon+VOM+merit
    shape, NOT a tuned constant (R12)."""
    cells = _measured_cells()
    assert cells["2019"]["reconstruction_wins"], cells["2019"]
    assert cells["2020"]["reconstruction_wins"], cells["2020"]


def test_exit_criterion_3a_is_honestly_2_of_5_with_the_grounded_carbon_series():
    """HONEST recorded state (R12: the measurement is a DIAGNOSTIC, never a target).

    Exit criterion 3a is NOT met: 2 of 5 calm cells. It was 3/5 while carbon was the
    flat CPS-only ~£18 (the ETS gap), and wiring the REAL, grounded EU-ETS series on
    2026-08-03 moved it to 2/5 — it got WORSE on this criterion.

    That is the correct and deliberate outcome, and it FALSIFIES the FRAME's stated
    expectation that the ETS series would close 2016/2017 'without any curve-fitting'.
    The real EUA price is strictly POSITIVE in every year (£4.31/t in 2016 rising to
    £21.81/t in 2020), so adding it can only RAISE the reconstructed price — it cannot
    reduce an over-prediction. The FRAME's hypothesis was simply wrong about the sign.

    Under R13 the series STAYS anyway: a GB CCGT in 2019 genuinely paid CPS + EUA
    (~£39.6/tCO2 total). Modelling that as zero is factually false about the world, and
    reverting it to protect a 3/5 score would be tuning an INPUT to flatter an OUTPUT —
    exactly what R12/R13 forbid. 3/5 bought by pretending the EU ETS did not exist is
    worth less than an honest 2/5. The real diagnostic is the bias STRUCTURE, pinned in
    the next test — not this count."""
    from simulation.run_merit_order_reconstructibility import reconstructibility_verdict

    cells = _measured_cells()
    verdict = reconstructibility_verdict(cells)
    assert verdict["met"] is False
    assert verdict["n_won"] == 2, verdict
    assert sorted(verdict["losing_cells"]) == ["2016", "2017", "2018"], verdict
    # The two renewables-heavy cells the structural repair EXISTS to fix still win.
    assert cells["2019"]["reconstruction_wins"] and cells["2020"]["reconstruction_wins"]
    assert verdict["aggregate_lift"] == pytest.approx(
        sum(c["mae_lift"] for c in cells.values())
    )


def test_grounded_carbon_makes_the_bias_a_LEVEL_offset_not_a_TREND_error():
    """The finding that actually matters, and the reason the grounded series stays
    despite costing a cell on criterion 3a.

    With flat CPS-only carbon the reconstruction's mean signed error vs real SSP SWINGS
    SIGN across the window (+3.2 in 2016 -> -5.0 in 2020): the model mis-tracks how the
    world CHANGED. With the real, correctly time-varying carbon series the error becomes
    uniformly positive and far flatter (+3.0..+6.3) — a near-constant ~+£4.7/MWh level
    offset. Adding a true input converted a TREND error into a LEVEL error, which is
    precisely what a genuine fidelity improvement looks like even when an MAE-vs-naive-
    floor criterion scores it lower.

    The residual level offset has a named, plausible cause NOT yet addressed: SSP is the
    imbalance cash-out SELL price, which sits systematically below the wholesale marginal
    energy price an SRMC stack reconstructs. That is a measurement-validity question about
    criterion 3a's construction — recorded here, deliberately NOT used to rewrite the
    criterion in this atom's own favour."""
    import numpy as np

    from sim.price_engine import DISPATCHABLE_CAPACITY_MW, X_TIGHT

    rows = _measured_rows()
    gas = np.array([r["gas_price"] for r in rows])
    dem = np.array([r["demand_mw"] for r in rows])
    ren = np.array([r["renewable_mw"] for r in rows])
    ssp = np.array([r["ssp"] for r in rows])
    yr = np.array([r["year"] for r in rows])
    ordinary = (dem - ren) / DISPATCHABLE_CAPACITY_MW <= X_TIGHT

    def per_cell_bias(ets):
        rec = np.array([
            reconstruct_price_gbp_per_mwh(g, d, r, int(y), ets_price_gbp_per_tonne=ets)
            for g, d, r, y in zip(gas, dem, ren, yr)
        ])
        return {int(y): float((rec[m] - ssp[m]).mean())
                for y in sorted(set(int(v) for v in yr))
                for m in [(yr == y) & ordinary]}

    cps_only = per_cell_bias(0.0)      # the prior state: flat carbon
    grounded = per_cell_bias(None)     # the real, time-varying series

    cps_spread = max(cps_only.values()) - min(cps_only.values())
    grounded_spread = max(grounded.values()) - min(grounded.values())
    assert grounded_spread < cps_spread, (
        f"grounded carbon did NOT tighten the bias spread "
        f"(CPS-only {cps_spread:.2f} vs grounded {grounded_spread:.2f}) — the claim that "
        f"the real series converts a trend error into a level offset no longer holds"
    )
    # CPS-only mis-tracks the trend so badly the error changes SIGN across the window...
    assert min(cps_only.values()) < 0 < max(cps_only.values())
    # ...while the grounded series leaves a consistently-signed offset in every cell.
    assert all(b > 0 for b in grounded.values()), grounded


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


def test_R15_reconstructibility_verdict_does_not_fail_open_on_empty_cells():
    """CLOSED 2026-08-03 (was a strict-xfail KNOWN GAP pinned by the 2026-07-30 re-audit).

    `reconstructibility_verdict({})` used to return met=True on EMPTY input — R15 killer
    pattern #2, a control that passes on missing data: `losing_cells` is vacuously empty
    when there are no cells at all, so a caller handed empty/malformed data (a silent
    cache-load failure, a broken join) read 'exit criterion 3a: MET' with ZERO measured
    evidence. A verdict with no evidence is NOT MET, never MET."""
    from simulation.run_merit_order_reconstructibility import reconstructibility_verdict

    verdict = reconstructibility_verdict({})
    assert verdict["met"] is False, (
        f"expected a not-met verdict on empty input, got vacuous met=True: {verdict}"
    )
    assert verdict["vacuous"] is True
    assert verdict["n_cells"] == 0 and verdict["n_won"] == 0
    assert "zero evidence" in verdict["not_met_reason"]


def test_R15_reconstructibility_verdict_rejects_non_finite_evidence():
    """Non-finite (NaN/inf) evidence is rejected FIRST, before any comparison. Without
    this, a NaN `mae_lift` sums into `aggregate_lift` as NaN while the per-cell win flags
    could still be all-True, yielding met=True off unmeasurable data."""
    from simulation.run_merit_order_reconstructibility import reconstructibility_verdict

    nan_cells = {
        "2019": {"reconstruction_wins": True, "mae_lift": float("nan")},
        "2020": {"reconstruction_wins": True, "mae_lift": +2.0},
    }
    verdict = reconstructibility_verdict(nan_cells)
    assert verdict["met"] is False, f"NaN evidence produced a passing verdict: {verdict}"
    assert verdict["vacuous"] is True
    assert "2019" in verdict["not_met_reason"]

    # ...and a cell missing the graded key entirely is malformed, not a silent pass.
    assert reconstructibility_verdict({"2019": {"mae_lift": 1.0}})["met"] is False


# --------------------------------------------------------------------------
# 5. R10 CLASS GUARD — the vacuous-evidence control FAMILY (2026-08-03).
#    The empty-input fail-open above is a CLASS defect, not an instance: R10
#    forbids closing it with an instance fix. These tests grade every judgement
#    function in this atom, and DISCOVER the family by introspection so a new
#    unguarded control cannot join the class silently.
# --------------------------------------------------------------------------

_FAMILY_MODULES = (
    "sim.merit_order_reconstruction",
    "simulation.run_merit_order_reconstructibility",
)


def _discover_control_functions():
    """Every public callable DEFINED IN one of the family modules whose name carries a
    judgement marker (verdict / monotone / reconstructibility). Introspection, not a
    hand-kept list — that is what makes the class guard automatic."""
    import importlib
    import inspect

    from sim.merit_order_reconstruction import CONTROL_NAME_MARKERS

    found = set()
    for mod_name in _FAMILY_MODULES:
        module = importlib.import_module(mod_name)
        for name, obj in vars(module).items():
            if name.startswith("_") or not inspect.isfunction(obj):
                continue
            if obj.__module__ != mod_name:  # imported symbol, graded in its own module
                continue
            if any(marker in name for marker in CONTROL_NAME_MARKERS):
                found.add(f"{mod_name}.{name}")
    return found


def test_R10_class_registry_matches_the_discovered_control_family():
    """The registry and reality must agree. If someone adds a new judgement function
    (anything named *verdict* / *monotone* / *reconstructibility*) without registering
    and guarding it, this FAILS — so the vacuity class cannot silently regrow."""
    from sim.merit_order_reconstruction import VACUITY_GUARDED_CONTROLS

    discovered = _discover_control_functions()
    registered = set(VACUITY_GUARDED_CONTROLS)
    assert discovered == registered, (
        "the vacuous-evidence control family drifted from its registry.\n"
        f"  unregistered (add a vacuity guard + register): {sorted(discovered - registered)}\n"
        f"  registered but gone (drop from the registry):  {sorted(registered - discovered)}"
    )
    assert discovered, "introspection found NO controls — the discovery rule itself broke"


def test_R10_every_control_in_the_family_is_not_met_on_empty_evidence():
    """The CLASS invariant: no member of this family may return a PASSING/vacuously-true
    answer when handed empty evidence. Each entry is the control's own null case."""
    from simulation.run_merit_order_reconstructibility import (
        per_cell_reconstructibility,
        reconstructibility_verdict,
    )

    from sim.merit_order_reconstruction import VACUITY_GUARDED_CONTROLS

    empty_case = {
        "sim.merit_order_reconstruction.is_merit_order_monotone":
            lambda: is_merit_order_monotone([]),
        "simulation.run_merit_order_reconstructibility.per_cell_reconstructibility":
            lambda: per_cell_reconstructibility([]),
        "simulation.run_merit_order_reconstructibility.reconstructibility_verdict":
            lambda: reconstructibility_verdict({}),
    }
    assert set(empty_case) == set(VACUITY_GUARDED_CONTROLS), (
        "a registered control has no empty-evidence case here — the class guard would "
        "silently skip it"
    )

    for name, probe in empty_case.items():
        result = probe()
        truthy = result.get("met", False) if isinstance(result, dict) else bool(result)
        assert not truthy, f"{name} PASSED on empty evidence (fail-open): {result}"


def test_R10_every_control_in_the_family_rejects_non_finite_evidence():
    """The CLASS invariant, second half: NaN/inf must be rejected BEFORE any comparison.
    `nan < x` is False and `all([])` is True — both would otherwise decide a verdict by
    accident. Reject-first makes the not-met a DECISION, with a reason."""
    from simulation.run_merit_order_reconstructibility import reconstructibility_verdict

    from sim.merit_order_reconstruction import MeritPlant

    nan_stack = [
        MeritPlant("must_run", 0.0, 8000.0),
        MeritPlant("ccgt_nan", float("nan"), 30000.0),
        MeritPlant("peaker", 90.0, 7000.0),
    ]
    assert is_merit_order_monotone(nan_stack) is False
    inf_stack = [
        MeritPlant("must_run", 0.0, 8000.0),
        MeritPlant("ccgt_inf", float("inf"), 30000.0),
    ]
    assert is_merit_order_monotone(inf_stack) is False

    assert reconstructibility_verdict(
        {"2019": {"reconstruction_wins": True, "mae_lift": float("inf")}}
    )["met"] is False


def test_R10_single_plant_stack_carries_no_ordering_evidence():
    """The named sub-defect inside `is_merit_order_monotone`: `zip(s, s[1:])` is EMPTY
    for a 0- or 1-element stack and `all([])` is True, so the unguarded control PASSED
    with no pair to order. Ordering is a claim about a pair."""
    from sim.merit_order_reconstruction import MeritPlant

    assert is_merit_order_monotone([]) is False
    assert is_merit_order_monotone([MeritPlant("lonely", 42.0, 1000.0)]) is False
    # ...but a genuine two-plant ordering still grades normally, both ways.
    cheap, dear = MeritPlant("a", 10.0, 1.0), MeritPlant("b", 20.0, 1.0)
    assert is_merit_order_monotone([cheap, dear]) is True
    assert is_merit_order_monotone([dear, cheap]) is False


def test_R10_per_cell_grading_marks_non_finite_cells_as_unmeasured_not_won():
    """`per_cell_reconstructibility` must not let a NaN-bearing cell score a win by
    accident, and must SAY the evidence was non-finite rather than hiding it as a loss."""
    from simulation.run_merit_order_reconstructibility import (
        per_cell_reconstructibility,
        reconstructibility_verdict,
    )

    rows = [
        {"year": 2019, "gas_price": 20.0, "demand_mw": 30000.0,
         "renewable_mw": 8000.0, "ssp": float("nan")},
        {"year": 2019, "gas_price": 21.0, "demand_mw": 29000.0,
         "renewable_mw": 8500.0, "ssp": 40.0},
    ]
    cells = per_cell_reconstructibility(rows)
    assert cells["2019"]["evidence_finite"] is False
    assert cells["2019"]["reconstruction_wins"] is False
    # ...and it propagates: the verdict refuses the cell rather than summing a NaN.
    assert reconstructibility_verdict(cells)["met"] is False


# --------------------------------------------------------------------------
# 6. LIVE WIRING into sim/price_engine.py (residual (c), 2026-08-03).
#    The engine was a standalone offline measurement module; it is now reachable
#    on the live simulated price path via `synthetic_price(engine="merit_order")`.
#    The DEFAULT is deliberately unchanged — see the `synthetic_price` docstring
#    for the fidelity reasoning (criterion 1 is 3/5; 2016/2017 lose pending the
#    ETS carbon series). These tests pin BOTH halves: the default did not move,
#    and the new path really does reach the SRMC engine.
# --------------------------------------------------------------------------

def test_default_price_engine_is_byte_identical_to_the_pre_wiring_reduced_form():
    """R13: wiring a new engine in must not silently move the CALIBRATED baseline.
    The default path must reproduce gas_floor -> system_margin_price exactly."""
    from sim.price_engine import (
        ENGINE_REDUCED_FORM,
        gas_floor_price,
        synthetic_price,
        system_margin_price,
    )

    for gas, demand, renewables in [
        (20.0, 30000.0, 8000.0), (45.0, 41000.0, 3000.0), (12.0, 22000.0, 17000.0),
    ]:
        expected = system_margin_price(gas_floor_price(gas), demand, renewables)
        assert synthetic_price(gas, demand, renewables) == expected
        assert synthetic_price(gas, demand, renewables, engine=ENGINE_REDUCED_FORM) == expected


def test_merit_order_engine_is_reachable_on_the_live_price_path():
    """Residual (c): 'ordinary-day SSP substantially reconstructible' must be true of
    the LIVE price path, not only of an offline analysis module. Selecting the engine
    must actually dispatch the SRMC stack — and must DIFFER from the reduced form,
    otherwise the wiring is decorative."""
    from sim.price_engine import ENGINE_MERIT_ORDER, synthetic_price

    gas, demand, renewables, year = 20.0, 30000.0, 8000.0, 2019
    wired = synthetic_price(gas, demand, renewables, year=year, engine=ENGINE_MERIT_ORDER)
    direct = reconstruct_price_gbp_per_mwh(gas, demand, renewables, year)
    assert wired == pytest.approx(direct)
    assert wired != pytest.approx(synthetic_price(gas, demand, renewables, year=year))


def test_merit_order_engine_passes_the_ets_carbon_series_through():
    """The NAMED GAP's seam: when the EU/UK-ETS series is sourced, it must reach the
    live path without any re-fit. A passthrough that silently dropped the argument
    would make the future ETS build a no-op."""
    from sim.price_engine import ENGINE_MERIT_ORDER, synthetic_price

    base = synthetic_price(20.0, 30000.0, 8000.0, year=2016, engine=ENGINE_MERIT_ORDER)
    with_ets = synthetic_price(20.0, 30000.0, 8000.0, year=2016,
                               engine=ENGINE_MERIT_ORDER, ets_price_gbp_per_tonne=25.0)
    assert with_ets > base, "the ETS carbon passthrough is inert — the gap cannot close"


def test_R15_merit_order_engine_fails_closed_on_a_missing_year():
    """R15 fail-open guard on the new seam: the SRMC stack is TIME-INDEXED (per-year
    DUKES efficiencies/emission factors). Silently defaulting a missing year would
    price every period off one arbitrary vintage and still look like it worked."""
    from sim.price_engine import ENGINE_MERIT_ORDER, synthetic_price

    with pytest.raises(ValueError, match="requires an explicit `year`"):
        synthetic_price(20.0, 30000.0, 8000.0, engine=ENGINE_MERIT_ORDER)


def test_R15_unknown_price_engine_is_rejected_not_silently_defaulted():
    """A typo'd engine name must RAISE, not fall through to the default — a silent
    fallback is the fail-open that makes 'we switched engines' unverifiable."""
    from sim.price_engine import synthetic_price

    with pytest.raises(ValueError, match="unknown price engine"):
        synthetic_price(20.0, 30000.0, 8000.0, year=2019, engine="merit-order")
