**Lane:** W1_market_weather · **Atom:** EP13_adapter_carbon_intensity (sibling defect) · filed BEFORE the run

# Pre-registration: does the price residual's double-counted solar cost fidelity?

Opened by `WORKER_FINDING_THE_WORLDS_PRICE_RESIDUAL_SUBTRACTS_EMBEDDED_SOLAR_FROM_A_DEMAND_ALREADY_NET_OF_IT_2026-09-30.md`,
which asks for exactly this before any price changes. No code changes. The measurement is blind to
company results: it reads only SSP, INDO, AGWS, FUELHH interconnectors and NBP.

## Design

The fit is `simulation/run_phase3b_recalibration._fit_form`, the form `sim/price_engine.py` ships,
with the shipped shape (`X_TIGHT` 0.70, exponent 2.0), `floor = gas / THERMAL_EFFICIENCY`,
`x = RD / DISPATCHABLE_CAPACITY_MW`. Three axes on IDENTICAL rows (the intersection of SSP, INDO,
AGWS wind and solar, FUELHH interconnectors and NBP):

- **A (shipped):** `RD = INDO − wind − solar`
- **B:** `RD = INDO − wind`
- **C:** `RD = INDO + exports − wind` (exports per cable, clamped, `sim.elexon_fuel_outturn.exports_by_period`)

Held-out grade: leave one calendar year out, fit A0–A2 on the rest, predict the held-out year.
Pooled held-out MAE over all years, plus per year. Also each axis's full-window grid argmin
MAE over the module's own grid, as a check that the shipped shape is not what decides it.

## Predictions

- **P1.** B against A, pooled held-out MAE: |Δ| < 2% of A, and B ≤ A. The fit has absorbed the
  offset; solar is a midday ~1.3 GW against a 35 GW scale.
- **P2.** In summer middays (Apr–Sep, SP 21–30), B's held-out MAE improvement over A is larger, in
  relative terms, than the pooled one.
- **P3.** C against B: held-out MAE in 2022 falls; the pooled change is < 3%.

## Decision rule, fixed now

If B or C improves pooled held-out MAE by ≥ 2%, the definition was costing fidelity and a refit of
`sim/price_engine.py`'s constants on the better axis is owed as its own world-fidelity item. Below
2%, the fit had absorbed the error; the only gain is honesty of the axis, and the finding is
closed as that, with no price changed.

## Result

(written after the run, below this line)

Run 2026-10-01 on 156,976 half hours, 2016-03 to 2025-06. The shipped dataset's own join has 157,106,
and none of its rows lacks solar. The intersection loses 130 rows that have no FUELHH interconnector
reading. Script: `/tmp/pr/axis.py`.

| Axis | Pooled held-out MAE | Summer midday | 2022 | Grid argmin (in-sample) |
|---|---|---|---|---|
| A, shipped: INDO − wind − solar | **33.80** | **31.42** | **88.12** | 32.50 |
| B: INDO − wind | 34.27 (+1.4%) | 32.57 (+3.7%) | 90.15 | 32.86 |
| C: INDO + exports − wind | 35.46 (+4.9%) | 33.84 (+7.7%) | 97.66 (+8.3% on B) | 33.43 |

Units are £/MWh. A is best in 9 of the 10 held-out years. B wins only 2025, by 0.08.

- **P1 is refuted on direction.** B is worse than A, not better. The size, under 2%, held.
- **P2 is refuted.** The summer midday is where B loses most.
- **P3 is refuted.** Adding exports makes 2022 worse by 8%, not better.

**Decision, by the rule fixed above:** neither honest axis improves the fit, so no price changes.
The double-counted solar is not costing fidelity. It is doing work.

**Post hoc, NOT pre-registered.** I swept a free solar weight, `x = (INDO − wind − β·solar) / cap`,
leave one year out:

| β | 0 | 0.5 | 1 (shipped) | 1.5 | 2 | 3 |
|---|---|---|---|---|---|---|
| Pooled held-out MAE | 34.27 | 33.96 | 33.80 | 33.80 | 33.92 | 34.29 |

The held-out optimum is β between 1 and 1.5. That is on top of an INDO which already falls with
embedded solar. SSP therefore falls with sunshine about twice as much as the solar's own MW explain.
Possible causes are the hour and season that solar marks, and embedded generation that AGWS does
not see. Neither is measured here.

What `RD` is in `sim/price_engine.system_margin_price` is now stated. It is a FITTED regressor
whose solar weight is empirical, at its held-out optimum. It is not physical residual demand.
Exports behave the same way. GB exports when it is cheap against the continent, so adding exports to
demand points the wrong way for a single-market price form. A comment at the line says so, so that
nobody "fixes" it to the physical definition.

This changes the carbon shape not at all. There, the physical definition is the quantity
(EP13 s19–s20).
