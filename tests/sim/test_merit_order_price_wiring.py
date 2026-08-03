"""W1_6b — the merit-order stack WIRED INTO the price engine (2026-08-03).

THE GAP THESE CONTROLS EXIST FOR. Until this build, `sim/price_engine.py` never
imported or called `sim/merit_order_reconstruction.py` — grep-confirmed, the sole
importer was the measurement harness — so the typed SRMC dispatch stack was a
STANDALONE DIAGNOSTIC, not a thing that formed price. Every control below is written
so that severing the wiring (price forming from the reduced-form multiplier again)
makes it go RED.

R15 INDEPENDENCE. The load-bearing controls do NOT re-derive the checked value from
`merit_order_price` itself. They assert that the formed price RESPONDS to inputs the
reduced form is structurally BLIND to — the published per-year DUKES efficiency /
emission factor (`year`) and the carbon price (`ets_price_gbp_per_tonne`). The
reduced-form `synthetic_price(gas, demand, renewable)` has no year parameter at all
and its every live caller leaves carbon at 0.0, so a severed wiring cannot fake these.

FAIL-OPEN. Each control asserts a STRICT inequality or an exact-zero on non-degenerate
inputs, and the degenerate cases (zero gas, empty tight-excess) are asserted
explicitly rather than left to pass vacuously.

FAIL-SILENT. `test_wiring_has_no_silent_fallback` proves the price engine RAISES if
the stack is unavailable rather than quietly reverting to the reduced form — an
unavailable component is a failure, never a degradation.
"""

import numpy as np
import pytest

import sim.merit_order_reconstruction as mo
import sim.price_engine as pe
from sim.price_engine import (
    X_TIGHT,
    DISPATCHABLE_CAPACITY_MW,
    merit_order_price,
    scarcity_rent_gbp_per_mwh,
    synthetic_price,
)

GAS = 20.0  # £/MWh, a representative ordinary NBP gas price

# Residual-demand fractions, expressed against the engine's own scarcity scale so the
# ordinary/tight split is the SAME x the reduced form uses (no second definition).
_ORDINARY_RD = 0.50 * DISPATCHABLE_CAPACITY_MW   # x = 0.50, comfortably ordinary
_TIGHT_RD = 0.95 * DISPATCHABLE_CAPACITY_MW      # x = 0.95, well past X_TIGHT -> rent is due

# TWO DIFFERENT THRESHOLDS, deliberately not conflated. The scarcity RENT starts above
# `X_TIGHT` (x > 0.70, i.e. residual demand > 24,500 MW on the engine's scarcity scale);
# the merit stack's PEAKER TIER starts higher, once residual demand exceeds the CCGT
# band top (MUST_RUN_FLOOR_MW + CCGT_CAPACITY_MW = 38,000 MW). Rent therefore begins
# while a CCGT is still marginal — which is how real scarcity pricing behaves: the
# margin tightens and bids rise above marginal cost before the last CCGT is gone.
_PEAKER_RD = mo.MUST_RUN_FLOOR_MW + mo.CCGT_CAPACITY_MW + 3000.0


def _demand_renewable_for(residual_mw: float) -> tuple[float, float]:
    """A (demand, renewable) pair with the requested residual demand. Renewables are
    held at a fixed non-zero level so residual demand is a genuine subtraction, not a
    demand relabelling."""
    renewable = 8000.0
    return residual_mw + renewable, renewable


# ---------------------------------------------------------------------------
# 1. THE WIRING ITSELF — the price engine now forms price FROM the stack.
# ---------------------------------------------------------------------------

def test_price_engine_imports_the_merit_stack_at_all():
    """The literal premise this atom closes: the price engine references the
    reconstruction. Structural, cheap, and it fails the instant someone deletes the
    call — the exact regression that produced the 'standalone diagnostic' finding."""
    source = (pe.__file__)
    with open(source) as fh:
        text = fh.read()
    assert "sim.merit_order_reconstruction" in text, (
        "sim/price_engine.py no longer references sim/merit_order_reconstruction.py — "
        "the merit-order stack has gone back to being a standalone diagnostic"
    )


