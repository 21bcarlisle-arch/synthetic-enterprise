"""Phase 3b (Epoch-2 recalibration) — merit-order wholesale price model
(Regime-3 generative physics engine).

This is the synthetic *price* physics engine: a structural model of how the
System Sell Price emerges from gas, carbon, demand, and renewable supply,
rather than a re-sampling of historical SSP itself. Real historical SSP
(sim/system_prices_history.py) is still the company-observable price over the
historical window; this engine forms the DERIVED price.

STALENESS CORRECTION (2026-08-03, W1_6b): the sentences this paragraph replaced
claimed the module "remains gated OFF in every production simulation phase" and
was "not yet wired into any live phase". That has been FALSE since 2026-07-20,
when W1_6_physics_price_signal landed `sim/weather_price_chain.py` — which
imports `synthetic_price` and makes it the last link of the live weather ->
demand+renewable -> residual -> price chain, read by `sim/flex_dispatch.py`,
`sim/ssp_tail_model.py` and the coupled-triad harness. The old "it is gated off,
so recalibrating it cannot perturb P&L" argument therefore no longer holds:
changes here DO move the derived price series, and R13 applies in full — this
module changes for fidelity-to-reality reasons only, decided blind to company
P&L.

--- Merit-order wiring (2026-08-03, atom W1_6b) ---
`merit_order_price` (below) forms price by dispatching the typed SRMC stack in
`sim/merit_order_reconstruction.py` and adding a scarcity rent that is exactly
zero outside tight hours. Before this, no code path in this module referenced
that stack at all, so the merit-order reconstruction was a standalone diagnostic
measured only by its own harness.

The baseline was NOT flipped to it. Measured over the full real Elexon record
(2016-03-01..2025-06-07, n=157,106) the merit-order former is a WASH against the
shipped reduced form (MAE 32.69 vs 32.79 £/MWh; correlation 0.638 vs 0.659;
7 of 10 year-cells better, 2016/2017/2022 worse). Under R13 a wash is not a
fidelity-to-reality reason to move the baseline, so `synthetic_price` and every
default path are byte-identical to before, and the merit-order former is
selected explicitly by callers that can supply a real calendar year. The residual
error concentrates in the LOW-CARBON early cells (2016/2017) — the same signature
as the atom's open NAMED GAP, the missing EU/UK-ETS carbon time-series (R10);
that gap is deliberately NOT closed by fabricating a series (R12/R13).
Full evidence: docs/fidelity/W1_6b_merit_order_price_wiring_evidence.md.

--- History: the original raw-ratio form failed calibration ---
The original spec (`P_HH = gas_floor * (demand/renewable)^gamma`, raw
national-MW inputs, gamma in [1.5, 2.5]) overestimated real Elexon SSP by
roughly 10x even at gamma=1.5 (see docs/calibration/price-engine.md for the
full original report, preserved as the record of why that form failed). Two
root causes were diagnosed: (a) the raw demand/renewable RATIO has a median
around 3.5, so even a low gamma explodes the gas floor by several times; (b)
the gas floor had no carbon (UK ETS) term, so it understated the true
marginal-cost floor.

--- The 2026-07-19 recalibration (docs/calibration/price-engine.md addendum) ---
Two structural changes, both fit against the full real 2016-03-01..2025-06-07
Elexon SSP window (n=157,106 settlement periods, sim/cache/elexon_ssp_full.json)
via `simulation/run_phase3b_recalibration.py`:

1. Carbon term added to the gas floor:
     P_gas_floor = (gas_price + carbon_price * EF_GAS_TCO2_PER_MWH_TH) / thermal_efficiency
   `carbon_price_gbp_per_tonne` defaults to 0.0 (no real UK-ETS historical
   series is wired into this recalibration pass — the term is structurally
   present and unit-tested, but inactive by default; see the R10 note below).

2. The margin term is now a RESIDUAL-DEMAND SCARCITY form, replacing the raw
   demand/renewable ratio:
     RD = demand_mw - renewable_generation_mw          (residual demand: the
                                                          load thermal plant
                                                          must actually serve)
     x  = RD / DISPATCHABLE_CAPACITY_MW                (normalized against
                                                          the GB dispatchable
                                                          fleet)
     multiplier = A0 + A1*x + A2 * max(0, x - X_TIGHT) ** SCARCITY_EXPONENT
     P_HH = P_gas_floor * multiplier
   This multiplier is ≈1 (near the floor) at typical (median) residual
   demand, falls toward/below zero when renewables flood the system
   (x very negative), and rises convexly only once the margin gets
   unusually tight (x > X_TIGHT) — matching the real merit-order intuition
   that a small extra increment of demand near full dispatch jumps to a much
   dearer plant, without the raw-ratio form's runaway explosion in typical
   conditions.

   Calibrated fit (full window, MAE-minimizing grid search over
   X_TIGHT/SCARCITY_EXPONENT, then closed-form least-squares for A0/A1/A2 at
   each grid point): MAE=£32.79/MWh, R^2=0.419, beating both the naive
   gas-floor-alone baseline (MAE=£35.78) and the 3-feature OLS regression
   (MAE=£33.96, docs/calibration/price-engine.md) on the same window. Full
   distribution and per-year table: docs/fidelity/EPOCH2_PRICE_ENGINE_FIDELITY_EVIDENCE.md.

3. Wind cubic physics (`wind_power_output_fraction`) is unchanged — the
   idealised turbine power curve was never the part of the model that failed
   calibration.

--- R10 simplifications (hand-set, not fit to data) ---
- `EF_GAS_TCO2_PER_MWH_TH = 0.184` — standard natural-gas combustion
  emissions factor (tCO2 per MWh thermal), DESNZ/DEFRA convention. Would be
  grounded by pulling the specific published DESNZ/DEFRA conversion-factor
  table for the relevant year (the factor drifts slightly year to year).
- `DISPATCHABLE_CAPACITY_MW = 35000.0` — approximate GB dispatchable
  generation fleet capacity (CCGT/OCGT/coal/nuclear/interconnector import
  capacity), asserted as a round-number physical scale, not fit to SSP data.
  Would be grounded by a National Grid ESO capacity-register figure for the
  specific year (this fleet has shrunk over 2016-2025 as coal exited).
- `carbon_price_gbp_per_tonne` defaults to 0.0 in every call in this
  recalibration — no real historical UK-ETS/EU-ETS carbon price series is
  wired into `simulation/run_phase3b_recalibration.py` yet. UK ETS has been
  effective since Jan 2021; a real carbon series would need to be
  time-indexed (pre-2021 the term should not apply, or should use the EU ETS
  price GB was under). Grounding this is future work, out of scope for this
  recalibration pass (which only had to fix the ~10x overestimate).

Generated by qwen2.5-coder:14b (original Phase 3b), recalibrated and
integrated by the frontier orchestrator (Epoch-2 recalibration, 2026-07-19).
"""

THERMAL_EFFICIENCY = 0.50  # MWh(e) per MWh(th), starting assumption per spec

EF_GAS_TCO2_PER_MWH_TH = 0.184  # tCO2 per MWh(th) — R10 simplification, see module docstring

# --- Residual-demand scarcity form: calibrated constants (2026-07-19) ---
# Fit via simulation/run_phase3b_recalibration.py against real Elexon SSP,
# full window 2016-03-01..2025-06-07 (n=157,106). See
# docs/fidelity/EPOCH2_PRICE_ENGINE_FIDELITY_EVIDENCE.md for the full
# calibration report (MAE, R^2, distribution match, per-year table).
DISPATCHABLE_CAPACITY_MW = 35000.0  # R10 simplification, see module docstring
X_TIGHT = 0.70  # scarcity kicks in once residual demand exceeds 70% of DISPATCHABLE_CAPACITY_MW
SCARCITY_EXPONENT = 2.0  # convexity of the tight-margin kicker (p)
A0 = 0.326998  # multiplier intercept
A1 = 1.334629  # multiplier slope in x
A2 = 3.828327  # convex tight-margin coefficient

WIND_CUT_IN_MS = 3.0
WIND_RATED_MS = 12.0
WIND_CUT_OUT_MS = 25.0


def gas_floor_price(
    gas_price_gbp_per_mwh: float,
    thermal_efficiency: float = THERMAL_EFFICIENCY,
    carbon_price_gbp_per_tonne: float = 0.0,
) -> float:
    """The marginal cost (£/MWh(e)) of gas-fired generation at gas_price,
    including the carbon (UK-ETS) cost of combustion.

    P_gas_floor = (gas_price + carbon_price * EF_GAS_TCO2_PER_MWH_TH) / thermal_efficiency

    `carbon_price_gbp_per_tonne` defaults to 0.0 — with the default, this
    reduces exactly to the original `gas_price / thermal_efficiency` form
    (back-compat with the pre-recalibration tests). UK ETS has applied since
    Jan 2021; a real time-indexed carbon price series is not yet wired in
    (see module docstring R10 note) — pass a non-zero value explicitly to
    exercise the carbon term.
    """
    carbon_cost_per_mwh_th = carbon_price_gbp_per_tonne * EF_GAS_TCO2_PER_MWH_TH
    return (gas_price_gbp_per_mwh + carbon_cost_per_mwh_th) / thermal_efficiency