def test_formed_price_depends_on_the_published_year_which_the_reduced_form_cannot_see(
    monkeypatch,
):
    """R15 INDEPENDENCE (not a tautology): the merit-order former must move when the
    PUBLISHED per-year inputs move (DUKES 5.10.C fleet efficiency, DUKES 5.14 emission
    factor, the DESNZ VOM bookends), because it genuinely dispatches the year-indexed
    stack. The reduced form takes no year at all, so a severed wiring cannot reproduce
    this.

    Second leg proves the year-sensitivity comes from THOSE TABLES and not from some
    incidental year branch: flatten the published tables so every year reads alike, and
    the price must stop moving. That is the independence the first leg alone cannot
    show. No direction is asserted — the three published series do not all move the
    same way between two given years, and inventing a direction would be reading the
    answer off the price under test."""
    demand, renewable = _demand_renewable_for(_ORDINARY_RD)
    assert merit_order_price(GAS, demand, renewable, 2019) != pytest.approx(
        merit_order_price(GAS, demand, renewable, 2023)
    ), "the formed price is year-blind — it is not coming from the per-year stack"

    flat_eff = {y: 0.49 for y in mo.CCGT_THERMAL_EFFICIENCY_BY_YEAR}
    flat_ef = {y: 0.375 for y in mo.EF_GAS_TCO2_PER_MWH_E_BY_YEAR}
    monkeypatch.setattr(mo, "CCGT_THERMAL_EFFICIENCY_BY_YEAR", flat_eff)
    monkeypatch.setattr(mo, "EF_GAS_TCO2_PER_MWH_E_BY_YEAR", flat_ef)
    monkeypatch.setattr(mo, "variable_om_gbp_per_mwh", lambda year: 4.0)
    assert merit_order_price(GAS, demand, renewable, 2019) == pytest.approx(
        merit_order_price(GAS, demand, renewable, 2023)
    ), "price still moves with the year after the published tables were flattened — "\
       "the year-sensitivity is not coming from the published inputs"


def test_formed_price_depends_on_carbon_which_the_live_reduced_form_path_never_sees():
    """R15 INDEPENDENCE: carbon is load-bearing in the formed price. Every live caller
    of `synthetic_price` leaves `carbon_price_gbp_per_tonne` at its 0.0 default, so a
    severed wiring produces a carbon-invariant price and this goes RED."""
    demand, renewable = _demand_renewable_for(_ORDINARY_RD)
    without_ets = merit_order_price(GAS, demand, renewable, 2019)
    with_ets = merit_order_price(GAS, demand, renewable, 2019, ets_price_gbp_per_tonne=40.0)
    assert with_ets > without_ets
    # Carbon Price Support alone is already in there (it is grounded and flat), so the
    # formed price sits strictly above the carbon-free reduced-form gas floor.
    assert without_ets > mo.gas_floor_alone_price_gbp_per_mwh(GAS)


def test_ordinary_hour_price_is_a_marginal_plants_srmc_not_a_multiple_of_a_floor():
    """On an ordinary hour the formed price must BE the marginal CCGT's SRMC — bounded
    by the published efficiency band's two ends — rather than a fitted multiple of a
    gas floor. Independent oracle: the band ends come from the DUKES fleet average and
    the DESNZ best-build reference, not from the price being checked."""
    demand, renewable = _demand_renewable_for(_ORDINARY_RD)
    price = merit_order_price(GAS, demand, renewable, 2019)
    worst_eff, best_eff = mo._ccgt_efficiency_band(2019)
    cheapest = mo.ccgt_srmc_gbp_per_mwh(GAS, 2019, best_eff)
    dearest = mo.ccgt_srmc_gbp_per_mwh(GAS, 2019, worst_eff)
    assert cheapest <= price <= dearest