def system_margin_price(
    gas_floor_price_gbp_per_mwh: float,
    demand_mw: float,
    renewable_generation_mw: float,
    dispatchable_capacity_mw: float = DISPATCHABLE_CAPACITY_MW,
) -> float:
    """The merit-order system price (£/MWh): the gas floor scaled by a
    residual-demand scarcity multiplier.

    RD = demand_mw - renewable_generation_mw      (residual/thermal demand)
    x  = RD / dispatchable_capacity_mw             (normalized scarcity)
    multiplier = A0 + A1*x + A2 * max(0, x - X_TIGHT) ** SCARCITY_EXPONENT
    P_HH = gas_floor_price_gbp_per_mwh * multiplier

    Replaces the pre-recalibration raw-ratio form
    `gas_floor * (demand/renewable)^gamma`, which overestimated real SSP by
    ~10x (docs/calibration/price-engine.md). This form:
      - is ≈ the gas floor at typical (median) residual demand,
      - rises convexly, supralinearly, only once the margin is unusually
        tight (x > X_TIGHT) — a small extra demand increment near full
        dispatch jumps to a much dearer marginal plant,
      - can fall BELOW the floor, toward and below zero, when renewable
        generation is abundant relative to demand (x very negative,
        i.e. renewables flooding the system) — real SSP goes as low as
        -£185/MWh in oversupply periods.

    A0, A1, A2, X_TIGHT, SCARCITY_EXPONENT are calibrated constants (module
    level) fit against real Elexon SSP — see module docstring. No longer
    requires renewable_generation_mw > 0 (residual demand handles a
    zero-renewables period gracefully; it is simply RD = demand_mw).
    """
    residual_demand_mw = demand_mw - renewable_generation_mw
    x = residual_demand_mw / dispatchable_capacity_mw
    tight_excess = max(0.0, x - X_TIGHT)
    multiplier = A0 + A1 * x + A2 * (tight_excess ** SCARCITY_EXPONENT)
    return gas_floor_price_gbp_per_mwh * multiplier


def wind_power_output_fraction(wind_speed_ms: float, rated_power_mw: float = 1.0) -> float:
    """Idealised turbine power curve: fraction of rated_power_mw delivered
    at wind_speed_ms.

    - < 3 m/s (cut-in): 0
    - 3-12 m/s: cubic ramp, P proportional to v^3, continuous from 0 at
      3 m/s to rated_power_mw at 12 m/s
    - 12-25 m/s (rated): rated_power_mw
    - > 25 m/s (cut-out): 0
    """
    if wind_speed_ms < WIND_CUT_IN_MS or wind_speed_ms > WIND_CUT_OUT_MS:
        return 0.0
    if wind_speed_ms <= WIND_RATED_MS:
        ramp_fraction = (wind_speed_ms ** 3 - WIND_CUT_IN_MS ** 3) / (
            WIND_RATED_MS ** 3 - WIND_CUT_IN_MS ** 3
        )
        return ramp_fraction * rated_power_mw
    return rated_power_mw


def synthetic_price(
    gas_price_gbp_per_mwh: float,
    demand_mw: float,
    renewable_generation_mw: float,
    thermal_efficiency: float = THERMAL_EFFICIENCY,
    carbon_price_gbp_per_tonne: float = 0.0,
    dispatchable_capacity_mw: float = DISPATCHABLE_CAPACITY_MW,
) -> float:
    """Convenience wrapper chaining gas_floor_price -> system_margin_price —
    the full REDUCED-FORM price for one settlement period.

    This is the shipped baseline price former (`weather_price_chain.derive_price`
    calls it). It is a fitted multiplier on a gas floor, NOT a dispatch of a plant
    stack — see `merit_order_price` below for the structural alternative, and the
    "merit-order wiring" section of this module's docstring for why the baseline
    was NOT flipped to it."""
    floor = gas_floor_price(gas_price_gbp_per_mwh, thermal_efficiency, carbon_price_gbp_per_tonne)
    return system_margin_price(floor, demand_mw, renewable_generation_mw, dispatchable_capacity_mw)


# ---------------------------------------------------------------------------
# W1_6b MERIT-ORDER WIRING (2026-08-03) — the price engine forms price FROM the
# typed SRMC dispatch stack, not only from the fitted multiplier.
# See this module's docstring section "--- Merit-order wiring ---".
# ---------------------------------------------------------------------------

def scarcity_rent_gbp_per_mwh(
    gas_price_gbp_per_mwh: float,
    demand_mw: float,
    renewable_generation_mw: float,
    dispatchable_capacity_mw: float = DISPATCHABLE_CAPACITY_MW,
) -> float:
    """The calibrated SCARCITY RENT, isolated from the marginal-cost terms.

    This is exactly the `A2 * max(0, x - X_TIGHT) ** SCARCITY_EXPONENT` component of
    `system_margin_price`'s multiplier, applied to the gas floor — no constant is new
    and no constant is refit (R12/R13). Isolating it is what makes the atom's own
    thesis — "scarcity earns its keep ONLY in tight hours" — a TESTABLE property of a
    named function rather than an implicit term buried in a fitted multiplier:

        x <= X_TIGHT  ->  returns EXACTLY 0.0   (ordinary/oversupply hours pay no rent)
        x >  X_TIGHT  ->  rises convexly with the tightness of the margin

    Rent is a payment ABOVE marginal cost. It is deliberately NOT bounded below by
    zero via a separate clamp: the `max(0.0, ...)` on the tight excess IS the clamp,
    and removing it (the R15 mutation) makes ordinary hours pay a spurious rent.
    """
    residual_demand_mw = demand_mw - renewable_generation_mw
    x = residual_demand_mw / dispatchable_capacity_mw
    tight_excess = max(0.0, x - X_TIGHT)
    if tight_excess == 0.0:
        return 0.0
    floor = gas_floor_price(gas_price_gbp_per_mwh)
    return floor * A2 * (tight_excess ** SCARCITY_EXPONENT)