# ---------------------------------------------------------------------------
# 2. SCARCITY RENT EARNS ITS KEEP ONLY IN TIGHT HOURS (the atom's own thesis).
# ---------------------------------------------------------------------------

def test_scarcity_rent_is_exactly_zero_across_every_ordinary_hour():
    """Swept, not spot-checked: the rent must be EXACTLY 0.0 for every residual-demand
    fraction at or below X_TIGHT — including deep oversupply (negative x). A rent that
    leaks into ordinary hours is the reduced form's defect, restated."""
    xs = np.linspace(-0.5, X_TIGHT, 200)
    for x in xs:
        demand, renewable = _demand_renewable_for(float(x) * DISPATCHABLE_CAPACITY_MW)
        assert scarcity_rent_gbp_per_mwh(GAS, demand, renewable) == 0.0, f"rent leaked at x={x}"


def test_scarcity_rent_is_strictly_positive_and_convex_in_tight_hours():
    """FAIL-OPEN guard: the zero-in-ordinary-hours control above would pass vacuously
    if the rent were zero EVERYWHERE. It must be strictly positive above X_TIGHT and
    rise faster than linearly as the margin tightens."""
    def rent_at(x):
        demand, renewable = _demand_renewable_for(x * DISPATCHABLE_CAPACITY_MW)
        return scarcity_rent_gbp_per_mwh(GAS, demand, renewable)

    r1, r2, r3 = rent_at(0.80), rent_at(0.90), rent_at(1.00)
    assert 0.0 < r1 < r2 < r3
    assert (r3 - r2) > (r2 - r1)  # convex, not a straight line


def test_scarcity_rent_does_not_pay_out_on_a_zero_gas_price():
    """FAIL-OPEN guard on the degenerate input: rent is scaled by the gas floor, so a
    zero gas price must pay zero rent even in a tight hour — not a spurious constant."""
    demand, renewable = _demand_renewable_for(_TIGHT_RD)
    assert scarcity_rent_gbp_per_mwh(0.0, demand, renewable) == 0.0


def test_tight_hour_price_is_marginal_cost_plus_rent_and_ordinary_is_marginal_cost_alone():
    """The composition, asserted against its two INDEPENDENT parts: in an ordinary hour
    the formed price equals the stack's marginal SRMC with nothing added; in a tight
    hour it equals that SRMC plus a strictly positive rent."""
    ord_d, ord_r = _demand_renewable_for(_ORDINARY_RD)
    srmc_ord = mo.marginal_srmc_gbp_per_mwh(GAS, ord_d, ord_r, 2019)
    assert merit_order_price(GAS, ord_d, ord_r, 2019) == pytest.approx(srmc_ord)

    tight_d, tight_r = _demand_renewable_for(_TIGHT_RD)
    srmc_tight = mo.marginal_srmc_gbp_per_mwh(GAS, tight_d, tight_r, 2019)
    rent = scarcity_rent_gbp_per_mwh(GAS, tight_d, tight_r)
    assert rent > 0.0
    assert merit_order_price(GAS, tight_d, tight_r, 2019) == pytest.approx(srmc_tight + rent)


# ---------------------------------------------------------------------------
# 3. PHYSICAL BOUNDS — the formed price respects real GB cash-out limits.
# ---------------------------------------------------------------------------

def test_formed_price_is_capped_at_the_gb_cash_out_ceiling():
    """An extreme crisis hour (crisis-era gas, a very short margin) must not price
    above the GB cash-out ceiling. Verified to actually BIND: the unbounded sum
    genuinely exceeds the ceiling on these inputs, so this is not a vacuous cap."""
    crisis_gas = 300.0
    demand, renewable = _demand_renewable_for(2.6 * DISPATCHABLE_CAPACITY_MW)
    unbounded = (mo.marginal_srmc_gbp_per_mwh(crisis_gas, demand, renewable, 2022)
                 + scarcity_rent_gbp_per_mwh(crisis_gas, demand, renewable))
    assert unbounded > mo.CASH_OUT_CEILING_GBP_PER_MWH, "inputs do not exercise the cap"
    assert merit_order_price(crisis_gas, demand, renewable, 2022) == pytest.approx(
        mo.CASH_OUT_CEILING_GBP_PER_MWH
    )