def merit_order_price(
    gas_price_gbp_per_mwh: float,
    demand_mw: float,
    renewable_generation_mw: float,
    year: int,
    ets_price_gbp_per_tonne: float = 0.0,
    dispatchable_capacity_mw: float = DISPATCHABLE_CAPACITY_MW,
) -> float:
    """The MERIT-ORDER price former: marginal cost from the dispatch stack, plus
    scarcity rent that is nonzero only in tight hours, capped at the real GB cash-out
    ceiling. The curtailment floor needs no clamp — the stack's own oversupply regime
    already bottoms out there (see the note at the return).

        P = min( marginal_srmc(gas, carbon, RD, year) + scarcity_rent(x),
                 CASH_OUT_CEILING )

    `marginal_srmc` comes from `sim.merit_order_reconstruction` — the typed SRMC stack
    grounded in DUKES 5.10.C/5.14 per-year efficiencies and emission factors, the HMRC
    Carbon Price Support (~£18/tCO2, flat 2016-2028), and the DESNZ VOM bookends. That
    import is what closes the W1_6b wiring gap: before 2026-08-03 the price engine never
    referenced the reconstruction at all, so the stack was a standalone diagnostic.

    `year` is REQUIRED and has no default. The stack's constants are published PER YEAR;
    inventing a window-average year would be fabricating an input, so a caller that
    cannot supply a real calendar year cannot use this former (R10 — a named gap is
    carried, never filled with a made-up number).

    `ets_price_gbp_per_tonne` defaults to 0.0: carbon is therefore Carbon Price Support
    ALONE. The EU/UK-ETS market series remains the atom's open NAMED GAP; it is threaded
    through so that sourcing it later needs no re-fit and no curve-fitting (R12/R13).

    NOT THE DEFAULT BASELINE, deliberately. Measured over the full real Elexon record
    (2016-03-01..2025-06-07, n=157,106) this former is a WASH against the shipped
    reduced form — MAE 32.69 vs 32.79 £/MWh, correlation 0.638 vs 0.659, winning 7 of
    10 year-cells and losing 2016/2017/2022. A wash is not a fidelity-to-reality win, so
    under R13 it does not justify moving the baseline; the baseline series stays
    byte-identical and this former is selected explicitly. Full table:
    docs/fidelity/W1_6b_merit_order_price_wiring_evidence.md.
    """
    # Lazy import: sim.merit_order_reconstruction imports THERMAL_EFFICIENCY from this
    # module at import time (the frozen ruler), so a module-level import here would be a
    # cycle. Deliberately NOT wrapped in try/except — if the stack is unavailable this
    # must raise, never silently degrade to the reduced form (R15 pattern #3, FAIL-SILENT).
    from sim.merit_order_reconstruction import (
        CASH_OUT_CEILING_GBP_PER_MWH,
        CURTAILMENT_FLOOR_GBP_PER_MWH,
        marginal_srmc_gbp_per_mwh,
    )

    srmc = marginal_srmc_gbp_per_mwh(
        gas_price_gbp_per_mwh,
        demand_mw,
        renewable_generation_mw,
        year,
        ets_price_gbp_per_tonne,
    )
    rent = scarcity_rent_gbp_per_mwh(
        gas_price_gbp_per_mwh, demand_mw, renewable_generation_mw, dispatchable_capacity_mw
    )
    price = srmc + rent
    # Only the CEILING is clamped here. A symmetric floor clamp was written and then
    # REMOVED as dead code (R11 — a branch whose release can never fire is a defect):
    # `marginal_srmc_gbp_per_mwh`'s oversupply regime already clamps its collapse
    # fraction to [0, 1], so its own minimum IS the curtailment floor, and rent is zero
    # there — the sum can never go below it. The floor is a guarantee of the STACK, and
    # `test_formed_price_never_falls_below_the_curtailment_floor` asserts it as such.
    if price > CASH_OUT_CEILING_GBP_PER_MWH:
        return CASH_OUT_CEILING_GBP_PER_MWH
    return price