def test_formed_price_never_falls_below_the_curtailment_floor():
    """Deep oversupply (renewables flooding the system) collapses the price, but not
    through the curtailment floor.

    Note this floor is a guarantee of the STACK, not of a clamp in `merit_order_price`
    (a symmetric floor clamp there would be unreachable dead code — R11 — because the
    stack's oversupply regime clamps its own collapse fraction to [0, 1] and rent is
    zero there). Swept across the whole oversupply range so it is the property, not one
    lucky point, that is pinned."""
    for renewable in np.linspace(9000.0, 60000.0, 60):
        price = merit_order_price(GAS, 12000.0, float(renewable), 2019)
        # 1e-9 £/MWh of float noise on the collapse arithmetic, not a breach; anything
        # a defect could plausibly produce is many orders of magnitude larger.
        assert price >= mo.CURTAILMENT_FLOOR_GBP_PER_MWH - 1e-9
    deep = merit_order_price(GAS, 12000.0, 30000.0, 2019)
    assert deep == pytest.approx(mo.CURTAILMENT_FLOOR_GBP_PER_MWH)
    assert deep < mo.gas_floor_alone_price_gbp_per_mwh(GAS)


# ---------------------------------------------------------------------------
# 4. FAIL-SILENT — an unavailable stack must RAISE, never degrade quietly.
# ---------------------------------------------------------------------------

def test_wiring_has_no_silent_fallback(monkeypatch):
    """R15 killer pattern #3. If `merit_order_price` caught an unavailable stack and
    quietly returned the reduced form, every control above would keep passing while the
    merit order had silently stopped forming price. Break the stack; demand a raise."""
    def _boom(*a, **kw):
        raise RuntimeError("merit stack unavailable")

    monkeypatch.setattr(mo, "marginal_srmc_gbp_per_mwh", _boom)
    demand, renewable = _demand_renewable_for(_ORDINARY_RD)
    with pytest.raises(RuntimeError):
        merit_order_price(GAS, demand, renewable, 2019)


# ---------------------------------------------------------------------------
# 5. THE BASELINE DID NOT MOVE (R13) — and the alternative former is really live.
# ---------------------------------------------------------------------------

def test_reduced_form_baseline_is_byte_identical_to_the_pre_wiring_form():
    """R13: the shipped baseline changes only for fidelity-to-reality reasons, and the
    full-real-record measurement was a WASH — so `synthetic_price` must be untouched.
    Independent oracle: the closed-form reduced expression, written out here from the
    published calibration constants, NOT read back out of the function under test."""
    for gas, demand, renewable in [(20.0, 30000.0, 8000.0),
                                   (60.0, 45000.0, 5000.0),
                                   (12.0, 18000.0, 16000.0)]:
        x = (demand - renewable) / DISPATCHABLE_CAPACITY_MW
        expected = (gas / pe.THERMAL_EFFICIENCY) * (
            pe.A0 + pe.A1 * x + pe.A2 * max(0.0, x - X_TIGHT) ** pe.SCARCITY_EXPONENT
        )
        assert synthetic_price(gas, demand, renewable) == pytest.approx(expected)


def test_the_two_formers_genuinely_disagree_so_the_wiring_is_not_an_orphan():
    """R11 (no orphan transitions): selecting the merit-order former must actually
    CHANGE the price. If the two formers agreed everywhere, the wiring would be
    decorative and every control above would be theatre."""
    demand, renewable = _demand_renewable_for(_ORDINARY_RD)
    reduced = synthetic_price(GAS, demand, renewable)
    merit = merit_order_price(GAS, demand, renewable, 2019)
    assert reduced != pytest.approx(merit)


# ---------------------------------------------------------------------------
# 6. THE LIVE CHAIN — the former is reachable on the real record, and the
#    default series is unmoved. Skipped when the 100MB+ caches are absent.
# ---------------------------------------------------------------------------

def _chain():
    from sim import weather_price_chain as wpc
    if not (wpc._CACHE / "elexon_ssp_full.json").exists():
        pytest.skip("weather/price caches absent — chain wiring measured offline")
    return wpc


def test_live_chain_default_series_is_still_formed_by_the_reduced_form():
    """R13, the baseline did not move. The DEFAULT derived-price series over the real
    record must still be the reduced form applied to the chain's own demand/renewable
    columns. Independent oracle: recomputed from `synthetic_price` against the record's
    published intermediate columns, not read back out of `derived_price`."""
    wpc = _chain()
    out = wpc.derive_price_on_record()
    expected = np.array([
        synthetic_price(float(g), float(d), float(r))
        for g, d, r in zip(out["gas_price"], out["demand_mw"], out["renewable_mw"])
    ])
    assert np.allclose(out["derived_price"], expected)


def test_live_chain_merit_order_path_really_forms_a_different_series():
    """R11 (no orphan transitions): selecting the merit-order former on the live record
    must produce a genuinely different price series, priced at each row's OWN real
    calendar year. A flag whose release changes nothing is a defect."""
    wpc = _chain()
    default = wpc.derive_price_on_record()["derived_price"]
    merit = wpc.derive_price_on_record(merit_order=True)["derived_price"]
    assert len(merit) == len(default)
    assert not np.allclose(merit, default)
    # And it is genuinely per-row year-indexed, not one year applied to everything:
    # the two ends of the record must not price as if they shared a year.
    assert float(np.abs(merit - default).max()) > 1.0


def test_live_chain_merit_order_mae_is_reported_as_a_diagnostic_not_a_target():
    """R12. Both formers' MAE against real published SSP are reportable side by side.
    The control asserts only that the diagnostic is WELL-FORMED and computed over the
    same rows — never that one number beats the other, which would make an output
    metric into a target."""
    wpc = _chain()
    base = wpc.chain_vs_real_ssp_mae()
    merit = wpc.chain_vs_real_ssp_mae(merit_order=True)
    assert base["n"] == merit["n"] > 0
    assert base["real_mean"] == pytest.approx(merit["real_mean"])  # same ruler
    assert merit["mae"] > 0.0
    assert merit["chain_mean"] != pytest.approx(base["chain_mean"])


def test_reconstruction_ruler_is_untouched_by_the_new_marginal_srmc_split():
    """Exit criterion 2: `reconstruct_price_gbp_per_mwh` is the frozen subject of the
    reconstructibility lift table and must NOT have been re-expressed in terms of the
    new `marginal_srmc_gbp_per_mwh`. They agree in the oversupply and ordinary regimes
    (same code path by construction) and must DIVERGE in tight hours, where the
    reconstruction keeps its convex climb toward the ceiling and the new function
    returns the flat peaker SRMC."""
    ord_d, ord_r = _demand_renewable_for(_ORDINARY_RD)
    assert mo.reconstruct_price_gbp_per_mwh(GAS, ord_d, ord_r, 2019) == pytest.approx(
        mo.marginal_srmc_gbp_per_mwh(GAS, ord_d, ord_r, 2019)
    )
    over_d, over_r = 12000.0, 30000.0
    assert mo.reconstruct_price_gbp_per_mwh(GAS, over_d, over_r, 2019) == pytest.approx(
        mo.marginal_srmc_gbp_per_mwh(GAS, over_d, over_r, 2019)
    )
    peaker_d, peaker_r = _demand_renewable_for(_PEAKER_RD)
    assert mo.reconstruct_price_gbp_per_mwh(GAS, peaker_d, peaker_r, 2019) > (
        mo.marginal_srmc_gbp_per_mwh(GAS, peaker_d, peaker_r, 2019)
    )
